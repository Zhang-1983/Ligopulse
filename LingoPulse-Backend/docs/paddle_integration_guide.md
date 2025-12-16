# 飞桨平台集成指南

本文档介绍了如何在LingoPulse项目中集成飞桨平台并使用访问令牌进行身份验证。

## 获取访问令牌

1. 访问[飞桨平台官网](https://www.paddlepaddle.org.cn/)
2. 登录您的账户
3. 进入API密钥管理页面
4. 创建新的访问令牌
5. 复制并安全保存此令牌

## 配置环境变量

1. 复制 `.env.example` 文件并重命名为 `.env`
2. 编辑 `.env` 文件，设置以下飞桨平台相关配置：

```bash
# 飞桨平台配置
PADDLE_ACCESS_TOKEN=your_paddle_access_token_here
PADDLE_BASE_URL=https://api.paddlepaddle.org
PADDLE_MODEL_NAME=paddle-model-name
PADDLE_TEMPERATURE=0.7
PADDLE_MAX_TOKENS=1000
```

将 `your_paddle_access_token_here` 替换为您在第一步获取的访问令牌。

## 使用API

LingoPulse项目为飞桨平台提供了以下API端点：

1. **设置访问令牌**
   - 端点: `POST /api/v1/paddle/token`
   - 描述: 设置飞桨平台的访问令牌

2. **生成对话**
   - 端点: `POST /api/v1/paddle/chat/completions`
   - 描述: 使用飞桨平台生成对话

3. **获取模型信息**
   - 端点: `GET /api/v1/paddle/models`
   - 描述: 获取可用的飞桨平台模型信息

4. **测试连接**
   - 端点: `GET /api/v1/paddle/ping`
   - 描述: 测试与飞桨平台的连接

## 代码示例

```python
import requests
import json

# 配置
BASE_URL = "http://localhost:8000/api/v1"
PADDLE_TOKEN = "your_paddle_access_token_here"

# 设置访问令牌
def set_access_token():
    url = f"{BASE_URL}/paddle/token"
    headers = {"Content-Type": "application/json"}
    data = {"access_token": PADDLE_TOKEN}
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json()

# 生成对话
def generate_chat(message):
    url = f"{BASE_URL}/paddle/chat/completions"
    headers = {"Content-Type": "application/json"}
    data = {
        "messages": [
            {"role": "user", "content": message}
        ],
        "model": "paddle-model-name",
        "temperature": 0.7,
        "max_tokens": 1000
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json()

# 获取模型信息
def get_models():
    url = f"{BASE_URL}/paddle/models"
    response = requests.get(url)
    return response.json()

# 测试连接
def ping():
    url = f"{BASE_URL}/paddle/ping"
    response = requests.get(url)
    return response.json()

# 示例用法
if __name__ == "__main__":
    # 设置访问令牌
    set_access_token()
    
    # 测试连接
    print(ping())
    
    # 生成对话
    response = generate_chat("你好，请介绍一下你自己。")
    print(response)
    
    # 获取模型信息
    print(get_models())
```

## 注意事项

1. 访问令牌是敏感信息，请不要将其提交到版本控制系统
2. 在生产环境中，应通过安全的方式存储和传输访问令牌
3. 请遵守飞桨平台的使用条款和限制
4. 本集成目前只支持基本的对话生成功能，如需使用更多功能，请参考飞桨平台官方文档

## 故障排除

如果您在集成过程中遇到问题，请检查：

1. 访问令牌是否正确设置
2. 网络连接是否正常
3. 飞桨平台服务是否可用
4. API端点URL是否正确

如需更多帮助，请联系开发团队或查看飞桨平台官方文档。