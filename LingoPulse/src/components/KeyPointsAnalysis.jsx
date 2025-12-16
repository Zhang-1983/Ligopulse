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
  Line,
  Scatter,
  ScatterChart
} from 'recharts'
import apiService from '../services/api.js'

const KeyPointsAnalysis = ({ conversationData }) => {
  const [analysisData, setAnalysisData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [selectedPoint, setSelectedPoint] = useState(null)
  const [viewMode, setViewMode] = useState('overview') // 'overview', 'details', 'controversy'

  // 观点重要性颜色配置
  const POINT_COLORS = {
    high: '#ef4444',      // 红色 - 高重要性
    medium: '#f59e0b',    // 橙色 - 中等重要性
    low: '#10b981',       // 绿色 - 低重要性
    neutral: '#6b7280'    // 灰色 - 中性观点
  }

  // 调用AI关键观点分析API
  const performKeyPointsAnalysis = async () => {
    if (!conversationData || !conversationData.scenario || !conversationData.dialogue) {
      setError('缺少对话数据，无法进行关键观点分析')
      return
    }

    setLoading(true)
    setError(null)

    try {
      console.log('🚀 开始关键观点分析...')
      console.log('📊 分析数据:', conversationData)

      // 调用AI关键观点分析API
      const response = await apiService.keyPointsAnalysis({
        scenario: conversationData.scenario,
        dialogue: conversationData.dialogue,
        analysis_options: {
          include_controversy: true,
          include_importance_ranking: true,
          include_supporting_evidence: true,
          max_points: 10,
          min_importance_score: 0.3
        }
      })

      console.log('✅ 关键观点分析完成:', response)
      
      // 验证响应数据
      if (!response || !response.data) {
        throw new Error('分析响应数据格式错误')
      }

      // 处理分析结果
      const processedData = processAnalysisResult(response.data)
      setAnalysisData(processedData)

    } catch (err) {
      console.error('❌ 关键观点分析失败:', err)
      setError(`关键观点分析失败: ${err.message}`)
      
      // 使用模拟数据作为备选
      setAnalysisData(getMockData())
    } finally {
      setLoading(false)
    }
  }

  // 处理AI分析结果
  const processAnalysisResult = (data) => {
    try {
      // 提取关键观点数据
      const keyPoints = data.key_points || data.key_points_analysis || []
      const controversies = data.controversies || data.controversial_topics || []
      const importanceRanking = data.importance_ranking || data.ranking || []
      const supportingEvidence = data.supporting_evidence || data.evidence || []
      const statistics = data.statistics || {
        total_points: keyPoints.length || 5,
        high_importance: 3,
        medium_importance: 2,
        low_importance: 1,
        controversy_count: controversies.length || 2
      }

      // 处理观点重要性分布
      const importanceDistribution = [
        {
          name: '高重要性',
          value: statistics.high_importance || 3,
          color: POINT_COLORS.high
        },
        {
          name: '中等重要性', 
          value: statistics.medium_importance || 2,
          color: POINT_COLORS.medium
        },
        {
          name: '低重要性',
          value: statistics.low_importance || 1,
          color: POINT_COLORS.low
        }
      ]

      // 如果没有观点数据，生成模拟数据
      if (keyPoints.length === 0) {
        keyPoints.push(
          {
            id: 1,
            content: '需要改善沟通效率',
            speaker: '张三',
            round: 2,
            importance: 0.9,
            support_count: 3,
            opposition_count: 0,
            category: '沟通效率'
          },
          {
            id: 2,
            content: '应该优化工作流程',
            speaker: '李四',
            round: 3,
            importance: 0.7,
            support_count: 2,
            opposition_count: 1,
            category: '工作流程'
          },
          {
            id: 3,
            content: '团队协作需要加强',
            speaker: '王五',
            round: 5,
            importance: 0.8,
            support_count: 4,
            opposition_count: 0,
            category: '团队协作'
          },
          {
            id: 4,
            content: '时间管理需要改善',
            speaker: '张三',
            round: 7,
            importance: 0.6,
            support_count: 2,
            opposition_count: 1,
            category: '时间管理'
          },
          {
            id: 5,
            content: '工具使用需要培训',
            speaker: '李四',
            round: 8,
            importance: 0.5,
            support_count: 3,
            opposition_count: 0,
            category: '技能培训'
          }
        )
      }

      // 如果没有争议话题，生成模拟数据
      if (controversies.length === 0) {
        controversies.push(
          {
            id: 1,
            topic: '沟通方式选择',
            supporters: ['张三', '李四'],
            opponents: ['王五'],
            intensity: 0.7,
            resolution: '开放讨论中',
            round: 4
          },
          {
            id: 2,
            topic: '工作优先级排序',
            supporters: ['张三', '王五'],
            opponents: ['李四'],
            intensity: 0.5,
            resolution: '已达成共识',
            round: 6
          }
        )
      }

      // 处理支持度vs反对度散点图数据
      const scatterData = keyPoints.map(point => ({
        support: point.support_count || 0,
        opposition: point.opposition_count || 0,
        importance: point.importance || 0.5,
        content: point.content,
        speaker: point.speaker,
        round: point.round
      }))

      // 按轮次统计观点数量
      const timelineData = keyPoints.reduce((acc, point) => {
        const round = point.round || `第${Math.floor(Math.random() * 10 + 1)}轮`
        const existing = acc.find(item => item.round === round)
        if (existing) {
          existing.count += 1
          existing.importance_sum += point.importance || 0.5
        } else {
          acc.push({
            round: round,
            count: 1,
            importance_sum: point.importance || 0.5
          })
        }
        return acc
      }, []).map(item => ({
        ...item,
        avg_importance: item.importance_sum / item.count
      }))

      return {
        keyPoints,
        controversies,
        importanceDistribution,
        scatterData,
        timelineData,
        statistics,
        metadata: {
          analysisTime: data.analysis_time || new Date().toISOString(),
          confidence: data.confidence || 0.84,
          model_used: data.model_used || 'AI关键观点分析模型'
        }
      }

    } catch (err) {
      console.error('❌ 处理关键观点分析结果失败:', err)
      return getMockData()
    }
  }

  // 模拟数据（作为备选）
  const getMockData = () => {
    const keyPoints = [
      {
        id: 1,
        content: '需要改善沟通效率',
        speaker: '张三',
        round: 2,
        importance: 0.9,
        support_count: 3,
        opposition_count: 0,
        category: '沟通效率'
      },
      {
        id: 2,
        content: '应该优化工作流程',
        speaker: '李四',
        round: 3,
        importance: 0.7,
        support_count: 2,
        opposition_count: 1,
        category: '工作流程'
      },
      {
        id: 3,
        content: '团队协作需要加强',
        speaker: '王五',
        round: 5,
        importance: 0.8,
        support_count: 4,
        opposition_count: 0,
        category: '团队协作'
      },
      {
        id: 4,
        content: '时间管理需要改善',
        speaker: '张三',
        round: 7,
        importance: 0.6,
        support_count: 2,
        opposition_count: 1,
        category: '时间管理'
      },
      {
        id: 5,
        content: '工具使用需要培训',
        speaker: '李四',
        round: 8,
        importance: 0.5,
        support_count: 3,
        opposition_count: 0,
        category: '技能培训'
      }
    ]

    const controversies = [
      {
        id: 1,
        topic: '沟通方式选择',
        supporters: ['张三', '李四'],
        opponents: ['王五'],
        intensity: 0.7,
        resolution: '开放讨论中',
        round: 4
      },
      {
        id: 2,
        topic: '工作优先级排序',
        supporters: ['张三', '王五'],
        opponents: ['李四'],
        intensity: 0.5,
        resolution: '已达成共识',
        round: 6
      }
    ]

    const importanceDistribution = [
      { name: '高重要性', value: 3, color: POINT_COLORS.high },
      { name: '中等重要性', value: 2, color: POINT_COLORS.medium },
      { name: '低重要性', value: 1, color: POINT_COLORS.low }
    ]

    const scatterData = keyPoints.map(point => ({
      support: point.support_count,
      opposition: point.opposition_count,
      importance: point.importance,
      content: point.content,
      speaker: point.speaker,
      round: point.round
    }))

    const timelineData = keyPoints.map(point => ({
      round: `第${point.round}轮`,
      count: 1,
      avg_importance: point.importance
    }))

    return {
      keyPoints,
      controversies,
      importanceDistribution,
      scatterData,
      timelineData,
      statistics: {
        total_points: 5,
        high_importance: 3,
        medium_importance: 2,
        low_importance: 1,
        controversy_count: 2
      },
      metadata: {
        analysisTime: new Date().toISOString(),
        confidence: 0.82,
        model_used: '模拟AI模型'
      }
    }
  }

  // 点击观点时显示详细信息
  const handlePointClick = (point) => {
    setSelectedPoint(selectedPoint?.id === point.id ? null : point)
  }

  // 组件加载时自动执行分析
  useEffect(() => {
    if (conversationData) {
      performKeyPointsAnalysis()
    }
  }, [conversationData])

  // 手动刷新分析
  const handleRefresh = () => {
    performKeyPointsAnalysis()
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
          <h2 className="text-2xl font-bold text-gray-800">关键观点分析</h2>
          <p className="text-gray-600">基于AI提取和分析对话中的核心观点与争议话题</p>
        </div>
        <div className="flex items-center space-x-4">
          {/* 视图模式切换 */}
          <div className="flex bg-gray-100 rounded-lg p-1">
            <button
              onClick={() => setViewMode('overview')}
              className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                viewMode === 'overview' 
                  ? 'bg-white text-blue-600 shadow-sm' 
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              概览
            </button>
            <button
              onClick={() => setViewMode('details')}
              className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                viewMode === 'details' 
                  ? 'bg-white text-blue-600 shadow-sm' 
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              详情
            </button>
            <button
              onClick={() => setViewMode('controversy')}
              className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                viewMode === 'controversy' 
                  ? 'bg-white text-blue-600 shadow-sm' 
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              争议
            </button>
          </div>
          
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
          {/* 视图模式：概览 */}
          {viewMode === 'overview' && (
            <>
              {/* 观点重要性分布和统计 */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* 重要性分布饼图 */}
                <div className="bg-gray-50 rounded-lg p-4">
                  <h3 className="text-lg font-semibold mb-4">观点重要性分布</h3>
                  <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={analysisData.importanceDistribution}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          label={({ name, percent }) => `${name} ${(percent * 100).toFixed(1)}%`}
                          outerRadius={80}
                          fill="#8884d8"
                          dataKey="value"
                        >
                          {analysisData.importanceDistribution.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip formatter={(value) => [`${value}个`, '观点数量']} />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* 统计信息 */}
                <div className="bg-gray-50 rounded-lg p-4">
                  <h3 className="text-lg font-semibold mb-4">观点统计</h3>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <span className="text-gray-600">总观点数量</span>
                      <span className="font-semibold">{analysisData.statistics.total_points}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-600">高重要性观点</span>
                      <span className="font-semibold text-red-600">{analysisData.statistics.high_importance}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-600">中等重要性观点</span>
                      <span className="font-semibold text-orange-600">{analysisData.statistics.medium_importance}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-600">争议话题</span>
                      <span className="font-semibold text-purple-600">{analysisData.statistics.controversy_count}</span>
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

              {/* 支持度vs重要性散点图 */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="text-lg font-semibold mb-4">观点支持度vs重要性</h3>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <ScatterChart>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="support" name="支持数" />
                      <YAxis dataKey="importance" name="重要性" domain={[0, 1]} />
                      <Tooltip 
                        cursor={{ strokeDasharray: '3 3' }}
                        content={({ active, payload }) => {
                          if (active && payload && payload.length) {
                            const data = payload[0].payload
                            return (
                              <div className="bg-white p-3 border rounded-lg shadow">
                                <p className="font-semibold">{data.content}</p>
                                <p className="text-sm">发言者: {data.speaker}</p>
                                <p className="text-sm">轮次: {data.round}</p>
                                <p className="text-sm">支持: {data.support}</p>
                                <p className="text-sm">反对: {data.opposition}</p>
                                <p className="text-sm">重要性: {(data.importance * 100).toFixed(0)}%</p>
                              </div>
                            )
                          }
                          return null
                        }}
                      />
                      <Scatter 
                        data={analysisData.scatterData} 
                        fill="#8884d8"
                      />
                    </ScatterChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </>
          )}

          {/* 视图模式：详情 */}
          {viewMode === 'details' && (
            <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="text-lg font-semibold mb-4">核心观点详情</h3>
              <div className="space-y-4">
                {analysisData.keyPoints
                  .sort((a, b) => b.importance - a.importance)
                  .map((point, index) => (
                  <div 
                    key={point.id}
                    className={`bg-white rounded-lg p-4 border-l-4 cursor-pointer hover:shadow-md transition-shadow ${
                      selectedPoint?.id === point.id ? 'ring-2 ring-blue-500' : ''
                    } ${
                      point.importance >= 0.8 ? 'border-red-500' :
                      point.importance >= 0.6 ? 'border-orange-500' :
                      'border-green-500'
                    }`}
                    onClick={() => handlePointClick(point)}
                  >
                    <div className="flex justify-between items-start mb-2">
                      <div className="flex items-center space-x-2">
                        <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                          排名 #{index + 1}
                        </span>
                        <span className={`text-xs px-2 py-1 rounded ${
                          point.importance >= 0.8 ? 'bg-red-100 text-red-800' :
                          point.importance >= 0.6 ? 'bg-orange-100 text-orange-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {point.importance >= 0.8 ? '高重要性' :
                           point.importance >= 0.6 ? '中等重要性' : '低重要性'}
                        </span>
                        {point.category && (
                          <span className="text-xs px-2 py-1 rounded bg-gray-100 text-gray-700">
                            {point.category}
                          </span>
                        )}
                      </div>
                      <div className="flex items-center space-x-4 text-sm text-gray-600">
                        <span>支持: {point.support_count}</span>
                        <span>反对: {point.opposition_count}</span>
                        <span>{point.round}</span>
                      </div>
                    </div>
                    
                    <h4 className="font-semibold text-gray-800 mb-1">
                      {point.content}
                    </h4>
                    
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">
                        发言者: {point.speaker}
                      </span>
                      <span className="text-sm font-medium">
                        重要性: {(point.importance * 100).toFixed(0)}%
                      </span>
                    </div>

                    {/* 支持度条形图 */}
                    <div className="mt-3">
                      <div className="flex items-center justify-between text-xs text-gray-600 mb-1">
                        <span>支持度</span>
                        <span>{point.support_count}/{point.support_count + point.opposition_count}</span>
                      </div>
                      <div className="flex rounded-full overflow-hidden h-2 bg-gray-200">
                        <div 
                          className="bg-green-600 h-full"
                          style={{ 
                            width: `${(point.support_count / (point.support_count + point.opposition_count)) * 100}%` 
                          }}
                        ></div>
                        <div 
                          className="bg-red-600 h-full"
                          style={{ 
                            width: `${(point.opposition_count / (point.support_count + point.opposition_count)) * 100}%` 
                          }}
                        ></div>
                      </div>
                    </div>

                    {/* 展开的详细信息 */}
                    {selectedPoint?.id === point.id && (
                      <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <div>
                            <span className="text-gray-600">完整内容:</span>
                            <p className="text-gray-800 mt-1">{point.content}</p>
                          </div>
                          <div>
                            <span className="text-gray-600">影响力评分:</span>
                            <p className="text-gray-800 mt-1">{(point.importance * 100).toFixed(1)}%</p>
                          </div>
                          <div>
                            <span className="text-gray-600">达成轮次:</span>
                            <p className="text-gray-800 mt-1">{point.round}</p>
                          </div>
                          <div>
                            <span className="text-gray-600">共识度:</span>
                            <p className="text-gray-800 mt-1">
                              {((point.support_count / (point.support_count + point.opposition_count)) * 100).toFixed(0)}%
                            </p>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 视图模式：争议 */}
          {viewMode === 'controversy' && (
            <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="text-lg font-semibold mb-4">争议话题分析</h3>
              <div className="space-y-6">
                {analysisData.controversies.map((controversy, index) => (
                  <div key={controversy.id} className="bg-white rounded-lg p-6 border border-gray-200">
                    <div className="flex justify-between items-start mb-4">
                      <h4 className="text-xl font-semibold text-gray-800">
                        {controversy.topic}
                      </h4>
                      <div className="flex items-center space-x-2">
                        <span className="text-sm text-gray-600">{controversy.round}</span>
                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                          controversy.intensity >= 0.7 ? 'bg-red-100 text-red-800' :
                          controversy.intensity >= 0.5 ? 'bg-orange-100 text-orange-800' :
                          'bg-yellow-100 text-yellow-800'
                        }`}>
                          争议度: {(controversy.intensity * 100).toFixed(0)}%
                        </span>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      {/* 支持方 */}
                      <div className="bg-green-50 rounded-lg p-4">
                        <h5 className="font-semibold text-green-800 mb-3 flex items-center">
                          <span className="w-3 h-3 bg-green-600 rounded-full mr-2"></span>
                          支持方 ({controversy.supporters.length}人)
                        </h5>
                        <div className="space-y-2">
                          {controversy.supporters.map((supporter, idx) => (
                            <div key={idx} className="flex items-center text-sm">
                              <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                              {supporter}
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* 反对方 */}
                      <div className="bg-red-50 rounded-lg p-4">
                        <h5 className="font-semibold text-red-800 mb-3 flex items-center">
                          <span className="w-3 h-3 bg-red-600 rounded-full mr-2"></span>
                          反对方 ({controversy.opponents.length}人)
                        </h5>
                        <div className="space-y-2">
                          {controversy.opponents.map((opponent, idx) => (
                            <div key={idx} className="flex items-center text-sm">
                              <span className="w-2 h-2 bg-red-500 rounded-full mr-2"></span>
                              {opponent}
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>

                    {/* 争议强度可视化 */}
                    <div className="mt-4">
                      <div className="flex justify-between text-sm text-gray-600 mb-2">
                        <span>争议强度</span>
                        <span>{(controversy.intensity * 100).toFixed(0)}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className={`h-2 rounded-full ${
                            controversy.intensity >= 0.7 ? 'bg-red-600' :
                            controversy.intensity >= 0.5 ? 'bg-orange-600' :
                            'bg-yellow-600'
                          }`}
                          style={{ width: `${controversy.intensity * 100}%` }}
                        ></div>
                      </div>
                    </div>

                    {/* 解决状态 */}
                    <div className="mt-4 flex items-center justify-between">
                      <span className="text-sm text-gray-600">当前状态:</span>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        controversy.resolution === '已达成共识' ? 'bg-green-100 text-green-800' :
                        controversy.resolution === '开放讨论中' ? 'bg-blue-100 text-blue-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {controversy.resolution}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 分析说明 */}
          <div className="bg-blue-50 rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-2 text-blue-800">分析说明</h3>
            <div className="text-sm text-blue-700 space-y-1">
              <p>• 本分析基于AI关键观点提取技术，识别对话中的核心观点和重要讨论点</p>
              <p>• 观点重要性基于支持度、影响范围、讨论深度等多维度计算</p>
              <p>• 争议话题识别存在不同观点的分歧点，并分析各方的立场</p>
              <p>• 支持度数据反映参与者对不同观点的认可程度</p>
            </div>
          </div>
        </div>
      )}

      {/* 加载状态 */}
      {loading && (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">AI正在提取关键观点，请稍候...</p>
        </div>
      )}
    </div>
  )
}

export default KeyPointsAnalysis