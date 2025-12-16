@echo off
REM LingoPulse Backend Setup Script for Windows
REM LingoPulse 后端项目 Windows 设置脚本

echo 🚀 Setting up LingoPulse Backend...
echo =====================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8+ first.
    exit /b 1
)

REM Show Python version
echo ✅ Python version:
python --version

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo 📦 Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo 📦 Installing dependencies...
pip install -r requirements.txt

REM Create necessary directories
echo 📁 Creating directories...
if not exist "logs" mkdir logs
if not exist "uploads" mkdir uploads
if not exist "reports" mkdir reports
if not exist "models" mkdir models

REM Copy environment file if it doesn't exist
if not exist ".env" (
    echo 📝 Creating .env file from template...
    copy .env.example .env
    echo ⚠️  Please edit .env file with your API keys and configurations
)

REM Run dependency check
echo 🔍 Checking dependencies...
python main.py --check-deps

echo.
echo 🎉 Setup completed successfully!
echo =====================================
echo 📋 Next steps:
echo    1. Edit .env file with your API keys
echo    2. Activate virtual environment: venv\Scripts\activate.bat
echo    3. Start the server: python main.py --reload
echo.
echo 🌐 Available endpoints:
echo    • API Documentation: http://localhost:8000/docs
echo    • Health Check: http://localhost:8000/health
echo    • API v1: http://localhost:8000/api/v1
echo.
echo 📚 For more information, see README.md

pause