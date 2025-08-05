import { useState } from 'react'
import { BarChart3, TrendingUp, MessageCircle, Clock, Users, Download } from 'lucide-react'

// Mock data for demonstration
const mockAnalytics = {
  totalChats: 1234,
  totalMessages: 5678,
  averageSessionLength: 4.2,
  topQuestions: [
    { question: "How do I reset my password?", count: 89 },
    { question: "What are your business hours?", count: 67 },
    { question: "How can I contact support?", count: 54 },
    { question: "Where can I find pricing information?", count: 43 },
    { question: "How do I cancel my subscription?", count: 38 },
  ],
  dailyStats: [
    { date: '2024-01-01', chats: 45, messages: 123 },
    { date: '2024-01-02', chats: 52, messages: 145 },
    { date: '2024-01-03', chats: 38, messages: 98 },
    { date: '2024-01-04', chats: 61, messages: 167 },
    { date: '2024-01-05', chats: 48, messages: 132 },
    { date: '2024-01-06', chats: 55, messages: 151 },
    { date: '2024-01-07', chats: 42, messages: 115 },
  ]
}

const timeRanges = [
  { value: '7d', label: 'Last 7 days' },
  { value: '30d', label: 'Last 30 days' },
  { value: '90d', label: 'Last 90 days' },
  { value: '1y', label: 'Last year' },
]

export default function Analytics() {
  const [selectedTimeRange, setSelectedTimeRange] = useState('7d')

  const exportData = () => {
    // In a real app, this would export actual data
    const csvContent = "data:text/csv;charset=utf-8," 
      + "Date,Chats,Messages\n"
      + mockAnalytics.dailyStats.map(stat => `${stat.date},${stat.chats},${stat.messages}`).join("\n")
    
    const encodedUri = encodeURI(csvContent)
    const link = document.createElement("a")
    link.setAttribute("href", encodedUri)
    link.setAttribute("download", "chatbot_analytics.csv")
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Analytics</h2>
          <p className="text-gray-600">Monitor your chatbot's performance and user interactions</p>
        </div>
        <div className="flex items-center space-x-3">
          <select 
            value={selectedTimeRange}
            onChange={(e) => setSelectedTimeRange(e.target.value)}
            className="input-field w-auto"
          >
            {timeRanges.map((range) => (
              <option key={range.value} value={range.value}>
                {range.label}
              </option>
            ))}
          </select>
          <button
            onClick={exportData}
            className="btn-secondary flex items-center"
          >
            <Download className="w-4 h-4 mr-2" />
            Export
          </button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <MessageCircle className="h-8 w-8 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total Conversations</p>
              <p className="text-2xl font-semibold text-gray-900">{mockAnalytics.totalChats.toLocaleString()}</p>
              <p className="text-sm text-green-600">+12% from last period</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <TrendingUp className="h-8 w-8 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total Messages</p>
              <p className="text-2xl font-semibold text-gray-900">{mockAnalytics.totalMessages.toLocaleString()}</p>
              <p className="text-sm text-green-600">+8% from last period</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Clock className="h-8 w-8 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Avg. Session Length</p>
              <p className="text-2xl font-semibold text-gray-900">{mockAnalytics.averageSessionLength} min</p>
              <p className="text-sm text-green-600">+5% from last period</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Users className="h-8 w-8 text-orange-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Active Users</p>
              <p className="text-2xl font-semibold text-gray-900">456</p>
              <p className="text-sm text-green-600">+15% from last period</p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Daily Activity Chart */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Daily Activity</h3>
          <div className="space-y-4">
            {mockAnalytics.dailyStats.map((stat, index) => {
              const maxChats = Math.max(...mockAnalytics.dailyStats.map(s => s.chats))
              const maxMessages = Math.max(...mockAnalytics.dailyStats.map(s => s.messages))
              const chatPercentage = (stat.chats / maxChats) * 100
              const messagePercentage = (stat.messages / maxMessages) * 100
              
              return (
                <div key={index} className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="font-medium">{new Date(stat.date).toLocaleDateString()}</span>
                    <span className="text-gray-500">{stat.chats} chats, {stat.messages} messages</span>
                  </div>
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      <span className="text-xs text-blue-600 w-12">Chats</span>
                      <div className="flex-1 bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${chatPercentage}%` }}
                        />
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="text-xs text-green-600 w-12">Messages</span>
                      <div className="flex-1 bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-green-600 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${messagePercentage}%` }}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Top Questions */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Most Asked Questions</h3>
          <div className="space-y-3">
            {mockAnalytics.topQuestions.map((item, index) => {
              const maxCount = Math.max(...mockAnalytics.topQuestions.map(q => q.count))
              const percentage = (item.count / maxCount) * 100
              
              return (
                <div key={index} className="space-y-2">
                  <div className="flex justify-between items-start">
                    <p className="text-sm font-medium text-gray-900 flex-1 pr-2">
                      {item.question}
                    </p>
                    <span className="text-sm text-gray-500 font-medium">{item.count}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>

      {/* Performance Insights */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance Insights</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="text-3xl font-bold text-green-600 mb-2">94%</div>
            <div className="text-sm text-gray-600">User Satisfaction</div>
            <div className="text-xs text-gray-500 mt-1">Based on feedback</div>
          </div>
          
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600 mb-2">1.2s</div>
            <div className="text-sm text-gray-600">Avg. Response Time</div>
            <div className="text-xs text-gray-500 mt-1">Including API calls</div>
          </div>
          
          <div className="text-center">
            <div className="text-3xl font-bold text-purple-600 mb-2">87%</div>
            <div className="text-sm text-gray-600">Resolution Rate</div>
            <div className="text-xs text-gray-500 mt-1">Questions answered successfully</div>
          </div>
        </div>
      </div>

      {/* Usage Patterns */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Usage Patterns</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium text-gray-900 mb-3">Peak Hours</h4>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">9:00 AM - 11:00 AM</span>
                <span className="text-sm font-medium">High Activity</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">2:00 PM - 4:00 PM</span>
                <span className="text-sm font-medium">Peak Activity</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">11:00 PM - 1:00 AM</span>
                <span className="text-sm font-medium">Low Activity</span>
              </div>
            </div>
          </div>
          
          <div>
            <h4 className="font-medium text-gray-900 mb-3">Common Topics</h4>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Account Support</span>
                <span className="text-sm font-medium">35%</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Product Information</span>
                <span className="text-sm font-medium">28%</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Technical Issues</span>
                <span className="text-sm font-medium">22%</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">General Inquiries</span>
                <span className="text-sm font-medium">15%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
