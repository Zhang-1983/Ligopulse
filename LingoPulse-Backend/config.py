"""
Application Configuration
应用配置管理
"""
import os
from typing import Optional
from functools import lru_cache

# 兼容性处理 Pydantic BaseSettings
try:
    from pydantic_settings import BaseSettings
    from pydantic import Field
except ImportError:
    try:
        from pydantic.v1 import BaseSettings
        from pydantic.v1 import Field
    except ImportError:
        # 如果都无法导入，使用简单的配置类
        from abc import ABC, abstractmethod
        
        class BaseSettings(ABC):
            """简单的配置基类"""
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)
        
        class Field:
            """简化的 Field 函数"""
            def __init__(self, default=None, description=None, **kwargs):
                self.default = default
                self.description = description
                self.kwargs = kwargs


class Settings(BaseSettings):
    """应用设置"""
    
    # 应用基本信息
    app_name: str = Field(default="LingoPulse Backend", description="应用名称")
    app_version: str = Field(default="1.0.0", description="应用版本")
    debug: bool = Field(default=False, description="调试模式")
    environment: str = Field(default="development", description="运行环境")
    
    # 服务器配置
    host: str = Field(default="0.0.0.0", description="服务器主机")
    port: int = Field(default=8000, description="服务器端口")
    reload: bool = Field(default=True, description="自动重载")
    
    # 数据库配置
    database_url: str = Field(default="sqlite:///./lingopulse.db", description="数据库URL")
    redis_url: str = Field(default="redis://localhost:6379", description="Redis URL")
    
    # LLM 提供商配置
    wenxin_api_key: Optional[str] = Field(default=None, description="文心一言 API密钥")
    wenxin_secret_key: Optional[str] = Field(default=None, description="文心一言 Secret密钥")
    
    # 飞桨平台配置
    paddle_access_token: Optional[str] = Field(default=None, description="飞桨平台访问令牌")
    paddle_base_url: str = Field(default="https://aistudio.baidu.com/llm/lmapi/v3", description="飞桨平台基础URL")
    paddle_model_name: str = Field(default="ERNIE-4.5-21B-A3B-Thinking", description="飞桨平台模型名称")
    
    # 本地模型配置
    local_model_path: str = Field(default="./models", description="本地模型路径")
    enable_local_models: bool = Field(default=True, description="启用本地模型")
    
    # CORS 配置
    allowed_origins: list[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:5173",
            "http://localhost:5174",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:5174"
        ],
        description="允许的跨域来源"
    )
    
    # JWT 配置
    jwt_secret_key: str = Field(default="your-secret-key", description="JWT密钥")
    jwt_algorithm: str = Field(default="HS256", description="JWT算法")
    jwt_expire_minutes: int = Field(default=30, description="JWT过期分钟数")
    
    # 分析配置
    max_conversation_length: int = Field(default=10000, description="最大对话长度")
    analysis_timeout: int = Field(default=300, description="分析超时秒数")
    batch_analysis_limit: int = Field(default=100, description="批量分析限制")
    
    # 缓存配置
    cache_ttl: int = Field(default=1800, description="缓存生存时间（秒）")
    enable_caching: bool = Field(default=True, description="启用缓存")
    
    # 日志配置
    log_level: str = Field(default="INFO", description="日志级别")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="日志格式"
    )
    
    # 文件存储配置
    upload_dir: str = Field(default="./uploads", description="上传文件目录")
    report_dir: str = Field(default="./reports", description="报告文件目录")
    max_file_size: int = Field(default=50 * 1024 * 1024, description="最大文件大小（字节）")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"  # 允许额外的环境变量字段


