# LingoPulse - AI对话分析平台

LingoPulse 是一个基于 AI 的对话分析平台，专注于使用百度飞桨（PaddlePaddle）和文心一言（ERNIE）模型进行对话内容的深度分析。

## 🌟 功能特性

- **对话情感分析**：自动识别对话的情感倾向
- **关键词提取**：智能提取对话中的核心关键词
- **语言复杂度评估**：分析对话的语言难度和复杂度
- **深度洞察生成**：基于分析结果生成有价值的洞察
- **实用建议推荐**：提供针对性的改进建议
- **多模型支持**：支持多种百度飞桨模型，包括 ERNIE-4.5-21B-A3B-Thinking

## 🛠️ 技术栈

### 后端
- **框架**：FastAPI
- **语言**：Python 3.9+
- **AI 模型**：百度飞桨（PaddlePaddle）、文心一言（ERNIE）
- **数据库**：SQLite（开发）/ PostgreSQL（生产）
- **API 文档**：Swagger UI / ReDoc

### 前端
- **框架**：React 18
- **构建工具**：Vite
- **UI 组件**：Ant Design
- **HTTP 客户端**：Axios

## 📁 项目结构

```
.
├── LingoPulse/                  # 前端项目目录
│   ├── src/                     # 前端源代码
│   ├── public/                  # 静态资源
│   ├── package.json             # 前端依赖配置
│   └── vite.config.js           # Vite 配置
├── LingoPulse-Backend/          # 后端项目目录
│   ├── infrastructure/          # 基础设施层
│   │   └── llm_providers/       # LLM 提供商实现
│   ├── presentation/            # 表示层（API 路由）
│   ├── utils/                   # 工具函数
│   ├── config.py                # 配置管理
│   ├── main.py                  # 后端入口
│   ├── requirements.txt         # 后端依赖
│   └── .env                     # 环境变量配置
└── README.md                    # 项目说明文档
```

## 🚀 快速开始

### 1. 环境要求

- Python 3.9+
- Node.js 16+
- npm 或 yarn

### 2. 后端安装与运行

```bash
# 进入后端目录
cd LingoPulse-Backend

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
# 复制 .env.example 为 .env 并修改配置
# cp .env.example .env

# 启动开发服务器
python main.py --host 0.0.0.0 --port 8001 --reload
```

### 3. 前端安装与运行

```bash
# 进入前端目录
cd LingoPulse

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 4. 访问应用

- 前端应用：http://localhost:5173
- API 文档：http://localhost:8001/docs
- 健康检查：http://localhost:8001/health

## ⚙️ 配置说明

### 环境变量配置

在 `LingoPulse-Backend/.env` 文件中配置以下参数：

```env
# 飞桨平台配置
PADDLE_ACCESS_TOKEN=your_paddle_access_token
PADDLE_BASE_URL=https://aistudio.baidu.com/llm/lmapi/v3
PADDLE_MODEL_NAME=ERNIE-4.5-21B-A3B-Thinking
PADDLE_TEMPERATURE=0.7
PADDLE_MAX_TOKENS=1000

# 服务配置
HOST=0.0.0.0
PORT=8001
DEBUG=true
```

### 模型配置

目前支持的模型：
- ERNIE-4.5-21B-A3B-Thinking
- ERNIE-3.5
- ERNIE-4.0

## 📖 API 文档

启动后端服务后，可通过以下地址访问 API 文档：

- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

### 主要 API 端点

- `POST /api/v1/analysis/simple` - 简单对话分析
- `GET /api/v1/providers` - 获取可用的 LLM 提供商
- `GET /health` - 健康检查

## 📊 使用示例

### 对话分析请求

```bash
curl -X POST "http://localhost:8001/api/v1/analysis/simple" \
  -H "Content-Type: application/json" \
  -d '{"text": "你好，我想了解一下你们的产品。"}'
```

### 响应示例

```json
{
  "sentiment": 0.8,
  "keywords": ["产品", "了解"],
  "complexity": 0.3,
  "insights": ["用户对产品表现出兴趣"],
  "recommendations": ["可以详细介绍产品的核心功能"]
}
```

## 🔧 开发指南

### 后端开发

```bash
# 运行测试
pytest

# 代码格式化
black .

# 代码检查
flake8
```

### 前端开发

```bash
# 运行测试
npm test

# 构建生产版本
npm run build

# 代码格式化
npm run format
```

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 Apache 2.0 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- 百度飞桨（PaddlePaddle）团队
- 文心一言（ERNIE）团队
- FastAPI 社区
- React 社区

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 项目地址：https://github.com/Zhang-1983/Lingopulse.git
- 邮箱：1175297551@qq.com

---

**LingoPulse - 让对话分析更智能** 🚀
