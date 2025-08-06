import React, { useState, useEffect } from 'react'
import { 
  Brain, 
  Shield, 
  MessageSquare, 
  Network, 
  TrendingUp, 
  AlertTriangle, 
  CheckCircle, 
  Users, 
  Eye, 
  Zap,
  BarChart3,
  Activity,
  RefreshCw,
  Filter,
  Search,
  Download
} from 'lucide-react'
import Card from '../ui/Card'
import Badge from '../ui/Badge'
import Button from '../ui/Button'

interface IntelligenceData {
  conversation_intelligence: {
    total_analyzed: number
    sentiment_distribution: Record<string, number>
    intent_distribution: Record<string, number>
    avg_satisfaction: number
    avg_urgency: number
    top_topics: string[]
  }
  content_moderation: {
    total_moderated: number
    action_distribution: Record<string, number>
    toxicity_distribution: Record<string, number>
    block_rate: number
    flag_rate: number
    ai_safety_score: number
  }
  knowledge_graph: {
    total_entities: number
    total_relationships: number
    entity_types: Record<string, number>
    relationship_types: Record<string, number>
    extraction_stats: Record<string, number>
  }
  collaboration: {
    active_sessions: number
    total_users: number
    features_used: Record<string, number>
    avg_session_duration: number
  }
}

