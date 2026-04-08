@echo off
chcp 65001 >nul
echo ==========================================
echo   LIMPIEZA DE PROCESOS - Saulo v2
echo ==========================================
echo.

echo [1/5] Cerrando cloudflared...
taskkill /F /IM cloudflared.exe 2>nul
echo.

echo [2/5] Cerrando Python (Saulo v2 antiguo)...
taskkill /F /IM python.exe 2>nul
echo.

echo [3/5] Cerrando uvicorn...
taskkill /F /IM uvicorn.exe 2>nul
echo.

echo [4/5] Cerrando Node.js (si hay dashboard viejo)...
taskkill /F /IM node.exe 2>nul
echo.

echo [5/5] Verificando puertos...
echo    - Puerto 8095 (Saulo v2):
netstat -ano | findstr :8095
echo.
echo    - Puerto 8000:
netstat -ano | findstr :8000
echo.

echo ==========================================
echo   Procesos cerrados!
echo ==========================================
echo.
echo Ahora puedes iniciar Saulo v2 corregido:
echo.
echo    cd C:\Users\xiute\Desktop\saulo-v2
echo    start-saulo.bat
echo.
echo Y configurar el tunnel:
echo    cloudflared tunnel run saulo
echo.
pause
