"""
Endpoints de transacciones
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from typing import List
from datetime import datetime
import random
import string

from src.core.database import get_db
from src.core.security import get_current_user_email
from src.models.transaction import Transaction, TransactionType
from src.models.order import Order, OrderStatus
from src.models.user import User
from src.models.customer import Customer
from src.schemas.transaction import (
    TransactionCreate,
    TransactionResponse,
    TransactionWithOrder
)

router = APIRouter()


def generate_transaction_number() -> str:
    """Genera un número de transacción único"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"TXN-{timestamp}-{random_chars}"


@router.get("/order/{order_id}", response_model=List[TransactionResponse])
async def get_order_transactions(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_email: str = Depends(get_current_user_email)
):
    """
    Obtiene todas las transacciones de una orden
    """
    # Verificar que la orden existe y el usuario tiene acceso
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
    
    # Obtener usuario actual
    result = await db.execute(
        select(User).where(User.email == current_user_email)
    )
    user = result.scalar_one_or_none()
    
    # Verificar permisos
    if user.role not in ["admin", "staff"]:
        # Si es cliente, verificar que sea su orden
        if order.customer.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos para ver estas transacciones"
            )
    
    # Obtener transacciones
    result = await db.execute(
        select(Transaction).where(Transaction.order_id == order_id)
    )
    transactions = result.scalars().all()
    
    return transactions


@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction_data: TransactionCreate,
    db: AsyncSession = Depends(get_db),
    current_user_email: str = Depends(get_current_user_email)
):
    """
    Crea una nueva transacción (solo staff/admin)
    """
    try:
        with open("transaction_debug.log", "a", encoding="utf-8") as f:
            f.write(f"\n=== CREATE TRANSACTION CALLED ===\n")
            f.write(f"User: {current_user_email}\n")
            f.write(f"Data: {transaction_data.model_dump()}\n")
        
        # Verificar que sea staff o admin
        result = await db.execute(
            select(User).where(User.email == current_user_email)
        )
        user = result.scalar_one_or_none()
        
        if not user or user.role not in ["admin", "staff"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos para crear transacciones"
            )
        
        with open("transaction_debug.log", "a", encoding="utf-8") as f:
            f.write(f"User verified: {user.role}\n")
        
        # Verificar que la orden existe
        result = await db.execute(
            select(Order).where(Order.id == transaction_data.order_id)
        )
        order = result.scalar_one_or_none()
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Orden no encontrada"
            )
        
        with open("transaction_debug.log", "a", encoding="utf-8") as f:
            f.write(f"Order found: ID={order.id}\n")
            f.write(f"Creating transaction...\n")
        
        # Generar número de transacción
        transaction_number = generate_transaction_number()
        
        # Crear transacción
        new_transaction = Transaction(
            transaction_number=transaction_number,
            **transaction_data.model_dump()
        )
        
        db.add(new_transaction)
        
        # ✅ NUEVO: Actualizar estado de la orden cuando se registra un pago
        if transaction_data.type == TransactionType.PAYMENT:
            # Marcar orden como pagada
            order.is_paid = True
            
            # Cambiar estado de PENDING a CONFIRMED si es un pago
            if order.status == OrderStatus.PENDING:
                order.status = OrderStatus.CONFIRMED
                order.confirmed_at = datetime.utcnow()
        
        with open("transaction_debug.log", "a", encoding="utf-8") as f:
            f.write(f"Transaction added, committing...\n")
            if transaction_data.type == TransactionType.PAYMENT:
                f.write(f"Order updated: is_paid={order.is_paid}, status={order.status}\n")
        
        await db.commit()
        await db.refresh(new_transaction)
        
        with open("transaction_debug.log", "a", encoding="utf-8") as f:
            f.write(f"Transaction created successfully: ID={new_transaction.id}\n")
        
        return new_transaction
    except HTTPException:
        raise
    except Exception as e:
        with open("transaction_debug.log", "a", encoding="utf-8") as f:
            import traceback
            f.write(f"\n!!! EXCEPTION !!!\n")
            f.write(f"Type: {type(e).__name__}\n")
            f.write(f"Message: {str(e)}\n")
            f.write(f"Traceback:\n{traceback.format_exc()}\n")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear transacción: {str(e)}"
        )


@router.get("/{transaction_id}", response_model=TransactionWithOrder)
async def get_transaction(
    transaction_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_email: str = Depends(get_current_user_email)
):
    """
    Obtiene detalles de una transacción
    """
    result = await db.execute(
        select(Transaction).where(Transaction.id == transaction_id)
    )
    transaction = result.scalar_one_or_none()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transacción no encontrada"
        )
    
    # Verificar permisos
    result = await db.execute(
        select(User).where(User.email == current_user_email)
    )
    user = result.scalar_one_or_none()
    
    if user.role not in ["admin", "staff"]:
        # Si es cliente, verificar que sea su transacción
        if transaction.order.customer.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos para ver esta transacción"
            )
    
    return transaction
