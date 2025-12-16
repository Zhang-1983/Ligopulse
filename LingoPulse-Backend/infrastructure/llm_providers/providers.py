"""
Infrastructure Layer - LLM Providers
基础设施层 - LLM提供商接口
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import httpx
import json


@dataclass
class LLMResponse:
    """LLM响应数据"""
    content: str
    confidence: float
    usage: Dict[str, int]
    model: str
    finish_reason: str


class LLMProvider(ABC):
    """LLM提供商基类"""
    
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
    
    @abstractmethod
    async def analyze_sentiment(self, text: str) -> float:
        """分析文本情感"""
        pass
    
    @abstractmethod
    async def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """提取关键词"""
        pass
    
    @abstractmethod
    async def calculate_complexity(self, text: str) -> float:
        """计算语言复杂度"""
        pass
# class WenxinProvider(LLMProvider):
#     """文心一言提供商"""
    
#     def __init__(self, api_key: str, secret_key: str):
#         super().__init__(api_key, "https://aip.baidubce.com/rpc/2.0")
#         self.secret_key = secret_key
#         self.access_token = None
#         self.client = httpx.AsyncClient()
    
#     async def _get_access_token(self) -> str:
#         """获取访问令牌"""
#         if self.access_token:
#             return self.access_token
        
#         try:
#             response = await self.client.post(
#                 f"https://aip.baidubce.com/oauth/2.0/token",
#                 data={
#                     "grant_type": "client_credentials",
#                     "client_id": self.api_key,
#                     "client_secret": self.secret_key
#                 }
#             )
            
#             if response.status_code == 200:
#                 result = response.json()
#                 self.access_token = result["access_token"]
#                 return self.access_token
#             else:
#                 raise Exception("Failed to get access token")
                
#         except Exception:
#             raise Exception("Failed to authenticate with Wenxin")
    
#     async def analyze_sentiment(self, text: str) -> float:
#         """分析文本情感"""
#         try:
#             access_token = await self._get_access_token()
            
#             # 使用文心的情感分析API
#             response = await self.client.post(
#                 f"{self.base_url}/nlp/v1/sentiment_classify?access_token={access_token}",
#                 json={"text": text}
#             )
            
#             if response.status_code == 200:
#                 result = response.json()
#                 # 文心返回的是分类结果，需要转换为数值
#                 items = result.get("items", [])
#                 if items:
#                     sentiment_label = items[0].get("sentiment", 0)
#                     # 0:负面, 1:中性, 2:正面
#                     if sentiment_label == 2:
#                         return 0.7
#                     elif sentiment_label == 1:
#                         return 0.0
#                     else:
#                         return -0.7
#                 return 0.0
#             else:
#                 return 0.0
                
#         except Exception:
#             return 0.0
    
#     async def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
#         """提取关键词 - 使用文心的文本相似度功能"""
#         # 这里简化实现，实际应该使用更复杂的NLP功能
#         try:
#             # 模拟关键词提取
#             words = text.split()
#             # 过滤停用词和短词
#             keywords = [word for word in words if len(word) > 1 and word not in {'的', '了', '在', '是', '我', '有', '和'}]
#             return keywords[:max_keywords]
#         except Exception:
#             return []
    
#     async def calculate_complexity(self, text: str) -> float:
#         """计算语言复杂度"""
#         try:
#             # 简化实现：基于句子长度和词汇复杂度
#             sentences = text.split('。') + text.split('.') + text.split('!') + text.split('?')
#             if sentences:
#                 avg_length = sum(len(s.split()) for s in sentences) / len(sentences)
#                 return min(avg_length / 20, 1.0)
#             return 0.5
#         except Exception:
#             return 0.5
    
#     async def close(self):
#         """关闭客户端"""
#         await self.client.aclose()


class LocalModelProvider(LLMProvider):
    """本地模型提供商（增强实现）"""
    
    def __init__(self, model_path: str):
        super().__init__("", "")
        self.model_path = model_path
        self.client = httpx.AsyncClient()
        print("🤖 初始化本地AI模型提供商（增强版）")
    
    async def analyze_sentiment(self, text: str) -> float:
        """分析文本情感 - 增强本地实现"""
        print(f"🔍 本地AI分析情感: {text[:30]}...")
        
        # 更丰富的情感词汇库，按强度分级
        very_positive_words = {'太好了', '完美', '杰出', '出色', '感动', '激动', '崇拜', '敬佩', '爱死', '超级棒', '惊艳', '震撼'}
        positive_words = {'好', '棒', '优秀', '喜欢', '高兴', '快乐', '满意', '赞', '精彩', '幸福', '美好', '愉快', '开心', '感谢', '感恩'}
        neutral_words = {'还行', '一般', '普通', '平常', '中规中矩', '可以', '凑合'}
        negative_words = {'坏', '差', '讨厌', '恨', '难过', '失望', '沮丧', '痛苦', '悲伤', '愤怒', '焦虑', '担心', '害怕', '绝望', '无聊', '烦躁'}
        very_negative_words = {'糟糕', '恶劣', '可怕', '崩溃', '绝望', '恶心', '反感', '愤慨', '仇恨', '恐怖'}
        
        # 更细致的情感分析
        words = text.split()
        
        # 基础统计
        very_positive_count = sum(1 for word in words if word in very_positive_words)
        positive_count = sum(1 for word in words if word in positive_words)
        neutral_count = sum(1 for word in words if word in neutral_words)
        negative_count = sum(1 for word in words if word in negative_words)
        very_negative_count = sum(1 for word in words if word in very_negative_words)
        
        # 情感强度修饰词
        intensity_modifiers = {
            '非常': 1.3, '特别': 1.2, '极其': 1.5, '超级': 1.4, '十分': 1.2, '相当': 1.1, 
            '格外': 1.2, '超': 1.4, '太': 1.2, '特别': 1.2, '真的': 1.1, '确实': 1.1,
            '挺': 1.0, '蛮': 1.0, '蛮好': 1.1, '挺棒': 1.1
        }
        
        # 应用强度修饰
        for word in words:
            if word in intensity_modifiers:
                modifier = intensity_modifiers[word]
                # 向前查找一个词看是否匹配情感词
                for i in range(len(words)-1):
                    if i < len(words)-1 and words[i] == word:
                        next_word = words[i+1]
                        if next_word in positive_words or next_word in very_positive_words:
                            positive_count *= modifier
                        elif next_word in negative_words or next_word in very_negative_words:
                            negative_count *= modifier
        
        # 文本长度和复杂度影响
        text_complexity = min(len(text) / 100, 1.0)
        
        # 计算最终情感分数 - 使用加权计算
        positive_score = (positive_count * 1.0 + very_positive_count * 1.5) / max(len(words), 1) * 0.8
        negative_score = (negative_count * 1.0 + very_negative_count * 1.5) / max(len(words), 1) * 0.8
        
        # 考虑标点符号
        exclamation_count = text.count('!') + text.count('！')
        question_count = text.count('?') + text.count('？')
        emotion_punctuation = (exclamation_count * 0.1) - (question_count * 0.05)
        
        # 综合计算情感分数
        sentiment = positive_score - negative_score + emotion_punctuation
        sentiment = max(-1.0, min(1.0, sentiment))
        
        # 如果没有任何情感词，基于文本特征给出大致判断
        if very_positive_count + positive_count + neutral_count + negative_count + very_negative_count == 0:
            # 基于文本长度和特征给出基础情感判断
            if '?' in text or '？' in text:
                sentiment = 0.1  # 问题通常表示中性到轻微积极
            elif len(text) > 50:
                sentiment = 0.05  # 长文本通常比较中性
            else:
                sentiment = 0.0
        
        print(f"📊 情感分析结果: {sentiment:.3f} (极积极:{very_positive_count}, 积极:{positive_count}, 消极:{negative_count}, 极消极:{very_negative_count})")
        return sentiment
    
    async def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """提取关键词 - 增强本地实现"""
        print(f"🔍 本地AI提取关键词: {text[:30]}...")
        
        # 停用词列表
        stop_words = {
            '的', '了', '是', '在', '有', '和', '与', '或', '但', '而', '因为', '所以', 
            '这个', '那个', '一个', '一些', '很', '非常', '也', '都', '还', '就', 
            '如果', '虽然', '可是', '不过', '然而', '因此', '所以', '而且', '或者',
            '什么', '怎么', '为什么', '如何', '哪里', '谁', '吗', '呢', '的', '地', '得'
        }
        
        # 关键词提取逻辑
        words = text.split()
        word_freq = {}
        
        # 统计词频
        for word in words:
            clean_word = word.strip('，。！？；：""''()（）').lower()
            if clean_word and len(clean_word) > 1 and clean_word not in stop_words:
                word_freq[clean_word] = word_freq.get(clean_word, 0) + 1
        
        # 按频率排序并提取关键词
        keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        result = [word for word, freq in keywords[:max_keywords]]
        
        print(f"📊 关键词提取结果: {result}")
        return result
    
    async def calculate_complexity(self, text: str) -> float:
        """计算语言复杂度 - 增强实现"""
        print(f"🧠 本地AI计算复杂度: {text[:30]}...")
        
        try:
            import re
            
            # 分析语言复杂度指标
            words = text.split()
            sentences = re.split(r'[。！？.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            # 指标1: 平均句长
            if sentences:
                avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
            else:
                avg_sentence_length = len(words)
            
            # 指标2: 词汇多样性（不同词汇占总词汇的比例）
            unique_words = set(words)
            lexical_diversity = len(unique_words) / max(len(words), 1)
            
            # 指标3: 标点符号复杂度
            punctuation_marks = ['，', '、', '；', '：', '——', '…', '…', '（', '）', '《', '》']
            punctuation_count = sum(1 for char in text if char in punctuation_marks)
            punctuation_density = punctuation_count / max(len(text), 1)
            
            # 指标4: 连接词和逻辑词使用
            logical_words = ['因为', '所以', '但是', '然而', '如果', '虽然', '即使', '因此', '此外', '另外', '而且', '或者', '以及', '或者说', '更重要', '值得注意的是']
            logical_count = sum(1 for word in words if word in logical_words)
            logical_density = logical_count / max(len(words), 1)
            
            # 综合复杂度计算
            length_factor = min(avg_sentence_length / 15, 1.0)  # 句长因子
            diversity_factor = lexical_diversity  # 词汇多样性
            punctuation_factor = min(punctuation_density * 20, 1.0)  # 标点密度
            logical_factor = min(logical_density * 10, 1.0)  # 逻辑词密度
            
            # 加权综合
            complexity = (
                0.4 * length_factor +
                0.3 * diversity_factor +
                0.2 * punctuation_factor +
                0.1 * logical_factor
            )
            
            final_complexity = max(0.0, min(1.0, complexity))
            print(f"🎯 复杂度分析: {final_complexity:.3f} (句长:{avg_sentence_length:.1f}, 多样性:{lexical_diversity:.2f})")
            
            return final_complexity
            
        except Exception as e:
            print(f"❌ 复杂度计算失败: {e}")
            return 0.5
    
    async def close(self):
        """关闭客户端"""
        await self.client.aclose()


class BaiduAistudioProvider(LLMProvider):
    """百度AI Studio推理模型提供商"""
    
    def __init__(self, access_token: str):
        super().__init__(access_token, "https://aistudio.baidu.com/llm/lmapi/v3")
        self.client = httpx.AsyncClient(timeout=120.0)  # 设置120秒超时
        self.model = "ernie-3.5-8k"  # 修复模型名称
        print("🤖 初始化百度AI Studio推理模型提供商")
    
    async def analyze_sentiment(self, text: str) -> float:
        """分析文本情感"""
        prompt = f"""
        分析以下文本的情感倾向，返回-1到1之间的数值：
        -1表示强烈负面，0表示中性，1表示强烈正面
        文本：{text}
        """
        
        try:
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 50,
                    "temperature": 0.3  # 增加温度，让结果更有差异性
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"].strip()
                print(f"🔍 百度API情感分析原始响应: {content}")
                
                # 提取数值
                import re
                numbers = re.findall(r'[-+]?\d*\.?\d+', content)
                if numbers:
                    try:
                        sentiment_score = float(numbers[0])
                        # 确保分数在[-1, 1]范围内
                        sentiment_score = max(-1.0, min(1.0, sentiment_score))
                        print(f"📊 提取的情感分数: {sentiment_score}")
                        return sentiment_score
                    except ValueError:
                        print(f"❌ 无法转换情感分数: {numbers[0]}")
                        return 0.0
                else:
                    print(f"❌ 未找到数字，原始内容: {content}")
                    return 0.0
            else:
                print(f"百度AI Studio API错误: {response.status_code}")
                return 0.0
                
        except Exception as e:
            print(f"百度AI Studio情感分析失败: {e}")
            return 0.0
    
    async def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """提取关键词"""
        prompt = f"""
        从以下文本中提取{max_keywords}个最重要的关键词，以逗号分隔：
        文本：{text}
        """
        
        try:
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 300,  # 大幅增加关键词提取的token限制
                    "temperature": 0.7  # 提高温度，让关键词提取更灵活
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"].strip()
                print(f"🔍 百度API关键词提取原始响应: {content}")
                
                # 处理可能的关键词响应格式
                import re
                keywords = []
                
                # 尝试以逗号分隔
                if ',' in content:
                    potential_keywords = [kw.strip() for kw in content.split(",")]
                    for kw in potential_keywords:
                        if kw and len(kw) <= 10:  # 过滤掉太长的描述
                            keywords.append(kw)
                
                # 如果没有逗号分隔，尝试提取可能的关键词
                if not keywords:
                    # 寻找可能是关键词的短词组
                    words = re.findall(r'[一-龯]{2,8}', content)
                    keywords = words[:max_keywords]
                
                # 如果还是找不到，返回一些默认关键词
                if not keywords:
                    keywords = ['产品', '服务', '质量', '体验']
                
                result_keywords = keywords[:max_keywords]
                print(f"📊 提取的关键词: {result_keywords}")
                return result_keywords
            else:
                print(f"百度AI Studio API错误: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"百度AI Studio关键词提取失败: {e}")
            return []
    
    async def calculate_complexity(self, text: str) -> float:
        """计算语言复杂度"""
        prompt = f"""
        评估以下文本的语言复杂度，返回0到1之间的数值：
        0表示非常简单，1表示非常复杂
        考虑因素：句式复杂度、词汇难度、逻辑结构等
        文本：{text}
        """
        
        try:
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 10,
                    "temperature": 0.3
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"].strip()
                try:
                    return float(content)
                except ValueError:
                    return 0.5
            else:
                print(f"百度AI Studio API错误: {response.status_code}")
                return 0.5
                
        except Exception as e:
            print(f"百度AI Studio复杂度计算失败: {e}")
            return 0.5

    async def generate_insights(self, dialogue: str, sentiment_score: float, keywords: List[str], complexity_score: float) -> List[str]:
        """使用百度AI Studio生成洞察"""
        try:
            prompt = f"""基于以下对话内容生成3-5个深度洞察：
