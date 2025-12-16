"""
Domain Layer - Pulse Model
领域层 - 语言脉冲分析模型
"""
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import math
from .entities import Conversation, Turn, SpeakerRole
from .features import FeatureExtractor


@dataclass
class PulsePoint:
    """脉冲点数据"""
    timestamp: datetime
    intensity: float  # 0-1
    sentiment: float  # -1 to 1
    engagement: float  # 0-1
    clarity: float  # 0-1
    turn_id: str = ""
    speaker_role: SpeakerRole = SpeakerRole.USER
    
    # 附加特征
    features: Dict[str, float] = field(default_factory=dict)


@dataclass
class PulsePattern:
    """脉冲模式"""
    name: str
    description: str
    pattern_type: str  # "rising", "falling", "oscillating", "stable"
    confidence: float  # 0-1
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    avg_intensity: float = 0.0
    volatility: float = 0.0


@dataclass
class PulseAnalysis:
    """脉冲分析结果"""
    conversation_id: str
    overall_score: float  # 0-1
    pulse_points: List[PulsePoint] = field(default_factory=list)
    patterns: List[PulsePattern] = field(default_factory=list)
    insights: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    # 对话统计
    total_duration_minutes: float = 0.0
    peak_intensity: float = 0.0
    avg_intensity: float = 0.0
    stability_score: float = 0.0  # 对话稳定性
    momentum_score: float = 0.0  # 对话动量
    
    created_at: datetime = field(default_factory=datetime.now)


