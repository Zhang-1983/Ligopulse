"""
Application Layer - Use Cases
应用层 - 用例实现
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime
import asyncio

from domain.entities import Conversation, Turn, SpeakerRole, ConversationType
from domain.features import FeatureExtractor
from domain.pulse_model import PulseAnalyzer, PulseAnalysis


class ConversationRepository(ABC):
    """对话仓储接口"""
    
    @abstractmethod
    async def save_conversation(self, conversation: Conversation) -> bool:
        """保存对话"""
        pass
    
    @abstractmethod
    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """获取对话"""
        pass
    
    @abstractmethod
    async def save_turn(self, turn: Turn) -> bool:
        """保存对话轮次"""
        pass
    
    @abstractmethod
    async def get_conversation_turns(self, conversation_id: str) -> List[Turn]:
        """获取对话的所有轮次"""
        pass


class AnalysisCache(ABC):
    """分析缓存接口"""
    
    @abstractmethod
    async def cache_analysis(self, conversation_id: str, analysis: PulseAnalysis, expire_seconds: int = 1800):
        """缓存分析结果"""
        pass
    
    @abstractmethod
    async def get_cached_analysis(self, conversation_id: str) -> Optional[PulseAnalysis]:
        """获取缓存的分析结果"""
        pass


class CreateConversationUseCase:
    """创建对话用例"""
    
    def __init__(self, conversation_repo: ConversationRepository):
        self.conversation_repo = conversation_repo
    
    async def execute(self, title: str, conversation_type: ConversationType, participants: List[str]) -> Conversation:
        """执行创建对话用例"""
        # 创建新对话
        conversation = Conversation(
            title=title,
            conversation_type=conversation_type,
            participants=participants
        )
        
        # 保存到数据库
        success = await self.conversation_repo.save_conversation(conversation)
        if not success:
            raise Exception("Failed to save conversation")
        
        return conversation


class AddTurnUseCase:
    """添加对话轮次用例"""
    
    def __init__(self, conversation_repo: ConversationRepository, feature_extractor: FeatureExtractor):
        self.conversation_repo = conversation_repo
        self.feature_extractor = feature_extractor
    
    async def execute(self, conversation_id: str, content: str, speaker_role: SpeakerRole) -> Turn:
        """执行添加对话轮次用例"""
        # 获取对话
        conversation = await self.conversation_repo.get_conversation(conversation_id)
        if not conversation:
            raise Exception("Conversation not found")
        
        # 创建新轮次
        turn = Turn(
            conversation_id=conversation_id,
            content=content,
            speaker_role=speaker_role
        )
        
        # 提取特征
        previous_turns = await self.conversation_repo.get_conversation_turns(conversation_id)
        turn.features = self.feature_extractor.extract_turn_features(turn, previous_turns)
        
        # 保存轮次
        success = await self.conversation_repo.save_turn(turn)
        if not success:
            raise Exception("Failed to save turn")
        
        return turn


class AnalyzeConversationUseCase:
    """分析对话用例"""
    
    def __init__(
        self, 
        conversation_repo: ConversationRepository,
        analysis_cache: AnalysisCache,
        pulse_analyzer: PulseAnalyzer
    ):
        self.conversation_repo = conversation_repo
        self.analysis_cache = analysis_cache
        self.pulse_analyzer = pulse_analyzer
    
    async def execute(self, conversation_id: str) -> PulseAnalysis:
        """执行分析对话用例"""
        # 检查缓存
        cached_analysis = await self.analysis_cache.get_cached_analysis(conversation_id)
        if cached_analysis:
            return cached_analysis
        
        # 获取对话和轮次
        conversation = await self.conversation_repo.get_conversation(conversation_id)
        if not conversation:
            raise Exception("Conversation not found")
        
        turns = await self.conversation_repo.get_conversation_turns(conversation_id)
        conversation.turns = turns
        
        # 执行分析
        analysis = self.pulse_analyzer.analyze_conversation(conversation)
        
        # 缓存结果
        await self.analysis_cache.cache_analysis(conversation_id, analysis)
        
        return analysis


class GetConversationHistoryUseCase:
    """获取对话历史用例"""
    
    def __init__(self, conversation_repo: ConversationRepository):
        self.conversation_repo = conversation_repo
    
    async def execute(self, limit: int = 50, offset: int = 0) -> List[Conversation]:
        """执行获取对话历史用例"""
        # 这里简化实现，实际应该有分页逻辑
        # 模拟返回一些对话
        conversations = []
        for i in range(limit):
            conv = Conversation(
                title=f"对话 {i+1+offset}",
                conversation_type=ConversationType.BUSINESS,
                participants=["用户1", "用户2"]
            )
            conversations.append(conv)
        
        return conversations


class GetAnalysisHistoryUseCase:
    """获取分析历史用例"""
    
    def __init__(self, conversation_repo: ConversationRepository, analysis_cache: AnalysisCache):
        self.conversation_repo = conversation_repo
        self.analysis_cache = analysis_cache
    
    async def execute(self, limit: int = 20) -> List[Dict[str, Any]]:
        """执行获取分析历史用例"""
        # 模拟分析历史数据
        history = []
        for i in range(limit):
            analysis_data = {
                "id": f"analysis_{i}",
                "conversation_id": f"conv_{i}",
                "conversation_title": f"对话 {i+1}",
                "overall_score": 0.5 + (i % 10) * 0.05,
                "pulse_patterns": ["上升趋势", "稳定模式"],
                "created_at": datetime.now(),
                "duration_minutes": 10 + i * 2
            }
            history.append(analysis_data)
        
        return history


class ExportAnalysisReportUseCase:
    """导出分析报告用例"""
    
    def __init__(self, conversation_repo: ConversationRepository, pulse_analyzer: PulseAnalyzer):
        self.conversation_repo = conversation_repo
        self.pulse_analyzer = pulse_analyzer
    
    async def execute(self, conversation_id: str, format_type: str = "json") -> Dict[str, Any]:
        """执行导出分析报告用例"""
        # 获取对话
        conversation = await self.conversation_repo.get_conversation(conversation_id)
        if not conversation:
            raise Exception("Conversation not found")
        
        turns = await self.conversation_repo.get_conversation_turns(conversation_id)
        conversation.turns = turns
        
        # 执行分析
        analysis = self.pulse_analyzer.analyze_conversation(conversation)
        
        # 生成报告
        report = {
            "conversation_info": {
                "id": conversation.id,
                "title": conversation.title,
                "type": conversation.conversation_type.value,
                "participants": conversation.participants,
                "created_at": conversation.created_at,
                "duration_minutes": conversation.duration_minutes
            },
            "analysis_summary": {
                "overall_score": analysis.overall_score,
                "peak_intensity": analysis.peak_intensity,
                "avg_intensity": analysis.avg_intensity,
                "stability_score": analysis.stability_score,
                "momentum_score": analysis.momentum_score
            },
            "pulse_patterns": [
                {
                    "name": pattern.name,
                    "description": pattern.description,
                    "confidence": pattern.confidence,
                    "pattern_type": pattern.pattern_type
                }
                for pattern in analysis.patterns
            ],
            "insights": analysis.insights,
            "recommendations": analysis.recommendations,
            "pulse_points": [
                {
                    "timestamp": point.timestamp.isoformat(),
                    "intensity": point.intensity,
                    "sentiment": point.sentiment,
                    "engagement": point.engagement,
                    "clarity": point.clarity,
                    "speaker_role": point.speaker_role.value
                }
                for point in analysis.pulse_points
            ],
            "export_time": datetime.now().isoformat(),
            "format": format_type
        }
        
        return report


class BatchAnalyzeConversationsUseCase:
    """批量分析对话用例"""
    
    def __init__(
        self, 
        conversation_repo: ConversationRepository,
        analysis_cache: AnalysisCache,
        pulse_analyzer: PulseAnalyzer
    ):
        self.conversation_repo = conversation_repo
        self.analysis_cache = analysis_cache
        self.pulse_analyzer = pulse_analyzer
    
    async def execute(self, conversation_ids: List[str], max_concurrent: int = 5) -> Dict[str, str]:
        """执行批量分析用例"""
        # 控制并发数
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def analyze_single_conversation(conversation_id: str) -> tuple[str, bool]:
            async with semaphore:
                try:
                    # 检查缓存
                    cached_analysis = await self.analysis_cache.get_cached_analysis(conversation_id)
                    if cached_analysis:
                        return conversation_id, True
                    
                    # 获取对话和轮次
                    conversation = await self.conversation_repo.get_conversation(conversation_id)
                    if not conversation:
                        return conversation_id, False
                    
                    turns = await self.conversation_repo.get_conversation_turns(conversation_id)
                    conversation.turns = turns
                    
                    # 执行分析
                    analysis = self.pulse_analyzer.analyze_conversation(conversation)
                    
                    # 缓存结果
                    await self.analysis_cache.cache_analysis(conversation_id, analysis)
                    
                    return conversation_id, True
                    
                except Exception as e:
                    print(f"Error analyzing conversation {conversation_id}: {e}")
                    return conversation_id, False
        
        # 并发执行分析
        tasks = [analyze_single_conversation(cid) for cid in conversation_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 构建结果
        analysis_results = {}
        for result in results:
            if isinstance(result, tuple):
                conversation_id, success = result
                analysis_results[conversation_id] = "success" if success else "failed"
            else:
                # 处理异常情况
                analysis_results[str(result)] = "error"
        
        return analysis_results