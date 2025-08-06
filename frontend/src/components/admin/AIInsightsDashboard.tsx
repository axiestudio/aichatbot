import React, { useState, useEffect } from 'react'
import { 
  Brain, 
  TrendingUp, 
  TrendingDown, 
  Zap, 
  Shield, 
  Users, 
  BarChart3,
  PieChart,
  Activity,
  AlertTriangle,
  CheckCircle,
  Target,
  Lightbulb,
  Rocket,
  Eye,
  Clock,
  DollarSign
} from 'lucide-react'
import Card from '../ui/Card'
import Badge from '../ui/Badge'
import Button from '../ui/Button'

interface AIInsight {
  type: string
  title: string
  description: string
  confidence: number
  impact: string
  recommendation: string
  data: any
}

interface DashboardData {
  timestamp: string
  instance_id?: string
  core_metrics: {
    messages_24h: number
    messages_last_hour: number
    avg_response_time_ms: number
    active_sessions: number
    messages_per_minute: number
  }
  user_analytics: {
    engagement: {
      avg_session_duration: number
      messages_per_session: number
      engagement_rate: number
      peak_hours: string[]
    }
    retention_rate: number
    bounce_rate: number
  }
  performance_insights: {
    performance_score: number
    response_time_analysis: {
      avg_response_time: number
      trend: string
      anomalies_detected: number
    }
    error_analysis: {
      error_rate: number
      error_trend: string
    }
  }
  business_metrics: {
    conversions: {
      conversion_rate: number
      conversion_trend: string
    }
    user_satisfaction: {
      overall_score: number
      satisfaction_trend: string
    }
    roi_score: {
      score: number
      roi_percentage: number
    }
  }
  ai_insights: AIInsight[]
  predictions: {
    traffic: {
      next_hour: { predicted_requests: number; confidence: number }
      next_day: { predicted_requests: number; confidence: number }
    }
    confidence_score: number
  }
  health_score: number
}

