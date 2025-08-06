import { useEffect, useRef, useState } from 'react'
import { useParams } from 'react-router-dom'
import { useChatStore } from '../stores/chatStore'
import { ChatConfig } from '../types'
import ChatMessage from '../components/ChatMessage'
import ChatInput from '../components/ChatInput'
import ModernChatInterface from '../components/chat/ModernChatInterface'

// Default config for demo purposes
const defaultConfig: ChatConfig = {
  id: 'default',
  name: 'Default Chat',
  primaryColor: '#3b82f6',
  secondaryColor: '#e5e7eb',
  fontFamily: 'Inter',
  fontSize: 14,
  borderRadius: 12,
  position: 'bottom-right',
  welcomeMessage: 'Hello! How can I help you today?',
  placeholder: 'Type your message...',
  height: 500,
  width: 350,
  isActive: true,
  createdAt: new Date(),
  updatedAt: new Date(),
}

export default function ChatInterface() {
  const { configId } = useParams()
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const [liveConfig, setLiveConfig] = useState<any>(null)
  const [isConfigLoading, setIsConfigLoading] = useState(true)
  const [websocket, setWebsocket] = useState<WebSocket | null>(null)

  const {
    messages,
    isLoading,
    config,
    addMessage,
    setConfig,
    sendMessage,
    clearChat
  } = useChatStore()

  useEffect(() => {
    loadLiveConfiguration()
    setupWebSocket()

    return () => {
      if (websocket) {
        websocket.close()
      }
    }
  }, [])

  const loadLiveConfiguration = async () => {
    try {
      const response = await fetch('/api/v1/admin/live-config/preview')

      if (response.ok) {
        const liveConfigData = await response.json()
        setLiveConfig(liveConfigData)

        // Convert live config to chat config format
        const chatConfig: ChatConfig = {
          ...defaultConfig,
          primaryColor: liveConfigData.primary_color || defaultConfig.primaryColor,
          secondaryColor: liveConfigData.secondary_color || defaultConfig.secondaryColor,
          welcomeMessage: liveConfigData.welcome_message || defaultConfig.welcomeMessage,
          placeholder: liveConfigData.placeholder_text || defaultConfig.placeholder,
          name: liveConfigData.chat_title || defaultConfig.name
        }

        setConfig(chatConfig)

        // Add welcome message if no messages exist
        if (messages.length === 0) {
          addMessage({
            id: `msg-${Date.now()}`,
            session_id: 'default',
            content: liveConfigData.welcome_message || defaultConfig.welcomeMessage,
            role: 'assistant',
            timestamp: new Date(),
            status: 'sent',
            attachments: [],
            reactions: [],
            metadata: {}
          })
        }
      } else {
        // Fallback to default config
        setConfig(defaultConfig)
        if (messages.length === 0) {
          addMessage({
            id: `msg-${Date.now()}`,
            session_id: 'default',
            content: defaultConfig.welcomeMessage,
            role: 'assistant',
            timestamp: new Date(),
            status: 'sent',
            attachments: [],
            reactions: [],
            metadata: {}
          })
        }
      }
    } catch (error) {
      console.error('Error loading live configuration:', error)
      // Fallback to default config
      setConfig(defaultConfig)
    } finally {
      setIsConfigLoading(false)
    }
  }

  const setupWebSocket = () => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//${window.location.host}/api/v1/ws/default?connection_type=chat`

    const ws = new WebSocket(wsUrl)

    ws.onopen = () => {
      console.log('WebSocket connected for live configuration updates')
      setWebsocket(ws)
    }

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data)

      if (message.type === 'config_update') {
        console.log('Received live configuration update:', message.changes)
        loadLiveConfiguration() // Reload configuration
      }
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }

    ws.onclose = () => {
      console.log('WebSocket disconnected')
      setWebsocket(null)
    }
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const handleSendMessage = async (message: string) => {
    if (!message.trim() || isLoading) return
    await sendMessage(message.trim())
  }

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Professional Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
            </div>
            <div>
              <h1 className="text-lg font-semibold text-gray-900">Chat Assistant</h1>
              <p className="text-sm text-gray-500">Always here to help</p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={clearChat}
              className="px-3 py-1.5 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
            >
              Clear Chat
            </button>
            <div className="w-2 h-2 bg-green-500 rounded-full" title="Online"></div>
          </div>
        </div>
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto bg-white">
        <div className="max-w-4xl mx-auto px-6 py-8">
          {messages.length === 0 ? (
            <div className="text-center py-12">
              <div className="w-16 h-16 bg-blue-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Start a conversation</h3>
              <p className="text-gray-600 max-w-sm mx-auto">
                Ask me anything and I'll do my best to help you. I can assist with questions, provide information, or just have a friendly chat.
              </p>
            </div>
          ) : (
            <div className="space-y-6">
              {messages.map((message) => (
                <ChatMessage key={message.id} message={message} />
              ))}

              {isLoading && (
                <ChatMessage
                  message={{
                    id: 'typing',
                    session_id: 'default',
                    content: '',
                    role: 'assistant',
                    timestamp: new Date(),
                    status: 'sending',
                    attachments: [],
                    reactions: [],
                    metadata: {}
                  }}
                  isTyping={true}
                />
              )}
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-200 bg-white">
        <ChatInput
          onSendMessage={handleSendMessage}
          disabled={isLoading}
          placeholder="Type your message..."
        />
      </div>
    </div>
  )
}


