"""
LingoPulse Backend Tests
LingoPulse 后端单元测试
"""

import unittest
import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from domain.entities import Conversation, Turn, SpeakerRole, ConversationType, TurnFeatures
from domain.features import FeatureExtractor
from domain.pulse_model import PulseAnalyzer, PulsePoint, PulsePattern


class TestDomainEntities(unittest.TestCase):
    """测试领域实体"""
    
    def test_turn_features_creation(self):
        """测试特征数据类创建"""
        features = TurnFeatures(
            word_count=10,
            sentiment_score=0.5,
            emotional_intensity=0.6,
            engagement_score=0.8,
            complexity_score=0.6
        )
        
        self.assertEqual(features.word_count, 10)
        self.assertEqual(features.sentiment_score, 0.5)
        self.assertEqual(features.emotional_intensity, 0.6)
        self.assertEqual(features.engagement_score, 0.8)
    
    def test_turn_creation(self):
        """测试对话轮次创建"""
        turn = Turn(
            conversation_id="test_conv_123",
            content="这是一个测试对话轮次",
            speaker_role=SpeakerRole.USER
        )
        
        self.assertEqual(turn.conversation_id, "test_conv_123")
        self.assertEqual(turn.content, "这是一个测试对话轮次")
        self.assertEqual(turn.speaker_role, SpeakerRole.USER)
        self.assertIsNotNone(turn.id)
        self.assertIsNotNone(turn.timestamp)
    
    def test_conversation_creation(self):
        """测试对话创建"""
        conversation = Conversation(
            title="测试对话",
            conversation_type=ConversationType.BUSINESS,
            participants=["用户1", "用户2"]
        )
        
        self.assertEqual(conversation.title, "测试对话")
        self.assertEqual(conversation.conversation_type, ConversationType.BUSINESS)
        self.assertEqual(len(conversation.participants), 2)
        self.assertIsNotNone(conversation.id)
        self.assertIsNotNone(conversation.created_at)


class TestFeatureExtractor(unittest.TestCase):
    """测试特征提取器"""
    
    def setUp(self):
        """设置测试"""
        self.extractor = FeatureExtractor()
        self.test_turn = Turn(
            conversation_id="test_conv",
            content="这是一个测试的对话内容，包含几个问题？你怎么看这个问题？",
            speaker_role=SpeakerRole.USER
        )
    
    def test_basic_features_extraction(self):
        """测试基础特征提取"""
        features = self.extractor.extract_turn_features(self.test_turn, [])
        
        self.assertEqual(features.word_count, 25)  # 修正期望值
        self.assertGreater(features.sentiment_score, -1)
        self.assertLess(features.sentiment_score, 1)
        self.assertGreaterEqual(features.emotional_intensity, 0)
        self.assertGreaterEqual(features.engagement_score, 0)
        self.assertLessEqual(features.engagement_score, 1)


class TestPulseAnalyzer(unittest.TestCase):
    """测试脉冲分析器"""
    
    def setUp(self):
        """设置测试"""
        self.analyzer = PulseAnalyzer()
        self.conversation = Conversation(
            title="测试对话",
            conversation_type=ConversationType.PERSONAL,
            participants=["用户A", "用户B"]
        )
        
        # 添加几个测试轮次
        turns = [
            Turn(conversation_id="test", content="你好", speaker_role=SpeakerRole.USER),
            Turn(conversation_id="test", content="你好，很高兴见到你", speaker_role=SpeakerRole.ASSISTANT),
            Turn(conversation_id="test", content="今天天气不错", speaker_role=SpeakerRole.USER),
        ]
        
        for i, turn in enumerate(turns):
            turn.timestamp = turn.timestamp
            if turn.features is None:
                turn.features = TurnFeatures(
                    word_count=len(turn.content.split()),
                    sentiment_score=0.5,
                    emotional_intensity=0.6,
                    engagement_score=0.6,
                    complexity_score=0.4
                )
        
        self.conversation.turns = turns
    
    def test_analyze_conversation(self):
        """测试对话分析"""
        analysis = self.analyzer.analyze_conversation(self.conversation)
        
        self.assertIsInstance(analysis.overall_score, float)
        self.assertGreaterEqual(analysis.overall_score, 0)
        self.assertLessEqual(analysis.overall_score, 1)
        
        self.assertGreaterEqual(analysis.peak_intensity, 0)
        self.assertLessEqual(analysis.peak_intensity, 1)
        
        self.assertIsInstance(analysis.patterns, list)
        self.assertIsInstance(analysis.insights, list)
        self.assertIsInstance(analysis.recommendations, list)


