export interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
}

export interface ChatConfig {
  id: string;
  name: string;
  primaryColor: string;
  secondaryColor: string;
  fontFamily: string;
  fontSize: number;
  borderRadius: number;
  position: 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left';
  welcomeMessage: string;
  placeholder: string;
  height: number;
  width: number;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface ApiConfig {
  id: string;
  provider: 'openai' | 'anthropic' | 'custom';
  apiKey: string;
  model: string;
  temperature: number;
  maxTokens: number;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface SupabaseConfig {
  id: string;
  url: string;
  anonKey: string;
  serviceKey?: string;
  tableName: string;
  searchColumns: string[];
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface RagInstruction {
  id: string;
  name: string;
  systemPrompt: string;
  contextPrompt: string;
  maxContextLength: number;
  searchLimit: number;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface ChatSession {
  id: string;
  messages: Message[];
  configId: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface AdminUser {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'user';
  createdAt: Date;
  lastLogin: Date;
}

export interface Analytics {
  totalChats: number;
  totalMessages: number;
  averageSessionLength: number;
  topQuestions: Array<{
    question: string;
    count: number;
  }>;
  dailyStats: Array<{
    date: string;
    chats: number;
    messages: number;
  }>;
}
