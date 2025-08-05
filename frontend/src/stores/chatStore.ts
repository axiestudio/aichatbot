import { create } from 'zustand'
import { Message, ChatConfig } from '../types'

interface ChatState {
  messages: Message[]
  isLoading: boolean
  config: ChatConfig | null
  sessionId: string | null
  
  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void
  setMessages: (messages: Message[]) => void
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
    const newMessage: Message = {
      ...message,
      id: Date.now().toString(),
      timestamp: new Date(),
    }
    set((state) => ({
      messages: [...state.messages, newMessage]
    }))
  },
  
  setMessages: (messages) => set({ messages }),
  setLoading: (isLoading) => set({ isLoading }),
  setConfig: (config) => set({ config }),
  setSessionId: (sessionId) => set({ sessionId }),
  
  clearChat: () => set({ messages: [], sessionId: null }),
  
  sendMessage: async (content: string) => {
    const { addMessage, config } = get()
    
    // Add user message
    addMessage({ content, role: 'user' })
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
        content: data.response, 
        role: 'assistant' 
      })
      
      // Update session ID if provided
      if (data.sessionId) {
        set({ sessionId: data.sessionId })
      }
      
    } catch (error) {
      console.error('Error sending message:', error)
      addMessage({ 
        content: 'Sorry, I encountered an error. Please try again.', 
        role: 'assistant' 
      })
    } finally {
      set({ isLoading: false })
    }
  },
}))
