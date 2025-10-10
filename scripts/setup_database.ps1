# Script para configurar la base de datos
Write-Host "🔧 Configurando Base de Datos - Elevo Online" -ForegroundColor Cyan
Write-Host ""

# Verificar que estamos en el entorno virtual
if (-not $env:VIRTUAL_ENV) {
    Write-Host "⚠️  Activando entorno virtual..." -ForegroundColor Yellow
    & .\venv\Scripts\Activate.ps1
}

Write-Host "✅ Entorno virtual activado" -ForegroundColor Green
Write-Host ""

# Paso 1: Verificar conexión a PostgreSQL
Write-Host "📊 Paso 1: Verificando conexión a PostgreSQL..." -ForegroundColor Cyan
try {
    $pgStatus = Get-Service -Name "postgresql*" -ErrorAction SilentlyContinue
    if ($pgStatus) {
        Write-Host "✅ PostgreSQL está corriendo" -ForegroundColor Green
    } else {
        Write-Host "⚠️  PostgreSQL no encontrado como servicio" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  No se pudo verificar el estado de PostgreSQL" -ForegroundColor Yellow
}
Write-Host ""

# Paso 2: Generar migración
Write-Host "📝 Paso 2: Generando migración inicial..." -ForegroundColor Cyan
alembic revision --autogenerate -m "Initial migration"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Migración generada exitosamente" -ForegroundColor Green
    Write-Host ""
    
    # Paso 3: Aplicar migración
    Write-Host "🚀 Paso 3: Aplicando migración a la base de datos..." -ForegroundColor Cyan
    alembic upgrade head
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Migración aplicada exitosamente" -ForegroundColor Green
        Write-Host ""
        Write-Host "🎉 ¡Base de datos configurada correctamente!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Próximo paso: Iniciar el servidor" -ForegroundColor Cyan
        Write-Host "Ejecuta: python src/main.py" -ForegroundColor Yellow
    } else {
        Write-Host "❌ Error al aplicar migración" -ForegroundColor Red
        Write-Host "Verifica tu conexión a PostgreSQL y el archivo .env" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ Error al generar migración" -ForegroundColor Red
    Write-Host "Revisa los errores arriba para más detalles" -ForegroundColor Yellow
}

Write-Host ""
