import React, { useState, useEffect, useRef } from 'react'
import { MessageSquare, X, Minimize2, Maximize2 } from 'lucide-react'
import EnhancedChatInterface from '../chat/EnhancedChatInterface'
import { ChatConfig } from '../../types'

interface EmbeddableChatProps {
  tenantId: string
  embedConfig?: {
    position?: 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left' | 'center'
    theme?: 'light' | 'dark' | 'auto'
    size?: 'small' | 'medium' | 'large' | 'fullscreen'
    showLauncher?: boolean
    launcherText?: string
    allowedDomains?: string[]
    customCSS?: string
    autoOpen?: boolean
    openDelay?: number
  }
  onLoad?: () => void
  onError?: (error: string) => void
}

const EmbeddableChat: React.FC<EmbeddableChatProps> = ({
  tenantId,
  embedConfig = {},
  onLoad,
  onError
}) => {
  const [isOpen, setIsOpen] = useState(false)
  const [isMinimized, setIsMinimized] = useState(false)
  const [config, setConfig] = useState<ChatConfig | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [unreadCount, setUnreadCount] = useState(0)
  
  const chatRef = useRef<HTMLDivElement>(null)
  const launcherRef = useRef<HTMLButtonElement>(null)

  const {
    position = 'bottom-right',
    theme = 'auto',
    size = 'medium',
    showLauncher = true,
    launcherText = 'Chat with us',
    allowedDomains = [],
    customCSS = '',
    autoOpen = false,
    openDelay = 0
  } = embedConfig

  useEffect(() => {
    initializeChat()
    
    if (autoOpen && openDelay > 0) {
      setTimeout(() => setIsOpen(true), openDelay)
    } else if (autoOpen) {
      setIsOpen(true)
    }
  }, [tenantId, autoOpen, openDelay])

  useEffect(() => {
    // Security check - validate domain
    if (allowedDomains.length > 0) {
      const currentDomain = window.location.hostname
      const isAllowed = allowedDomains.some(domain => 
        currentDomain === domain || currentDomain.endsWith(`.${domain}`)
      )
      
      if (!isAllowed) {
        setError('Domain not authorized for this chat widget')
        onError?.('Domain not authorized')
        return
      }
    }

    // Apply custom CSS
    if (customCSS) {
      const styleElement = document.createElement('style')
      styleElement.textContent = customCSS
      document.head.appendChild(styleElement)
      
      return () => {
        document.head.removeChild(styleElement)
      }
    }
  }, [allowedDomains, customCSS, onError])

  const initializeChat = async () => {
    try {
      setLoading(true)
      
      // Load tenant configuration
      const response = await fetch(`/api/v1/embed/${tenantId}/config`)
      
      if (!response.ok) {
        throw new Error(`Failed to load chat configuration: ${response.statusText}`)
      }
      
      const configData = await response.json()
      setConfig(configData)
      onLoad?.()
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to initialize chat'
      setError(errorMessage)
      onError?.(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const getPositionClasses = () => {
    const baseClasses = 'fixed z-50'
    
    switch (position) {
      case 'bottom-right':
        return `${baseClasses} bottom-4 right-4`
      case 'bottom-left':
        return `${baseClasses} bottom-4 left-4`
      case 'top-right':
        return `${baseClasses} top-4 right-4`
      case 'top-left':
        return `${baseClasses} top-4 left-4`
      case 'center':
        return `${baseClasses} top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2`
      default:
        return `${baseClasses} bottom-4 right-4`
    }
  }

  const getSizeClasses = () => {
    if (size === 'fullscreen') {
      return 'w-screen h-screen'
    }
    
    switch (size) {
      case 'small':
        return 'w-80 h-96'
      case 'medium':
        return 'w-96 h-[500px]'
      case 'large':
        return 'w-[500px] h-[600px]'
      default:
        return 'w-96 h-[500px]'
    }
  }

  const getThemeClasses = () => {
    if (theme === 'auto') {
      return 'theme-auto'
    }
    return theme === 'dark' ? 'theme-dark' : 'theme-light'
  }

  if (error) {
    return (
      <div className={getPositionClasses()}>
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 max-w-sm">
          <div className="flex items-center">
            <X className="w-5 h-5 text-red-600 mr-2" />
            <span className="text-red-800 text-sm">{error}</span>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className={`embeddable-chat ${getThemeClasses()}`}>
      {/* Chat Launcher */}
      {showLauncher && !isOpen && (
        <button
          ref={launcherRef}
          onClick={() => setIsOpen(true)}
          className={`${getPositionClasses()} bg-blue-600 hover:bg-blue-700 text-white rounded-full p-4 shadow-lg transition-all duration-200 hover:scale-105 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2`}
          aria-label={launcherText}
        >
          <MessageSquare className="w-6 h-6" />
          {unreadCount > 0 && (
            <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full w-6 h-6 flex items-center justify-center">
              {unreadCount > 99 ? '99+' : unreadCount}
            </span>
          )}
        </button>
      )}

      {/* Chat Interface */}
      {isOpen && (
        <div
          ref={chatRef}
          className={`${getPositionClasses()} ${getSizeClasses()} bg-white rounded-lg shadow-2xl border border-gray-200 overflow-hidden transition-all duration-300 ${
            isMinimized ? 'h-12' : ''
          }`}
        >
          {/* Chat Header */}
          <div className="flex items-center justify-between p-3 bg-gray-50 border-b border-gray-200">
            <div className="flex items-center space-x-2">
              <MessageSquare className="w-5 h-5 text-blue-600" />
              <span className="font-medium text-gray-900">
                {config?.name || 'Chat Support'}
              </span>
            </div>
            
            <div className="flex items-center space-x-1">
              <button
                onClick={() => setIsMinimized(!isMinimized)}
                className="p-1 hover:bg-gray-200 rounded transition-colors"
                aria-label={isMinimized ? 'Maximize' : 'Minimize'}
              >
                {isMinimized ? (
                  <Maximize2 className="w-4 h-4 text-gray-600" />
                ) : (
                  <Minimize2 className="w-4 h-4 text-gray-600" />
                )}
              </button>
              
              <button
                onClick={() => setIsOpen(false)}
                className="p-1 hover:bg-gray-200 rounded transition-colors"
                aria-label="Close chat"
              >
                <X className="w-4 h-4 text-gray-600" />
              </button>
            </div>
          </div>

          {/* Chat Content */}
          {!isMinimized && (
            <div className="flex-1 overflow-hidden">
              {loading ? (
                <div className="flex items-center justify-center h-full">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                </div>
              ) : config ? (
                <EnhancedChatInterface
                  config={config}
                  className="h-full border-none shadow-none"
                />
              ) : (
                <div className="flex items-center justify-center h-full text-gray-500">
                  <span>Failed to load chat configuration</span>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Custom Styles */}
      <style>{`
        .embeddable-chat {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
        }
        
        .theme-dark {
          --bg-primary: #1f2937;
          --bg-secondary: #374151;
          --text-primary: #f9fafb;
          --text-secondary: #d1d5db;
          --border-color: #4b5563;
        }
        
        .theme-light {
          --bg-primary: #ffffff;
          --bg-secondary: #f9fafb;
          --text-primary: #111827;
          --text-secondary: #6b7280;
          --border-color: #e5e7eb;
        }
        
        .theme-auto {
          --bg-primary: #ffffff;
          --bg-secondary: #f9fafb;
          --text-primary: #111827;
          --text-secondary: #6b7280;
          --border-color: #e5e7eb;
        }
        
        @media (prefers-color-scheme: dark) {
          .theme-auto {
            --bg-primary: #1f2937;
            --bg-secondary: #374151;
            --text-primary: #f9fafb;
            --text-secondary: #d1d5db;
            --border-color: #4b5563;
          }
        }
        
        @media (max-width: 640px) {
          .embeddable-chat [class*="w-96"], 
          .embeddable-chat [class*="w-80"],
          .embeddable-chat [class*="w-[500px]"] {
            width: calc(100vw - 2rem) !important;
            max-width: 400px;
          }
          
          .embeddable-chat [class*="h-96"],
          .embeddable-chat [class*="h-[500px]"],
          .embeddable-chat [class*="h-[600px]"] {
            height: calc(100vh - 8rem) !important;
            max-height: 600px;
          }
        }
      `}</style>
    </div>
  )
}

export default EmbeddableChat
