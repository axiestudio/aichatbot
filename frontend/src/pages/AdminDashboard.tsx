import { Routes, Route } from 'react-router-dom'
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
  Activity
} from 'lucide-react'
import { useAuthStore } from '../stores/authStore'
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
  const { logout, user } = useAuthStore()

  const handleLogout = () => {
    logout()
  }

  return (
    <DashboardLayout
      title="Admin Panel"
      subtitle="Chatbot Management System"
      navigation={navigation}
      user={user ? {
        name: user.name || 'Administrator',
        email: user.email || 'admin@chatbot.com'
      } : undefined}
      onLogout={handleLogout}
      notifications={0}
    >
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
    </DashboardLayout>
  )
}
