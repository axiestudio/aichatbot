import React, { useState, useEffect } from 'react'
import { Routes, Route, Link, useLocation, Navigate, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard,
  Building2,
  BarChart3,
  CreditCard,
  Users,
  Settings,
  LogOut,
  Crown,
  Globe,
  TrendingUp,
  AlertTriangle,
  Eye,
  UserPlus
} from 'lucide-react'
import { useSuperAdminStore } from '../stores/superAdminStore'
import DashboardLayout from '../components/layout/DashboardLayout'
import Button from '../components/ui/Button'
import Card from '../components/ui/Card'
import Badge from '../components/ui/Badge'

// Super Admin Components (we'll create these)
// import SuperAdminOverview from '../components/super-admin/SuperAdminOverview'
// import InstanceManagement from '../components/super-admin/InstanceManagement'
// import GlobalAnalytics from '../components/super-admin/GlobalAnalytics'
// import BillingManagement from '../components/super-admin/BillingManagement'
// import SuperAdminSettings from '../components/super-admin/SuperAdminSettings'

const SuperAdminDashboard: React.FC = () => {
  const location = useLocation()
  const navigate = useNavigate()
  const [isSidebarOpen, setIsSidebarOpen] = useState(true)
  const [notifications, setNotifications] = useState(0)

  const {
    superAdmin,
    isAuthenticated,
    clients,
    systemStats,
    impersonatedClient,
    loadClients,
    loadSystemStats,
    impersonateClient,
    stopImpersonation,
    logout
  } = useSuperAdminStore()

  useEffect(() => {
    if (!isAuthenticated || !superAdmin) {
      navigate('/super-admin/login')
      return
    }

    loadClients()
    loadSystemStats()
  }, [isAuthenticated, superAdmin])

  const navigation = [
    {
      name: 'Overview',
      href: '/super-admin',
      icon: LayoutDashboard,
      current: location.pathname === '/super-admin'
    },
    {
      name: 'Instances',
      href: '/super-admin/instances',
      icon: Building2,
      current: location.pathname.startsWith('/super-admin/instances')
    },
    {
      name: 'Analytics',
      href: '/super-admin/analytics',
      icon: BarChart3,
      current: location.pathname.startsWith('/super-admin/analytics')
    },
    {
      name: 'Billing',
      href: '/super-admin/billing',
      icon: CreditCard,
      current: location.pathname.startsWith('/super-admin/billing')
    },
    {
      name: 'Settings',
      href: '/super-admin/settings',
      icon: Settings,
      current: location.pathname.startsWith('/super-admin/settings')
    }
  ]

  useEffect(() => {
    // Load notifications count
    fetchNotifications()
  }, [])

  const fetchNotifications = async () => {
    try {
      const response = await fetch('/api/v1/super-admin/billing/alerts', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('superAdminToken')}`
        }
      })
      if (response.ok) {
        const alerts = await response.json()
        setNotifications(alerts.length)
      }
    } catch (error) {
      console.error('Failed to fetch notifications:', error)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('superAdminToken')
    window.location.href = '/super-admin/login'
  }

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <div className={`${isSidebarOpen ? 'w-64' : 'w-16'} bg-gradient-to-b from-purple-900 to-indigo-900 text-white transition-all duration-300 flex flex-col`}>
        {/* Logo */}
        <div className="p-6 border-b border-purple-800">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-lg flex items-center justify-center">
              <Crown className="w-6 h-6 text-white" />
            </div>
            {isSidebarOpen && (
              <div>
                <h1 className="text-xl font-bold">Super Admin</h1>
                <p className="text-purple-300 text-sm">Platform Control</p>
              </div>
            )}
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-4 py-6 space-y-2">
          {navigation.map((item) => {
            const Icon = item.icon
            return (
              <Link
                key={item.name}
                to={item.href}
                className={`
                  flex items-center px-3 py-3 rounded-lg text-sm font-medium transition-colors
                  ${item.current 
                    ? 'bg-purple-800 text-white' 
                    : 'text-purple-200 hover:bg-purple-800 hover:text-white'
                  }
                `}
              >
                <Icon className="w-5 h-5 mr-3" />
                {isSidebarOpen && item.name}
                {item.name === 'Billing' && notifications > 0 && (
                  <span className="ml-auto bg-red-500 text-white text-xs rounded-full px-2 py-1">
                    {notifications}
                  </span>
                )}
              </Link>
            )
          })}
        </nav>

        {/* User Menu */}
        <div className="p-4 border-t border-purple-800">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-purple-600 rounded-full flex items-center justify-center">
              <Users className="w-4 h-4" />
            </div>
            {isSidebarOpen && (
              <div className="flex-1">
                <p className="text-sm font-medium">Super Admin</p>
                <p className="text-xs text-purple-300">Platform Manager</p>
              </div>
            )}
          </div>
          {isSidebarOpen && (
            <button
              onClick={handleLogout}
              className="mt-3 w-full flex items-center px-3 py-2 text-sm text-purple-200 hover:text-white hover:bg-purple-800 rounded-lg transition-colors"
            >
              <LogOut className="w-4 h-4 mr-2" />
              Logout
            </button>
          )}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setIsSidebarOpen(!isSidebarOpen)}
                className="p-2 rounded-lg hover:bg-gray-100"
              >
                <LayoutDashboard className="w-5 h-5" />
              </button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Super Admin Dashboard</h1>
                <p className="text-gray-600">Manage all chat instances and platform operations</p>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              {/* Quick Stats */}
              <div className="hidden md:flex items-center space-x-6">
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">99.9%</div>
                  <div className="text-xs text-gray-500">Uptime</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">
                    <Globe className="w-6 h-6 inline" />
                  </div>
                  <div className="text-xs text-gray-500">Global</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-600">
                    <TrendingUp className="w-6 h-6 inline" />
                  </div>
                  <div className="text-xs text-gray-500">Growing</div>
                </div>
              </div>

              {/* Notifications */}
              {notifications > 0 && (
                <Link
                  to="/super-admin/billing"
                  className="relative p-2 text-gray-600 hover:text-gray-900"
                >
                  <AlertTriangle className="w-6 h-6" />
                  <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full px-2 py-1">
                    {notifications}
                  </span>
                </Link>
              )}
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto bg-gray-50">
          <div className="p-6">
            <Routes>
              <Route path="/" element={<SuperAdminOverview />} />
              <Route path="/instances/*" element={<InstanceManagement />} />
              <Route path="/analytics/*" element={<GlobalAnalytics />} />
              <Route path="/billing/*" element={<BillingManagement />} />
              <Route path="/settings/*" element={<SuperAdminSettings />} />
              <Route path="*" element={<Navigate to="/super-admin" replace />} />
            </Routes>
          </div>
        </main>
      </div>
    </div>
  )
}

export default SuperAdminDashboard
