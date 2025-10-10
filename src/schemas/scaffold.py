"""
Schemas para Scaffold
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime, date
from src.models.scaffold import ScaffoldType, ScaffoldCondition


# Schema base
class ScaffoldBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    sku: str = Field(..., min_length=2, max_length=50)
    type: ScaffoldType
    description: Optional[str] = None
    
    # Especificaciones técnicas
    height: Optional[float] = Field(None, gt=0)
    width: Optional[float] = Field(None, gt=0)
    length: Optional[float] = Field(None, gt=0)
    weight: Optional[float] = Field(None, gt=0)
    load_capacity: Optional[float] = Field(None, gt=0)
    material: Optional[str] = Field(None, max_length=100)
    
    # Precios
    daily_rate: float = Field(..., gt=0)
    weekly_rate: float = Field(..., gt=0)
    monthly_rate: float = Field(..., gt=0)
    deposit_amount: float = Field(default=0.0, ge=0)
    
    # Estado
    condition: ScaffoldCondition = ScaffoldCondition.BUENO
    is_active: bool = True
    is_featured: bool = False
    
    # Media
    image_url: Optional[str] = Field(None, max_length=500)
    thumbnail_url: Optional[str] = Field(None, max_length=500)
    
    # Metadata
    manufacturer: Optional[str] = Field(None, max_length=100)
    model: Optional[str] = Field(None, max_length=100)
    year: Optional[int] = Field(None, ge=1900, le=2100)
    
    @validator('weekly_rate')
    def validate_weekly_rate(cls, v, values):
        if 'daily_rate' in values and v > values['daily_rate'] * 7:
            raise ValueError('La tarifa semanal no puede ser mayor a 7 veces la tarifa diaria')
        return v
    
    @validator('monthly_rate')
    def validate_monthly_rate(cls, v, values):
        if 'daily_rate' in values and v > values['daily_rate'] * 30:
            raise ValueError('La tarifa mensual no puede ser mayor a 30 veces la tarifa diaria')
        return v


# Schema para creación
class ScaffoldCreate(ScaffoldBase):
    total_stock: int = Field(..., ge=0)
    available_stock: int = Field(..., ge=0)
    min_stock_alert: int = Field(default=5, ge=0)
    
    @validator('available_stock')
    def validate_available_stock(cls, v, values):
        if 'total_stock' in values and v > values['total_stock']:
            raise ValueError('El stock disponible no puede ser mayor al stock total')
        return v


# Schema para actualización
class ScaffoldUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = None
    
    # Especificaciones técnicas
    height: Optional[float] = Field(None, gt=0)
    width: Optional[float] = Field(None, gt=0)
    length: Optional[float] = Field(None, gt=0)
    weight: Optional[float] = Field(None, gt=0)
    load_capacity: Optional[float] = Field(None, gt=0)
    material: Optional[str] = Field(None, max_length=100)
    
    # Inventario
    total_stock: Optional[int] = Field(None, ge=0)
    available_stock: Optional[int] = Field(None, ge=0)
    min_stock_alert: Optional[int] = Field(None, ge=0)
    
    # Precios
    daily_rate: Optional[float] = Field(None, gt=0)
    weekly_rate: Optional[float] = Field(None, gt=0)
    monthly_rate: Optional[float] = Field(None, gt=0)
    deposit_amount: Optional[float] = Field(None, ge=0)
    
    # Estado
    condition: Optional[ScaffoldCondition] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None
    
    # Media
    image_url: Optional[str] = Field(None, max_length=500)
    thumbnail_url: Optional[str] = Field(None, max_length=500)


# Schema para respuesta
class ScaffoldResponse(ScaffoldBase):
    id: int
    total_stock: int
    available_stock: int
    reserved_stock: int
    min_stock_alert: int
    stock_status: str
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Schema para lista de andamios (simplificado)
class ScaffoldListItem(BaseModel):
    id: int
    name: str
    sku: str
    type: ScaffoldType
    daily_rate: float
    weekly_rate: float
    monthly_rate: float
    available_stock: int
    stock_status: str
    is_active: bool
    is_featured: bool
    thumbnail_url: Optional[str]
    
    class Config:
        from_attributes = True


# Schema para actualización de stock
class ScaffoldStockUpdate(BaseModel):
    total_stock: int = Field(..., ge=0)
    available_stock: int = Field(..., ge=0)
    
    @validator('available_stock')
    def validate_available_stock(cls, v, values):
        if 'total_stock' in values and v > values['total_stock']:
            raise ValueError('El stock disponible no puede ser mayor al stock total')
        return v


class ScaffoldAvailability(BaseModel):
    """Respuesta de verificación de disponibilidad"""
    scaffold_id: int
    available: bool
    available_quantity: int = Field(..., ge=0)
    requested_quantity: int = Field(..., ge=1)
    start_date: date
    end_date: date
    message: Optional[str] = None
    
    class Config:
        from_attributes = True
