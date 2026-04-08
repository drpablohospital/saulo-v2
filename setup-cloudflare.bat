@echo off
chcp 65001 >nul
echo 🌐 Configurando Cloudflare Tunnel para Saulo...
echo.

:: Check if cloudflared is installed
where cloudflared >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ cloudflared no encontrado
    echo.
    echo Instalalo desde: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/
    pause
    exit /b 1
)

:: Create tunnel if doesn't exist
cloudflared tunnel list | findstr "saulo" >nul 2>&1
if %errorlevel% neq 0 (
    echo 🔨 Creando tunnel 'saulo'...
    cloudflared tunnel create saulo
) else (
    echo ✅ Tunnel 'saulo' ya existe
)

:: Setup DNS route
echo 📝 Configurando DNS route...
cloudflared tunnel route dns saulo saulo.dogma.tools

echo.
echo ✅ Configuración completada!
echo.
echo Para iniciar el tunnel, ejecuta:
echo    cloudflared tunnel run saulo
echo.
echo Esto conectará saulo.dogma.tools a tu servidor local.
echo.
pause
