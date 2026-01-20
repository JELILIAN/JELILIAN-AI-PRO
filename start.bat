@echo off
title JELILIAN AI PRO
echo ========================================
echo    JELILIAN AI PRO 启动中...
echo ========================================
echo.

cd /d "%~dp0"

:: 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

:: 启动服务器
echo 正在启动服务器...
echo 访问地址: http://localhost:8003
echo.
echo 按 Ctrl+C 停止服务器
echo ========================================

python start_server.py

pause