对话内容：{dialogue}
情感分数：{sentiment_score} (范围-1到1，-1最消极，1最积极)
关键词：{', '.join(keywords)}
复杂度分数：{complexity_score} (范围0-1)

请用中文生成3-5个深度洞察，每个洞察一句话，格式简洁明了。"""
            
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 400,
                    "temperature": 0.8
                }
            )
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    print(f"🔍 洞察生成API原始响应: {result}")
                    content = result["choices"][0]["message"]["content"]
                    print(f"🔍 洞察生成内容: {content}")
                    
                    # 解析洞察
                    insights = []
                    lines = content.split('\n')
                    for line in lines:
                        line = line.strip()
                        if line and not line.startswith('#') and not line.startswith('洞察：'):
                            # 移除序号和常见前缀
                            cleaned = line.strip('123456789.-、。· ')
                            if cleaned:
                                insights.append(cleaned)
                    
                    if not insights:
                        # 如果解析失败，尝试按其他方式解析
                        content = content.replace('洞察：', '').replace('洞察:', '')
                        lines = [line.strip() for line in content.split('\n') if line.strip() and not line.startswith('洞察')]
                        insights = [line.strip('123456789.-、。· ') for line in lines if line.strip()]
                    
                    result_insights = insights[:5] if insights else ["对话分析洞察生成完成"]
                    print(f"🤖 百度AI生成洞察: {result_insights}")
                    return result_insights
                except Exception as parse_error:
                    print(f"❌ 洞察响应解析错误: {parse_error}")
                    print(f"❌ 原始响应: {result}")
                    return ["AI洞察生成失败，使用基础洞察"]
            else:
                print(f"❌ 百度AI洞察生成API错误: {response.status_code}")
                return ["AI洞察生成失败，使用基础洞察"]
                
        except Exception as e:
            print(f"❌ 百度AI洞察生成错误: {e}")
            import traceback
            traceback.print_exc()
            return ["AI洞察生成失败，使用基础洞察"]

    async def generate_recommendations(self, dialogue: str, sentiment_score: float, keywords: List[str], complexity_score: float) -> List[str]:
        """使用百度AI Studio生成建议"""
        try:
            prompt = f"""基于以下对话内容生成3-5个建议：
