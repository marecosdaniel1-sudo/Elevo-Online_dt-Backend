"""
Modelo Transaction - Transacciones de pago
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from src.core.database import Base


class TransactionType(str, enum.Enum):
    """Tipos de transacción"""
    PAYMENT = "payment"  # Pago
    REFUND = "refund"  # Reembolso
    DEPOSIT = "deposit"  # Depósito de garantía
    DEPOSIT_RETURN = "deposit_return"  # Devolución de depósito
    LATE_FEE = "late_fee"  # Cargo por retraso
    DAMAGE_FEE = "damage_fee"  # Cargo por daños


class TransactionStatus(str, enum.Enum):
    """Estados de transacción"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentMethod(str, enum.Enum):
    """Métodos de pago"""
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PAYPAL = "paypal"
    STRIPE = "stripe"
    BANK_TRANSFER = "bank_transfer"
    CASH = "cash"
    CHECK = "check"


class Transaction(Base):
    """
    Tabla de transacciones
    Registra todos los movimientos financieros relacionados con pedidos
    """
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    transaction_number = Column(String(50), unique=True, index=True, nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    
    # Información de la transacción
    type = Column(Enum(TransactionType), nullable=False)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING, nullable=False)
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    
    # Montos
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="MXN", nullable=False)  # ISO 4217
    
    # Información del procesador de pagos
    payment_gateway = Column(String(50), nullable=True)  # stripe, paypal, etc.
    gateway_transaction_id = Column(String(255), nullable=True)  # ID de transacción del gateway
    gateway_response = Column(Text, nullable=True)  # Respuesta completa del gateway (JSON)
    
    # Metadata
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Información de reembolso
    refund_reason = Column(Text, nullable=True)
    refunded_amount = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relaciones
    order = relationship("Order", back_populates="transactions", lazy="select")
    
    def __repr__(self):
        return f"<Transaction {self.transaction_number} - {self.type} - {self.status}>"
