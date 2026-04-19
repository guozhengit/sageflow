@echo off
echo ========================================
echo    SageFlow - Smart Q&A Solutions
echo    Starting all services...
echo ========================================
echo.

REM 检查 Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed. Please install Docker first.
    pause
    exit /b 1
)

echo [1/3] Copying environment file...
if not exist .env (
    copy .env.example .env
    echo [INFO] .env file created. Please edit it if needed.
)

echo [2/3] Pulling model (qwen2.5:3b)...
REM 注意：第一次运行需要下载模型，可能需要几分钟
docker-compose run --rm ollama ollama pull qwen2.5:3b

echo [3/3] Starting services...
docker-compose up -d

echo.
echo ========================================
echo    Waiting for services to be ready...
echo ========================================
timeout /t 15 /nobreak >nul

echo.
echo ========================================
echo    SageFlow Started Successfully!
echo ========================================
echo.
echo    Frontend:  http://localhost:3000
echo    API:       http://localhost:8000
echo    Swagger:   http://localhost:8000/docs
echo    Qdrant:    http://localhost:6333/dashboard
echo.
echo    To view logs: docker-compose logs -f
echo    To stop:      docker-compose down
echo ========================================
pause
