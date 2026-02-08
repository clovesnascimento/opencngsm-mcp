@echo off
REM OpenClaw MCP - Iniciar Todos os Serviços (Windows)

echo.
echo ========================================
echo   OpenClaw MCP - Iniciando Sistema
echo ========================================
echo.

REM Verificar se está no diretório correto
if not exist "core\gateway\gateway.py" (
    echo ERRO: Execute este script dentro do diretorio openclaw-system
    pause
    exit /b 1
)

echo [1/3] Iniciando Gateway MCP...
start "OpenClaw Gateway" cmd /k "python core/gateway/gateway.py"
timeout /t 3 /nobreak >nul

echo [2/3] Iniciando Web Dashboard...
start "OpenClaw Web Dashboard" cmd /k "python interfaces/web/dashboard/app.py"
timeout /t 2 /nobreak >nul

echo [3/3] Iniciando Telegram Bot...
start "OpenClaw Telegram Bot" cmd /k "python interfaces/telegram/bot.py"

echo.
echo ========================================
echo   Todos os servicos foram iniciados!
echo ========================================
echo.
echo  Gateway:       http://127.0.0.1:18789
echo  Web Dashboard: http://127.0.0.1:8080
echo  Telegram Bot:  Rodando
echo.
echo  Swagger Docs:  http://127.0.0.1:18789/docs
echo.
echo Para parar os servicos, feche as janelas do terminal.
echo.
pause
