"""
Endpoints de clientes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List

from src.core.database import get_db
from src.core.security import get_current_user_email
from src.models.customer import Customer
from src.models.user import User
from src.schemas.customer import (
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse,
    CustomerWithUser
)

router = APIRouter()


# ============================================================================
# RUTAS ESPECÍFICAS PRIMERO (deben ir antes que /{customer_id})
# ============================================================================

@router.get("/me", response_model=CustomerWithUser)
async def get_my_profile(
    db: AsyncSession = Depends(get_db),
    current_user_email: str = Depends(get_current_user_email)
):
    """
    Obtiene el perfil del cliente actual
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
    
    # Obtener perfil de cliente con eager loading
    result = await db.execute(
        select(Customer).options(selectinload(Customer.user)).where(Customer.user_id == user.id)
    )
    customer = result.scalar_one_or_none()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No tiene un perfil de cliente creado"
        )
    
    return customer


@router.put("/me", response_model=CustomerResponse)
async def update_my_profile(
    customer_data: CustomerUpdate,
    db: AsyncSession = Depends(get_db),
    current_user_email: str = Depends(get_current_user_email)
):
    """
    Actualiza el perfil del cliente actual
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
    
    # Obtener perfil de cliente
    result = await db.execute(
        select(Customer).where(Customer.user_id == user.id)
    )
    customer = result.scalar_one_or_none()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No tiene un perfil de cliente creado"
        )
    
    # Actualizar campos
    update_data = customer_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(customer, field, value)
    
    await db.commit()
    await db.refresh(customer)
    
    return customer


@router.get("/", response_model=List[CustomerWithUser])
async def list_customers(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user_email: str = Depends(get_current_user_email)
):
    """
    Lista todos los clientes (solo admin/staff)
    """
    # Verificar que sea admin o staff
    result = await db.execute(
        select(User).where(User.email == current_user_email)
    )
    current_user = result.scalar_one_or_none()
    
    if not current_user or current_user.role not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para acceder a esta información"
        )
    
    # Usar eager loading para cargar la relación con User
    result = await db.execute(
        select(Customer).options(selectinload(Customer.user)).offset(skip).limit(limit)
    )
    customers = result.scalars().all()
    
    return customers


@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    customer_data: CustomerCreate,
    db: AsyncSession = Depends(get_db),
    current_user_email: str = Depends(get_current_user_email)
):
    """
    Crea un perfil de cliente para el usuario actual
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
    
    # Verificar si ya tiene perfil de cliente
    result = await db.execute(
        select(Customer).where(Customer.user_id == user.id)
    )
    existing_customer = result.scalar_one_or_none()
    
    if existing_customer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario ya tiene un perfil de cliente"
        )
    
    # Crear nuevo cliente
    new_customer = Customer(
        user_id=user.id,
        **customer_data.model_dump(exclude_unset=True)
    )
    
    db.add(new_customer)
    await db.commit()
    await db.refresh(new_customer)
    
    return new_customer


# ============================================================================
# RUTAS DINÁMICAS AL FINAL
# ============================================================================

@router.get("/{customer_id}", response_model=CustomerWithUser)
async def get_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_email: str = Depends(get_current_user_email)
):
    """
    Obtiene detalles de un cliente
    """
    result = await db.execute(
        select(Customer).options(selectinload(Customer.user)).where(Customer.id == customer_id)
    )
    customer = result.scalar_one_or_none()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado"
        )
    
    return customer


@router.patch("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: int,
    customer_data: CustomerUpdate,
    db: AsyncSession = Depends(get_db),
    current_user_email: str = Depends(get_current_user_email)
):
    """
    Actualiza información de un cliente
    """
    result = await db.execute(
        select(Customer).where(Customer.id == customer_id)
    )
    customer = result.scalar_one_or_none()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado"
        )
    
    # Actualizar campos
    update_data = customer_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(customer, field, value)
    
    await db.commit()
    await db.refresh(customer)
    
    return customer
