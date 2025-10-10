"""
Modelo Notification - Sistema de notificaciones
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from src.core.database import Base


class NotificationType(str, enum.Enum):
    """Tipos de notificación"""
    ORDER_CONFIRMATION = "order_confirmation"
    ORDER_PREPARING = "order_preparing"
    ORDER_SHIPPED = "order_shipped"
    ORDER_DELIVERED = "order_delivered"
    RETURN_REMINDER = "return_reminder"
    OVERDUE_ALERT = "overdue_alert"
    PAYMENT_RECEIVED = "payment_received"
    PAYMENT_FAILED = "payment_failed"
    DEPOSIT_RETURNED = "deposit_returned"
    GENERAL = "general"


class NotificationChannel(str, enum.Enum):
    """Canales de notificación"""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"


class NotificationStatus(str, enum.Enum):
    """Estados de notificación"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    READ = "read"


class Notification(Base):
    """
    Tabla de notificaciones
    Registra todas las notificaciones enviadas a usuarios
    """
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Información de la notificación
    type = Column(Enum(NotificationType), nullable=False)
    channel = Column(Enum(NotificationChannel), nullable=False)
    status = Column(Enum(NotificationStatus), default=NotificationStatus.PENDING, nullable=False)
    
    # Contenido
    subject = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    html_content = Column(Text, nullable=True)  # Para emails HTML
    
    # Metadata
    recipient_email = Column(String(255), nullable=True)
    recipient_phone = Column(String(20), nullable=True)
    
    # Información de envío
    sent_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    read_at = Column(DateTime(timezone=True), nullable=True)
    failed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Reintentos
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    user = relationship("User", back_populates="notifications", lazy="select")
    
    def __repr__(self):
        return f"<Notification {self.type} to User:{self.user_id} - {self.status}>"
