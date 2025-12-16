"""
Infrastructure Layer - Database Implementation
基础设施层 - 数据库实现
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime
import asyncio
from sqlalchemy import create_engine, Column, String, DateTime, Text, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import redis.asyncio as redis
import json


# 数据库模型
Base = declarative_base()


class ConversationDB(Base):
    """对话数据库模型"""
    __tablename__ = "conversations"
    
    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    conversation_type = Column(String, nullable=False)
    participants = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 分析结果
    analysis_summary = Column(Text, nullable=True)
    pulse_score = Column(Float, nullable=True)
    patterns = Column(JSON, nullable=True)
    
    # 元数据
    meta_data = Column(JSON, nullable=True)


class TurnDB(Base):
    """对话轮次数据库模型"""
    __tablename__ = "turns"
    
    id = Column(String, primary_key=True, index=True)
    conversation_id = Column(String, nullable=False, index=True)
    speaker_role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # 特征数据（JSON格式存储）
    features = Column(JSON, nullable=True)
    
    # 元数据
    meta_data = Column(JSON, nullable=True)


class DatabaseProvider(ABC):
    """数据库提供商基类"""
    
    @abstractmethod
    async def save_conversation(self, conversation: Dict[str, Any]) -> bool:
        """保存对话"""
        pass
    
    @abstractmethod
    async def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """获取对话"""
        pass
    
    @abstractmethod
    async def save_turn(self, turn: Dict[str, Any]) -> bool:
        """保存对话轮次"""
        pass
    
    @abstractmethod
    async def get_conversation_turns(self, conversation_id: str) -> List[Dict[str, Any]]:
        """获取对话的所有轮次"""
        pass
    
    @abstractmethod
    async def update_conversation_analysis(self, conversation_id: str, analysis_data: Dict[str, Any]) -> bool:
        """更新对话分析结果"""
        pass


class PostgreSQLProvider(DatabaseProvider):
    """PostgreSQL数据库提供商"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.async_engine = create_async_engine(
            database_url.replace("postgresql://", "postgresql+asyncpg://"),
            echo=False
        )
        self.async_session = async_sessionmaker(
            self.async_engine, 
            class_=AsyncSession, 
            expire_on_commit=False
        )
    
    async def init_db(self):
        """初始化数据库"""
        async with self.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def save_conversation(self, conversation: Dict[str, Any]) -> bool:
        """保存对话"""
        try:
            async with self.async_session() as session:
                conversation_db = ConversationDB(**conversation)
                session.add(conversation_db)
                await session.commit()
                return True
        except SQLAlchemyError:
            return False
    
    async def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """获取对话"""
        try:
            async with self.async_session() as session:
                result = await session.get(ConversationDB, conversation_id)
                if result:
                    return {
                        "id": result.id,
                        "title": result.title,
                        "conversation_type": result.conversation_type,
                        "participants": result.participants,
                        "created_at": result.created_at,
                        "updated_at": result.updated_at,
                        "analysis_summary": result.analysis_summary,
                        "pulse_score": result.pulse_score,
                        "patterns": result.patterns,
                        "metadata": result.metadata
                    }
                return None
        except SQLAlchemyError:
            return None
    
    async def save_turn(self, turn: Dict[str, Any]) -> bool:
        """保存对话轮次"""
        try:
            async with self.async_session() as session:
                turn_db = TurnDB(**turn)
                session.add(turn_db)
                await session.commit()
                return True
        except SQLAlchemyError:
            return False
    
    async def get_conversation_turns(self, conversation_id: str) -> List[Dict[str, Any]]:
        """获取对话的所有轮次"""
        try:
            async with self.async_session() as session:
                result = await session.execute(
                    "SELECT * FROM turns WHERE conversation_id = :cid ORDER BY timestamp",
                    {"cid": conversation_id}
                )
                turns = result.fetchall()
                return [
                    {
                        "id": turn.id,
                        "conversation_id": turn.conversation_id,
                        "speaker_role": turn.speaker_role,
                        "content": turn.content,
                        "timestamp": turn.timestamp,
                        "features": turn.features,
                        "metadata": turn.metadata
                    }
                    for turn in turns
                ]
        except SQLAlchemyError:
            return []
    
    async def update_conversation_analysis(self, conversation_id: str, analysis_data: Dict[str, Any]) -> bool:
        """更新对话分析结果"""
        try:
            async with self.async_session() as session:
                await session.execute(
                    "UPDATE conversations SET analysis_summary = :summary, pulse_score = :score, patterns = :patterns, updated_at = :updated WHERE id = :id",
                    {
                        "id": conversation_id,
                        "summary": analysis_data.get("analysis_summary"),
                        "score": analysis_data.get("pulse_score"),
                        "patterns": analysis_data.get("patterns"),
                        "updated": datetime.utcnow()
                    }
                )
                await session.commit()
                return True
        except SQLAlchemyError:
            return False
    
    async def close(self):
        """关闭数据库连接"""
        await self.async_engine.dispose()


