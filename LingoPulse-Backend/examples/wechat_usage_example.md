# 微信聊天记录处理使用示例

## 功能概述

LingoPulse-Backend 现在支持处理微信聊天记录，包括导入、分析和批量处理功能。

## 支持的格式

### 1. 文本格式 (.txt)
微信导出的文本格式聊天记录，每条消息占一行，格式为：
```
2024-01-01 12:00:00 张三: 你好
2024-01-01 12:01:00 李四: 你好，有什么新的项目吗？
2024-01-01 12:02:00 张三: 是的，我们有一个AI聊天分析的新项目
```

### 2. JSON格式 (.json)
结构化的JSON格式，包含消息数组：
```json
{
  "messages": [
    {
      "timestamp": "2024-01-01T12:00:00",
      "sender": "张三",
      "content": "你好"
    },
    {
      "timestamp": "2024-01-01T12:01:00", 
      "sender": "李四",
      "content": "你好，有什么新的项目吗？"
    }
  ]
}
```

### 3. CSV格式 (.csv)
逗号分隔的CSV格式：
```csv
timestamp,sender,content
2024-01-01 12:00:00,张三,你好
2024-01-01 12:01:00,李四,你好，有什么新的项目吗？
2024-01-01 12:02:00,张三,是的，我们有一个AI聊天分析的新项目
```

## API使用示例

### 1. 上传微信聊天记录文件

```bash
curl -X POST "http://localhost:8000/api/v1/wechat/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@wechat_chat_record.txt" \
  -F "conversation_name=项目讨论群" \
  -F 'participants=["张三", "李四", "王五"]' \
  -F "conversation_type=wechat"
```

### 2. 导入聊天记录

```bash
curl -X POST "http://localhost:8000/api/v1/wechat/import" \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "/path/to/wechat_record.txt",
    "conversation_name": "项目讨论群",
    "participants": ["张三", "李四", "王五"],
    "conversation_type": "wechat"
  }'
```

### 3. 分析微信对话

```bash
curl -X GET "http://localhost:8000/api/v1/wechat/analysis/{conversation_id}"
```

### 4. 批量导入

```bash
curl -X POST "http://localhost:8000/api/v1/wechat/batch-import" \
  -H "Content-Type: application/json" \
  -d '{
    "file_paths": [
      "/path/to/chat1.txt",
      "/path/to/chat2.json", 
      "/path/to/chat3.csv"
    ],
    "conversation_name": "批量导入测试",
    "participants": ["用户A", "用户B"]
  }'
```

### 5. 获取支持的格式信息

```bash
curl -X GET "http://localhost:8000/api/v1/wechat/formats"
```

## Python客户端示例

### 基础使用

```python
import requests
import json

# API基础地址
BASE_URL = "http://localhost:8000/api/v1"

# 1. 上传微信聊天记录
def upload_wechat_record(file_path, conversation_name, participants):
    url = f"{BASE_URL}/wechat/upload"
    
    with open(file_path, 'rb') as f:
        files = {'file': f}
        data = {
            'conversation_name': conversation_name,
            'participants': json.dumps(participants),
            'conversation_type': 'wechat'
        }
        
        response = requests.post(url, files=files, data=data)
        return response.json()

# 2. 分析微信对话
def analyze_wechat_conversation(conversation_id):
    url = f"{BASE_URL}/wechat/analysis/{conversation_id}"
    response = requests.get(url)
    return response.json()

# 3. 批量导入
def batch_import_wechat_records(file_paths, conversation_name, participants):
    url = f"{BASE_URL}/wechat/batch-import"
    data = {
        'file_paths': file_paths,
        'conversation_name': conversation_name,
        'participants': participants
    }
    response = requests.post(url, json=data)
    return response.json()

# 使用示例
if __name__ == "__main__":
    # 上传微信聊天记录
    result = upload_wechat_record(
        "wechat_record.txt",
        "项目讨论群",
        ["张三", "李四", "王五"]
    )
    print("上传结果:", result)
    
    # 分析对话
    analysis = analyze_wechat_conversation("conversation-id-here")
    print("分析结果:", analysis)
```

### 完整工作流

