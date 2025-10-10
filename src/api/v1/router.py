"""
Router principal de API v1
Agrupa todos los endpoints
"""
from fastapi import APIRouter

from src.api.v1.endpoints import (
    auth,
    scaffolds,
    orders,
    customers,
    inventory,
    transactions,
    notifications
)

api_router = APIRouter()

# Incluir routers de cada módulo
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["auth"]
)

api_router.include_router(
    scaffolds.router,
    prefix="/scaffolds",
    tags=["scaffolds"]
)

api_router.include_router(
    orders.router,
    prefix="/orders",
    tags=["orders"]
)

api_router.include_router(
    customers.router,
    prefix="/customers",
    tags=["customers"]
)

api_router.include_router(
    inventory.router,
    prefix="/inventory",
    tags=["scaffolds"]  # Agrupado con scaffolds
)

api_router.include_router(
    transactions.router,
    prefix="/transactions",
    tags=["transactions"]
)

api_router.include_router(
    notifications.router,
    prefix="/notifications",
    tags=["notifications"]
)