class RedisCacheProvider:
    """Redis缓存提供商"""
    
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.redis_client = None
    
    async def connect(self):
        """连接Redis"""
        self.redis_client = redis.from_url(self.redis_url)
    
    async def cache_conversation(self, conversation_id: str, conversation_data: Dict[str, Any], expire_seconds: int = 3600):
        """缓存对话数据"""
        try:
            if self.redis_client:
                key = f"conversation:{conversation_id}"
                await self.redis_client.setex(
                    key, 
                    expire_seconds, 
                    json.dumps(conversation_data, default=str)
                )
        except Exception:
            pass  # 缓存失败不影响主功能
    
    async def get_cached_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """获取缓存的对话数据"""
        try:
            if self.redis_client:
                key = f"conversation:{conversation_id}"
                data = await self.redis_client.get(key)
                if data:
                    return json.loads(data)
        except Exception:
            pass
        return None
    
    async def cache_analysis_result(self, conversation_id: str, analysis_data: Dict[str, Any], expire_seconds: int = 1800):
        """缓存分析结果"""
        try:
            if self.redis_client:
                key = f"analysis:{conversation_id}"
                await self.redis_client.setex(
                    key,
                    expire_seconds,
                    json.dumps(analysis_data, default=str)
                )
        except Exception:
            pass
    
    async def get_cached_analysis(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """获取缓存的分析结果"""
        try:
            if self.redis_client:
                key = f"analysis:{conversation_id}"
                data = await self.redis_client.get(key)
                if data:
                    return json.loads(data)
        except Exception:
            pass
        return None
    
    async def cache_pulse_points(self, conversation_id: str, pulse_points: List[Dict[str, Any]], expire_seconds: int = 1800):
        """缓存脉冲点数据"""
        try:
            if self.redis_client:
                key = f"pulse_points:{conversation_id}"
                await self.redis_client.setex(
                    key,
                    expire_seconds,
                    json.dumps(pulse_points, default=str)
                )
        except Exception:
            pass
    
    async def get_cached_pulse_points(self, conversation_id: str) -> Optional[List[Dict[str, Any]]]:
        """获取缓存的脉冲点数据"""
        try:
            if self.redis_client:
                key = f"pulse_points:{conversation_id}"
                data = await self.redis_client.get(key)
                if data:
                    return json.loads(data)
        except Exception:
            pass
        return None
    
    async def close(self):
        """关闭Redis连接"""
        if self.redis_client:
            await self.redis_client.close()


class MockDatabaseProvider(DatabaseProvider):
    """模拟数据库提供商（用于测试）"""
    
    def __init__(self):
        self.conversations = {}
        self.turns = {}
    
    async def save_conversation(self, conversation: Dict[str, Any]) -> bool:
        """保存对话"""
        try:
            self.conversations[conversation["id"]] = conversation
            return True
        except Exception:
            return False
    
    async def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """获取对话"""
        return self.conversations.get(conversation_id)
    
    async def save_turn(self, turn: Dict[str, Any]) -> bool:
        """保存对话轮次"""
        try:
            if turn["conversation_id"] not in self.turns:
                self.turns[turn["conversation_id"]] = []
            self.turns[turn["conversation_id"]].append(turn)
            return True
        except Exception:
            return False
    
    async def get_conversation_turns(self, conversation_id: str) -> List[Dict[str, Any]]:
        """获取对话的所有轮次"""
        return self.turns.get(conversation_id, [])
    
    async def update_conversation_analysis(self, conversation_id: str, analysis_data: Dict[str, Any]) -> bool:
        """更新对话分析结果"""
        try:
            if conversation_id in self.conversations:
                self.conversations[conversation_id].update(analysis_data)
                return True
            return False
        except Exception:
            return False


class DatabaseProviderFactory:
    """数据库提供商工厂"""
    
    @staticmethod
    def create_provider(provider_type: str, **kwargs) -> DatabaseProvider:
        """创建数据库提供商实例"""
        if provider_type.lower() == "postgresql":
            return PostgreSQLProvider(kwargs.get("database_url", ""))
        elif provider_type.lower() == "mock":
            return MockDatabaseProvider()
        else:
            raise ValueError(f"Unsupported database provider type: {provider_type}")