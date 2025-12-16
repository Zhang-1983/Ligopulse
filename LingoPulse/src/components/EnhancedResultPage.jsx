import React, { useState, useEffect } from 'react';
import { Download, ArrowLeft, BarChart3, Heart, MessageSquare, Brain, Network, Eye, TrendingUp, FileText } from 'lucide-react';
import { ResponsiveContainer } from 'recharts';

// 导入所有分析组件
import TopicAnalysis from './TopicAnalysis';
import SentimentAnalysis from './SentimentAnalysis';
import KeyPointsAnalysis from './KeyPointsAnalysis';
import IntentAnalysis from './IntentAnalysis';
import LogicalStructureAnalysis from './LogicalStructureAnalysis';
import HiddenInfoAnalysis from './HiddenInfoAnalysis';
import FutureDevelopmentAnalysis from './FutureDevelopmentAnalysis';

const EnhancedResultPage = ({ onNavigate, scenario, dialogue, analysisData }) => {
  const [activeTab, setActiveTab] = useState('overview');
  const [fullAnalysisData, setFullAnalysisData] = useState(null);

  useEffect(() => {
    // 生成完整的增强分析数据
    const generateEnhancedData = () => {
      if (analysisData) {
        return {
          ...analysisData,
          topicAnalysis: {
            themes: [
              { name: '项目讨论', weight: 0.35, evolution: [0.2, 0.4, 0.35, 0.5, 0.45] },
              { name: '团队协作', weight: 0.25, evolution: [0.1, 0.3, 0.4, 0.3, 0.25] },
              { name: '决策制定', weight: 0.2, evolution: [0.3, 0.2, 0.15, 0.4, 0.3] },
              { name: '问题解决', weight: 0.2, evolution: [0.4, 0.1, 0.1, 0.2, 0.0] }
            ],
            transitions: [
              { from: '问题解决', to: '项目讨论', frequency: 5 },
              { from: '项目讨论', to: '团队协作', frequency: 3 },
              { from: '团队协作', to: '决策制定', frequency: 2 }
            ],
            keySegments: [
              { time: '5分钟', theme: '问题解决', snippet: '我们需要重新评估项目时间线...' },
              { time: '15分钟', theme: '项目讨论', snippet: '关于新功能的开发进度...' },
              { time: '25分钟', theme: '团队协作', snippet: '每个人都应该明确自己的职责...' }
            ]
          },
          sentimentAnalysis: {
            trends: [
              { time: '0%', positive: 0.3, negative: 0.4, neutral: 0.3 },
              { time: '25%', positive: 0.5, negative: 0.2, neutral: 0.3 },
              { time: '50%', positive: 0.6, negative: 0.1, neutral: 0.3 },
              { time: '75%', positive: 0.4, negative: 0.3, neutral: 0.3 },
              { time: '100%', positive: 0.7, negative: 0.1, neutral: 0.2 }
            ],
            distribution: { positive: 0.52, negative: 0.22, neutral: 0.26 },
            score: 0.68,
            turningPoints: [
              { time: '12分钟', event: '团队达成共识', impact: 0.3 },
              { time: '28分钟', event: '解决了关键争议', impact: 0.4 }
            ]
          },
          keyPointsAnalysis: {
            mainPoints: [
              { title: '项目里程碑调整', importance: 0.9, consensus: 0.8, intensity: 0.7 },
              { title: '资源分配优化', importance: 0.8, consensus: 0.9, intensity: 0.6 },
              { title: '团队沟通机制', importance: 0.6, consensus: 0.7, intensity: 0.4 }
            ],
            controversial: [
              { topic: '项目截止日期', stance: 'A方主张提前', support: 0.6 },
              { topic: '预算分配', stance: 'B方希望增加投入', support: 0.4 }
            ],
            consensus: [
              { agreement: '新功能优先级', level: 0.85 },
              { agreement: '团队协作方式', level: 0.92 }
            ],
            evidence: [
              { quote: '我们需要确保按时交付', speaker: 'A方', timestamp: '8:30' },
              { quote: '这确实是一个合理的调整', speaker: 'B方', timestamp: '15:45' }
            ]
          },
          intentAnalysis: {
            participants: [
              { name: 'A方', radarData: { involvement: 0.8, influence: 0.7, satisfaction: 0.6, cooperation: 0.9 } },
              { name: 'B方', radarData: { involvement: 0.6, influence: 0.8, satisfaction: 0.8, cooperation: 0.7 } }
            ],
            motivations: [
              { priority: 1, motivation: '项目成功', confidence: 0.9, participant: '双方' },
              { priority: 2, motivation: '效率提升', confidence: 0.8, participant: 'A方' },
              { priority: 3, motivation: '团队和谐', confidence: 0.7, participant: 'B方' }
            ],
            roles: [
              { role: '主导者', person: 'A方', power: 0.8, influence: 0.7 },
              { role: '协调者', person: 'B方', power: 0.6, influence: 0.8 }
            ],
            communicationPatterns: [
              { pattern: '直接沟通', frequency: 0.7 },
              { pattern: '倾听反馈', frequency: 0.6 },
              { pattern: '质疑求证', frequency: 0.4 }
            ]
          },
          logicalStructureAnalysis: {
            cohesionTrend: [
              { round: 1, cohesion: 0.6, strength: 0.5 },
              { round: 2, cohesion: 0.7, strength: 0.6 },
              { round: 3, cohesion: 0.5, strength: 0.4 },
              { round: 4, cohesion: 0.8, strength: 0.7 },
              { round: 5, cohesion: 0.9, strength: 0.8 }
            ],
            logicalChains: [
              { chain: '问题识别 → 原因分析 → 解决方案', coherence: 0.85 },
              { chain: '需求确认 → 资源评估 → 执行计划', coherence: 0.92 }
            ],
            turningPoints: [
              { point: '争议爆发', impact: 0.6, recovery: '解决共识' },
              { point: '达成一致', impact: 0.8, recovery: '推进执行' }
            ],
            completeness: { score: 0.88, coverage: '95%', missing: ['风险评估', '应急预案'] },
            consistency: { score: 0.82, conflicts: 2, resolution: 1 },
            decisionTree: [
              { decision: '项目优先级调整', outcome: '达成一致', confidence: 0.9 },
              { decision: '时间表重新规划', outcome: '需要进一步讨论', confidence: 0.6 }
            ]
          },
          hiddenInfoAnalysis: {
            subtexts: [
              { content: '对当前进度不满', strength: 0.7, participants: ['A方'] },
              { content: '希望获得更多支持', strength: 0.6, participants: ['B方'] },
              { content: '担心项目延期风险', strength: 0.8, participants: ['双方'] }
            ],
            hiddennessScores: [
              { person: 'A方', score: 0.3, indicators: ['回避眼神接触', '语速变化'] },
              { person: 'B方', score: 0.2, indicators: ['表达犹豫', '肢体语言'] }
            ],
            powerDynamics: [
              { aspect: '正式权力', A: 0.8, B: 0.6 },
              { aspect: '非正式影响力', A: 0.6, B: 0.8 },
              { aspect: '决策权', A: 0.7, B: 0.5 }
            ],
            hiddenMotivations: [
              { motivation: '维护权威形象', confidence: 0.8, evidence: '坚持己见、不接受反驳' },
              { motivation: '寻求认同和理解', confidence: 0.7, evidence: '反复强调观点、寻求确认' }
            ],
            unspokenConcerns: [
              { concern: '项目质量可能受影响', urgency: 0.8, impact: 0.9 },
              { concern: '团队协作效率问题', urgency: 0.6, impact: 0.7 }
            ],
            relationshipHints: [
              { relationship: '上下级', strength: 0.3 },
              { relationship: '同事合作', strength: 0.8 },
              { relationship: '竞争关系', strength: 0.4 }
            ]
          },
          futureDevelopmentAnalysis: {
            trendAnalysis: {
              collaborationTrend: [
                { period: '当前', value: 0.75 },
                { period: '1周后', value: 0.8 },
                { period: '1月后', value: 0.85 },
                { period: '3月后', value: 0.9 },
                { period: '6月后', value: 0.88 }
              ],
              productivityTrend: [
                { period: '当前', value: 0.7 },
                { period: '1周后', value: 0.72 },
                { period: '1月后', value: 0.78 },
                { period: '3月后', value: 0.85 },
                { period: '6月后', value: 0.9 }
              ],
              satisfactionTrend: [
                { period: '当前', value: 0.65 },
                { period: '1周后', value: 0.68 },
                { period: '1月后', value: 0.75 },
                { period: '3月后', value: 0.8 },
                { period: '6月后', value: 0.82 }
              ]
            },
            riskPrediction: {
              '沟通效率下降': { probability: 0.7, impact: 0.8, mitigation: '建立定期沟通机制', timeline: '1-2周内' },
              '决策执行延迟': { probability: 0.6, impact: 0.9, mitigation: '明确责任分工和时间节点', timeline: '2-4周内' },
              '团队动力不足': { probability: 0.5, impact: 0.7, mitigation: '增加激励机制和反馈', timeline: '1-3个月内' },
              '资源冲突': { probability: 0.4, impact: 0.6, mitigation: '建立资源协调机制', timeline: '2-6个月内' }
            },
            improvementSuggestions: [
              {
                category: '沟通优化',
                priority: '高',
                impact: 0.9,
                effort: 0.3,
                title: '建立例会制度',
                description: '每周定期召开团队例会，及时同步进展和解决问题',
                implementation: '立即执行',
                expectedOutcome: '沟通效率提升30%'
              },
              {
                category: '决策流程',
                priority: '高',
                impact: 0.85,
                effort: 0.4,
                title: '简化决策流程',
                description: '减少决策层级，提高决策速度和执行效率',
                implementation: '1周内',
                expectedOutcome: '决策时间缩短50%'
              },
              {
                category: '团队建设',
                priority: '中',
                impact: 0.7,
                effort: 0.5,
                title: '团建活动',
                description: '定期组织团队活动，增强成员间的信任和协作',
                implementation: '2周内',
                expectedOutcome: '团队凝聚力提升40%'
              },
              {
                category: '工具升级',
                priority: '中',
                impact: 0.8,
                effort: 0.7,
                title: '协作工具升级',
                description: '引入更先进的项目管理和沟通协作工具',
                implementation: '1个月内',
                expectedOutcome: '工作效率提升25%'
              }
            ],
            potentialOutcomes: {
              '项目按期完成': { probability: 0.8, benefits: '按时交付，客户满意度高', challenges: '需要压缩部分测试时间', preparation: '提前规划资源调配' },
              '项目延期完成': { probability: 0.15, benefits: '质量更高，细节更完善', challenges: '成本增加，客户可能不满', preparation: '提前沟通延期风险' },
              '项目提前完成': { probability: 0.05, benefits: '成本节约，团队士气高', challenges: '可能遗漏某些细节', preparation: '质量检查机制' }
            },
            actionItems: [
              { action: '制定详细时间计划', owner: '项目经理', deadline: '3天内', status: 'pending', priority: '高' },
              { action: '分配具体任务', owner: '团队负责人', deadline: '5天内', status: 'pending', priority: '高' },
              { action: '建立监控机制', owner: '质量经理', deadline: '1周内', status: 'pending', priority: '中' },
              { action: '制定应急预案', owner: '风险控制', deadline: '2周内', status: 'pending', priority: '中' }
            ],
            successMetrics: {
              '按时完成率': { current: 0.75, target: 0.9, trend: '上升' },
              '质量满意度': { current: 0.8, target: 0.95, trend: '稳定' },
              '团队效率': { current: 0.7, target: 0.85, trend: '上升' },
              '沟通质量': { current: 0.65, target: 0.9, trend: '上升' },
              '创新能力': { current: 0.6, target: 0.8, trend: '稳定' }
            }
          }
        };
      }

      return {};
    };

    setFullAnalysisData(generateEnhancedData());
  }, [analysisData]);

  const handleExportReport = () => {
    const reportData = {
      scenario,
      dialogue,
      analysisData: fullAnalysisData,
      timestamp: new Date().toISOString(),
      reportType: 'enhanced_analysis'
    };

    const dataStr = JSON.stringify(reportData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `lingopulse-enhanced-report-${Date.now()}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const tabs = [
    { id: 'overview', name: '概览', icon: BarChart3 },
    { id: 'topic', name: '主题分析', icon: MessageSquare },
    { id: 'sentiment', name: '情感分析', icon: Heart },
    { id: 'keypoints', name: '关键观点', icon: FileText },
    { id: 'intent', name: '意图分析', icon: Brain },
    { id: 'structure', name: '逻辑结构', icon: Network },
    { id: 'hidden', name: '隐含信息', icon: Eye },
    { id: 'future', name: '发展预测', icon: TrendingUp }
  ];

  // 生成概览数据
  const overviewData = fullAnalysisData ? {
    pulseData: analysisData?.pulseData || [],
    insights: analysisData?.insights || [],
    patterns: analysisData?.patterns || {},
    suggestions: analysisData?.suggestions || []
  } : null;

  if (!fullAnalysisData) {
    return (
      <div className="app-container">
        <button className="main-button" onClick={() => onNavigate('home')} style={{ alignSelf: 'flex-start', marginBottom: '24px' }}>
          <ArrowLeft size={16} />
          返回首页
        </button>
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>正在生成增强分析...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="app-container enhanced-result-page">
      <button className="main-button" onClick={() => onNavigate('home')} style={{ alignSelf: 'flex-start', marginBottom: '24px' }}>
        <ArrowLeft size={16} />
        返回首页
      </button>

      <div className="enhanced-result-container">
        <div className="enhanced-result-header">
          <h2 className="section-title">增强分析结果</h2>
          <div className="scenario-badge">{scenario}</div>
          <button className="main-button" onClick={handleExportReport}>
            <Download size={16} />
            导出增强报告
          </button>
        </div>

        {/* 选项卡导航 */}
        <div className="tabs-navigation">
          {tabs.map((tab) => {
            const IconComponent = tab.icon;
            return (
              <button
                key={tab.id}
                className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
                onClick={() => setActiveTab(tab.id)}
              >
                <IconComponent size={18} />
                <span>{tab.name}</span>
              </button>
            );
          })}
        </div>

        {/* 内容区域 */}
        <div className="tab-content">
          {activeTab === 'overview' && overviewData && (
            <div className="overview-section">
              <div className="overview-metrics">
                <div className="metric-card">
                  <div className="metric-value">{fullAnalysisData.topicAnalysis.themes.length}</div>
                  <div className="metric-label">识别主题数</div>
                </div>
                <div className="metric-card">
                  <div className="metric-value">{(fullAnalysisData.sentimentAnalysis.score * 100).toFixed(0)}%</div>
                  <div className="metric-label">情感健康度</div>
                </div>
                <div className="metric-card">
                  <div className="metric-value">{fullAnalysisData.keyPointsAnalysis.mainPoints.length}</div>
                  <div className="metric-label">关键观点数</div>
                </div>
                <div className="metric-card">
                  <div className="metric-value">{fullAnalysisData.intentAnalysis.participants.length}</div>
                  <div className="metric-label">参与者意图</div>
                </div>
                <div className="metric-card">
                  <div className="metric-value">{fullAnalysisData.logicalStructureAnalysis.completeness.score > 0.8 ? '高' : '中等'}</div>
                  <div className="metric-label">结构完整性</div>
                </div>
              </div>

              <div className="overview-pulse">
                <h3>关系脉冲曲线</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={overviewData.pulseData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis dataKey="round" stroke="#666" />
                    <YAxis stroke="#666" />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: 'white', 
                        border: '1px solid #e0e0e0',
                        borderRadius: '8px'
                      }} 
                    />
                    <Line 
                      type="monotone" 
                      dataKey="energy" 
                      stroke="#ff6b6b" 
                      strokeWidth={3}
                      dot={{ fill: '#ff6b6b', strokeWidth: 2, r: 4 }}
                      activeDot={{ r: 6, stroke: '#ff6b6b', strokeWidth: 2 }}
                      name="情感能量"
                    />
                    <Line 
                      type="monotone" 
                      dataKey="symmetry" 
                      stroke="#4ecdc4" 
                      strokeWidth={3}
                      dot={{ fill: '#4ecdc4', strokeWidth: 2, r: 4 }}
                      activeDot={{ r: 6, stroke: '#4ecdc4', strokeWidth: 2 }}
                      name="对称性"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              <div className="overview-insights">
                <h3>关键洞察</h3>
                <div className="insights-grid">
                  {overviewData.insights.map((insight, index) => (
                    <div key={index} className="insight-card">
                      <h4>{insight.title}</h4>
                      <p>{insight.description}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'topic' && <TopicAnalysis conversationData={{ scenario, dialogue }} />}
          {activeTab === 'sentiment' && <SentimentAnalysis conversationData={{ scenario, dialogue }} />}
          {activeTab === 'keypoints' && <KeyPointsAnalysis conversationData={{ scenario, dialogue }} />}
          {activeTab === 'intent' && <IntentAnalysis conversationData={{ scenario, dialogue }} />}
          {activeTab === 'structure' && <LogicalStructureAnalysis 
            conversationData={{ scenario, dialogue }} 
            analysisRequest={{ scenario, dialogue, llmProvider: 'baidu' }}
            onAnalysisComplete={(data) => console.log('结构分析完成:', data)}
          />}
          {activeTab === 'hidden' && <HiddenInfoAnalysis conversationData={{ scenario, dialogue }} />}
          {activeTab === 'future' && <FutureDevelopmentAnalysis conversationData={{ scenario, dialogue }} />}
        </div>
      </div>
    </div>
  );
};

export default EnhancedResultPage;