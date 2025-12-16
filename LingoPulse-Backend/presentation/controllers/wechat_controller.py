#!/usr/bin/env python3
"""
微信聊天记录处理API控制器
提供微信聊天记录的导入、解析和分析功能
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import tempfile
import shutil
from pathlib import Path
import uuid
import json

from infrastructure.data_importers.wechat_importer import WeChatChatImporter
from domain.entities import Conversation
from application.usecases import AnalyzeConversationUseCase


# Pydantic模型
class WeChatImportRequest(BaseModel):
    """微信聊天记录导入请求"""
    file_format: str = Field(default="auto", description="文件格式 (auto/json/csv/txt)")
    preserve_original_names: bool = Field(default=True, description="是否保留原始用户名")
    filter_system_messages: bool = Field(default=True, description="是否过滤系统消息")
    encoding: str = Field(default="utf-8", description="文件编码")


class WeChatMessageItem(BaseModel):
    """微信消息项"""
    timestamp: str
    sender: str
    content: str
    speaker_role: str
    message_type: str = "text"


class WeChatConversationResponse(BaseModel):
    """微信对话响应"""
    id: str
    conversation_type: str
    participants: List[str]
    total_messages: int
    first_message_time: str
    last_message_time: str
    sample_messages: List[WeChatMessageItem]
    metadata: Dict[str, Any]


class WeChatImportResponse(BaseModel):
    """微信导入响应"""
    success: bool
    message: str
    conversations: List[WeChatConversationResponse]
    total_processed: int
    processed_files: List[str]


class WeChatAnalysisRequest(BaseModel):
    """微信分析请求"""
    conversation_id: str
    analysis_options: Dict[str, Any] = Field(default_factory=dict)


# 路由器
router = APIRouter(prefix="/api/v1/wechat", tags=["wechat"])

# 全局变量存储导入的对话
_imported_conversations: Dict[str, Conversation] = {}


@router.post("/import", response_model=WeChatImportResponse)
async def import_wechat_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="微信聊天记录文件"),
    file_format: str = Form("auto", description="文件格式"),
    preserve_names: bool = Form(True, description="保留原始用户名"),
    filter_system: bool = Form(True, description="过滤系统消息")
):
    """
    导入微信聊天记录文件
    
    支持的格式:
    - .txt: 文本格式的聊天记录
    - .json: JSON格式的聊天记录  
    - .csv: CSV格式的聊天记录
    """
    
    # 验证文件格式
    allowed_extensions = ['.txt', '.json', '.csv']
    file_extension = Path(file.filename).suffix.lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"不支持的文件格式: {file_extension}。支持的格式: {', '.join(allowed_extensions)}"
        )
    
    # 创建临时文件
    temp_dir = Path(tempfile.gettempdir()) / "lingopulse_wechat"
    temp_dir.mkdir(exist_ok=True)
    
    temp_file_path = temp_dir / f"{uuid.uuid4()}{file_extension}"
    
    try:
        # 保存上传的文件
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 使用导入器处理文件
        importer = WeChatChatImporter()
        conversations = importer.import_from_file(temp_file_path, file_format)
        
        # 处理导入的对话
        processed_conversations = []
        conversation_ids = []
        
        for conv in conversations:
            # 生成唯一ID
            conv_id = str(uuid.uuid4())
            
            # 过滤消息（如果需要）
            if filter_system:
                conv.turns = [
                    turn for turn in conv.turns 
                    if not turn.content.startswith(('系统消息', '系统提示'))
                ]
            
            # 存储对话
            _imported_conversations[conv_id] = conv
            conversation_ids.append(conv_id)
            
            # 构建响应数据
            if conv.turns:
                first_msg_time = conv.turns[0].timestamp.isoformat()
                last_msg_time = conv.turns[-1].timestamp.isoformat()
                
                # 提取示例消息（前10条）
                sample_messages = []
                for turn in conv.turns[:10]:
                    sample_messages.append(WeChatMessageItem(
                        timestamp=turn.timestamp.isoformat(),
                        sender=turn.metadata.get('original_sender', '未知'),
                        content=turn.content,
                        speaker_role=turn.speaker_role.value,
                        message_type=turn.metadata.get('message_type', 'text')
                    ))
                
                response_conv = WeChatConversationResponse(
                    id=conv_id,
                    conversation_type=conv.conversation_type.value,
                    participants=conv.participants,
                    total_messages=len(conv.turns),
                    first_message_time=first_msg_time,
                    last_message_time=last_msg_time,
                    sample_messages=sample_messages,
                    metadata=conv.metadata
                )
                
                processed_conversations.append(response_conv)
        
        # 清理临时文件
        background_tasks.add_task(cleanup_temp_file, temp_file_path)
        
        return WeChatImportResponse(
            success=True,
            message=f"成功导入 {len(conversations)} 个对话",
            conversations=processed_conversations,
            total_processed=len(processed_conversations),
            processed_files=[file.filename]
        )
        
    except Exception as e:
        # 清理临时文件
        cleanup_temp_file(temp_file_path)
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")


@router.post("/analyze/{conversation_id}")
async def analyze_wechat_conversation(
    conversation_id: str,
    analysis_options: Optional[WeChatAnalysisRequest] = None
):
    """
    分析微信对话
    
    Args:
        conversation_id: 对话ID
        analysis_options: 分析选项（可选）
    """
    
    if conversation_id not in _imported_conversations:
        raise HTTPException(status_code=404, detail="对话未找到")
    
    try:
        conversation = _imported_conversations[conversation_id]
        
        # 使用分析用例
        use_case = AnalyzeConversationUseCase()
        result = use_case.execute(conversation)
        
        return {
            "success": True,
            "conversation_id": conversation_id,
            "analysis_result": {
                "features": result.features.dict(),
                "pulse_score": result.pulse_score,
                "insights": result.insights,
                "recommendations": result.recommendations
            },
            "metadata": {
                "analysis_time": datetime.now().isoformat(),
                "total_messages": len(conversation.turns),
                "participants": conversation.participants
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


@router.get("/conversations")
async def list_imported_conversations():
    """获取已导入的对话列表"""
    
    conversations_info = []
    
    for conv_id, conv in _imported_conversations.items():
        if conv.turns:
            conversations_info.append({
                "id": conv_id,
                "conversation_type": conv.conversation_type.value,
                "participants": conv.participants,
                "total_messages": len(conv.turns),
                "first_message_time": conv.turns[0].timestamp.isoformat(),
                "last_message_time": conv.turns[-1].timestamp.isoformat(),
                "metadata": conv.metadata
            })
    
    return {
        "success": True,
        "total_conversations": len(conversations_info),
        "conversations": conversations_info
    }


@router.get("/conversations/{conversation_id}")
async def get_conversation_details(conversation_id: str):
    """获取对话详情"""
    
    if conversation_id not in _imported_conversations:
        raise HTTPException(status_code=404, detail="对话未找到")
    
    conversation = _imported_conversations[conversation_id]
    
    # 转换所有消息
    all_messages = []
    for turn in conversation.turns:
        all_messages.append(WeChatMessageItem(
            timestamp=turn.timestamp.isoformat(),
            sender=turn.metadata.get('original_sender', '未知'),
            content=turn.content,
            speaker_role=turn.speaker_role.value,
            message_type=turn.metadata.get('message_type', 'text')
        ))
    
    return {
        "success": True,
        "conversation": {
            "id": conversation_id,
            "conversation_type": conversation.conversation_type.value,
            "participants": conversation.participants,
            "total_messages": len(conversation.turns),
            "messages": all_messages,
            "metadata": conversation.metadata
        }
    }


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """删除导入的对话"""
    
    if conversation_id not in _imported_conversations:
        raise HTTPException(status_code=404, detail="对话未找到")
    
    del _imported_conversations[conversation_id]
    
    return {
        "success": True,
        "message": f"对话 {conversation_id} 已删除"
    }


@router.post("/batch-import")
async def batch_import_wechat_files(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(..., description="多个微信聊天记录文件")
):
    """
    批量导入多个微信聊天记录文件
    """
    
    if len(files) > 10:  # 限制最多10个文件
        raise HTTPException(status_code=400, detail="一次最多只能导入10个文件")
    
    all_conversations = []
    processed_files = []
    errors = []
    
    temp_dir = Path(tempfile.gettempdir()) / "lingopulse_wechat_batch"
    temp_dir.mkdir(exist_ok=True)
    
    try:
        for file in files:
            try:
                # 验证文件格式
                file_extension = Path(file.filename).suffix.lower()
                if file_extension not in ['.txt', '.json', '.csv']:
                    errors.append(f"{file.filename}: 不支持的文件格式")
                    continue
                
                # 保存临时文件
                temp_file_path = temp_dir / f"{uuid.uuid4()}{file_extension}"
                
                with open(temp_file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                
                # 导入文件
                importer = WeChatChatImporter()
                conversations = importer.import_from_file(temp_file_path, "auto")
                
                for conv in conversations:
                    conv_id = str(uuid.uuid4())
                    _imported_conversations[conv_id] = conv
                    
                    # 构建响应
                    if conv.turns:
                        response_conv = WeChatConversationResponse(
                            id=conv_id,
                            conversation_type=conv.conversation_type.value,
                            participants=conv.participants,
                            total_messages=len(conv.turns),
                            first_message_time=conv.turns[0].timestamp.isoformat(),
                            last_message_time=conv.turns[-1].timestamp.isoformat(),
                            sample_messages=[
                                WeChatMessageItem(
                                    timestamp=turn.timestamp.isoformat(),
                                    sender=turn.metadata.get('original_sender', '未知'),
                                    content=turn.content,
                                    speaker_role=turn.speaker_role.value,
                                    message_type=turn.metadata.get('message_type', 'text')
                                ) for turn in conv.turns[:5]  # 批量导入只返回前5条示例
                            ],
                            metadata=conv.metadata
                        )
                        all_conversations.append(response_conv)
                
                processed_files.append(file.filename)
                
                # 清理临时文件
                background_tasks.add_task(cleanup_temp_file, temp_file_path)
                
            except Exception as e:
                errors.append(f"{file.filename}: {str(e)}")
        
        # 清理批量导入目录
        background_tasks.add_task(cleanup_temp_dir, temp_dir)
        
        return WeChatImportResponse(
            success=len(all_conversations) > 0,
            message=f"成功导入 {len(all_conversations)} 个对话，处理了 {len(processed_files)} 个文件",
            conversations=all_conversations,
            total_processed=len(all_conversations),
            processed_files=processed_files
        )
        
    except Exception as e:
        # 清理临时目录
        cleanup_temp_dir(temp_dir)
        raise HTTPException(status_code=500, detail=f"批量导入失败: {str(e)}")


@router.get("/supported-formats")
async def get_supported_formats():
    """获取支持的微信聊天记录格式信息"""
    
    return {
        "supported_extensions": [".txt", ".json", ".csv"],
        "format_examples": {
            "txt": [
                "2023-12-01 10:30:25 张三: 你好",
                "2023-12-01 10:31:10 李四: 早上好！"
            ],
            "json": [
                {
                    "timestamp": "2023-12-01T10:30:25",
                    "sender": "张三",
                    "content": "你好",
                    "type": "text"
                }
            ],
            "csv": [
                "timestamp,sender,content,type",
                "2023-12-01 10:30:25,张三,你好,text"
            ]
        },
        "features": {
            "auto_format_detection": True,
            "batch_import": True,
            "system_message_filtering": True,
            "encoding_support": ["utf-8", "gbk", "gb2312"],
            "max_file_size": "50MB",
            "max_files_per_batch": 10
        }
    }


# 工具函数
async def cleanup_temp_file(file_path: Path):
    """清理临时文件"""
    try:
        if file_path.exists():
            file_path.unlink()
    except:
        pass


async def cleanup_temp_dir(dir_path: Path):
    """清理临时目录"""
    try:
        if dir_path.exists():
            shutil.rmtree(dir_path)
    except:
        pass


# 使用示例和文档
@router.get("/documentation")
async def get_documentation():
    """获取微信聊天记录处理功能的使用文档"""
    
    return {
        "title": "微信聊天记录处理API文档",
        "version": "1.0.0",
        "description": "提供微信聊天记录的导入、解析和分析功能",
        "endpoints": {
            "POST /api/v1/wechat/import": {
                "description": "导入单个微信聊天记录文件",
                "parameters": {
                    "file": "上传的聊天记录文件",
                    "file_format": "文件格式 (auto/json/csv/txt)",
                    "preserve_names": "是否保留原始用户名",
                    "filter_system": "是否过滤系统消息"
                },
                "response": "导入的对话信息"
            },
            "POST /api/v1/wechat/batch-import": {
                "description": "批量导入多个聊天记录文件",
                "parameters": {
                    "files": "多个文件列表（最多10个）"
                },
                "response": "所有导入的对话信息"
            },
            "GET /api/v1/wechat/conversations": {
                "description": "获取已导入的对话列表",
                "response": "对话列表信息"
            },
            "GET /api/v1/wechat/conversations/{id}": {
                "description": "获取指定对话的详细信息",
                "parameters": {
                    "id": "对话ID"
                },
                "response": "对话详情和所有消息"
            },
            "POST /api/v1/wechat/analyze/{id}": {
                "description": "分析指定的微信对话",
                "parameters": {
                    "id": "对话ID"
                },
                "response": "分析结果和洞察"
            },
            "DELETE /api/v1/wechat/conversations/{id}": {
                "description": "删除指定的对话",
                "parameters": {
                    "id": "对话ID"
                },
                "response": "删除确认"
            }
        },
        "supported_formats": {
            "txt": "文本格式的聊天记录，支持多种时间格式",
            "json": "JSON格式的结构化聊天记录数据",
            "csv": "CSV格式的表格聊天记录数据"
        },
        "features": [
            "自动格式检测",
            "批量文件处理",
            "系统消息过滤",
            "时间戳解析",
            "用户名标准化",
            "消息类型识别",
            "实时分析"
        ]
    }