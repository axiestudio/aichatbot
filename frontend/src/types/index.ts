export interface MessageAttachment {
  id: string;
  filename: string;
  original_filename: string;
  file_size: number;
  mime_type: string;
  attachment_type: 'image' | 'audio' | 'document' | 'video';
  url: string;
  thumbnail_url?: string;
}

export interface MessageReaction {
  emoji: string;
  count: number;
  users: string[];
}

export interface MessageReply {
  message_id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
}

export interface Message {
  id: string;
  session_id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  status: 'sending' | 'sent' | 'delivered' | 'read' | 'failed';
  attachments: MessageAttachment[];
  reactions: MessageReaction[];
  reply_to?: MessageReply;
  edited_at?: Date;
  deleted_at?: Date;
  metadata: Record<string, any>;
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
  showTimestamps?: boolean;
  showAvatars?: boolean;
}

export interface ApiConfig {
  id: string;
  name?: string;
  provider: 'openai' | 'anthropic' | 'custom';
  apiKey: string;
  model: string;
  temperature: number;
  maxTokens: number;
  topP?: number;
  frequencyPenalty?: number;
  presencePenalty?: number;
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
  tenantId?: string;
  subscription?: {
    tier: 'free' | 'premium' | 'enterprise';
    status: 'active' | 'inactive' | 'cancelled' | 'past_due';
    current_period_end?: Date;
    cancel_at_period_end?: boolean;
  };
  usage?: {
    conversations: number;
    messages: number;
    storage: number;
    api_calls: number;
  };
  permissions?: {
    can_access_analytics: boolean;
    can_manage_billing: boolean;
    can_customize_branding: boolean;
    can_export_data: boolean;
    can_manage_users: boolean;
  };
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

export interface BillingPlan {
  id: string;
  tier: 'free' | 'premium' | 'enterprise';
  name: string;
  description: string;
  priceMonthly: number;
  priceYearly: number;
  features: {
    removeBranding?: boolean;
    customBranding?: boolean;
    conversationsLimit: number; // -1 for unlimited
    advancedAnalytics?: boolean;
    prioritySupport?: boolean;
    apiAccess?: boolean;
    customIntegrations?: boolean;
  };
  popular?: boolean;
}

export interface IntelligenceAnalytics {
  total_analyzed: number;
  sentiment_distribution: Record<string, number>;
  intent_distribution: Record<string, number>;
  avg_satisfaction: number;
  avg_urgency: number;
  top_topics: Array<{ topic: string; count: number }>;
}

export interface ModerationAnalytics {
  total_content_moderated: number;
  action_distribution: Record<string, number>;
  toxicity_distribution: Record<string, number>;
  block_rate: number;
  flag_rate: number;
  average_ai_safety_score: number;
}

export interface KnowledgeGraphAnalytics {
  total_entities: number;
  total_relationships: number;
  entity_types: Record<string, number>;
  relationship_types: Record<string, number>;
  extraction_stats: Record<string, number>;
}
