// API服务层 - 统一管理后端API调用
const API_BASE_URL = 'http://localhost:8001'

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL
  }

  // 通用请求方法
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`
    
    // 对于AI分析请求，使用更长的超时时间
    const timeout = endpoint.includes('/analysis/') ? 60000 : 10000 // AI分析60秒，其他10秒
    
    const config = {
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        ...options.headers,
      },
      // 添加超时设置 - AI分析使用更长时间
      signal: AbortSignal.timeout(timeout),
      ...options,
    }

    try {
      console.log(`🔗 发起API请求: ${options.method || 'GET'} ${url} (超时: ${timeout/1000}秒)`)
      console.log('📤 请求数据:', options.body ? JSON.parse(options.body) : null)
      
      const response = await fetch(url, config)
      
      console.log(`📥 响应状态: ${response.status} ${response.statusText}`)
      
      if (!response.ok) {
        const errorText = await response.text()
        console.error('❌ API错误响应:', errorText)
        throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`)
      }
      
      const contentType = response.headers.get('content-type')
      if (contentType && contentType.includes('application/json')) {
        const result = await response.json()
        console.log('✅ API成功响应:', result)
        return result
      }
      
      const textResult = await response.text()
      console.log('📝 API文本响应:', textResult)
      return textResult
    } catch (error) {
      console.error('💥 API请求失败:', error)
      console.error('💥 错误类型:', error.constructor.name)
      console.error('💥 错误详情:', error.message)
      
      // 对于超时错误，提供更友好的错误信息
      if (error.name === 'TimeoutError' || error.message.includes('signal timed out')) {
        throw new Error('AI分析需要较长时间，请稍等片刻后重试')
      }
      
      throw error
    }
  }

  // 微信提取相关API

  /**
   * 配置OCR设置
   * @param {Object} ocrConfig - OCR配置对象
   * @param {string} ocrConfig.apiKey - 百度OCR API Key
   * @param {string} ocrConfig.secretKey - 百度OCR Secret Key
   */
  async configureOCR(ocrConfig) {
    return this.request('/api/v1/wechat-extractor/ocr-config', {
      method: 'POST',
      body: JSON.stringify(ocrConfig)
    })
  }

  /**
   * 上传文件用于微信记录提取
   * @param {File} file - 要上传的文件
   * @param {Function} onProgress - 上传进度回调
   */
  async uploadWeChatFile(file, onProgress = null) {
    const formData = new FormData()
    formData.append('file', file)

    const config = {
      method: 'POST',
      body: formData,
    }

    // 如果有进度回调，使用XMLHttpRequest来获取上传进度
    if (onProgress) {
      return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest()
        
        xhr.upload.addEventListener('progress', (event) => {
          if (event.lengthComputable) {
            const percentComplete = (event.loaded / event.total) * 100
            onProgress(percentComplete)
          }
        })

        xhr.addEventListener('load', () => {
          if (xhr.status >= 200 && xhr.status < 300) {
            try {
              resolve(JSON.parse(xhr.responseText))
            } catch (e) {
              resolve(xhr.responseText)
            }
          } else {
            reject(new Error(`Upload failed with status ${xhr.status}`))
          }
        })

        xhr.addEventListener('error', () => {
          reject(new Error('Upload failed'))
        })

        xhr.open('POST', `${this.baseURL}/api/v1/wechat/upload`)
        xhr.send(formData)
      })
    }

    // 普通请求
    return this.request('/api/v1/wechat/upload', config)
  }

  /**
   * 批量导入微信聊天记录
   * @param {Object} importData - 导入数据
   */
  async batchImportWeChatRecords(importData) {
    return this.request('/api/v1/wechat/import', {
      method: 'POST',
      body: JSON.stringify(importData)
    })
  }

  /**
   * 从图片提取微信聊天记录
   * @param {Object} extractRequest - 提取请求参数
   */
  async extractFromImage(extractRequest) {
    return this.request('/api/v1/wechat-extractor/extract/image', {
      method: 'POST',
      body: JSON.stringify(extractRequest)
    })
  }

  // AI分析相关API

  /**
   * 简单分析 - 基础对话分析
   * @param {Object} analysisRequest - 分析请求
   */
  async simpleAnalysis(analysisRequest) {
    return this.request('/api/v1/analysis/simple', {
      method: 'POST',
      body: JSON.stringify(analysisRequest)
    })
  }

  /**
   * 多维度增强分析 - 深度AI分析
   * @param {Object} analysisRequest - 分析请求
   */
  async enhancedAnalysis(analysisRequest) {
    return this.request('/api/v1/analysis/enhanced', {
      method: 'POST',
      body: JSON.stringify(analysisRequest)
    })
  }

  /**
   * 主题分析 - AI主题识别和演化分析
   * @param {Object} analysisRequest - 分析请求
   */
  async topicAnalysis(analysisRequest) {
    return this.request('/api/v1/analysis/topic', {
      method: 'POST',
      body: JSON.stringify(analysisRequest)
    })
  }

  /**
   * 情感分析 - AI情感倾向分析
   * @param {Object} analysisRequest - 分析请求
   */
  async sentimentAnalysis(analysisRequest) {
    return this.request('/api/v1/analysis/sentiment', {
      method: 'POST',
      body: JSON.stringify(analysisRequest)
    })
  }

  /**
   * 关键观点分析 - AI观点提取和重要性分析
   * @param {Object} analysisRequest - 分析请求
   */
  async keyPointsAnalysis(analysisRequest) {
    return this.request('/api/v1/analysis/keypoints', {
      method: 'POST',
      body: JSON.stringify(analysisRequest)
    })
  }

  /**
   * 意图分析 - AI对话意图识别
   * @param {Object} analysisRequest - 分析请求
   */
  async intentAnalysis(analysisRequest) {
    return this.request('/api/v1/analysis/intent', {
      method: 'POST',
      body: JSON.stringify(analysisRequest)
    })
  }

  /**
   * 逻辑结构分析 - AI逻辑关系分析
   * @param {Object} analysisRequest - 分析请求
   */
  async logicalAnalysis(analysisRequest) {
    return this.request('/api/v1/analysis/logical', {
      method: 'POST',
      body: JSON.stringify(analysisRequest)
    })
  }

  /**
   * 隐含信息分析 - AI隐性内容挖掘
   * @param {Object} analysisRequest - 分析请求
   */
  async hiddenAnalysis(analysisRequest) {
    return this.request('/api/v1/analysis/hidden', {
      method: 'POST',
      body: JSON.stringify(analysisRequest)
    })
  }

  /**
   * 未来发展预测 - AI趋势预测
   * @param {Object} analysisRequest - 分析请求
   */
  async futureAnalysis(analysisRequest) {
    return this.request('/api/v1/analysis/future', {
      method: 'POST',
      body: JSON.stringify(analysisRequest)
    })
  }

  /**
   * 批量分析 - 同时进行多种分析
   * @param {Object} analysisRequest - 分析请求
   */
  async batchAnalysis(analysisRequest) {
    return this.request('/api/v1/analysis/batch', {
      method: 'POST',
      body: JSON.stringify(analysisRequest)
    })
  }

  /**
   * 获取分析模板列表
   */
  async getAnalysisTemplates() {
    return this.request('/api/v1/analysis/templates', {
      method: 'GET'
    })
  }

  /**
   * 保存分析模板
   * @param {Object} templateData - 模板数据
   */
  async saveAnalysisTemplate(templateData) {
    return this.request('/api/v1/analysis/templates', {
      method: 'POST',
      body: JSON.stringify(templateData)
    })
  }

  /**
   * 导出分析报告
   * @param {string} analysisId - 分析ID
   * @param {string} format - 导出格式 (json, pdf, csv)
   */
  async exportAnalysisReport(analysisId, format = 'json') {
    return this.request(`/api/v1/analysis/${analysisId}/export?format=${format}`, {
      method: 'GET'
    })
  }

  /**
   * 比较分析结果
   * @param {Object} comparisonRequest - 比较请求
   */
  async compareAnalysis(comparisonRequest) {
    return this.request('/api/v1/analysis/compare', {
      method: 'POST',
      body: JSON.stringify(comparisonRequest)
    })
  }

  /**
   * 获取分析历史记录
   */
  async getAnalysisHistory() {
    return this.request('/api/v1/analysis/history', {
      method: 'GET'
    })
  }

  /**
   * 获取分析状态
   * @param {string} analysisId - 分析ID
   */
  async getAnalysisStatus(analysisId) {
    return this.request(`/api/v1/analysis/${analysisId}/status`, {
      method: 'GET'
    })
  }

  /**
   * 智能分析建议 - 基于对话内容推荐分析类型
   * @param {Object} conversationData - 对话数据
   */
  async getAnalysisRecommendations(conversationData) {
    return this.request('/api/v1/analysis/recommendations', {
      method: 'POST',
      body: JSON.stringify(conversationData)
    })
  }

  /**
   * 对话洞察分析 - 综合AI洞察生成
   * @param {Object} analysisRequest - 分析请求
   */
  async conversationInsights(analysisRequest) {
    return this.request('/api/v1/analysis/insights', {
      method: 'POST',
      body: JSON.stringify(analysisRequest)
    })
  }

  /**
   * 获取支持的AI模型列表
   */
  async getAvailableModels() {
    return this.request('/api/v1/models/available', {
      method: 'GET'
    })
  }

  /**
   * 配置AI模型参数
   * @param {Object} modelConfig - 模型配置
   */
  async configureModel(modelConfig) {
    return this.request('/api/v1/models/config', {
      method: 'POST',
      body: JSON.stringify(modelConfig)
    })
  }

  // PaddleOCR相关API (继续之前的代码)

  /**
   * 配置PaddleOCR MCP服务器
   * @param {Object} paddleConfig - PaddleOCR配置对象
   */
  async configurePaddleOCR(paddleConfig) {
    return this.request('/api/v1/paddleocr/config', {
      method: 'POST',
      body: JSON.stringify(paddleConfig)
    })
  }

  /**
   * 获取PaddleOCR状态
   */
  async getPaddleOCRStatus() {
    return this.request('/api/v1/paddleocr/status', {
      method: 'GET'
    })
  }

  /**
   * 获取PaddleOCR MCP配置
   */
  async getPaddleOCRMCPConfig() {
    return this.request('/api/v1/paddleocr/mcp-config', {
      method: 'GET'
    })
  }

  /**
   * 获取PaddleOCR功能列表
   */
  async getPaddleOCRFeatures() {
    return this.request('/api/v1/paddleocr/features', {
      method: 'GET'
    })
  }

  /**
   * 获取PaddleOCR与百度OCR对比
   */
  async getOCRComparison() {
    return this.request('/api/v1/paddleocr/comparison', {
      method: 'GET'
    })
  }

  /**
   * 测试PaddleOCR连接
   */
  async testPaddleOCRConnection() {
    return this.request('/api/v1/paddleocr/test', {
      method: 'POST'
    })
  }

  /**
   * 上传文件并使用PaddleOCR分析
   * @param {File} file - 要上传的文件
   * @param {string} analysisType - 分析类型
   */
  async uploadAndAnalyzeWithPaddleOCR(file, analysisType = 'wechat') {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('analysis_type', analysisType)

    const config = {
      method: 'POST',
      body: formData,
    }

    return this.request('/api/v1/paddleocr/upload-and-analyze', config)
  }
}

// 创建单例
const apiService = new ApiService()

export default apiService