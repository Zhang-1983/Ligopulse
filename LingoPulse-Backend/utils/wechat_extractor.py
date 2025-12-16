"""
微信聊天记录提取器
支持从微信聊天截图、导出的文件等多种方式提取聊天记录
集成百度OCR API进行文字识别
"""

import os
import re
import json
import csv
import base64
import requests
from datetime import datetime
from typing import List, Dict, Optional, Union, Any
from pathlib import Path
import hashlib
import time
from dataclasses import dataclass

try:
    from PIL import Image
except ImportError:
    Image = None

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from infrastructure.data_importers.wechat_importer import WeChatChatImporter


@dataclass
class ExtractedMessage:
    """提取的消息数据结构"""
    timestamp: str
    sender: str
    content: str
    message_type: str = "text"
    raw_data: Optional[Dict] = None


@dataclass
class ExtractionResult:
    """提取结果"""
    success: bool
    messages: List[ExtractedMessage]
    total_messages: int
    participants: List[str]
    extraction_method: str
    error_message: Optional[str] = None


class BaiduOCRClient:
    """百度OCR API客户端"""
    
    def __init__(self, api_key: str, secret_key: str):
        """
        初始化百度OCR客户端
        
        Args:
            api_key: 百度OCR API Key
            secret_key: 百度OCR Secret Key
        """
        self.api_key = api_key
        self.secret_key = secret_key
        self.access_token = None
        self.token_expires = 0
        self.base_url = "https://aip.baidubce.com"
        
    def get_access_token(self) -> str:
        """获取访问令牌"""
        if self.access_token and time.time() < self.token_expires:
            return self.access_token
            
        url = f"{self.base_url}/oauth/2.0/token"
        params = {
            'grant_type': 'client_credentials',
            'client_id': self.api_key,
            'client_secret': self.secret_key
        }
        
        response = requests.post(url, params=params)
        data = response.json()
        
        if 'access_token' in data:
            self.access_token = data['access_token']
            self.token_expires = time.time() + data.get('expires_in', 3600) - 60  # 提前60秒刷新
            return self.access_token
        else:
            raise Exception(f"获取访问令牌失败: {data}")
    
    def recognize_text(self, image_path: str, language_type: str = "CHN_ENG") -> Dict[str, Any]:
        """
        识别图片中的文字
        
        Args:
            image_path: 图片路径
            language_type: 语言类型，默认为中英文混合
            
        Returns:
            识别结果字典
        """
        if not Image:
            raise Exception("需要安装Pillow库: pip install Pillow")
            
        # 读取图片并转为base64
        with open(image_path, 'rb') as f:
            image_data = f.read()
            base64_image = base64.b64encode(image_data).decode()
        
        # 获取访问令牌
        access_token = self.get_access_token()
        
        # 调用OCR API
        url = f"{self.base_url}/rest/2.0/ocr/v1/general_basic"
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {
            'access_token': access_token,
            'image': base64_image,
            'language_type': language_type
        }
        
        response = requests.post(url, headers=headers, data=data)
        result = response.json()
        
        if 'words_result' in result:
            # 提取文字内容
            text_lines = [item['words'] for item in result['words_result']]
            return {
                'success': True,
                'text': '\n'.join(text_lines),
                'lines': text_lines,
                'confidence': result.get('confidence', 0.0)
            }
        else:
            return {
                'success': False,
                'error': result.get('error_msg', '未知错误'),
                'full_response': result
            }


