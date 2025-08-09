import React, { useEffect } from 'react'
import { Routes, Route, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard,
  Palette,
  Settings,
  Database,
  FileText,
  BarChart3,
  Monitor,
  Brain,
  Zap,
  MessageSquare,
  Activity,
  CreditCard,
  Globe,
  Eye,
  Users
} from 'lucide-react'
import { useAuthStore } from '../stores/authStore'
import { useClientStore } from '../stores/clientStore'
import { useSuperAdminStore } from '../stores/superAdminStore'
import DashboardLayout from '../components/layout/DashboardLayout'
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
import EmbedManager from '../components/admin/EmbedManager'
import BillingManager from '../components/admin/BillingManager'

const navigation = [
  {
    name: 'Overview',
    href: '/admin',
    icon: LayoutDashboard,
    description: 'Dashboard and system status'
  },
  {
    name: 'AI Insights',
    href: '/admin/ai-insights',
    icon: Brain,
    description: 'AI-powered analytics and predictions'
  },
  {
    name: 'Intelligence Hub',
    href: '/admin/intelligence',
    icon: Zap,
    description: 'Conversation, content & knowledge intelligence'
  },
  {
    name: 'Embed Manager',
    href: '/admin/embed',
    icon: MessageSquare,
    description: 'Generate embed codes and manage chat widgets'
  },
  {
    name: 'Billing & Premium',
    href: '/admin/billing',
    icon: CreditCard,
    description: 'Manage subscription and remove branding'
  },
  {
    name: 'Live Configuration',
    href: '/admin/live-config',
    icon: Settings,
    description: 'Real-time chat interface settings'
  },
  {
    name: 'System Monitoring',
    href: '/admin/monitoring',
    icon: Monitor,
    description: 'Real-time system health and performance'
  },
  {
    name: 'Chat Design',
    href: '/admin/design',
    icon: Palette,
    description: 'Customize chat appearance'
  },
  {
    name: 'API Configuration',
    href: '/admin/api',
    icon: Settings,
    description: 'AI provider settings'
  },
  {
    name: 'Supabase Setup',
    href: '/admin/supabase',
    icon: Database,
    description: 'Database integration'
  },
  {
    name: 'RAG Instructions',
    href: '/admin/rag',
    icon: FileText,
    description: 'System prompts and context'
  },
  {
    name: 'Document Manager',
    href: '/admin/documents',
    icon: FileText,
    description: 'Upload and manage RAG documents'
  },
  {
    name: 'Analytics',
    href: '/admin/analytics',
    icon: BarChart3,
    description: 'Usage statistics and insights'
  },
]

export default function AdminDashboard() {
  const navigate = useNavigate()
  const { logout, user } = useAuthStore()
  const { client, isAuthenticated, loadChatConfig, loadActiveEmbeds, loadLiveSessions, loadAnalytics } = useClientStore()
  const { impersonatedClient, stopImpersonation } = useSuperAdminStore()

  useEffect(() => {
    // Load client data when dashboard loads
    if (isAuthenticated) {
      loadChatConfig()
      loadActiveEmbeds()
      loadLiveSessions()
      loadAnalytics()
    }
  }, [isAuthenticated])

  const handleLogout = () => {
    // If being impersonated, stop impersonation instead of logout
    if (impersonatedClient) {
      stopImpersonation()
      navigate('/super-admin')
    } else {
      logout()
    }
  }

  return (
    <DashboardLayout
      title="Admin Panel"
      subtitle={impersonatedClient ? "Super Admin View" : "Chatbot Management System"}
      navigation={navigation}
      user={user ? {
        name: user.name || 'Administrator',
        email: user.email || 'admin@chatbot.com'
      } : undefined}
      onLogout={handleLogout}
      notifications={0}
    >
      {/* Impersonation Banner */}
      {impersonatedClient && (
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <Eye className="w-5 h-5 text-yellow-400 mr-2" />
              <div>
                <p className="text-sm font-medium text-yellow-800">
                  Super Admin Mode: Viewing client dashboard
                </p>
                <p className="text-sm text-yellow-700">
                  You are currently impersonating a client admin account
                </p>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="bg-yellow-100 hover:bg-yellow-200 text-yellow-800 px-3 py-1 rounded text-sm font-medium transition-colors"
            >
              Exit Impersonation
            </button>
          </div>
        </div>
      )}

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
        <Route path="/embed" element={<EmbedManager />} />
        <Route path="/billing" element={<BillingManager />} />
      </Routes>
    </DashboardLayout>
  )
}
