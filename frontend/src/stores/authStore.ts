import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { AdminUser } from '../types'

interface AuthState {
  isAuthenticated: boolean
  isLoading: boolean
  user: AdminUser | null
  login: (email: string, password: string) => Promise<boolean>
  logout: () => void
  setUser: (user: AdminUser) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      isAuthenticated: false,
      isLoading: false,
      user: null,
      
      login: async (email: string, password: string) => {
        try {
          // In a real app, this would make an API call
          // For demo purposes, we'll use hardcoded credentials
          if (email === 'admin@chatbot.com' && password === 'admin123') {
            const user: AdminUser = {
              id: '1',
              email,
              name: 'Admin User',
              role: 'admin',
              createdAt: new Date(),
              lastLogin: new Date(),
            }
            
            set({ isAuthenticated: true, user })
            return true
          }
          return false
        } catch (error) {
          console.error('Login error:', error)
          return false
        }
      },
      
      logout: () => {
        set({ isAuthenticated: false, user: null })
      },
      
      setUser: (user: AdminUser) => {
        set({ user })
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ 
        isAuthenticated: state.isAuthenticated, 
        user: state.user 
      }),
    }
  )
)
