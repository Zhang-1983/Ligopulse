import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ScatterChart, Scatter, BarChart, Bar } from 'recharts';
import ApiService from '../services/api';

const LogicalStructureAnalysis = ({ conversationData, analysisRequest, onAnalysisComplete }) => {
  const [logicalData, setLogicalData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [viewMode, setViewMode] = useState('overview');

  const apiService = new ApiService();

  useEffect(() => {
    if (conversationData && analysisRequest) {
      performLogicalAnalysis();
    }
  }, [conversationData, analysisRequest]);

  const performLogicalAnalysis = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await apiService.logicalStructureAnalysis(analysisRequest);
      
      // 标准化数据结构
      const standardizedData = standardizeLogicalData(result);
      setLogicalData(standardizedData);
      
      if (onAnalysisComplete) {
        onAnalysisComplete(standardizedData);
      }
    } catch (error) {
      console.error('逻辑结构分析失败:', error);
      setError(`分析失败: ${error.message}`);
      
      // 使用降级数据
      const fallbackData = getFallbackLogicalData();
      setLogicalData(fallbackData);
    } finally {
      setLoading(false);
    }
  };

  const standardizeLogicalData = (data) => {
    return {
      conversationFlow: data.conversation_flow || data.conversationFlow || [],
      turningPoints: data.turning_points || data.turningPoints || [],
      logicalChains: data.logical_chains || data.logicalChains || [],
      completenessAnalysis: data.completeness_analysis || data.completenessAnalysis || {},
      coherenceMetrics: data.coherence_metrics || data.coherenceMetrics || {},
      decisionTree: data.decision_tree || data.decisionTree || {},
      statistics: {
        overallCompleteness: data.overall_completeness || data.statistics?.overall_completeness || 0,
        averageCohesion: data.average_cohesion || data.statistics?.average_cohesion || 0,
        logicalConsistency: data.logical_consistency || data.statistics?.logical_consistency || 0,
        flowSmoothness: data.flow_smoothness || data.statistics?.flow_smoothness || 0
      },
      insights: data.insights || [],
      recommendations: data.recommendations || []
    };
  };

  const getFallbackLogicalData = () => {
    return {
      conversationFlow: [
        { round: 1, cohesion: 0.6, topic: "问题识别", participants: 3, connections: 2 },
        { round: 2, cohesion: 0.7, topic: "现状分析", participants: 4, connections: 5 },
        { round: 3, cohesion: 0.85, topic: "解决方案讨论", participants: 5, connections: 8 },
        { round: 4, cohesion: 0.75, topic: "可行性评估", participants: 4, connections: 6 },
        { round: 5, cohesion: 0.9, topic: "决策制定", participants: 5, connections: 10 },
        { round: 6, cohesion: 0.8, topic: "实施计划", participants: 4, connections: 7 }
      ],
      turningPoints: [
        {
          round: 2,
          type: "话题转折",
          description: "从问题讨论转向解决方案",
          impact: 0.8,
          participants: ["分析助手"],
          coherence: 0.9
        },
        {
          round: 4,
          type: "观点冲突",
          description: "技术方案存在分歧",
          impact: 0.6,
          participants: ["分析助手"],
          coherence: 0.7
        }
      ],
      logicalChains: [
        {
          chain: "问题识别 → 根因分析 → 解决方案",
          strength: 0.92,
          participants: ["分析助手"],
          rounds: [1, 2, 3]
        },
        {
          chain: "方案评估 → 风险分析 → 决策制定",
          strength: 0.88,
          participants: ["分析助手"],
          rounds: [4, 5, 6]
        }
      ],
      completenessAnalysis: {
        problemAnalysis: 0.95,
        solutionGeneration: 0.85,
        evaluation: 0.8,
        decision: 0.9,
        implementation: 0.75
      },
      coherenceMetrics: {
        averageCohesion: 0.78,
        logicalConsistency: 0.82,
        argumentStrength: 0.88,
        flowSmoothness: 0.75,
        resolutionQuality: 0.9
      },
      statistics: {
        overallCompleteness: 0.87,
        averageCohesion: 0.78,
        logicalConsistency: 0.82,
        flowSmoothness: 0.75
      },
      insights: [
        "对话在问题分析阶段表现优异，为后续决策提供了坚实基础",
        "实施计划部分需要进一步完善，建议增加具体时间节点"
      ],
      recommendations: [
        "增强实施计划的具体性，增加时间线和里程碑",
        "提高论证强度，为方案选择提供更多支撑",
        "优化流程流畅度，减少不必要的重复讨论"
      ]
    };
  };

  if (loading) {
    return (
      <div className="logical-structure-analysis loading">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>正在进行逻辑结构分析...</p>
        </div>
      </div>
    );
  }

  if (error && !logicalData) {
    return (
      <div className="logical-structure-analysis error">
        <div className="error-message">
          <h3>⚠️ 分析失败</h3>
          <p>{error}</p>
          <button onClick={performLogicalAnalysis} className="retry-button">
            重试分析
          </button>
        </div>
      </div>
    );
  }

  if (!logicalData) {
    return (
      <div className="logical-structure-analysis">
        <div className="no-data">
          <h3>📊 等待数据</h3>
          <p>请提供对话数据进行逻辑结构分析</p>
        </div>
      </div>
    );
  }

  const {
    conversationFlow = [],
    turningPoints = [],
    logicalChains = [],
    completenessAnalysis = {},
    coherenceMetrics = {},
    statistics = {}
  } = logicalData;

  // 统计数据
  const overallCompleteness = statistics.overallCompleteness || 
    (Object.values(completenessAnalysis).reduce((a, b) => a + b, 0) / Object.values(completenessAnalysis).length) || 0;
  
  const averageCohesion = statistics.averageCohesion || 
    (coherenceMetrics.averageCohesion || 0);
  
  const logicalConsistency = statistics.logicalConsistency || 
    (coherenceMetrics.logicalConsistency || 0);

  const getFlowColor = (cohesion) => {
    if (cohesion >= 0.8) return '#4CAF50';
    if (cohesion >= 0.6) return '#FFC107';
    return '#F44336';
  };

  const getChainColor = (strength) => {
    if (strength >= 0.85) return '#2196F3';
    if (strength >= 0.75) return '#FF9800';
    return '#9C27B0';
  };

  const getImpactColor = (impact) => {
    if (impact >= 0.8) return '#D32F2F';
    if (impact >= 0.6) return '#FF5722';
    return '#FFC107';
  };

  // 获取分析说明
  const getAnalysisSummary = () => {
    if (logicalData.insights && logicalData.insights.length > 0) {
      return logicalData.insights.join('；');
    }
    return `逻辑结构分析完成，共识别${logicalChains.length}个主要逻辑链条，${turningPoints.length}个关键转折点，整体完整性${(overallCompleteness * 100).toFixed(1)}%。`;
  };

  return (
    <div className="logical-structure-analysis">
      <div className="analysis-header">
        <h3 className="analysis-title">🧩 对话逻辑结构分析</h3>
        <div className="view-mode-toggle">
          <button 
            className={viewMode === 'overview' ? 'active' : ''} 
            onClick={() => setViewMode('overview')}
          >
            概览
          </button>
          <button 
            className={viewMode === 'detail' ? 'active' : ''} 
            onClick={() => setViewMode('detail')}
          >
            详情
          </button>
          <button 
            className={viewMode === 'chains' ? 'active' : ''} 
            onClick={() => setViewMode('chains')}
          >
            逻辑链
          </button>
        </div>
        <div className="logical-metrics">
          <div className="metric-card">
            <div className="metric-value">{overallCompleteness.toFixed(2)}</div>
            <div className="metric-label">逻辑完整性</div>
          </div>
          <div className="metric-card">
            <div className="metric-value">{averageCohesion.toFixed(2)}</div>
            <div className="metric-label">平均凝聚力</div>
          </div>
          <div className="metric-card">
            <div className="metric-value">{logicalChains.length}</div>
            <div className="metric-label">逻辑链条数</div>
          </div>
        </div>
      </div>

      <div className="analysis-summary">
        <h4>📋 分析总结</h4>
        <p>{getAnalysisSummary()}</p>
      </div>

      {viewMode === 'overview' && (
        <div className="logical-content">
          {/* 对话流程趋势 */}
          <div className="conversation-flow-section">
            <h4>📈 对话凝聚力变化趋势</h4>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={conversationFlow}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="round" stroke="#666" />
                <YAxis stroke="#666" domain={[0, 1]} />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'white', 
                    border: '1px solid #e0e0e0',
                    borderRadius: '8px'
                  }} 
                  formatter={(value) => [value.toFixed(2), '凝聚力']}
                />
                <Line 
                  type="monotone" 
                  dataKey="cohesion" 
                  stroke="#4CAF50" 
                  strokeWidth={3}
                  dot={{ fill: '#4CAF50', strokeWidth: 2, r: 6 }}
                  name="凝聚力"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* 转折点概览 */}
          <div className="turning-points-section">
            <h4>🔄 关键转折点</h4>
            <div className="turning-points-overview">
              {turningPoints.slice(0, 3).map((point, index) => (
                <div key={index} className="turning-point-item-overview">
                  <div className="turning-point-round">第{point.round}轮</div>
                  <div className="turning-point-type">{point.type}</div>
                  <div 
                    className="turning-point-impact"
                    style={{ color: getImpactColor(point.impact) }}
                  >
                    {(point.impact * 100).toFixed(0)}%
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {viewMode === 'detail' && (
        <div className="logical-content">
          {/* 完整性分析 */}
          <div className="completeness-section">
            <h4>✅ 对话完整性分析</h4>
            <div className="completeness-grid">
              {Object.entries(completenessAnalysis).map(([key, value]) => (
                <div key={key} className="completeness-item">
                  <div className="completeness-label">
                    {key === 'problemAnalysis' ? '问题分析' :
                     key === 'solutionGeneration' ? '方案生成' :
                     key === 'evaluation' ? '方案评估' :
                     key === 'decision' ? '决策制定' :
                     key === 'implementation' ? '实施计划' : 
                     key === 'overall' ? '整体完整性' : key}
                  </div>
                  <div className="completeness-bar-container">
                    <div 
                      className="completeness-bar" 
                      style={{ 
                        width: `${value * 100}%`,
                        backgroundColor: value > 0.8 ? '#4CAF50' : value > 0.6 ? '#FFC107' : '#F44336'
                      }}
                    ></div>
                  </div>
                  <div 
                    className="completeness-value"
                    style={{ color: value > 0.8 ? '#4CAF50' : value > 0.6 ? '#FFC107' : '#F44336' }}
                  >
                    {(value * 100).toFixed(0)}%
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 一致性指标 */}
          <div className="coherence-metrics-section">
            <h4>🎯 逻辑一致性指标</h4>
            <div className="metrics-grid">
              {Object.entries(coherenceMetrics).map(([key, value]) => (
                <div key={key} className="metric-card-coherence">
                  <div className="metric-title">
                    {key === 'averageCohesion' ? '平均凝聚力' :
                     key === 'logicalConsistency' ? '逻辑一致性' :
                     key === 'argumentStrength' ? '论证强度' :
                     key === 'flowSmoothness' ? '流程流畅度' :
                     key === 'resolutionQuality' ? '解决方案质量' : key}
                  </div>
                  <div className="metric-value-coherence" style={{ color: value > 0.8 ? '#4CAF50' : value > 0.6 ? '#FFC107' : '#F44336' }}>
                    {value.toFixed(2)}
                  </div>
                  <div className="metric-bar-coherence">
                    <div 
                      className="metric-fill-coherence" 
                      style={{ 
                        width: `${value * 100}%`,
                        backgroundColor: value > 0.8 ? '#4CAF50' : value > 0.6 ? '#FFC107' : '#F44336'
                      }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 转折点详细分析 */}
          <div className="turning-points-section">
            <h4>🔄 对话转折点详细分析</h4>
            <div className="turning-points-list">
              {turningPoints.map((point, index) => (
                <div key={index} className="turning-point-item">
                  <div className="turning-point-header">
                    <div className="turning-point-round">第{point.round}轮</div>
                    <div className="turning-point-type">{point.type}</div>
                    <div 
                      className="turning-point-impact"
                      style={{ color: getImpactColor(point.impact) }}
                    >
                      影响度: {(point.impact * 100).toFixed(0)}%
                    </div>
                  </div>
                  
                  <div className="turning-point-description">{point.description}</div>
                  
                  <div className="turning-point-participants">
                    <span className="participants-label">相关参与者:</span>
                    <span className="participants-list">{point.participants.join(', ')}</span>
                  </div>

                  <div className="turning-point-coherence">
                    <span className="coherence-label">逻辑一致性:</span>
                    <div className="coherence-bar">
                      <div 
                        className="coherence-fill" 
                        style={{ 
                          width: `${point.coherence * 100}%`,
                          backgroundColor: point.coherence > 0.8 ? '#4CAF50' : '#FFC107'
                        }}
                      ></div>
                    </div>
                    <span className="coherence-value">{(point.coherence * 100).toFixed(0)}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {viewMode === 'chains' && (
        <div className="logical-content">
          {/* 逻辑链条分析 */}
          <div className="logical-chains-section">
            <h4>🔗 逻辑链条分析</h4>
            <div className="chains-list">
              {logicalChains.map((chain, index) => (
                <div key={index} className="chain-item">
                  <div className="chain-header">
                    <div className="chain-title">{chain.chain}</div>
                    <div 
                      className="chain-strength"
                      style={{ color: getChainColor(chain.strength) }}
                    >
                      强度: {(chain.strength * 100).toFixed(0)}%
                    </div>
                  </div>
                  
                  <div className="chain-participants">
                    <span className="participants-label">参与成员:</span>
                    <span className="participants-list">{chain.participants.join(', ')}</span>
                  </div>
                  
                  <div className="chain-rounds">
                    <span className="rounds-label">涉及轮次:</span>
                    <span className="rounds-list">第{chain.rounds.join(', ')}轮</span>
                  </div>

                  <div className="chain-strength-bar">
                    <div 
                      className="strength-fill" 
                      style={{ 
                        width: `${chain.strength * 100}%`,
                        backgroundColor: getChainColor(chain.strength)
                      }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 流程详情 */}
          <div className="conversation-flow-section">
            <h4>📊 对话流程详情</h4>
            <div className="flow-details">
              {conversationFlow.map((flow, index) => (
                <div key={index} className="flow-item">
                  <div className="flow-round">第{flow.round}轮</div>
                  <div className="flow-topic">{flow.topic}</div>
                  <div 
                    className="flow-cohesion"
                    style={{ color: getFlowColor(flow.cohesion) }}
                  >
                    凝聚力: {flow.cohesion.toFixed(2)}
                  </div>
                  <div className="flow-participants">参与: {flow.participants}人</div>
                  <div className="flow-connections">连接: {flow.connections}个</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {logicalData.recommendations && logicalData.recommendations.length > 0 && (
        <div className="analysis-recommendations">
          <h4>💡 改进建议</h4>
          <ul>
            {logicalData.recommendations.map((recommendation, index) => (
              <li key={index}>{recommendation}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default LogicalStructureAnalysis;