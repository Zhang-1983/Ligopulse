"""
PaddleOCR MCP服务器集成客户端
支持OCR文本识别和PP-StructureV3文档解析功能
"""
import asyncio
import json
import base64
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import httpx


class PaddleOCRProvider:
    """PaddleOCR MCP服务器提供商"""
    
    def __init__(self, 
                 access_token: str,
                 paddle_url: str = "http://j8r5t1c993t4tfy2.sandbox-aistudio-hub.baidu.com/ocr",
                 structure_url: str = "http://oceaxdm1h3v1v1pb.sandbox-aistudio-hub.baidu.com/layout-parsing",
                 use_mcp_server: bool = True):
        """
        初始化PaddleOCR客户端
        
        Args:
            access_token: 百度AI Studio访问令牌
            paddle_url: OCR服务URL
            structure_url: PP-StructureV3服务URL
            use_mcp_server: 是否使用MCP服务器
        """
        self.access_token = access_token
        self.paddle_url = paddle_url
        self.structure_url = structure_url
        self.use_mcp_server = use_mcp_server
        
        # MCP服务器配置（用于Claude Desktop集成）
        self.mcp_config = {
            "paddleocr-ocr": {
                "command": "uvx",
                "args": [
                    "--from", 
                    "paddleocr-mcp@https://paddle-model-ecology.bj.bcebos.com/paddlex/PaddleX3.0/mcp/paddleocr_mcp/releases/v0.2.0/paddleocr_mcp-0.2.0-py3-none-any.whl",
                    "paddleocr_mcp"
                ],
                "env": {
                    "PADDLEOCR_MCP_PIPELINE": "OCR",
                    "PADDLEOCR_MCP_PPOCR_SOURCE": "aistudio",
                    "PADDLEOCR_MCP_SERVER_URL": paddle_url,
                    "PADDLEOCR_MCP_AISTUDIO_ACCESS_TOKEN": access_token
                }
            },
            "paddleocr-structure": {
                "command": "uvx",
                "args": [
                    "--from",
                    "paddleocr-mcp@https://paddle-model-ecology.bj.bcebos.com/paddlex/PaddleX3.0/mcp/paddleocr_mcp/releases/v0.2.0/paddleocr_mcp-0.2.0-py3-none-any.whl",
                    "paddleocr_mcp"
                ],
                "env": {
                    "PADDLEOCR_MCP_PIPELINE": "PP-StructureV3",
                    "PADDLEOCR_MCP_PPOCR_SOURCE": "aistudio",
                    "PADDLEOCR_MCP_SERVER_URL": structure_url,
                    "PADDLEOCR_MCP_AISTUDIO_ACCESS_TOKEN": access_token
                }
            }
        }
    
    def generate_mcp_config(self) -> Dict[str, Any]:
        """生成Claude Desktop MCP配置文件"""
        return self.mcp_config
    
    async def ocr_recognition(self, image_path: str, language: str = "chs") -> Dict[str, Any]:
        """
        OCR文本识别
        
        Args:
            image_path: 图像文件路径
            language: 语言类型（chs, en, chs_eng等）
            
        Returns:
            识别结果
        """
        try:
            print(f"🔍 PaddleOCR识别图像: {image_path}")
            
            # 读取图像文件并转为base64
            with open(image_path, 'rb') as f:
                image_data = f.read()
                base64_image = base64.b64encode(image_data).decode()
            
            # 准备请求数据
            request_data = {
                "image": base64_image,
                "language_type": language
            }
            
            # 发送请求到PaddleOCR API
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.access_token}"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.paddle_url,
                    headers=headers,
                    json=request_data,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "success": True,
                        "text": result.get("text", ""),
                        "confidence": result.get("confidence", 0.0),
                        "detected_texts": result.get("detected_texts", []),
                        "language_detected": result.get("language", language),
                        "method": "paddleocr_ocr"
                    }
                else:
                    error_msg = f"API请求失败: {response.status_code} - {response.text}"
                    print(f"❌ {error_msg}")
                    return {"success": False, "error": error_msg}
                    
        except Exception as e:
            error_msg = f"OCR识别失败: {str(e)}"
            print(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}
    
    async def document_structure_analysis(self, image_path: str) -> Dict[str, Any]:
        """
        PP-StructureV3文档结构分析
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            结构化分析结果
        """
        try:
            print(f"📄 PaddleOCR文档分析: {image_path}")
            
            # 读取图像文件并转为base64
            with open(image_path, 'rb') as f:
                image_data = f.read()
                base64_image = base64.b64encode(image_data).decode()
            
            # 准备请求数据
            request_data = {
                "image": base64_image,
                "output_format": "markdown"  # 或 "json"
            }
            
            # 发送请求到PP-StructureV3 API
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.access_token}"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.structure_url,
                    headers=headers,
                    json=request_data,
                    timeout=60.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "success": True,
                        "markdown_content": result.get("markdown", ""),
                        "json_structure": result.get("structure", {}),
                        "pages": result.get("pages", []),
                        "elements": result.get("elements", []),
                        "method": "paddleocr_structure"
                    }
                else:
                    error_msg = f"文档分析失败: {response.status_code} - {response.text}"
                    print(f"❌ {error_msg}")
                    return {"success": False, "error": error_msg}
                    
        except Exception as e:
            error_msg = f"文档结构分析失败: {str(e)}"
            print(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}
    
    async def analyze_wechat_image(self, image_path: str) -> Dict[str, Any]:
        """
        专门针对微信聊天记录图片的分析
        
        Args:
            image_path: 微信聊天记录图像文件路径
            
        Returns:
            分析结果
        """
        print(f"💬 分析微信聊天记录: {image_path}")
        
        # 并行执行OCR和文档结构分析
        ocr_task = asyncio.create_task(self.ocr_recognition(image_path))
        structure_task = asyncio.create_task(self.document_structure_analysis(image_path))
        
        try:
            ocr_result, structure_result = await asyncio.gather(ocr_task, structure_task)
            
            # 合并结果
            combined_result = {
                "success": True,
                "image_path": image_path,
                "analysis_timestamp": datetime.now().isoformat(),
                "ocr_result": ocr_result,
                "structure_result": structure_result,
                "summary": {
                    "text_extracted": ocr_result.get("success", False),
                    "structure_analyzed": structure_result.get("success", False),
                    "total_confidence": (ocr_result.get("confidence", 0.0) + 
                                       structure_result.get("confidence", 0.0)) / 2
                }
            }
            
            print(f"✅ 微信图片分析完成 - 置信度: {combined_result['summary']['total_confidence']:.3f}")
            return combined_result
            
        except Exception as e:
            error_msg = f"微信图片分析失败: {str(e)}"
            print(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}


