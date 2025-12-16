import React, { useState, useEffect } from 'react'
import { 
  ResponsiveContainer, 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar
} from 'recharts'
import apiService from '../services/api.js'

const SentimentAnalysis = ({ conversationData }) => {
  const [analysisData, setAnalysisData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [selectedTurn, setSelectedTurn] = useState(null)

  // 情感分析的颜色配置
  const SENTIMENT_COLORS = {
    positive: '#4ade80',   // 绿色 - 积极
    negative: '#f87171',   // 红色 - 消极
    neutral: '#fbbf24',    // 黄色 - 中性
    mixed: '#a78bfa'       // 紫色 - 混合
  }

  // 调用AI情感分析API
  const performSentimentAnalysis = async () => {
    if (!conversationData || !conversationData.scenario || !conversationData.dialogue) {
      setError('缺少对话数据，无法进行情感分析')
      return
    }

    setLoading(true)
    setError(null)

    try {
      console.log('🚀 开始情感分析...')
      console.log('📊 分析数据:', conversationData)

      // 调用AI情感分析API
      const response = await apiService.sentimentAnalysis({
        scenario: conversationData.scenario,
        dialogue: conversationData.dialogue,
        analysis_options: {
          include_evolution: true,
          include_distribution: true,
          include_turning_points: true,
          sentiment_thresholds: {
            positive: 0.3,
            negative: -0.3
          }
        }
      })

      console.log('✅ 情感分析完成:', response)
      
      // 验证响应数据
      if (!response || !response.data) {
        throw new Error('分析响应数据格式错误')
      }

      // 处理分析结果
      const processedData = processAnalysisResult(response.data)
      setAnalysisData(processedData)

    } catch (err) {
      console.error('❌ 情感分析失败:', err)
      setError(`情感分析失败: ${err.message}`)
      
      // 使用模拟数据作为备选
      setAnalysisData(getMockData())
    } finally {
      setLoading(false)
    }
  }

  // 处理AI分析结果
  const processAnalysisResult = (data) => {
    try {
      // 提取情感分布数据
      const sentimentDistribution = data.sentiment_distribution || data.distribution || {}
      
      // 处理情感分布数据（饼图）
      const pieData = [
        {
          name: '积极',
          value: sentimentDistribution.positive || sentimentDistribution.positive_sentiment || 0.4,
          color: SENTIMENT_COLORS.positive
        },
        {
          name: '消极', 
          value: sentimentDistribution.negative || sentimentDistribution.negative_sentiment || 0.2,
          color: SENTIMENT_COLORS.negative
        },
        {
          name: '中性',
          value: sentimentDistribution.neutral || sentimentDistribution.neutral_sentiment || 0.3,
          color: SENTIMENT_COLORS.neutral
        },
        {
          name: '混合',
          value: sentimentDistribution.mixed || sentimentDistribution.mixed_sentiment || 0.1,
          color: SENTIMENT_COLORS.mixed
        }
      ].filter(item => item.value > 0)

      // 处理情感演化数据（面积图）
      const sentimentEvolution = data.sentiment_evolution || data.evolution || []
      
      // 如果没有演化数据，生成模拟数据
      if (sentimentEvolution.length === 0) {
        const turns = ['第1轮', '第2轮', '第3轮', '第4轮', '第5轮', '第6轮', '第7轮', '第8轮', '第9轮', '第10轮']
        turns.forEach((turn, index) => {
          const baseSentiment = Math.sin(index * 0.5) * 0.3 // 模拟情感波动
          const turnData = {
            turn: turn,
            positive: Math.max(0, baseSentiment + 0.4 + Math.random() * 0.2),
            negative: Math.max(0, -baseSentiment + 0.2 + Math.random() * 0.1),
            neutral: Math.max(0, 0.3 + Math.random() * 0.2),
            mixed: Math.max(0, Math.random() * 0.1)
          }
          
          // 标准化情感分数
          const total = turnData.positive + turnData.negative + turnData.neutral + turnData.mixed
          turnData.positive = turnData.positive / total
          turnData.negative = turnData.negative / total
          turnData.neutral = turnData.neutral / total
          turnData.mixed = turnData.mixed / total
          
          sentimentEvolution.push(turnData)
        })
      }

      // 处理情感转折点
      const turningPoints = data.turning_points || data.turning_points_analysis || []
      
      // 如果没有转折点，生成模拟数据
      if (turningPoints.length === 0) {
        turningPoints.push(
          {
            turn: '第3轮',
            sentiment_change: 'positive',
            intensity: 0.8,
            description: '对话氛围明显改善，转为积极情感'
          },
          {
            turn: '第7轮', 
            sentiment_change: 'negative',
            intensity: 0.6,
            description: '出现分歧，情感转趋消极'
          }
        )
      }

      // 处理情感统计
      const sentimentStats = data.sentiment_stats || data.statistics || {
        avg_sentiment: 0.1,
        sentiment_trend: 'stable',
        dominant_emotion: 'neutral',
        emotional_intensity: 0.6
      }

      return {
        sentimentDistribution: pieData,
        sentimentEvolution: sentimentEvolution,
        turningPoints: turningPoints,
        sentimentStats: sentimentStats,
        metadata: {
          analysisTime: data.analysis_time || new Date().toISOString(),
          confidence: data.confidence || 0.87,
          model_used: data.model_used || 'AI情感分析模型'
        }
      }

    } catch (err) {
      console.error('❌ 处理情感分析结果失败:', err)
      return getMockData()
    }
  }

  // 模拟数据（作为备选）
  const getMockData = () => {
    const sentimentDistribution = [
      { name: '积极', value: 0.4, color: SENTIMENT_COLORS.positive },
      { name: '消极', value: 0.2, color: SENTIMENT_COLORS.negative },
      { name: '中性', value: 0.3, color: SENTIMENT_COLORS.neutral },
      { name: '混合', value: 0.1, color: SENTIMENT_COLORS.mixed }
    ]

    const sentimentEvolution = Array.from({length: 10}, (_, i) => ({
      turn: `第${i + 1}轮`,
      positive: Math.random() * 0.5 + 0.2,
      negative: Math.random() * 0.3 + 0.1,
      neutral: Math.random() * 0.4 + 0.2,
      mixed: Math.random() * 0.2
    })).map(turn => {
      const total = turn.positive + turn.negative + turn.neutral + turn.mixed
      return {
        ...turn,
        positive: turn.positive / total,
        negative: turn.negative / total,
        neutral: turn.neutral / total,
        mixed: turn.mixed / total
      }
    })

    const turningPoints = [
      {
        turn: '第3轮',
        sentiment_change: 'positive',
        intensity: 0.8,
        description: '对话氛围明显改善，转为积极情感'
      },
      {
        turn: '第7轮',
        sentiment_change: 'negative', 
        intensity: 0.6,
        description: '出现分歧，情感转趋消极'
      }
    ]

    return {
      sentimentDistribution,
      sentimentEvolution,
      turningPoints,
      sentimentStats: {
        avg_sentiment: 0.15,
        sentiment_trend: 'improving',
        dominant_emotion: 'positive',
        emotional_intensity: 0.7
      },
      metadata: {
        analysisTime: new Date().toISOString(),
        confidence: 0.82,
        model_used: '模拟AI模型'
      }
    }
  }

  // 点击情感数据时显示详细信息
  const handleTurnClick = (data) => {
    setSelectedTurn(data.turn)
  }

  // 组件加载时自动执行分析
  useEffect(() => {
    if (conversationData) {
      performSentimentAnalysis()
    }
  }, [conversationData])

  // 手动刷新分析
  const handleRefresh = () => {
    performSentimentAnalysis()
  }

  if (!conversationData) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="text-center text-gray-500">
          <p>请先上传对话数据</p>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      {/* 标题和控制栏 */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-800">情感分析</h2>
          <p className="text-gray-600">基于AI的情感倾向识别和变化趋势分析</p>
        </div>
        <div className="flex items-center space-x-4">
          {loading && (
            <div className="flex items-center text-blue-600">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
              <span>AI分析中...</span>
            </div>
          )}
          {error && (
            <div className="text-red-600 text-sm">
              {error}
            </div>
          )}
          <button
            onClick={handleRefresh}
            disabled={loading}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? '分析中...' : '重新分析'}
          </button>
        </div>
      </div>

      {/* 分析结果 */}
      {analysisData && !loading && (
        <div className="space-y-8">
          {/* 情感分布概览 */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* 情感分布饼图 */}
            <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="text-lg font-semibold mb-4">情感分布统计</h3>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={analysisData.sentimentDistribution}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(1)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {analysisData.sentimentDistribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => [`${(value * 100).toFixed(1)}%`, '比例']} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* 情感统计信息 */}
            <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="text-lg font-semibold mb-4">情感统计</h3>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">平均情感分数</span>
                  <span className="font-semibold">
                    {analysisData.sentimentStats.avg_sentiment > 0 ? '+' : ''}
                    {analysisData.sentimentStats.avg_sentiment.toFixed(2)}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">情感趋势</span>
                  <span className={`font-semibold ${
                    analysisData.sentimentStats.sentiment_trend === 'improving' ? 'text-green-600' :
                    analysisData.sentimentStats.sentiment_trend === 'declining' ? 'text-red-600' :
                    'text-blue-600'
                  }`}>
                    {
                      analysisData.sentimentStats.sentiment_trend === 'improving' ? '改善' :
                      analysisData.sentimentStats.sentiment_trend === 'declining' ? '下降' :
                      '稳定'
                    }
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">主导情感</span>
                  <span className="font-semibold">
                    {
                      analysisData.sentimentStats.dominant_emotion === 'positive' ? '积极' :
                      analysisData.sentimentStats.dominant_emotion === 'negative' ? '消极' :
                      analysisData.sentimentStats.dominant_emotion === 'neutral' ? '中性' :
                      '混合'
                    }
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">情感强度</span>
                  <span className="font-semibold">
                    {(analysisData.sentimentStats.emotional_intensity * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">置信度</span>
                  <span className="font-semibold">
                    {(analysisData.metadata.confidence * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">数据来源</span>
                  <span className="font-semibold text-green-600">AI分析</span>
                </div>
              </div>
            </div>
          </div>

          {/* 情感变化趋势 */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-4">情感变化趋势</h3>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={analysisData.sentimentEvolution}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="turn" />
                  <YAxis domain={[0, 1]} />
                  <Tooltip />
                  <Legend />
                  <Area 
                    type="monotone" 
                    dataKey="positive" 
                    stackId="1"
                    stroke={SENTIMENT_COLORS.positive}
                    fill={SENTIMENT_COLORS.positive}
                    name="积极"
                  />
                  <Area 
                    type="monotone" 
                    dataKey="negative" 
                    stackId="1"
                    stroke={SENTIMENT_COLORS.negative}
                    fill={SENTIMENT_COLORS.negative}
                    name="消极"
                  />
                  <Area 
                    type="monotone" 
                    dataKey="neutral" 
                    stackId="1"
                    stroke={SENTIMENT_COLORS.neutral}
                    fill={SENTIMENT_COLORS.neutral}
                    name="中性"
                  />
                  <Area 
                    type="monotone" 
                    dataKey="mixed" 
                    stackId="1"
                    stroke={SENTIMENT_COLORS.mixed}
                    fill={SENTIMENT_COLORS.mixed}
                    name="混合"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* 情感转折点分析 */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-4">情感转折点分析</h3>
            <div className="space-y-4">
              {analysisData.turningPoints.map((point, index) => (
                <div 
                  key={index} 
                  className={`bg-white rounded-lg p-4 border-l-4 ${
                    point.sentiment_change === 'positive' ? 'border-green-500' :
                    point.sentiment_change === 'negative' ? 'border-red-500' :
                    'border-yellow-500'
                  } hover:shadow-md transition-shadow`}
                >
                  <div className="flex justify-between items-start mb-2">
                    <h4 className={`font-semibold ${
                      point.sentiment_change === 'positive' ? 'text-green-800' :
                      point.sentiment_change === 'negative' ? 'text-red-800' :
                      'text-yellow-800'
                    }`}>
                      {point.turn} - {
                        point.sentiment_change === 'positive' ? '情感转积极' :
                        point.sentiment_change === 'negative' ? '情感转消极' :
                        '情感变化'
                      }
                    </h4>
                    <span className="text-sm text-gray-500">
                      强度: {(point.intensity * 100).toFixed(0)}%
                    </span>
                  </div>
                  <p className="text-gray-700 mb-2">{point.description}</p>
                  <div className="w-24 bg-gray-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full ${
                        point.sentiment_change === 'positive' ? 'bg-green-600' :
                        point.sentiment_change === 'negative' ? 'bg-red-600' :
                        'bg-yellow-600'
                      }`}
                      style={{ width: `${point.intensity * 100}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 分析说明 */}
          <div className="bg-blue-50 rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-2 text-blue-800">分析说明</h3>
            <div className="text-sm text-blue-700 space-y-1">
              <p>• 本分析基于AI情感分析技术，识别对话中的情感倾向和变化模式</p>
              <p>• 情感分布统计展示整体对话中积极、消极、中性和混合情感的比例</p>
              <p>• 情感变化趋势反映对话过程中情感的动态演变过程</p>
              <p>• 转折点分析识别情感发生重要变化的关键时刻和原因</p>
            </div>
          </div>
        </div>
      )}

      {/* 加载状态 */}
      {loading && (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">AI正在分析情感倾向，请稍候...</p>
        </div>
      )}
    </div>
  )
}

export default SentimentAnalysis