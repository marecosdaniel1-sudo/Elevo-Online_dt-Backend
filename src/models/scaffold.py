"""
Modelo Scaffold - Catálogo de andamios disponibles
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from src.core.database import Base


class ScaffoldType(str, enum.Enum):
    """Tipos de andamios"""
    TUBULAR = "tubular"  # Andamio tubular
    MULTIDIRECCIONAL = "multidireccional"  # Andamio multidireccional
    EUROPEO = "europeo"  # Andamio europeo
    COLGANTE = "colgante"  # Andamio colgante
    MOVIL = "movil"  # Andamio móvil
    ESCALERA = "escalera"  # Andamio tipo escalera


class ScaffoldCondition(str, enum.Enum):
    """Estado/condición del andamio"""
    NUEVO = "nuevo"
    EXCELENTE = "excelente"
    BUENO = "bueno"
    REGULAR = "regular"


class Scaffold(Base):
    """
    Tabla de andamios
    Catálogo de productos disponibles para renta
    """
    __tablename__ = "scaffolds"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Información básica
    name = Column(String(255), nullable=False)
    sku = Column(String(50), unique=True, index=True, nullable=False)  # Código de producto
    type = Column(Enum(ScaffoldType), nullable=False)
    description = Column(Text, nullable=True)
    
    # Especificaciones técnicas
    height = Column(Float, nullable=True)  # Altura en metros
    width = Column(Float, nullable=True)  # Ancho en metros
    length = Column(Float, nullable=True)  # Largo en metros
    weight = Column(Float, nullable=True)  # Peso en kg
    load_capacity = Column(Float, nullable=True)  # Capacidad de carga en kg
    material = Column(String(100), nullable=True)  # Material (acero, aluminio, etc.)
    
    # Inventario
    total_stock = Column(Integer, default=0, nullable=False)  # Cantidad total
    available_stock = Column(Integer, default=0, nullable=False)  # Cantidad disponible
    reserved_stock = Column(Integer, default=0, nullable=False)  # Cantidad reservada
    min_stock_alert = Column(Integer, default=5)  # Alerta de stock mínimo
    
    # Precios
    daily_rate = Column(Float, nullable=False)  # Tarifa por día
    weekly_rate = Column(Float, nullable=False)  # Tarifa por semana
    monthly_rate = Column(Float, nullable=False)  # Tarifa por mes
    deposit_amount = Column(Float, default=0.0)  # Depósito de garantía
    
    # Estado
    condition = Column(Enum(ScaffoldCondition), default=ScaffoldCondition.BUENO)
    is_active = Column(Boolean, default=True)  # Si está disponible para renta
    is_featured = Column(Boolean, default=False)  # Si es producto destacado
    
    # Media
    image_url = Column(String(500), nullable=True)  # URL de imagen principal
    thumbnail_url = Column(String(500), nullable=True)  # URL de miniatura
    
    # Metadata
    manufacturer = Column(String(100), nullable=True)
    model = Column(String(100), nullable=True)
    year = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    order_items = relationship("OrderItem", back_populates="scaffold", lazy="select")
    
    def __repr__(self):
        return f"<Scaffold {self.name} ({self.sku})>"
    
    @property
    def stock_status(self) -> str:
        """Retorna el estado del stock"""
        if self.available_stock == 0:
            return "sin_stock"
        elif self.available_stock <= self.min_stock_alert:
            return "stock_bajo"
        else:
            return "disponible"
