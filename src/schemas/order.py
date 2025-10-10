"""
Schemas para Order y OrderItem
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from src.models.order import OrderStatus, RentalPeriod


# Schema para OrderItem
class OrderItemBase(BaseModel):
    scaffold_id: int
    quantity: int = Field(..., gt=0)
    notes: Optional[str] = None


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemResponse(OrderItemBase):
    id: int
    order_id: int
    unit_price: float
    subtotal: float
    scaffold_name: Optional[str] = None
    scaffold_sku: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Schema para Order
class OrderBase(BaseModel):
    start_date: datetime
    end_date: datetime
    rental_period: RentalPeriod = RentalPeriod.DAILY
    
    # Dirección de entrega
    delivery_address: str = Field(..., min_length=10)
    delivery_city: str = Field(..., min_length=2, max_length=100)
    delivery_state: str = Field(..., min_length=2, max_length=100)
    delivery_postal_code: str = Field(..., max_length=20)
    delivery_notes: Optional[str] = None
    
    # Notas
    notes: Optional[str] = None
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('La fecha de fin debe ser posterior a la fecha de inicio')
        return v


class OrderCreate(OrderBase):
    customer_id: int
    items: List[OrderItemCreate] = Field(..., min_items=1)
    payment_method: Optional[str] = Field(None, max_length=50)


class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    delivery_address: Optional[str] = None
    delivery_city: Optional[str] = None
    delivery_state: Optional[str] = None
    delivery_postal_code: Optional[str] = None
    delivery_notes: Optional[str] = None
    notes: Optional[str] = None
    internal_notes: Optional[str] = None


class OrderResponse(OrderBase):
    id: int
    order_number: str
    customer_id: int
    status: OrderStatus
    order_date: datetime
    actual_return_date: Optional[datetime]
    
    # Costos
    subtotal: float
    delivery_fee: float
    discount_amount: float
    tax_amount: float
    deposit_amount: float
    total_amount: float
    
    # Información adicional
    internal_notes: Optional[str]
    is_paid: bool
    payment_method: Optional[str]
    rental_days: int
    is_overdue: bool
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime]
    confirmed_at: Optional[datetime]
    delivered_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class OrderWithItems(OrderResponse):
    items: List[OrderItemResponse] = []
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None


class OrderListItem(BaseModel):
    id: int
    order_number: str
    customer_id: int
    customer_name: Optional[str]
    status: OrderStatus
    start_date: datetime
    end_date: datetime
    total_amount: float
    is_paid: bool
    is_overdue: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Schema para cálculo de precio
class OrderPriceCalculation(BaseModel):
    items: List[OrderItemCreate]
    start_date: datetime
    end_date: datetime
    rental_period: RentalPeriod
    delivery_postal_code: str


class OrderPriceResponse(BaseModel):
    subtotal: float
    delivery_fee: float
    discount_amount: float
    discount_percentage: float
    tax_amount: float
    deposit_amount: float
    total_amount: float
    rental_days: int
    breakdown: List[dict]  # Desglose por item
