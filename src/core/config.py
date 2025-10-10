"""
Configuración de la aplicación
Gestiona variables de entorno y configuraciones globales
"""
from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    """
    Configuración de la aplicación usando Pydantic Settings
    Lee automáticamente desde variables de entorno y archivo .env
    """
    # App Settings
    APP_NAME: str = "Elevo Online"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/elevo_online"
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str = "elevo_online"
    DATABASE_USER: str = "user"
    DATABASE_PASSWORD: str = "password"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # Email Configuration
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "noreply@elevoonline.com"
    
    # File Upload
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 5242880  # 5MB
    
    # Redis (opcional)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Payment Gateway
    PAYMENT_GATEWAY: str = "stripe"
    STRIPE_SECRET_KEY: str = ""
    STRIPE_PUBLIC_KEY: str = ""
    
    # Business Logic - Pricing
    BASE_DAILY_RATE: float = 50.0  # Tarifa base por día
    BASE_WEEKLY_RATE: float = 300.0  # Tarifa base por semana
    BASE_MONTHLY_RATE: float = 1000.0  # Tarifa base por mes
    DELIVERY_FEE: float = 100.0  # Costo de envío base
    
    # Discounts
    WEEKLY_DISCOUNT: float = 0.10  # 10% descuento para renta semanal
    MONTHLY_DISCOUNT: float = 0.20  # 20% descuento para renta mensual
    BULK_DISCOUNT_THRESHOLD: int = 10  # Descuento por volumen a partir de 10 unidades
    BULK_DISCOUNT_RATE: float = 0.15  # 15% descuento por volumen
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignorar campos extra en .env que no están definidos en Settings


@lru_cache()
def get_settings() -> Settings:
    """
    Obtiene la configuración de la aplicación (singleton con caché)
    """
    return Settings()


# Instancia global de configuración
settings = get_settings()