class WeChatExtractor:
    """微信聊天记录提取器"""
    
    def __init__(self, baidu_ocr_key: str = None, baidu_ocr_secret: str = None):
        """
        初始化提取器
        
        Args:
            baidu_ocr_key: 百度OCR API Key
            baidu_ocr_secret: 百度OCR Secret Key
        """
        self.baidu_ocr = None
        if baidu_ocr_key and baidu_ocr_secret:
            self.baidu_ocr = BaiduOCRClient(baidu_ocr_key, baidu_ocr_secret)
        
        # 微信聊天记录正则表达式模式
        self.time_patterns = [
            # 2024-01-01 12:00:00
            r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})',
            # 2024/1/1 12:00
            r'(\d{4}[/-]\d{1,2}[/-]\d{1,2}\s+\d{1,2}:\d{2})',
            # 1月1日 12:00
            r'(\d{1,2}月\d{1,2}日\s+\d{1,2}:\d{2})',
            # 12:00
            r'(\d{1,2}:\d{2})'
        ]
        
        self.sender_patterns = [
            # 张三:
            r'^([^:]+):\s*(.+)$',
            # 张三 says:
            r'^([^says]+)\s+[says]+:\s*(.+)$',
            # [张三]
            r'^\[([^\]]+)\]\s*(.+)$'
        ]
        
        self.importer = WeChatChatImporter()
    
    def extract_from_image(self, image_path: str) -> ExtractionResult:
        """
        从图片中提取聊天记录
        
        Args:
            image_path: 图片路径
            
        Returns:
            提取结果
        """
        if not self.baidu_ocr:
            return ExtractionResult(
                success=False,
                messages=[],
                total_messages=0,
                participants=[],
                extraction_method="image_ocr",
                error_message="未配置百度OCR API，请设置api_key和secret_key"
            )
        
        try:
            # 使用OCR识别文字
            ocr_result = self.baidu_ocr.recognize_text(image_path)
            
            if not ocr_result['success']:
                return ExtractionResult(
                    success=False,
                    messages=[],
                    total_messages=0,
                    participants=[],
                    extraction_method="image_ocr",
                    error_message=ocr_result['error']
                )
            
            # 从识别的文本中提取聊天记录
            text = ocr_result['text']
            messages = self._parse_text_messages(text)
            
            participants = list(set(msg.sender for msg in messages if msg.sender))
            
            return ExtractionResult(
                success=True,
                messages=messages,
                total_messages=len(messages),
                participants=participants,
                extraction_method="image_ocr"
            )
            
        except Exception as e:
            return ExtractionResult(
                success=False,
                messages=[],
                total_messages=0,
                participants=[],
                extraction_method="image_ocr",
                error_message=str(e)
            )
    
    def extract_from_text(self, text_content: str) -> ExtractionResult:
        """
        从文本内容中提取聊天记录
        
        Args:
            text_content: 文本内容
            
        Returns:
            提取结果
        """
        try:
            messages = self._parse_text_messages(text_content)
            participants = list(set(msg.sender for msg in messages if msg.sender))
            
            return ExtractionResult(
                success=True,
                messages=messages,
                total_messages=len(messages),
                participants=participants,
                extraction_method="text_parse"
            )
            
        except Exception as e:
            return ExtractionResult(
                success=False,
                messages=[],
                total_messages=0,
                participants=[],
                extraction_method="text_parse",
                error_message=str(e)
            )
    
    def extract_from_file(self, file_path: str) -> ExtractionResult:
        """
        从文件中提取聊天记录
        
        Args:
            file_path: 文件路径
            
        Returns:
            提取结果
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            return ExtractionResult(
                success=False,
                messages=[],
                total_messages=0,
                participants=[],
                extraction_method="file_parse",
                error_message="文件不存在"
            )
        
        # 支持图片格式
        if file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp']:
            return self.extract_from_image(str(file_path))
        
        # 支持文本格式
        elif file_path.suffix.lower() in ['.txt', '.log']:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return self.extract_from_text(content)
            except UnicodeDecodeError:
                # 尝试其他编码
                for encoding in ['gbk', 'gb2312', 'utf-8']:
                    try:
                        with open(file_path, 'r', encoding=encoding) as f:
                            content = f.read()
                        return self.extract_from_text(content)
                    except UnicodeDecodeError:
                        continue
                
                return ExtractionResult(
                    success=False,
                    messages=[],
                    total_messages=0,
                    participants=[],
                    extraction_method="file_parse",
                    error_message="无法解码文件，请检查文件编码"
                )
        
        else:
            return ExtractionResult(
                success=False,
                messages=[],
                total_messages=0,
                participants=[],
                extraction_method="file_parse",
                error_message=f"不支持的文件格式: {file_path.suffix}"
            )
    
    def _parse_text_messages(self, text: str) -> List[ExtractedMessage]:
        """
        解析文本消息
        
        Args:
            text: 文本内容
            
        Returns:
            消息列表
        """
        messages = []
        lines = text.split('\n')
        current_sender = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 尝试解析时间和发送者
            parsed = self._parse_message_line(line)
            
            if parsed:
                # 保存上一条消息
                if current_content:
                    messages.append(ExtractedMessage(
                        timestamp=datetime.now().isoformat(),
                        sender=current_sender or "未知",
                        content=' '.join(current_content).strip(),
                        message_type="text"
                    ))
                    current_content = []
                
                current_sender = parsed['sender']
                current_content.append(parsed['content'])
            else:
                # 可能是上一条消息的延续
                if current_sender:
                    current_content.append(line)
                else:
                    # 尝试设置为默认发送者
                    current_sender = "系统"
                    current_content.append(line)
        
        # 添加最后一条消息
        if current_content:
            messages.append(ExtractedMessage(
                timestamp=datetime.now().isoformat(),
                sender=current_sender or "未知",
                content=' '.join(current_content).strip(),
                message_type="text"
            ))
        
        return messages
    
    def _parse_message_line(self, line: str) -> Optional[Dict[str, str]]:
        """
        解析单条消息行
        
        Args:
            line: 消息行
            
        Returns:
            解析结果，失败返回None
        """
        # 尝试发送者模式
        for pattern in self.sender_patterns:
            match = re.match(pattern, line)
            if match:
                sender = match.group(1).strip()
                content = match.group(2).strip()
                
                # 清理发送者名称
                if sender.endswith(':'):
                    sender = sender[:-1]
                if sender.startswith('[') and sender.endswith(']'):
                    sender = sender[1:-1]
                
                return {
                    'sender': sender,
                    'content': content
                }
        
        return None
    
    def export_to_format(self, extraction_result: ExtractionResult, 
                        output_path: str, format_type: str = "json") -> bool:
        """
        导出提取结果到指定格式
        
        Args:
            extraction_result: 提取结果
            output_path: 输出文件路径
            format_type: 输出格式 (json, txt, csv)
            
        Returns:
            是否成功
        """
        if not extraction_result.success:
            return False
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if format_type.lower() == "json":
            return self._export_to_json(extraction_result, str(output_path))
        elif format_type.lower() == "txt":
            return self._export_to_txt(extraction_result, str(output_path))
        elif format_type.lower() == "csv":
            return self._export_to_csv(extraction_result, str(output_path))
        else:
            raise ValueError(f"不支持的格式: {format_type}")
    
    def _export_to_json(self, extraction_result: ExtractionResult, output_path: str) -> bool:
        """导出为JSON格式"""
        try:
            data = {
                "extraction_info": {
                    "method": extraction_result.extraction_method,
                    "timestamp": datetime.now().isoformat(),
                    "total_messages": extraction_result.total_messages,
                    "participants": extraction_result.participants
                },
                "messages": [
                    {
                        "timestamp": msg.timestamp,
                        "sender": msg.sender,
                        "content": msg.content,
                        "type": msg.message_type
                    }
                    for msg in extraction_result.messages
                ]
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            print(f"导出JSON失败: {e}")
            return False
    
    def _export_to_txt(self, extraction_result: ExtractionResult, output_path: str) -> bool:
        """导出为TXT格式"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"微信聊天记录导出\n")
                f.write(f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"提取方法: {extraction_result.extraction_method}\n")
                f.write(f"参与者: {', '.join(extraction_result.participants)}\n")
                f.write(f"总消息数: {extraction_result.total_messages}\n")
                f.write("-" * 50 + "\n\n")
                
                for msg in extraction_result.messages:
                    timestamp = msg.timestamp.split('T')[0] + ' ' + msg.timestamp.split('T')[1][:8]
                    f.write(f"{timestamp} {msg.sender}: {msg.content}\n")
            
            return True
            
        except Exception as e:
            print(f"导出TXT失败: {e}")
            return False
    
    def _export_to_csv(self, extraction_result: ExtractionResult, output_path: str) -> bool:
        """导出为CSV格式"""
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'sender', 'content', 'type'])
                
                for msg in extraction_result.messages:
                    writer.writerow([
                        msg.timestamp,
                        msg.sender,
                        msg.content,
                        msg.message_type
                    ])
            
            return True
            
        except Exception as e:
            print(f"导出CSV失败: {e}")
            return False
    
    def batch_extract(self, file_paths: List[str], output_dir: str, 
                     format_type: str = "json") -> Dict[str, bool]:
        """
        批量提取聊天记录
        
        Args:
            file_paths: 文件路径列表
            output_dir: 输出目录
            format_type: 输出格式
            
        Returns:
            提取结果字典 {file_path: success}
        """
        results = {}
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for file_path in file_paths:
            try:
                # 提取聊天记录
                extraction_result = self.extract_from_file(file_path)
                
                if extraction_result.success:
                    # 生成输出文件名
                    file_hash = hashlib.md5(file_path.encode()).hexdigest()[:8]
                    output_filename = f"wechat_export_{file_hash}.{format_type}"
                    output_path = output_dir / output_filename
                    
                    # 导出结果
                    success = self.export_to_format(extraction_result, str(output_path), format_type)
                    results[file_path] = success
                    
                    if success:
                        print(f"✅ 成功提取: {file_path} -> {output_path}")
                    else:
                        print(f"❌ 导出失败: {file_path}")
                else:
                    results[file_path] = False
                    print(f"❌ 提取失败: {file_path} - {extraction_result.error_message}")
                    
            except Exception as e:
                results[file_path] = False
                print(f"❌ 处理错误: {file_path} - {e}")
        
        return results


