#!/usr/bin/env python3
"""
微信聊天记录导入器
支持多种微信聊天记录格式的导入和处理
"""

import json
import csv
import re
from datetime import datetime
from typing import List, Dict, Optional, Union
from pathlib import Path

from domain.entities import Conversation, Turn, SpeakerRole, ConversationType


class WeChatChatImporter:
    """微信聊天记录导入器"""
    
    def __init__(self):
        self.supported_formats = ['.txt', '.json', '.csv']
        self.message_patterns = {
            'time': r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})',
            'speaker': r'([^:]+):',
            'content': r':\s*(.+)$'
        }
    
    def import_from_file(self, file_path: Union[str, Path], format_type: str = 'auto') -> List[Conversation]:
        """
        从文件导入微信聊天记录
        
        Args:
            file_path: 文件路径
            format_type: 文件格式类型 ('auto', 'json', 'csv', 'txt')
        
        Returns:
            导入的对话列表
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        if format_type == 'auto':
            format_type = self._detect_format(file_path)
        
        if format_type == 'json':
            return self._import_from_json(file_path)
        elif format_type == 'csv':
            return self._import_from_csv(file_path)
        elif format_type == 'txt':
            return self._import_from_txt(file_path)
        else:
            raise ValueError(f"不支持的格式类型: {format_type}")
    
    def _detect_format(self, file_path: Path) -> str:
        """自动检测文件格式"""
        suffix = file_path.suffix.lower()
        
        if suffix in self.supported_formats:
            if suffix == '.json':
                return 'json'
            elif suffix == '.csv':
                return 'csv'
            elif suffix == '.txt':
                return 'txt'
        
        # 尝试读取文件内容来判断格式
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                
                if content.startswith('[') or content.startswith('{'):
                    return 'json'
                elif ',' in content and '\n' in content:
                    return 'csv'
                else:
                    return 'txt'
        except:
            return 'txt'
    
    def _import_from_json(self, file_path: Path) -> List[Conversation]:
        """从JSON文件导入"""
        conversations = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 处理不同类型的JSON格式
        if isinstance(data, list):
            # 标准格式：消息列表
            messages = data
        elif isinstance(data, dict):
            # 微信导出格式
            if 'messages' in data:
                messages = data['messages']
            elif 'chat' in data:
                messages = data['chat']['messages']
            else:
                messages = [data]
        else:
            raise ValueError("无效的JSON格式")
        
        conversation = self._create_conversation_from_messages(messages)
        conversations.append(conversation)
        
        return conversations
    
    def _import_from_csv(self, file_path: Path) -> List[Conversation]:
        """从CSV文件导入"""
        conversations = []
        messages = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                messages.append(row)
        
        conversation = self._create_conversation_from_messages(messages)
        conversations.append(conversation)
        
        return conversations
    
    def _import_from_txt(self, file_path: Path) -> List[Conversation]:
        """从文本文件导入"""
        conversations = []
        messages = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 按行分割并解析
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            message = self._parse_txt_line(line)
            if message:
                messages.append(message)
        
        conversation = self._create_conversation_from_messages(messages)
        conversations.append(conversation)
        
        return conversations
    
    def _parse_txt_line(self, line: str) -> Optional[Dict]:
        """解析文本行"""
        # 常见的微信格式匹配
        
        # 格式1: 2023-12-01 10:30:25 张三: 你好
        pattern1 = r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+([^:]+):\s*(.+)'
        match1 = re.match(pattern1, line)
        if match1:
            return {
                'timestamp': match1.group(1),
                'sender': match1.group(2),
                'content': match1.group(3),
                'type': 'text'
            }
        
        # 格式2: 张三 10:30:25 你好
        pattern2 = r'([^0-9]+)\s+(\d{2}:\d{2}:\d{2})\s+(.+)'
        match2 = re.match(pattern2, line)
        if match2:
            return {
                'timestamp': match2.group(2),
                'sender': match2.group(1),
                'content': match2.group(3),
                'type': 'text'
            }
        
        return None
    
    def _create_conversation_from_messages(self, messages: List[Dict]) -> Conversation:
        """从消息列表创建对话对象"""
        turns = []
        
        for msg in messages:
            # 提取发送者
            sender = self._extract_sender(msg)
            
            # 提取内容
            content = self._extract_content(msg)
            
            # 提取时间戳
            timestamp = self._extract_timestamp(msg)
            
            # 提取消息类型
            message_type = self._extract_message_type(msg)
            
            # 只处理文本消息
            if message_type == 'text' and content.strip():
                turn = Turn(
                    content=content,
                    speaker_role=SpeakerRole.USER if sender != '我' else SpeakerRole.ASSISTANT,
                    timestamp=timestamp,
                    metadata={
                        'original_sender': sender,
                        'message_type': message_type,
                        'source': 'wechat'
                    }
                )
                turns.append(turn)
        
        # 创建对话
        conversation = Conversation(
            conversation_type=ConversationType.PERSONAL,
            participants=[turn.metadata['original_sender'] for turn in turns],
            turns=turns,
            metadata={
                'source': 'wechat_import',
                'total_messages': len(turns),
                'import_time': datetime.now().isoformat()
            }
        )
        
        return conversation
    
    def _extract_sender(self, message: Dict) -> str:
        """提取发送者"""
        # 尝试不同的字段名
        sender_fields = ['sender', 'from', 'from_user', 'user', 'name', 'nickname']
        
        for field in sender_fields:
            if field in message:
                return str(message[field]).strip()
        
        # 尝试从其他字段推断
        if 'sender_name' in message:
            return str(message['sender_name']).strip()
        
        return '未知用户'
    
    def _extract_content(self, message: Dict) -> str:
        """提取消息内容"""
        # 尝试不同的字段名
        content_fields = ['content', 'text', 'msg', 'message', 'body']
        
        for field in content_fields:
            if field in message:
                content = str(message[field]).strip()
                # 过滤掉系统消息和无效内容
                if self._is_valid_content(content):
                    return content
        
        return ''
    
    def _extract_timestamp(self, message: Dict) -> datetime:
        """提取时间戳"""
        # 尝试不同的字段名
        time_fields = ['timestamp', 'time', 'date', 'created_at']
        
        for field in time_fields:
            if field in message:
                try:
                    if isinstance(message[field], str):
                        return datetime.fromisoformat(message[field].replace('Z', '+00:00'))
                    elif isinstance(message[field], (int, float)):
                        return datetime.fromtimestamp(message[field])
                except:
                    continue
        
        # 尝试解析字符串时间格式
        if 'timestamp' in message:
            try:
                timestamp_str = str(message['timestamp'])
                # 常见时间格式解析
                formats = [
                    '%Y-%m-%d %H:%M:%S',
                    '%Y-%m-%d %H:%M',
                    '%Y/%m/%d %H:%M:%S',
                    '%Y/%m/%d %H:%M'
                ]
                
                for fmt in formats:
                    try:
                        return datetime.strptime(timestamp_str, fmt)
                    except:
                        continue
            except:
                pass
        
        return datetime.now()
    
    def _extract_message_type(self, message: Dict) -> str:
        """提取消息类型"""
        type_fields = ['type', 'msg_type', 'message_type', 'category']
        
        for field in type_fields:
            if field in message:
                msg_type = str(message[field]).lower()
                if msg_type in ['text', 'msg', 'message']:
                    return 'text'
                elif msg_type in ['image', 'img', 'pic']:
                    return 'image'
                elif msg_type in ['voice', 'audio']:
                    return 'voice'
                elif msg_type in ['video']:
                    return 'video'
                else:
                    return 'text'  # 默认为文本
        
        return 'text'  # 默认为文本
    
    def _is_valid_content(self, content: str) -> bool:
        """检查内容是否有效"""
        # 过滤掉系统消息、空消息等
        invalid_patterns = [
            r'^(系统消息|system|通知|提示)',
            r'^[^a-zA-Z0-9\u4e00-\u9fff]',  # 非中英文数字开头的消息
            r'^\s*$',  # 纯空白字符
        ]
        
        for pattern in invalid_patterns:
            if re.match(pattern, content):
                return False
        
        return len(content.strip()) > 0
    
    def batch_import(self, directory: Union[str, Path]) -> List[Conversation]:
        """
        批量导入目录中的所有聊天记录文件
        
        Args:
            directory: 目录路径
        
        Returns:
            导入的所有对话列表
        """
        directory = Path(directory)
        conversations = []
        
        # 支持的微信聊天记录文件扩展名
        wechat_extensions = ['*.txt', '*.json', '*.csv', '*.log']
        
        for pattern in wechat_extensions:
            for file_path in directory.glob(pattern):
                try:
                    print(f"正在导入: {file_path.name}")
                    imported_conversations = self.import_from_file(file_path)
                    conversations.extend(imported_conversations)
                    print(f"成功导入 {len(imported_conversations)} 个对话")
                except Exception as e:
                    print(f"导入文件 {file_path} 失败: {e}")
        
        return conversations
    
    def export_to_standard_format(self, conversations: List[Conversation], output_path: Union[str, Path]):
        """
        将微信聊天记录导出为标准格式
        
        Args:
            conversations: 对话列表
            output_path: 输出文件路径
        """
        output_path = Path(output_path)
        
        # 转换为标准格式
        standard_data = []
        for conv in conversations:
            for turn in conv.turns:
                if turn.metadata.get('source') == 'wechat':
                    standard_data.append({
                        'timestamp': turn.timestamp.isoformat(),
                        'sender': turn.metadata.get('original_sender', ''),
                        'content': turn.content,
                        'speaker_role': turn.speaker_role.value,
                        'message_type': turn.metadata.get('message_type', 'text')
                    })
        
        # 导出为JSON格式
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(standard_data, f, ensure_ascii=False, indent=2)
        
        print(f"标准格式导出完成: {output_path}")


# 使用示例
def main():
    """使用示例"""
    importer = WeChatChatImporter()
    
    # 导入单个文件
    try:
        conversations = importer.import_from_file("微信聊天记录.txt")
        print(f"成功导入 {len(conversations)} 个对话")
        
        for conv in conversations:
            print(f"对话包含 {len(conv.turns)} 条消息")
    except Exception as e:
        print(f"导入失败: {e}")
    
    # 批量导入
    # conversations = importer.batch_import("wechat_exports/")
    
    # 导出标准格式
    # if conversations:
    #     importer.export_to_standard_format(conversations, "standard_format.json")


if __name__ == "__main__":
    main()