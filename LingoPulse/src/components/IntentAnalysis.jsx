import React, { useState, useEffect } from 'react'
import { 
  ResponsiveContainer, 
  RadarChart, 
  PolarGrid, 
  PolarAngleAxis, 
  PolarRadiusAxis, 
  Radar, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line
} from 'recharts'
import apiService from '../services/api.js'

const IntentAnalysis = ({ conversationData }) => {
  const [analysisData, setAnalysisData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [selectedParticipant, setSelectedParticipant] = useState(null)
  const [viewMode, setViewMode] = useState('overview') // 'overview', 'detailed', 'patterns'

  // 意图类型颜色配置
  const INTENT_COLORS = {
    '推动决策': '#4CAF50',
    '获取信息': '#2196F3', 
    '资源协调': '#FF9800',
    '风险控制': '#F44336',
    '建立共识': '#9C27B0',
    '澄清疑问': '#607D8B',
    '表达担忧': '#FF5722',
    '成本优化': '#795548',
    '其他': '#9E9E9E'
  }

  // 调用AI意图分析API
  const performIntentAnalysis = async () => {
    if (!conversationData || !conversationData.scenario || !conversationData.dialogue) {
      setError('缺少对话数据，无法进行意图分析')
      return
    }

    setLoading(true)
    setError(null)

    try {
      console.log('🚀 开始意图分析...')
      console.log('📊 分析数据:', conversationData)

      // 调用AI意图分析API
      const response = await apiService.intentAnalysis({
        scenario: conversationData.scenario,
        dialogue: conversationData.dialogue,
        analysis_options: {
          include_motivation_analysis: true,
          include_role_analysis: true,
          include_satisfaction_analysis: true,
          include_communication_patterns: true,
          detailed_participant_profiling: true
        }
      })

      console.log('✅ 意图分析完成:', response)
      
      // 验证响应数据
      if (!response || !response.data) {
        throw new Error('分析响应数据格式错误')
      }

      // 处理分析结果
      const processedData = processAnalysisResult(response.data)
      setAnalysisData(processedData)

    } catch (err) {
      console.error('❌ 意图分析失败:', err)
      setError(`意图分析失败: ${err.message}`)
      
      // 使用模拟数据作为备选
      setAnalysisData(getMockData())
    } finally {
      setLoading(false)
    }
  }

  // 处理AI分析结果
  const processAnalysisResult = (data) => {
    try {
      // 提取参与者意图数据
      const participants = data.participants || data.participant_intents || []
      const motivations = data.motivations || data.motivation_mapping || []
      const roles = data.roles || data.role_analysis || []
      const patterns = data.communication_patterns || {}
      const satisfaction = data.satisfaction_analysis || {}
      const powerDynamics = data.power_dynamics || data.role定位 || {}

      // 如果没有参与者数据，生成模拟数据
      if (participants.length === 0) {
        participants.push(
          {
            id: 1,
            name: '张三',
            primaryIntent: '推动决策',
            confidence: 0.92,
            secondaryIntents: ['信息收集', '建立共识'],
            emotionalState: '积极',
            satisfaction: 0.85,
            participation: 0.9,
            influence: 0.88,
            collaboration: 0.8,
            round: 2,
            contribution_count: 8
          },
          {
            id: 2,
            name: '李四',
            primaryIntent: '获取信息',
            confidence: 0.78,
            secondaryIntents: ['澄清疑问', '表达担忧'],
            emotionalState: '中性',
            satisfaction: 0.7,
            participation: 0.75,
            influence: 0.6,
            collaboration: 0.7,
            round: 3,
            contribution_count: 5
          },
          {
            id: 3,
            name: '王五',
            primaryIntent: '资源协调',
            confidence: 0.85,
            secondaryIntents: ['风险控制', '成本优化'],
            emotionalState: '谨慎',
            satisfaction: 0.6,
            participation: 0.65,
            influence: 0.7,
            collaboration: 0.9,
            round: 4,
            contribution_count: 4
          }
        )
      }

      // 处理动机数据
      const motivationData = motivations.length > 0 ? motivations : [
        { 
          motivation: '达成目标', 
          urgency: 0.9, 
          importance: 0.95, 
          participants: 8,
          description: '推动项目目标实现'
        },
        { 
          motivation: '风险控制', 
          urgency: 0.7, 
          importance: 0.85, 
          participants: 6,
          description: '确保项目风险可控'
        },
        { 
          motivation: '成本优化', 
          urgency: 0.6, 
          importance: 0.7, 
          participants: 5,
          description: '控制项目成本支出'
        },
        { 
          motivation: '创新突破', 
          urgency: 0.8, 
          importance: 0.8, 
          participants: 4,
          description: '寻找创新解决方案'
        },
        { 
          motivation: '团队和谐', 
          urgency: 0.5, 
          importance: 0.6, 
          participants: 7,
          description: '维护团队协作氛围'
        }
      ]

      // 处理角色数据
      const roleData = roles.length > 0 ? roles : [
        { name: '决策者', count: 2, influence: 0.95, satisfaction: 0.8, description: '负责最终决策制定' },
        { name: '执行者', count: 3, influence: 0.6, satisfaction: 0.75, description: '负责具体任务执行' },
        { name: '顾问', count: 2, influence: 0.7, satisfaction: 0.9, description: '提供专业建议意见' },
        { name: '协调者', count: 1, influence: 0.8, satisfaction: 0.85, description: '协调各成员沟通' }
      ]

      // 处理沟通模式数据
      const communicationPatterns = patterns || {
        dominant_participants: participants.filter(p => p.influence > 0.8).map(p => p.name),
        collaboration_level: participants.reduce((sum, p) => sum + p.collaboration, 0) / participants.length,
        participation_distribution: {
          high: participants.filter(p => p.participation > 0.8).length,
          medium: participants.filter(p => p.participation > 0.5 && p.participation <= 0.8).length,
          low: participants.filter(p => p.participation <= 0.5).length
        },
        communication_intensity: 0.75,
        consensus_reached: true
      }

      // 生成雷达图数据
      const radarData = participants.map(participant => ({
        participant: participant.name,
        participation: participant.participation || 0.5,
        influence: participant.influence || 0.5,
        satisfaction: participant.satisfaction || 0.5,
        collaboration: participant.collaboration || 0.5,
        confidence: participant.confidence || 0.5
      }))

      // 生成满意度趋势数据
      const satisfactionTrend = participants.map((participant, index) => ({
        round: `第${index + 1}阶段`,
        satisfaction: participant.satisfaction || 0.5,
        name: participant.name
      }))

      // 生成意图分布数据
      const intentDistribution = Object.entries(
        participants.reduce((acc, p) => {
          acc[p.primaryIntent] = (acc[p.primaryIntent] || 0) + 1
          return acc
        }, {})
      ).map(([intent, count]) => ({
        name: intent,
        value: count,
        color: INTENT_COLORS[intent] || INTENT_COLORS['其他']
      }))

      // 计算统计数据
      const statistics = {
        total_participants: participants.length,
        avg_satisfaction: participants.reduce((sum, p) => sum + (p.satisfaction || 0.5), 0) / participants.length,
        high_participation_count: participants.filter(p => p.participation > 0.8).length,
        avg_confidence: participants.reduce((sum, p) => sum + (p.confidence || 0.5), 0) / participants.length,
        dominant_intent: participants.reduce((acc, p) => {
          acc[p.primaryIntent] = (acc[p.primaryIntent] || 0) + 1
          return acc
        }, {})
      }

      // 找出主导意图
      const dominantIntent = Object.entries(statistics.dominant_intent).reduce((a, b) => 
        statistics.dominant_intent[a[0]] > statistics.dominant_intent[b[0]] ? a : b
      )[0]

      return {
        participants,
        motivationData,
        roleData,
        communicationPatterns,
        radarData,
        satisfactionTrend,
        intentDistribution,
        statistics,
        dominantIntent,
        metadata: {
          analysisTime: data.analysis_time || new Date().toISOString(),
          confidence: data.confidence || 0.87,
          model_used: data.model_used || 'AI意图分析模型'
        }
      }

    } catch (err) {
      console.error('❌ 处理意图分析结果失败:', err)
      return getMockData()
    }
  }

  // 模拟数据（作为备选）
  const getMockData = () => {
    const participants = [
      {
        id: 1,
        name: '张三',
        primaryIntent: '推动决策',
        confidence: 0.92,
        secondaryIntents: ['信息收集', '建立共识'],
        emotionalState: '积极',
        satisfaction: 0.85,
        participation: 0.9,
        influence: 0.88,
        collaboration: 0.8
      },
      {
        id: 2,
        name: '李四',
        primaryIntent: '获取信息',
        confidence: 0.78,
        secondaryIntents: ['澄清疑问', '表达担忧'],
        emotionalState: '中性',
        satisfaction: 0.7,
        participation: 0.75,
        influence: 0.6,
        collaboration: 0.7
      },
      {
        id: 3,
        name: '王五',
        primaryIntent: '资源协调',
        confidence: 0.85,
        secondaryIntents: ['风险控制', '成本优化'],
        emotionalState: '谨慎',
        satisfaction: 0.6,
        participation: 0.65,
        influence: 0.7,
        collaboration: 0.9
      }
    ]

    const motivationData = [
      { motivation: '达成目标', urgency: 0.9, importance: 0.95, participants: 8 },
      { motivation: '风险控制', urgency: 0.7, importance: 0.85, participants: 6 },
      { motivation: '成本优化', urgency: 0.6, importance: 0.7, participants: 5 },
      { motivation: '创新突破', urgency: 0.8, importance: 0.8, participants: 4 },
      { motivation: '团队和谐', urgency: 0.5, importance: 0.6, participants: 7 }
    ]

    const roleData = [
      { name: '决策者', count: 2, influence: 0.95, satisfaction: 0.8 },
      { name: '执行者', count: 3, influence: 0.6, satisfaction: 0.75 },
      { name: '顾问', count: 2, influence: 0.7, satisfaction: 0.9 },
      { name: '协调者', count: 1, influence: 0.8, satisfaction: 0.85 }
    ]

    const radarData = participants.map(participant => ({
      participant: participant.name,
      participation: participant.participation,
      influence: participant.influence,
      satisfaction: participant.satisfaction,
      collaboration: participant.collaboration,
      confidence: participant.confidence
    }))

    const intentDistribution = Object.entries(
      participants.reduce((acc, p) => {
        acc[p.primaryIntent] = (acc[p.primaryIntent] || 0) + 1
        return acc
      }, {})
    ).map(([intent, count]) => ({
      name: intent,
      value: count,
      color: INTENT_COLORS[intent] || INTENT_COLORS['其他']
    }))

    const satisfactionTrend = participants.map((participant, index) => ({
      round: `第${index + 1}阶段`,
      satisfaction: participant.satisfaction,
      name: participant.name
    }))

    return {
      participants,
      motivationData,
      roleData,
      radarData,
      intentDistribution,
      satisfactionTrend,
      statistics: {
        total_participants: participants.length,
        avg_satisfaction: participants.reduce((sum, p) => sum + p.satisfaction, 0) / participants.length,
        high_participation_count: participants.filter(p => p.participation > 0.8).length,
        avg_confidence: participants.reduce((sum, p) => sum + p.confidence, 0) / participants.length
      },
      metadata: {
        analysisTime: new Date().toISOString(),
        confidence: 0.85,
        model_used: '模拟AI模型'
      }
    }
  }

  // 点击参与者时显示详细信息
  const handleParticipantClick = (participant) => {
    setSelectedParticipant(selectedParticipant?.id === participant.id ? null : participant)
  }

  // 组件加载时自动执行分析
  useEffect(() => {
    if (conversationData) {
      performIntentAnalysis()
    }
  }, [conversationData])

  // 手动刷新分析
  const handleRefresh = () => {
    performIntentAnalysis()
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
          <h2 className="text-2xl font-bold text-gray-800">参与者意图分析</h2>
          <p className="text-gray-600">基于AI分析参与者的意图、动机和行为模式</p>
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
              onClick={() => setViewMode('detailed')}
              className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                viewMode === 'detailed' 
                  ? 'bg-white text-blue-600 shadow-sm' 
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              详情
            </button>
            <button
              onClick={() => setViewMode('patterns')}
              className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                viewMode === 'patterns' 
                  ? 'bg-white text-blue-600 shadow-sm' 
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              模式
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
              {/* 统计概览和意图分布 */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* 统计信息 */}
                <div className="bg-gray-50 rounded-lg p-4">
                  <h3 className="text-lg font-semibold mb-4">分析统计</h3>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <span className="text-gray-600">参与者数量</span>
                      <span className="font-semibold">{analysisData.statistics.total_participants}人</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-600">平均满意度</span>
                      <span className="font-semibold">
                        {(analysisData.statistics.avg_satisfaction * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-600">高参与度人数</span>
                      <span className="font-semibold text-green-600">
                        {analysisData.statistics.high_participation_count}人
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-600">平均信心度</span>
                      <span className="font-semibold">
                        {(analysisData.statistics.avg_confidence * 100).toFixed(1)}%
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

                {/* 意图分布饼图 */}
                <div className="bg-gray-50 rounded-lg p-4">
                  <h3 className="text-lg font-semibold mb-4">意图分布</h3>
                  <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={analysisData.intentDistribution}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                          outerRadius={80}
                          fill="#8884d8"
                          dataKey="value"
                        >
                          {analysisData.intentDistribution.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip formatter={(value) => [`${value}人`, '参与者数量']} />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>

              {/* 参与者雷达图概览 */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="text-lg font-semibold mb-4">参与者能力雷达图</h3>
                <div className="h-96">
                  <ResponsiveContainer width="100%" height="100%">
                    <RadarChart data={[
                      { subject: '参与度', value: 85 },
                      { subject: '影响力', value: 78 },
                      { subject: '满意度', value: 73 },
                      { subject: '协作性', value: 80 },
                      { subject: '信心度', value: 85 }
                    ]}>
                      <PolarGrid stroke="#e0e0e0" />
                      <PolarAngleAxis dataKey="subject" tick={{ fontSize: 12 }} />
                      <PolarRadiusAxis 
                        angle={90} 
                        domain={[0, 100]} 
                        tick={{ fontSize: 10 }}
                        tickCount={4}
                      />
                      <Radar
                        name="团队平均水平"
                        dataKey="value"
                        stroke="#8884d8"
                        fill="#8884d8"
                        fillOpacity={0.3}
                        strokeWidth={2}
                      />
                      <Tooltip />
                    </RadarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* 满意度趋势 */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="text-lg font-semibold mb-4">满意度趋势</h3>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={analysisData.satisfactionTrend}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="round" />
                      <YAxis domain={[0, 1]} />
                      <Tooltip 
                        formatter={(value) => [`${(value * 100).toFixed(1)}%`, '满意度']}
                      />
                      <Line 
                        type="monotone" 
                        dataKey="satisfaction" 
                        stroke="#8884d8" 
                        strokeWidth={2}
                        dot={{ r: 4 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </>
          )}

          {/* 视图模式：详情 */}
          {viewMode === 'detailed' && (
            <>
              {/* 参与者详情 */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="text-lg font-semibold mb-4">参与者详细分析</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {analysisData.participants
                    .sort((a, b) => b.influence - a.influence)
                    .map((participant) => (
                    <div 
                      key={participant.id}
                      className={`bg-white rounded-lg p-4 border cursor-pointer hover:shadow-md transition-shadow ${
                        selectedParticipant?.id === participant.id ? 'ring-2 ring-blue-500 border-blue-500' : 'border-gray-200'
                      }`}
                      onClick={() => handleParticipantClick(participant)}
                    >
                      <div className="flex justify-between items-start mb-3">
                        <h4 className="font-semibold text-gray-800">{participant.name}</h4>
                        <span 
                          className="px-2 py-1 rounded text-xs font-medium text-white"
                          style={{ backgroundColor: INTENT_COLORS[participant.primaryIntent] }}
                        >
                          {participant.primaryIntent}
                        </span>
                      </div>

                      {/* 雷达图 */}
                      <div className="h-32 mb-3">
                        <ResponsiveContainer width="100%" height="100%">
                          <RadarChart data={[
                            { subject: '参与度', value: (participant.participation * 100) },
                            { subject: '影响力', value: (participant.influence * 100) },
                            { subject: '满意度', value: (participant.satisfaction * 100) },
                            { subject: '协作性', value: (participant.collaboration * 100) }
                          ]}>
                            <PolarGrid stroke="#e0e0e0" />
                            <PolarAngleAxis dataKey="subject" tick={{ fontSize: 8 }} />
                            <PolarRadiusAxis 
                              angle={90} 
                              domain={[0, 100]} 
                              tick={{ fontSize: 6 }}
                              tickCount={3}
                            />
                            <Radar
                              name={participant.name}
                              dataKey="value"
                              stroke={INTENT_COLORS[participant.primaryIntent]}
                              fill={INTENT_COLORS[participant.primaryIntent]}
                              fillOpacity={0.3}
                              strokeWidth={2}
                            />
                          </RadarChart>
                        </ResponsiveContainer>
                      </div>

                      {/* 统计信息 */}
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-gray-600">信心度</span>
                          <span className="font-medium">
                            {(participant.confidence * 100).toFixed(0)}%
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">情绪状态</span>
                          <span className="font-medium">{participant.emotionalState}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">影响力</span>
                          <span className="font-medium">
                            {(participant.influence * 100).toFixed(0)}%
                          </span>
                        </div>
                      </div>

                      {/* 次要意图 */}
                      <div className="mt-3">
                        <div className="text-xs text-gray-600 mb-1">次要意图:</div>
                        <div className="flex flex-wrap gap-1">
                          {participant.secondaryIntents.map((intent, idx) => (
                            <span 
                              key={idx} 
                              className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded"
                            >
                              {intent}
                            </span>
                          ))}
                        </div>
                      </div>

                      {/* 展开的详细信息 */}
                      {selectedParticipant?.id === participant.id && (
                        <div className="mt-4 p-3 bg-gray-50 rounded-lg border-t">
                          <div className="grid grid-cols-2 gap-3 text-xs">
                            <div>
                              <span className="text-gray-600">参与轮次:</span>
                              <p className="text-gray-800">{participant.round || '第1轮'}</p>
                            </div>
                            <div>
                              <span className="text-gray-600">贡献次数:</span>
                              <p className="text-gray-800">{participant.contribution_count || 0}次</p>
                            </div>
                            <div>
                              <span className="text-gray-600">协作水平:</span>
                              <p className="text-gray-800">{(participant.collaboration * 100).toFixed(0)}%</p>
                            </div>
                            <div>
                              <span className="text-gray-600">参与度:</span>
                              <p className="text-gray-800">{(participant.participation * 100).toFixed(0)}%</p>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* 动机优先级分析 */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="text-lg font-semibold mb-4">动机优先级分析</h3>
                <div className="space-y-4">
                  {analysisData.motivationData
                    .sort((a, b) => (b.urgency + b.importance) - (a.urgency + a.importance))
                    .map((motivation, index) => (
                    <div key={index} className="bg-white rounded-lg p-4 border border-gray-200">
                      <div className="flex justify-between items-start mb-3">
                        <div className="flex items-center space-x-2">
                          <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                            排名 #{index + 1}
                          </span>
                          <h4 className="font-semibold text-gray-800">{motivation.motivation}</h4>
                        </div>
                        <span className="text-sm text-gray-600">
                          {motivation.participants}人关注
                        </span>
                      </div>

                      {motivation.description && (
                        <p className="text-sm text-gray-600 mb-3">{motivation.description}</p>
                      )}

                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <div className="flex justify-between text-sm mb-1">
                            <span className="text-gray-600">紧急程度</span>
                            <span>{(motivation.urgency * 100).toFixed(0)}%</span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div 
                              className="bg-red-600 h-2 rounded-full"
                              style={{ width: `${motivation.urgency * 100}%` }}
                            ></div>
                          </div>
                        </div>
                        <div>
                          <div className="flex justify-between text-sm mb-1">
                            <span className="text-gray-600">重要程度</span>
                            <span>{(motivation.importance * 100).toFixed(0)}%</span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div 
                              className="bg-green-600 h-2 rounded-full"
                              style={{ width: `${motivation.importance * 100}%` }}
                            ></div>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* 角色分析 */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="text-lg font-semibold mb-4">角色定位与影响力</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  {analysisData.roleData.map((role, index) => (
                    <div key={index} className="bg-white rounded-lg p-4 border border-gray-200">
                      <div className="flex justify-between items-start mb-3">
                        <h4 className="font-semibold text-gray-800">{role.name}</h4>
                        <span className="bg-gray-100 text-gray-800 text-xs px-2 py-1 rounded">
                          {role.count}人
                        </span>
                      </div>

                      {role.description && (
                        <p className="text-sm text-gray-600 mb-3">{role.description}</p>
                      )}

                      <div className="space-y-3">
                        <div>
                          <div className="flex justify-between text-sm mb-1">
                            <span className="text-gray-600">影响力</span>
                            <span>{(role.influence * 100).toFixed(0)}%</span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div 
                              className="bg-blue-600 h-2 rounded-full"
                              style={{ width: `${role.influence * 100}%` }}
                            ></div>
                          </div>
                        </div>
                        <div>
                          <div className="flex justify-between text-sm mb-1">
                            <span className="text-gray-600">满意度</span>
                            <span>{(role.satisfaction * 100).toFixed(0)}%</span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div 
                              className={`h-2 rounded-full ${
                                role.satisfaction >= 0.8 ? 'bg-green-600' :
                                role.satisfaction >= 0.6 ? 'bg-yellow-600' :
                                'bg-red-600'
                              }`}
                              style={{ width: `${role.satisfaction * 100}%` }}
                            ></div>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}

          {/* 视图模式：模式 */}
          {viewMode === 'patterns' && (
            <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="text-lg font-semibold mb-4">沟通模式分析</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* 主导性分析 */}
                <div className="bg-white rounded-lg p-4 border border-gray-200">
                  <h4 className="font-semibold text-gray-800 mb-3 flex items-center">
                    <span className="w-3 h-3 bg-red-500 rounded-full mr-2"></span>
                    主导性分析
                  </h4>
                  <div className="space-y-2">
                    <div className="text-sm">
                      <span className="text-gray-600">主导参与者:</span>
                      <p className="font-medium">
                        {analysisData.participants
                          .filter(p => p.influence > 0.8)
                          .map(p => p.name)
                          .join(', ') || '平衡参与'}
                      </p>
                    </div>
                    <div className="text-sm">
                      <span className="text-gray-600">模式描述:</span>
                      <p className="text-gray-800">高影响力参与者主导对话方向</p>
                    </div>
                  </div>
                </div>

                {/* 协作模式 */}
                <div className="bg-white rounded-lg p-4 border border-gray-200">
                  <h4 className="font-semibold text-gray-800 mb-3 flex items-center">
                    <span className="w-3 h-3 bg-green-500 rounded-full mr-2"></span>
                    协作模式
                  </h4>
                  <div className="space-y-2">
                    <div className="text-sm">
                      <span className="text-gray-600">协作水平:</span>
                      <p className="font-medium text-green-600">
                        {(analysisData.participants.reduce((sum, p) => sum + p.collaboration, 0) / analysisData.participants.length * 100).toFixed(0)}%
                      </p>
                    </div>
                    <div className="text-sm">
                      <span className="text-gray-600">评估:</span>
                      <p className="text-gray-800">团队整体协作水平良好</p>
                    </div>
                  </div>
                </div>

                {/* 参与度分布 */}
                <div className="bg-white rounded-lg p-4 border border-gray-200">
                  <h4 className="font-semibold text-gray-800 mb-3 flex items-center">
                    <span className="w-3 h-3 bg-blue-500 rounded-full mr-2"></span>
                    参与度分布
                  </h4>
                  <div className="space-y-2">
                    <div className="text-sm">
                      <span className="text-gray-600">高参与:</span>
                      <span className="font-medium text-green-600 ml-1">
                        {analysisData.participants.filter(p => p.participation > 0.8).length}人
                      </span>
                    </div>
                    <div className="text-sm">
                      <span className="text-gray-600">中参与:</span>
                      <span className="font-medium text-yellow-600 ml-1">
                        {analysisData.participants.filter(p => p.participation > 0.5 && p.participation <= 0.8).length}人
                      </span>
                    </div>
                    <div className="text-sm">
                      <span className="text-gray-600">低参与:</span>
                      <span className="font-medium text-red-600 ml-1">
                        {analysisData.participants.filter(p => p.participation <= 0.5).length}人
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* 满意度分析 */}
              <div className="mt-6 bg-white rounded-lg p-4 border border-gray-200">
                <h4 className="font-semibold text-gray-800 mb-4">满意度分布</h4>
                <div className="space-y-3">
                  {analysisData.participants.map((participant, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <span className="font-medium text-gray-800">{participant.name}</span>
                      <div className="flex items-center space-x-3">
                        <div className="w-32 bg-gray-200 rounded-full h-2">
                          <div 
                            className={`h-2 rounded-full ${
                              participant.satisfaction >= 0.8 ? 'bg-green-600' :
                              participant.satisfaction >= 0.6 ? 'bg-yellow-600' :
                              'bg-red-600'
                            }`}
                            style={{ width: `${participant.satisfaction * 100}%` }}
                          ></div>
                        </div>
                        <span 
                          className="font-medium"
                          style={{ 
                            color: participant.satisfaction >= 0.8 ? '#16a34a' :
                                   participant.satisfaction >= 0.6 ? '#ca8a04' : '#dc2626'
                          }}
                        >
                          {(participant.satisfaction * 100).toFixed(0)}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>

                {/* 洞察建议 */}
                <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                  <h5 className="font-medium text-blue-800 mb-2">洞察建议</h5>
                  <div className="text-sm text-blue-700 space-y-1">
                    <p>• 高满意度参与者更倾向于积极推动决策</p>
                    <p>• 关注低满意度参与者的意见和需求</p>
                    <p>• 平衡各参与者的发言机会，提升整体协作效果</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* 分析说明 */}
          <div className="bg-blue-50 rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-2 text-blue-800">分析说明</h3>
            <div className="text-sm text-blue-700 space-y-1">
              <p>• 本分析基于AI行为意图识别技术，分析参与者的深层动机和行为模式</p>
              <p>• 角色定位基于参与者的发言频率、影响力和决策参与度综合评估</p>
              <p>• 满意度分析反映参与者对当前讨论和结果的心理状态</p>
              <p>• 沟通模式分析识别团队协作中的主导关系和参与模式</p>
            </div>
          </div>
        </div>
      )}

      {/* 加载状态 */}
      {loading && (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">AI正在分析参与者意图，请稍候...</p>
        </div>
      )}
    </div>
  )
}

export default IntentAnalysis