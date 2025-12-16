"""
飞桨平台(LLM)服务提供商
提供与飞桨平台交互的功能
"""
import os
import json
import time
import asyncio
import hashlib
import hmac
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import httpx
from loguru import logger

from config import get_settings, get_llm_settings
from infrastructure.llm_providers.providers import LLMProvider


class PaddleLLMProvider(LLMProvider):
    """飞桨平台LLM提供商"""
    
    def __init__(self):
        """初始化飞桨平台提供商"""
        # 调用父类构造函数
        super().__init__(api_key="", base_url="")
        self.settings = get_settings()
        self.llm_settings = get_llm_settings()
        
        # 获取飞桨平台配置
        self.base_url = self.settings.paddle_base_url
        self.model_name = self.settings.paddle_model_name
        self.temperature = self.llm_settings.paddle_temperature
        self.max_tokens = self.llm_settings.paddle_max_tokens
        self.access_token = self.settings.paddle_access_token
        
        # 初始化HTTP客户端
        self.client = httpx.AsyncClient(timeout=60.0)
        
        # 检查访问令牌
        if not self.access_token:
            logger.warning("未设置飞桨平台访问令牌，请使用set_access_token方法设置")
        
        logger.info(f"初始化飞桨平台提供商，使用模型: {self.model_name}")
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self
    
    async def __aexit__(self, exc_type, exc_value, traceback):
        """异步上下文管理器出口"""
        await self.client.aclose()
    
    def set_access_token(self, token: str):
        """设置访问令牌"""
        self.access_token = token
        logger.info("已更新飞桨平台访问令牌")
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        retry_count: int = 3,
        retry_delay: float = 1.0,
        **kwargs
    ) -> Dict[str, Any]:
        """
        与飞桨平台进行对话生成
        
        Args:
            messages: 对话历史消息列表
            model: 模型名称，默认为配置中的模型
            temperature: 采样温度，默认为配置中的温度
            max_tokens: 最大生成长度，默认为配置中的最大token数
            retry_count: 重试次数，默认为3次
            retry_delay: 重试延迟，默认为1秒
            **kwargs: 其他参数
            
        Returns:
            包含生成结果的字典
        """
        # 设置默认值
        model = model or self.model_name
        temperature = temperature or self.temperature
        max_tokens = max_tokens or self.max_tokens
        
        # 检查访问令牌
        if not self.access_token:
            logger.error("访问令牌未设置，无法调用飞桨平台API")
            return {
                "success": False,
                "error": "访问令牌未设置",
                "response": None
            }
        
        # 构建请求URL - 百度AI Studio API路径
        request_url = f"{self.base_url}/chat/completions"
        
        # 准备请求数据 - 百度AI Studio格式
        request_data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        
        # 添加其他参数
        if kwargs:
            for key, value in kwargs.items():
                if key not in request_data:
                    request_data[key] = value
        
        # 重试机制
        for attempt in range(retry_count):
            # 准备请求头
            current_datetime = datetime.utcnow()
            iso_date = current_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
            
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {self.access_token}",
                "X-BCE-Date": iso_date,
                "Date": current_datetime.strftime("%a, %d %b %Y %H:%M:%S GMT")
            }
            
            try:
                # 发送请求
                logger.info(f"向飞桨平台发送请求，模型: {model} (尝试 {attempt + 1}/{retry_count})")
                start_time = time.time()
                
                response = await self.client.post(
                    request_url,
                    headers=headers,
                    json=request_data,
                    timeout=120.0
                )
                
                # 处理响应
                elapsed_time = time.time() - start_time
                logger.info(f"飞桨平台响应时间: {elapsed_time:.2f}秒")
                logger.debug(f"响应状态: {response.status_code}")
                logger.debug(f"响应内容: {response.text}")
                
                # 解析响应
                try:
                    response_data = response.json()
                except json.JSONDecodeError:
                    logger.error(f"响应解析失败: {response.text}")
                    return {
                        "success": False,
                        "error": f"响应解析失败: {response.text[:100]}...",
                        "response": response.text
                    }
                
                # 检查API响应状态 - 百度AI Studio格式
                if "errorCode" in response_data:
                    error_msg = response_data.get("errorMsg", "未知错误")
                    error_code = response_data.get("errorCode", "未知错误码")
                    
                    # 如果是频率限制错误，重试
                    if "访问过于频繁" in error_msg and attempt < retry_count - 1:
                        logger.warning(f"API调用过于频繁，{retry_delay}秒后重试...")
                        await asyncio.sleep(retry_delay * (2 ** attempt))  # 指数退避
                        continue
                    
                    logger.error(f"飞桨平台API返回错误: 错误码 {error_code}, 错误信息: {error_msg}")
                    return {
                        "success": False,
                        "error": f"API返回错误: {error_msg} (错误码: {error_code})",
                        "response": response_data
                    }
                
                # 检查HTTP状态
                if response.status_code != 200:
                    # 如果是403或429错误，重试
                    if response.status_code in [403, 429] and attempt < retry_count - 1:
                        logger.warning(f"请求被拒绝 (状态码: {response.status_code})，{retry_delay}秒后重试...")
                        await asyncio.sleep(retry_delay * (2 ** attempt))  # 指数退避
                        continue
                    
                    logger.error(f"飞桨平台API调用失败，状态码: {response.status_code}")
                    return {
                        "success": False,
                        "error": f"API调用失败，状态码: {response.status_code}",
                        "response": response_data
                    }
                
                # 提取结果内容 - 兼容多种响应格式
                content = ""
                
                # 格式1: OpenAI兼容格式
                if "choices" in response_data:
                    choice = response_data["choices"][0]
                    message = choice.get("message", {})
                    # 优先获取content，若为空则使用reasoning_content
                    content = message.get("content", "")
                    if not content:
                        content = message.get("reasoning_content", "")
                        logger.info(f"使用reasoning_content作为响应内容")
                # 格式2: 百度ERNIE API格式
                elif "result" in response_data:
                    content = response_data["result"]
                # 格式3: 其他可能的格式
                elif "data" in response_data:
                    if isinstance(response_data["data"], dict):
                        content = response_data["data"].get("content", "")
                    elif isinstance(response_data["data"], list):
                        content = response_data["data"][0].get("content", "") if response_data["data"] else ""
                
                # 如果内容仍然为空，尝试从其他字段提取
                if not content:
                    content = str(response_data)
                    logger.warning(f"无法从标准字段提取内容，使用原始响应: {content[:100]}...")
                
                # 构建标准化的响应格式
                normalized_response = {
                    "success": True,
                    "text": content,
                    "model": model,
                    "usage": {
                        "prompt_tokens": response_data.get("usage", {}).get("prompt_tokens", 0),
                        "completion_tokens": response_data.get("usage", {}).get("completion_tokens", 0),
                        "total_tokens": response_data.get("usage", {}).get("total_tokens", 0)
                    },
                    "created_at": datetime.now().isoformat(),
                    "raw_response": response_data
                }
                
                logger.info(f"成功从飞桨平台获取响应，内容长度: {len(content)}")
                return normalized_response
                
            except httpx.TimeoutException:
                if attempt < retry_count - 1:
                    logger.warning(f"请求超时，{retry_delay}秒后重试...")
                    await asyncio.sleep(retry_delay * (2 ** attempt))  # 指数退避
                    continue
                logger.error("飞桨平台API请求超时")
                return {
                    "success": False,
                    "error": "请求超时",
                    "response": None
                }
            
            except httpx.RequestError as e:
                if attempt < retry_count - 1:
                    logger.warning(f"请求错误，{retry_delay}秒后重试...")
                    await asyncio.sleep(retry_delay * (2 ** attempt))  # 指数退避
                    continue
                logger.error(f"飞桨平台API请求错误: {str(e)}")
                return {
                    "success": False,
                    "error": f"请求错误: {str(e)}",
                    "response": None
                }
            
            except Exception as e:
                if attempt < retry_count - 1:
                    logger.warning(f"未知错误，{retry_delay}秒后重试...")
                    await asyncio.sleep(retry_delay * (2 ** attempt))  # 指数退避
                    continue
                logger.error(f"飞桨平台API调用未知错误: {str(e)}")
                return {
                    "success": False,
                    "error": f"未知错误: {str(e)}",
                    "response": None
                }
        
        # 所有重试都失败
        logger.error(f"所有重试都失败，无法调用飞桨平台API")
        return {
            "success": False,
            "error": "所有重试都失败，API调用过于频繁",
            "response": None
        }
    
    async def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        if not self.access_token:
            logger.error("访问令牌未设置，无法获取模型信息")
            return {
                "success": False,
                "error": "访问令牌未设置",
                "model_info": None
            }
        
        try:
            # 这里可以添加获取模型信息的API调用
            return {
                "success": True,
                "model_info": {
                    "name": self.model_name,
                    "type": "PaddlePaddle LLM",
                    "parameters": {
                        "temperature": self.temperature,
                        "max_tokens": self.max_tokens
                    },
                    "supported_features": [
                        "chat_completion"
                    ]
                }
            }
        except Exception as e:
            logger.error(f"获取模型信息错误: {str(e)}")
            return {
                "success": False,
                "error": f"获取模型信息错误: {str(e)}",
                "model_info": None
            }
    
    async def test_connection(self) -> bool:
        """测试连接是否正常"""
        try:
            # 发送一个简单的测试消息
            test_messages = [
                {"role": "user", "content": "你好，请回复'连接测试成功'"}
            ]
            
            response = await self.chat_completion(test_messages)
            return response.get("success", False)
        except Exception as e:
            logger.error(f"连接测试失败: {str(e)}")
            return False
    
    @staticmethod
    async def create_client(access_token: Optional[str] = None) -> "PaddleLLMProvider":
        """
        创建飞桨平台客户端的静态方法
        
        Args:
            access_token: 访问令牌，如果为None则使用配置中的令牌
            
        Returns:
            飞桨平台客户端实例
        """
        client = PaddleLLMProvider()
        
        # 如果提供了访问令牌，设置它
        if access_token:
            client.set_access_token(access_token)
        
        return client
    
    async def close(self):
        """关闭客户端"""
        await self.client.aclose()

    # 实现LLMProvider抽象方法
    async def analyze_sentiment(self, text: str) -> float:
        """分析文本情感"""
        prompt = f"""
        分析以下文本的情感倾向，返回-1到1之间的数值：
        -1表示强烈负面，0表示中性，1表示强烈正面
        文本：{text}
        只返回数字，不要返回其他内容。
        """
        
        messages = [{"role": "user", "content": prompt}]
        response = await self.chat_completion(messages, temperature=0.0, max_tokens=10)
        
        if response.get("success") and "text" in response:
            try:
                # 提取数字
                import re
                numbers = re.findall(r'[-+]?\d*\.?\d+', response["text"])
                if numbers:
                    sentiment_score = float(numbers[0])
                    # 确保分数在[-1, 1]范围内
                    return max(-1.0, min(1.0, sentiment_score))
            except Exception as e:
                logger.error(f"情感分析结果解析失败: {e}")
        
        return 0.0

    async def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """提取关键词"""
        prompt = f"""
        从以下文本中提取{max_keywords}个最重要的关键词，以逗号分隔：
        文本：{text}
        只返回关键词列表，不要返回其他内容。
        """
        
        messages = [{"role": "user", "content": prompt}]
        response = await self.chat_completion(messages, temperature=0.3, max_tokens=100)
        
        keywords = []
        if response.get("success") and "text" in response:
            content = response["text"]
            # 处理可能的关键词响应格式
            if ',' in content:
                potential_keywords = [kw.strip() for kw in content.split(",")]
                for kw in potential_keywords:
                    if kw and len(kw) <= 10:
                        keywords.append(kw)
            else:
                # 尝试提取可能的关键词
                import re
                words = re.findall(r'[一-龯]{2,8}', content)
                keywords = words[:max_keywords]
        
        # 如果没有提取到关键词，返回空列表
        return keywords[:max_keywords] if keywords else []

    async def calculate_complexity(self, text: str) -> float:
        """计算语言复杂度"""
        prompt = f"""
        评估以下文本的语言复杂度，返回0到1之间的数值：
        0表示非常简单，1表示非常复杂
        考虑因素：句式复杂度、词汇难度、逻辑结构等
        文本：{text}
        只返回数字，不要返回其他内容。
        """
        
        messages = [{"role": "user", "content": prompt}]
        response = await self.chat_completion(messages, temperature=0.0, max_tokens=10)
        
        if response.get("success") and "text" in response:
            try:
                # 提取数字
                import re
                numbers = re.findall(r'[-+]?\d*\.?\d+', response["text"])
                if numbers:
                    complexity = float(numbers[0])
                    # 确保在0-1范围内
                    return max(0.0, min(1.0, complexity))
            except Exception as e:
                logger.error(f"复杂度计算结果解析失败: {e}")
        
        return 0.5

    async def generate_insights(self, dialogue: str, sentiment_score: float, keywords: List[str], complexity_score: float) -> List[str]:
        """生成洞察"""
        prompt = f"""
        基于以下对话内容生成3-5个深度洞察：
        对话内容：{dialogue}
        情感分数：{sentiment_score} (范围-1到1，-1最消极，1最积极)
        关键词：{', '.join(keywords)}
        复杂度分数：{complexity_score} (范围0-1)
        
        请用中文生成3-5个深度洞察，每个洞察一句话，格式简洁明了。
        """
        
        messages = [{"role": "user", "content": prompt}]
        response = await self.chat_completion(messages, temperature=0.8, max_tokens=400)
        
        insights = []
        if response.get("success") and "text" in response:
            content = response["text"]
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#') and not line.startswith('洞察：'):
                    cleaned = line.strip('123456789.-、。· ')
                    if cleaned:
                        insights.append(cleaned)
        
        return insights[:5] if insights else []

    async def generate_recommendations(self, dialogue: str, sentiment_score: float, keywords: List[str], complexity_score: float) -> List[str]:
        """生成建议"""
        prompt = f"""
        基于以下对话内容生成3-5个建议：
        对话内容：{dialogue}
        情感分数：{sentiment_score} (范围-1到1，-1最消极，1最积极)
        关键词：{', '.join(keywords)}
        复杂度分数：{complexity_score} (范围0-1)
        
        请用中文生成3-5个实用建议，每个建议一句话，提供具体的改进方向。
        """
        
        messages = [{"role": "user", "content": prompt}]
        response = await self.chat_completion(messages, temperature=0.8, max_tokens=400)
        
        recommendations = []
        if response.get("success") and "text" in response:
            content = response["text"]
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#') and not line.startswith('建议：'):
                    cleaned = line.strip('123456789.-、。· ')
                    if cleaned:
                        recommendations.append(cleaned)
        
        return recommendations[:5] if recommendations else []


# 飞桨平台客户端单例
_paddle_client = None


async def get_paddle_client(access_token: Optional[str] = None) -> PaddleLLMProvider:
    """
    获取飞桨平台客户端单例
    
    Args:
        access_token: 可选的访问令牌，如果提供将覆盖配置中的令牌
        
    Returns:
        飞桨平台客户端实例
    """
    global _paddle_client
    
    if _paddle_client is None:
        _paddle_client = await PaddleLLMProvider.create_client(access_token)
    else:
        # 如果提供了访问令牌，更新它
        if access_token:
            _paddle_client.set_access_token(access_token)
    
    return _paddle_client


async def close_paddle_client():
    """关闭飞桨平台客户端"""
    global _paddle_client
    
    if _paddle_client is not None:
        await _paddle_client.close()
        _paddle_client = None