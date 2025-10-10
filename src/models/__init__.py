"""
Módulo de modelos de base de datos
Importa todos los modelos en el orden correcto para evitar problemas de dependencias circulares
"""

# Importar Base primero
from src.core.database import Base

# Importar modelos en orden de dependencias
# 1. Modelos sin dependencias
from src.models.user import User, UserRole
from src.models.scaffold import Scaffold, ScaffoldType, ScaffoldCondition

# 2. Modelos que dependen de User
from src.models.customer import Customer

# 3. Modelos que dependen de Customer y Scaffold  
from src.models.order import Order, OrderItem, OrderStatus, RentalPeriod

# 4. Modelos que dependen de Order
from src.models.transaction import Transaction, TransactionType, TransactionStatus, PaymentMethod

# 5. Modelos que dependen de User
from src.models.notification import Notification, NotificationType, NotificationChannel, NotificationStatus

__all__ = [
    # Base
    "Base",
    
    # User models
    "User",
    "UserRole",
    
    # Customer models
    "Customer",
    
    # Scaffold models
    "Scaffold",
    "ScaffoldType",
    "ScaffoldCondition",
    
    # Order models
    "Order",
    "OrderItem",
    "OrderStatus",
    "RentalPeriod",
    
    # Transaction models
    "Transaction",
    "TransactionType",
    "TransactionStatus",
    "PaymentMethod",
    
    # Notification models
    "Notification",
    "NotificationType",
    "NotificationChannel",
    "NotificationStatus",
]