# 全局PaddleOCR客户端实例
_paddleocr_client: Optional[PaddleOCRProvider] = None


async def get_paddleocr_client(access_token: str = None) -> PaddleOCRProvider:
    """获取PaddleOCR客户端实例"""
    global _paddleocr_client
    
    if _paddleocr_client is None:
        if not access_token:
            # 从环境变量获取访问令牌
            from dotenv import load_dotenv
            import os
            
            load_dotenv()
            access_token = os.getenv("PADDLEOCR_ACCESS_TOKEN", "06e462ca9e7d5ad023db6205b7e4ecdd3f06ec2a")
        
        _paddleocr_client = PaddleOCRProvider(
            access_token=access_token
        )
    
    return _paddleocr_client


async def close_paddleocr_client():
    """关闭PaddleOCR客户端"""
    global _paddleocr_client
    _paddleocr_client = None


# 测试函数
async def test_paddleocr_integration():
    """测试PaddleOCR集成"""
    print("🚀 开始测试PaddleOCR集成...")
    
    try:
        client = await get_paddleocr_client()
        
        # 生成MCP配置
        mcp_config = client.generate_mcp_config()
        print("📋 MCP配置生成成功")
        print(json.dumps(mcp_config, indent=2, ensure_ascii=False))
        
        # 这里可以添加图像测试（需要实际图像文件）
        print("✅ PaddleOCR客户端初始化成功")
        
        return True
        
    except Exception as e:
        print(f"❌ PaddleOCR测试失败: {e}")
        return False


if __name__ == "__main__":
    asyncio.run(test_paddleocr_integration())