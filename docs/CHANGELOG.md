# 📝 Changelog - Elevo Online Backend

Historial de cambios, correcciones y mejoras del backend de Elevo Online.

---

## [1.2.0] - 2025-10-09 ✅ STABLE

### 🎉 Backend 100% Funcional - Listo para Producción

**Estado:** 43/43 tests pasando (100%)

### ✨ Correcciones Críticas

#### 🔧 Reset de Base de Datos Robusto
**Problema:** Tests inconsistentes (43/43 → 13/25 → variable)

**Solución Implementada:**
- ✅ Cierre forzado de conexiones activas antes del reset
- ✅ Liberación explícita de pool de conexiones (`engine.dispose()`)
- ✅ Pool pre-ping para detectar conexiones muertas
- ✅ Query SQL para terminar procesos de BD:
  ```sql
  SELECT pg_terminate_backend(pg_stat_activity.pid)
  FROM pg_stat_activity
  WHERE pg_stat_activity.datname = 'elevo_online'
  AND pid <> pg_backend_pid()
  ```

**Archivos modificados:**
- `scripts/reset_db.py` - Reset robusto con cierre de conexiones
- `test/test_backend.py` - Reset automático antes de cada ejecución
- `start.bat` - Limpieza de procesos Python antiguos

**Resultado:** 100% de consistencia en tests

#### 🧪 Tests Automatizados
**Cambios:**
- ✅ Reset automático de BD (no pregunta al usuario)
- ✅ Espera de 2 segundos post-reset para estabilización
- ✅ Verificación de servidor corriendo antes de tests
- ✅ 43 tests completos cubriendo todos los endpoints

**Resultado:** Tests 100% confiables y repetibles

#### 🚀 Scripts de Inicio Mejorados
**Cambios:**
- ✅ `start.bat` mata procesos Python viejos automáticamente
- ✅ Prevención de conflictos de puerto 8000
- ✅ Mensajes claros de progreso

### 📊 Cobertura de Tests

**Autenticación (9 tests)**
- Registro de usuarios (admin, staff, customer)
- Login con JWT
- Validación de credenciales
- Manejo de errores

**Clientes (4 tests)**
- CRUD de perfiles
- Control de acceso por roles
- Actualización de información

**Andamios/Inventario (10 tests)**
- CRUD completo
- Filtros y búsquedas
- Verificación de disponibilidad
- Control de stock

**Precios (3 tests)**
- Cálculo de tarifas (diaria, semanal, mensual)
- IVA y descuentos
- Validaciones

**Órdenes (8 tests)**
- Creación y gestión
- Estados y transiciones
- Aprobación/cancelación
- Control de acceso

**Transacciones (2 tests)**
- Registro de pagos
- Historial por orden

**Notificaciones (2 tests)**
- Creación y envío
- Listado personalizado

**Validaciones (5 tests)**
- Autenticación requerida
- Permisos por rol
- Validación de inventario
- Duplicados

### 🗂️ Estructura de Archivos

```
Elevo_Online-dt/
├── start.bat           # Inicia servidor (limpia procesos)
├── test.bat            # Ejecuta tests (reset automático)
├── reset.bat           # Reset manual de BD
├── scripts/
│   ├── start_server.py # Configuración uvicorn
│   └── reset_db.py     # Reset robusto de BD
├── test/
│   └── test_backend.py # Suite de 43 tests
└── src/
    ├── main.py         # App FastAPI principal
    ├── api/            # Endpoints REST
    ├── core/           # Config, seguridad, BD
    ├── models/         # Modelos SQLAlchemy
    └── schemas/        # Schemas Pydantic
```

### 🔒 Seguridad

- ✅ Autenticación JWT
- ✅ Hash de contraseñas con bcrypt
- ✅ Validación de permisos por rol
- ✅ Protección de endpoints sensibles
- ✅ CORS configurado
- ✅ Validación de datos con Pydantic

### 📚 Documentación

- ✅ Swagger UI interactivo (`/docs`)
- ✅ ReDoc alternativo (`/redoc`)
- ✅ Guía de inicio rápido
- ✅ Documentación de API
- ✅ Ejemplos de uso

---

## [1.1.0] - 2025-10-08

### ✨ Nuevas Características

#### Módulo de Notificaciones
- Sistema de notificaciones en tiempo real
- Múltiples canales (email, push, in-app)
- Estados y prioridades

#### Cálculo de Precios
- Endpoint dedicado para cálculo de tarifas
- Soporte para períodos personalizados
- IVA y descuentos aplicables

### 🐛 Correcciones

- Validación de stock en órdenes
- Actualización de inventario al confirmar orden
- Manejo de transacciones concurrentes

---

## [1.0.0] - 2025-10-01 🎉 RELEASE INICIAL

### ✨ Características Iniciales

#### Autenticación y Usuarios
- Sistema de registro y login
- Roles: Admin, Staff, Customer
- JWT para autenticación
- Perfiles de usuario

#### Gestión de Clientes
- Perfiles de cliente completos
- Información de facturación
- Direcciones de envío
- Historial de órdenes

#### Inventario de Andamios
- Catálogo completo de productos
- Tipos: Tubular, Multidireccional, Colgante, Torre Móvil, Europeo
- Especificaciones técnicas detalladas
- Control de stock en tiempo real

#### Sistema de Órdenes
- Creación de órdenes de renta
- Múltiples items por orden
- Estados: Pendiente, Confirmada, Aprobada, En proceso, Completada, Cancelada
- Períodos de renta: Diario, Semanal, Mensual

#### Transacciones
- Registro de pagos
- Múltiples métodos de pago
- Estados de transacción
- Historial completo

### 🏗️ Arquitectura

- **Framework:** FastAPI 0.104+
- **Base de Datos:** PostgreSQL 13+
- **ORM:** SQLAlchemy (async)
- **Autenticación:** JWT (python-jose)
- **Validación:** Pydantic v2
- **Tests:** pytest + httpx

### 📊 Métricas Iniciales

- 35+ endpoints REST
- 43 tests unitarios
- ~2000 líneas de código
- Cobertura: 85%+

---

## Convenciones de Versionado

Usamos [Semantic Versioning](https://semver.org/):

- **MAJOR.MINOR.PATCH** (ej: 1.2.0)
  - **MAJOR:** Cambios incompatibles en la API
  - **MINOR:** Nueva funcionalidad compatible
  - **PATCH:** Correcciones de bugs

### Etiquetas

- ✨ Nuevas características
- 🐛 Correcciones de bugs
- 🔒 Seguridad
- ⚡ Rendimiento
- 📚 Documentación
- 🧪 Tests
- 🔧 Configuración
- 🗑️ Deprecado
- ❌ Eliminado

---

## Próximas Versiones (Roadmap)

### [1.3.0] - Planificado

**Características:**
- [ ] Reportes y analytics
- [ ] Exportación a PDF
- [ ] Sistema de recordatorios automáticos
- [ ] API de webhooks

**Mejoras:**
- [ ] Cache con Redis
- [ ] Rate limiting por usuario
- [ ] Logging estructurado
- [ ] Métricas con Prometheus

### [2.0.0] - Futuro

**Características mayores:**
- [ ] Multi-tenancy
- [ ] API GraphQL
- [ ] Sistema de reservaciones
- [ ] Integración con pasarelas de pago

---

## Contribuciones

Para reportar bugs o sugerir mejoras:
1. Abre un issue en GitHub
2. Describe el problema o sugerencia
3. Incluye logs si es un bug
4. Propone una solución si es posible

---

**Última actualización:** 9 de Octubre, 2025  
**Versión actual:** 1.2.0 ✅ STABLE
