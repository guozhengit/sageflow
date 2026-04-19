@echo off
echo ========================================
echo    SageFlow - Stopping all services
echo ========================================
echo.

docker-compose down

echo.
echo All services stopped.
echo To remove volumes: docker-compose down -v
pause
