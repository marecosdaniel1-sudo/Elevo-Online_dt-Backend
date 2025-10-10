"""
Script para resetear completamente la base de datos
Elimina todas las tablas y las recrea desde cero
"""
import asyncio
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine
from src.core.config import settings
from src.core.database import Base

# Importar todos los modelos para que SQLAlchemy los registre
from src.models.user import User
from src.models.customer import Customer
from src.models.scaffold import Scaffold
from src.models.order import Order, OrderItem
from src.models.transaction import Transaction
from src.models.notification import Notification


async def reset_database():
    """
    Resetea la base de datos eliminando y recreando todas las tablas
    CIERRA todas las conexiones activas primero para evitar conflictos
    """
    engine = None
    print("🗑️  Reseteando base de datos...")
    
    try:
        # Extraer info de la BD
        db_parts = settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL
        db_host = db_parts.split('/')[0]
        db_name = db_parts.split('/')[1].split('?')[0]
        print(f"📍 Conexión: {db_host}/{db_name}")
        
        # Crear engine con pool_pre_ping para detectar conexiones muertas
        engine = create_async_engine(
            settings.DATABASE_URL,
            echo=False,
            pool_pre_ping=True,  # Verifica conexiones antes de usarlas
            pool_size=5,
            max_overflow=10
        )
        
        # PASO 1: Terminar TODAS las conexiones activas (excepto la nuestra)
        print("⏳ Cerrando conexiones activas...")
        from sqlalchemy import text
        async with engine.connect() as conn:
            await conn.execute(text("""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = :dbname
                AND pid <> pg_backend_pid()
            """), {"dbname": db_name})
            await conn.commit()
        print("✓ Conexiones cerradas")
        
        # PASO 2: Eliminar todas las tablas
        print("⏳ Eliminando tablas...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        print("✓ Tablas eliminadas")
        
        # PASO 3: Crear todas las tablas
        print("⏳ Creando tablas...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✓ Tablas creadas")
        
        print("✅ Base de datos reseteada correctamente\n")
        return True
        
    except Exception as e:
        print(f"❌ Error al resetear base de datos: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # SIEMPRE cerrar el engine para liberar conexiones
        if engine:
            await engine.dispose()
            print("🔌 Conexiones liberadas\n")


if __name__ == "__main__":
    success = asyncio.run(reset_database())
    sys.exit(0 if success else 1)
