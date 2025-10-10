"""
Endpoints de inventario
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime

from src.core.database import get_db
from src.core.security import get_current_user_email
from src.models.scaffold import Scaffold
from src.schemas.scaffold import ScaffoldResponse, ScaffoldStockUpdate
from src.services.inventory import InventoryService

router = APIRouter()


@router.get("/check-availability/{scaffold_id}")
async def check_availability(
    scaffold_id: int,
    quantity: int = Query(..., gt=0),
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Verifica disponibilidad de un andamio para un periodo específico
    """
    availability = await InventoryService.check_availability(
        db,
        scaffold_id,
        quantity,
        start_date,
        end_date
    )
    
    return availability


@router.get("/low-stock", response_model=List[ScaffoldResponse])
async def get_low_stock_alerts(
    db: AsyncSession = Depends(get_db),
    current_user_email: str = Depends(get_current_user_email)
):
    """
    Obtiene andamios con stock bajo
    Requiere autenticación de admin/staff
    """
    scaffolds = await InventoryService.get_low_stock_alerts(db)
    return scaffolds


@router.patch("/{scaffold_id}/stock", response_model=ScaffoldResponse)
async def update_stock(
    scaffold_id: int,
    stock_data: ScaffoldStockUpdate,
    db: AsyncSession = Depends(get_db),
    current_user_email: str = Depends(get_current_user_email)
):
    """
    Actualiza niveles de stock de un andamio
    Requiere autenticación de admin/staff
    """
    scaffold = await InventoryService.update_stock_levels(
        db,
        scaffold_id,
        stock_data.total_stock,
        stock_data.available_stock
    )
    
    return scaffold
