"""
飞桨平台API控制器
处理与飞桨平台相关的API请求
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field

from infrastructure.llm_providers.paddle_provider import get_paddle_client, close_paddle_client


# 消息请求模型
class MessageRequest(BaseModel):
    role: str = Field(..., description="消息角色")
    content: str = Field(..., description="消息内容")


# 对话请求模型
class ChatCompletionRequest(BaseModel):
    messages: List[MessageRequest] = Field(..., description="对话历史消息列表")
    model: Optional[str] = Field(None, description="模型名称")
    temperature: Optional[float] = Field(None, description="采样温度")
    max_tokens: Optional[int] = Field(None, description="最大生成长度")


# 令牌请求模型
class TokenRequest(BaseModel):
    access_token: str = Field(..., description="飞桨平台访问令牌")


# 通用响应模型
class ApiResponse(BaseModel):
    success: bool = Field(..., description="请求是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[Dict[str, Any]] = Field(None, description="响应数据")


# 初始化路由器
paddle_router = APIRouter(prefix="/api/v1/paddle", tags=["paddle"])


@paddle_router.post("/token", response_model=ApiResponse)
async def set_paddle_token(request: TokenRequest):
    """设置飞桨平台访问令牌"""
    try:
        # 获取客户端
        client = await get_paddle_client()
        
        # 设置访问令牌
        client.set_access_token(request.access_token)
        
        return ApiResponse(
            success=True,
            message="成功设置飞桨平台访问令牌"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"设置访问令牌失败: {str(e)}")


@paddle_router.post("/chat/completion", response_model=ApiResponse)
async def paddle_chat_completion(request: ChatCompletionRequest, req: Request):
    """飞桨平台对话生成"""
    try:
        # 获取客户端
        client = await get_paddle_client()
        
        # 转换消息格式
        messages = [message.dict() for message in request.messages]
        
        # 调用API
        result = await client.chat_completion(
            messages=messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        # 构建响应
        if result.get("success"):
            return ApiResponse(
                success=True,
                message="成功生成回复",
                data={
                    "text": result.get("text", ""),
                    "model": result.get("model", ""),
                    "usage": result.get("usage", {}),
                    "created_at": result.get("created_at", "")
                }
            )
        else:
            error_msg = result.get("error", "未知错误")
            raise HTTPException(status_code=400, detail=f"飞桨平台API错误: {error_msg}")
    
    except HTTPException:
        raise
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理请求时出错: {str(e)}")


@paddle_router.get("/model", response_model=ApiResponse)
async def get_paddle_model_info():
    """获取飞桨平台模型信息"""
    try:
        # 获取客户端
        client = await get_paddle_client()
        
        # 调用API
        result = await client.get_model_info()
        
        # 构建响应
        if result.get("success"):
            return ApiResponse(
                success=True,
                message="成功获取模型信息",
                data=result.get("model_info", {})
            )
        else:
            error_msg = result.get("error", "未知错误")
            raise HTTPException(status_code=400, detail=f"获取模型信息失败: {error_msg}")
    
    except HTTPException:
        raise
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理请求时出错: {str(e)}")


@paddle_router.get("/test", response_model=ApiResponse)
async def test_paddle_connection():
    """测试飞桨平台连接"""
    try:
        # 获取客户端
        client = await get_paddle_client()
        
        # 调用API
        result = await client.test_connection()
        
        # 构建响应
        if result:
            return ApiResponse(
                success=True,
                message="飞桨平台连接测试成功"
            )
        else:
            raise HTTPException(status_code=400, detail="飞桨平台连接测试失败")
    
    except HTTPException:
        raise
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理请求时出错: {str(e)}")


@paddle_router.get("/health", response_model=ApiResponse)
async def paddle_health_check():
    """飞桨平台健康检查"""
    try:
        # 获取客户端
        client = await get_paddle_client()
        
        # 检查是否有访问令牌
        if not client.access_token:
            return ApiResponse(
                success=False,
                message="飞桨平台健康检查失败：未设置访问令牌"
            )
        
        # 返回健康状态
        return ApiResponse(
            success=True,
            message="飞桨平台健康状态正常"
        )
    
    except Exception as e:
        return ApiResponse(
            success=False,
            message=f"飞桨平台健康检查失败：{str(e)}"
        )