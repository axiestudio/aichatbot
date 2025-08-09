import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { SuperAdminUser, ClientManagement, AdminUser } from '../types'

interface SuperAdminState {
  // Authentication
  superAdmin: SuperAdminUser | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null

  // Client Management
  clients: ClientManagement[]
  selectedClient: ClientManagement | null
  impersonatedClient: string | null

  // System Analytics
  systemStats: {
    totalClients: number
    activeClients: number
    totalConversations: number
    totalMessages: number
    totalRevenue: number
    monthlyGrowth: number
  } | null

  // Actions
  login: (username: string, password: string) => Promise<boolean>
  logout: () => void
  loadClients: () => Promise<void>
  createClient: (clientData: Partial<ClientManagement>) => Promise<void>
  suspendClient: (clientId: string) => Promise<void>
  activateClient: (clientId: string) => Promise<void>
  deleteClient: (clientId: string) => Promise<void>
  impersonateClient: (clientId: string) => void
  stopImpersonation: () => void
  loadSystemStats: () => Promise<void>
  selectClient: (client: ClientManagement | null) => void
  clearError: () => void
}

export const useSuperAdminStore = create<SuperAdminState>()(
  persist(
    (set, get) => ({
      // Initial state
      superAdmin: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
      clients: [],
      selectedClient: null,
      impersonatedClient: null,
      systemStats: null,

      // Authentication
      login: async (username: string, password: string) => {
        set({ isLoading: true, error: null })
        
        try {
          // Check environment credentials
          const superAdminUsername = import.meta.env.VITE_SUPER_ADMIN_USERNAME
          const superAdminPassword = import.meta.env.VITE_SUPER_ADMIN_PASSWORD
          
          if (username === superAdminUsername && password === superAdminPassword) {
            const superAdmin: SuperAdminUser = {
              id: 'super-admin-001',
              email: username,
              name: 'Stefan Miranda',
              role: 'super_admin',
              createdAt: new Date(),
              lastLogin: new Date(),
              tenantId: null,
              isActive: true,
              superAdminPermissions: {
                canCreateClients: true,
                canSuspendClients: true,
                canAccessAllData: true,
                canImpersonateClients: true,
                canManageSystemSettings: true,
                canViewSystemAnalytics: true,
              }
            }
            
            set({ 
              superAdmin, 
              isAuthenticated: true, 
              isLoading: false 
            })
            
            // Load initial data
            await get().loadClients()
            await get().loadSystemStats()
            
            return true
          } else {
            set({ 
              error: 'Invalid super admin credentials', 
              isLoading: false 
            })
            return false
          }
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
          superAdmin: null,
          isAuthenticated: false,
          clients: [],
          selectedClient: null,
          impersonatedClient: null,
          systemStats: null,
          error: null
        })
      },

      // Client Management
      loadClients: async () => {
        set({ isLoading: true })
        
        try {
          // Mock data for now - replace with actual API call
          const mockClients: ClientManagement[] = [
            {
              id: 'client-001',
              name: 'Acme Corporation',
              email: 'admin@acme.com',
              domain: 'acme.com',
              status: 'active',
              subscription: {
                tier: 'premium',
                status: 'active',
                current_period_end: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000)
              },
              usage: {
                conversations: 1250,
                messages: 8500,
                storage: 2.5,
                api_calls: 15000
              },
              createdAt: new Date('2024-01-15'),
              lastActivity: new Date(),
              adminUsers: []
            },
            {
              id: 'client-002', 
              name: 'TechStart Inc',
              email: 'admin@techstart.io',
              domain: 'techstart.io',
              status: 'active',
              subscription: {
                tier: 'free',
                status: 'active'
              },
              usage: {
                conversations: 45,
                messages: 320,
                storage: 0.1,
                api_calls: 500
              },
              createdAt: new Date('2024-02-20'),
              lastActivity: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000),
              adminUsers: []
            }
          ]
          
          set({ clients: mockClients, isLoading: false })
        } catch (error) {
          set({ error: 'Failed to load clients', isLoading: false })
        }
      },

      createClient: async (clientData) => {
        set({ isLoading: true })
        
        try {
          const newClient: ClientManagement = {
            id: `client-${Date.now()}`,
            name: clientData.name || 'New Client',
            email: clientData.email || '',
            domain: clientData.domain,
            status: 'active',
            subscription: {
              tier: 'free',
              status: 'active'
            },
            usage: {
              conversations: 0,
              messages: 0,
              storage: 0,
              api_calls: 0
            },
            createdAt: new Date(),
            lastActivity: new Date(),
            adminUsers: []
          }
          
          set(state => ({
            clients: [...state.clients, newClient],
            isLoading: false
          }))
        } catch (error) {
          set({ error: 'Failed to create client', isLoading: false })
        }
      },

      suspendClient: async (clientId) => {
        set(state => ({
          clients: state.clients.map(client =>
            client.id === clientId 
              ? { ...client, status: 'suspended' as const }
              : client
          )
        }))
      },

      activateClient: async (clientId) => {
        set(state => ({
          clients: state.clients.map(client =>
            client.id === clientId 
              ? { ...client, status: 'active' as const }
              : client
          )
        }))
      },

      deleteClient: async (clientId) => {
        set(state => ({
          clients: state.clients.filter(client => client.id !== clientId),
          selectedClient: state.selectedClient?.id === clientId ? null : state.selectedClient
        }))
      },

      impersonateClient: (clientId) => {
        set({ impersonatedClient: clientId })
      },

      stopImpersonation: () => {
        set({ impersonatedClient: null })
      },

      loadSystemStats: async () => {
        try {
          const { clients } = get()
          
          const systemStats = {
            totalClients: clients.length,
            activeClients: clients.filter(c => c.status === 'active').length,
            totalConversations: clients.reduce((sum, c) => sum + c.usage.conversations, 0),
            totalMessages: clients.reduce((sum, c) => sum + c.usage.messages, 0),
            totalRevenue: clients.filter(c => c.subscription.tier !== 'free').length * 29, // Mock calculation
            monthlyGrowth: 15.5 // Mock percentage
          }
          
          set({ systemStats })
        } catch (error) {
          set({ error: 'Failed to load system stats' })
        }
      },

      selectClient: (client) => {
        set({ selectedClient: client })
      },

      clearError: () => {
        set({ error: null })
      }
    }),
    {
      name: 'super-admin-storage',
      partialize: (state) => ({
        superAdmin: state.superAdmin,
        isAuthenticated: state.isAuthenticated,
        impersonatedClient: state.impersonatedClient
      })
    }
  )
)
