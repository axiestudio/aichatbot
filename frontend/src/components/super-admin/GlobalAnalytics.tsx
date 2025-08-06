import React, { useState, useEffect } from 'react'
import { BarChart3, TrendingUp, Users, DollarSign, Activity, Globe } from 'lucide-react'
import Card from '../ui/Card'

interface AnalyticsData {
  revenue: {
    total_revenue: number
    monthly_recurring_revenue: number
    revenue_by_plan: Record<string, number>
    churn_rate: number
    growth_rate: number
  }
  usage: {
    total_messages_month: number
    average_messages_per_instance: number
    top_performing_instances: Array<{
      instance_name: string
      monthly_messages: number
      plan_type: string
    }>
  }
}

const GlobalAnalytics: React.FC = () => {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [timeRange, setTimeRange] = useState('30d')

  useEffect(() => {
    loadAnalytics()
  }, [timeRange])

  const loadAnalytics = async () => {
    try {
      const token = localStorage.getItem('superAdminToken')
      
      const [revenueResponse, usageResponse] = await Promise.all([
        fetch('/api/v1/super-admin/analytics/revenue', {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch('/api/v1/super-admin/analytics/usage', {
          headers: { 'Authorization': `Bearer ${token}` }
        })
      ])

      if (revenueResponse.ok && usageResponse.ok) {
        const revenue = await revenueResponse.json()
        const usage = await usageResponse.json()
        
        setAnalytics({ revenue, usage })
      }
    } catch (error) {
      console.error('Failed to load analytics:', error)
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

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Global Analytics</h1>
          <p className="text-gray-600">Platform-wide performance metrics and insights</p>
        </div>
        <select
          value={timeRange}
          onChange={(e) => setTimeRange(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
        >
          <option value="7d">Last 7 days</option>
          <option value="30d">Last 30 days</option>
          <option value="90d">Last 90 days</option>
          <option value="1y">Last year</option>
        </select>
      </div>

      {/* Revenue Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Revenue</p>
              <p className="text-3xl font-bold text-gray-900">
                ${analytics?.revenue.total_revenue.toLocaleString() || 0}
              </p>
              <p className="text-sm text-green-600 flex items-center mt-1">
                <TrendingUp className="w-4 h-4 mr-1" />
                {analytics?.revenue.growth_rate.toFixed(1) || 0}% growth
              </p>
            </div>
            <DollarSign className="w-8 h-8 text-green-600" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Monthly Messages</p>
              <p className="text-3xl font-bold text-gray-900">
                {analytics?.usage.total_messages_month.toLocaleString() || 0}
              </p>
              <p className="text-sm text-blue-600 flex items-center mt-1">
                <Activity className="w-4 h-4 mr-1" />
                Platform activity
              </p>
            </div>
            <BarChart3 className="w-8 h-8 text-blue-600" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Churn Rate</p>
              <p className="text-3xl font-bold text-gray-900">
                {analytics?.revenue.churn_rate.toFixed(1) || 0}%
              </p>
              <p className="text-sm text-gray-600 flex items-center mt-1">
                <Users className="w-4 h-4 mr-1" />
                Customer retention
              </p>
            </div>
            <Globe className="w-8 h-8 text-purple-600" />
          </div>
        </Card>
      </div>

      {/* Revenue by Plan */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Revenue by Plan</h3>
        <div className="space-y-4">
          {analytics?.revenue.revenue_by_plan && Object.entries(analytics.revenue.revenue_by_plan).map(([plan, revenue]) => (
            <div key={plan} className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className={`w-4 h-4 rounded-full ${
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
      </Card>

      {/* Top Performing Instances */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Top Performing Instances</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-2 text-sm font-medium text-gray-600">Instance</th>
                <th className="text-left py-2 text-sm font-medium text-gray-600">Plan</th>
                <th className="text-right py-2 text-sm font-medium text-gray-600">Messages</th>
              </tr>
            </thead>
            <tbody>
              {analytics?.usage.top_performing_instances.map((instance, index) => (
                <tr key={index} className="border-b border-gray-100">
                  <td className="py-3 text-sm text-gray-900">{instance.instance_name}</td>
                  <td className="py-3">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      instance.plan_type === 'enterprise' ? 'bg-purple-100 text-purple-800' :
                      instance.plan_type === 'pro' ? 'bg-blue-100 text-blue-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {instance.plan_type.toUpperCase()}
                    </span>
                  </td>
                  <td className="py-3 text-right text-sm text-gray-900">
                    {instance.monthly_messages.toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  )
}

export default GlobalAnalytics
