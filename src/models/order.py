"""
Modelo Order - Pedidos de renta de andamios
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from datetime import datetime, timedelta
from typing import Optional

from src.core.database import Base


class OrderStatus(str, enum.Enum):
    """Estados de un pedido"""
    PENDING = "pending"  # Pendiente de confirmación
    CONFIRMED = "confirmed"  # Confirmado
    PREPARING = "preparing"  # En preparación
    IN_TRANSIT = "in_transit"  # En tránsito
    DELIVERED = "delivered"  # Entregado
    IN_USE = "in_use"  # En uso por el cliente
    RETURNED = "returned"  # Devuelto
    COMPLETED = "completed"  # Completado
    CANCELLED = "cancelled"  # Cancelado


class RentalPeriod(str, enum.Enum):
    """Periodos de renta"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


class Order(Base):
    """
    Tabla de pedidos/órdenes de renta
    """
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_number = Column(String(50), unique=True, index=True, nullable=False)  # Número de orden único
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    
    # Información del pedido
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    rental_period = Column(Enum(RentalPeriod), default=RentalPeriod.DAILY, nullable=False)
    
    # Fechas
    order_date = Column(DateTime(timezone=True), server_default=func.now())
    start_date = Column(DateTime(timezone=True), nullable=False)  # Fecha de inicio de renta
    end_date = Column(DateTime(timezone=True), nullable=False)  # Fecha de fin de renta
    actual_return_date = Column(DateTime(timezone=True), nullable=True)  # Fecha real de devolución
    
    # Dirección de entrega
    delivery_address = Column(Text, nullable=False)
    delivery_city = Column(String(100), nullable=False)
    delivery_state = Column(String(100), nullable=False)
    delivery_postal_code = Column(String(20), nullable=False)
    delivery_notes = Column(Text, nullable=True)
    
    # Costos
    subtotal = Column(Float, default=0.0, nullable=False)  # Subtotal sin delivery
    delivery_fee = Column(Float, default=0.0, nullable=False)  # Costo de envío
    discount_amount = Column(Float, default=0.0, nullable=False)  # Descuento aplicado
    tax_amount = Column(Float, default=0.0, nullable=False)  # IVA u otros impuestos
    deposit_amount = Column(Float, default=0.0, nullable=False)  # Depósito de garantía
    total_amount = Column(Float, default=0.0, nullable=False)  # Total a pagar
    
    # Información adicional
    notes = Column(Text, nullable=True)  # Notas del cliente
    internal_notes = Column(Text, nullable=True)  # Notas internas
    
    # Control de pagos
    is_paid = Column(Boolean, default=False)
    payment_method = Column(String(50), nullable=True)  # stripe, paypal, cash, transfer
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    confirmed_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relaciones
    customer = relationship("Customer", back_populates="orders", lazy="select")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan", lazy="select")
    transactions = relationship("Transaction", back_populates="order", cascade="all, delete-orphan", lazy="select")
    
    def __repr__(self):
        return f"<Order {self.order_number} - {self.status}>"
    
    @property
    def rental_days(self) -> int:
        """Calcula los días de renta"""
        delta = self.end_date - self.start_date
        return max(1, delta.days)
    
    @property
    def is_overdue(self) -> bool:
        """Verifica si el pedido está vencido"""
        if self.status in [OrderStatus.COMPLETED, OrderStatus.CANCELLED, OrderStatus.RETURNED]:
            return False
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        # Ensure end_date is timezone-aware
        end_date = self.end_date
        if end_date.tzinfo is None:
            end_date = end_date.replace(tzinfo=timezone.utc)
        return now > end_date
    
    @property
    def customer_name(self) -> Optional[str]:
        """Obtiene el nombre del customer si está cargado"""
        if self.customer and self.customer.user:
            return self.customer.user.full_name
        return None
    
    @property
    def customer_email(self) -> Optional[str]:
        """Obtiene el email del customer si está cargado"""
        if self.customer and self.customer.user:
            return self.customer.user.email
        return None


class OrderItem(Base):
    """
    Tabla de items de pedido
    Detalla cada andamio en un pedido
    """
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    scaffold_id = Column(Integer, ForeignKey("scaffolds.id", ondelete="RESTRICT"), nullable=False)
    
    # Cantidad y precios
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)  # Precio por unidad en el momento de la orden
    subtotal = Column(Float, nullable=False)  # quantity * unit_price
    
    # Información adicional
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    order = relationship("Order", back_populates="order_items", lazy="select")
    scaffold = relationship("Scaffold", back_populates="order_items", lazy="select")
    
    def __repr__(self):
        return f"<OrderItem Order:{self.order_id} Scaffold:{self.scaffold_id} Qty:{self.quantity}>"