class WeChatExportExtractor:
    """微信导出文件提取器"""
    
    def __init__(self):
        self.supported_formats = {
            '.txt': self._parse_txt_export,
            '.csv': self._parse_csv_export,
            '.json': self._parse_json_export
        }
    
    def extract_export_file(self, file_path: str) -> ExtractionResult:
        """
        提取微信导出的聊天记录文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            提取结果
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            return ExtractionResult(
                success=False,
                messages=[],
                total_messages=0,
                participants=[],
                extraction_method="wechat_export",
                error_message="文件不存在"
            )
        
        parser = self.supported_formats.get(file_path.suffix.lower())
        if not parser:
            return ExtractionResult(
                success=False,
                messages=[],
                total_messages=0,
                participants=[],
                extraction_method="wechat_export",
                error_message=f"不支持的文件格式: {file_path.suffix}"
            )
        
        try:
            return parser(file_path)
        except Exception as e:
            return ExtractionResult(
                success=False,
                messages=[],
                total_messages=0,
                participants=[],
                extraction_method="wechat_export",
                error_message=str(e)
            )
    
    def _parse_txt_export(self, file_path: Path) -> ExtractionResult:
        """解析TXT格式导出文件"""
        messages = []
        participants = set()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 微信TXT格式通常包含特定模式
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # 尝试解析微信格式
                # 格式: 2024-01-01 12:00:00 张三: 你好
                match = re.match(r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+([^:]+):\s*(.+)', line)
                if match:
                    timestamp, sender, content = match.groups()
                    sender = sender.strip()
                    participants.add(sender)
                    
                    messages.append(ExtractedMessage(
                        timestamp=timestamp,
                        sender=sender,
                        content=content.strip(),
                        message_type="text"
                    ))
            
            return ExtractionResult(
                success=True,
                messages=messages,
                total_messages=len(messages),
                participants=list(participants),
                extraction_method="wechat_txt_export"
            )
            
        except Exception as e:
            return ExtractionResult(
                success=False,
                messages=[],
                total_messages=0,
                participants=[],
                extraction_method="wechat_txt_export",
                error_message=str(e)
            )
    
    def _parse_csv_export(self, file_path: Path) -> ExtractionResult:
        """解析CSV格式导出文件"""
        messages = []
        participants = set()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    sender = row.get('sender', '').strip()
                    content = row.get('content', '').strip()
                    timestamp = row.get('timestamp', datetime.now().isoformat())
                    
                    if sender and content:
                        participants.add(sender)
                        messages.append(ExtractedMessage(
                            timestamp=timestamp,
                            sender=sender,
                            content=content,
                            message_type="text"
                        ))
            
            return ExtractionResult(
                success=True,
                messages=messages,
                total_messages=len(messages),
                participants=list(participants),
                extraction_method="wechat_csv_export"
            )
            
        except Exception as e:
            return ExtractionResult(
                success=False,
                messages=[],
                total_messages=0,
                participants=[],
                extraction_method="wechat_csv_export",
                error_message=str(e)
            )
    
    def _parse_json_export(self, file_path: Path) -> ExtractionResult:
        """解析JSON格式导出文件"""
        messages = []
        participants = set()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 假设JSON结构包含messages数组
            if isinstance(data, dict) and 'messages' in data:
                message_list = data['messages']
            elif isinstance(data, list):
                message_list = data
            else:
                raise ValueError("无效的JSON格式")
            
            for msg_data in message_list:
                if isinstance(msg_data, dict):
                    sender = msg_data.get('sender', '').strip()
                    content = msg_data.get('content', '').strip()
                    timestamp = msg_data.get('timestamp', datetime.now().isoformat())
                    
                    if sender and content:
                        participants.add(sender)
                        messages.append(ExtractedMessage(
                            timestamp=timestamp,
                            sender=sender,
                            content=content,
                            message_type="text"
                        ))
            
            return ExtractionResult(
                success=True,
                messages=messages,
                total_messages=len(messages),
                participants=list(participants),
                extraction_method="wechat_json_export"
            )
            
        except Exception as e:
            return ExtractionResult(
                success=False,
                messages=[],
                total_messages=0,
                participants=[],
                extraction_method="wechat_json_export",
                error_message=str(e)
            )