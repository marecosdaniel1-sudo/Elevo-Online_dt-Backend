@echo off
REM Script para iniciar el servidor de desarrollo
REM Elevo Online Backend

title Elevo Online - Server

echo.
echo ============================================
echo   ELEVO ONLINE - Iniciando Servidor
echo ============================================
echo.

REM Matar procesos Python viejos primero
echo [1/2] Limpiando procesos antiguos...
powershell -Command "Get-Process | Where-Object {$_.ProcessName -like '*python*'} | Stop-Process -Force -ErrorAction SilentlyContinue" 2>nul
timeout /t 1 /nobreak >nul
echo     ✓ Listo
echo.

REM Iniciar servidor
echo [2/2] Iniciando servidor...
echo.
echo URL: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Presiona Ctrl+C para detener el servidor
echo.

REM Ejecutar servidor con Python del entorno virtual
venv\Scripts\python.exe scripts\start_server.py
