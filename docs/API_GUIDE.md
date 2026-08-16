refs/users/12/1000012, y# 📖 Guía de Uso - Elevo Online API

Documentación completa para usar la API REST de Elevo Online.

---

## 🚀 Inicio Rápido

### 1. Iniciar el Servidor

```bash
.\start.bat
```

**URLs importantes:**
- **API Base:** http://localhost:8000
- **Swagger UI:** http://localhost:8000/docs 🎯 ← Recomendado
- **ReDoc:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

### 2. Ejecutar Tests

```bash
.\test.bat
```

**Resultado esperado:** 43/43 tests (100%)

### 3. Resetear Base de Datos

```bash
.\reset.bat
```

---

## 🔐 Autenticación

La API usa **JWT (JSON Web Tokens)** para autenticación.

### Registro de Usuario

**Endpoint:** `POST /api/v1/auth/register`

**Body:**
```json
{
  "email": "cliente@ejemplo.com",
  "password": "MiPassword123!",
  "full_name": "Juan Pérez",
  "role": "customer"
}
```

**Roles disponibles:**
- `customer` - Cliente (usuario normal)
- `staff` - Personal (gestión básica)
- `admin` - Administrador (acceso total)

**Respuesta (201):**
```json
{
  "id": 1,
  "email": "cliente@ejemplo.com",
  "full_name": "Juan Pérez",
  "role": "customer",
  "is_active": true,
  "is_verified": false,
  "created_at": "2025-10-09T12:00:00Z"
}
```

### Login

**Endpoint:** `POST /api/v1/auth/login`

**Body:**
```json
{
  "email": "cliente@ejemplo.com",
  "password": "MiPassword123!"
}
```

**Respuesta (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "cliente@ejemplo.com",
    "full_name": "Juan Pérez",
    "role": "customer"
  }
}
```

### Usar el Token

Incluye el token en el header `Authorization` de todas las requests:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Ejemplo con fetch:**
```javascript
fetch('http://localhost:8000/api/v1/customers/me', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
})
```

**Ejemplo con curl:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/api/v1/customers/me
```

---

## 👤 Usuarios

### Obtener Mi Perfil

**Endpoint:** `GET /api/v1/users/me`  
**Auth:** ✅ Requerida

**Respuesta (200):**
```json
{
  "id": 1,
  "email": "cliente@ejemplo.com",
  "full_name": "Juan Pérez",
  "role": "customer",
  "is_active": true,
  "is_verified": false,
  "created_at": "2025-10-09T12:00:00Z"
}
```

### Listar Usuarios (Admin)

**Endpoint:** `GET /api/v1/users`  
**Auth:** ✅ Admin solamente  
**Query Params:**
- `skip` (int): Offset para paginación (default: 0)
- `limit` (int): Límite de resultados (default: 100)

---

## 🏢 Clientes

### Obtener Mi Perfil de Cliente

**Endpoint:** `GET /api/v1/customers/me`  
**Auth:** ✅ Requerida (rol: customer)

**Respuesta (200):**
```json
{
  "id": 1,
  "user_id": 1,
  "company_name": "Construcciones ABC",
  "tax_id": "ABC123456789",
  "billing_address": "Calle Principal 123",
  "billing_city": "Ciudad de México",
  "billing_state": "CDMX",
  "billing_postal_code": "12345",
  "shipping_address": "Calle Principal 123",
  "shipping_city": "Ciudad de México",
  "is_corporate": true,
  "credit_limit": 0,
  "created_at": "2025-10-09T12:00:00Z"
}
```

### Actualizar Mi Perfil

**Endpoint:** `PUT /api/v1/customers/me`  
**Auth:** ✅ Requerida (rol: customer)

**Body:**
```json
{
  "company_name": "Construcciones ABC S.A.",
  "tax_id": "ABC123456789",
  "billing_address": "Calle Principal 123, Col. Centro",
  "billing_city": "Ciudad de México",
  "billing_state": "CDMX",
  "billing_postal_code": "12345",
  "shipping_address": "Av. Construcción 456",
  "shipping_city": "Ciudad de México"
}
```

