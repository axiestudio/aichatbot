import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { AdminUser, ChatConfig, Message } from '../types'

interface ClientState {
  // Client Authentication & Info
  client: AdminUser | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
  
  // Chat Configuration
  chatConfig: ChatConfig | null
  isConfigLoading: boolean
  
  // Real-time Embed Status
  activeEmbeds: {
    id: string
    domain: string
    isActive: boolean
    lastSeen: Date
    visitors: number
  }[]
  
  // Live Chat Sessions
  liveSessions: {
    sessionId: string
    domain: string
    userAgent: string
    startTime: Date
    lastActivity: Date
    messageCount: number
    isActive: boolean
  }[]
  
  // Analytics
  analytics: {
    totalSessions: number
    activeSessions: number
    totalMessages: number
    avgSessionDuration: number
    topDomains: { domain: string; sessions: number }[]
    hourlyStats: { hour: number; sessions: number; messages: number }[]
  } | null

  // Actions
  login: (email: string, password: string) => Promise<boolean>
  logout: () => void
  loadChatConfig: () => Promise<void>
  updateChatConfig: (config: Partial<ChatConfig>) => Promise<void>
  loadActiveEmbeds: () => Promise<void>
  loadLiveSessions: () => Promise<void>
  loadAnalytics: () => Promise<void>
  generateEmbedCode: () => string
  testEmbedConnection: (domain: string) => Promise<boolean>
  clearError: () => void
}

