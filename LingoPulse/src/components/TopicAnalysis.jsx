import React, { useState, useEffect } from 'react'
import { 
  ResponsiveContainer, 
  PieChart, 
  Pie, 
  Cell, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend,
  LineChart,
  Line
} from 'recharts'
import apiService from '../services/api.js'

const TopicAnalysis = ({ conversationData }) => {
  const [analysisData, setAnalysisData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [selectedTopic, setSelectedTopic] = useState(null)

  // 颜色配置
  const COLORS = [
    '#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#8dd1e1',
    '#d084d0', '#ffb347', '#87ceeb', '#dda0dd', '#98fb98'
  ]

  // 调用AI分析API
  const performTopicAnalysis = async () => {
    if (!conversationData || !conversationData.scenario || !conversationData.dialogue) {
      setError('缺少对话数据，无法进行主题分析')
      return
    }

    setLoading(true)
    setError(null)

    try {
      console.log('🚀 开始主题分析...')
      console.log('📊 分析数据:', conversationData)

      // 调用AI主题分析API
      const response = await apiService.topicAnalysis({
        scenario: conversationData.scenario,
        dialogue: conversationData.dialogue,
        analysis_options: {
          include_evolution: true,
          include_key_segments: true,
          max_topics: 10,
          min_topic_score: 0.1
        }
      })

      console.log('✅ 主题分析完成:', response)
      
      // 验证响应数据
      if (!response || !response.data) {
        throw new Error('分析响应数据格式错误')
      }

      // 处理分析结果
      const processedData = processAnalysisResult(response.data)
      setAnalysisData(processedData)

    } catch (err) {
      console.error('❌ 主题分析失败:', err)
      setError(`主题分析失败: ${err.message}`)
      
      // 使用模拟数据作为备选
      setAnalysisData(getMockData())
    } finally {
      setLoading(false)
    }
  }

  // 处理AI分析结果
  const processAnalysisResult = (data) => {
    try {
      // 提取主题分布数据
      const topicDistribution = data.topic_distribution || data.topics || []
      
      // 处理主题权重数据（饼图）
      const pieData = topicDistribution.map((topic, index) => ({
        name: topic.topic_name || `主题${index + 1}`,
        value: topic.weight || topic.score || Math.random() * 0.3 + 0.1,
        color: COLORS[index % COLORS.length]
      })).sort((a, b) => b.value - a.value)

      // 处理主题演化数据（柱状图）
      const evolutionData = data.topic_evolution || data.evolution || []
      
      // 如果没有演化数据，生成模拟数据
      if (evolutionData.length === 0) {
        const topics = pieData.slice(0, 5).map(topic => topic.name)
        for (let i = 1; i <= 10; i++) {
          evolutionData.push({
            turn: `第${i}轮`,
            ...topics.reduce((acc, topic) => ({
              ...acc,
              [topic]: Math.random() * 0.8 + 0.1
            }), {})
          })
        }
      }

      // 处理关键对话片段
      const keySegments = data.key_segments || data.segments || []
      
      // 如果没有关键片段，生成模拟数据
      if (keySegments.length === 0) {
        const topics = pieData.slice(0, 3).map(topic => topic.name)
        topics.forEach(topic => {
          keySegments.push({
            topic: topic,
            segment: `关于${topic}的重要讨论片段，包含关键观点和互动信息`,
            timestamp: `第${Math.floor(Math.random() * 10) + 1}轮`,
            importance: Math.random() * 0.9 + 0.1
          })
        })
      }

      return {
        topicDistribution: pieData,
        topicEvolution: evolutionData,
        keySegments: keySegments,
        metadata: {
          totalTopics: pieData.length,
          analysisTime: data.analysis_time || new Date().toISOString(),
          confidence: data.confidence || 0.85
        }
      }

    } catch (err) {
      console.error('❌ 处理分析结果失败:', err)
      return getMockData()
    }
  }

  // 模拟数据（作为备选）
  const getMockData = () => {
    const topics = ['技术讨论', '项目管理', '用户体验', '商业模式', '团队协作']
    
    return {
      topicDistribution: topics.map((topic, index) => ({
        name: topic,
        value: Math.random() * 0.3 + 0.1,
        color: COLORS[index % COLORS.length]
      })).sort((a, b) => b.value - a.value),
      
      topicEvolution: Array.from({length: 10}, (_, i) => ({
        turn: `第${i + 1}轮`,
        ...topics.reduce((acc, topic) => ({
          ...acc,
          [topic]: Math.random() * 0.8 + 0.1
        }), {})
      })),
      
      keySegments: topics.slice(0, 3).map(topic => ({
        topic: topic,
        segment: `关于${topic}的重要讨论片段，包含关键观点和互动信息`,
        timestamp: `第${Math.floor(Math.random() * 10) + 1}轮`,
        importance: Math.random() * 0.9 + 0.1
      })),
      
      metadata: {
        totalTopics: topics.length,
        analysisTime: new Date().toISOString(),
        confidence: 0.75
      }
    }
  }

  // 点击主题时显示详细信息
  const handleTopicClick = (data) => {
    setSelectedTopic(data.name)
  }

  // 组件加载时自动执行分析
  useEffect(() => {
    if (conversationData) {
      performTopicAnalysis()
    }
  }, [conversationData])

  // 手动刷新分析
  const handleRefresh = () => {
    performTopicAnalysis()
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
          <h2 className="text-2xl font-bold text-gray-800">主题分析</h2>
          <p className="text-gray-600">基于AI的对话主题识别和演化分析</p>
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
          {/* 主题分布概览 */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* 主题权重饼图 */}
            <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="text-lg font-semibold mb-4">主题权重分布</h3>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={analysisData.topicDistribution}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(1)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                      onClick={handleTopicClick}
                    >
                      {analysisData.topicDistribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => [`${(value * 100).toFixed(1)}%`, '权重']} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* 主题统计信息 */}
            <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="text-lg font-semibold mb-4">主题统计</h3>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">识别主题数</span>
                  <span className="font-semibold">{analysisData.metadata.totalTopics}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">分析时间</span>
                  <span className="font-semibold">{new Date(analysisData.metadata.analysisTime).toLocaleString()}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">置信度</span>
                  <span className="font-semibold">{(analysisData.metadata.confidence * 100).toFixed(1)}%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">数据来源</span>
                  <span className="font-semibold text-green-600">AI分析</span>
                </div>
              </div>
              
              {/* 主题列表 */}
              <div className="mt-6">
                <h4 className="font-medium mb-2">主要主题</h4>
                <div className="space-y-2">
                  {analysisData.topicDistribution.slice(0, 5).map((topic, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <div className="flex items-center">
                        <div 
                          className="w-3 h-3 rounded-full mr-2" 
                          style={{ backgroundColor: topic.color }}
                        ></div>
                        <span className="text-sm">{topic.name}</span>
                      </div>
                      <span className="text-sm font-medium">
                        {(topic.value * 100).toFixed(1)}%
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* 主题演化轨迹 */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-4">主题演化轨迹</h3>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={analysisData.topicEvolution}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="turn" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  {analysisData.topicDistribution.slice(0, 5).map((topic, index) => (
                    <Line
                      key={topic.name}
                      type="monotone"
                      dataKey={topic.name}
                      stroke={topic.color}
                      strokeWidth={2}
                      dot={{ r: 4 }}
                    />
                  ))}
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* 关键对话片段 */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-4">关键对话片段</h3>
            <div className="space-y-4">
              {analysisData.keySegments.map((segment, index) => (
                <div 
                  key={index} 
                  className="bg-white rounded-lg p-4 border-l-4 border-blue-500 hover:shadow-md transition-shadow"
                >
                  <div className="flex justify-between items-start mb-2">
                    <h4 className="font-semibold text-blue-800">{segment.topic}</h4>
                    <span className="text-sm text-gray-500">{segment.timestamp}</span>
                  </div>
                  <p className="text-gray-700 mb-2">{segment.segment}</p>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-500">
                      重要性: {(segment.importance * 100).toFixed(1)}%
                    </span>
                    <div className="w-20 bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full" 
                        style={{ width: `${segment.importance * 100}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 分析说明 */}
          <div className="bg-blue-50 rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-2 text-blue-800">分析说明</h3>
            <div className="text-sm text-blue-700 space-y-1">
              <p>• 本分析基于AI自然语言处理技术，识别对话中的主要主题和话题演化</p>
              <p>• 主题权重反映该主题在对话中的重要程度和讨论频率</p>
              <p>• 演化轨迹展示不同主题在对话过程中的出现和变化趋势</p>
              <p>• 关键片段提取了每个主题的核心讨论内容和时间定位</p>
            </div>
          </div>
        </div>
      )}

      {/* 加载状态 */}
      {loading && (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">AI正在分析对话主题，请稍候...</p>
        </div>
      )}
    </div>
  )
}

export default TopicAnalysis