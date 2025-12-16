#!/bin/bash
# LingoPulse Backend Setup Script
# LingoPulse 后端项目设置脚本

set -e  # Exit on any error

echo "🚀 Setting up LingoPulse Backend..."
echo "====================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python version: $PYTHON_VERSION"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs uploads reports models

# Copy environment file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your API keys and configurations"
fi

# Run dependency check
echo "🔍 Checking dependencies..."
python main.py --check-deps

echo ""
echo "🎉 Setup completed successfully!"
echo "====================================="
echo "📋 Next steps:"
echo "   1. Edit .env file with your API keys"
echo "   2. Activate virtual environment: source venv/bin/activate"
echo "   3. Start the server: python main.py --reload"
echo ""
echo "🌐 Available endpoints:"
echo "   • API Documentation: http://localhost:8000/docs"
echo "   • Health Check: http://localhost:8000/health"
echo "   • API v1: http://localhost:8000/api/v1"
echo ""
echo "📚 For more information, see README.md"