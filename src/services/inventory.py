"""
Servicio de gestión de inventario
Maneja la disponibilidad y reserva de andamios
"""
from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime

from src.models.scaffold import Scaffold
from src.models.order import Order, OrderItem, OrderStatus


class InventoryService:
    """
    Servicio para gestionar inventario de andamios
    """
    
    @staticmethod
    async def check_availability(
        db: AsyncSession,
        scaffold_id: int,
        quantity: int,
        start_date: datetime,
        end_date: datetime,
        exclude_order_id: Optional[int] = None
    ) -> Dict[str, any]:
        """
        Verifica la disponibilidad de un andamio para un periodo específico
        
        Returns:
            Dict con available (bool), available_quantity (int), message (str)
        """
        # Obtener el andamio
        result = await db.execute(
            select(Scaffold).where(Scaffold.id == scaffold_id)
        )
        scaffold = result.scalar_one_or_none()
        
        if not scaffold:
            return {
                "available": False,
                "available_quantity": 0,
                "message": "Andamio no encontrado"
            }
        
        if not scaffold.is_active:
            return {
                "available": False,
                "available_quantity": 0,
                "message": "Andamio no disponible para renta"
            }
        
        # Calcular cantidad reservada en el periodo
        reserved_quantity = await InventoryService._get_reserved_quantity(
            db, scaffold_id, start_date, end_date, exclude_order_id
        )
        
        # Disponible = Total - Reservado en este periodo
        available_quantity = scaffold.total_stock - reserved_quantity
        
        if available_quantity < quantity:
            return {
                "available": False,
                "available_quantity": available_quantity,
                "message": f"Solo hay {available_quantity} unidades disponibles para este periodo"
            }
        
        return {
            "available": True,
            "available_quantity": available_quantity,
            "message": "Disponible"
        }
    
    @staticmethod
    async def _get_reserved_quantity(
        db: AsyncSession,
        scaffold_id: int,
        start_date: datetime,
        end_date: datetime,
        exclude_order_id: Optional[int] = None
    ) -> int:
        """
        Calcula la cantidad reservada de un andamio en un periodo
        """
        # Estados que cuentan como "reservado"
        active_statuses = [
            OrderStatus.PENDING,
            OrderStatus.CONFIRMED,
            OrderStatus.PREPARING,
            OrderStatus.IN_TRANSIT,
            OrderStatus.DELIVERED,
            OrderStatus.IN_USE
        ]
        
        # Query para obtener items de órdenes activas que se solapan con el periodo
        query = (
            select(OrderItem)
            .join(Order)
            .where(
                and_(
                    OrderItem.scaffold_id == scaffold_id,
                    Order.status.in_(active_statuses),
                    # Verificar solapamiento de fechas
                    Order.start_date < end_date,
                    Order.end_date > start_date
                )
            )
        )
        
        if exclude_order_id:
            query = query.where(Order.id != exclude_order_id)
        
        result = await db.execute(query)
        order_items = result.scalars().all()
        
        # Sumar cantidades
        total_reserved = sum(item.quantity for item in order_items)
        
        return total_reserved
    
    @staticmethod
    async def reserve_stock(
        db: AsyncSession,
        items: List[Dict],  # [{scaffold_id: int, quantity: int}]
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, any]:
        """
        Reserva stock para un pedido
        Verifica disponibilidad de todos los items antes de reservar
        
        Returns:
            Dict con success (bool), message (str), unavailable_items (list)
        """
        unavailable_items = []
        
        # Verificar disponibilidad de todos los items
        for item in items:
            availability = await InventoryService.check_availability(
                db,
                item['scaffold_id'],
                item['quantity'],
                start_date,
                end_date
            )
            
            if not availability['available']:
                unavailable_items.append({
                    "scaffold_id": item['scaffold_id'],
                    "requested": item['quantity'],
                    "available": availability['available_quantity'],
                    "message": availability['message']
                })
        
        if unavailable_items:
            return {
                "success": False,
                "message": "Algunos items no están disponibles",
                "unavailable_items": unavailable_items
            }
        
        # Actualizar stock reservado
        for item in items:
            result = await db.execute(
                select(Scaffold).where(Scaffold.id == item['scaffold_id'])
            )
            scaffold = result.scalar_one()
            
            scaffold.reserved_stock += item['quantity']
            scaffold.available_stock -= item['quantity']
        
        await db.commit()
        
        return {
            "success": True,
            "message": "Stock reservado exitosamente",
            "unavailable_items": []
        }
    
    @staticmethod
    async def release_stock(
        db: AsyncSession,
        items: List[Dict]  # [{scaffold_id: int, quantity: int}]
    ) -> None:
        """
        Libera stock reservado (cuando se cancela o completa un pedido)
        """
        for item in items:
            result = await db.execute(
                select(Scaffold).where(Scaffold.id == item['scaffold_id'])
            )
            scaffold = result.scalar_one_or_none()
            
            if scaffold:
                scaffold.reserved_stock -= item['quantity']
                scaffold.available_stock += item['quantity']
                
                # Asegurar que no haya valores negativos
                scaffold.reserved_stock = max(0, scaffold.reserved_stock)
                scaffold.available_stock = min(
                    scaffold.total_stock,
                    scaffold.available_stock
                )
        
        await db.commit()
    
    @staticmethod
    async def update_stock_levels(
        db: AsyncSession,
        scaffold_id: int,
        total_stock: int,
        available_stock: int
    ) -> Scaffold:
        """
        Actualiza los niveles de stock de un andamio
        """
        result = await db.execute(
            select(Scaffold).where(Scaffold.id == scaffold_id)
        )
        scaffold = result.scalar_one()
        
        scaffold.total_stock = total_stock
        scaffold.available_stock = available_stock
        scaffold.reserved_stock = total_stock - available_stock
        
        await db.commit()
        await db.refresh(scaffold)
        
        return scaffold
    
    @staticmethod
    async def get_low_stock_alerts(db: AsyncSession) -> List[Scaffold]:
        """
        Obtiene andamios con stock bajo
        """
        result = await db.execute(
            select(Scaffold).where(
                and_(
                    Scaffold.is_active == True,
                    Scaffold.available_stock <= Scaffold.min_stock_alert
                )
            )
        )
        
        return result.scalars().all()
