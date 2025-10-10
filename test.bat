@echo off
REM Script para ejecutar las pruebas del backend
REM Elevo Online Backend

title Elevo Online - Tests

echo.
echo ============================================
echo   ELEVO ONLINE - Ejecutar Pruebas
echo ============================================
echo.

REM Ejecutar pruebas con Python del entorno virtual
venv\Scripts\python.exe test\test_backend.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================
    echo   Pruebas completadas exitosamente
    echo ============================================
) else (
    echo.
    echo ============================================
    echo   Algunas pruebas fallaron
    echo ============================================
)

echo.
echo Presiona cualquier tecla para salir...
pause >nul
