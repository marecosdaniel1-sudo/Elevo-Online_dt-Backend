# Script para iniciar el servidor
Write-Host "🚀 Iniciando Servidor - Elevo Online" -ForegroundColor Cyan
Write-Host ""

# Verificar que estamos en el entorno virtual
if (-not $env:VIRTUAL_ENV) {
    Write-Host "⚠️  Activando entorno virtual..." -ForegroundColor Yellow
    & .\venv\Scripts\Activate.ps1
}

# Verificar que estamos en el entorno virtual
if (-not $env:VIRTUAL_ENV) {
    Write-Host "⚠️  Activando entorno virtual..." -ForegroundColor Yellow
    & .\venv\Scripts\Activate.ps1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Error al activar el entorno virtual" -ForegroundColor Red
        Write-Host "Ejecuta manualmente: .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host "✅ Entorno virtual activado" -ForegroundColor Green
Write-Host ""

Write-Host "🌐 Iniciando servidor FastAPI..." -ForegroundColor Cyan
Write-Host "Documentación: http://localhost:8000/api/docs" -ForegroundColor Yellow
Write-Host "Presiona CTRL+C para detener el servidor" -ForegroundColor Gray
Write-Host ""

# Usar python -m para ejecutar uvicorn con el módulo correcto
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