```python
class WeChatChatProcessor:
    def __init__(self, base_url="http://localhost:8000/api/v1"):
        self.base_url = base_url
    
    def process_wechat_chat(self, file_path, conversation_name, participants):
        """完整的微信聊天记录处理流程"""
        
        print("1. 上传聊天记录文件...")
        upload_result = self.upload_file(file_path, conversation_name, participants)
        
        if upload_result['status'] == 'uploaded':
            print("✅ 文件上传成功")
            
            print("2. 导入聊天记录...")
            import_result = self.import_chat_record(
                upload_result.get('file_path'),
                conversation_name,
                participants
            )
            
            if import_result['status'] == 'success':
                print("✅ 聊天记录导入成功")
                
                # 获取第一个对话ID进行分析
                conversations = import_result['conversations']
                if conversations:
                    conversation_id = conversations[0]['id']
                    
                    print("3. 分析聊天记录...")
                    analysis_result = self.analyze_conversation(conversation_id)
                    
                    return {
                        'upload_result': upload_result,
                        'import_result': import_result,
                        'analysis_result': analysis_result
                    }
        
        return None
    
    def upload_file(self, file_path, conversation_name, participants):
        """上传文件"""
        import requests
        
        url = f"{self.base_url}/wechat/upload"
        
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {
                'conversation_name': conversation_name,
                'participants': json.dumps(participants),
                'conversation_type': 'wechat'
            }
            
            response = requests.post(url, files=files, data=data)
            return response.json()
    
    def import_chat_record(self, file_path, conversation_name, participants):
        """导入聊天记录"""
        import requests
        
        url = f"{self.base_url}/wechat/import"
        data = {
            'file_path': file_path,
            'conversation_name': conversation_name,
            'participants': participants,
            'conversation_type': 'wechat'
        }
        
        response = requests.post(url, json=data)
        return response.json()
    
    def analyze_conversation(self, conversation_id):
        """分析对话"""
        import requests
        
        url = f"{self.base_url}/wechat/analysis/{conversation_id}"
        response = requests.get(url)
        return response.json()

# 使用示例
processor = WeChatChatProcessor()

result = processor.process_wechat_chat(
    "wechat_record.txt",
    "团队项目讨论",
    ["项目经理", "开发人员A", "开发人员B", "测试人员"]
)

if result:
    print("\n📊 分析报告:")
    analysis = result['analysis_result']
    print(f"对话ID: {analysis['conversation_id']}")
    print(f"总体情感: {analysis['results']['sentiment_analysis']['overall_sentiment']}")
    print(f"沟通风格: {analysis['results']['communication_style']}")
    print(f"参与度评分: {analysis['results']['interaction_quality']['engagement_score']}")
    print("\n💡 建议:")
    for rec in analysis['recommendations']:
        print(f"  • {rec}")
```

## 分析结果说明

分析功能会提供以下维度的分析：

### 1. 沟通模式
- 消息频率分析
- 平均响应时间
- 活跃时间段统计

### 2. 情感分析
- 整体情感倾向
- 情感趋势变化
- 情感峰值检测

### 3. 互动质量
- 参与度评分
- 清晰度评分
- 协作性评分

### 4. 话题分析
- 关键话题提取
- 话题频次统计
- 话题转换分析

### 5. 沟通风格
- 沟通方式识别
- 专业度评估
- 友好程度分析

## 注意事项

1. **文件大小限制**: 单个文件最大50MB
2. **消息数量**: 单个文件最多10,000条消息
3. **编码支持**: 支持UTF-8、GBK、GB2312编码
4. **临时文件**: 上传的文件在处理完成后会自动删除
5. **后台处理**: 文件上传后会在后台异步处理，可以通过状态接口查询处理进度

## 错误处理

常见错误及解决方案：

- **不支持的文件格式**: 请使用 .txt、.json 或 .csv 格式
- **文件不存在**: 请确保文件路径正确且文件存在
- **编码错误**: 建议使用UTF-8编码保存文件
- **文件过大**: 请压缩聊天记录或分批处理

## 示例文件

您可以在 `examples/` 目录下找到示例聊天记录文件，用于测试功能。

- `sample_wechat.txt` - 文本格式示例
- `sample_wechat.json` - JSON格式示例
- `sample_wechat.csv` - CSV格式示例