"""
Endpoints de pedidos
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload, joinedload
from typing import List, Optional
from datetime import datetime
import random
import string

from src.core.database import get_db
from src.core.security import get_current_user_email
from src.models.order import Order, OrderItem, OrderStatus
from src.models.scaffold import Scaffold
from src.models.user import User
from src.models.customer import Customer
from src.schemas.order import (
    OrderCreate,
    OrderUpdate,
    OrderResponse,
    OrderWithItems,
    OrderListItem,
    OrderPriceCalculation,
    OrderPriceResponse
)
from src.services.pricing import PricingService
from src.services.inventory import InventoryService

router = APIRouter()


def generate_order_number() -> str:
    """Genera un número de orden único"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"ORD-{timestamp}-{random_chars}"


async def update_order_status_by_date(order: Order, db: AsyncSession) -> bool:
    """
    Actualiza el estado de una orden basándose en las fechas
    - Si está CONFIRMED y llegó start_date → IN_USE
    - Si está IN_USE y llegó end_date → COMPLETED
    
    Returns True si se actualizó el estado
    """
    try:
        # Obtener fecha actual (naive para comparar con dates)
        now = datetime.now().date()
        updated = False
        
        # Manejar caso donde start_date o end_date pueden ser None
        if not order.start_date or not order.end_date:
            return False
        
        # Convertir start_date y end_date a date si son datetime
        start_date = order.start_date.date() if hasattr(order.start_date, 'date') else order.start_date
        end_date = order.end_date.date() if hasattr(order.end_date, 'date') else order.end_date
        
        # Si está confirmado y llegó la fecha de inicio, cambiar a IN_USE
        if order.status == OrderStatus.CONFIRMED and start_date <= now:
            order.status = OrderStatus.IN_USE
            order.delivered_at = datetime.utcnow()
            updated = True
        
        # Si está en uso y llegó la fecha de fin, cambiar a COMPLETED
        elif order.status == OrderStatus.IN_USE and end_date <= now:
            order.status = OrderStatus.COMPLETED
            order.completed_at = datetime.utcnow()
            updated = True
        
        return updated
    except Exception as e:
        # Log error pero no romper el flujo
        print(f"Error updating order status: {e}")
        return False

@router.post("/calculate-price", response_model=OrderPriceResponse)
async def calculate_price(
    calculation: OrderPriceCalculation,
    db: AsyncSession = Depends(get_db)
):
    """
    Calcula el precio de un pedido sin crearlo
    """
    # Obtener andamios
    items_with_scaffolds = []
    for item in calculation.items:
        result = await db.execute(
            select(Scaffold).where(Scaffold.id == item.scaffold_id)
        )
        scaffold = result.scalar_one_or_none()
        
        if not scaffold:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Andamio con ID {item.scaffold_id} no encontrado"
            )
        
        items_with_scaffolds.append({
            'scaffold': scaffold,
            'quantity': item.quantity
        })
    
    # Calcular precio
    price_data = PricingService.calculate_order_price(
        items_with_scaffolds,
        calculation.start_date,
        calculation.end_date,
        calculation.rental_period,
        calculation.delivery_postal_code
    )
    
    return price_data