### Listar Clientes (Admin/Staff)

**Endpoint:** `GET /api/v1/customers`  
**Auth:** ✅ Admin o Staff

---

## 🏗️ Andamios (Inventario)

### Listar Andamios (Público)

**Endpoint:** `GET /api/v1/scaffolds`  
**Auth:** ❌ No requerida  
**Query Params:**
- `type` (string): Filtrar por tipo
- `skip` (int): Offset
- `limit` (int): Límite
- `available_only` (bool): Solo disponibles

**Tipos disponibles:**
- `TUBULAR` - Andamio tubular
- `MULTIDIRECCIONAL` - Sistema multidireccional
- `COLGANTE` - Andamio colgante
- `TORRE_MOVIL` - Torre móvil
- `EUROPEO` - Sistema europeo

**Respuesta (200):**
```json
[
  {
    "id": 1,
    "name": "Andamio Tubular Estándar 2m",
    "sku": "AND-TUB-STD-2M",
    "type": "TUBULAR",
    "description": "Andamio tubular de acero galvanizado",
    "height": 2.0,
    "width": 0.7,
    "length": 1.5,
    "weight": 25.0,
    "load_capacity": 200.0,
    "material": "Acero galvanizado",
    "total_stock": 50,
    "available_stock": 50,
    "reserved_stock": 0,
    "daily_rate": 150.00,
    "weekly_rate": 900.00,
    "monthly_rate": 3000.00,
    "condition": "EXCELENTE",
    "is_active": true
  }
]
```

### Obtener Andamio Específico

**Endpoint:** `GET /api/v1/scaffolds/{id}`  
**Auth:** ❌ No requerida

### Crear Andamio

**Endpoint:** `POST /api/v1/scaffolds`  
**Auth:** ✅ Staff o Admin

**Body:**
```json
{
  "name": "Torre Móvil 5m",
  "sku": "TOR-MOV-5M",
  "type": "TORRE_MOVIL",
  "description": "Torre móvil de aluminio con ruedas",
  "height": 5.0,
  "width": 1.5,
  "length": 1.5,
  "weight": 55.0,
  "load_capacity": 250.0,
  "material": "Aluminio",
  "total_stock": 10,
  "available_stock": 10,
  "daily_rate": 350.00,
  "weekly_rate": 2100.00,
  "monthly_rate": 7000.00,
  "condition": "NUEVO",
  "is_active": true
}
```

### Actualizar Andamio

**Endpoint:** `PUT /api/v1/scaffolds/{id}`  
**Auth:** ✅ Staff o Admin

### Eliminar Andamio

**Endpoint:** `DELETE /api/v1/scaffolds/{id}`  
**Auth:** ✅ Admin solamente

### Verificar Disponibilidad

**Endpoint:** `GET /api/v1/scaffolds/{id}/available`  
**Query Params:**
- `quantity` (int): Cantidad requerida
- `start_date` (string): Fecha inicio (YYYY-MM-DD)
- `end_date` (string): Fecha fin (YYYY-MM-DD)

**Respuesta (200):**
```json
{
  "available": true,
  "quantity_available": 50,
  "quantity_requested": 5
}
```

---

## 💰 Cálculo de Precios

### Calcular Precio de Renta

**Endpoint:** `POST /api/v1/scaffolds/calculate-price`  
**Auth:** ❌ No requerida

**Body:**
```json
{
  "items": [
    {
      "scaffold_id": 1,
      "quantity": 5
    },
    {
      "scaffold_id": 2,
      "quantity": 3
    }
  ],
  "rental_period": "MENSUAL",
  "start_date": "2025-10-15",
  "end_date": "2025-11-15"
}
```

**Períodos válidos:**
- `DIARIO` - Por día
- `SEMANAL` - Por semana (7 días)
- `MENSUAL` - Por mes (30 días)

**Respuesta (200):**
```json
{
  "subtotal": 15000.00,
  "tax": 2400.00,
  "discount": 0.00,
  "total": 17400.00,
  "rental_period": "MENSUAL",
  "days": 31,
  "items": [
    {
      "scaffold_id": 1,
      "name": "Andamio Tubular Estándar 2m",
      "quantity": 5,
      "unit_price": 3000.00,
      "subtotal": 15000.00
    }
  ]
}
```

