"""
Domain Layer - Core Business Entities
领域层 - 核心业务实体定义
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


class SpeakerRole(Enum):
    """说话人角色"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ConversationType(Enum):
    """对话类型"""
    BUSINESS = "business"
    PERSONAL = "personal"
    INTERVIEW = "interview"
    THERAPY = "therapy"
    EDUCATION = "education"


@dataclass
class TurnFeatures:
    """对话轮次的特征数据"""
    # 语言特征
    word_count: int = 0
    sentence_count: int = 0
    avg_sentence_length: float = 0.0
    vocabulary_richness: float = 0.0
    
    # 情感特征
    sentiment_score: float = 0.0  # -1 到 1
    emotional_intensity: float = 0.0  # 0 到 1
    confidence_level: float = 0.0  # 0 到 1
    
    # 交互特征
    turn_timing: Optional[datetime] = None
    response_delay: float = 0.0  # 秒
    topic_consistency: float = 0.0  # 0 到 1
    
    # 认知特征
    complexity_score: float = 0.0  # 0 到 1
    clarity_score: float = 0.0  # 0 到 1
    engagement_score: float = 0.0  # 0 到 1


@dataclass
class Turn:
    """对话轮次实体"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: str = ""
    speaker_role: SpeakerRole = SpeakerRole.USER
    content: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    
    # 特征数据
    features: TurnFeatures = field(default_factory=TurnFeatures)
    
    # 元数据
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """后处理验证"""
        if not self.content.strip():
            raise ValueError("对话内容不能为空")
        
        if not self.conversation_id:
            raise ValueError("conversation_id 不能为空")
    
    @property
    def word_count(self) -> int:
        """获取单词数量"""
        return len(self.content.split())
    
    @property
    def is_question(self) -> bool:
        """判断是否为问题"""
        return '?' in self.content or self.content.strip().endswith('？')
    
    @property
    def sentiment_level(self) -> str:
        """获取情感等级"""
        score = self.features.sentiment_score
        if score > 0.3:
            return "positive"
        elif score < -0.3:
            return "negative"
        else:
            return "neutral"


@dataclass
class Conversation:
    """对话实体"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    conversation_type: ConversationType = ConversationType.BUSINESS
    participants: List[str] = field(default_factory=list)
    turns: List[Turn] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # 分析结果
    analysis_summary: Optional[str] = None
    pulse_score: Optional[float] = None  # 0 到 1
    patterns: List[str] = field(default_factory=list)
    
    # 元数据
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """后处理验证"""
        if not self.title.strip():
            self.title = f"对话 {self.id[:8]}"
    
    def add_turn(self, turn: Turn) -> None:
        """添加对话轮次"""
        if turn.conversation_id != self.id:
            raise ValueError("turn的conversation_id与当前对话不匹配")
        
        self.turns.append(turn)
        self.updated_at = datetime.now()
    
    @property
    def total_turns(self) -> int:
        """获取总轮次数"""
        return len(self.turns)
    
    @property
    def duration_minutes(self) -> float:
        """获取对话持续时间（分钟）"""
        if not self.turns:
            return 0.0
        
        start_time = min(turn.timestamp for turn in self.turns)
        end_time = max(turn.timestamp for turn in self.turns)
        return (end_time - start_time).total_seconds() / 60.0
    
    @property
    def user_turns(self) -> List[Turn]:
        """获取用户轮次"""
        return [turn for turn in self.turns if turn.speaker_role == SpeakerRole.USER]
    
    @property
    def assistant_turns(self) -> List[Turn]:
        """获取助手轮次"""
        return [turn for turn in self.turns if turn.speaker_role == SpeakerRole.ASSISTANT]
    
    def get_recent_turns(self, count: int = 5) -> List[Turn]:
        """获取最近的轮次"""
        return self.turns[-count:] if count > 0 else self.turns