@router.post("/", response_model=OrderWithItems, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user_email: str = Depends(get_current_user_email)
):
    """
    Crea un nuevo pedido de renta
    """
    # Verificar que el customer existe
    result = await db.execute(
        select(Customer).where(Customer.id == order_data.customer_id)
    )
    customer = result.scalar_one_or_none()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado"
        )
    
    # Obtener andamios y verificar disponibilidad
    items_with_scaffolds = []
    for item in order_data.items:
        result = await db.execute(
            select(Scaffold).where(Scaffold.id == item.scaffold_id)
        )
        scaffold = result.scalar_one_or_none()
        
        if not scaffold:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Andamio con ID {item.scaffold_id} no encontrado"
            )
        
        items_with_scaffolds.append({
            'scaffold': scaffold,
            'quantity': item.quantity,
            'notes': item.notes
        })
    
    # Verificar disponibilidad de inventario
    inventory_items = [
        {'scaffold_id': item['scaffold'].id, 'quantity': item['quantity']}
        for item in items_with_scaffolds
    ]
    
    availability = await InventoryService.reserve_stock(
        db,
        inventory_items,
        order_data.start_date,
        order_data.end_date
    )
    
    if not availability['success']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=availability['message'],
            headers={"X-Unavailable-Items": str(availability['unavailable_items'])}
        )
    
    # Calcular precios
    price_data = PricingService.calculate_order_price(
        items_with_scaffolds,
        order_data.start_date,
        order_data.end_date,
        order_data.rental_period,
        order_data.delivery_postal_code
    )
    
    # Crear orden
    new_order = Order(
        order_number=generate_order_number(),
        customer_id=order_data.customer_id,
        rental_period=order_data.rental_period,
        start_date=order_data.start_date,
        end_date=order_data.end_date,
        delivery_address=order_data.delivery_address,
        delivery_city=order_data.delivery_city,
        delivery_state=order_data.delivery_state,
        delivery_postal_code=order_data.delivery_postal_code,
        delivery_notes=order_data.delivery_notes,
        notes=order_data.notes,
        subtotal=price_data['subtotal'],
        delivery_fee=price_data['delivery_fee'],
        discount_amount=price_data['discount_amount'],
        tax_amount=price_data['tax_amount'],
        deposit_amount=price_data['deposit_amount'],
        total_amount=price_data['total_amount'],
        payment_method=order_data.payment_method
    )
    
    db.add(new_order)
    await db.flush()
    
    # Crear order items
    for idx, item in enumerate(items_with_scaffolds):
        order_item = OrderItem(
            order_id=new_order.id,
            scaffold_id=item['scaffold'].id,
            quantity=item['quantity'],
            unit_price=price_data['breakdown'][idx]['unit_price'],
            subtotal=price_data['breakdown'][idx]['subtotal'],
            notes=item.get('notes')
        )
        db.add(order_item)
    
    await db.commit()
    
    # Recargar la orden con eager loading de las relaciones necesarias
    result = await db.execute(
        select(Order)
        .options(
            selectinload(Order.customer).selectinload(Customer.user),
            selectinload(Order.order_items)
        )
        .where(Order.id == new_order.id)
    )
    order_with_relations = result.scalar_one()
    
    return order_with_relations


@router.get("/my-orders", response_model=List[OrderListItem])
async def get_my_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[OrderStatus] = None,
    db: AsyncSession = Depends(get_db),
    current_user_email: str = Depends(get_current_user_email)
):
    """
    Lista las órdenes del cliente actual
    """
    try:
        # Log inicial
        with open("my_orders_debug.log", "a", encoding="utf-8") as f:
            f.write(f"\n=== MY-ORDERS CALLED ===\n")
            f.write(f"User email: {current_user_email}\n")
        
        # Obtener usuario actual
        result = await db.execute(
            select(User).where(User.email == current_user_email)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        with open("my_orders_debug.log", "a", encoding="utf-8") as f:
            f.write(f"User found: ID={user.id}\n")
        
        # Obtener customer del usuario
        result = await db.execute(
            select(Customer).where(Customer.user_id == user.id)
        )
        customer = result.scalar_one_or_none()
        
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No tiene un perfil de cliente"
            )
        
        with open("my_orders_debug.log", "a", encoding="utf-8") as f:
            f.write(f"Customer found: ID={customer.id}\n")
        
        # Consultar órdenes del cliente con eager loading
        query = select(Order).options(
            joinedload(Order.customer).joinedload(Customer.user)
        ).where(Order.customer_id == customer.id)
        
        if status:
            query = query.where(Order.status == status)
        
        query = query.offset(skip).limit(limit).order_by(Order.created_at.desc())
        
        result = await db.execute(query)
        orders = result.scalars().all()
        
        # ✅ Actualizar estados automáticamente basándose en fechas
        needs_commit = False
        for order in orders:
            if await update_order_status_by_date(order, db):
                needs_commit = True
        
        # Hacer un solo commit si hubo cambios
        if needs_commit:
            await db.commit()
            # Refrescar todas las órdenes actualizadas
            for order in orders:
                await db.refresh(order)
        
        with open("my_orders_debug.log", "a", encoding="utf-8") as f:
            f.write(f"Orders found: {len(orders)}\n")
        
        # Populate customer_name manually
        order_list = []
        for order in orders:
            order_dict = {
                "id": order.id,
                "order_number": order.order_number,
                "customer_id": order.customer_id,
                "customer_name": order.customer.user.full_name if order.customer and order.customer.user else None,
                "status": order.status,
                "start_date": order.start_date,
                "end_date": order.end_date,
                "total_amount": order.total_amount,
                "is_paid": order.is_paid,
                "is_overdue": order.is_overdue,
                "created_at": order.created_at
            }
            order_list.append(OrderListItem(**order_dict))
        
        with open("my_orders_debug.log", "a", encoding="utf-8") as f:
            f.write(f"Returning {len(order_list)} orders\n")
        
        return order_list
    except HTTPException:
        raise
    except Exception as e:
        with open("my_orders_debug.log", "a", encoding="utf-8") as f:
            import traceback
            f.write(f"\n!!! EXCEPTION !!!\n")
            f.write(f"Type: {type(e).__name__}\n")
            f.write(f"Message: {str(e)}\n")
            f.write(f"Traceback:\n{traceback.format_exc()}\n")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar órdenes: {str(e)}"
        )


