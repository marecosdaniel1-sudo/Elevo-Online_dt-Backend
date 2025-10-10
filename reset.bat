@echo off
REM Script para resetear la base de datos
REM Elevo Online Backend

title Elevo Online - Reset Database

echo.
echo ============================================
echo   ELEVO ONLINE - Resetear Base de Datos
echo ============================================
echo.
echo ADVERTENCIA: Esto eliminara TODOS los datos!
echo.
set /p confirm="Estas seguro? (S/N): "

if /i "%confirm%" NEQ "S" (
    echo.
    echo Operacion cancelada.
    timeout /t 3 >nul
    exit /b 0
)

echo.
echo Iniciando reset...
echo.

REM Ejecutar con Python del entorno virtual
venv\Scripts\python.exe scripts\reset_db.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Reset completado. Poblando con datos de prueba...
    echo.
    venv\Scripts\python.exe scripts\seed_data.py
    
    if %ERRORLEVEL% EQU 0 (
        echo.
        echo ============================================
        echo   Base de datos lista para usar
        echo ============================================
    ) else (
        echo.
        echo ============================================
        echo   Error al poblar datos
        echo ============================================
    )
) else (
    echo.
    echo ============================================
    echo   Error durante el reset
    echo ============================================
)

echo.
echo Presiona cualquier tecla para salir...
pause >nul
