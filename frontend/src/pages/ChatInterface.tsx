import { useEffect, useRef, useState } from 'react'
import { useParams } from 'react-router-dom'
import { useChatStore } from '../stores/chatStore'
import { ChatConfig } from '../types'
import EnhancedChatInterface from '../components/chat/EnhancedChatInterface'

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
    <div className="h-screen bg-gray-50 p-4">
      <EnhancedChatInterface
        config={config}
        onConfigChange={setConfig}
        className="h-full max-w-4xl mx-auto"
      />
    </div>
  )
}


