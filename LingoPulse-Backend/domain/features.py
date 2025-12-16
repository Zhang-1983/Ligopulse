"""
Domain Layer - Feature Extraction Logic
领域层 - 特征提取逻辑
"""
from typing import Dict, List, Optional, Tuple
import re
import math
from datetime import datetime, timedelta
from .entities import Turn, TurnFeatures, Conversation


class FeatureExtractor:
    """特征提取器"""
    
    # 常见停用词
    STOP_WORDS = {
        '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', 
        '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', 
        '没有', '看', '好', '自己', '这', 'the', 'and', 'or', 'but', 'in', 
        'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 
        'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did'
    }
    
    # 情感词典（简化版）
    POSITIVE_WORDS = {'好', '棒', '优秀', '喜欢', '爱', '高兴', '快乐', '满意', '赞', 'good', 'great', 'excellent', 'love', 'like', 'happy', 'joy'}
    NEGATIVE_WORDS = {'坏', '差', '讨厌', '恨', '生气', '难过', '失望', 'bad', 'terrible', 'hate', 'angry', 'sad', 'disappointed'}
    
    # 复杂度指示词
    COMPLEXITY_INDICATORS = {
        '因为', '所以', '但是', '然而', '虽然', '尽管', '如果', '要是', 'unless', 'because', 'therefore', 'however', 'although', 'if'
    }
    
    @classmethod
    def extract_turn_features(cls, turn: Turn, previous_turns: Optional[List[Turn]] = None) -> TurnFeatures:
        """提取对话轮次的特征"""
        features = TurnFeatures()
        
        # 基础语言特征
        features.word_count = cls._count_words(turn.content)
        features.sentence_count = cls._count_sentences(turn.content)
        features.avg_sentence_length = features.word_count / max(features.sentence_count, 1)
        features.vocabulary_richness = cls._calculate_vocabulary_richness(turn.content)
        
        # 情感特征
        features.sentiment_score = cls._analyze_sentiment(turn.content)
        features.emotional_intensity = cls._calculate_emotional_intensity(turn.content)
        features.confidence_level = cls._estimate_confidence(turn.content)
        
        # 交互特征
        if previous_turns:
            features.response_delay = cls._calculate_response_delay(turn, previous_turns)
            features.topic_consistency = cls._calculate_topic_consistency(turn, previous_turns)
        
        # 认知特征
        features.complexity_score = cls._calculate_complexity(turn.content)
        features.clarity_score = cls._estimate_clarity(turn.content)
        features.engagement_score = cls._estimate_engagement(turn.content)
        
        return features
    
    @classmethod
    def _count_words(cls, text: str) -> int:
        """计算单词数量（支持中英文）"""
        # 对于中文，直接计算字符数量（去掉标点）
        if re.search(r'[\u4e00-\u9fff]', text):  # 包含中文字符
            # 去除标点符号，计算中文字符数量
            chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
            return len(chinese_chars)
        else:
            # 英文使用单词分割
            words = re.findall(r'\b\w+\b', text.lower())
            return len(words)
    
    @classmethod
    def _count_sentences(cls, text: str) -> int:
        """计算句子数量"""
        # 以句号、问号、感叹号结尾的视为句子
        sentences = re.split(r'[.!?。！？]+', text.strip())
        return len([s for s in sentences if s.strip()])
    
    @classmethod
    def _calculate_vocabulary_richness(cls, text: str) -> float:
        """计算词汇丰富度"""
        words = [w.lower() for w in re.findall(r'\b\w+\b', text) if w.lower() not in cls.STOP_WORDS]
        if not words:
            return 0.0
        
        unique_words = set(words)
        return len(unique_words) / len(words) if words else 0.0
    
    @classmethod
    def _analyze_sentiment(cls, text: str) -> float:
        """情感分析"""
        words = [w.lower() for w in re.findall(r'\b\w+\b', text)]
        
        positive_score = sum(1 for word in words if word in cls.POSITIVE_WORDS)
        negative_score = sum(1 for word in words if word in cls.NEGATIVE_WORDS)
        
        total_sentiment_words = positive_score + negative_score
        if total_sentiment_words == 0:
            return 0.0
        
        return (positive_score - negative_score) / total_sentiment_words
    
    @classmethod
    def _calculate_emotional_intensity(cls, text: str) -> float:
        """计算情感强度"""
        # 基于感叹号、问号、大写字母等指标
        intensity_indicators = [
            len(re.findall(r'!+', text)),  # 感叹号
            len(re.findall(r'\?+', text)),  # 问号
            sum(1 for c in text if c.isupper()) / len(text) if text else 0,  # 大写字母比例
        ]
        
        intensity = sum(intensity_indicators) / len(intensity_indicators)
        return min(intensity, 1.0)
    
    @classmethod
    def _estimate_confidence(cls, text: str) -> float:
        """估计表达自信度"""
        confidence_indicators = [
            '确实', '肯定', '一定', '当然', 'sure', 'definitely', 'absolutely', 'certainly'
        ]
        
        doubt_indicators = [
            '可能', '也许', '大概', '或许', 'maybe', 'perhaps', 'probably', 'likely'
        ]
        
        words = text.lower()
        confidence_words = sum(1 for indicator in confidence_indicators if indicator in words)
        doubt_words = sum(1 for indicator in doubt_indicators if indicator in words)
        
        total_words = confidence_words + doubt_words
        if total_words == 0:
            return 0.5  # 中性
        
        return confidence_words / total_words
    
    @classmethod
    def _calculate_response_delay(cls, turn: Turn, previous_turns: List[Turn]) -> float:
        """计算响应延迟"""
        if not previous_turns:
            return 0.0
        
        last_turn = previous_turns[-1]
        delay = (turn.timestamp - last_turn.timestamp).total_seconds()
        return max(0.0, delay)
    
    @classmethod
    def _calculate_topic_consistency(cls, current_turn: Turn, previous_turns: List[Turn]) -> float:
        """计算话题一致性"""
        if not previous_turns:
            return 1.0
        
        # 简化的话题一致性计算：基于关键词重叠
        current_keywords = set(cls._extract_keywords(current_turn.content))
        if not current_keywords:
            return 0.0
        
        total_consistency = 0.0
        count = 0
        
        for prev_turn in previous_turns[-3:]:  # 最近3轮
            prev_keywords = set(cls._extract_keywords(prev_turn.content))
            if prev_keywords:
                overlap = len(current_keywords & prev_keywords)
                consistency = overlap / len(current_keywords | prev_keywords)
                total_consistency += consistency
                count += 1
        
        return total_consistency / max(count, 1)
    
    @classmethod
    def _calculate_complexity(cls, text: str) -> float:
        """计算语言复杂度"""
        complexity_factors = []
        
        # 句长复杂度
        words = len(re.findall(r'\b\w+\b', text))
        sentences = cls._count_sentences(text)
        avg_sentence_length = words / max(sentences, 1)
        complexity_factors.append(min(avg_sentence_length / 20, 1.0))  # 归一化到20词
        
        # 复杂度指示词
        complexity_indicators = sum(1 for indicator in cls.COMPLEXITY_INDICATORS if indicator in text.lower())
        complexity_factors.append(min(complexity_indicators / 5, 1.0))  # 归一化到5个
        
        # 连接词多样性
        conjunctions = ['和', '与', '以及', 'and', 'or', 'but', 'so']
        conj_count = sum(1 for conj in conjunctions if conj in text.lower())
        complexity_factors.append(min(conj_count / 3, 1.0))
        
        return sum(complexity_factors) / len(complexity_factors)
    
    @classmethod
    def _estimate_clarity(cls, text: str) -> float:
        """估计表达清晰度"""
        clarity_indicators = []
        
        # 标点符号使用
        punctuation_ratio = len(re.findall(r'[.,;:!?，。；：！？]', text)) / max(len(text), 1)
        clarity_indicators.append(min(punctuation_ratio * 10, 1.0))  # 适度使用标点
        
        # 重复词汇检查
        words = re.findall(r'\b\w+\b', text.lower())
        if words:
            unique_words = set(words)
            repetition_ratio = 1 - len(unique_words) / len(words)
            clarity_indicators.append(max(0, 1 - repetition_ratio))  # 重复少=清晰
        
        # 句子长度适中度
        sentences = cls._count_sentences(text)
        if sentences > 0:
            avg_length = len(words) / sentences
            clarity_indicators.append(1 - abs(avg_length - 15) / 30)  # 15词左右最清晰
        
        return max(0, sum(clarity_indicators) / len(clarity_indicators))
    
    @classmethod
    def _estimate_engagement(cls, text: str) -> float:
        """估计参与度"""
        engagement_indicators = []
        
        # 问号表示互动
        question_ratio = text.count('?') + text.count('？')
        engagement_indicators.append(min(question_ratio / 2, 1.0))
        
        # 第二人称使用
        second_person = ['你', '您', 'you', 'your']
        second_person_count = sum(1 for word in second_person if word in text.lower())
        engagement_indicators.append(min(second_person_count / 3, 1.0))
        
        # 感叹号表示情感投入
        exclamation_ratio = text.count('!') + text.count('！')
        engagement_indicators.append(min(exclamation_ratio / 3, 1.0))
        
        return sum(engagement_indicators) / len(engagement_indicators)
    
    @classmethod
    def _extract_keywords(cls, text: str, max_keywords: int = 10) -> List[str]:
        """提取关键词"""
        # 移除停用词和短词
        words = [w.lower() for w in re.findall(r'\b\w{2,}\b', text) 
                if w.lower() not in cls.STOP_WORDS]
        
        # 返回前N个关键词（这里简化处理，实际可以用TF-IDF等算法）
        return words[:max_keywords]