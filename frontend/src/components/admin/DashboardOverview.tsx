import React from 'react'
import PageHeader from '../PageHeader'
import StatsCard from '../StatsCard'
import Card from '../ui/Card'
import Button from '../ui/Button'

export default function DashboardOverview() {
  const stats = [
    {
      title: 'Total Conversations',
      value: '1,234',
      change: { value: '+12%', type: 'increase' as const, period: 'vs last month' },
      description: 'Messages processed this month'
    },
    {
      title: 'Active Users',
      value: '456',
      change: { value: '+8%', type: 'increase' as const, period: 'vs last month' },
      description: 'Unique users this month'
    },
    {
      title: 'Response Rate',
      value: '98.5%',
      change: { value: '+2.1%', type: 'increase' as const, period: 'vs last month' },
      description: 'Successful AI responses'
    },
    {
      title: 'Configurations',
      value: '3',
      change: { value: '0', type: 'neutral' as const, period: 'active configs' },
      description: 'Chat configurations'
    },
  ]

  const recentActivity = [
    {
      id: 1,
      type: 'chat',
      message: 'New conversation started',
      time: '2 minutes ago',
      user: 'Anonymous User',
    },
    {
      id: 2,
      type: 'config',
      message: 'Chat design updated',
      time: '1 hour ago',
      user: 'Admin User',
    },
    {
      id: 3,
      type: 'api',
      message: 'API configuration saved',
      time: '3 hours ago',
      user: 'Admin User',
    },
    {
      id: 4,
      type: 'chat',
      message: 'New conversation started',
      time: '5 hours ago',
      user: 'Anonymous User',
    },
  ]

  return (
    <div className="space-y-6">
      <PageHeader
        title="Dashboard Overview"
        description="Monitor your chatbot's performance and usage statistics in real-time."
        actions={
          <div className="flex space-x-3">
            <Button variant="outline" size="sm">
              Export Data
            </Button>
            <Button size="sm">
              View Analytics
            </Button>
          </div>
        }
      />

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <StatsCard
            key={stat.title}
            title={stat.title}
            value={stat.value}
            change={stat.change}
            description={stat.description}
          />
        ))}
      </div>
      {/* Quick Actions and Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Quick Actions */}
        <Card>
          <h3 className="text-lg font-semibold text-gray-900 mb-6">Quick Actions</h3>
          <div className="space-y-3">
            <button className="w-full text-left p-4 rounded-lg border border-gray-200 hover:bg-gray-50 hover:border-gray-300 transition-all duration-200">
              <div>
                <p className="font-medium text-gray-900 mb-1">Configure Chat Design</p>
                <p className="text-sm text-gray-500">Customize appearance and behavior</p>
              </div>
            </button>

            <button className="w-full text-left p-4 rounded-lg border border-gray-200 hover:bg-gray-50 hover:border-gray-300 transition-all duration-200">
              <div>
                <p className="font-medium text-gray-900 mb-1">Update RAG Instructions</p>
                <p className="text-sm text-gray-500">Modify AI behavior and responses</p>
              </div>
            </button>

            <button className="w-full text-left p-4 rounded-lg border border-gray-200 hover:bg-gray-50 hover:border-gray-300 transition-all duration-200">
              <div>
                <p className="font-medium text-gray-900 mb-1">View Analytics</p>
                <p className="text-sm text-gray-500">Monitor performance and usage</p>
              </div>
            </button>
          </div>
        </Card>

        {/* Recent Activity */}
        <Card>
          <h3 className="text-lg font-semibold text-gray-900 mb-6">Recent Activity</h3>
          <div className="space-y-4">
            {recentActivity.map((activity) => (
              <div key={activity.id} className="flex items-start space-x-3 pb-4 border-b border-gray-100 last:border-b-0 last:pb-0">
                <div className={`w-2 h-2 rounded-full mt-2 flex-shrink-0 ${
                  activity.type === 'chat' ? 'bg-green-500' :
                  activity.type === 'config' ? 'bg-blue-500' :
                  'bg-yellow-500'
                }`} />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900">{activity.message}</p>
                  <p className="text-xs text-gray-500 mt-1">{activity.user} • {activity.time}</p>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* System Status */}
      <Card>
        <h3 className="text-lg font-semibold text-gray-900 mb-6">System Status</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="flex items-center space-x-3">
            <div className="w-3 h-3 bg-green-500 rounded-full flex-shrink-0"></div>
            <div>
              <p className="text-sm font-medium text-gray-900">Chat Interface</p>
              <p className="text-xs text-gray-500">Operational</p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <div className="w-3 h-3 bg-yellow-500 rounded-full flex-shrink-0"></div>
            <div>
              <p className="text-sm font-medium text-gray-900">API Connection</p>
              <p className="text-xs text-gray-500">Needs Configuration</p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <div className="w-3 h-3 bg-red-500 rounded-full flex-shrink-0"></div>
            <div>
              <p className="text-sm font-medium text-gray-900">Supabase</p>
              <p className="text-xs text-gray-500">Not Connected</p>
            </div>
          </div>
        </div>
      </Card>
    </div>
  )
}
