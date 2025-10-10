"""
Elevo Online - Sistema de Renta de Andamios
Punto de entrada principal de la aplicación
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from src.core.config import settings
from src.core.database import engine, Base
from src.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestiona el ciclo de vida de la aplicación
    """
    # Startup
    print("🚀 Iniciando Elevo Online...")
    
    # Crear tablas en la base de datos (solo para desarrollo)
    # En producción, usar Alembic migrations
    if settings.DEBUG:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    # Crear directorio de uploads si no existe
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    print("✅ Aplicación iniciada correctamente")
    
    yield
    
    # Shutdown
    print("🛑 Cerrando Elevo Online...")
    await engine.dispose()


# Crear instancia de FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
## 🏗️ Elevo Online - API REST para Sistema de Renta de Andamios

Sistema completo de gestión de alquiler de andamios de construcción.

### 🚀 Características principales

- **Autenticación JWT** - Seguridad basada en tokens
- **Gestión de usuarios** - ADMIN, STAFF, CUSTOMER
- **Catálogo de andamios** - 5 tipos diferentes con control de stock
- **Sistema de órdenes** - Flujo completo desde cotización hasta entrega
- **Pagos y transacciones** - Registro de todos los movimientos
- **Notificaciones** - Sistema de alertas configurable

### 📚 Documentación completa

- **Guía de API**: `/docs/API_GUIDE.md`
- **Arquitectura**: `/docs/ARCHITECTURE.md`
- **Changelog**: `/docs/CHANGELOG.md`

### 🔐 Autenticación

1. **Registrarse**: `POST /api/v1/auth/register`
2. **Login**: `POST /api/v1/auth/login` → Obtener token JWT
3. **Usar token**: Agregar header `Authorization: Bearer <token>` en todas las requests

### 🧪 Testing

- **43 tests E2E** con 100% de éxito
- **Ejecutar tests**: `test.bat`
- **Reset BD**: `reset.bat`

### 🛠️ Scripts de utilidad

- **start.bat** - Iniciar servidor en http://localhost:8000
- **test.bat** - Ejecutar suite completa de tests
- **reset.bat** - Resetear base de datos con datos de prueba

---

**Desarrollado con FastAPI + PostgreSQL + SQLAlchemy**
    """,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
    contact={
        "name": "Elevo Online",
        "url": "https://github.com/tu-repo/elevo-online",
        "email": "support@elevoonline.com"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    },
    openapi_tags=[
        {
            "name": "auth",
            "description": "**Autenticación y autorización** - Registro, login, obtención de token JWT"
        },
        {
            "name": "users",
            "description": "**Gestión de usuarios** - CRUD de usuarios del sistema (ADMIN, STAFF, CUSTOMER)"
        },
        {
            "name": "customers",
            "description": "**Clientes** - Información de empresas que rentan andamios"
        },
        {
            "name": "scaffolds",
            "description": "**Catálogo de andamios** - Tipos, precios, stock disponible"
        },
        {
            "name": "orders",
            "description": "**Órdenes de renta** - Creación, seguimiento y gestión de pedidos"
        },
        {
            "name": "transactions",
            "description": "**Transacciones** - Registro de pagos y movimientos financieros"
        },
        {
            "name": "notifications",
            "description": "**Notificaciones** - Sistema de alertas y comunicación"
        }
    ]
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar directorio de archivos estáticos
if os.path.exists(settings.UPLOAD_DIR):
    app.mount(
        "/uploads",
        StaticFiles(directory=settings.UPLOAD_DIR),
        name="uploads"
    )

# Incluir routers de API
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    """
    Endpoint raíz de la API
    """
    return {
        "message": "Bienvenido a Elevo Online API",
        "version": settings.APP_VERSION,
        "docs": "/api/docs"
    }


@app.get("/health")
async def health_check():
    """
    Endpoint para verificar el estado de la aplicación
    """
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
