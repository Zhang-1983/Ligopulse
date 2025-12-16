import React, { useState, useEffect } from 'react';
import { 
  AreaChart, 
  Area, 
  BarChart, 
  Bar, 
  CartesianGrid, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer 
} from 'recharts';
import apiService from '../services/api';

const FutureDevelopmentAnalysis = ({ chatData }) => {
  const [activeView, setActiveView] = useState('overview');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [analysisData, setAnalysisData] = useState(null);

  // AI分析API调用
  useEffect(() => {
    if (chatData && chatData.messages && chatData.messages.length > 0) {
      fetchFutureDevelopmentAnalysis();
    }
  }, [chatData]);

  const fetchFutureDevelopmentAnalysis = async () => {
    if (!chatData || !chatData.messages) {
      setError('无效的对话数据');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // 构建标准的分析请求对象
      const analysisRequest = {
        scenario: chatData.scenario || '对话分析',
        dialogue: chatData.messages,
        llmProvider: chatData.llmProvider || 'default',
        analysis_options: {
          include_trend_prediction: true,
          include_risk_analysis: true,
          include_action_items: true,
          include_success_metrics: true
        }
      };

      console.log('🚀 开始未来发展预测分析...');
      console.log('📊 分析数据:', analysisRequest);

      // 调用AI未来发展预测API
      const result = await apiService.futureAnalysis(analysisRequest);

      console.log('✅ 未来发展预测分析完成:', result);
      
      // 验证响应数据
      if (!result || !result.data) {
        throw new Error('分析响应数据格式错误');
      }

      setAnalysisData(result);
    } catch (err) {
      console.error('未来发展预测分析失败:', err);
      setError(`未来发展预测分析失败: ${err.message}`);
      
      // 使用模拟数据作为备选
      setAnalysisData(getMockData());
    } finally {
      setLoading(false);
    }
  };

  // 数据标准化处理
  const processAnalysisData = (rawData) => {
    if (!rawData) return null;

    const {
      trendPrediction = [],
      riskPrediction = [],
      improvementSuggestions = [],
      outcomePossibilities = [],
      actionItems = [],
      successMetrics = []
    } = rawData;

    return {
      trendPrediction,
      riskPrediction,
      improvementSuggestions,
      outcomePossibilities,
      actionItems,
      successMetrics,
      summary: rawData.summary || {
        overallTrend: 'positive',
        keyInsights: [],
        recommendations: [],
        riskLevel: 'medium'
      }
    };
  };

  const processedData = processAnalysisData(analysisData?.data);

  // 获取优先级颜色
  const getPriorityColor = (priority) => {
    switch(priority?.toLowerCase()) {
      case '高': case 'high': return '#F44336';
      case '中': case 'medium': return '#FF9800';
      case '低': case 'low': return '#4CAF50';
      default: return '#9E9E9E';
    }
  };

  // 获取状态颜色
  const getStatusColor = (status) => {
    switch(status?.toLowerCase()) {
      case 'completed': case '已完成': return '#4CAF50';
      case 'in_progress': case '进行中': return '#2196F3';
      case 'pending': case '待执行': return '#FF9800';
      case 'overdue': case '已逾期': return '#F44336';
      default: return '#9E9E9E';
    }
  };

  // 获取趋势图标
  const getTrendIcon = (trend) => {
    switch(trend?.toLowerCase()) {
      case '上升': case 'increase': case 'positive': return '📈';
      case '下降': case 'decrease': case 'negative': return '📉';
      case '稳定': case 'stable': case 'neutral': return '➡️';
      default: return '➡️';
    }
  };

  // 渲染加载状态
  if (loading) {
    return (
      <div className="future-development-analysis">
        <div className="analysis-header">
          <h3 className="analysis-title">🚀 后续发展方向预测</h3>
          <div className="loading-indicator">
            <div className="loading-spinner"></div>
            <span>正在分析未来发展趋势...</span>
          </div>
        </div>
      </div>
    );
  }

  // 渲染错误状态
  if (error) {
    return (
      <div className="future-development-analysis">
        <div className="analysis-header">
          <h3 className="analysis-title">🚀 后续发展方向预测</h3>
        </div>
        <div className="error-message">
          <span className="error-icon">⚠️</span>
          <span>{error}</span>
          <button onClick={fetchFutureDevelopmentAnalysis} className="retry-button">
            重试
          </button>
        </div>
      </div>
    );
  }

  // 渲染无数据状态
  if (!processedData) {
    return (
      <div className="future-development-analysis">
        <div className="analysis-header">
          <h3 className="analysis-title">🚀 后续发展方向预测</h3>
        </div>
        <div className="no-data-message">
          <span className="no-data-icon">📊</span>
          <span>暂无未来发展预测数据</span>
        </div>
      </div>
    );
  }

  const { trendPrediction = [], riskPrediction = [], improvementSuggestions = [], outcomePossibilities = [], actionItems = [], successMetrics = [], summary = {} } = processedData;

  // 转换数据为图表格式
  const chartData = trendPrediction.length > 0 ? trendPrediction.map(item => ({
    period: item.period || item.month,
    协作度: (item.collaborationTrend || item.collaboration) * 100,
    生产力: (item.productivityTrend || item.productivity) * 100,
    满意度: (item.satisfactionTrend || item.satisfaction) * 100
  })) : [];

  const outcomeChartData = outcomePossibilities.map(item => ({
    outcome: item.outcome || item.result,
    probability: item.probability || item.prob
  }));

  return (
    <div className="future-development-analysis">
      <div className="analysis-header">
        <h3 className="analysis-title">🚀 后续发展方向预测</h3>
        <div className="view-switcher">
          {[
            { key: 'overview', label: '概览', icon: '📊' },
            { key: 'trends', label: '趋势分析', icon: '📈' },
            { key: 'risks', label: '风险预测', icon: '⚠️' },
            { key: 'actions', label: '行动项目', icon: '📋' }
          ].map(view => (
            <button
              key={view.key}
              onClick={() => setActiveView(view.key)}
              className={`view-button ${activeView === view.key ? 'active' : ''}`}
            >
              <span className="view-icon">{view.icon}</span>
              <span>{view.label}</span>
            </button>
          ))}
        </div>
        
        <div className="future-metrics">
          <div className="metric-card">
            <div className="metric-value">
              {summary.overallTrend ? 
                `${Math.round((successMetrics.reduce((sum, m) => sum + (m.current / m.target), 0) / successMetrics.length) * 100)}%` : 
                'N/A'
              }
            </div>
            <div className="metric-label">整体成功率预测</div>
          </div>
          <div className="metric-card">
            <div className="metric-value">{riskPrediction.length}</div>
            <div className="metric-label">识别风险数量</div>
          </div>
          <div className="metric-card">
            <div className="metric-value">{actionItems.length}</div>
            <div className="metric-label">待执行行动</div>
          </div>
        </div>
      </div>

      <div className="future-content">
        {/* 趋势分析 */}
        {(activeView === 'overview' || activeView === 'trends') && (
          <div className="trend-analysis-section">
            <h4>📈 发展趋势预测</h4>
            {chartData.length > 0 ? (
              <ResponsiveContainer width="100%" height={350}>
                <AreaChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="period" stroke="#666" />
                  <YAxis stroke="#666" />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: 'white', 
                      border: '1px solid #e0e0e0',
                      borderRadius: '8px'
                    }} 
                    formatter={(value) => [`${value.toFixed(1)}%`, '']}
                  />
                  <Area type="monotone" dataKey="协作度" stackId="1" stroke="#4CAF50" fill="#4CAF50" fillOpacity={0.3} />
                  <Area type="monotone" dataKey="生产力" stackId="1" stroke="#2196F3" fill="#2196F3" fillOpacity={0.3} />
                  <Area type="monotone" dataKey="满意度" stackId="1" stroke="#FF9800" fill="#FF9800" fillOpacity={0.3} />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="chart-placeholder">
                <span>暂无趋势数据</span>
              </div>
            )}

            <div className="trend-insights">
              {summary.keyInsights?.map((insight, index) => (
                <div key={index} className="insight-item">
                  <span className="insight-icon">💡</span>
                  <span className="insight-text">{insight}</span>
                </div>
              )) || [
                <div key="default-1" className="insight-item">
                  <span className="insight-icon">💡</span>
                  <span className="insight-text">
                    基于当前数据预测未来发展趋势
                  </span>
                </div>
              ]}
            </div>
          </div>
        )}

        {/* 风险预警 */}
        {(activeView === 'overview' || activeView === 'risks') && (
          <div className="risk-prediction-section">
            <h4>⚠️ 风险预警与缓解策略</h4>
            <div className="risk-list">
              {riskPrediction.length > 0 ? riskPrediction.map((risk, index) => (
                <div key={index} className="risk-item">
                  <div className="risk-header">
                    <div className="risk-title">{risk.risk || risk.description}</div>
                    <div className="risk-timeline">{risk.timeline || risk.timeframe}</div>
                  </div>
                  
                  <div className="risk-metrics">
                    <div className="risk-metric">
                      <span className="metric-label">发生概率:</span>
                      <span 
                        className="metric-value probability"
                        style={{ 
                          color: (risk.probability || 0) > 0.7 ? '#F44336' : 
                                (risk.probability || 0) > 0.4 ? '#FF9800' : '#4CAF50' 
                        }}
                      >
                        {((risk.probability || 0) * 100).toFixed(0)}%
                      </span>
                      <div className="risk-bar">
                        <div 
                          className="risk-fill probability" 
                          style={{ 
                            width: `${(risk.probability || 0) * 100}%`,
                            backgroundColor: (risk.probability || 0) > 0.7 ? '#F44336' : 
                                          (risk.probability || 0) > 0.4 ? '#FF9800' : '#4CAF50'
                          }}
                        ></div>
                      </div>
                    </div>
                    
                    <div className="risk-metric">
                      <span className="metric-label">影响程度:</span>
                      <span 
                        className="metric-value impact"
                        style={{ 
                          color: (risk.impact || 0) > 0.7 ? '#F44336' : 
                                (risk.impact || 0) > 0.4 ? '#FF9800' : '#4CAF50' 
                        }}
                      >
                        {((risk.impact || 0) * 100).toFixed(0)}%
                      </span>
                      <div className="risk-bar">
                        <div 
                          className="risk-fill impact" 
                          style={{ 
                            width: `${(risk.impact || 0) * 100}%`,
                            backgroundColor: (risk.impact || 0) > 0.7 ? '#F44336' : 
                                          (risk.impact || 0) > 0.4 ? '#FF9800' : '#4CAF50'
                          }}
                        ></div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="risk-mitigation">
                    <span className="mitigation-label">缓解策略:</span>
                    <span className="mitigation-text">{risk.mitigation || risk.solution}</span>
                  </div>
                </div>
              )) : <div className="empty-message">暂无风险数据</div>}
            </div>
          </div>
        )}

        {/* 改善建议与实施路径 */}
        {(activeView === 'overview' || activeView === 'trends') && (
          <div className="improvement-suggestions-section">
            <h4>💡 改善建议与实施路径</h4>
            <div className="suggestions-list">
              {improvementSuggestions.length > 0 ? improvementSuggestions.map((suggestion, index) => (
                <div key={index} className="suggestion-item">
                  <div className="suggestion-header">
                    <div className="suggestion-title">{suggestion.title || suggestion.suggestion}</div>
                    <div 
                      className="suggestion-priority"
                      style={{ backgroundColor: getPriorityColor(suggestion.priority) }}
                    >
                      {suggestion.priority}优先级
                    </div>
                  </div>
                  
                  <div className="suggestion-category">
                    <span className="category-label">类别:</span>
                    <span className="category-value">{suggestion.category}</span>
                  </div>
                  
                  <div className="suggestion-description">{suggestion.description}</div>
                  
                  <div className="suggestion-metrics">
                    <div className="suggestion-metric">
                      <span className="metric-label">预期影响:</span>
                      <div className="impact-bar">
                        <div 
                          className="impact-fill" 
                          style={{ width: `${(suggestion.impact || 0) * 100}%` }}
                        ></div>
                      </div>
                      <span className="metric-value">{((suggestion.impact || 0) * 100).toFixed(0)}%</span>
                    </div>
                    
                    <div className="suggestion-metric">
                      <span className="metric-label">实施难度:</span>
                      <div className="effort-bar">
                        <div 
                          className="effort-fill" 
                          style={{ width: `${(suggestion.effort || 0) * 100}%` }}
                        ></div>
                      </div>
                      <span className="metric-value">{((suggestion.effort || 0) * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                  
                  <div className="suggestion-implementation">
                    <span className="implementation-label">实施时间:</span>
                    <span className="implementation-value">{suggestion.implementation || suggestion.timeline}</span>
                  </div>
                  
                  <div className="suggestion-outcome">
                    <span className="outcome-label">预期结果:</span>
                    <span className="outcome-value">{suggestion.expectedOutcome || suggestion.outcome}</span>
                  </div>
                </div>
              )) : <div className="empty-message">暂无改善建议</div>}
            </div>
          </div>
        )}

        {/* 潜在结果分析 */}
        {activeView === 'overview' && (
          <div className="potential-outcomes-section">
            <h4>🎯 潜在结果可能性分析</h4>
            {outcomeChartData.length > 0 ? (
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={outcomeChartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="outcome" stroke="#666" angle={-45} textAnchor="end" height={80} />
                  <YAxis stroke="#666" />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: 'white', 
                      border: '1px solid #e0e0e0',
                      borderRadius: '8px'
                    }} 
                    formatter={(value) => [`${(value * 100).toFixed(1)}%`, '概率']}
                  />
                  <Bar dataKey="probability" fill="#4CAF50" name="发生概率" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="chart-placeholder">
                <span>暂无结果数据</span>
              </div>
            )}

            <div className="outcomes-details">
              {outcomePossibilities.map((outcome, index) => (
                <div key={index} className="outcome-item">
                  <div className="outcome-header">
                    <div className="outcome-title">{outcome.outcome || outcome.result}</div>
                    <div 
                      className="outcome-probability"
                      style={{ 
                        color: (outcome.probability || 0) > 0.6 ? '#4CAF50' : 
                              (outcome.probability || 0) > 0.3 ? '#FF9800' : '#F44336' 
                      }}
                    >
                      概率: {((outcome.probability || 0) * 100).toFixed(0)}%
                    </div>
                  </div>
                  
                  <div className="outcome-content">
                    <div className="outcome-benefits">
                      <span className="benefits-label">💚 潜在收益:</span>
                      <span className="benefits-text">{outcome.benefits}</span>
                    </div>
                    <div className="outcome-challenges">
                      <span className="challenges-label">⚠️ 潜在挑战:</span>
                      <span className="challenges-text">{outcome.challenges}</span>
                    </div>
                    <div className="outcome-preparation">
                      <span className="preparation-label">🎯 准备建议:</span>
                      <span className="preparation-text">{outcome.preparation}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 行动项目 */}
        {(activeView === 'overview' || activeView === 'actions') && (
          <div className="action-items-section">
            <h4>📋 待执行行动项目</h4>
            <div className="action-items-list">
              {actionItems.length > 0 ? actionItems.map((action, index) => (
                <div key={index} className="action-item">
                  <div className="action-header">
                    <div className="action-title">{action.action || action.task}</div>
                    <div 
                      className="action-priority"
                      style={{ backgroundColor: getPriorityColor(action.priority) }}
                    >
                      {action.priority}
                    </div>
                  </div>
                  
                  <div className="action-details">
                    <div className="action-owner">
                      <span className="owner-label">负责人:</span>
                      <span className="owner-value">{action.owner}</span>
                    </div>
                    <div className="action-deadline">
                      <span className="deadline-label">截止时间:</span>
                      <span className="deadline-value">{action.deadline || action.dueDate}</span>
                    </div>
                  </div>
                  
                  <div className="action-status">
                    <span className="status-label">状态:</span>
                    <span 
                      className="status-value"
                      style={{ color: getStatusColor(action.status) }}
                    >
                      {action.status === 'pending' || action.status === '待执行' ? '待执行' : 
                       action.status === 'in_progress' || action.status === '进行中' ? '进行中' : 
                       action.status === 'completed' || action.status === '已完成' ? '已完成' : 
                       action.status === 'overdue' || action.status === '已逾期' ? '已逾期' : action.status}
                    </span>
                  </div>
                </div>
              )) : <div className="empty-message">暂无行动项目</div>}
            </div>
          </div>
        )}

        {/* 成功指标 */}
        {activeView === 'overview' && (
          <div className="success-metrics-section">
            <h4>📊 成功指标跟踪</h4>
            <div className="metrics-list">
              {successMetrics.length > 0 ? successMetrics.map((metric, index) => (
                <div key={index} className="metric-item">
                  <div className="metric-header">
                    <div className="metric-name">{metric.metric || metric.name}</div>
                    <div className="metric-trend">
                      <span className="trend-icon">{getTrendIcon(metric.trend)}</span>
                      <span className="trend-text">{metric.trend}</span>
                    </div>
                  </div>
                  
                  <div className="metric-progress">
                    <div className="progress-bars">
                      <div className="progress-item">
                        <span className="progress-label">当前</span>
                        <div className="progress-bar">
                          <div 
                            className="progress-fill current" 
                            style={{ width: `${(metric.current || 0) * 100}%` }}
                          ></div>
                        </div>
                        <span className="progress-value">{((metric.current || 0) * 100).toFixed(0)}%</span>
                      </div>
                      
                      <div className="progress-item">
                        <span className="progress-label">目标</span>
                        <div className="progress-bar">
                          <div 
                            className="progress-fill target" 
                            style={{ width: `${(metric.target || 0) * 100}%` }}
                          ></div>
                        </div>
                        <span className="progress-value">{((metric.target || 0) * 100).toFixed(0)}%</span>
                      </div>
                    </div>
                    
                    <div className="progress-gap">
                      <span className="gap-label">差距:</span>
                      <span 
                        className="gap-value"
                        style={{ 
                          color: ((metric.target || 0) - (metric.current || 0)) > 0.2 ? '#F44336' : '#4CAF50' 
                        }}
                      >
                        {(((metric.target || 0) - (metric.current || 0)) * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                </div>
              )) : <div className="empty-message">暂无成功指标数据</div>}
            </div>
          </div>
        )}

        {/* 预测总结 */}
        {activeView === 'overview' && (
          <div className="prediction-summary">
            <h4>🎯 发展预测总结</h4>
            <div className="summary-content">
              {summary.recommendations?.map((rec, index) => (
                <div key={`rec-${index}`} className="summary-item action">
                  <span className="summary-icon">🚀</span>
                  <span className="summary-text">{rec}</span>
                </div>
              )) || [
                <div key="default-1" className="summary-item positive">
                  <span className="summary-icon">✅</span>
                  <span className="summary-text">
                    基于当前数据，分析未来发展趋势和潜在风险
                  </span>
                </div>
              ]}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default FutureDevelopmentAnalysis;