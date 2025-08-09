import { useState, useCallback, useEffect, useRef } from 'react'
import { useChatStore } from '../stores/chatStore'
import api from '../utils/api'

export interface MessageAttachment {
  id: string
  filename: string
  original_filename: string
  file_size: number
  mime_type: string
  attachment_type: 'image' | 'audio' | 'document' | 'video'
  url: string
  thumbnail_url?: string
}

export interface MessageReaction {
  emoji: string
  count: number
  users: string[]
}

export interface MessageReply {
  message_id: string
  content: string
  role: 'user' | 'assistant'
  timestamp: Date
}

export interface Message {
  id: string
  session_id: string
  content: string
  role: 'user' | 'assistant'
  timestamp: Date
  status: 'sending' | 'sent' | 'delivered' | 'read' | 'failed'
  attachments: MessageAttachment[]
  reactions: MessageReaction[]
  reply_to?: MessageReply
  edited_at?: Date
  deleted_at?: Date
  metadata: Record<string, any>
}

export const useChat = (sessionId?: string) => {
  const { messages, addMessage, updateMessage, setLoading, isLoading } = useChatStore()
  const [error, setError] = useState<string | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [isTyping, setIsTyping] = useState(false)
  const [typingUsers, setTypingUsers] = useState<string[]>([])

  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout>>()
  const typingTimeoutRef = useRef<ReturnType<typeof setTimeout>>()
  const currentSessionId = sessionId || 'default'

  // WebSocket connection management
  const connectWebSocket = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return

    const wsUrl = `${import.meta.env.VITE_WS_URL || 'ws://localhost:8000'}/api/v1/realtime/ws/${currentSessionId}`
    wsRef.current = new WebSocket(wsUrl)

    wsRef.current.onopen = () => {
      console.log('WebSocket connected')
      setIsConnected(true)
      setError(null)
    }

    wsRef.current.onmessage = (event: MessageEvent) => {
      try {
        const data = JSON.parse(event.data)
        handleWebSocketMessage(data)
      } catch (err) {
        console.error('WebSocket message parse error:', err)
      }
    }

    wsRef.current.onclose = () => {
      console.log('WebSocket disconnected')
      setIsConnected(false)

      // Attempt to reconnect after 3 seconds
      reconnectTimeoutRef.current = setTimeout(() => {
        connectWebSocket()
      }, 3000)
    }

    wsRef.current.onerror = (error: Event) => {
      console.error('WebSocket error:', error)
      setError('Connection error')
    }
  }, [currentSessionId])

  // Handle WebSocket messages
  const handleWebSocketMessage = useCallback((data: any) => {
    switch (data.type) {
      case 'user_message':
        const userMessage: Message = {
          id: data.message_id,
          session_id: currentSessionId,
          content: data.message,
          role: 'user',
          timestamp: new Date(data.timestamp),
          status: 'sent',
          attachments: [],
          reactions: [],
          metadata: {}
        }
        addMessage(userMessage)
        break

      case 'ai_response':
        const aiMessage: Message = {
          id: data.message_id,
          session_id: currentSessionId,
          content: data.message,
          role: 'assistant',
          timestamp: new Date(data.timestamp),
          status: 'delivered',
          attachments: [],
          reactions: [],
          metadata: data.metadata || {}
        }
        addMessage(aiMessage)
        break

      case 'user_typing':
        if (data.is_typing) {
          setTypingUsers((prev: string[]) => [...prev.filter((u: string) => u !== data.user_id), data.user_id])
        } else {
          setTypingUsers((prev: string[]) => prev.filter((u: string) => u !== data.user_id))
        }
        break

      case 'message_status_update':
        updateMessage(data.message_id, { status: data.status })
        break

      case 'message_reaction':
        updateMessage(data.message_id, {
          reactions: data.reactions
        })
        break

      case 'connection_established':
        console.log('WebSocket connection established:', data)
        break

      case 'error':
        setError(data.message)
        break

      default:
        console.log('Unknown WebSocket message type:', data.type)
    }
  }, [currentSessionId, addMessage, updateMessage])

  // Send message with WebSocket
  const sendMessage = useCallback(async (content: string, attachments: File[] = []) => {
    if (!content.trim() && attachments.length === 0) return

    const messageId = `msg_${Date.now()}_${Math.random().toString(36).substring(2, 11)}`

    // Create user message
    const userMessage: Message = {
      id: messageId,
      session_id: currentSessionId,
      content: content.trim(),
      role: 'user',
      timestamp: new Date(),
      status: 'sending',
      attachments: [],
      reactions: [],
      metadata: {}
    }

    addMessage(userMessage)
    setLoading(true)
    setError(null)

    try {
      // Upload attachments first if any
      let attachmentIds: string[] = []
      if (attachments.length > 0) {
        const formData = new FormData()
        attachments.forEach(file => formData.append('files', file))
        formData.append('session_id', currentSessionId)

        const uploadResponse = await api.post('/files/upload', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })

        attachmentIds = uploadResponse.data
          .filter((result: any) => result.status === 'success')
          .map((result: any) => result.file_id)
      }

      // Send via WebSocket if connected, otherwise use HTTP
      if (isConnected && wsRef.current) {
        wsRef.current.send(JSON.stringify({
          type: 'chat_message',
          message: content,
          attachments: attachmentIds,
          message_id: messageId
        }))

        // Update message status
        updateMessage(messageId, { status: 'sent' })
      } else {
        // Fallback to HTTP API
        const response = await api.post('/chat/send', {
          message: content,
          session_id: currentSessionId,
          attachments: attachmentIds
        })

        updateMessage(messageId, {
          status: 'delivered',
          id: response.data.message_id
        })

        const assistantMessage: Message = {
          id: response.data.message_id + '_ai',
          session_id: currentSessionId,
          content: response.data.response,
          role: 'assistant',
          timestamp: new Date(),
          status: 'delivered',
          attachments: [],
          reactions: [],
          metadata: response.data.metadata || {}
        }

        addMessage(assistantMessage)
      }
    } catch (err: any) {
      updateMessage(messageId, { status: 'failed' })
      setError(err.response?.data?.detail || 'Failed to send message')
      console.error('Chat error:', err)
    } finally {
      setLoading(false)
    }
  }, [currentSessionId, addMessage, updateMessage, setLoading, isConnected])

  // Typing indicators
  const startTyping = useCallback(() => {
    if (isConnected && wsRef.current) {
      wsRef.current.send(JSON.stringify({
        type: 'typing_start'
      }))

      setIsTyping(true)

      // Clear existing timeout
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current)
      }

      // Auto-stop typing after 3 seconds
      typingTimeoutRef.current = setTimeout(() => {
        stopTyping()
      }, 3000)
    }
  }, [isConnected])

  const stopTyping = useCallback(() => {
    if (isConnected && wsRef.current) {
      wsRef.current.send(JSON.stringify({
        type: 'typing_stop'
      }))
    }

    setIsTyping(false)

    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current)
    }
  }, [isConnected])

  // Message reactions
  const addReaction = useCallback(async (messageId: string, emoji: string) => {
    try {
      await api.post(`/chat/messages/${messageId}/reactions`, {
        emoji
      })
    } catch (err) {
      console.error('Failed to add reaction:', err)
    }
  }, [])

  // Reply to message
  const replyToMessage = useCallback(async (replyToMessage: Message, content: string, _attachments: File[] = []) => {
    const messageId = `msg_${Date.now()}_${Math.random().toString(36).substring(2, 11)}`

    const userMessage: Message = {
      id: messageId,
      session_id: currentSessionId,
      content: content.trim(),
      role: 'user',
      timestamp: new Date(),
      status: 'sending',
      attachments: [],
      reactions: [],
      reply_to: {
        message_id: replyToMessage.id,
        content: replyToMessage.content,
        role: replyToMessage.role,
        timestamp: replyToMessage.timestamp
      },
      metadata: {}
    }

    addMessage(userMessage)

    // Send the message (similar to sendMessage but with reply_to)
    try {
      if (isConnected && wsRef.current) {
        wsRef.current.send(JSON.stringify({
          type: 'chat_message',
          message: content,
          reply_to_message_id: replyToMessage.id,
          message_id: messageId
        }))
      }
    } catch (err) {
      console.error('Failed to send reply:', err)
    }
  }, [currentSessionId, addMessage, isConnected])

  // Copy message content
  const copyMessage = useCallback(async (message: Message) => {
    try {
      await navigator.clipboard.writeText(message.content)
    } catch (err) {
      console.error('Failed to copy message:', err)
    }
  }, [])

  // Delete message
  const deleteMessage = useCallback(async (messageId: string) => {
    try {
      await api.delete(`/chat/messages/${messageId}`)
      updateMessage(messageId, { deleted_at: new Date() })
    } catch (err) {
      console.error('Failed to delete message:', err)
    }
  }, [updateMessage])

  // Initialize WebSocket connection
  useEffect(() => {
    connectWebSocket()

    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current)
      }
    }
  }, [connectWebSocket])

  // Ping WebSocket to keep connection alive
  useEffect(() => {
    if (!isConnected) return

    const pingInterval = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: 'ping' }))
      }
    }, 30000) // Ping every 30 seconds

    return () => clearInterval(pingInterval)
  }, [isConnected])

  const clearChat = useCallback(() => {
    useChatStore.getState().clearMessages()
    setError(null)
  }, [])

  return {
    // Messages
    messages,
    sendMessage,
    replyToMessage,

    // Message actions
    addReaction,
    copyMessage,
    deleteMessage,

    // Typing
    startTyping,
    stopTyping,
    isTyping,
    typingUsers,

    // Connection
    isConnected,
    connectWebSocket,

    // State
    isLoading,
    error,
    clearError: () => setError(null),
    clearChat,

    // Session
    sessionId: currentSessionId
  }
}
