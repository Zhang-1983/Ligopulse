#!/usr/bin/env python3
"""
LingoPulse Backend Server
LingoPulse 后端服务器启动脚本
"""

import uvicorn
import sys
import os
import argparse
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from config import get_settings
    from presentation.controllers import api_router
    from presentation.paddleocr_controller import paddleocr_router
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.middleware.gzip import GZipMiddleware
    from fastapi.responses import JSONResponse
    import logging
    import json
    from datetime import datetime
except ImportError as e:
    print(f"Import error: {e}")
    print("Please install required dependencies: pip install -r requirements.txt")
    sys.exit(1)


def create_app() -> FastAPI:
    """创建 FastAPI 应用"""
    settings = get_settings()
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="LingoPulse - AI-Powered Conversation Analysis Platform",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
    )
    
    # 添加中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # 注册API路由
    app.include_router(api_router)
    app.include_router(paddleocr_router)
    
    # 添加根路径路由
    @app.get("/")
    async def root():
        """根路径"""
        return {
            "service": settings.app_name,
            "version": settings.app_version,
            "status": "running",
            "timestamp": datetime.now().isoformat(),
            "environment": settings.environment,
            "docs": "/docs" if settings.debug else "Documentation not available in production"
        }
    
    # 添加健康检查
    @app.get("/health")
    async def health_check():
        """健康检查"""
        return {
            "status": "healthy",
            "service": settings.app_name,
            "version": settings.app_version,
            "timestamp": datetime.now().isoformat()
        }
    
    # 全局异常处理器
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        """全局异常处理"""
        logging.error(f"Global exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "detail": str(exc) if settings.debug else "An error occurred",
                "timestamp": datetime.now().isoformat()
            }
        )
    
    return app


def setup_logging():
    """设置日志配置"""
    settings = get_settings()
    
    # 创建日志目录
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 配置日志格式
    log_format = settings.log_format
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # 配置根日志器
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.FileHandler(log_dir / "lingopulse.log", encoding="utf-8"),
            logging.StreamHandler()
        ]
    )
    
    # 设置第三方库的日志级别
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("watchfiles").setLevel(logging.WARNING)
    logging.getLogger("watchfiles.main").setLevel(logging.WARNING)


def check_dependencies():
    """检查依赖"""
    required_modules = [
        "fastapi", "uvicorn", "pydantic", "sqlalchemy", 
        "redis", "openai", "requests"
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"Missing required modules: {', '.join(missing_modules)}")
        print("Please install them with: pip install -r requirements.txt")
        return False
    
    return True


def create_directories():
    """创建必要的目录"""
    directories = [
        "logs",
        "uploads",
        "reports",
        "models"
    ]
    
    for directory in directories:
        dir_path = Path(directory)
        dir_path.mkdir(exist_ok=True)
        print(f"Created directory: {directory}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="LingoPulse Backend Server")
    parser.add_argument(
        "--host", 
        default="0.0.0.0", 
        help="Server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000, 
        help="Server port (default: 8000)"
    )
    parser.add_argument(
        "--reload", 
        action="store_true", 
        help="Enable auto-reload for development"
    )
    parser.add_argument(
        "--workers", 
        type=int, 
        default=1, 
        help="Number of workers (default: 1)"
    )
    parser.add_argument(
        "--log-level", 
        default="info", 
        choices=["debug", "info", "warning", "error"],
        help="Log level (default: info)"
    )
    parser.add_argument(
        "--check-deps", 
        action="store_true", 
        help="Check dependencies and exit"
    )
    parser.add_argument(
        "--create-dirs", 
        action="store_true", 
        help="Create necessary directories and exit"
    )
    
    args = parser.parse_args()
    
    # 检查依赖
    if args.check_deps:
        if check_dependencies():
            print("All dependencies are installed.")
            sys.exit(0)
        else:
            sys.exit(1)
    
    # 创建目录
    if args.create_dirs:
        create_directories()
        sys.exit(0)
    
    # 设置日志
    setup_logging()
    
    # 创建应用
    app = create_app()
    
    # 显示启动信息
    settings = get_settings()
    print(f"""
{'='*60}
🚀 LingoPulse Backend Server
{'='*60}
📊 Service: {settings.app_name}
🔧 Version: {settings.app_version}
🌍 Environment: {settings.environment}
🏥 Host: {args.host}
🔌 Port: {args.port}
🔄 Reload: {args.reload}
👥 Workers: {args.workers}
📝 Log Level: {args.log_level}
{'='*60}
📋 Available Endpoints:
   • Health Check: http://{args.host}:{args.port}/health
   • API Documentation: http://{args.host}:{args.port}/docs
   • API v1: http://{args.host}:{args.port}/api/v1
{'='*60}
    """)
    
    try:
        # 启动服务器
        uvicorn.run(
            "main:create_app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            workers=args.workers if not args.reload else 1,
            log_level=args.log_level.lower(),
            access_log=True
        )
    except KeyboardInterrupt:
        print("\\n🛑 Server shutdown requested by user")
    except Exception as e:
        print(f"\\n❌ Server failed to start: {e}")
        sys.exit(1)
    finally:
        print("👋 Server stopped")


if __name__ == "__main__":
    main()