const AIInsightsDashboard: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [selectedTimeframe, setSelectedTimeframe] = useState('24h')
  const [autoRefresh, setAutoRefresh] = useState(true)

  useEffect(() => {
    loadDashboardData()
    
    let interval: NodeJS.Timeout
    if (autoRefresh) {
      interval = setInterval(loadDashboardData, 30000) // Refresh every 30 seconds
    }
    
    return () => {
      if (interval) clearInterval(interval)
    }
  }, [autoRefresh, selectedTimeframe])

  const loadDashboardData = async () => {
    try {
      const token = localStorage.getItem('adminToken')
      const response = await fetch('/api/v1/analytics/dashboard', {
        headers: { 'Authorization': `Bearer ${token}` }
      })

      if (response.ok) {
        const data = await response.json()
        setDashboardData(data)
      }
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const getHealthScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600'
    if (score >= 80) return 'text-blue-600'
    if (score >= 70) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'high': return 'error'
      case 'medium': return 'warning'
      case 'low': return 'success'
      default: return 'default'
    }
  }

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'increasing':
      case 'accelerating':
        return <TrendingUp className="w-4 h-4 text-green-500" />
      case 'decreasing':
        return <TrendingDown className="w-4 h-4 text-red-500" />
      default:
        return <Activity className="w-4 h-4 text-gray-500" />
    }
  }

  const formatNumber = (num: number) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`
    return num.toString()
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (!dashboardData) {
    return (
      <div className="text-center py-12">
        <AlertTriangle className="w-12 h-12 text-yellow-500 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No Data Available</h3>
        <p className="text-gray-600">Unable to load dashboard data. Please try again.</p>
        <Button onClick={loadDashboardData} className="mt-4">
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
            AI Insights Dashboard
          </h1>
          <p className="text-gray-600">AI-powered analytics and predictive insights</p>
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
            <Activity className={`w-4 h-4 mr-2 ${autoRefresh ? 'animate-pulse' : ''}`} />
            Auto Refresh
          </Button>
        </div>
      </div>

      {/* Health Score */}
      <Card className="p-6 bg-gradient-to-r from-purple-50 to-blue-50">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Overall Health Score</h3>
            <div className={`text-4xl font-bold ${getHealthScoreColor(dashboardData.health_score)}`}>
              {dashboardData.health_score.toFixed(1)}%
            </div>
            <p className="text-sm text-gray-600 mt-1">
              System performing {dashboardData.health_score >= 90 ? 'excellently' : 
                               dashboardData.health_score >= 80 ? 'well' : 
                               dashboardData.health_score >= 70 ? 'adequately' : 'poorly'}
            </p>
          </div>
          <div className="text-right">
            <div className="w-24 h-24 relative">
              <svg className="w-24 h-24 transform -rotate-90" viewBox="0 0 100 100">
                <circle
                  cx="50"
                  cy="50"
                  r="40"
                  stroke="currentColor"
                  strokeWidth="8"
                  fill="transparent"
                  className="text-gray-200"
                />
                <circle
                  cx="50"
                  cy="50"
                  r="40"
                  stroke="currentColor"
                  strokeWidth="8"
                  fill="transparent"
                  strokeDasharray={`${2 * Math.PI * 40}`}
                  strokeDashoffset={`${2 * Math.PI * 40 * (1 - dashboardData.health_score / 100)}`}
                  className={getHealthScoreColor(dashboardData.health_score)}
                  strokeLinecap="round"
                />
              </svg>
            </div>
          </div>
        </div>
      </Card>

      {/* Core Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Messages (24h)</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatNumber(dashboardData.core_metrics.messages_24h)}
              </p>
            </div>
            <Users className="w-8 h-8 text-blue-600" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Sessions</p>
              <p className="text-2xl font-bold text-gray-900">
                {dashboardData.core_metrics.active_sessions}
              </p>
            </div>
            <Activity className="w-8 h-8 text-green-600" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Avg Response</p>
              <p className="text-2xl font-bold text-gray-900">
                {dashboardData.core_metrics.avg_response_time_ms}ms
              </p>
            </div>
            <Clock className="w-8 h-8 text-purple-600" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Engagement Rate</p>
              <p className="text-2xl font-bold text-gray-900">
                {dashboardData.user_analytics.engagement.engagement_rate}%
              </p>
            </div>
            <Target className="w-8 h-8 text-orange-600" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">ROI Score</p>
              <p className="text-2xl font-bold text-gray-900">
                {dashboardData.business_metrics.roi_score.score}%
              </p>
            </div>
            <DollarSign className="w-8 h-8 text-green-600" />
          </div>
        </Card>
      </div>

      {/* AI Insights */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center">
            <Lightbulb className="w-5 h-5 text-yellow-500 mr-2" />
            AI-Powered Insights
          </h3>
          <Badge variant="success">
            {dashboardData.ai_insights.length} Active Insights
          </Badge>
        </div>

        <div className="space-y-4">
          {dashboardData.ai_insights.slice(0, 5).map((insight, index) => (
            <div key={index} className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center space-x-2">
                  <Badge variant={getImpactColor(insight.impact)}>
                    {insight.impact.toUpperCase()}
                  </Badge>
                  <span className="text-sm text-gray-500">
                    {(insight.confidence * 100).toFixed(0)}% confidence
                  </span>
                </div>
                <div className="text-xs text-gray-400">
                  {insight.type}
                </div>
              </div>
              
              <h4 className="font-medium text-gray-900 mb-1">{insight.title}</h4>
              <p className="text-sm text-gray-600 mb-2">{insight.description}</p>
              
              <div className="bg-blue-50 border border-blue-200 rounded p-3">
                <p className="text-sm text-blue-800">
                  <strong>Recommendation:</strong> {insight.recommendation}
                </p>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Predictions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Eye className="w-5 h-5 text-blue-500 mr-2" />
            Traffic Predictions
          </h3>
          
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Next Hour</span>
              <div className="text-right">
                <div className="font-semibold">
                  {formatNumber(dashboardData.predictions.traffic.next_hour.predicted_requests)} requests
                </div>
                <div className="text-xs text-gray-500">
                  {(dashboardData.predictions.traffic.next_hour.confidence * 100).toFixed(0)}% confidence
                </div>
              </div>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Next Day</span>
              <div className="text-right">
                <div className="font-semibold">
                  {formatNumber(dashboardData.predictions.traffic.next_day.predicted_requests)} requests
                </div>
                <div className="text-xs text-gray-500">
                  {(dashboardData.predictions.traffic.next_day.confidence * 100).toFixed(0)}% confidence
                </div>
              </div>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <BarChart3 className="w-5 h-5 text-green-500 mr-2" />
            Performance Trends
          </h3>
          
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Response Time</span>
              <div className="flex items-center space-x-2">
                {getTrendIcon(dashboardData.performance_insights.response_time_analysis.trend)}
                <span className="font-semibold">
                  {dashboardData.performance_insights.response_time_analysis.avg_response_time}ms
                </span>
              </div>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Error Rate</span>
              <div className="flex items-center space-x-2">
                {getTrendIcon(dashboardData.performance_insights.error_analysis.error_trend)}
                <span className="font-semibold">
                  {dashboardData.performance_insights.error_analysis.error_rate}%
                </span>
              </div>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">User Satisfaction</span>
              <div className="flex items-center space-x-2">
                {getTrendIcon(dashboardData.business_metrics.user_satisfaction.satisfaction_trend)}
                <span className="font-semibold">
                  {dashboardData.business_metrics.user_satisfaction.overall_score}%
                </span>
              </div>
            </div>
          </div>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <Rocket className="w-5 h-5 text-purple-500 mr-2" />
          Recommended Actions
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Button variant="outline" className="p-4 h-auto">
            <div className="text-center">
              <Zap className="w-6 h-6 text-yellow-500 mx-auto mb-2" />
              <div className="font-medium">Optimize Performance</div>
              <div className="text-xs text-gray-500 mt-1">
                Implement caching improvements
              </div>
            </div>
          </Button>
          
          <Button variant="outline" className="p-4 h-auto">
            <div className="text-center">
              <Shield className="w-6 h-6 text-blue-500 mx-auto mb-2" />
              <div className="font-medium">Enhance Security</div>
              <div className="text-xs text-gray-500 mt-1">
                Review security patterns
              </div>
            </div>
          </Button>
          
          <Button variant="outline" className="p-4 h-auto">
            <div className="text-center">
              <Users className="w-6 h-6 text-green-500 mx-auto mb-2" />
              <div className="font-medium">Boost Engagement</div>
              <div className="text-xs text-gray-500 mt-1">
                Implement engagement features
              </div>
            </div>
          </Button>
        </div>
      </Card>
    </div>
  )
}

export default AIInsightsDashboard