class TestModuleImports(unittest.TestCase):
    """测试模块导入"""
    
    def test_domain_imports(self):
        """测试领域层导入"""
        try:
            from domain.entities import Conversation, Turn, SpeakerRole, ConversationType
            from domain.features import FeatureExtractor
            from domain.pulse_model import PulseAnalyzer
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import domain modules: {e}")
    
    def test_infrastructure_imports(self):
        """测试基础设施层导入"""
        try:
            from infrastructure.llm_providers.providers import LLMProvider, OpenAIProvider
            from infrastructure.database.repositories import DatabaseProvider
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import infrastructure modules: {e}")
    
    def test_application_imports(self):
        """测试应用层导入"""
        try:
            from application.usecases import (
                CreateConversationUseCase,
                AddTurnUseCase,
                AnalyzeConversationUseCase
            )
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import application modules: {e}")
    
    def test_presentation_imports(self):
        """测试表现层导入"""
        try:
            from presentation.controllers import api_router
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import presentation modules: {e}")


class TestConfiguration(unittest.TestCase):
    """测试配置"""
    
    def test_config_imports(self):
        """测试配置导入"""
        try:
            from config import get_settings, get_database_settings
            settings = get_settings()
            self.assertIsNotNone(settings)
            self.assertEqual(settings.app_name, "LingoPulse Backend")
        except ImportError as e:
            self.fail(f"Failed to import config modules: {e}")


class TestProjectStructure(unittest.TestCase):
    """测试项目结构"""
    
    def test_required_files_exist(self):
        """测试必需文件存在"""
        required_files = [
            "requirements.txt",
            "main.py",
            "config.py",
            ".env.example",
            "README.md",
            "domain/entities.py",
            "domain/features.py",
            "domain/pulse_model.py",
            "infrastructure/llm_providers/providers.py",
            "infrastructure/database/repositories.py",
            "application/usecases.py",
            "presentation/controllers.py"
        ]
        
        base_path = Path(__file__).parent.parent
        for file_path in required_files:
            full_path = base_path / file_path
            self.assertTrue(full_path.exists(), f"Required file missing: {file_path}")
    
    def test_directory_structure(self):
        """测试目录结构"""
        base_path = Path(__file__).parent.parent
        
        required_directories = [
            "domain",
            "infrastructure",
            "infrastructure/llm_providers",
            "infrastructure/database",
            "application",
            "presentation"
        ]
        
        for dir_path in required_directories:
            full_path = base_path / dir_path
            self.assertTrue(full_path.exists(), f"Required directory missing: {dir_path}")


def run_basic_tests():
    """运行基础测试"""
    print("🧪 Running LingoPulse Backend Tests...")
    print("=" * 50)
    
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加测试类
    test_classes = [
        TestModuleImports,
        TestProjectStructure,
        TestConfiguration,
        TestDomainEntities,
        TestFeatureExtractor,
        TestPulseAnalyzer
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("🎉 All tests passed!")
    else:
        print(f"❌ Tests failed: {len(result.failures)} failures, {len(result.errors)} errors")
        
    return result.wasSuccessful()


if __name__ == "__main__":
    run_basic_tests()