class PulseAnalyzer:
    """语言脉冲分析器"""
    
    def __init__(self):
        self.feature_extractor = FeatureExtractor()
    
    def analyze_conversation(self, conversation: Conversation) -> PulseAnalysis:
        """分析对话的语言脉冲"""
        # 生成脉冲点
        pulse_points = self._generate_pulse_points(conversation)
        
        # 检测脉冲模式
        patterns = self._detect_patterns(pulse_points)
        
        # 生成洞察和建议
        insights = self._generate_insights(pulse_points, patterns)
        recommendations = self._generate_recommendations(patterns, insights)
        
        # 计算总体指标
        overall_score = self._calculate_overall_score(pulse_points, patterns)
        total_duration = conversation.duration_minutes
        peak_intensity = max((p.intensity for p in pulse_points), default=0.0)
        avg_intensity = sum(p.intensity for p in pulse_points) / max(len(pulse_points), 1)
        stability_score = self._calculate_stability(pulse_points)
        momentum_score = self._calculate_momentum(pulse_points)
        
        return PulseAnalysis(
            conversation_id=conversation.id,
            overall_score=overall_score,
            pulse_points=pulse_points,
            patterns=patterns,
            insights=insights,
            recommendations=recommendations,
            total_duration_minutes=total_duration,
            peak_intensity=peak_intensity,
            avg_intensity=avg_intensity,
            stability_score=stability_score,
            momentum_score=momentum_score
        )
    
    def _generate_pulse_points(self, conversation: Conversation) -> List[PulsePoint]:
        """生成脉冲点"""
        pulse_points = []
        
        for i, turn in enumerate(conversation.turns):
            # 提取特征
            previous_turns = conversation.turns[:i] if i > 0 else []
            features = self.feature_extractor.extract_turn_features(turn, previous_turns)
            
            # 更新turn的特征
            turn.features = features
            
            # 计算脉冲强度（综合多个特征）
            intensity = self._calculate_intensity(features)
            
            # 创建脉冲点
            pulse_point = PulsePoint(
                timestamp=turn.timestamp,
                intensity=intensity,
                sentiment=features.sentiment_score,
                engagement=features.engagement_score,
                clarity=features.clarity_score,
                turn_id=turn.id,
                speaker_role=turn.speaker_role,
                features={
                    'word_count': features.word_count,
                    'complexity': features.complexity_score,
                    'confidence': features.confidence_level,
                    'emotional_intensity': features.emotional_intensity,
                    'response_delay': features.response_delay
                }
            )
            
            pulse_points.append(pulse_point)
        
        return pulse_points
    
    def _calculate_intensity(self, features) -> float:
        """计算脉冲强度"""
        # 综合多个特征计算脉冲强度
        intensity_factors = [
            features.engagement_score * 0.3,
            features.emotional_intensity * 0.25,
            features.complexity_score * 0.2,
            (features.word_count / 50) * 0.15,  # 归一化到50词
            features.confidence_level * 0.1
        ]
        
        # 调整因子：问号和感叹号增加强度
        question_boost = 0.1 if features.word_count > 0 else 0
        
        intensity = sum(intensity_factors) + question_boost
        return min(max(intensity, 0.0), 1.0)
    
    def _detect_patterns(self, pulse_points: List[PulsePoint]) -> List[PulsePattern]:
        """检测脉冲模式"""
        if len(pulse_points) < 3:
            return []
        
        patterns = []
        intensities = [p.intensity for p in pulse_points]
        
        # 上升趋势
        rising_trend = self._detect_rising_trend(pulse_points)
        if rising_trend:
            patterns.append(rising_trend)
        
        # 下降趋势
        falling_trend = self._detect_falling_trend(pulse_points)
        if falling_trend:
            patterns.append(falling_trend)
        
        # 波动模式
        oscillating = self._detect_oscillating(pulse_points)
        if oscillating:
            patterns.append(oscillating)
        
        # 稳定模式
        stable = self._detect_stable(pulse_points)
        if stable:
            patterns.append(stable)
        
        return patterns
    
    def _detect_rising_trend(self, pulse_points: List[PulsePoint]) -> Optional[PulsePattern]:
        """检测上升趋势"""
        if len(pulse_points) < 5:
            return None
        
        intensities = [p.intensity for p in pulse_points]
        
        # 计算趋势
        n = len(intensities)
        x = list(range(n))
        y = intensities
        
        # 简单线性回归
        x_mean = sum(x) / n
        y_mean = sum(y) / n
        
        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return None
        
        slope = numerator / denominator
        
        # 如果斜率为正且足够大，认为是上升趋势
        if slope > 0.05:
            confidence = min(slope * 10, 1.0)  # 归一化置信度
            
            return PulsePattern(
                name="上升趋势",
                description="对话强度逐渐上升，表明参与度和兴趣在增长",
                pattern_type="rising",
                confidence=confidence,
                start_time=pulse_points[0].timestamp,
                end_time=pulse_points[-1].timestamp,
                avg_intensity=sum(intensities) / len(intensities),
                volatility=self._calculate_volatility(intensities)
            )
        
        return None
    
    def _detect_falling_trend(self, pulse_points: List[PulsePoint]) -> Optional[PulsePattern]:
        """检测下降趋势"""
        if len(pulse_points) < 5:
            return None
        
        intensities = [p.intensity for p in pulse_points]
        
        n = len(intensities)
        x = list(range(n))
        y = intensities
        
        x_mean = sum(x) / n
        y_mean = sum(y) / n
        
        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return None
        
        slope = numerator / denominator
        
        # 如果斜率为负且绝对值足够大，认为是下降趋势
        if slope < -0.05:
            confidence = min(abs(slope) * 10, 1.0)
            
            return PulsePattern(
                name="下降趋势",
                description="对话强度逐渐下降，可能表示疲劳或兴趣降低",
                pattern_type="falling",
                confidence=confidence,
                start_time=pulse_points[0].timestamp,
                end_time=pulse_points[-1].timestamp,
                avg_intensity=sum(intensities) / len(intensities),
                volatility=self._calculate_volatility(intensities)
            )
        
        return None
    
    def _detect_oscillating(self, pulse_points: List[PulsePoint]) -> Optional[PulsePattern]:
        """检测波动模式"""
        if len(pulse_points) < 6:
            return None
        
        intensities = [p.intensity for p in pulse_points]
        
        # 计算变化次数
        changes = 0
        for i in range(1, len(intensities)):
            if (intensities[i] > intensities[i-1] and i > 1 and intensities[i-1] <= intensities[i-2]) or \
               (intensities[i] < intensities[i-1] and i > 1 and intensities[i-1] >= intensities[i-2]):
                changes += 1
        
        # 如果变化频繁，认为是波动模式
        change_ratio = changes / (len(intensities) - 2)
        if change_ratio > 0.4:
            confidence = min(change_ratio * 2, 1.0)
            
            return PulsePattern(
                name="波动模式",
                description="对话强度频繁变化，可能表示话题转换或情绪波动",
                pattern_type="oscillating",
                confidence=confidence,
                start_time=pulse_points[0].timestamp,
                end_time=pulse_points[-1].timestamp,
                avg_intensity=sum(intensities) / len(intensities),
                volatility=self._calculate_volatility(intensities)
            )
        
        return None
    
    def _detect_stable(self, pulse_points: List[PulsePoint]) -> Optional[PulsePattern]:
        """检测稳定模式"""
        if len(pulse_points) < 4:
            return None
        
        intensities = [p.intensity for p in pulse_points]
        volatility = self._calculate_volatility(intensities)
        
        # 如果波动性低，认为是稳定模式
        if volatility < 0.1:
            confidence = 1.0 - min(volatility * 5, 1.0)
            
            return PulsePattern(
                name="稳定模式",
                description="对话强度保持稳定，表明交流顺畅且节奏良好",
                pattern_type="stable",
                confidence=confidence,
                start_time=pulse_points[0].timestamp,
                end_time=pulse_points[-1].timestamp,
                avg_intensity=sum(intensities) / len(intensities),
                volatility=volatility
            )
        
        return None
    
    def _calculate_volatility(self, intensities: List[float]) -> float:
        """计算波动性"""
        if len(intensities) < 2:
            return 0.0
        
        mean_intensity = sum(intensities) / len(intensities)
        variance = sum((x - mean_intensity) ** 2 for x in intensities) / len(intensities)
        return math.sqrt(variance)
    
    def _calculate_overall_score(self, pulse_points: List[PulsePoint], patterns: List[PulsePattern]) -> float:
        """计算总体脉冲分数"""
        if not pulse_points:
            return 0.0
        
        # 基于平均强度、稳定性和模式置信度
        avg_intensity = sum(p.intensity for p in pulse_points) / len(pulse_points)
        
        if pulse_points:
            stability = 1.0 - self._calculate_volatility([p.intensity for p in pulse_points])
        else:
            stability = 0.0
        
        pattern_confidence = max((p.confidence for p in patterns), default=0.5)
        
        # 加权平均
        overall_score = avg_intensity * 0.4 + stability * 0.3 + pattern_confidence * 0.3
        return min(max(overall_score, 0.0), 1.0)
    
    def _calculate_stability(self, pulse_points: List[PulsePoint]) -> float:
        """计算对话稳定性"""
        if len(pulse_points) < 2:
            return 1.0
        
        intensities = [p.intensity for p in pulse_points]
        volatility = self._calculate_volatility(intensities)
        
        # 稳定性 = 1 - 波动性
        return max(0.0, 1.0 - volatility * 2)  # 增强波动性的影响
    
    def _calculate_momentum(self, pulse_points: List[PulsePoint]) -> float:
        """计算对话动量"""
        if len(pulse_points) < 3:
            return 0.0
        
        # 基于最近几轮的强度变化
        recent_intensities = [p.intensity for p in pulse_points[-3:]]
        
        if len(recent_intensities) >= 2:
            momentum = recent_intensities[-1] - recent_intensities[0]
            return max(0.0, min(momentum, 1.0))  # 只考虑正向动量
        
        return 0.0
    
    def _generate_insights(self, pulse_points: List[PulsePoint], patterns: List[PulsePattern]) -> List[str]:
        """生成分析洞察"""
        insights = []
        
        # 基于模式生成洞察
        for pattern in patterns:
            if pattern.pattern_type == "rising" and pattern.confidence > 0.7:
                insights.append("对话显示出积极的上升趋势，参与度在持续提高")
            elif pattern.pattern_type == "falling" and pattern.confidence > 0.7:
                insights.append("对话强度呈下降趋势，建议调整话题或休息")
            elif pattern.pattern_type == "oscillating" and pattern.confidence > 0.6:
                insights.append("对话存在明显的波动，可能需要关注话题的连续性")
            elif pattern.pattern_type == "stable" and pattern.confidence > 0.8:
                insights.append("对话节奏稳定，说明双方交流顺畅")
        
        # 基于统计数据生成洞察
        if pulse_points:
            avg_intensity = sum(p.intensity for p in pulse_points) / len(pulse_points)
            
            if avg_intensity > 0.7:
                insights.append("整体对话强度很高，双方都非常投入")
            elif avg_intensity < 0.3:
                insights.append("对话强度偏低，可能需要更积极的互动")
            
            # 检查情感变化
            sentiments = [p.sentiment for p in pulse_points]
            if max(sentiments) - min(sentiments) > 0.6:
                insights.append("对话中情感变化较大，需要关注情绪管理")
        
        return insights
    
    def _generate_recommendations(self, patterns: List[PulsePattern], insights: List[str]) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        # 基于模式生成建议
        for pattern in patterns:
            if pattern.pattern_type == "falling" and pattern.confidence > 0.6:
                recommendations.append("尝试引入新话题或提问来重新激发对话兴趣")
                recommendations.append("检查是否存在理解障碍，适时澄清和确认")
            elif pattern.pattern_type == "oscillating" and pattern.confidence > 0.5:
                recommendations.append("保持当前话题的连续性，避免频繁转换")
                recommendations.append("在话题转换时提供明确的过渡")
            elif pattern.pattern_type == "rising" and pattern.confidence > 0.7:
                recommendations.append("保持当前的交流节奏和话题深度")
                recommendations.append("可以进一步探讨相关主题")
        
        # 基于洞察生成建议
        for insight in insights:
            if "情感变化较大" in insight:
                recommendations.append("注意倾听对方的情感表达，及时给予回应")
            elif "强度偏低" in insight:
                recommendations.append("主动提问或分享更多个人经历来增加互动")
            elif "强度很高" in insight:
                recommendations.append("注意控制节奏，避免信息过载")
        
        return recommendations