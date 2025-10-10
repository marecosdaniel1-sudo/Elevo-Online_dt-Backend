"""
Script para poblar la base de datos con datos de prueba
Incluye usuarios, clientes, andamios y pedidos de ejemplo
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from src.core.config import settings
from src.core.security import get_password_hash
from src.models.user import User
from src.models.customer import Customer
from src.models.scaffold import Scaffold, ScaffoldType
from src.models.order import Order, OrderItem, OrderStatus


async def seed_data():
    """Pobla la base de datos con datos de prueba"""
    
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            print("🌱 Poblando base de datos con datos de prueba...")
            
            # 1. Crear usuarios
            print("\n👥 Creando usuarios...")
            admin_user = User(
                email="admin@elevo.com",
                hashed_password=get_password_hash("admin123"),
                full_name="Admin Elevo",
                role="admin",
                is_active=True
            )
            session.add(admin_user)
            
            customer_user1 = User(
                email="cliente1@ejemplo.com",
                hashed_password=get_password_hash("cliente123"),
                full_name="Juan Pérez",
                role="customer",
                is_active=True
            )
            session.add(customer_user1)
            
            customer_user2 = User(
                email="cliente2@ejemplo.com",
                hashed_password=get_password_hash("cliente123"),
                full_name="María García",
                role="customer",
                is_active=True
            )
            session.add(customer_user2)
            
            await session.flush()  # Para obtener los IDs
            print(f"   ✓ Admin: {admin_user.email}")
            print(f"   ✓ Cliente 1: {customer_user1.email}")
            print(f"   ✓ Cliente 2: {customer_user2.email}")
            
            # 2. Crear clientes (perfiles de customer)
            print("\n🏢 Creando perfiles de clientes...")
            customer1 = Customer(
                user_id=customer_user1.id,
                company_name="Constructora ABC S.A.",
                tax_id="RFC123456789",
                billing_address="Av. Principal 123",
                billing_city="Ciudad de México",
                billing_state="CDMX",
                billing_postal_code="01234",
                credit_limit=50000,
                is_corporate=True
            )
            session.add(customer1)
            
            customer2 = Customer(
                user_id=customer_user2.id,
                company_name="Obras XYZ Ltda.",
                tax_id="RFC987654321",
                billing_address="Calle Secundaria 456",
                billing_city="Guadalajara",
                billing_state="Jalisco",
                billing_postal_code="44100",
                credit_limit=75000,
                is_corporate=True
            )
            session.add(customer2)
            
            await session.flush()
            print(f"   ✓ {customer1.company_name}")
            print(f"   ✓ {customer2.company_name}")
            
            # 3. Crear andamios
            print("\n🏗️  Creando catálogo de andamios...")
            scaffolds = [
                Scaffold(
                    name="Andamio Tubular Estándar",
                    sku="AND-TUB-001",
                    description="Andamio tubular de acero galvanizado, ideal para obras de mediana altura",
                    type=ScaffoldType.TUBULAR,
                    daily_rate=150.00,
                    weekly_rate=900.00,
                    monthly_rate=3000.00,
                    total_stock=50,
                    available_stock=50,
                    weight=25.5,
                    height=2.0,
                    width=1.5,
                    length=2.0,
                    load_capacity=200.0,
                    is_featured=True,
                    is_active=True
                ),
                Scaffold(
                    name="Andamio Europeo Premium",
                    sku="AND-EUR-001",
                    description="Andamio tipo europeo con plataformas de aluminio y sistema de seguridad avanzado",
                    type=ScaffoldType.EUROPEO,
                    daily_rate=250.00,
                    weekly_rate=1500.00,
                    monthly_rate=5000.00,
                    total_stock=30,
                    available_stock=30,
                    weight=35.0,
                    height=2.5,
                    width=2.0,
                    length=2.5,
                    load_capacity=300.0,
                    is_featured=True,
                    is_active=True
                ),
                Scaffold(
                    name="Torre Móvil Aluminio",
                    sku="AND-TOR-001",
                    description="Torre móvil de aluminio con ruedas, perfecta para trabajos en interiores",
                    type=ScaffoldType.MOVIL,
                    daily_rate=200.00,
                    weekly_rate=1200.00,
                    monthly_rate=4000.00,
                    total_stock=20,
                    available_stock=20,
                    weight=45.0,
                    height=3.0,
                    width=1.8,
                    length=1.8,
                    load_capacity=250.0,
                    is_featured=False,
                    is_active=True
                ),
                Scaffold(
                    name="Andamio Multidireccional",
                    sku="AND-MUL-001",
                    description="Sistema multidireccional para estructuras complejas",
                    type=ScaffoldType.MULTIDIRECCIONAL,
                    daily_rate=300.00,
                    weekly_rate=1800.00,
                    monthly_rate=6000.00,
                    total_stock=25,
                    available_stock=25,
                    weight=40.0,
                    height=3.0,
                    width=2.0,
                    length=3.0,
                    load_capacity=400.0,
                    is_featured=True,
                    is_active=True
                ),
                Scaffold(
                    name="Andamio Colgante Industrial",
                    sku="AND-COL-001",
                    description="Andamio colgante para fachadas y trabajos en altura",
                    type=ScaffoldType.COLGANTE,
                    daily_rate=350.00,
                    weekly_rate=2100.00,
                    monthly_rate=7000.00,
                    total_stock=15,
                    available_stock=15,
                    weight=55.0,
                    height=1.5,
                    width=2.5,
                    length=6.0,
                    load_capacity=500.0,
                    is_featured=False,
                    is_active=True
                ),
            ]
            
            for scaffold in scaffolds:
                session.add(scaffold)
            
            await session.flush()
            print(f"   ✓ Creados {len(scaffolds)} andamios")
            
            # 4. Crear pedidos de ejemplo
            print("\n📦 Creando pedidos de ejemplo...")
            
            # Pedido 1: Cliente 1 - Activo
            today = datetime.now()
            order1 = Order(
                order_number=f"ORD-{today.strftime('%Y%m%d')}-001",
                customer_id=customer1.id,
                status=OrderStatus.IN_USE,
                start_date=today - timedelta(days=5),
                end_date=today + timedelta(days=25),
                delivery_address="Obra Central - Av. Principal 123",
                delivery_city="Ciudad de México",
                delivery_state="CDMX",
                delivery_postal_code="01234",
                subtotal=9000.00,
                delivery_fee=500.00,
                tax_amount=1520.00,
                discount_amount=0.00,
                total_amount=11020.00,
                is_paid=True,
                payment_method="stripe",
                notes="Pedido para obra de 30 días"
            )
            session.add(order1)
            await session.flush()
            
            # Items del pedido 1
            order1_items = [
                OrderItem(
                    order_id=order1.id,
                    scaffold_id=scaffolds[0].id,
                    quantity=10,
                    unit_price=scaffolds[0].monthly_rate,
                    subtotal=3000.00
                ),
                OrderItem(
                    order_id=order1.id,
                    scaffold_id=scaffolds[1].id,
                    quantity=12,
                    unit_price=scaffolds[1].monthly_rate,
                    subtotal=6000.00
                ),
            ]
            for item in order1_items:
                session.add(item)
            
            # Pedido 2: Cliente 1 - Confirmado
            order2 = Order(
                order_number=f"ORD-{today.strftime('%Y%m%d')}-002",
                customer_id=customer1.id,
                status=OrderStatus.CONFIRMED,
                is_paid=False,
                start_date=today + timedelta(days=7),
                end_date=today + timedelta(days=21),
                delivery_address="Obra Norte - Calle Industrial 456",
                delivery_city="Ciudad de México",
                delivery_state="CDMX",
                delivery_postal_code="01235",
                subtotal=8400.00,
                delivery_fee=500.00,
                tax_amount=1424.00,
                discount_amount=200.00,
                total_amount=10124.00,
                notes="Entrega programada para la próxima semana"
            )
            session.add(order2)
            await session.flush()
            
            # Items del pedido 2
            order2_items = [
                OrderItem(
                    order_id=order2.id,
                    scaffold_id=scaffolds[2].id,
                    quantity=7,
                    unit_price=scaffolds[2].monthly_rate,
                    subtotal=8400.00
                ),
            ]
            for item in order2_items:
                session.add(item)
            
            # Pedido 3: Cliente 2 - Completado
            order3 = Order(
                order_number=f"ORD-{(today - timedelta(days=60)).strftime('%Y%m%d')}-003",
                customer_id=customer2.id,
                status=OrderStatus.COMPLETED,
                is_paid=True,
                start_date=today - timedelta(days=60),
                end_date=today - timedelta(days=30),
                delivery_address="Proyecto Sur - Av. Revolución 789",
                delivery_city="Guadalajara",
                delivery_state="Jalisco",
                delivery_postal_code="44100",
                subtotal=12000.00,
                delivery_fee=800.00,
                tax_amount=2048.00,
                discount_amount=500.00,
                total_amount=14348.00,
                notes="Proyecto completado exitosamente"
            )
            session.add(order3)
            await session.flush()
            
            # Items del pedido 3
            order3_items = [
                OrderItem(
                    order_id=order3.id,
                    scaffold_id=scaffolds[3].id,
                    quantity=2,
                    unit_price=scaffolds[3].monthly_rate,
                    subtotal=12000.00
                ),
            ]
            for item in order3_items:
                session.add(item)
            
            print(f"   ✓ Pedido {order1.order_number} - {order1.status}")
            print(f"   ✓ Pedido {order2.order_number} - {order2.status}")
            print(f"   ✓ Pedido {order3.order_number} - {order3.status}")
            
            # Commit final
            await session.commit()
            
            print("\n✅ Base de datos poblada exitosamente!")
            print("\n📋 Credenciales de acceso:")
            print("─" * 50)
            print("👑 ADMINISTRADOR:")
            print(f"   Email: {admin_user.email}")
            print("   Password: admin123")
            print("\n👤 CLIENTES:")
            print(f"   Email: {customer_user1.email}")
            print("   Password: cliente123")
            print(f"   Email: {customer_user2.email}")
            print("   Password: cliente123")
            print("─" * 50)
            
        except Exception as e:
            await session.rollback()
            print(f"\n❌ Error: {e}")
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_data())