export const useClientStore = create<ClientState>()(
  persist(
    (set, get) => ({
      // Initial state
      client: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
      chatConfig: null,
      isConfigLoading: false,
      activeEmbeds: [],
      liveSessions: [],
      analytics: null,

      // Authentication
      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null })
        
        try {
          // Mock authentication - replace with actual API
          const mockClient: AdminUser = {
            id: `client-${Date.now()}`,
            email,
            name: email.split('@')[0],
            role: 'admin',
            createdAt: new Date(),
            lastLogin: new Date(),
            tenantId: `tenant-${Date.now()}`,
            isActive: true,
            subscription: {
              tier: 'premium',
              status: 'active',
              current_period_end: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000)
            },
            usage: {
              conversations: 0,
              messages: 0,
              storage: 0,
              api_calls: 0
            },
            permissions: {
              can_access_analytics: true,
              can_manage_billing: true,
              can_customize_branding: true,
              can_export_data: true,
              can_manage_users: true
            }
          }
          
          set({ 
            client: mockClient, 
            isAuthenticated: true, 
            isLoading: false 
          })
          
          // Load initial data
          await Promise.all([
            get().loadChatConfig(),
            get().loadActiveEmbeds(),
            get().loadLiveSessions(),
            get().loadAnalytics()
          ])
          
          return true
        } catch (error) {
          set({ 
            error: 'Login failed', 
            isLoading: false 
          })
          return false
        }
      },

      logout: () => {
        set({
          client: null,
          isAuthenticated: false,
          chatConfig: null,
          activeEmbeds: [],
          liveSessions: [],
          analytics: null,
          error: null
        })
      },

      // Chat Configuration
      loadChatConfig: async () => {
        set({ isConfigLoading: true })
        
        try {
          const { client } = get()
          if (!client) return
          
          // Mock config - replace with actual API
          const mockConfig: ChatConfig = {
            id: `config-${client.tenantId}`,
            name: `${client.name}'s Chat`,
            primaryColor: '#2563eb',
            secondaryColor: '#f3f4f6',
            fontFamily: 'Inter',
            fontSize: 14,
            borderRadius: 8,
            position: 'bottom-right',
            welcomeMessage: `Hello! Welcome to ${client.name}'s support. How can I help you today?`,
            placeholder: 'Type your message...',
            height: 600,
            width: 400,
            isActive: true,
            createdAt: new Date(),
            updatedAt: new Date()
          }
          
          set({ chatConfig: mockConfig, isConfigLoading: false })
        } catch (error) {
          set({ error: 'Failed to load chat configuration', isConfigLoading: false })
        }
      },

      updateChatConfig: async (configUpdates) => {
        const { chatConfig } = get()
        if (!chatConfig) return
        
        try {
          const updatedConfig = {
            ...chatConfig,
            ...configUpdates,
            updatedAt: new Date()
          }
          
          set({ chatConfig: updatedConfig })
          
          // Broadcast changes to all active embeds
          // This would trigger real-time updates to embedded widgets
          window.postMessage({
            type: 'CHAT_CONFIG_UPDATE',
            config: updatedConfig
          }, '*')
          
        } catch (error) {
          set({ error: 'Failed to update chat configuration' })
        }
      },

      // Embed Management
      loadActiveEmbeds: async () => {
        try {
          // Mock data - replace with actual API
          const mockEmbeds = [
            {
              id: 'embed-1',
              domain: 'example.com',
              isActive: true,
              lastSeen: new Date(),
              visitors: 45
            },
            {
              id: 'embed-2', 
              domain: 'demo.example.com',
              isActive: true,
              lastSeen: new Date(Date.now() - 5 * 60 * 1000),
              visitors: 12
            }
          ]
          
          set({ activeEmbeds: mockEmbeds })
        } catch (error) {
          set({ error: 'Failed to load active embeds' })
        }
      },

      loadLiveSessions: async () => {
        try {
          // Mock data - replace with actual API
          const mockSessions = [
            {
              sessionId: 'session-1',
              domain: 'example.com',
              userAgent: 'Mozilla/5.0...',
              startTime: new Date(Date.now() - 10 * 60 * 1000),
              lastActivity: new Date(),
              messageCount: 5,
              isActive: true
            },
            {
              sessionId: 'session-2',
              domain: 'demo.example.com', 
              userAgent: 'Mozilla/5.0...',
              startTime: new Date(Date.now() - 25 * 60 * 1000),
              lastActivity: new Date(Date.now() - 2 * 60 * 1000),
              messageCount: 12,
              isActive: false
            }
          ]
          
          set({ liveSessions: mockSessions })
        } catch (error) {
          set({ error: 'Failed to load live sessions' })
        }
      },

      loadAnalytics: async () => {
        try {
          // Mock analytics - replace with actual API
          const mockAnalytics = {
            totalSessions: 1250,
            activeSessions: 8,
            totalMessages: 8500,
            avgSessionDuration: 4.5,
            topDomains: [
              { domain: 'example.com', sessions: 850 },
              { domain: 'demo.example.com', sessions: 400 }
            ],
            hourlyStats: Array.from({ length: 24 }, (_, i) => ({
              hour: i,
              sessions: Math.floor(Math.random() * 50),
              messages: Math.floor(Math.random() * 200)
            }))
          }
          
          set({ analytics: mockAnalytics })
        } catch (error) {
          set({ error: 'Failed to load analytics' })
        }
      },

      generateEmbedCode: () => {
        const { client, chatConfig } = get()
        if (!client || !chatConfig) return ''
        
        return `<!-- Axie Studio Chat Widget -->
<script>
  window.AxieChatConfig = {
    tenantId: "${client.tenantId}",
    configId: "${chatConfig.id}",
    apiUrl: "${window.location.origin}/api/v1"
  };
</script>
<script src="${window.location.origin}/embed/chat-widget.js" async></script>
<!-- End Axie Studio Chat Widget -->`
      },

      testEmbedConnection: async (domain) => {
        try {
          // Mock test - replace with actual API
          await new Promise(resolve => setTimeout(resolve, 1000))
          return Math.random() > 0.2 // 80% success rate
        } catch (error) {
          return false
        }
      },

      clearError: () => {
        set({ error: null })
      }
    }),
    {
      name: 'client-storage',
      partialize: (state) => ({
        client: state.client,
        isAuthenticated: state.isAuthenticated,
        chatConfig: state.chatConfig
      })
    }
  )
)