---

## 📦 Órdenes

### Crear Orden

**Endpoint:** `POST /api/v1/orders`  
**Auth:** ✅ Customer

**Body:**
```json
{
  "items": [
    {
      "scaffold_id": 1,
      "quantity": 5
    },
    {
      "scaffold_id": 2,
      "quantity": 3
    }
  ],
  "rental_period": "MENSUAL",
  "start_date": "2025-10-15",
  "end_date": "2025-11-15",
  "shipping_address": "Obra Construcción Norte, Calle 123",
  "shipping_city": "Ciudad de México",
  "notes": "Entrega temprano en la mañana"
}
```

**Respuesta (201):**
```json
{
  "id": 1,
  "customer_id": 1,
  "status": "PENDIENTE",
  "rental_period": "MENSUAL",
  "start_date": "2025-10-15",
  "end_date": "2025-11-15",
  "subtotal": 21000.00,
  "tax": 3360.00,
  "discount": 0.00,
  "total": 24360.00,
  "shipping_address": "Obra Construcción Norte, Calle 123",
  "items": [
    {
      "id": 1,
      "scaffold_id": 1,
      "scaffold_name": "Andamio Tubular Estándar 2m",
      "quantity": 5,
      "unit_price": 3000.00,
      "subtotal": 15000.00
    },
    {
      "id": 2,
      "scaffold_id": 2,
      "scaffold_name": "Andamio Multidireccional 3m",
      "quantity": 3,
      "unit_price": 5000.00,
      "subtotal": 15000.00
    }
  ],
  "created_at": "2025-10-09T12:00:00Z"
}
```

### Listar Mis Órdenes

**Endpoint:** `GET /api/v1/orders`  
**Auth:** ✅ Requerida  
**Query Params:**
- `status` (string): Filtrar por estado
- `skip` (int): Offset
- `limit` (int): Límite

**Estados de Orden:**
- `PENDIENTE` - Orden creada, esperando confirmación
- `CONFIRMADA` - Cliente confirmó la orden
- `APROBADA` - Admin/Staff aprobó la orden
- `EN_PROCESO` - Preparando/entregando
- `COMPLETADA` - Orden finalizada
- `CANCELADA` - Orden cancelada

### Obtener Orden Específica

**Endpoint:** `GET /api/v1/orders/{id}`  
**Auth:** ✅ Requerida (solo propia o admin)

### Actualizar Estado de Orden

**Endpoint:** `PUT /api/v1/orders/{id}`  
**Auth:** ✅ Customer (propia) o Admin/Staff

**Body:**
```json
{
  "status": "CONFIRMADA"
}
```

### Aprobar Orden (Admin/Staff)

**Endpoint:** `POST /api/v1/orders/{id}/approve`  
**Auth:** ✅ Admin o Staff

**Respuesta (200):**
```json
{
  "id": 1,
  "status": "APROBADA",
  "message": "Orden aprobada exitosamente"
}
```

### Cancelar Orden

**Endpoint:** `POST /api/v1/orders/{id}/cancel`  
**Auth:** ✅ Requerida (propia o admin)

**Body (opcional):**
```json
{
  "reason": "Cliente cambió de opinión"
}
```

---

## 💳 Transacciones

### Crear Transacción (Pago)

**Endpoint:** `POST /api/v1/transactions`  
**Auth:** ✅ Admin o Staff

**Body:**
```json
{
  "order_id": 1,
  "transaction_type": "PAGO",
  "payment_method": "TRANSFERENCIA",
  "amount": 24360.00,
  "reference": "REF-20251009-001",
  "notes": "Pago completo de la orden"
}
```

**Tipos de Transacción:**
- `PAGO` - Pago de cliente
- `REEMBOLSO` - Devolución de dinero
- `DEPOSITO` - Depósito de garantía
- `DEVOLUCION_DEPOSITO` - Devolución de depósito

