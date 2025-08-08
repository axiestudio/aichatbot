import React, { useState, useEffect, useRef, useCallback } from 'react'
import { 
  Send, 
  Paperclip, 
  Mic, 
  MicOff, 
  MoreVertical, 
  Download,
  Copy,
  RefreshCw,
  Zap,
  Shield,
  Clock
} from 'lucide-react'
import { useChatStore } from '../../stores/chatStore'
import { Message, ChatConfig } from '../../types'
import { Button, StatusIndicator } from '../ui'
import ChatMessage from '../ChatMessage'
import ChatInput from '../ChatInput'

interface EnhancedChatInterfaceProps {
  config?: ChatConfig
  className?: string
  onConfigChange?: (config: ChatConfig) => void
}

const EnhancedChatInterface: React.FC<EnhancedChatInterfaceProps> = ({
  config,
  className = '',
  onConfigChange
}) => {
  const { 
    messages, 
    isLoading, 
    sendMessage, 
    clearMessages,
    sessionId 
  } = useChatStore()
  
  const [isRecording, setIsRecording] = useState(false)
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'connecting' | 'disconnected'>('connected')
  const [responseTime, setResponseTime] = useState<number>(0)
  const [messageCount, setMessageCount] = useState(0)
  const [showMetrics, setShowMetrics] = useState(false)
  
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const chatContainerRef = useRef<HTMLDivElement>(null)
  const responseStartTime = useRef<number>(0)

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages, scrollToBottom])

  useEffect(() => {
    setMessageCount(messages.length)
  }, [messages])

  const handleSendMessage = async (message: string, attachments?: File[]) => {
    if (!message.trim() && !attachments?.length) return

    responseStartTime.current = Date.now()
    setConnectionStatus('connecting')

    try {
      await sendMessage(message, attachments)
      const responseTime = Date.now() - responseStartTime.current
      setResponseTime(responseTime)
      setConnectionStatus('connected')
    } catch (error) {
      console.error('Failed to send message:', error)
      setConnectionStatus('disconnected')
    }
  }

  const handleVoiceRecording = () => {
    setIsRecording(!isRecording)
    // TODO: Implement voice recording functionality
  }

  const handleExportChat = () => {
    const chatData = {
      sessionId,
      messages: messages.map(msg => ({
        role: msg.role,
        content: msg.content,
        timestamp: msg.timestamp
      })),
      exportedAt: new Date().toISOString()
    }
    
    const blob = new Blob([JSON.stringify(chatData, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `chat-export-${sessionId}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const handleCopyChat = async () => {
    const chatText = messages
      .map(msg => `${msg.role.toUpperCase()}: ${msg.content}`)
      .join('\n\n')
    
    try {
      await navigator.clipboard.writeText(chatText)
      // TODO: Show success toast
    } catch (error) {
      console.error('Failed to copy chat:', error)
    }
  }

  const formatResponseTime = (time: number) => {
    if (time < 1000) return `${time}ms`
    return `${(time / 1000).toFixed(1)}s`
  }

  const getConnectionStatusColor = () => {
    switch (connectionStatus) {
      case 'connected': return 'healthy'
      case 'connecting': return 'pending'
      case 'disconnected': return 'unhealthy'
      default: return 'unknown'
    }
  }

  return (
    <div className={`flex flex-col h-full bg-white rounded-lg shadow-lg overflow-hidden ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-gray-50">
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2">
            <Zap className="w-5 h-5 text-blue-600" />
            <h3 className="font-semibold text-gray-900">
              {config?.name || 'AI Assistant'}
            </h3>
          </div>
          <StatusIndicator 
            status={getConnectionStatusColor()}
            size="sm"
            showLabel={false}
          />
        </div>

        <div className="flex items-center space-x-2">
          {showMetrics && (
            <div className="flex items-center space-x-4 text-xs text-gray-500 mr-4">
              <div className="flex items-center space-x-1">
                <Clock className="w-3 h-3" />
                <span>{formatResponseTime(responseTime)}</span>
              </div>
              <div className="flex items-center space-x-1">
                <Shield className="w-3 h-3" />
                <span>{messageCount} msgs</span>
              </div>
            </div>
          )}

          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowMetrics(!showMetrics)}
            className="p-2"
          >
            <MoreVertical className="w-4 h-4" />
          </Button>

          <div className="relative">
            <Button
              variant="ghost"
              size="sm"
              className="p-2"
            >
              <Download className="w-4 h-4" />
            </Button>
            {/* TODO: Add dropdown menu for export options */}
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div 
        ref={chatContainerRef}
        className="flex-1 overflow-y-auto p-4 space-y-4"
        style={{ 
          maxHeight: config?.height ? `${config.height - 120}px` : '400px'
        }}
      >
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-4">
              <Zap className="w-8 h-8 text-blue-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Welcome to {config?.name || 'AI Assistant'}
            </h3>
            <p className="text-gray-600 max-w-sm">
              {config?.welcomeMessage || 'I\'m here to help! Ask me anything and I\'ll do my best to assist you.'}
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {messages.map((message) => (
              <ChatMessage 
                key={message.id} 
                message={message}
                showTimestamp={config?.showTimestamps}
                showAvatar={config?.showAvatars}
              />
            ))}

            {isLoading && (
              <ChatMessage
                message={{
                  id: 'typing',
                  session_id: sessionId || 'default',
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

      {/* Input Area */}
      <div className="border-t border-gray-200 bg-white">
        <ChatInput
          onSendMessage={handleSendMessage}
          disabled={isLoading || connectionStatus === 'disconnected'}
          placeholder={config?.placeholder || 'Type your message...'}
          allowAttachments={true}
          allowVoiceInput={true}
          maxLength={2000}
        />
      </div>

      {/* Status Bar */}
      {showMetrics && (
        <div className="px-4 py-2 bg-gray-50 border-t border-gray-200">
          <div className="flex items-center justify-between text-xs text-gray-500">
            <div className="flex items-center space-x-4">
              <span>Session: {sessionId?.slice(-8) || 'N/A'}</span>
              <span>Messages: {messageCount}</span>
              <span>Avg Response: {formatResponseTime(responseTime)}</span>
            </div>
            <div className="flex items-center space-x-2">
              <StatusIndicator 
                status={getConnectionStatusColor()}
                label={connectionStatus}
                size="sm"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default EnhancedChatInterface
