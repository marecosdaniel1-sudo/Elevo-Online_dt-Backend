"""
Endpoints de andamios (catálogo de productos)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from typing import List, Optional
from datetime import date, datetime

from src.core.database import get_db
from src.core.security import get_current_user_email
from src.models.scaffold import Scaffold, ScaffoldType
from src.models.order import Order, OrderStatus, OrderItem
from src.models.user import User
from src.schemas.scaffold import (
    ScaffoldCreate,
    ScaffoldUpdate,
    ScaffoldResponse,
    ScaffoldListItem,
    ScaffoldStockUpdate,
    ScaffoldAvailability
)

router = APIRouter()


@router.get("/", response_model=List[ScaffoldListItem])
async def list_scaffolds(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    type: Optional[ScaffoldType] = None,
    is_active: Optional[bool] = True,
    is_featured: Optional[bool] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Lista todos los andamios disponibles con filtros opcionales
    """
    query = select(Scaffold)
    
    # Aplicar filtros
    filters = []
    
    if is_active is not None:
        filters.append(Scaffold.is_active == is_active)
    
    if is_featured is not None:
        filters.append(Scaffold.is_featured == is_featured)
    
    if type:
        filters.append(Scaffold.type == type)
    
    if search:
        search_filter = or_(
            Scaffold.name.ilike(f"%{search}%"),
            Scaffold.sku.ilike(f"%{search}%"),
            Scaffold.description.ilike(f"%{search}%")
        )
        filters.append(search_filter)
    
    if filters:
        query = query.where(and_(*filters))
    
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    scaffolds = result.scalars().all()
    
    return scaffolds


@router.get("/{scaffold_id}/availability", response_model=ScaffoldAvailability)
async def check_scaffold_availability(
    scaffold_id: int,
    start_date: date = Query(..., description="Fecha de inicio del alquiler"),
    end_date: date = Query(..., description="Fecha de fin del alquiler"),
    quantity: int = Query(..., ge=1, description="Cantidad solicitada"),
    db: AsyncSession = Depends(get_db)
):
    """
    Verifica la disponibilidad de un andamio para un rango de fechas
    
    Considera:
    - Stock disponible del andamio
    - Órdenes activas en ese rango de fechas
    - Cantidad solicitada
    """
    try:
        # Verificar que el andamio existe
        result = await db.execute(
            select(Scaffold).where(Scaffold.id == scaffold_id)
        )
        scaffold = result.scalar_one_or_none()
        
        if not scaffold:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Andamio no encontrado"
            )
        
        if not scaffold.is_active:
            return ScaffoldAvailability(
                scaffold_id=scaffold_id,
                available=False,
                available_quantity=0,
                requested_quantity=quantity,
                start_date=start_date,
                end_date=end_date,
                message="El andamio no está activo"
            )
        
        # Convertir date a datetime para comparación con Order.start_date y Order.end_date
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
        
        # Buscar órdenes activas que se solapan con el rango de fechas
        result = await db.execute(
            select(OrderItem)
            .join(Order)
            .where(
                and_(
                    OrderItem.scaffold_id == scaffold_id,
                    Order.status.in_([
                        OrderStatus.PENDING,
                        OrderStatus.CONFIRMED,
                        OrderStatus.PREPARING,
                        OrderStatus.IN_TRANSIT,
                        OrderStatus.DELIVERED,
                        OrderStatus.IN_USE
                    ]),
                    # Verificar solapamiento de fechas
                    or_(
                        and_(
                            Order.start_date <= start_datetime,
                            Order.end_date >= start_datetime
                        ),
                        and_(
                            Order.start_date <= end_datetime,
                            Order.end_date >= end_datetime
                        ),
                        and_(
                            Order.start_date >= start_datetime,
                            Order.end_date <= end_datetime
                        )
                    )
                )
            )
        )
        
        order_items = result.scalars().all()
        
        # Calcular cantidad reservada
        reserved_quantity = sum(item.quantity for item in order_items)
        
        # Calcular disponibilidad
        available_quantity = max(0, scaffold.available_stock - reserved_quantity)
        available = available_quantity >= quantity
        
        message = None
        if not available:
            if available_quantity == 0:
                message = "No hay unidades disponibles para este rango de fechas"
            else:
                message = f"Solo hay {available_quantity} unidades disponibles (solicitadas: {quantity})"
        
        return ScaffoldAvailability(
            scaffold_id=scaffold_id,
            available=available,
            available_quantity=available_quantity,
            requested_quantity=quantity,
            start_date=start_date,
            end_date=end_date,
            message=message
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR EN AVAILABILITY: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al verificar disponibilidad: {str(e)}"
        )


