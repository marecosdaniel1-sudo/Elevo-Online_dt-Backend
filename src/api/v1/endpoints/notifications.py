"""
Endpoints de notificaciones
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List

from src.core.database import get_db
from src.core.security import get_current_user_email
from src.models.notification import Notification, NotificationStatus
from src.models.user import User
from src.schemas.notification import (
    NotificationCreate,
    NotificationUpdate,
    NotificationResponse
)

router = APIRouter()


@router.get("/my-notifications", response_model=List[NotificationResponse])
async def get_my_notifications(
    unread_only: bool = False,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user_email: str = Depends(get_current_user_email)
):
    """
    Obtiene las notificaciones del usuario actual
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
    
    # Construir query
    query = select(Notification).where(Notification.user_id == user.id)
    
    if unread_only:
        query = query.where(Notification.status == NotificationStatus.UNREAD)
    
    query = query.offset(skip).limit(limit).order_by(Notification.created_at.desc())
    
    result = await db.execute(query)
    notifications = result.scalars().all()
    
    return notifications


@router.post("/", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_notification(
    notification_data: NotificationCreate,
    db: AsyncSession = Depends(get_db),
    current_user_email: str = Depends(get_current_user_email)
):
    """
    Crea una nueva notificación (solo staff/admin)
    """
    # Verificar que sea staff o admin
    result = await db.execute(
        select(User).where(User.email == current_user_email)
    )
    user = result.scalar_one_or_none()
    
    if not user or user.role not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para crear notificaciones"
        )
    
    # Verificar que el usuario destino existe
    result = await db.execute(
        select(User).where(User.id == notification_data.user_id)
    )
    target_user = result.scalar_one_or_none()
    
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario destino no encontrado"
        )
    
    # Crear notificación
    new_notification = Notification(
        **notification_data.model_dump()
    )
    
    db.add(new_notification)
    await db.commit()
    await db.refresh(new_notification)
    
    return new_notification


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
async def mark_as_read(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_email: str = Depends(get_current_user_email)
):
    """
    Marca una notificación como leída
    """
    # Obtener usuario actual
    result = await db.execute(
        select(User).where(User.email == current_user_email)
    )
    user = result.scalar_one_or_none()
    
    # Obtener notificación
    result = await db.execute(
        select(Notification).where(
            and_(
                Notification.id == notification_id,
                Notification.user_id == user.id
            )
        )
    )
    notification = result.scalar_one_or_none()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificación no encontrada"
        )
    
    # Marcar como leída
    notification.status = NotificationStatus.READ
    
    await db.commit()
    await db.refresh(notification)
    
    return notification


@router.post("/mark-all-read")
async def mark_all_as_read(
    db: AsyncSession = Depends(get_db),
    current_user_email: str = Depends(get_current_user_email)
):
    """
    Marca todas las notificaciones del usuario como leídas
    """
    # Obtener usuario actual
    result = await db.execute(
        select(User).where(User.email == current_user_email)
    )
    user = result.scalar_one_or_none()
    
    # Actualizar todas las notificaciones no leídas
    result = await db.execute(
        select(Notification).where(
            and_(
                Notification.user_id == user.id,
                Notification.status == NotificationStatus.UNREAD
            )
        )
    )
    notifications = result.scalars().all()
    
    for notification in notifications:
        notification.status = NotificationStatus.READ
    
    await db.commit()
    
    return {"message": f"{len(notifications)} notificaciones marcadas como leídas"}
