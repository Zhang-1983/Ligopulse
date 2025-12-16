import React, { useState, useEffect } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';
import apiService from '../services/api';

const HiddenInfoAnalysis = ({ hiddenData }) => {
  const [analysisData, setAnalysisData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeView, setActiveView] = useState('overview');

  useEffect(() => {
    const fetchHiddenInfoAnalysis = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const analysisRequest = {
          analysisType: 'hidden_info',
          inputData: hiddenData || {},
          config: {
            enableSubtextAnalysis: true,
            enableEmotionalAssessment: true,
            enablePowerAnalysis: true,
            enableMotiveDetection: true,
            enableConcernIdentification: true,
            enableRelationshipMapping: true
          }
        };

        const result = await apiService.hiddenInfoAnalysis(analysisRequest);
        setAnalysisData(result);
      } catch (err) {
        console.error('隐含信息分析失败:', err);
        setError(err.message || '隐含信息分析失败，请重试');
      } finally {
        setLoading(false);
      }
    };

    if (hiddenData) {
      fetchHiddenInfoAnalysis();
    } else {
      setLoading(false);
      setError('缺少分析数据');
    }
  }, [hiddenData]);

  // 数据标准化函数
  const normalizeData = (data) => {
    if (!data) return null;

    return {
      subtextAnalysis: data.subtextAnalysis || data.潜台词分析 || {},
      emotionalHiddenness: data.emotionalHiddenness || data.情感隐藏度 || {},
      powerBalance: data.powerBalance || data.权力平衡 || {},
      underlyingMotives: data.underlyingMotives || data.潜在动机 || {},
      unspokenConcerns: data.unspokenConcerns || data.未言明担忧 || [],
      impliedRelationships: data.impliedRelationships || data.暗示性关系 || {},
      summary: data.summary || data.摘要 || {},
      insights: data.insights || data.洞察 || []
    };
  };

  // 获取处理后的数据
  const processedData = analysisData ? normalizeData(analysisData) : null;

  // 如果数据为空或无效，使用默认数据结构
  const getFallbackData = () => ({
    subtextData: [
      { name: "表面协调", strength: 0.6, hiddenness: 0.8, participants: 3 },
      { name: "深层担忧", strength: 0.9, hiddenness: 0.95, participants: 2 },
      { name: "潜在冲突", strength: 0.7, hiddenness: 0.9, participants: 4 },
      { name: "隐藏议程", strength: 0.5, hiddenness: 0.98, participants: 1 },
      { name: "未表达需求", strength: 0.8, hiddenness: 0.85, participants: 3 }
    ],
    emotionalHiddennessData: [
      { participant: "张三", hiddenness: 0.3, authentic: 0.7, defense: 0.4 },
      { participant: "李四", hiddenness: 0.7, authentic: 0.3, defense: 0.8 },
      { participant: "王五", hiddenness: 0.5, authentic: 0.5, defense: 0.6 },
      { participant: "赵六", hiddenness: 0.8, authentic: 0.2, defense: 0.9 }
    ],
    powerBalanceData: [
      { participant: "张三", formalPower: 0.9, informalPower: 0.7, influence: 0.8 },
      { participant: "李四", formalPower: 0.6, informalPower: 0.8, influence: 0.7 },
      { participant: "王五", formalPower: 0.7, informalPower: 0.5, influence: 0.6 },
      { participant: "赵六", formalPower: 0.4, informalPower: 0.6, influence: 0.5 }
    ],
    underlyingMotivesData: [
      { motive: "保护自身利益", confidence: 0.85, evidence: 3, impact: 0.8 },
      { motive: "寻求认可", confidence: 0.7, evidence: 5, impact: 0.6 },
      { motive: "避免责任", confidence: 0.9, evidence: 2, impact: 0.7 },
      { motive: "推进议程", confidence: 0.75, evidence: 4, impact: 0.9 },
      { motive: "维护关系", confidence: 0.6, evidence: 6, impact: 0.5 }
    ],
    concernsData: [
      {
        concern: "时间压力可能影响质量",
        participant: "质量总监",
        impact: 0.8,
        evidence: "多次提到质量控制的重要性",
        urgency: 0.7
      },
      {
        concern: "预算可能超支",
        participant: "财务经理", 
        impact: 0.9,
        evidence: "反复询问成本控制措施",
        urgency: 0.8
      },
      {
        concern: "团队协作存在问题",
        participant: "人力资源总监",
        impact: 0.6,
        evidence: "观察到沟通中的摩擦",
        urgency: 0.5
      }
    ],
    relationshipData: [
      { participant: "张三", relationships: { "李四": 0.8, "王五": 0.6 } },
      { participant: "李四", relationships: { "张三": 0.8, "赵六": 0.7 } },
      { participant: "王五", relationships: { "张三": 0.6, "赵六": 0.9 } },
      { participant: "赵六", relationships: { "李四": 0.7, "王五": 0.9 } }
    ]
  });

  // 获取最终显示数据
  const getDisplayData = () => {
    if (!processedData) return getFallbackData();

    const {
      subtextAnalysis,
      emotionalHiddenness,
      powerBalance,
      underlyingMotives,
      unspokenConcerns,
      impliedRelationships
    } = processedData;

    return {
      subtextData: Object.keys(subtextAnalysis).length > 0
        ? Object.entries(subtextAnalysis).map(([key, value]) => ({ name: key, ...value }))
        : getFallbackData().subtextData,
      
      emotionalHiddennessData: Object.keys(emotionalHiddenness).length > 0
        ? Object.entries(emotionalHiddenness).map(([participant, data]) => ({ participant, ...data }))
        : getFallbackData().emotionalHiddennessData,
      
      powerBalanceData: Object.keys(powerBalance).length > 0
        ? Object.entries(powerBalance).map(([participant, data]) => ({ participant, ...data }))
        : getFallbackData().powerBalanceData,
      
      underlyingMotivesData: Object.keys(underlyingMotives).length > 0
        ? Object.entries(underlyingMotives).map(([key, value]) => ({ motive: key, ...value }))
        : getFallbackData().underlyingMotivesData,
      
      concernsData: unspokenConcerns.length > 0 ? unspokenConcerns : getFallbackData().concernsData,
      
      relationshipData: Object.keys(impliedRelationships).length > 0 
        ? Object.entries(impliedRelationships).map(([participant, relationships]) => ({ 
            participant, 
            relationships 
          }))
        : getFallbackData().relationshipData
    };
  };

  const displayData = getDisplayData();

  const COLORS = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8'];

  const getHiddennessColor = (score) => {
    if (score >= 0.8) return '#D32F2F';
    if (score >= 0.6) return '#FF5722';
    return '#FFC107';
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return '#4CAF50';
    if (confidence >= 0.6) return '#FFC107';
    return '#F44336';
  };

  // 加载状态
  if (loading) {
    return (
      <div className="hidden-info-analysis">
        <div className="analysis-header">
          <h3 className="analysis-title">🔍 潜在隐含信息挖掘</h3>
          <div className="loading-spinner">
            <div className="spinner"></div>
            <span>正在分析隐含信息...</span>
          </div>
        </div>
      </div>
    );
  }

  // 错误状态
  if (error) {
    return (
      <div className="hidden-info-analysis">
        <div className="analysis-header">
          <h3 className="analysis-title">🔍 潜在隐含信息挖掘</h3>
          <div className="error-message">
            <span className="error-icon">⚠️</span>
            <span>{error}</span>
            <button 
              className="retry-button" 
              onClick={() => window.location.reload()}
            >
              重试
            </button>
          </div>
        </div>
      </div>
    );
  }

  // 无数据状态
  if (!processedData && !hiddenData) {
    return (
      <div className="hidden-info-analysis">
        <div className="analysis-header">
          <h3 className="analysis-title">🔍 潜在隐含信息挖掘</h3>
          <div className="no-data-message">
            <span className="no-data-icon">📊</span>
            <span>暂无隐含信息数据</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="hidden-info-analysis">
      <div className="analysis-header">
        <h3 className="analysis-title">🔍 潜在隐含信息挖掘</h3>
        
        {/* 视图切换 */}
        <div className="view-tabs">
          <button 
            className={`view-tab ${activeView === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveView('overview')}
          >
            概览
          </button>
          <button 
            className={`view-tab ${activeView === 'subtext' ? 'active' : ''}`}
            onClick={() => setActiveView('subtext')}
          >
            潜台词分析
          </button>
          <button 
            className={`view-tab ${activeView === 'emotion' ? 'active' : ''}`}
            onClick={() => setActiveView('emotion')}
          >
            情感隐藏度
          </button>
          <button 
            className={`view-tab ${activeView === 'power' ? 'active' : ''}`}
            onClick={() => setActiveView('power')}
          >
            权力分析
          </button>
          <button 
            className={`view-tab ${activeView === 'motives' ? 'active' : ''}`}
            onClick={() => setActiveView('motives')}
          >
            动机识别
          </button>
        </div>

        <div className="hidden-metrics">
          <div className="metric-card">
            <div className="metric-value">
              {displayData.subtextData.reduce((sum, item) => sum + item.strength, 0) / displayData.subtextData.length || 0.72}
            </div>
            <div className="metric-label">平均隐含强度</div>
          </div>
          <div className="metric-card">
            <div className="metric-value">
              {displayData.emotionalHiddennessData.reduce((sum, item) => sum + item.hiddenness, 0) / displayData.emotionalHiddennessData.length || 0.58}
            </div>
            <div className="metric-label">情感隐藏度</div>
          </div>
          <div className="metric-card">
            <div className="metric-value">{displayData.concernsData.length}</div>
            <div className="metric-label">未言明担忧</div>
          </div>
          <div className="metric-card">
            <div className="metric-value">{displayData.underlyingMotivesData.length}</div>
            <div className="metric-label">识别动机</div>
          </div>
        </div>
      </div>

      <div className="hidden-content">
        {/* 概览视图 */}
        {activeView === 'overview' && (
          <div className="overview-section">
            <div className="overview-grid">
              <div className="overview-card">
                <h4>💭 潜台词强度分布</h4>
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie
                      data={displayData.subtextData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, strength }) => `${name} ${(strength * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="strength"
                    >
                      {displayData.subtextData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>

              <div className="overview-card">
                <h4>⚖️ 权力动态平衡</h4>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={displayData.powerBalanceData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis dataKey="participant" stroke="#666" />
                    <YAxis stroke="#666" />
                    <Tooltip />
                    <Bar dataKey="influence" fill="#4CAF50" name="实际影响力" />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <div className="overview-card">
                <h4>🎯 关键潜在动机</h4>
                <div className="motives-preview">
                  {displayData.underlyingMotivesData.slice(0, 3).map((motive, index) => (
                    <div key={index} className="motive-preview">
                      <div className="motive-name">{motive.motive}</div>
                      <div className="motive-confidence">
                        置信度: {(motive.confidence * 100).toFixed(0)}%
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="overview-card">
                <h4>⚠️ 重要担忧事项</h4>
                <div className="concerns-preview">
                  {displayData.concernsData.slice(0, 3).map((concern, index) => (
                    <div key={index} className="concern-preview">
                      <div className="concern-title">{concern.concern}</div>
                      <div className="concern-meta">
                        {concern.participant} | 影响: {(concern.impact * 100).toFixed(0)}%
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* 分析总结 */}
            {processedData?.summary && (
              <div className="analysis-summary">
                <h4>📝 分析总结</h4>
                <div className="summary-content">
                  <p>{processedData.summary.overall || '隐含信息分析已完成，发现了多个层面的潜在信息和动机。'}</p>
                </div>
              </div>
            )}
          </div>
        )}

        {/* 潜台词分析视图 */}
        {activeView === 'subtext' && (
          <div className="subtext-analysis-section">
            <h4>💭 潜台词强度分布</h4>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={displayData.subtextData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, strength }) => `${name} ${(strength * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="strength"
                >
                  {displayData.subtextData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>

            <div className="subtext-details">
              {displayData.subtextData.map((item, index) => (
                <div key={index} className="subtext-item">
                  <div className="subtext-header">
                    <div className="subtext-name">{item.name}</div>
                    <div className="subtext-participants">
                      涉及: {item.participants}人
                    </div>
                  </div>
                  
                  <div className="subtext-metrics">
                    <div className="metric-row">
                      <span className="metric-label">强度:</span>
                      <div className="metric-bar">
                        <div 
                          className="metric-fill strength" 
                          style={{ width: `${item.strength * 100}%` }}
                        ></div>
                      </div>
                      <span className="metric-value">{(item.strength * 100).toFixed(0)}%</span>
                    </div>
                    
                    <div className="metric-row">
                      <span className="metric-label">隐藏度:</span>
                      <div className="metric-bar">
                        <div 
                          className="metric-fill hiddenness" 
                          style={{ 
                            width: `${item.hiddenness * 100}%`,
                            backgroundColor: getHiddennessColor(item.hiddenness)
                          }}
                        ></div>
                      </div>
                      <span 
                        className="metric-value"
                        style={{ color: getHiddennessColor(item.hiddenness) }}
                      >
                        {(item.hiddenness * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 情感隐藏度分析视图 */}
        {activeView === 'emotion' && (
          <div className="emotional-hiddenness-section">
            <h4>🎭 情感真实性评估</h4>
            <div className="hiddenness-grid">
              {displayData.emotionalHiddennessData.map((participant, index) => (
                <div key={index} className="participant-hiddenness">
                  <div className="participant-name">{participant.participant}</div>
                  
                  <div className="hiddenness-bars">
                    <div className="hiddenness-item">
                      <span className="hiddenness-label">隐藏度</span>
                      <div className="hiddenness-bar">
                        <div 
                          className="hiddenness-fill" 
                          style={{ 
                            width: `${participant.hiddenness * 100}%`,
                            backgroundColor: getHiddennessColor(participant.hiddenness)
                          }}
                        ></div>
                      </div>
                      <span 
                        className="hiddenness-value"
                        style={{ color: getHiddennessColor(participant.hiddenness) }}
                      >
                        {(participant.hiddenness * 100).toFixed(0)}%
                      </span>
                    </div>
                    
                    <div className="hiddenness-item">
                      <span className="hiddenness-label">真实性</span>
                      <div className="hiddenness-bar">
                        <div 
                          className="hiddenness-fill authentic" 
                          style={{ width: `${participant.authentic * 100}%` }}
                        ></div>
                      </div>
                      <span className="hiddenness-value">
                        {(participant.authentic * 100).toFixed(0)}%
                      </span>
                    </div>
                    
                    <div className="hiddenness-item">
                      <span className="hiddenness-label">防御性</span>
                      <div className="hiddenness-bar">
                        <div 
                          className="hiddenness-fill defense" 
                          style={{ width: `${participant.defense * 100}%` }}
                        ></div>
                      </div>
                      <span className="hiddenness-value">
                        {(participant.defense * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>

                  <div className="hiddenness-assessment">
                    <span className="assessment-label">评估:</span>
                    <span 
                      className="assessment-value"
                      style={{ 
                        color: participant.hiddenness > 0.7 ? '#F44336' : participant.hiddenness > 0.4 ? '#FFC107' : '#4CAF50'
                      }}
                    >
                      {participant.hiddenness > 0.7 ? '高度隐藏' : participant.hiddenness > 0.4 ? '适度隐藏' : '相对开放'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 权力平衡分析视图 */}
        {activeView === 'power' && (
          <div className="power-balance-section">
            <h4>⚖️ 权力动态平衡分析</h4>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={displayData.powerBalanceData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="participant" stroke="#666" />
                <YAxis stroke="#666" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'white', 
                    border: '1px solid #e0e0e0',
                    borderRadius: '8px'
                  }} 
                />
                <Bar dataKey="formalPower" fill="#2196F3" name="正式权力" />
                <Bar dataKey="informalPower" fill="#FF9800" name="非正式权力" />
                <Bar dataKey="influence" fill="#4CAF50" name="实际影响力" />
              </BarChart>
            </ResponsiveContainer>

            <div className="power-analysis">
              <div className="power-dominance">
                <h5>权力主导者</h5>
                <div className="dominant-participants">
                  {displayData.powerBalanceData
                    .filter(p => p.influence > 0.7)
                    .map(p => p.participant)
                    .join(', ') || '权力分布均衡'}
                </div>
              </div>
              
              <div className="power-dynamics">
                <h5>权力动态</h5>
                <div className="dynamics-item">
                  <span className="dynamics-label">权力差距:</span>
                  <span className="dynamics-value">
                    {(Math.max(...displayData.powerBalanceData.map(p => p.influence)) - 
                      Math.min(...displayData.powerBalanceData.map(p => p.influence))).toFixed(2)}
                  </span>
                </div>
                <div className="dynamics-item">
                  <span className="dynamics-label">平衡状态:</span>
                  <span className="dynamics-value">
                    {Math.abs(Math.max(...displayData.powerBalanceData.map(p => p.influence)) - 
                             Math.min(...displayData.powerBalanceData.map(p => p.influence))) > 0.3 ? 
                     '不平衡' : '相对平衡'}
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* 潜在动机分析视图 */}
        {activeView === 'motives' && (
          <div className="underlying-motives-section">
            <h4>🎯 潜在动机识别</h4>
            <div className="motives-list">
              {displayData.underlyingMotivesData.map((motive, index) => (
                <div key={index} className="motive-item">
                  <div className="motive-header">
                    <div className="motive-name">{motive.motive}</div>
                    <div 
                      className="motive-confidence"
                      style={{ color: getConfidenceColor(motive.confidence) }}
                    >
                      置信度: {(motive.confidence * 100).toFixed(0)}%
                    </div>
                  </div>
                  
                  <div className="motive-metrics">
                    <div className="motive-metric">
                      <span className="metric-label">证据数量:</span>
                      <span className="metric-value">{motive.evidence}个</span>
                    </div>
                    <div className="motive-metric">
                      <span className="metric-label">影响程度:</span>
                      <span className="metric-value">{(motive.impact * 100).toFixed(0)}%</span>
                    </div>
                  </div>

                  <div className="motive-bar">
                    <div 
                      className="motive-fill" 
                      style={{ 
                        width: `${motive.confidence * 100}%`,
                        backgroundColor: getConfidenceColor(motive.confidence)
                      }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 未言明担忧 */}
        <div className="unspoken-concerns-section">
          <h4>⚠️ 未言明的担忧</h4>
          <div className="concerns-list">
            {displayData.concernsData.map((concern, index) => (
              <div key={index} className="concern-item">
                <div className="concern-header">
                  <div className="concern-title">{concern.concern}</div>
                  <div className="concern-participant">{concern.participant}</div>
                </div>
                
                <div className="concern-metrics">
                  <div className="concern-metric">
                    <span className="metric-label">影响程度:</span>
                    <span className="metric-value">{(concern.impact * 100).toFixed(0)}%</span>
                  </div>
                  <div className="concern-metric">
                    <span className="metric-label">紧急程度:</span>
                    <span className="metric-value">{(concern.urgency * 100).toFixed(0)}%</span>
                  </div>
                </div>
                
                <div className="concern-evidence">
                  <span className="evidence-label">证据:</span>
                  <span className="evidence-text">{concern.evidence}</span>
                </div>

                <div className="concern-level">
                  <div className="concern-bar">
                    <div 
                      className="concern-fill impact" 
                      style={{ width: `${concern.impact * 100}%` }}
                    ></div>
                    <div 
                      className="concern-fill urgency" 
                      style={{ width: `${concern.urgency * 100}%` }}
                    ></div>
                  </div>
                  <div className="concern-labels">
                    <span>影响</span>
                    <span>紧急</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 暗示性关系 */}
        <div className="implied-relationships-section">
          <h4>🕸️ 暗示性关系网络</h4>
          <div className="relationship-network">
            <div className="network-nodes">
              {displayData.relationshipData.map((node, index) => (
                <div key={index} className="network-node">
                  <div className="node-name">{node.participant}</div>
                  <div className="node-relationships">
                    {Object.entries(node.relationships).map(([target, strength]) => (
                      <div key={target} className="node-relationship">
                        → {target}: {(strength * 100).toFixed(0)}%
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
            
            <div className="network-insights">
              <div className="insight-item">
                <span className="insight-icon">🔗</span>
                <span className="insight-text">
                  关系网络密度较高，团队内部联系紧密
                </span>
              </div>
              <div className="insight-item">
                <span className="insight-icon">⚡</span>
                <span className="insight-text">
                  存在明显的意见领袖和信息传播节点
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* 分析说明 */}
        {processedData?.insights && processedData.insights.length > 0 && (
          <div className="analysis-insights">
            <h4>💡 分析洞察</h4>
            <div className="insights-list">
              {processedData.insights.map((insight, index) => (
                <div key={index} className="insight-item">
                  <span className="insight-icon">🔍</span>
                  <span className="insight-text">{insight}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default HiddenInfoAnalysis;