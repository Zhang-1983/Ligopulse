"""
微信聊天记录提取API控制器
提供从图片、文本等多种方式提取微信聊天记录的功能
"""

from fastapi import APIRouter, HTTPException, File, UploadFile, BackgroundTasks, Form, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
import tempfile
import os
import sys
from pathlib import Path
import uuid
import json
from datetime import datetime
import hashlib

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent.parent))

# 导入微信聊天记录提取器
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from utils.wechat_extractor import WeChatExtractor, WeChatExportExtractor, BaiduOCRClient, ExtractedMessage, ExtractionResult


# API路由器
router = APIRouter(prefix="/api/v1", tags=["wechat-extractor"])


# 请求模型
class TextExtractionRequest(BaseModel):
    """文本提取请求"""
    text_content: str = Field(..., description="文本内容")
    output_format: str = Field(default="json", description="输出格式: json, txt, csv")


class BatchExtractionRequest(BaseModel):
    """批量提取请求"""
    file_paths: List[str] = Field(..., description="文件路径列表")
    output_format: str = Field(default="json", description="输出格式")
    output_directory: str = Field(default="extracted_chats", description="输出目录")


class OCRConfigRequest(BaseModel):
    """OCR配置请求"""
    api_key: str = Field(..., description="百度OCR API Key")
    secret_key: str = Field(..., description="百度OCR Secret Key")


# 响应模型
class ExtractionResponse(BaseModel):
    """提取响应"""
    success: bool
    method: str
    total_messages: int
    participants: List[str]
    messages: List[Dict[str, Any]]
    output_file: Optional[str] = None
    error_message: Optional[str] = None
    processing_time: float


class BatchExtractionResponse(BaseModel):
    """批量提取响应"""
    success: bool
    total_files: int
    successful_extractions: int
    failed_extractions: int
    results: Dict[str, bool]
    output_files: List[str]
    error_summary: List[str]


# 全局变量存储OCR配置
_ocr_config = {
    "api_key": None,
    "secret_key": None,
    "configured": False
}


@router.post("/wechat-extractor/ocr-config", response_model=Dict[str, Any])
async def configure_ocr(request: OCRConfigRequest):
    """
    配置百度OCR API
    """
    try:
        # 验证API配置
        test_extractor = WeChatExtractor(
            baidu_ocr_key=request.api_key,
            baidu_ocr_secret=request.secret_key
        )
        
        # 这里可以添加简单的连接测试
        # 简化实现，直接配置成功
        global _ocr_config
        _ocr_config = {
            "api_key": request.api_key,
            "secret_key": request.secret_key,
            "configured": True
        }
        
        return {
            "success": True,
            "message": "OCR配置成功",
            "configured_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OCR配置失败: {str(e)}")


@router.post("/wechat-extractor/extract/image", response_model=ExtractionResponse)
async def extract_from_image(
    file: UploadFile = File(...),
    output_format: str = Form("json")
):
    """
    从图片中提取微信聊天记录
    """
    start_time = datetime.now()
    
    try:
        # 验证文件类型
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.bmp'}
        file_extension = Path(file.filename).suffix.lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的图片格式。支持的格式: {', '.join(allowed_extensions)}"
            )
        
        # 检查OCR配置
        if not _ocr_config["configured"]:
            raise HTTPException(
                status_code=400,
                detail="请先配置百度OCR API"
            )
        
        # 保存上传的图片
        temp_dir = Path(tempfile.gettempdir()) / "wechat_extractor"
        temp_dir.mkdir(exist_ok=True)
        
        temp_file_path = temp_dir / f"{uuid.uuid4()}{file_extension}"
        
        with open(temp_file_path, 'wb') as buffer:
            content = await file.read()
            buffer.write(content)
        
        # 提取聊天记录
        extractor = WeChatExtractor(
            baidu_ocr_key=_ocr_config["api_key"],
            baidu_ocr_secret=_ocr_config["secret_key"]
        )
        
        extraction_result = extractor.extract_from_image(str(temp_file_path))
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        if extraction_result.success:
            # 导出到指定格式
            output_dir = Path("extracted_chats")
            output_dir.mkdir(exist_ok=True)
            
            output_filename = f"extracted_{uuid.uuid4().hex[:8]}.{output_format}"
            output_path = output_dir / output_filename
            
            export_success = extractor.export_to_format(
                extraction_result, 
                str(output_path), 
                output_format
            )
            
            response = ExtractionResponse(
                success=True,
                method=extraction_result.extraction_method,
                total_messages=extraction_result.total_messages,
                participants=extraction_result.participants,
                messages=[
                    {
                        "timestamp": msg.timestamp,
                        "sender": msg.sender,
                        "content": msg.content,
                        "type": msg.message_type
                    }
                    for msg in extraction_result.messages
                ],
                output_file=str(output_path) if export_success else None,
                processing_time=processing_time
            )
        else:
            response = ExtractionResponse(
                success=False,
                method=extraction_result.extraction_method,
                total_messages=0,
                participants=[],
                messages=[],
                error_message=extraction_result.error_message,
                processing_time=processing_time
            )
        
        # 清理临时文件
        background_tasks.add_task(cleanup_temp_file, str(temp_file_path))
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"图片提取失败: {str(e)}")