**Métodos de Pago:**
- `EFECTIVO` - Pago en efectivo
- `TRANSFERENCIA` - Transferencia bancaria
- `TARJETA` - Tarjeta de crédito/débito
- `CHEQUE` - Cheque

**Respuesta (201):**
```json
{
  "id": 1,
  "order_id": 1,
  "transaction_type": "PAGO",
  "payment_method": "TRANSFERENCIA",
  "amount": 24360.00,
  "status": "COMPLETADA",
  "reference": "REF-20251009-001",
  "created_at": "2025-10-09T12:00:00Z"
}
```

### Listar Transacciones de una Orden

**Endpoint:** `GET /api/v1/orders/{order_id}/transactions`  
**Auth:** ✅ Requerida (propia o admin)

---

## 🔔 Notificaciones

### Crear Notificación

**Endpoint:** `POST /api/v1/notifications`  
**Auth:** ✅ Admin o Staff

**Body:**
```json
{
  "user_id": 1,
  "type": "ORDEN",
  "title": "Orden Aprobada",
  "message": "Tu orden #1 ha sido aprobada y está en proceso",
  "channel": "EMAIL",
  "priority": "NORMAL"
}
```

**Tipos:**
- `ORDEN` - Relacionada con órdenes
- `PAGO` - Relacionada con pagos
- `INVENTARIO` - Stock bajo, etc.
- `SISTEMA` - Mantenimiento, actualizaciones
- `PROMOCION` - Ofertas especiales

**Canales:**
- `EMAIL` - Correo electrónico
- `PUSH` - Notificación push
- `SMS` - Mensaje de texto
- `IN_APP` - Dentro de la aplicación

**Prioridades:**
- `BAJA` - Informativa
- `NORMAL` - Estándar
- `ALTA` - Importante
- `URGENTE` - Requiere acción inmediata

### Listar Mis Notificaciones

**Endpoint:** `GET /api/v1/notifications/me`  
**Auth:** ✅ Requerida  
**Query Params:**
- `status` (string): `PENDIENTE`, `LEIDA`, `ARCHIVADA`
- `skip` (int): Offset
- `limit` (int): Límite

---

## 🔍 Códigos de Estado HTTP

| Código | Significado | Cuándo ocurre |
|--------|-------------|---------------|
| 200 | OK | Request exitoso |
| 201 | Created | Recurso creado exitosamente |
| 204 | No Content | Eliminación exitosa |
| 400 | Bad Request | Datos inválidos |
| 401 | Unauthorized | Token faltante/inválido |
| 403 | Forbidden | Sin permisos |
| 404 | Not Found | Recurso no encontrado |
| 409 | Conflict | Conflicto (ej: email duplicado) |
| 422 | Unprocessable Entity | Validación falló |
| 500 | Internal Server Error | Error del servidor |

---

## 🛠️ Ejemplos Prácticos

### Ejemplo 1: Flujo Completo de Cliente

```javascript
// 1. Registrar usuario
const registerResponse = await fetch('http://localhost:8000/api/v1/auth/register', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'nuevo@cliente.com',
    password: 'Password123!',
    full_name: 'Nuevo Cliente',
    role: 'customer'
  })
});
const user = await registerResponse.json();

// 2. Login
const loginResponse = await fetch('http://localhost:8000/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'nuevo@cliente.com',
    password: 'Password123!'
  })
});
const { access_token } = await loginResponse.json();

// 3. Ver andamios disponibles
const scaffoldsResponse = await fetch('http://localhost:8000/api/v1/scaffolds?available_only=true');
const scaffolds = await scaffoldsResponse.json();

// 4. Calcular precio
const priceResponse = await fetch('http://localhost:8000/api/v1/scaffolds/calculate-price', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    items: [{ scaffold_id: 1, quantity: 5 }],
    rental_period: 'MENSUAL',
    start_date: '2025-10-15',
    end_date: '2025-11-15'
  })
});
const pricing = await priceResponse.json();

// 5. Crear orden
const orderResponse = await fetch('http://localhost:8000/api/v1/orders', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${access_token}`
  },
  body: JSON.stringify({
    items: [{ scaffold_id: 1, quantity: 5 }],
    rental_period: 'MENSUAL',
    start_date: '2025-10-15',
    end_date: '2025-11-15',
    shipping_address: 'Mi dirección de obra'
  })
});
const order = await orderResponse.json();