class DatabaseSettings(BaseSettings):
    """数据库配置"""
    
    # PostgreSQL 配置
    postgresql_host: str = Field(default="localhost", description="PostgreSQL 主机")
    postgresql_port: int = Field(default=5432, description="PostgreSQL 端口")
    postgresql_user: str = Field(default="lingopulse", description="PostgreSQL 用户")
    postgresql_password: str = Field(default="password", description="PostgreSQL 密码")
    postgresql_database: str = Field(default="lingopulse", description="PostgreSQL 数据库")
    
    # SQLite 配置（开发用）
    sqlite_path: str = Field(default="./lingopulse.db", description="SQLite 数据库路径")
    
    # 连接池配置
    database_pool_size: int = Field(default=10, description="数据库连接池大小")
    database_max_overflow: int = Field(default=20, description="数据库最大溢出连接")
    
    class Config:
        env_file = ".env"


class LLMProviderSettings(BaseSettings):
    """LLM 提供商配置"""
    
    # 本地模型配置
    local_model_name: str = Field(default="chinese-chatglm-6b", description="本地模型名称")
    local_model_device: str = Field(default="cuda", description="本地模型设备")
    
    # 百度AI Studio配置
    baidu_access_token: Optional[str] = Field(default=None, description="百度AI Studio访问令牌")
    baidu_base_url: str = Field(default="https://aistudio.baidu.com/llm/lmapi/v3", description="百度AI Studio基础URL")
    baidu_model: str = Field(default="ernie-4.0", description="百度AI Studio模型名称")
    baidu_temperature: float = Field(default=0.8, description="百度AI Studio温度参数 (提高创造力)")
    baidu_max_tokens: int = Field(default=4000, description="百度AI Studio最大token数 (增加详细度)")
    
    # 飞桨平台配置
    paddle_temperature: float = Field(default=0.8, description="飞桨平台温度参数")
    paddle_max_tokens: int = Field(default=4000, description="飞桨平台最大token数")
    
    local_model_load_in_8bit: bool = Field(default=True, description="本地模型8位量化")
    local_model_max_length: int = Field(default=2048, description="本地模型最大长度")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"  # 允许额外的环境变量字段


class SecuritySettings(BaseSettings):
    """安全配置"""
    
    # CORS 配置
    cors_allow_credentials: bool = Field(default=True, description="CORS 允许凭据")
    cors_allow_methods: list[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        description="CORS 允许方法"
    )
    cors_allow_headers: list[str] = Field(
        default=["*"],
        description="CORS 允许头部"
    )
    
    # 限流配置
    rate_limit_enabled: bool = Field(default=True, description="启用限流")
    rate_limit_requests: int = Field(default=100, description="限流请求数")
    rate_limit_window: int = Field(default=3600, description="限流时间窗口（秒）")
    
    # API 密钥配置
    api_key_header: str = Field(default="X-API-Key", description="API密钥头部")
    admin_api_key: Optional[str] = Field(default=None, description="管理员API密钥")
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    """获取应用设置（缓存）"""
    return Settings()


@lru_cache()
def get_database_settings() -> DatabaseSettings:
    """获取数据库设置（缓存）"""
    return DatabaseSettings()


@lru_cache()
def get_llm_settings() -> LLMProviderSettings:
    """获取LLM设置（缓存）"""
    return LLMProviderSettings()


@lru_cache()
def get_security_settings() -> SecuritySettings:
    """获取安全设置（缓存）"""
    return SecuritySettings()


def get_database_url() -> str:
    """获取数据库连接URL"""
    db_settings = get_database_settings()
    
    # 如果设置了环境变量中的数据库URL，直接使用
    if os.getenv("DATABASE_URL"):
        return os.getenv("DATABASE_URL")
    
    # 否则根据数据库类型构建URL
    if os.getenv("DATABASE_TYPE", "sqlite") == "postgresql":
        return (
            f"postgresql://{db_settings.postgresql_user}:"
            f"{db_settings.postgresql_password}@"
            f"{db_settings.postgresql_host}:"
            f"{db_settings.postgresql_port}/"
            f"{db_settings.postgresql_database}"
        )
    else:
        return f"sqlite:///{db_settings.sqlite_path}"


def get_redis_url() -> str:
    """获取Redis连接URL"""
    if os.getenv("REDIS_URL"):
        return os.getenv("REDIS_URL")
    
    redis_settings = get_database_settings()
    return f"redis://{redis_settings.postgresql_host}:6379/0"