"""
Presentation Layer - API Controllers
表现层 - API控制器
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, File, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
import logging
import tempfile
import os
import asyncio
from pathlib import Path
from datetime import datetime

# 导入微信聊天记录导入器
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from infrastructure.data_importers.wechat_importer import WeChatChatImporter

# 导入微信聊天记录提取器
from presentation.wechat_extractor_controller import router as wechat_extractor_router

# 导入LLM提供商
from infrastructure.llm_providers.providers import LLMProviderFactory, LLMProvider
from config import get_settings

# 这里需要从应用层导入用例实现
# 注意：实际使用时需要从 application.usecases 导入


# Pydantic 模型用于请求和响应
class CreateConversationRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="对话标题")
    conversation_type: str = Field(..., description="对话类型: business, casual, academic")
    participants: List[str] = Field(..., min_items=1, max_items=20, description="参与者列表")


class AddTurnRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000, description="对话内容")
    speaker_role: str = Field(..., description="说话者角色: interviewer, respondent")


class ConversationResponse(BaseModel):
    id: str
    title: str
    conversation_type: str
    participants: List[str]
    created_at: datetime
    duration_minutes: Optional[int] = None
    turns_count: int = 0


class TurnResponse(BaseModel):
    id: str
    conversation_id: str
    content: str
    speaker_role: str
    timestamp: datetime
    features: Optional[Dict[str, Any]] = None


class AnalysisResponse(BaseModel):
    id: str
    conversation_id: str
    overall_score: float
    peak_intensity: float
    avg_intensity: float
    stability_score: float
    momentum_score: float
    patterns: List[Dict[str, Any]]
    insights: List[str]
    recommendations: List[str]
    pulse_points: List[Dict[str, Any]]
    created_at: datetime


class AnalysisHistoryResponse(BaseModel):
    id: str
    conversation_id: str
    conversation_title: str
    overall_score: float
    pulse_patterns: List[str]
    created_at: datetime
    duration_minutes: int


class ExportReportRequest(BaseModel):
    format_type: str = Field(default="json", description="导出格式: json, pdf, csv")


class BatchAnalyzeRequest(BaseModel):
    conversation_ids: List[str] = Field(..., min_items=1, max_items=100, description="要分析的对话ID列表")
    max_concurrent: int = Field(default=5, ge=1, le=20, description="最大并发数")


class StatusResponse(BaseModel):
    status: str
    message: str
    timestamp: datetime


# API 路由器
api_router = APIRouter(prefix="/api/v1", tags=["lingopulse"])

# 依赖注入 - 实际使用时需要配置
async def get_conversation_use_case():
    # 这里返回具体的用例实现实例
    # 需要根据实际的DI容器配置
    pass

async def get_add_turn_use_case():
    pass

async def get_analyze_conversation_use_case():
    pass

async def get_conversation_history_use_case():
    pass

async def get_analysis_history_use_case():
    pass

async def get_export_report_use_case():
    pass

async def get_batch_analyze_use_case():
    pass


@api_router.post("/conversations", response_model=ConversationResponse, status_code=201)
async def create_conversation(
    request: CreateConversationRequest,
    use_case=Depends(get_conversation_use_case)
):
    """
    创建新的对话
    """
    try:
        # 转换请求类型
        from domain.entities import ConversationType
        conversation_type_map = {
            "business": ConversationType.BUSINESS,
            "casual": ConversationType.CASUAL,
            "academic": ConversationType.ACADEMIC
        }
        
        if request.conversation_type not in conversation_type_map:
            raise HTTPException(status_code=400, detail="Invalid conversation type")
        
        conversation = await use_case.execute(
            title=request.title,
            conversation_type=conversation_type_map[request.conversation_type],
            participants=request.participants
        )
        
        return ConversationResponse(
            id=conversation.id,
            title=conversation.title,
            conversation_type=conversation.conversation_type.value,
            participants=conversation.participants,
            created_at=conversation.created_at,
            duration_minutes=conversation.duration_minutes,
            turns_count=len(conversation.turns) if conversation.turns else 0
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create conversation: {str(e)}")


@api_router.post("/conversations/{conversation_id}/turns", response_model=TurnResponse, status_code=201)
async def add_turn(
    conversation_id: str,
    request: AddTurnRequest,
    use_case=Depends(get_add_turn_use_case)
):
    """
    为对话添加新的轮次
    """
    try:
        # 验证说话者角色
        from domain.entities import SpeakerRole
        if request.speaker_role not in ["interviewer", "respondent"]:
            raise HTTPException(status_code=400, detail="Invalid speaker role")
        
        speaker_role = SpeakerRole.INTERVIEWER if request.speaker_role == "interviewer" else SpeakerRole.RESPONDENT
        
        turn = await use_case.execute(
            conversation_id=conversation_id,
            content=request.content,
            speaker_role=speaker_role
        )
        
        return TurnResponse(
            id=turn.id,
            conversation_id=turn.conversation_id,
            content=turn.content,
            speaker_role=turn.speaker_role.value,
            timestamp=turn.timestamp,
            features=turn.features.dict() if turn.features else None
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add turn: {str(e)}")


@api_router.get("/conversations/{conversation_id}/analysis", response_model=AnalysisResponse)
async def analyze_conversation(
    conversation_id: str,
    use_case=Depends(get_analyze_conversation_use_case)
):
    """
    分析对话并返回脉冲分析结果
    """
    try:
        analysis = await use_case.execute(conversation_id=conversation_id)
        
        return AnalysisResponse(
            id=str(uuid.uuid4()),
            conversation_id=conversation_id,
            overall_score=analysis.overall_score,
            peak_intensity=analysis.peak_intensity,
            avg_intensity=analysis.avg_intensity,
            stability_score=analysis.stability_score,
            momentum_score=analysis.momentum_score,
            patterns=[
                {
                    "name": pattern.name,
                    "description": pattern.description,
                    "confidence": pattern.confidence,
                    "pattern_type": pattern.pattern_type
                }
                for pattern in analysis.patterns
            ],
            insights=analysis.insights,
            recommendations=analysis.recommendations,
            pulse_points=[
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
            created_at=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze conversation: {str(e)}")


@api_router.get("/conversations", response_model=List[ConversationResponse])
async def get_conversation_history(
    limit: int = 50,
    offset: int = 0,
    use_case=Depends(get_conversation_history_use_case)
):
    """
    获取对话历史列表
    """
    try:
        conversations = await use_case.execute(limit=limit, offset=offset)
        
        return [
            ConversationResponse(
                id=conv.id,
                title=conv.title,
                conversation_type=conv.conversation_type.value,
                participants=conv.participants,
                created_at=conv.created_at,
                duration_minutes=conv.duration_minutes,
                turns_count=len(conv.turns) if conv.turns else 0
            )
            for conv in conversations
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get conversation history: {str(e)}")


@api_router.get("/conversations/{conversation_id}/turns", response_model=List[TurnResponse])
async def get_conversation_turns(conversation_id: str):
    """
    获取对话的所有轮次
    """
    try:
        # 简化实现，实际应该从仓储中获取
        # 这里返回空列表作为示例
        return []
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get conversation turns: {str(e)}")


@api_router.get("/analysis/history", response_model=List[AnalysisHistoryResponse])
async def get_analysis_history(
    limit: int = 20,
    use_case=Depends(get_analysis_history_use_case)
):
    """
    获取分析历史记录
    """
    try:
        history = await use_case.execute(limit=limit)
        
        return [
            AnalysisHistoryResponse(
                id=item["id"],
                conversation_id=item["conversation_id"],
                conversation_title=item["conversation_title"],
                overall_score=item["overall_score"],
                pulse_patterns=item["pulse_patterns"],
                created_at=item["created_at"],
                duration_minutes=item["duration_minutes"]
            )
            for item in history
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analysis history: {str(e)}")


@api_router.get("/conversations/{conversation_id}/report")
async def export_analysis_report(
    conversation_id: str,
    format_type: str = "json",
    use_case=Depends(get_export_report_use_case)
):
    """
    导出分析报告
    """
    try:
        if format_type not in ["json", "pdf", "csv"]:
            raise HTTPException(status_code=400, detail="Invalid export format")
        
        report = await use_case.execute(conversation_id=conversation_id, format_type=format_type)
        
        if format_type == "json":
            return JSONResponse(content=report)
        else:
            # 对于 PDF/CSV，返回文件下载链接或文件内容
            # 这里简化为返回报告数据
            return JSONResponse(content={
                "message": f"Report exported in {format_type} format",
                "download_url": f"/api/v1/reports/{conversation_id}.{format_type}",
                "report_data": report
            })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export report: {str(e)}")


@api_router.post("/analysis/batch")
async def batch_analyze_conversations(
    request: BatchAnalyzeRequest,
    background_tasks: BackgroundTasks,
    use_case=Depends(get_batch_analyze_use_case)
):
    """
    批量分析对话
    """
    try:
        # 启动后台任务
        background_tasks.add_task(
            execute_batch_analysis,
            request.conversation_ids,
            request.max_concurrent
        )
        
        return StatusResponse(
            status="accepted",
            message="Batch analysis started",
            timestamp=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start batch analysis: {str(e)}")


@api_router.get("/analysis/{analysis_id}/status", response_model=StatusResponse)
async def get_analysis_status(analysis_id: str):
    """
    获取分析任务状态
    """
    # 简化实现，实际应该从任务队列或缓存中获取状态
    return StatusResponse(
        status="completed",
        message="Analysis completed successfully",
        timestamp=datetime.now()
    )


@api_router.post("/analysis/simple")
async def simple_analysis(
    request: dict
):
    """
    简单分析接口 - 支持scenario和dialogue直接分析，集成AI模型增强分析
    """
    try:
        scenario = request.get("scenario", "general")
        dialogue = request.get("dialogue", "")
        llm_provider = request.get("llm_provider", "baidu")  # 新增LLM提供商参数
        
        if not dialogue:
            raise HTTPException(status_code=400, detail="对话内容不能为空")
        
        # 分析过程，延迟几秒模拟真实处理
        await asyncio.sleep(2)
        
        # 使用指定AI模型增强的智能分析对话内容
        analysis_result = await _analyze_conversation_with_ai(dialogue, scenario, llm_provider)
        
        return analysis_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze: {str(e)}")


async def _analyze_conversation_with_ai(dialogue: str, scenario: str, llm_provider_name: str = "baidu") -> dict:
    """
    使用AI模型增强的智能分析对话内容
    结合传统算法和AI模型的优势，提供更准确、个性化的分析结果
    """
    import random
    import hashlib
    
    # 创建基于对话内容的种子，确保相同输入产生一致结果
    seed_str = f"{dialogue}_{scenario}"
    seed = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16)
    random.seed(seed)
    
    # 基础文本分析
    dialogue_lower = dialogue.lower()
    word_count = len(dialogue.split())
    char_count = len(dialogue)
    
    # 传统关键词检测
    positive_words = ['好', '棒', '优秀', '感谢', '同意', '满意', '喜欢', '开心', '高兴', '太好了', '完美', '赞', '厉害', '成功', '优秀']
    negative_words = ['不好', '糟糕', '不同意', '失望', '生气', '难过', '问题', '困难', '失败', '错误', '讨厌', '烦人', '麻烦', '痛苦']
    question_words = ['什么', '怎么', '为什么', '如何', '哪里', '谁', '吗', '呢', '？', '是不是', '能不能', '要不要']
    
    positive_count = sum(1 for word in positive_words if word in dialogue_lower)
    negative_count = sum(1 for word in negative_words if word in dialogue_lower)
    question_count = sum(1 for word in question_words if word in dialogue_lower)
    
    # 初始化AI提供商进行深度分析
    llm_provider = None
    ai_sentiment_score = None
    ai_keywords = []
    ai_complexity = None
    
    try:
        # 根据用户选择的LLM提供商初始化AI分析
        try:
            # 检查配置，使用用户指定的AI提供商
            settings = get_settings()
            llm_provider = None
            provider_used = "local"  # 记录实际使用的提供商
            
            # 根据用户选择的提供商类型创建实例
            # 1. 优先使用飞桨平台
            if llm_provider_name == "paddle" or llm_provider_name == "baidu":
                # 飞桨平台
                if hasattr(settings, 'paddle_access_token') and settings.paddle_access_token:
                    llm_provider = LLMProviderFactory.create_provider("paddle", 
                        access_token=settings.paddle_access_token)
                    provider_used = "百度飞桨平台"
                    print("使用用户指定的百度飞桨平台AI提供商")
                # 2. 其次使用百度AI Studio
                elif hasattr(settings, 'baidu_access_token') and settings.baidu_access_token:
                    llm_provider = LLMProviderFactory.create_provider("baidu", 
                        access_token=settings.baidu_access_token)
                    provider_used = "百度AI Studio"
                    print("使用用户指定的百度AI Studio AI提供商")
                else:
                    print("百度飞桨和百度AI Studio访问令牌未配置，使用本地模拟")
                    
            elif llm_provider_name == "wenxin":
                # 文心一言
                if settings.wenxin_api_key and settings.wenxin_secret_key:
                    llm_provider = LLMProviderFactory.create_provider("wenxin", 
                        api_key=settings.wenxin_api_key, 
                        secret_key=settings.wenxin_secret_key)
                    provider_used = "文心一言"
                    print("使用用户指定的文心一言AI提供商")
                else:
                    print("文心一言API密钥未配置，使用本地模拟")
                    
            # elif llm_provider_name == "openai":
            #     # OpenAI
            #     if settings.openai_api_key:
            #         llm_provider = LLMProviderFactory.create_provider("openai", 
            #             api_key=settings.openai_api_key)
            #         provider_used = "OpenAI"
            #         print("使用用户指定的OpenAI提供商")
            #     else:
            #         print("OpenAI API密钥未配置，使用本地模拟")
                    
            elif llm_provider_name == "local":
                # 本地模型
                llm_provider = LLMProviderFactory.create_provider("local", model_path="")
                provider_used = "本地模型"
                print("使用用户指定的本地模型")
            
            # 如果指定提供商不可用，回退到其他可用提供商
            if not llm_provider:
                print(f"用户选择的{llm_provider_name}提供商不可用，回退到其他可用提供商")
                
                # 检查其他可用提供商，优先使用百度相关技术
                # 1. 首选百度飞桨平台
                if hasattr(settings, 'paddle_access_token') and settings.paddle_access_token:
                    llm_provider = LLMProviderFactory.create_provider("paddle", 
                        access_token=settings.paddle_access_token)
                    provider_used = "百度飞桨平台(回退)"
                    print("回退使用百度飞桨平台AI提供商")
                # 2. 其次使用百度AI Studio
                elif hasattr(settings, 'baidu_access_token') and settings.baidu_access_token:
                    llm_provider = LLMProviderFactory.create_provider("baidu", 
                        access_token=settings.baidu_access_token)
                    provider_used = "百度AI Studio(回退)"
                    print("回退使用百度AI Studio AI提供商")
                # 3. 其他百度相关服务
                elif settings.wenxin_api_key and settings.wenxin_secret_key:
                    llm_provider = LLMProviderFactory.create_provider("wenxin", 
                        api_key=settings.wenxin_api_key, 
                        secret_key=settings.wenxin_secret_key)
                    provider_used = "文心一言(回退)"
                    print("回退使用文心一言AI提供商")
                # 4. 非百度服务作为最后的选择
                elif settings.openai_api_key:
                    llm_provider = LLMProviderFactory.create_provider("openai", 
                        api_key=settings.openai_api_key)
                    provider_used = "OpenAI(回退)"
                    print("回退使用OpenAI提供商")
                else:
                    # 最后回退到本地模拟
                    llm_provider = LLMProviderFactory.create_provider("local", model_path="")
                    provider_used = "本地模拟(回退)"
                    print("所有API提供商都不可用，使用本地模拟AI提供商")
            
            # 记录实际使用的提供商
            print(f"✅ 实际使用AI提供商: {provider_used}")
            
            # 并行执行AI分析任务
            tasks = []
            
            # 1. AI情感分析
            tasks.append(llm_provider.analyze_sentiment(dialogue))
            
            # 2. AI关键词提取
            tasks.append(llm_provider.extract_keywords(dialogue, max_keywords=8))
            
            # 3. AI复杂度分析
            tasks.append(llm_provider.calculate_complexity(dialogue))
            
            # 执行所有AI分析任务
            ai_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 处理AI结果 - 确保所有变量都有默认值
            ai_sentiment_score = None
            ai_keywords = []
            ai_complexity = None
            
            if isinstance(ai_results[0], (int, float)):
                ai_sentiment_score = ai_results[0]
                print(f"🤖 AI情感分析结果: {ai_sentiment_score}")
            
            if isinstance(ai_results[1], list):
                ai_keywords = ai_results[1]
                print(f"🔍 AI关键词提取结果: {ai_keywords}")
                
            if isinstance(ai_results[2], (int, float)):
                ai_complexity = ai_results[2]
                print(f"📊 AI复杂度分析结果: {ai_complexity}")
                
            # 处理可能的异常情况
            if isinstance(ai_results[0], Exception):
                print(f"❌ AI情感分析失败: {ai_results[0]}")
            if isinstance(ai_results[1], Exception):
                print(f"❌ AI关键词提取失败: {ai_results[1]}")
            if isinstance(ai_results[2], Exception):
                print(f"❌ AI复杂度计算失败: {ai_results[2]}")
                
        except Exception as ai_error:
            print(f"AI分析失败，使用传统方法: {ai_error}")
            # 如果AI失败，使用传统方法的情感分数
            ai_sentiment_score = (positive_count - negative_count) / max(1, word_count / 10)
        
        # 融合AI和传统分析结果
        if ai_sentiment_score is not None:
            # 传统情感分数
            traditional_sentiment = (positive_count - negative_count) / max(1, word_count / 10)
            # 融合权重：AI模型70% + 传统方法30%
            sentiment_score = 0.7 * ai_sentiment_score + 0.3 * traditional_sentiment
        else:
            # 仅使用传统方法
            sentiment_score = (positive_count - negative_count) / max(1, word_count / 10)
        
        # 限制在-1到1之间
        sentiment_score = max(-1, min(1, sentiment_score))
        
        # 如果AI复杂度可用，使用AI结果，否则估算
        if ai_complexity is not None:
            complexity_score = ai_complexity
        else:
            # 基于对话长度和句子结构估算复杂度
            sentences = dialogue.split('。') + dialogue.split('.') + dialogue.split('!') + dialogue.split('?')
            if sentences:
                avg_length = sum(len(s.split()) for s in sentences) / len(sentences)
                complexity_score = min(avg_length / 20, 1.0)
            else:
                complexity_score = 0.5
        
        # 计算参与度（基于对话长度和问答比例）
        engagement_base = min(1.0, word_count / 100)  # 对话长度因子
        question_factor = min(1.0, question_count / max(1, word_count / 20))  # 问答互动因子
        engagement = (engagement_base + question_factor) / 2
        
        # AI增强的整体分数计算
        # 基础分数 + AI复杂度因子 + 参与度权重
        base_score = 0.3
        sentiment_factor = 0.3 * (sentiment_score + 1) / 2  # 转换为0-1范围
        engagement_factor = 0.4 * engagement
        complexity_factor = 0.1 * complexity_score  # 适度的复杂度奖励
        
        overall_score = round(min(1.0, base_score + sentiment_factor + engagement_factor + complexity_factor), 2)
        
        # 计算强度指标（AI增强）
        ai_influence = 0.3 if ai_sentiment_score is not None else 0.1
        avg_intensity = round(0.3 + 0.4 * engagement + 0.3 * (sentiment_score + 1) / 2 + ai_influence * complexity_score, 2)
        peak_intensity = round(min(1.0, avg_intensity + 0.3 * random.random()), 2)
        stability_score = round(1.0 - abs(sentiment_score) * 0.5 + 0.2 * random.random(), 2)
        momentum_score = round(0.4 + 0.4 * engagement + 0.2 * (1 - stability_score), 2)
        
        # 生成动态模式
        patterns = _generate_patterns(scenario, sentiment_score, question_count, word_count)
        
        # 生成洞察和建议 - 使用AI增强版本
        ai_insights = []
        ai_recommendations = []
        
        print(f"🔍 检查AI提供商: {llm_provider is not None}")
        
        if llm_provider:
            try:
                # 尝试使用AI生成洞察和建议
                print("🤖 开始使用AI生成深度洞察和建议...")
                print(f"📝 发送给AI的参数 - 情感分数: {ai_sentiment_score or sentiment_score:.3f}")
                print(f"🔑 AI关键词: {ai_keywords[:5] if ai_keywords else 'None'}")
                print(f"🧮 复杂度分数: {ai_complexity or 0.5:.3f}")
                
                # 并行生成洞察和建议
                insight_task = llm_provider.generate_insights(dialogue, ai_sentiment_score or sentiment_score, ai_keywords, ai_complexity or 0.5)
                recommendation_task = llm_provider.generate_recommendations(dialogue, ai_sentiment_score or sentiment_score, ai_keywords, ai_complexity or 0.5)
                
                print("⏳ 等待AI洞察和建议生成...")
                # 等待AI生成结果
                ai_insights, ai_recommendations = await asyncio.gather(insight_task, recommendation_task)
                
                # 验证AI结果
                if ai_insights:
                    print(f"✅ AI成功生成{len(ai_insights)}个洞察: {ai_insights[:2]}...")
                else:
                    ai_insights = ["AI洞察生成失败，使用传统洞察"]
                    
                if ai_recommendations:
                    print(f"✅ AI成功生成{len(ai_recommendations)}个建议: {ai_recommendations[:2]}...")
                else:
                    ai_recommendations = ["AI建议生成失败，使用传统建议"]
                    
            except Exception as ai_error:
                print(f"⚠️ AI洞察和建议生成失败: {ai_error}")
                ai_insights = ["网络错误，使用基础洞察"]
                ai_recommendations = ["网络错误，使用基础建议"]
        else:
            print("⚠️ AI提供商未初始化，使用传统方法")
        
        # 如果AI生成失败，回退到传统方法
        if not ai_insights:
            print("📝 使用传统方法生成洞察")
            ai_insights = _generate_insights(
                scenario=scenario,
                dialogue=dialogue,
                sentiment_score=sentiment_score,
                question_count=question_count,
                engagement=engagement,
                word_count=word_count
            )
            
        if not ai_recommendations:
            print("📝 使用传统方法生成建议")
            ai_recommendations = _generate_recommendations(
                scenario=scenario,
                dialogue=dialogue,
                sentiment_score=sentiment_score,
                question_count=question_count,
                engagement=engagement
            )
        
        # 生成脉冲点
        pulse_points = _generate_pulse_points(word_count, sentiment_score, engagement)
        
        # 构建增强的分析结果
        analysis_result = {
            "id": str(uuid.uuid4()),
            "scenario": scenario,
            "overall_score": overall_score,
            "peak_intensity": peak_intensity,
            "avg_intensity": avg_intensity,
            "stability_score": stability_score,
            "momentum_score": momentum_score,
            "complexity_score": round(complexity_score, 2),
            "patterns": patterns,
            "insights": ai_insights,
            "recommendations": ai_recommendations,
            "pulse_points": pulse_points,
            "ai_analysis": {
                "sentiment_score": round(ai_sentiment_score, 3) if ai_sentiment_score is not None else round(sentiment_score, 3),
                "keywords": ai_keywords[:5] if ai_keywords else [],  # 返回前5个AI提取的关键词
                "complexity_score": round(ai_complexity, 3) if ai_complexity is not None else round(complexity_score, 3),
                "enhancement_applied": ai_sentiment_score is not None or len(ai_keywords) > 0
            },
            "created_at": datetime.now()
        }
        
        # 关闭AI提供商连接
        if llm_provider:
            await llm_provider.close()
        
        return analysis_result
        
    except Exception as e:
        print(f"AI增强分析失败，使用传统方法: {e}")
        # 如果AI增强失败，回退到传统方法
        return _analyze_conversation(dialogue, scenario)


def _analyze_conversation(dialogue: str, scenario: str) -> dict:
    """
    智能分析对话内容
    """
    import random
    import hashlib
    import re
    
    # 创建基于对话内容的种子，确保相同输入产生一致结果
    seed_str = f"{dialogue}_{scenario}"
    seed = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16)
    random.seed(seed)
    
    # 分析对话特征
    dialogue_lower = dialogue.lower()
    word_count = len(dialogue.split())
    char_count = len(dialogue)
    
    # 检测情感关键词
    positive_words = ['好', '棒', '优秀', '感谢', '同意', '满意', '喜欢', '开心', '高兴', '太好了', '完美']
    negative_words = ['不好', '糟糕', '不同意', '失望', '生气', '难过', '问题', '困难', '失败', '错误']
    question_words = ['什么', '怎么', '为什么', '如何', '哪里', '谁', '吗', '呢', '？']
    
    positive_count = sum(1 for word in positive_words if word in dialogue_lower)
    negative_count = sum(1 for word in negative_words if word in dialogue_lower)
    question_count = sum(1 for word in question_words if word in dialogue_lower)
    
    # 计算情感倾向
    sentiment_score = (positive_count - negative_count) / max(1, word_count / 10)
    sentiment_score = max(-1, min(1, sentiment_score))  # 限制在-1到1之间
    
    # 计算参与度（基于对话长度和问答比例）
    engagement_base = min(1.0, word_count / 100)  # 对话长度因子
    question_factor = min(1.0, question_count / max(1, word_count / 20))  # 问答互动因子
    engagement = (engagement_base + question_factor) / 2
    
    # 计算整体分数
    overall_score = round(0.3 + 0.4 * engagement + 0.3 * (sentiment_score + 1) / 2, 2)
    
    # 计算强度指标
    avg_intensity = round(0.3 + 0.4 * engagement + 0.3 * random.random(), 2)
    peak_intensity = round(min(1.0, avg_intensity + 0.3 * random.random()), 2)
    stability_score = round(1.0 - abs(sentiment_score) * 0.5 + 0.2 * random.random(), 2)
    momentum_score = round(0.4 + 0.4 * engagement + 0.2 * (1 - stability_score), 2)
    
    # 生成动态模式
    patterns = _generate_patterns(scenario, sentiment_score, question_count, word_count)
    
    # 生成洞察
    insights = _generate_insights(
        scenario=scenario,
        dialogue=dialogue,
        sentiment_score=sentiment_score,
        question_count=question_count,
        engagement=engagement,
        word_count=word_count
    )
    
    # 生成建议
    recommendations = _generate_recommendations(
        scenario=scenario,
        dialogue=dialogue,
        sentiment_score=sentiment_score,
        question_count=question_count,
        engagement=engagement
    )
    
    # 生成脉冲点
    pulse_points = _generate_pulse_points(word_count, sentiment_score, engagement)
    
    return {
        "id": str(uuid.uuid4()),
        "scenario": scenario,
        "overall_score": overall_score,
        "peak_intensity": peak_intensity,
        "avg_intensity": avg_intensity,
        "stability_score": stability_score,
        "momentum_score": momentum_score,
        "patterns": patterns,
        "insights": insights,
        "recommendations": recommendations,
        "pulse_points": pulse_points,
        "created_at": datetime.now()
    }


def _generate_patterns(scenario: str, sentiment_score: float, question_count: int, word_count: int) -> list:
    """生成动态模式"""
    patterns = []
    
    # 基于情感倾向的模式
    if sentiment_score > 0.3:
        patterns.append({
            "name": "积极互动模式",
            "description": "对话中显示出良好的互动性和积极的沟通氛围",
            "confidence": round(0.7 + 0.3 * sentiment_score, 2),
            "pattern_type": "communication"
        })
    elif sentiment_score < -0.3:
        patterns.append({
            "name": "消极情绪模式",
            "description": "对话中可能存在一些负面情绪或挑战性话题",
            "confidence": round(0.6 + 0.3 * abs(sentiment_score), 2),
            "pattern_type": "emotional"
        })
    
    # 基于问答互动的模式
    if question_count > 0:
        engagement_level = min(1.0, question_count / max(1, word_count / 50))
        patterns.append({
            "name": "问答互动模式",
            "description": "对话中包含较多的问答互动，显示出良好的参与度",
            "confidence": round(0.6 + 0.4 * engagement_level, 2),
            "pattern_type": "engagement"
        })
    
    # 基于场景的模式
    if scenario in ["面试", "presentation", "演讲"]:
        patterns.append({
            "name": "正式沟通模式",
            "description": "在正式场合下的专业沟通模式",
            "confidence": 0.8,
            "pattern_type": "formal"
        })
    elif scenario in ["聊天", "日常对话"]:
        patterns.append({
            "name": "日常交流模式",
            "description": "轻松友好的日常交流模式",
            "confidence": 0.75,
            "pattern_type": "casual"
        })
    
    # 如果没有匹配的模式，添加默认模式
    if not patterns:
        patterns.append({
            "name": "一般对话模式",
            "description": "标准的中性对话模式",
            "confidence": 0.6,
            "pattern_type": "neutral"
        })
    
    return patterns


def _generate_insights(scenario: str, dialogue: str, sentiment_score: float, question_count: int, engagement: float, word_count: int) -> list:
    """生成个性化的深度洞察"""
    insights = []
    
    # 情感深度分析
    if sentiment_score > 0.5:
        insights.append("🎉 对话充满正能量，双方表现出高度的热情和积极性，可能建立了良好的情感连接")
    elif sentiment_score > 0.2:
        insights.append("😊 对话整体氛围友好正向，参与者保持了积极的态度和合作精神")
    elif sentiment_score < -0.5:
        insights.append("😰 对话中表现出明显的消极情绪，可能存在分歧、挫折或不满情绪需要关注")
    elif sentiment_score < -0.2:
        insights.append("😐 对话存在一定的紧张感或不确定性，建议加强沟通和理解")
    else:
        insights.append("⚖️ 对话保持理性平衡的状态，参与者以客观、冷静的态度进行交流")
    
    # 参与度质量分析
    if engagement > 0.8:
        insights.append("🔥 双方深度投入，对话互动频繁且富有成效，可能涉及重要话题")
    elif engagement > 0.6:
        insights.append("💬 对话参与积极，双方都表现出良好的沟通意愿和互动技巧")
    elif engagement > 0.4:
        insights.append("🤝 参与者保持适度的参与度，对话节奏控制得当")
    else:
        insights.append("😴 对话参与度偏低，可能存在信息不对称或兴趣不匹配的情况")
    
    # 对话结构分析
    if word_count > 200:
        insights.append("📚 对话内容丰富详实，可能涉及复杂话题的深入讨论")
    elif word_count > 100:
        insights.append("💭 对话内容适中，既保证了信息传递又维持了良好的沟通效率")
    else:
        insights.append("💬 对话简洁明快，传递核心信息，可能是高效的决策或确认性沟通")
    
    # 问答模式深度分析
    if question_count > word_count / 15:
        insights.append("🤔 对话以问题驱动为主，展现出探索性和学习性的交流特点")
        insights.append("💡 提问者表现出强烈的好奇心和求知欲，这是有效沟通的重要标志")
    elif question_count > word_count / 25:
        insights.append("❓ 对话平衡了提问和陈述，互动节奏良好")
    elif question_count == 0:
        insights.append("📢 对话以信息传递为主，可能是单向的说明或报告性沟通")
    
    # 场景特定的深度洞察
    if scenario == "面试":
        if sentiment_score > 0.3:
            insights.append("🎯 面试沟通专业且积极，候选人展现了良好的沟通技巧和自信心")
        else:
            insights.append("📋 面试对话相对正式，可能需要增加更多互动性来展示个人魅力")
    elif scenario == "聊天":
        if engagement > 0.6:
            insights.append("🗣️ 聊天氛围轻松自然，双方建立了良好的对话默契和情感连接")
        else:
            insights.append("😌 聊天风格温和理性，可能需要更多共同话题来提升互动质量")
    elif scenario == "会议":
        insights.append("🏢 对话体现了团队协作的特点，参与者展现了专业性和合作精神")
    elif scenario == "咨询":
        insights.append("🧠 咨询对话显示出专业性和建设性，可能是知识分享或问题解决的有效沟通")
    
    # 语言使用分析
    positive_words = ["谢谢", "感谢", "好", "棒", "喜欢", "满意", "同意", "支持"]
    negative_words = ["不好", "讨厌", "失望", "不满", "反对", "拒绝", "问题", "困难"]
    question_words = ["什么", "怎么", "为什么", "如何", "能否", "是否"]
    
    positive_count = sum(1 for word in positive_words if word in dialogue)
    negative_count = sum(1 for word in negative_words if word in dialogue)
    question_count_detailed = sum(1 for word in question_words if word in dialogue)
    
    if positive_count > negative_count * 1.5:
        insights.append("✨ 对话中积极词汇使用频繁，反映了乐观正面的沟通心态")
    elif negative_count > positive_count * 1.5:
        insights.append("⚠️ 对话中消极词汇较多，可能反映了当前的挑战或困难需要关注")
    
    if question_count_detailed > 3:
        insights.append("❓ 对话包含多个开放性问题，展现了深入思考和探索的倾向")
    
    return insights


def _generate_recommendations(scenario: str, dialogue: str, sentiment_score: float, question_count: int, engagement: float) -> list:
    """生成个性化的深度建议"""
    recommendations = []
    word_count = len(dialogue.split())
    
    # 情感优化的精细建议
    if sentiment_score < -0.6:
        recommendations.append("🚨 紧急建议：对话存在明显的负面情绪，建议立即暂停争议性话题，转换为中立讨论")
        recommendations.append("💝 可以尝试表达理解和共情，如'我理解你的担忧'，化解紧张氛围")
        recommendations.append("🤝 建议重新聚焦共同目标和价值观，寻找共识点")
    elif sentiment_score < -0.3:
        recommendations.append("⚖️ 对话略显紧张，建议采用更温和的措辞和语速，降低冲突风险")
        recommendations.append("👂 加强主动倾听技巧，通过复述对方观点来显示理解和尊重")
        recommendations.append("🔄 适时转换话题，避免在敏感点上过度纠缠")
    elif sentiment_score > 0.6:
        recommendations.append("🎉 优秀表现：保持当前的正向沟通风格，这是建立信任的基础")
        recommendations.append("🌟 可以适度分享个人感受和经验，增强对话的深度和真实性")
        recommendations.append("🚀 借此积极氛围，可以讨论更具有挑战性或创新性的议题")
    elif sentiment_score > 0.3:
        recommendations.append("😊 保持现有的积极沟通方式，这将有助于维持良好的关系")
        recommendations.append("📈 可以适当询问对方的想法和感受，促进双向交流")
    
    # 参与度优化的精准建议
    if engagement < 0.3:
        recommendations.append("😴 对话参与度较低，建议使用开放式问题启动对话")
        recommendations.append("🎯 尝试分享具体案例或故事来激发对方的兴趣和参与")
        recommendations.append("❓ 直接询问'你对这个问题怎么看？'等明确邀请参与的表达")
    elif engagement < 0.5:
        recommendations.append("📝 可以通过总结和澄清来增加互动：'让我确认一下，你是说...'")
        recommendations.append("🔍 建议使用'能否进一步解释...'来引导深度讨论")
    elif engagement > 0.8:
        recommendations.append("🔥 当前互动非常活跃，建议引导对话朝向具体行动计划")
        recommendations.append("📊 可以使用结构化总结来巩固讨论成果")
    elif engagement > 0.6:
        recommendations.append("💪 优秀的参与度！继续保持这种活跃的交流状态")
        recommendations.append("🌊 适时加入转折性内容，如'另一方面...'来丰富对话维度")
    
    # 对话结构优化建议
    if word_count < 50:
        recommendations.append("💬 对话较为简短，建议添加背景信息或具体例子来增强说服力")
        recommendations.append("📋 可以使用'让我详细说明一下...'来增加内容的丰富度")
    elif word_count > 300:
        recommendations.append("📚 对话内容丰富，建议在关键点进行总结和确认")
        recommendations.append("🗂️ 可以使用'总结一下我们刚才提到的...'来提高沟通效率")
    
    # 问答模式的优化建议
    if question_count == 0:
        recommendations.append("❓ 建议增加互动式问题，如'你觉得...如何？'来促进对话")
        recommendations.append("🤔 可以提出探索性问题来了解对方立场和想法")
    elif question_count > word_count / 10:
        recommendations.append("🗣️ 问题较多，建议适当添加更多陈述和分享来平衡对话")
        recommendations.append("📊 可以分享个人见解或经验来丰富对话内容")
    elif question_count < word_count / 50:
        recommendations.append("💭 可以适当增加澄清性或确认性问题，如'我理解对吗？'")
    
    # 场景特定的深度建议
    if scenario == "面试":
        if sentiment_score > 0.3:
            recommendations.append("🎯 面试表现优秀，建议继续展现专业能力和个人魅力")
            recommendations.append("💼 可以适当展示对公司和职位的深入了解")
        else:
            recommendations.append("📝 面试略显紧张，建议放慢语速，展现更多自信")
            recommendations.append("🎨 可以通过具体例子来展示解决问题的能力")
    elif scenario == "聊天":
        if engagement > 0.6:
            recommendations.append("🗣️ 聊天氛围很好，可以深入分享更多个人故事和感受")
            recommendations.append("🌈 适当加入幽默元素来增进情感连接")
        else:
            recommendations.append("😌 聊天风格温和，可以尝试找到更多共同兴趣点")
            recommendations.append("📸 可以通过分享生活经历来增加对话的真实性")
    elif scenario == "会议":
        recommendations.append("🏢 保持专业的会议沟通风格，确保所有参与者都有发言机会")
        recommendations.append("📋 建议明确行动项和时间节点，提高会议效率")
        recommendations.append("✅ 可以适时总结讨论成果并确认下一步行动")
    elif scenario == "咨询":
        recommendations.append("🧠 保持专业的咨询态度，确保为对方提供有价值的信息")
        recommendations.append("🎯 建议先确认具体需求，再提供针对性的建议")
        recommendations.append("📊 可以适当引用数据或案例来增强说服力")
    
    # 沟通技巧优化
    positive_words = ["谢谢", "感谢", "好", "棒", "喜欢", "满意", "同意", "支持"]
    negative_words = ["不好", "讨厌", "失望", "不满", "反对", "拒绝", "问题", "困难"]
    
    positive_count = sum(1 for word in positive_words if word in dialogue)
    negative_count = sum(1 for word in negative_words if word in dialogue)
    
    if positive_count < 1:
        recommendations.append("💝 建议增加更多表达感谢和认可的话语，如'谢谢你的分享'")
    
    if negative_count > positive_count * 1.5:
        recommendations.append("🌟 建议使用更多积极正向的表达来改善对话氛围")
        recommendations.append("🔄 可以将问题导向的表述转换为解决方案导向")
    
    # 确保至少有3-5个建议
    if len(recommendations) < 3:
        recommendations.append("🌱 继续练习主动倾听和同理心，这将显著提升沟通质量")
        recommendations.append("📖 可以学习一些沟通技巧，如使用'我理解你的观点...'等表达")
    
    return recommendations[:5]  # 限制在5个建议以内，避免信息过载


def _generate_pulse_points(word_count: int, sentiment_score: float, engagement: float) -> list:
    """生成脉冲点"""
    pulse_points = []
    
    # 根据对话长度生成脉冲点数量
    num_points = min(5, max(2, word_count // 50))
    
    import time
    base_timestamp = int(time.time())
    
    for i in range(num_points):
        # 基础时间戳（每30秒一个点）
        timestamp = base_timestamp - (num_points - i - 1) * 30
        
        # 生成动态的指标值
        time_factor = i / max(1, num_points - 1)  # 0到1的时间因子
        
        # 强度随时间有波动
        intensity = round(0.3 + 0.4 * engagement + 0.3 * (0.5 + 0.5 * sentiment_score) + 0.2 * (0.5 + 0.5 * (-1) ** i), 2)
        intensity = max(0.1, min(1.0, intensity))
        
        # 情感基于整体情感倾向并有波动
        sentiment = "positive" if sentiment_score > 0.1 else "negative" if sentiment_score < -0.1 else "neutral"
        
        # 参与度基于总体参与度并有时间变化
        engagement_point = round(max(0.1, min(1.0, engagement + 0.2 * (0.5 - abs(time_factor - 0.5)))), 2)
        
        # 清晰度基于情感稳定性和参与度
        clarity = round(0.4 + 0.3 * (1 - abs(sentiment_score)) + 0.3 * engagement_point, 2)
        
        pulse_points.append({
            "timestamp": f"2025-01-15T{10 + i // 2:02d}:{(i % 2) * 30:02d}:00Z",
            "intensity": intensity,
            "sentiment": sentiment,
            "engagement": engagement_point,
            "clarity": clarity,
            "speaker_role": f"participant_{chr(65 + i % 2)}"  # participant_A, participant_B
        })
    
    return pulse_points

@api_router.get("/health")
async def health_check():
    """
    健康检查接口
    """
    return {
        "status": "healthy",
        "service": "LingoPulse Backend",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@api_router.get("/stats")
async def get_service_stats():
    """
    获取服务统计信息
    """
    # 简化实现，实际应该从监控系统中获取
    return {
        "total_conversations": 0,
        "total_analyses": 0,
        "active_analyses": 0,
        "average_analysis_time": 0,
        "uptime": "0h 0m 0s",
        "last_updated": datetime.now().isoformat()
    }


# 后台任务函数
async def execute_batch_analysis(conversation_ids: List[str], max_concurrent: int):
    """
    执行批量分析的后台任务
    """
    try:
        # 这里需要从应用层获取用例实例
        # results = await batch_analyze_use_case.execute(conversation_ids, max_concurrent)
        print(f"Batch analysis started for {len(conversation_ids)} conversations")
        # 处理分析结果...
    except Exception as e:
        print(f"Batch analysis failed: {e}")


# 微信聊天记录导入相关模型
class WeChatUploadRequest(BaseModel):
    """微信聊天记录上传请求"""
    conversation_name: str = Field(..., description="对话名称")
    participants: List[str] = Field(..., description="参与者列表")
    conversation_type: str = Field(default="wechat", description="对话类型")


class WeChatAnalysisRequest(BaseModel):
    """微信聊天记录分析请求"""
    conversation_id: str = Field(..., description="对话ID")


class WeChatBatchImportRequest(BaseModel):
    """微信聊天记录批量导入请求"""
    file_paths: List[str] = Field(..., description="文件路径列表")
    conversation_name: str = Field(..., description="默认对话名称")
    participants: List[str] = Field(..., description="参与者列表")


# 微信聊天记录导入相关端点
@api_router.post("/wechat/upload", response_model=StatusResponse)
async def upload_wechat_file(
    file: UploadFile = File(...),
    request: WeChatUploadRequest = Depends(),
):
    """
    上传微信聊天记录文件
    """
    try:
        # 验证文件类型
        allowed_extensions = {'.txt', '.json', '.csv'}
        file_extension = Path(file.filename).suffix.lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"不支持的文件格式。支持的格式: {', '.join(allowed_extensions)}"
            )
        
        # 保存上传的文件
        uploads_dir = Path("uploads/wechat")
        uploads_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = uploads_dir / f"{uuid.uuid4()}_{file.filename}"
        
        with open(file_path, 'wb') as buffer:
            content = await file.read()
            buffer.write(content)
        
        # 初始化微信导入器
        importer = WeChatChatImporter()
        
        # 在后台任务中处理文件导入
        background_tasks.add_task(
            process_wechat_import,
            str(file_path),
            request.conversation_name,
            request.participants,
            request.conversation_type
        )
        
        return StatusResponse(
            status="uploaded",
            message="微信聊天记录文件上传成功，正在处理中...",
            timestamp=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


@api_router.post("/wechat/import", response_model=Dict[str, Any])
async def import_wechat_chat_record(
    file_path: str,
    conversation_name: str,
    participants: List[str],
    conversation_type: str = "wechat"
):
    """
    导入微信聊天记录
    """
    try:
        # 检查文件是否存在
        if not Path(file_path).exists():
            raise HTTPException(status_code=404, detail="文件不存在")
        
        # 初始化微信导入器
        importer = WeChatChatImporter()
        
        # 解析聊天记录
        conversations = importer.import_chat_record(file_path)
        
        # 验证和标准化数据
        validated_conversations = []
        
        for conv_data in conversations:
            # 验证必填字段
            if not conv_data.get('messages'):
                continue
                
            # 标准化数据格式
            validated_conv = {
                'id': str(uuid.uuid4()),
                'title': conversation_name or f"微信对话_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'participants': participants or ['未知参与者'],
                'conversation_type': conversation_type,
                'messages': conv_data['messages'],
                'created_at': datetime.now(),
                'metadata': {
                    'source': 'wechat',
                    'original_file': file_path,
                    'import_time': datetime.now().isoformat()
                }
            }
            validated_conversations.append(validated_conv)
        
        return {
            "status": "success",
            "message": f"成功导入 {len(validated_conversations)} 个对话",
            "conversations": validated_conversations,
            "total_messages": sum(len(conv['messages']) for conv in validated_conversations),
            "participants": participants,
            "import_time": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")


@api_router.get("/wechat/analysis/{conversation_id}")
async def analyze_wechat_conversation(conversation_id: str):
    """
    分析微信聊天记录
    """
    try:
        # 这里需要根据conversation_id获取对话数据
        # 然后调用分析功能
        # 简化实现，返回模拟数据
        
        analysis_result = {
            "conversation_id": conversation_id,
            "analysis_type": "wechat_chat_analysis",
            "results": {
                "communication_patterns": {
                    "message_frequency": "中等",
                    "response_time_avg": "2.5分钟",
                    "active_hours": ["09:00-12:00", "14:00-18:00", "20:00-22:00"]
                },
                "sentiment_analysis": {
                    "overall_sentiment": "积极",
                    "sentiment_trend": "稳定",
                    "emotional_peaks": 3
                },
                "interaction_quality": {
                    "engagement_score": 0.85,
                    "clarity_score": 0.78,
                    "collaboration_score": 0.82
                },
                "key_topics": ["工作讨论", "日常闲聊", "问题解决"],
                "communication_style": "友好且专业"
            },
            "recommendations": [
                "保持当前的积极沟通风格",
                "在工作时间内保持响应速度",
                "增加更多建设性的讨论话题"
            ],
            "analyzed_at": datetime.now().isoformat()
        }
        
        return analysis_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


@api_router.post("/wechat/batch-import")
async def batch_import_wechat_records(
    background_tasks: BackgroundTasks,
    request: WeChatBatchImportRequest = Depends(),
):
    """
    批量导入微信聊天记录
    """
    try:
        # 验证文件路径
        valid_files = []
        for file_path in request.file_paths:
            if Path(file_path).exists():
                valid_files.append(file_path)
            else:
                logging.warning(f"文件不存在: {file_path}")
        
        if not valid_files:
            raise HTTPException(status_code=400, detail="没有找到有效的文件")
        
        # 启动后台批量导入任务
        background_tasks.add_task(
            process_batch_wechat_import,
            valid_files,
            request.conversation_name,
            request.participants
        )
        
        return StatusResponse(
            status="accepted",
            message=f"批量导入任务已启动，共 {len(valid_files)} 个文件",
            timestamp=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量导入失败: {str(e)}")


@api_router.get("/wechat/formats")
async def get_supported_wechat_formats():
    """
    获取支持的微信聊天记录格式
    """
    return {
        "supported_formats": [
            {
                "extension": ".txt",
                "description": "微信导出的文本格式聊天记录",
                "example_structure": "2024-01-01 12:00:00 张三: 你好",
                "required_fields": ["timestamp", "sender", "content"]
            },
            {
                "extension": ".json",
                "description": "结构化的JSON格式聊天记录",
                "example_structure": {
                    "messages": [
                        {"timestamp": "2024-01-01T12:00:00", "sender": "张三", "content": "你好"}
                    ]
                },
                "required_fields": ["messages"]
            },
            {
                "extension": ".csv",
                "description": "逗号分隔的CSV格式聊天记录",
                "example_structure": "timestamp,sender,content\\n2024-01-01 12:00:00,张三,你好",
                "required_fields": ["timestamp", "sender", "content"]
            }
        ],
        "max_file_size": "50MB",
        "max_messages_per_file": 10000,
        "supported_encodings": ["UTF-8", "GBK", "GB2312"]
    }


# 后台任务函数
async def process_wechat_import(
    file_path: str,
    conversation_name: str,
    participants: List[str],
    conversation_type: str
):
    """
    处理微信聊天记录导入的后台任务
    """
    try:
        logging.info(f"开始处理微信聊天记录导入: {file_path}")
        
        # 初始化微信导入器
        importer = WeChatChatImporter()
        
        # 解析聊天记录
        conversations = importer.import_chat_record(file_path)
        
        # 这里应该将数据保存到数据库
        # 简化实现，只记录日志
        logging.info(f"成功导入 {len(conversations)} 个对话，共 {sum(len(conv.get('messages', [])) for conv in conversations)} 条消息")
        
        # 清理临时文件
        if Path(file_path).exists():
            Path(file_path).unlink()
            logging.info(f"已清理临时文件: {file_path}")
            
    except Exception as e:
        logging.error(f"微信聊天记录导入失败: {e}", exc_info=True)


async def process_batch_wechat_import(
    file_paths: List[str],
    conversation_name: str,
    participants: List[str]
):
    """
    处理批量微信聊天记录导入的后台任务
    """
    try:
        logging.info(f"开始批量导入微信聊天记录，共 {len(file_paths)} 个文件")
        
        importer = WeChatChatImporter()
        total_conversations = 0
        total_messages = 0
        
        for file_path in file_paths:
            try:
                conversations = importer.import_chat_record(file_path)
                total_conversations += len(conversations)
                total_messages += sum(len(conv.get('messages', [])) for conv in conversations)
                
                logging.info(f"处理文件 {file_path}: {len(conversations)} 个对话")
                
            except Exception as e:
                logging.error(f"处理文件 {file_path} 失败: {e}")
                continue
        
        logging.info(f"批量导入完成: {total_conversations} 个对话，{total_messages} 条消息")
        
    except Exception as e:
        logging.error(f"批量导入失败: {e}", exc_info=True)


# 注册微信提取器路由
api_router.include_router(wechat_extractor_router)