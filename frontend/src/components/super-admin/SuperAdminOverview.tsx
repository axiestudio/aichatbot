import React, { useState, useEffect } from 'react'
import { 
  Building2, 
  Users, 
  DollarSign, 
  MessageSquare, 
  TrendingUp, 
  TrendingDown,
  Activity,
  Globe,
  Crown,
  Zap
} from 'lucide-react'
import Card from '../ui/Card'
import Button from '../ui/Button'

interface GlobalMetrics {
  total_instances: number
  active_instances: number
  total_admins: number
  total_monthly_messages: number
  total_api_configurations: number
  revenue_metrics: {
    total_revenue: number
    revenue_by_plan: Record<string, number>
    average_revenue_per_user: number
  }
  growth_metrics: {
    new_instances_30d: number
    growth_rate: number
  }
}

interface SystemHealth {
  overall_status: string
  database_status: string
  api_response_time: number
  error_rate: number
  uptime_percentage: number
  active_connections: number
  memory_usage: number
  cpu_usage: number
}

const SuperAdminOverview: React.FC = () => {
  const [metrics, setMetrics] = useState<GlobalMetrics | null>(null)
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    loadDashboardData()
    
    // Refresh data every 30 seconds
    const interval = setInterval(loadDashboardData, 30000)
    return () => clearInterval(interval)
  }, [])

  const loadDashboardData = async () => {
    try {
      const token = localStorage.getItem('superAdminToken')
      
      // Load global metrics
      const metricsResponse = await fetch('/api/v1/super-admin/analytics/global-metrics', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      // Load system health
      const healthResponse = await fetch('/api/v1/super-admin/analytics/system-health', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      if (metricsResponse.ok && healthResponse.ok) {
        const metricsData = await metricsResponse.json()
        const healthData = await healthResponse.json()
        
        setMetrics(metricsData)
        setSystemHealth(healthData)
      }
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    )
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'text-green-600 bg-green-100'
      case 'degraded': return 'text-yellow-600 bg-yellow-100'
      case 'unhealthy': return 'text-red-600 bg-red-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  return (
    <div className="space-y-6">
      {/* Welcome Header */}
      <div className="bg-gradient-to-r from-purple-600 to-indigo-600 rounded-xl p-8 text-white">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center space-x-3 mb-4">
              <Crown className="w-8 h-8 text-yellow-400" />
              <h1 className="text-3xl font-bold">Super Admin Dashboard</h1>
            </div>
            <p className="text-purple-100 text-lg">
              Welcome to the platform control center. Monitor and manage all chat instances globally.
            </p>
          </div>
          <div className="text-right">
            <div className="text-4xl font-bold">{metrics?.total_instances || 0}</div>
            <div className="text-purple-200">Total Instances</div>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Instances</p>
              <p className="text-3xl font-bold text-gray-900">{metrics?.active_instances || 0}</p>
              <p className="text-sm text-green-600 flex items-center mt-1">
                <TrendingUp className="w-4 h-4 mr-1" />
                {metrics?.growth_metrics.growth_rate.toFixed(1) || 0}% growth
              </p>
            </div>
            <div className="p-3 bg-blue-100 rounded-full">
              <Building2 className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Admins</p>
              <p className="text-3xl font-bold text-gray-900">{metrics?.total_admins || 0}</p>
              <p className="text-sm text-gray-500 mt-1">Platform users</p>
            </div>
            <div className="p-3 bg-green-100 rounded-full">
              <Users className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Monthly Revenue</p>
              <p className="text-3xl font-bold text-gray-900">
                ${metrics?.revenue_metrics.total_revenue.toLocaleString() || 0}
              </p>
              <p className="text-sm text-green-600 flex items-center mt-1">
                <TrendingUp className="w-4 h-4 mr-1" />
                MRR Growth
              </p>
            </div>
            <div className="p-3 bg-purple-100 rounded-full">
              <DollarSign className="w-6 h-6 text-purple-600" />
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Monthly Messages</p>
              <p className="text-3xl font-bold text-gray-900">
                {metrics?.total_monthly_messages.toLocaleString() || 0}
              </p>
              <p className="text-sm text-blue-600 flex items-center mt-1">
                <Activity className="w-4 h-4 mr-1" />
                Platform usage
              </p>
            </div>
            <div className="p-3 bg-orange-100 rounded-full">
              <MessageSquare className="w-6 h-6 text-orange-600" />
            </div>
          </div>
        </Card>
      </div>

      {/* System Health & Revenue Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* System Health */}
        <Card className="p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">System Health</h3>
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(systemHealth?.overall_status || 'unknown')}`}>
              {systemHealth?.overall_status?.toUpperCase() || 'UNKNOWN'}
            </span>
          </div>

          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Database</span>
              <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(systemHealth?.database_status || 'unknown')}`}>
                {systemHealth?.database_status?.toUpperCase() || 'UNKNOWN'}
              </span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">API Response Time</span>
              <span className="text-sm font-medium text-gray-900">
                {systemHealth?.api_response_time || 0}ms
              </span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Uptime</span>
              <span className="text-sm font-medium text-green-600">
                {systemHealth?.uptime_percentage || 0}%
              </span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Error Rate</span>
              <span className="text-sm font-medium text-gray-900">
                {systemHealth?.error_rate || 0}%
              </span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Active Connections</span>
              <span className="text-sm font-medium text-gray-900">
                {systemHealth?.active_connections || 0}
              </span>
            </div>
          </div>
        </Card>

        {/* Revenue Breakdown */}
        <Card className="p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">Revenue by Plan</h3>
            <Button size="sm" variant="outline">View Details</Button>
          </div>

          <div className="space-y-4">
            {metrics?.revenue_metrics.revenue_by_plan && Object.entries(metrics.revenue_metrics.revenue_by_plan).map(([plan, revenue]) => (
              <div key={plan} className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className={`w-3 h-3 rounded-full ${
                    plan === 'enterprise' ? 'bg-purple-500' :
                    plan === 'pro' ? 'bg-blue-500' : 'bg-gray-400'
                  }`}></div>
                  <span className="text-sm font-medium text-gray-900 capitalize">{plan}</span>
                </div>
                <span className="text-sm font-medium text-gray-900">
                  ${revenue.toLocaleString()}
                </span>
              </div>
            ))}
          </div>

          <div className="mt-6 pt-4 border-t border-gray-200">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-900">Average Revenue per User</span>
              <span className="text-sm font-bold text-purple-600">
                ${metrics?.revenue_metrics.average_revenue_per_user.toFixed(2) || 0}
              </span>
            </div>
          </div>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Button className="flex items-center justify-center space-x-2 p-4">
            <Building2 className="w-5 h-5" />
            <span>Create New Instance</span>
          </Button>
          
          <Button variant="outline" className="flex items-center justify-center space-x-2 p-4">
            <Globe className="w-5 h-5" />
            <span>View Global Analytics</span>
          </Button>
          
          <Button variant="outline" className="flex items-center justify-center space-x-2 p-4">
            <Zap className="w-5 h-5" />
            <span>System Optimization</span>
          </Button>
        </div>
      </Card>
    </div>
  )
}

export default SuperAdminOverview