对话内容：{dialogue}
情感分数：{sentiment_score} (范围-1到1，-1最消极，1最积极)
关键词：{', '.join(keywords)}
复杂度分数：{complexity_score} (范围0-1)

请用中文生成3-5个实用建议，每个建议一句话，提供具体的改进方向。"""
            
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 400,
                    "temperature": 0.8
                }
            )
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    print(f"🔍 建议生成API原始响应: {result}")
                    content = result["choices"][0]["message"]["content"]
                    print(f"🔍 建议生成内容: {content}")
                    
                    # 解析建议
                    recommendations = []
                    lines = content.split('\n')
                    for line in lines:
                        line = line.strip()
                        if line and not line.startswith('#') and not line.startswith('建议：'):
                            # 移除序号和常见前缀
                            cleaned = line.strip('123456789.-、。· ')
                            if cleaned:
                                recommendations.append(cleaned)
                    
                    if not recommendations:
                        # 如果解析失败，尝试按其他方式解析
                        content = content.replace('建议：', '').replace('建议:', '')
                        lines = [line.strip() for line in content.split('\n') if line.strip() and not line.startswith('建议')]
                        recommendations = [line.strip('123456789.-、。· ') for line in lines if line.strip()]
                    
                    result_recommendations = recommendations[:5] if recommendations else ["对话改进建议生成完成"]
                    print(f"🤖 百度AI生成建议: {result_recommendations}")
                    return result_recommendations
                except Exception as parse_error:
                    print(f"❌ 建议响应解析错误: {parse_error}")
                    print(f"❌ 原始响应: {result}")
                    return ["AI建议生成失败，使用基础建议"]
            else:
                print(f"❌ 百度AI建议生成API错误: {response.status_code}")
                return ["AI建议生成失败，使用基础建议"]
                
        except Exception as e:
            print(f"❌ 百度AI建议生成错误: {e}")
            import traceback
            traceback.print_exc()
            return ["AI建议生成失败，使用基础建议"]
    
    async def close(self):
        """关闭客户端"""
        await self.client.aclose()


class LLMProviderFactory:
    """LLM提供商工厂"""
    
    @staticmethod
    def create_provider(provider_type: str, **kwargs) -> LLMProvider:
        """创建LLM提供商实例"""
        if provider_type.lower() == "paddle":
            from infrastructure.llm_providers.paddle_provider import PaddleLLMProvider
            client = PaddleLLMProvider()
            if "access_token" in kwargs:
                client.set_access_token(kwargs["access_token"])
            return client
        elif provider_type.lower() == "openai":
            return OpenAIProvider(kwargs.get("api_key", ""))
        elif provider_type.lower() == "wenxin":
            return WenxinProvider(
                api_key=kwargs.get("api_key", ""),
                secret_key=kwargs.get("secret_key", "")
            )
        elif provider_type.lower() == "local":
            return LocalModelProvider(kwargs.get("model_path", ""))
        elif provider_type.lower() == "baidu":
            return BaiduAistudioProvider(kwargs.get("access_token", ""))
        else:
            raise ValueError(f"Unsupported provider type: {provider_type}")