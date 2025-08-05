import { useState, useCallback } from 'react'
import { useChatStore } from '../stores/chatStore'
import api from '../utils/api'

export interface Message {
  id: string
  content: string
  role: 'user' | 'assistant'
  timestamp: Date
}

export const useChat = () => {
  const { messages, addMessage, setLoading, isLoading } = useChatStore()
  const [error, setError] = useState<string | null>(null)

  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      content: content.trim(),
      role: 'user',
      timestamp: new Date(),
    }

    addMessage(userMessage)
    setLoading(true)
    setError(null)

    try {
      const response = await api.post('/chat/message', {
        message: content,
        conversation_id: 'default',
      })

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: response.data.response,
        role: 'assistant',
        timestamp: new Date(),
      }

      addMessage(assistantMessage)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to send message')
      console.error('Chat error:', err)
    } finally {
      setLoading(false)
    }
  }, [addMessage, setLoading])

  const clearChat = useCallback(() => {
    useChatStore.getState().clearMessages()
    setError(null)
  }, [])

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    clearChat,
  }
}
