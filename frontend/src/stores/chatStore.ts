import { create } from 'zustand'
import { Message, ChatConfig } from '../types'

interface ChatState {
  messages: Message[]
  isLoading: boolean
  config: ChatConfig | null
  sessionId: string | null

  addMessage: (message: Message) => void
  updateMessage: (messageId: string, updates: Partial<Message>) => void
  setMessages: (messages: Message[]) => void
  clearMessages: () => void
  setLoading: (loading: boolean) => void
  setConfig: (config: ChatConfig) => void
  setSessionId: (sessionId: string) => void
  clearChat: () => void
  sendMessage: (content: string) => Promise<void>
}

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  isLoading: false,
  config: null,
  sessionId: null,
  
  addMessage: (message) => {
    set((state) => ({
      messages: [...state.messages, message]
    }))
  },

  updateMessage: (messageId, updates) => {
    set((state) => ({
      messages: state.messages.map(msg =>
        msg.id === messageId ? { ...msg, ...updates } : msg
      )
    }))
  },

  clearMessages: () => set({ messages: [] }),
  
  setMessages: (messages) => set({ messages }),
  setLoading: (isLoading) => set({ isLoading }),
  setConfig: (config) => set({ config }),
  setSessionId: (sessionId) => set({ sessionId }),
  
  clearChat: () => set({ messages: [], sessionId: null }),
  
  sendMessage: async (content: string) => {
    const { addMessage, config } = get()
    
    // Add user message
    addMessage({
      id: `msg-${Date.now()}-user`,
      session_id: 'default',
      content,
      role: 'user',
      timestamp: new Date(),
      status: 'sent',
      attachments: [],
      reactions: [],
      metadata: {}
    })
    set({ isLoading: true })
    
    try {
      // Make API call to backend
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: content,
          sessionId: get().sessionId,
          configId: config?.id,
        }),
      })
      
      if (!response.ok) {
        throw new Error('Failed to send message')
      }
      
      const data = await response.json()
      
      // Add assistant response
      addMessage({
        id: `msg-${Date.now()}-assistant`,
        session_id: data.sessionId || 'default',
        content: data.response,
        role: 'assistant',
        timestamp: new Date(),
        status: 'sent',
        attachments: [],
        reactions: [],
        metadata: {}
      })
      
      // Update session ID if provided
      if (data.sessionId) {
        set({ sessionId: data.sessionId })
      }
      
    } catch (error) {
      console.error('Error sending message:', error)
      addMessage({
        id: `msg-${Date.now()}-error`,
        session_id: 'default',
        content: 'Sorry, I encountered an error. Please try again.',
        role: 'assistant',
        timestamp: new Date(),
        status: 'sent',
        attachments: [],
        reactions: [],
        metadata: {}
      })
    } finally {
      set({ isLoading: false })
    }
  },
}))