@router.post("/wechat-extractor/extract/text", response_model=ExtractionResponse)
async def extract_from_text(request: TextExtractionRequest):
    """
    从文本中提取微信聊天记录
    """
    start_time = datetime.now()
    
    try:
        extractor = WeChatExtractor()
        extraction_result = extractor.extract_from_text(request.text_content)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        if extraction_result.success:
            # 导出到指定格式
            output_dir = Path("extracted_chats")
            output_dir.mkdir(exist_ok=True)
            
            output_filename = f"text_extracted_{uuid.uuid4().hex[:8]}.{request.output_format}"
            output_path = output_dir / output_filename
            
            export_success = extractor.export_to_format(
                extraction_result, 
                str(output_path), 
                request.output_format
            )
            
            return ExtractionResponse(
                success=True,
                method=extraction_result.extraction_method,
                total_messages=extraction_result.total_messages,
                participants=extraction_result.participants,
                messages=[
                    {
                        "timestamp": msg.timestamp,
                        "sender": msg.sender,
                        "content": msg.content,
                        "type": msg.message_type
                    }
                    for msg in extraction_result.messages
                ],
                output_file=str(output_path) if export_success else None,
                processing_time=processing_time
            )
        else:
            return ExtractionResponse(
                success=False,
                method=extraction_result.extraction_method,
                total_messages=0,
                participants=[],
                messages=[],
                error_message=extraction_result.error_message,
                processing_time=processing_time
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文本提取失败: {str(e)}")


@router.post("/wechat-extractor/extract/file", response_model=ExtractionResponse)
async def extract_from_file(
    file: UploadFile = File(...),
    output_format: str = Form("json")
):
    """
    从文件中提取微信聊天记录
    """
    start_time = datetime.now()
    
    try:
        # 保存上传的文件
        temp_dir = Path(tempfile.gettempdir()) / "wechat_extractor"
        temp_dir.mkdir(exist_ok=True)
        
        temp_file_path = temp_dir / f"{uuid.uuid4()}{Path(file.filename).suffix}"
        
        with open(temp_file_path, 'wb') as buffer:
            content = await file.read()
            buffer.write(content)
        
        # 检查文件类型并选择合适的提取器
        file_extension = Path(file.filename).suffix.lower()
        
        if file_extension in {'.jpg', '.jpeg', '.png', '.bmp', '.txt', '.log'}:
            # 使用普通提取器
            if file_extension in {'.jpg', '.jpeg', '.png', '.bmp'}:
                # 需要OCR配置
                if not _ocr_config["configured"]:
                    raise HTTPException(
                        status_code=400,
                        detail="图片文件需要配置百度OCR API"
                    )
                
                extractor = WeChatExtractor(
                    baidu_ocr_key=_ocr_config["api_key"],
                    baidu_ocr_secret=_ocr_config["secret_key"]
                )
            else:
                extractor = WeChatExtractor()
            
            extraction_result = extractor.extract_from_file(str(temp_file_path))
        
        elif file_extension in {'.txt', '.csv', '.json'}:
            # 使用微信导出文件提取器
            export_extractor = WeChatExportExtractor()
            extraction_result = export_extractor.extract_export_file(str(temp_file_path))
        
        else:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件格式: {file_extension}"
            )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        if extraction_result.success:
            # 导出到指定格式
            output_dir = Path("extracted_chats")
            output_dir.mkdir(exist_ok=True)
            
            output_filename = f"file_extracted_{uuid.uuid4().hex[:8]}.{output_format}"
            output_path = output_dir / output_filename
            
            export_success = extractor.export_to_format(
                extraction_result, 
                str(output_path), 
                output_format
            )
            
            return ExtractionResponse(
                success=True,
                method=extraction_result.extraction_method,
                total_messages=extraction_result.total_messages,
                participants=extraction_result.participants,
                messages=[
                    {
                        "timestamp": msg.timestamp,
                        "sender": msg.sender,
                        "content": msg.content,
                        "type": msg.message_type
                    }
                    for msg in extraction_result.messages
                ],
                output_file=str(output_path) if export_success else None,
                processing_time=processing_time
            )
        else:
            return ExtractionResponse(
                success=False,
                method=extraction_result.extraction_method,
                total_messages=0,
                participants=[],
                messages=[],
                error_message=extraction_result.error_message,
                processing_time=processing_time
            )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件提取失败: {str(e)}")
    
    finally:
        # 清理临时文件
        if 'temp_file_path' in locals() and temp_file_path.exists():
            temp_file_path.unlink()


