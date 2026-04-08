@echo off
chcp 65001 >nul
echo 🦞 Iniciando Saulo v2...
echo.

set SAULO_DIR=C:\Users\xiute\Desktop\saulo-v2
set PORT=8095

cd /d "%SAULO_DIR%"

:: Check if Python is available
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python no encontrado
    pause
    exit /b 1
)

:: Check for venv
if exist venv\Scripts\activate.bat (
    echo ✅ Usando entorno virtual...
    call venv\Scripts\activate.bat
) else (
    echo ⚠️  Creando entorno virtual...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo 📦 Instalando dependencias...
    pip install -q fastapi uvicorn python-jose pydantic websockets httpx
)

echo.
echo 🔧 Configuración:
echo    Directorio: %SAULO_DIR%
echo    Puerto: %PORT%
echo.

:: Start Saulo
echo 🚀 Iniciando servidor...
echo    URL: http://localhost:%PORT%
echo    URL pública: https://saulo.dogma.tools (si cloudflared está activo)
echo.
echo Presiona Ctrl+C para detener
echo =================================

python -m uvicorn main:app --host 0.0.0.0 --port %PORT% --reload

:: Deactivate venv on exit
call venv\Scripts\deactivate.bat >nul 2>&1
