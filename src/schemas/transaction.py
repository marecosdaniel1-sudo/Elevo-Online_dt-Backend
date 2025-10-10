"""
Schemas para Transaction
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from src.models.transaction import TransactionType, TransactionStatus, PaymentMethod


# Schema base
class TransactionBase(BaseModel):
    order_id: int
    type: TransactionType
    payment_method: PaymentMethod
    amount: float = Field(..., gt=0)
    currency: str = Field(default="MXN", max_length=3)
    description: Optional[str] = None


# Schema para creación
class TransactionCreate(TransactionBase):
    gateway_transaction_id: Optional[str] = None


# Schema para actualización de estado
class TransactionStatusUpdate(BaseModel):
    status: TransactionStatus
    gateway_response: Optional[str] = None
    error_message: Optional[str] = None


# Schema para reembolso
class TransactionRefund(BaseModel):
    refund_reason: str = Field(..., min_length=10)
    refunded_amount: float = Field(..., gt=0)


# Schema para respuesta
class TransactionResponse(TransactionBase):
    id: int
    transaction_number: str
    status: TransactionStatus
    payment_gateway: Optional[str]
    gateway_transaction_id: Optional[str]
    notes: Optional[str]
    refund_reason: Optional[str]
    refunded_amount: float
    created_at: datetime
    updated_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Schema para lista de transacciones
class TransactionListItem(BaseModel):
    id: int
    transaction_number: str
    order_id: int
    order_number: Optional[str]
    type: TransactionType
    status: TransactionStatus
    amount: float
    payment_method: PaymentMethod
    created_at: datetime
    
    class Config:
        from_attributes = True


# Schema con detalles de orden
class TransactionWithOrder(TransactionResponse):
    order: Optional[dict] = None  # Evitamos import circular
    
    class Config:
        from_attributes = True