@router.get("/", response_model=List[OrderListItem])
async def list_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[OrderStatus] = None,
    customer_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user_email: str = Depends(get_current_user_email)
):
    """
    Lista todos los pedidos con filtros opcionales
    """
    # Eager loading de customer y user para OrderListItem
    query = select(Order).options(
        selectinload(Order.customer).selectinload(Customer.user)
    )
    
    filters = []
    if status:
        filters.append(Order.status == status)
    if customer_id:
        filters.append(Order.customer_id == customer_id)
    
    if filters:
        query = query.where(and_(*filters))
    
    query = query.offset(skip).limit(limit).order_by(Order.created_at.desc())
    
    result = await db.execute(query)
    orders = result.scalars().all()
    
    # ✅ Actualizar estados automáticamente basándose en fechas
    needs_commit = False
    for order in orders:
        if await update_order_status_by_date(order, db):
            needs_commit = True
    
    # Hacer un solo commit si hubo cambios
    if needs_commit:
        await db.commit()
        # Refrescar todas las órdenes actualizadas
        for order in orders:
            await db.refresh(order)
    
    # Populate customer_name manually
    order_list = []
    for order in orders:
        order_dict = {
            "id": order.id,
            "order_number": order.order_number,
            "customer_id": order.customer_id,
            "customer_name": order.customer.user.full_name if order.customer and order.customer.user else None,
            "status": order.status,
            "start_date": order.start_date,
            "end_date": order.end_date,
            "total_amount": order.total_amount,
            "is_paid": order.is_paid,
            "is_overdue": order.is_overdue,
            "created_at": order.created_at
        }
        order_list.append(OrderListItem(**order_dict))
    
    return order_list


@router.get("/{order_id}", response_model=OrderWithItems)
async def get_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_email: str = Depends(get_current_user_email)
):
    """
    Obtiene detalles de un pedido específico
    """
    # Obtener usuario actual
    result = await db.execute(
        select(User).where(User.email == current_user_email)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    result = await db.execute(
        select(Order)
        .options(
            selectinload(Order.customer).selectinload(Customer.user),
            selectinload(Order.order_items)
        )
        .where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido no encontrado"
        )
    
    # Verificar permisos: solo el cliente dueño o staff/admin
    is_owner = order.customer.user_id == user.id
    is_staff = user.role in ["admin", "staff"]
    
    if not (is_owner or is_staff):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para ver este pedido"
        )
    
    # Construir response con customer info
    order_dict = OrderWithItems.model_validate(order).model_dump()
    if order.customer and order.customer.user:
        order_dict["customer_name"] = order.customer.user.full_name
        order_dict["customer_email"] = order.customer.user.email
    
    # Si los valores de pricing están en 0, recalcular (para órdenes antiguas)
    if order.subtotal == 0 or order.total_amount == 0:
        # Obtener scaffolds para los items
        items_with_scaffolds = []
        for item in order.order_items:
            result = await db.execute(
                select(Scaffold).where(Scaffold.id == item.scaffold_id)
            )
            scaffold = result.scalar_one_or_none()
            if scaffold:
                items_with_scaffolds.append({
                    'scaffold': scaffold,
                    'quantity': item.quantity
                })
        
        # Recalcular precios
        if items_with_scaffolds:
            price_data = PricingService.calculate_order_price(
                items_with_scaffolds,
                order.start_date,
                order.end_date,
                order.rental_period,
                order.delivery_postal_code
            )
            
            # Actualizar en el dict de respuesta
            order_dict["subtotal"] = price_data['subtotal']
            order_dict["delivery_fee"] = price_data['delivery_fee']
            order_dict["tax_amount"] = price_data['tax_amount']
            order_dict["discount_amount"] = price_data['discount_amount']
            order_dict["deposit_amount"] = price_data['deposit_amount']
            order_dict["total_amount"] = price_data['total_amount']
    
    return OrderWithItems(**order_dict)