@router.post("/wechat-extractor/extract/batch", response_model=BatchExtractionResponse)
async def batch_extract_files(request: BatchExtractionRequest):
    """
    批量提取微信聊天记录
    """
    try:
        output_dir = Path(request.output_directory)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = {}
        output_files = []
        error_summary = []
        
        for file_path in request.file_paths:
            try:
                file_path = Path(file_path)
                
                if not file_path.exists():
                    results[str(file_path)] = False
                    error_summary.append(f"文件不存在: {file_path}")
                    continue
                
                # 选择合适的提取器
                file_extension = file_path.suffix.lower()
                
                if file_extension in {'.jpg', '.jpeg', '.png', '.bmp'}:
                    if not _ocr_config["configured"]:
                        results[str(file_path)] = False
                        error_summary.append(f"图片文件需要OCR配置: {file_path}")
                        continue
                    
                    extractor = WeChatExtractor(
                        baidu_ocr_key=_ocr_config["api_key"],
                        baidu_ocr_secret=_ocr_config["secret_key"]
                    )
                    extraction_result = extractor.extract_from_image(str(file_path))
                
                elif file_extension in {'.txt', '.csv', '.json'}:
                    export_extractor = WeChatExportExtractor()
                    extraction_result = export_extractor.extract_export_file(str(file_path))
                
                else:
                    results[str(file_path)] = False
                    error_summary.append(f"不支持的文件格式: {file_path}")
                    continue
                
                if extraction_result.success:
                    # 生成输出文件名
                    file_hash = hashlib.md5(str(file_path).encode()).hexdigest()[:8]
                    output_filename = f"batch_extracted_{file_hash}.{request.output_format}"
                    output_path = output_dir / output_filename
                    
                    if file_extension in {'.jpg', '.jpeg', '.png', '.bmp'}:
                        success = extractor.export_to_format(
                            extraction_result, 
                            str(output_path), 
                            request.output_format
                        )
                    else:
                        success = extractor.export_to_format(
                            extraction_result, 
                            str(output_path), 
                            request.output_format
                        )
                    
                    results[str(file_path)] = success
                    
                    if success:
                        output_files.append(str(output_path))
                    
                else:
                    results[str(file_path)] = False
                    error_summary.append(f"提取失败: {file_path} - {extraction_result.error_message}")
                    
            except Exception as e:
                results[str(file_path)] = False
                error_summary.append(f"处理错误: {file_path} - {e}")
        
        successful_count = sum(1 for success in results.values() if success)
        failed_count = len(results) - successful_count
        
        return BatchExtractionResponse(
            success=failed_count == 0,
            total_files=len(request.file_paths),
            successful_extractions=successful_count,
            failed_extractions=failed_count,
            results=results,
            output_files=output_files,
            error_summary=error_summary
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量提取失败: {str(e)}")


@router.get("/wechat-extractor/status", response_model=Dict[str, Any])
async def get_extractor_status():
    """
    获取提取器状态
    """
    return {
        "ocr_configured": _ocr_config["configured"],
        "ocr_key_status": "configured" if _ocr_config["configured"] else "not_configured",
        "supported_formats": {
            "image": [".jpg", ".jpeg", ".png", ".bmp"],
            "text": [".txt", ".log"],
            "export": [".txt", ".csv", ".json"]
        },
        "extraction_methods": [
            "image_ocr",
            "text_parse",
            "file_parse",
            "wechat_txt_export",
            "wechat_csv_export",
            "wechat_json_export"
        ],
        "output_formats": ["json", "txt", "csv"],
        "timestamp": datetime.now().isoformat()
    }


@router.get("/wechat-extractor/formats", response_model=Dict[str, Any])
async def get_supported_formats():
    """
    获取支持的格式信息
    """
    return {
        "input_formats": {
            "image_ocr": {
                "description": "通过OCR识别图片中的微信聊天记录",
                "extensions": [".jpg", ".jpeg", ".png", ".bmp"],
                "requirements": "需要配置百度OCR API",
                "example": "微信聊天截图"
            },
            "text_parse": {
                "description": "解析文本格式的聊天记录",
                "extensions": [".txt", ".log"],
                "requirements": "无需额外配置",
                "example": "复制粘贴的聊天记录文本"
            },
            "wechat_export": {
                "description": "解析微信导出的聊天记录文件",
                "extensions": [".txt", ".csv", ".json"],
                "requirements": "微信导出的标准格式",
                "example": "微信PC版导出的聊天记录"
            }
        },
        "output_formats": {
            "json": {
                "description": "结构化的JSON格式",
                "use_case": "程序处理、API调用"
            },
            "txt": {
                "description": "可读的文本格式",
                "use_case": "人工查看、简单分析"
            },
            "csv": {
                "description": "逗号分隔的表格格式",
                "use_case": "Excel导入、数据分析"
            }
        },
        "limitations": {
            "max_file_size": "50MB",
            "max_image_size": "10MB",
            "max_text_length": 1000000,
            "supported_encodings": ["UTF-8", "GBK", "GB2312"]
        },
        "timestamp": datetime.now().isoformat()
    }


# 辅助函数
def cleanup_temp_file(file_path: str):
    """清理临时文件"""
    try:
        file_path = Path(file_path)
        if file_path.exists():
            file_path.unlink()
    except Exception as e:
        print(f"清理临时文件失败: {e}")