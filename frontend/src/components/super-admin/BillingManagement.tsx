import React, { useState, useEffect } from 'react'
import { CreditCard, AlertTriangle, TrendingUp, DollarSign } from 'lucide-react'
import Card from '../ui/Card'
import Button from '../ui/Button'
import Badge from '../ui/Badge'

interface BillingOverview {
  total_monthly_revenue: number
  total_yearly_potential: number
  revenue_by_plan: Record<string, any>
  total_customers: number
  approaching_limit: Array<{
    instance_id: string
    name: string
    usage_percentage: number
    plan_type: string
  }>
  churn_risk: number
}

interface UsageAlert {
  instance_id: string
  instance_name: string
  alert_type: string
  message: string
  severity: string
  created_at: string
}

const BillingManagement: React.FC = () => {
  const [overview, setOverview] = useState<BillingOverview | null>(null)
  const [alerts, setAlerts] = useState<UsageAlert[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    loadBillingData()
  }, [])

  const loadBillingData = async () => {
    try {
      const token = localStorage.getItem('superAdminToken')
      
      const [overviewResponse, alertsResponse] = await Promise.all([
        fetch('/api/v1/super-admin/billing/overview', {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch('/api/v1/super-admin/billing/alerts', {
          headers: { 'Authorization': `Bearer ${token}` }
        })
      ])

      if (overviewResponse.ok && alertsResponse.ok) {
        const overviewData = await overviewResponse.json()
        const alertsData = await alertsResponse.json()
        
        setOverview(overviewData)
        setAlerts(alertsData)
      }
    } catch (error) {
      console.error('Failed to load billing data:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'error'
      case 'high': return 'warning'
      case 'medium': return 'info'
      case 'low': return 'success'
      default: return 'default'
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
          <h1 className="text-2xl font-bold text-gray-900">Billing Management</h1>
          <p className="text-gray-600">Monitor revenue, subscriptions, and usage alerts</p>
        </div>
        <Button>Generate Report</Button>
      </div>

      {/* Revenue Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Monthly Revenue</p>
              <p className="text-3xl font-bold text-gray-900">
                ${overview?.total_monthly_revenue.toLocaleString() || 0}
              </p>
              <p className="text-sm text-green-600 flex items-center mt-1">
                <TrendingUp className="w-4 h-4 mr-1" />
                MRR
              </p>
            </div>
            <DollarSign className="w-8 h-8 text-green-600" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Yearly Potential</p>
              <p className="text-3xl font-bold text-gray-900">
                ${overview?.total_yearly_potential.toLocaleString() || 0}
              </p>
              <p className="text-sm text-blue-600 mt-1">ARR Potential</p>
            </div>
            <CreditCard className="w-8 h-8 text-blue-600" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Customers</p>
              <p className="text-3xl font-bold text-gray-900">
                {overview?.total_customers || 0}
              </p>
              <p className="text-sm text-purple-600 mt-1">Active Subscriptions</p>
            </div>
            <CreditCard className="w-8 h-8 text-purple-600" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Churn Risk</p>
              <p className="text-3xl font-bold text-red-600">
                {overview?.churn_risk || 0}
              </p>
              <p className="text-sm text-red-600 mt-1">High Usage</p>
            </div>
            <AlertTriangle className="w-8 h-8 text-red-600" />
          </div>
        </Card>
      </div>

      {/* Revenue by Plan */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Revenue Breakdown by Plan</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {overview?.revenue_by_plan && Object.entries(overview.revenue_by_plan).map(([plan, data]: [string, any]) => (
            <div key={plan} className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium text-gray-900 capitalize">{plan}</h4>
                <Badge variant={plan === 'enterprise' ? 'default' : plan === 'pro' ? 'info' : 'warning'}>
                  {data.count} customers
                </Badge>
              </div>
              <div className="space-y-1">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Monthly Revenue:</span>
                  <span className="font-medium">${data.monthly_revenue.toLocaleString()}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Yearly Potential:</span>
                  <span className="font-medium">${data.yearly_potential.toLocaleString()}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Usage Alerts */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Usage Alerts</h3>
          <Badge variant="error">{alerts.length} alerts</Badge>
        </div>
        
        {alerts.length > 0 ? (
          <div className="space-y-3">
            {alerts.map((alert, index) => (
              <div key={index} className="flex items-start space-x-3 p-4 bg-gray-50 rounded-lg">
                <AlertTriangle className={`w-5 h-5 mt-0.5 ${
                  alert.severity === 'critical' ? 'text-red-500' :
                  alert.severity === 'medium' ? 'text-yellow-500' : 'text-blue-500'
                }`} />
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <h4 className="font-medium text-gray-900">{alert.instance_name}</h4>
                    <Badge variant={getSeverityColor(alert.severity)}>
                      {alert.severity.toUpperCase()}
                    </Badge>
                  </div>
                  <p className="text-sm text-gray-600 mt-1">{alert.message}</p>
                  <p className="text-xs text-gray-500 mt-2">
                    {new Date(alert.created_at).toLocaleString()}
                  </p>
                </div>
                <Button size="sm" variant="outline">
                  View Instance
                </Button>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <AlertTriangle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">No usage alerts at this time</p>
          </div>
        )}
      </Card>

      {/* Instances Approaching Limits */}
      {overview?.approaching_limit && overview.approaching_limit.length > 0 && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Instances Approaching Limits</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-2 text-sm font-medium text-gray-600">Instance</th>
                  <th className="text-left py-2 text-sm font-medium text-gray-600">Plan</th>
                  <th className="text-right py-2 text-sm font-medium text-gray-600">Usage</th>
                  <th className="text-right py-2 text-sm font-medium text-gray-600">Actions</th>
                </tr>
              </thead>
              <tbody>
                {overview.approaching_limit.map((instance, index) => (
                  <tr key={index} className="border-b border-gray-100">
                    <td className="py-3 text-sm text-gray-900">{instance.name}</td>
                    <td className="py-3">
                      <Badge variant={instance.plan_type === 'enterprise' ? 'default' : instance.plan_type === 'pro' ? 'info' : 'warning'}>
                        {instance.plan_type.toUpperCase()}
                      </Badge>
                    </td>
                    <td className="py-3 text-right">
                      <span className={`text-sm font-medium ${
                        instance.usage_percentage > 95 ? 'text-red-600' :
                        instance.usage_percentage > 80 ? 'text-yellow-600' : 'text-green-600'
                      }`}>
                        {instance.usage_percentage.toFixed(1)}%
                      </span>
                    </td>
                    <td className="py-3 text-right">
                      <Button size="sm" variant="outline">
                        Upgrade Plan
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  )
}

export default BillingManagement