@router.patch("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: int,
    order_data: OrderUpdate,
    db: AsyncSession = Depends(get_db),
    current_user_email: str = Depends(get_current_user_email)
):
    """
    Actualiza un pedido
    """
    result = await db.execute(
        select(Order).where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido no encontrado"
        )
    
    # Actualizar campos
    update_data = order_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(order, field, value)
    
    # Actualizar timestamps según el estado
    if order_data.status == OrderStatus.CONFIRMED and not order.confirmed_at:
        order.confirmed_at = datetime.utcnow()
    elif order_data.status == OrderStatus.DELIVERED and not order.delivered_at:
        order.delivered_at = datetime.utcnow()
    elif order_data.status == OrderStatus.COMPLETED and not order.completed_at:
        order.completed_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(order)
    
    return order


@router.patch("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: int,
    status_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user_email: str = Depends(get_current_user_email)
):
    """
    Actualiza el estado de una orden (solo staff/admin)
    """
    # Verificar permisos
    result = await db.execute(
        select(User).where(User.email == current_user_email)
    )
    user = result.scalar_one_or_none()
    
    if not user or user.role not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para actualizar órdenes"
        )
    
    # Obtener orden
    result = await db.execute(
        select(Order).where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orden no encontrada"
        )
    
    # Actualizar estado
    new_status = status_data.get("status")
    if new_status:
        try:
            order.status = OrderStatus(new_status)
            
            # Actualizar timestamps
            if order.status == OrderStatus.CONFIRMED and not order.confirmed_at:
                order.confirmed_at = datetime.now()
            elif order.status == OrderStatus.DELIVERED and not order.delivered_at:
                order.delivered_at = datetime.now()
            elif order.status == OrderStatus.COMPLETED and not order.completed_at:
                order.completed_at = datetime.now()
                
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Estado inválido: {new_status}"
            )
    
    await db.commit()
    await db.refresh(order)
    
    return order


@router.post("/{order_id}/approve", response_model=OrderResponse)
async def approve_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_email: str = Depends(get_current_user_email)
):
    """
    Aprueba una orden (solo staff/admin)
    """
    # Verificar permisos
    result = await db.execute(
        select(User).where(User.email == current_user_email)
    )
    user = result.scalar_one_or_none()
    
    if not user or user.role not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para aprobar órdenes"
        )
    
    # Obtener orden
    result = await db.execute(
        select(Order).where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orden no encontrada"
        )
    
    # Aprobar orden
    order.status = OrderStatus.CONFIRMED
    if not order.confirmed_at:
        order.confirmed_at = datetime.now()
    
    await db.commit()
    await db.refresh(order)
    
    return order


@router.post("/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(
    order_id: int,
    cancellation_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user_email: str = Depends(get_current_user_email)
):
    """
    Cancela una orden (cliente dueño o staff/admin)
    """
    # Obtener usuario actual
    result = await db.execute(
        select(User).where(User.email == current_user_email)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Obtener orden con relaciones
    result = await db.execute(
        select(Order)
        .options(joinedload(Order.customer))
        .where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orden no encontrada"
        )
    
    # Verificar permisos
    is_owner = order.customer.user_id == user.id
    is_staff = user.role in ["admin", "staff"]
    
    if not (is_owner or is_staff):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para cancelar esta orden"
        )
    
    # Cancelar orden
    order.status = OrderStatus.CANCELLED
    if cancellation_data.get("reason"):
        order.cancellation_reason = cancellation_data["reason"]
    
    await db.commit()
    await db.refresh(order)
    
    return order