@router.get("/{scaffold_id}", response_model=ScaffoldResponse)
async def get_scaffold(
    scaffold_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene detalles de un andamio específico
    """
    result = await db.execute(
        select(Scaffold).where(Scaffold.id == scaffold_id)
    )
    scaffold = result.scalar_one_or_none()
    
    if not scaffold:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Andamio no encontrado"
        )
    
    return scaffold


@router.put("/{scaffold_id}", response_model=ScaffoldResponse)
async def update_scaffold(
    scaffold_id: int,
    scaffold_update: ScaffoldUpdate,
    db: AsyncSession = Depends(get_db),
    current_user_email: str = Depends(get_current_user_email)
):
    """
    Actualiza un andamio (solo admin/staff)
    """
    # Verificar permisos
    result = await db.execute(
        select(User).where(User.email == current_user_email)
    )
    user = result.scalar_one_or_none()
    
    if not user or user.role not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para actualizar andamios"
        )
    
    # Obtener andamio
    result = await db.execute(
        select(Scaffold).where(Scaffold.id == scaffold_id)
    )
    scaffold = result.scalar_one_or_none()
    
    if not scaffold:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Andamio no encontrado"
        )
    
    # Actualizar campos proporcionados
    update_data = scaffold_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(scaffold, field, value)
    
    await db.commit()
    await db.refresh(scaffold)
    
    return scaffold


@router.post("/", response_model=ScaffoldResponse, status_code=status.HTTP_201_CREATED)
async def create_scaffold(
    scaffold_data: ScaffoldCreate,
    db: AsyncSession = Depends(get_db),
    current_user_email: str = Depends(get_current_user_email)
):
    """
    Crea un nuevo andamio en el catálogo
    Requiere autenticación de admin/staff
    """
    from src.models.user import User
    
    # Verificar permisos (solo admin o staff)
    result = await db.execute(
        select(User).where(User.email == current_user_email)
    )
    user = result.scalar_one_or_none()
    
    if not user or user.role not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para crear andamios"
        )
    
    # Verificar si el SKU ya existe
    result = await db.execute(
        select(Scaffold).where(Scaffold.sku == scaffold_data.sku)
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El SKU ya existe"
        )
    
    # Crear andamio
    new_scaffold = Scaffold(**scaffold_data.model_dump())
    
    db.add(new_scaffold)
    await db.commit()
    await db.refresh(new_scaffold)
    
    return new_scaffold


@router.patch("/{scaffold_id}", response_model=ScaffoldResponse)
async def update_scaffold(
    scaffold_id: int,
    scaffold_data: ScaffoldUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user_email)
):
    """
    Actualiza información de un andamio
    Requiere autenticación de admin/staff
    """
    result = await db.execute(
        select(Scaffold).where(Scaffold.id == scaffold_id)
    )
    scaffold = result.scalar_one_or_none()
    
    if not scaffold:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Andamio no encontrado"
        )
    
    # Actualizar campos
    update_data = scaffold_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(scaffold, field, value)
    
    await db.commit()
    await db.refresh(scaffold)
    
    return scaffold


@router.delete("/{scaffold_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scaffold(
    scaffold_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user_email)
):
    """
    Elimina un andamio (soft delete - marca como inactivo)
    Requiere autenticación de admin
    """
    result = await db.execute(
        select(Scaffold).where(Scaffold.id == scaffold_id)
    )
    scaffold = result.scalar_one_or_none()
    
    if not scaffold:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Andamio no encontrado"
        )
    
    # Soft delete
    scaffold.is_active = False
    await db.commit()
    
    return None


@router.get("/featured/list", response_model=List[ScaffoldListItem])
async def list_featured_scaffolds(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """
    Lista andamios destacados
    """
    result = await db.execute(
        select(Scaffold)
        .where(
            and_(
                Scaffold.is_active == True,
                Scaffold.is_featured == True,
                Scaffold.available_stock > 0
            )
        )
        .limit(limit)
    )
    
    scaffolds = result.scalars().all()
    return scaffolds
