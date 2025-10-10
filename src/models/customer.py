"""
Modelo Customer - Clientes que rentan andamios
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.core.database import Base


class Customer(Base):
    """
    Tabla de clientes
    Contiene información adicional sobre los clientes que rentan
    """
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Información del cliente
    company_name = Column(String(255), nullable=True)  # Nombre de empresa (opcional)
    tax_id = Column(String(50), nullable=True)  # RFC o número de identificación fiscal
    
    # Dirección de facturación
    billing_address = Column(Text, nullable=True)
    billing_city = Column(String(100), nullable=True)
    billing_state = Column(String(100), nullable=True)
    billing_postal_code = Column(String(20), nullable=True)
    billing_country = Column(String(100), default="México")
    
    # Dirección de entrega por defecto
    shipping_address = Column(Text, nullable=True)
    shipping_city = Column(String(100), nullable=True)
    shipping_state = Column(String(100), nullable=True)
    shipping_postal_code = Column(String(20), nullable=True)
    
    # Información adicional
    notes = Column(Text, nullable=True)  # Notas internas sobre el cliente
    is_corporate = Column(Boolean, default=False)  # Cliente corporativo o individual
    credit_limit = Column(Integer, default=0)  # Límite de crédito (0 = sin crédito)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    user = relationship("User", back_populates="customer", lazy="select")
    orders = relationship("Order", back_populates="customer", cascade="all, delete-orphan", lazy="select")
    
    def __repr__(self):
        company = self.company_name if self.company_name else "Individual"
        return f"<Customer {company}>"
