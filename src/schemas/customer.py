"""
Schemas para Customer
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# Schema base
class CustomerBase(BaseModel):
    company_name: Optional[str] = Field(None, max_length=255)
    tax_id: Optional[str] = Field(None, max_length=50)
    
    # Dirección de facturación
    billing_address: Optional[str] = None
    billing_city: Optional[str] = Field(None, max_length=100)
    billing_state: Optional[str] = Field(None, max_length=100)
    billing_postal_code: Optional[str] = Field(None, max_length=20)
    billing_country: str = Field(default="México", max_length=100)
    
    # Dirección de entrega
    shipping_address: Optional[str] = None
    shipping_city: Optional[str] = Field(None, max_length=100)
    shipping_state: Optional[str] = Field(None, max_length=100)
    shipping_postal_code: Optional[str] = Field(None, max_length=20)
    
    # Información adicional
    notes: Optional[str] = None
    is_corporate: bool = False


# Schema para creación
class CustomerCreate(CustomerBase):
    pass  # El user_id se obtiene del usuario autenticado


# Schema para actualización
class CustomerUpdate(CustomerBase):
    pass


# Schema para respuesta
class CustomerResponse(CustomerBase):
    id: int
    user_id: int
    credit_limit: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Schema mínimo para el usuario
class UserMinimal(BaseModel):
    id: int
    email: str
    full_name: str
    phone: Optional[str]
    role: str
    
    class Config:
        from_attributes = True


# Schema completo con información del usuario
class CustomerWithUser(CustomerResponse):
    user: UserMinimal
    
    class Config:
        from_attributes = True

