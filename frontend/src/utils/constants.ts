export const API_ENDPOINTS = {
  CHAT: '/chat',
  CONFIG: '/config',
  ADMIN: '/admin',
  AUTH: '/auth',
  ANALYTICS: '/analytics',
} as const

export const CHAT_ROLES = {
  USER: 'user',
  ASSISTANT: 'assistant',
  SYSTEM: 'system',
} as const

export const CHAT_STATUS = {
  IDLE: 'idle',
  LOADING: 'loading',
  ERROR: 'error',
} as const

export const STORAGE_KEYS = {
  AUTH_TOKEN: 'auth_token',
  CHAT_CONFIG: 'chat_config',
  CHAT_HISTORY: 'chat_history',
} as const

export const DEFAULT_COLORS = {
  PRIMARY: '#3b82f6',
  SECONDARY: '#e5e7eb',
  SUCCESS: '#10b981',
  ERROR: '#ef4444',
  WARNING: '#f59e0b',
} as const

export const FONT_FAMILIES = [
  'Inter',
  'Roboto',
  'Open Sans',
  'Lato',
  'Montserrat',
  'Poppins',
  'Source Sans Pro',
  'Nunito',
] as const

export const CHAT_POSITIONS = [
  'bottom-right',
  'bottom-left',
  'top-right',
  'top-left',
] as const

export const FILE_TYPES = {
  ALLOWED: ['txt', 'pdf', 'docx', 'md'],
  MAX_SIZE: 10 * 1024 * 1024, // 10MB
} as const

export const RATE_LIMITS = {
  MESSAGES_PER_MINUTE: 30,
  REQUESTS_PER_HOUR: 100,
} as const