// 6. Ver mis órdenes
const myOrdersResponse = await fetch('http://localhost:8000/api/v1/orders', {
  headers: { 'Authorization': `Bearer ${access_token}` }
});
const myOrders = await myOrdersResponse.json();
```

### Ejemplo 2: Flujo de Admin

```javascript
// 1. Login como admin
const loginResponse = await fetch('http://localhost:8000/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'admin@elevo.com',
    password: 'Admin123!'
  })
});
const { access_token } = await loginResponse.json();

// 2. Ver todas las órdenes
const ordersResponse = await fetch('http://localhost:8000/api/v1/orders', {
  headers: { 'Authorization': `Bearer ${access_token}` }
});
const orders = await ordersResponse.json();

// 3. Aprobar una orden
const approveResponse = await fetch('http://localhost:8000/api/v1/orders/1/approve', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${access_token}` }
});

// 4. Registrar pago
const transactionResponse = await fetch('http://localhost:8000/api/v1/transactions', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${access_token}`
  },
  body: JSON.stringify({
    order_id: 1,
    transaction_type: 'PAGO',
    payment_method: 'TRANSFERENCIA',
    amount: 24360.00,
    reference: 'REF-001'
  })
});

// 5. Enviar notificación al cliente
const notificationResponse = await fetch('http://localhost:8000/api/v1/notifications', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${access_token}`
  },
  body: JSON.stringify({
    user_id: 1,
    type: 'ORDEN',
    title: 'Orden Lista',
    message: 'Tu orden está lista para entrega',
    channel: 'EMAIL'
  })
});
```

---

## 🧪 Testing con Swagger UI

### Paso 1: Abrir Swagger UI
Navega a: **http://localhost:8000/docs**

### Paso 2: Autenticarse
1. Haz clic en **POST /api/v1/auth/login**
2. Clic en "Try it out"
3. Ingresa credenciales:
   ```json
   {
     "email": "admin@elevoonline.com",
     "password": "Admin123!"
   }
   ```
4. Clic en "Execute"
5. Copia el `access_token` de la respuesta

### Paso 3: Configurar Authorization
1. Clic en el botón **"Authorize"** (🔒 arriba a la derecha)
2. Pega el token copiado
3. Clic en "Authorize"
4. Clic en "Close"

### Paso 4: Probar Endpoints
Ahora puedes probar cualquier endpoint protegido:
1. Expande el endpoint deseado
2. Clic en "Try it out"
3. Llena los parámetros
4. Clic en "Execute"
5. Ver la respuesta abajo

---

## 🐛 Solución de Problemas

### Error 401: Unauthorized

**Causa:** Token faltante, inválido o expirado

**Solución:**
1. Verifica que incluyes el header `Authorization`
2. El formato debe ser: `Bearer <token>`
3. Haz login de nuevo para obtener un nuevo token

### Error 403: Forbidden

**Causa:** Usuario autenticado pero sin permisos

**Solución:**
- Verifica que tu rol tiene acceso al endpoint
- Endpoints de admin requieren rol `admin`
- Endpoints de staff requieren rol `staff` o `admin`

### Error 422: Validation Error

**Causa:** Datos inválidos en el body o params

**Solución:**
1. Revisa el response body, incluye detalles del error
2. Verifica que todos los campos requeridos están presentes
3. Verifica que los tipos de datos son correctos
4. Revisa los formatos (fechas, emails, etc.)

### Error 409: Conflict

**Causa:** Recurso duplicado (ej: email ya existe)

**Solución:**
- Usa datos únicos (emails, SKUs, etc.)
- Verifica si el recurso ya existe antes de crear

---

## 📚 Recursos Adicionales

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health
- **OpenAPI Schema:** http://localhost:8000/openapi.json

---

**Última actualización:** 9 de Octubre, 2025  
**Versión API:** 1.2.0
