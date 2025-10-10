"""
Schemas para Notification
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from src.models.notification import NotificationType, NotificationChannel, NotificationStatus


# Schema base
class NotificationBase(BaseModel):
    user_id: int
    type: NotificationType
    channel: NotificationChannel
    subject: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1)


# Schema para creación
class NotificationCreate(NotificationBase):
    html_content: Optional[str] = None
    recipient_email: Optional[EmailStr] = None
    recipient_phone: Optional[str] = None


# Schema para actualización de estado
class NotificationStatusUpdate(BaseModel):
    status: NotificationStatus
    error_message: Optional[str] = None


# Schema para actualización general (marcar como leída)
class NotificationUpdate(BaseModel):
    read_at: Optional[datetime] = None
    status: Optional[NotificationStatus] = None


# Schema para respuesta
class NotificationResponse(NotificationBase):
    id: int
    status: NotificationStatus
    html_content: Optional[str]
    recipient_email: Optional[str]
    recipient_phone: Optional[str]
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    read_at: Optional[datetime]
    failed_at: Optional[datetime]
    error_message: Optional[str]
    retry_count: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Schema para marcar como leída
class NotificationMarkAsRead(BaseModel):
    notification_id: int
