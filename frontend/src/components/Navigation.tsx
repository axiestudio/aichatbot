import React from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import Button from './ui/Button'

interface NavigationItem {
  name: string
  href: string
  description?: string
}

const navigationItems: NavigationItem[] = [
  {
    name: 'Overview',
    href: '/admin',
    description: 'Dashboard and analytics'
  },
  {
    name: 'Chat Design',
    href: '/admin/design',
    description: 'Customize appearance'
  },
  {
    name: 'API Configuration',
    href: '/admin/api',
    description: 'AI provider settings'
  },
  {
    name: 'Database',
    href: '/admin/database',
    description: 'Supabase integration'
  },
  {
    name: 'Instructions',
    href: '/admin/instructions',
    description: 'RAG system prompts'
  },
  {
    name: 'Analytics',
    href: '/admin/analytics',
    description: 'Usage statistics'
  }
]

interface NavigationProps {
  className?: string
}

const Navigation: React.FC<NavigationProps> = ({ className = '' }) => {
  const navigate = useNavigate()
  const { logout, user } = useAuthStore()

  const handleLogout = () => {
    logout()
    navigate('/admin/login')
  }

  return (
    <nav className={`bg-white border-r border-gray-200 ${className}`}>
      <div className="flex flex-col h-full">
        {/* Header */}
        <div className="px-6 py-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
            </div>
            <div>
              <h1 className="text-lg font-semibold text-gray-900">Admin Panel</h1>
              <p className="text-sm text-gray-500">Chatbot Management</p>
            </div>
          </div>
        </div>

        {/* Navigation Items */}
        <div className="flex-1 px-4 py-6 space-y-1">
          {navigationItems.map((item) => (
            <NavLink
              key={item.name}
              to={item.href}
              end={item.href === '/admin'}
              className={({ isActive }) =>
                `group flex flex-col px-3 py-3 rounded-lg text-sm font-medium transition-all duration-200 ${
                  isActive
                    ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-600'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                }`
              }
            >
              <span className="font-medium">{item.name}</span>
              {item.description && (
                <span className="text-xs text-gray-500 mt-0.5 group-hover:text-gray-600">
                  {item.description}
                </span>
              )}
            </NavLink>
          ))}
        </div>

        {/* User Section */}
        <div className="px-4 py-4 border-t border-gray-200">
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
          
          <Button
            variant="ghost"
            size="sm"
            onClick={handleLogout}
            fullWidth
            className="justify-start text-gray-600 hover:text-gray-900"
          >
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
            Sign Out
          </Button>
        </div>
      </div>
    </nav>
  )
}

export default Navigation