const IntelligenceDashboard: React.FC = () => {
  const [data, setData] = useState<IntelligenceData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [selectedTimeframe, setSelectedTimeframe] = useState('24h')
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date())

  useEffect(() => {
    loadIntelligenceData()
    
    let interval: NodeJS.Timeout
    if (autoRefresh) {
      interval = setInterval(loadIntelligenceData, 30000)
    }
    
    return () => {
      if (interval) clearInterval(interval)
    }
  }, [autoRefresh, selectedTimeframe])

  const loadIntelligenceData = async () => {
    try {
      const token = localStorage.getItem('adminToken')
      
      // Load data from multiple intelligence endpoints
      const [conversationRes, moderationRes, knowledgeRes] = await Promise.all([
        fetch('/api/v1/ai/intelligence/conversation/stats', {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch('/api/v1/ai/intelligence/moderation/stats', {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch('/api/v1/ai/intelligence/knowledge/stats', {
          headers: { 'Authorization': `Bearer ${token}` }
        })
      ])

      const [conversationData, moderationData, knowledgeData] = await Promise.all([
        conversationRes.ok ? conversationRes.json() : {},
        moderationRes.ok ? moderationRes.json() : {},
        knowledgeRes.ok ? knowledgeRes.json() : {}
      ])

      setData({
        conversation_intelligence: {
          total_analyzed: conversationData.total_analyzed || 0,
          sentiment_distribution: conversationData.sentiment_distribution || {},
          intent_distribution: conversationData.intent_distribution || {},
          avg_satisfaction: conversationData.avg_satisfaction || 0,
          avg_urgency: conversationData.avg_urgency || 0,
          top_topics: conversationData.top_topics || []
        },
        content_moderation: {
          total_moderated: moderationData.total_content_moderated || 0,
          action_distribution: moderationData.action_distribution || {},
          toxicity_distribution: moderationData.toxicity_distribution || {},
          block_rate: moderationData.block_rate || 0,
          flag_rate: moderationData.flag_rate || 0,
          ai_safety_score: moderationData.average_ai_safety_score || 1.0
        },
        knowledge_graph: {
          total_entities: knowledgeData.total_entities || 0,
          total_relationships: knowledgeData.total_relationships || 0,
          entity_types: knowledgeData.entity_types || {},
          relationship_types: knowledgeData.relationship_types || {},
          extraction_stats: knowledgeData.extraction_stats || {}
        },
        collaboration: {
          active_sessions: 0,
          total_users: 0,
          features_used: {},
          avg_session_duration: 0
        }
      })

      setLastUpdate(new Date())
    } catch (error) {
      console.error('Failed to load intelligence data:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'very_positive': return 'text-green-600'
      case 'positive': return 'text-green-500'
      case 'neutral': return 'text-gray-500'
      case 'negative': return 'text-red-500'
      case 'very_negative': return 'text-red-600'
      default: return 'text-gray-500'
    }
  }

  const getModerationColor = (action: string) => {
    switch (action) {
      case 'allow': return 'success'
      case 'flag': return 'warning'
      case 'block': return 'error'
      case 'quarantine': return 'error'
      default: return 'default'
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="text-center py-12">
        <AlertTriangle className="w-12 h-12 text-yellow-500 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No Intelligence Data</h3>
        <p className="text-gray-600">Unable to load intelligence data. Please try again.</p>
        <Button onClick={loadIntelligenceData} className="mt-4">
          Retry
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center">
            <Brain className="w-8 h-8 text-purple-600 mr-3" />
            Intelligence Dashboard
          </h1>
          <p className="text-gray-600">AI-powered conversation, content, and knowledge intelligence</p>
        </div>
        <div className="flex items-center space-x-3">
          <select
            value={selectedTimeframe}
            onChange={(e) => setSelectedTimeframe(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm"
          >
            <option value="1h">Last Hour</option>
            <option value="24h">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
          </select>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={autoRefresh ? 'bg-green-50 border-green-200' : ''}
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${autoRefresh ? 'animate-spin' : ''}`} />
            Auto Refresh
          </Button>
          <Button size="sm" onClick={loadIntelligenceData}>
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Messages Analyzed</p>
              <p className="text-2xl font-bold text-gray-900">
                {data.conversation_intelligence.total_analyzed.toLocaleString()}
              </p>
            </div>
            <MessageSquare className="w-8 h-8 text-blue-600" />
          </div>
          <div className="mt-2">
            <p className="text-sm text-gray-500">
              Avg Satisfaction: {(data.conversation_intelligence.avg_satisfaction * 100).toFixed(1)}%
            </p>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Content Moderated</p>
              <p className="text-2xl font-bold text-gray-900">
                {data.content_moderation.total_moderated.toLocaleString()}
              </p>
            </div>
            <Shield className="w-8 h-8 text-green-600" />
          </div>
          <div className="mt-2">
            <p className="text-sm text-gray-500">
              Block Rate: {data.content_moderation.block_rate.toFixed(1)}%
            </p>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Knowledge Entities</p>
              <p className="text-2xl font-bold text-gray-900">
                {data.knowledge_graph.total_entities.toLocaleString()}
              </p>
            </div>
            <Network className="w-8 h-8 text-purple-600" />
          </div>
          <div className="mt-2">
            <p className="text-sm text-gray-500">
              Relationships: {data.knowledge_graph.total_relationships.toLocaleString()}
            </p>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">AI Safety Score</p>
              <p className="text-2xl font-bold text-green-600">
                {(data.content_moderation.ai_safety_score * 100).toFixed(1)}%
              </p>
            </div>
            <CheckCircle className="w-8 h-8 text-green-600" />
          </div>
          <div className="mt-2">
            <p className="text-sm text-gray-500">
              Excellent safety rating
            </p>
          </div>
        </Card>
      </div>

      {/* Conversation Intelligence */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <MessageSquare className="w-5 h-5 text-blue-500 mr-2" />
            Sentiment Analysis
          </h3>
          
          <div className="space-y-3">
            {Object.entries(data.conversation_intelligence.sentiment_distribution).map(([sentiment, count]) => (
              <div key={sentiment} className="flex items-center justify-between">
                <span className={`text-sm font-medium ${getSentimentColor(sentiment)}`}>
                  {sentiment.replace('_', ' ').toUpperCase()}
                </span>
                <div className="flex items-center space-x-2">
                  <div className="w-24 bg-gray-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full ${getSentimentColor(sentiment).replace('text-', 'bg-')}`}
                      style={{ 
                        width: `${(count / Math.max(...Object.values(data.conversation_intelligence.sentiment_distribution))) * 100}%` 
                      }}
                    ></div>
                  </div>
                  <span className="text-sm text-gray-600 w-8">{count}</span>
                </div>
              </div>
            ))}
          </div>
        </Card>

        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Eye className="w-5 h-5 text-green-500 mr-2" />
            Intent Recognition
          </h3>
          
          <div className="space-y-3">
            {Object.entries(data.conversation_intelligence.intent_distribution).map(([intent, count]) => (
              <div key={intent} className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-700">
                  {intent.replace('_', ' ').toUpperCase()}
                </span>
                <div className="flex items-center space-x-2">
                  <div className="w-24 bg-gray-200 rounded-full h-2">
                    <div 
                      className="h-2 rounded-full bg-green-500"
                      style={{ 
                        width: `${(count / Math.max(...Object.values(data.conversation_intelligence.intent_distribution))) * 100}%` 
                      }}
                    ></div>
                  </div>
                  <span className="text-sm text-gray-600 w-8">{count}</span>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* Content Moderation */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <Shield className="w-5 h-5 text-red-500 mr-2" />
          Content Moderation Overview
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <h4 className="font-medium text-gray-700 mb-3">Moderation Actions</h4>
            <div className="space-y-2">
              {Object.entries(data.content_moderation.action_distribution).map(([action, count]) => (
                <div key={action} className="flex items-center justify-between">
                  <Badge variant={getModerationColor(action)}>
                    {action.toUpperCase()}
                  </Badge>
                  <span className="text-sm font-medium">{count}</span>
                </div>
              ))}
            </div>
          </div>
          
          <div>
            <h4 className="font-medium text-gray-700 mb-3">Toxicity Levels</h4>
            <div className="space-y-2">
              {Object.entries(data.content_moderation.toxicity_distribution).map(([level, count]) => (
                <div key={level} className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">
                    {level.replace('_', ' ').toUpperCase()}
                  </span>
                  <span className="text-sm font-medium">{count}</span>
                </div>
              ))}
            </div>
          </div>
          
          <div>
            <h4 className="font-medium text-gray-700 mb-3">Safety Metrics</h4>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Block Rate</span>
                <span className="text-sm font-medium text-red-600">
                  {data.content_moderation.block_rate.toFixed(1)}%
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Flag Rate</span>
                <span className="text-sm font-medium text-yellow-600">
                  {data.content_moderation.flag_rate.toFixed(1)}%
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">AI Safety</span>
                <span className="text-sm font-medium text-green-600">
                  {(data.content_moderation.ai_safety_score * 100).toFixed(1)}%
                </span>
              </div>
            </div>
          </div>
        </div>
      </Card>

      {/* Knowledge Graph */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <Network className="w-5 h-5 text-purple-500 mr-2" />
          Knowledge Graph Intelligence
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium text-gray-700 mb-3">Entity Types</h4>
            <div className="space-y-2">
              {Object.entries(data.knowledge_graph.entity_types).map(([type, count]) => (
                <div key={type} className="flex items-center justify-between">
                  <span className="text-sm text-gray-600 capitalize">
                    {type.replace('_', ' ')}
                  </span>
                  <span className="text-sm font-medium">{count}</span>
                </div>
              ))}
            </div>
          </div>
          
          <div>
            <h4 className="font-medium text-gray-700 mb-3">Relationship Types</h4>
            <div className="space-y-2">
              {Object.entries(data.knowledge_graph.relationship_types).map(([type, count]) => (
                <div key={type} className="flex items-center justify-between">
                  <span className="text-sm text-gray-600 capitalize">
                    {type.replace('_', ' ')}
                  </span>
                  <span className="text-sm font-medium">{count}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </Card>

      {/* Quick Actions */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <Zap className="w-5 h-5 text-yellow-500 mr-2" />
          Intelligence Actions
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Button variant="outline" className="p-4 h-auto">
            <div className="text-center">
              <Search className="w-6 h-6 text-blue-500 mx-auto mb-2" />
              <div className="font-medium">Query Knowledge</div>
              <div className="text-xs text-gray-500 mt-1">
                Search knowledge graph
              </div>
            </div>
          </Button>
          
          <Button variant="outline" className="p-4 h-auto">
            <div className="text-center">
              <Filter className="w-6 h-6 text-green-500 mx-auto mb-2" />
              <div className="font-medium">Content Filters</div>
              <div className="text-xs text-gray-500 mt-1">
                Manage moderation rules
              </div>
            </div>
          </Button>
          
          <Button variant="outline" className="p-4 h-auto">
            <div className="text-center">
              <BarChart3 className="w-6 h-6 text-purple-500 mx-auto mb-2" />
              <div className="font-medium">Analytics Report</div>
              <div className="text-xs text-gray-500 mt-1">
                Generate intelligence report
              </div>
            </div>
          </Button>
          
          <Button variant="outline" className="p-4 h-auto">
            <div className="text-center">
              <Download className="w-6 h-6 text-orange-500 mx-auto mb-2" />
              <div className="font-medium">Export Data</div>
              <div className="text-xs text-gray-500 mt-1">
                Download intelligence data
              </div>
            </div>
          </Button>
        </div>
      </Card>
    </div>
  )
}

export default IntelligenceDashboard
