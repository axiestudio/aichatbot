import { useState } from 'react'
import { Routes, Route, Link, useLocation } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import DashboardOverview from '../components/admin/DashboardOverview'
import ChatDesign from '../components/admin/ChatDesign'
import ApiConfig from '../components/admin/ApiConfig'
import SupabaseConfig from '../components/admin/SupabaseConfig'
import RagInstructions from '../components/admin/RagInstructions'
import Analytics from '../components/admin/Analytics'
import { DocumentManager } from '../components/admin/DocumentManager'
import LiveConfiguration from '../components/admin/LiveConfiguration'
import SystemMonitoring from '../components/admin/SystemMonitoring'
import AIInsightsDashboard from '../components/admin/AIInsightsDashboard'
import IntelligenceDashboard from '../components/admin/IntelligenceDashboard'

const navigation = [
  { name: 'Overview', href: '/admin', description: 'Dashboard and system status' },
  { name: 'AI Insights', href: '/admin/ai-insights', description: 'AI-powered analytics and predictions' },
  { name: 'Intelligence Hub', href: '/admin/intelligence', description: 'Conversation, content & knowledge intelligence' },
  { name: 'Live Configuration', href: '/admin/live-config', description: 'Real-time chat interface settings' },
  { name: 'System Monitoring', href: '/admin/monitoring', description: 'Real-time system health and performance' },
  { name: 'Chat Design', href: '/admin/design', description: 'Customize chat appearance' },
  { name: 'API Configuration', href: '/admin/api', description: 'AI provider settings' },
  { name: 'Supabase Setup', href: '/admin/supabase', description: 'Database integration' },
  { name: 'RAG Instructions', href: '/admin/rag', description: 'System prompts and context' },
  { name: 'Document Manager', href: '/admin/documents', description: 'Upload and manage RAG documents' },
  { name: 'Analytics', href: '/admin/analytics', description: 'Usage statistics and insights' },
]

export default function AdminDashboard() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const location = useLocation()
  const { logout, user } = useAuthStore()

  const handleLogout = () => {
    logout()
  }

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        >
          <div className="absolute inset-0 bg-gray-600 opacity-75"></div>
        </div>
      )}

      {/* Sidebar */}
      <div className={`
        fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        <div className="flex items-center justify-between h-16 px-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
            </div>
            <div>
              <h1 className="text-lg font-semibold text-gray-900">Admin Panel</h1>
              <p className="text-xs text-gray-500">Chatbot Management</p>
            </div>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden p-2 rounded-lg hover:bg-gray-100"
          >
            <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <nav className="mt-6 px-4">
          <div className="space-y-1">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`
                    group flex flex-col px-3 py-3 text-sm font-medium rounded-lg transition-all duration-200
                    ${isActive
                      ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-600'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                    }
                  `}
                  onClick={() => setSidebarOpen(false)}
                >
                  <span className="font-medium">{item.name}</span>
                  <span className="text-xs text-gray-500 mt-0.5 group-hover:text-gray-600">
                    {item.description}
                  </span>
                </Link>
              )
            })}
          </div>
        </nav>

        {/* User info and logout */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
              <svg className="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">
                {user?.name || 'Administrator'}
              </p>
              <p className="text-xs text-gray-500 truncate">
                {user?.email || 'admin@chatbot.com'}
              </p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center w-full px-3 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
            Sign Out
          </button>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top bar */}
        <header className="bg-white shadow-sm border-b border-gray-200">
          <div className="flex items-center justify-between h-16 px-6">
            <button
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden p-2 rounded-lg hover:bg-gray-100"
            >
              <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            
            <div className="flex items-center">
              <h1 className="text-2xl font-semibold text-gray-900">
                {navigation.find(item => item.href === location.pathname)?.name || 'Dashboard'}
              </h1>
            </div>

            <div className="flex items-center space-x-4">
              <Link
                to="/chat"
                target="_blank"
                rel="noopener noreferrer"
                className="btn-secondary text-sm"
              >
                Preview Chat
              </Link>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto bg-gray-50">
          <div className="p-6">
            <Routes>
              <Route path="/" element={<DashboardOverview />} />
              <Route path="/ai-insights" element={<AIInsightsDashboard />} />
              <Route path="/intelligence" element={<IntelligenceDashboard />} />
              <Route path="/live-config" element={<LiveConfiguration />} />
              <Route path="/monitoring" element={<SystemMonitoring />} />
              <Route path="/design" element={<ChatDesign />} />
              <Route path="/api" element={<ApiConfig />} />
              <Route path="/supabase" element={<SupabaseConfig />} />
              <Route path="/rag" element={<RagInstructions />} />
              <Route path="/documents" element={<DocumentManager />} />
              <Route path="/analytics" element={<Analytics />} />
            </Routes>
          </div>
        </main>
      </div>
    </div>
  )
}
