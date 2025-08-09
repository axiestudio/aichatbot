import React, { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { 
  Save, 
  Eye, 
  Palette, 
  Settings, 
  MessageSquare, 
  Upload,
  History,
  RotateCcw,
  Zap
} from 'lucide-react'
import { toast } from 'react-hot-toast'
import Card from '../ui/Card'
import Button from '../ui/Button'

interface LiveConfig {
  id: string
  instance_id: string
  chat_title: string
  chat_subtitle: string
  welcome_message: string
  placeholder_text: string
  primary_color: string
  secondary_color: string
  accent_color: string
  background_color: string
  text_color: string
  logo_url?: string
  company_name?: string
  show_branding: boolean
  custom_css?: string
  typing_indicator: boolean
  sound_enabled: boolean
  auto_scroll: boolean
  message_timestamps: boolean
  file_upload_enabled: boolean
  max_file_size_mb: number
  allowed_file_types: string[]
  messages_per_minute: number
  messages_per_hour: number
  conversation_starters: string[]
  quick_replies: string[]
  custom_fields: Record<string, any>
  is_active: boolean
  last_updated_by?: string
  created_at: string
  updated_at: string
}

const LiveConfiguration: React.FC = () => {
  const [config, setConfig] = useState<LiveConfig | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [activeTab, setActiveTab] = useState('appearance')
  const [showPreview, setShowPreview] = useState(false)
  const [history, setHistory] = useState([])

  const { register, handleSubmit, watch, setValue, reset, formState: { errors } } = useForm<LiveConfig>()

  const tabs = [
    { id: 'appearance', name: 'Appearance', icon: Palette },
    { id: 'content', name: 'Content', icon: MessageSquare },
    { id: 'behavior', name: 'Behavior', icon: Settings },
    { id: 'features', name: 'Features', icon: Zap },
    { id: 'history', name: 'History', icon: History }
  ]

  useEffect(() => {
    loadConfiguration()
    setupWebSocket()
  }, [])

  const loadConfiguration = async () => {
    try {
      const response = await fetch('/api/v1/admin/live-config/', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setConfig(data)
        reset(data)
      } else {
        toast.error('Failed to load configuration')
      }
    } catch (error) {
      toast.error('Error loading configuration')
    } finally {
      setIsLoading(false)
    }
  }

  const setupWebSocket = () => {
    // Setup WebSocket for real-time updates
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//${window.location.host}/api/v1/ws/default?connection_type=admin`
    
    const ws = new WebSocket(wsUrl)
    
    ws.onmessage = (event) => {
      const message = JSON.parse(event.data)
      if (message.type === 'config_update') {
        toast.success('Configuration updated in real-time!')
        loadConfiguration() // Reload to get latest config
      }
    }
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }
    
    return () => ws.close()
  }

  const onSubmit = async (data: LiveConfig) => {
    setIsSaving(true)
    
    try {
      const response = await fetch('/api/v1/admin/live-config/', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
        },
        body: JSON.stringify(data)
      })

      if (response.ok) {
        const updatedConfig = await response.json()
        setConfig(updatedConfig)
        toast.success('Configuration updated successfully! Changes are live.')
      } else {
        const error = await response.json()
        toast.error(error.detail || 'Failed to update configuration')
      }
    } catch (error) {
      toast.error('Error updating configuration')
    } finally {
      setIsSaving(false)
    }
  }

  const loadHistory = async () => {
    try {
      const response = await fetch('/api/v1/admin/live-config/history', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setHistory(data)
      }
    } catch (error) {
      toast.error('Error loading history')
    }
  }

  const rollbackConfig = async (historyId: string) => {
    try {
      const response = await fetch(`/api/v1/admin/live-config/rollback/${historyId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
        }
      })

      if (response.ok) {
        toast.success('Configuration rolled back successfully!')
        loadConfiguration()
      } else {
        toast.error('Failed to rollback configuration')
      }
    } catch (error) {
      toast.error('Error rolling back configuration')
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Live Configuration</h1>
          <p className="text-gray-600">Configure your chat interface in real-time</p>
        </div>
        <div className="flex items-center space-x-3">
          <Button
            variant="outline"
            onClick={() => setShowPreview(!showPreview)}
            className="flex items-center space-x-2"
          >
            <Eye className="w-4 h-4" />
            <span>{showPreview ? 'Hide' : 'Show'} Preview</span>
          </Button>
          <Button
            onClick={handleSubmit(onSubmit)}
            disabled={isSaving}
            className="flex items-center space-x-2"
          >
            <Save className="w-4 h-4" />
            <span>{isSaving ? 'Saving...' : 'Save Changes'}</span>
          </Button>
        </div>
      </div>

      {/* Live Status Indicator */}
      <Card className="p-4 bg-green-50 border-green-200">
        <div className="flex items-center space-x-3">
          <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
          <span className="text-green-800 font-medium">Live Configuration Active</span>
          <span className="text-green-600 text-sm">Changes apply instantly to your chat interface</span>
        </div>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Configuration Panel */}
        <div className="lg:col-span-2">
          {/* Tabs */}
          <div className="border-b border-gray-200 mb-6">
            <nav className="-mb-px flex space-x-8">
              {tabs.map((tab) => {
                const Icon = tab.icon
                return (
                  <button
                    key={tab.id}
                    onClick={() => {
                      setActiveTab(tab.id)
                      if (tab.id === 'history') loadHistory()
                    }}
                    className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                      activeTab === tab.id
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span>{tab.name}</span>
                  </button>
                )
              })}
            </nav>
          </div>

          {/* Tab Content */}
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {activeTab === 'appearance' && (
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Visual Appearance</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Primary Color
                    </label>
                    <div className="flex items-center space-x-2">
                      <input
                        type="color"
                        {...register('primary_color')}
                        className="w-12 h-10 border border-gray-300 rounded"
                      />
                      <input
                        type="text"
                        {...register('primary_color')}
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-lg"
                        placeholder="#3b82f6"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Secondary Color
                    </label>
                    <div className="flex items-center space-x-2">
                      <input
                        type="color"
                        {...register('secondary_color')}
                        className="w-12 h-10 border border-gray-300 rounded"
                      />
                      <input
                        type="text"
                        {...register('secondary_color')}
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-lg"
                        placeholder="#e5e7eb"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Accent Color
                    </label>
                    <div className="flex items-center space-x-2">
                      <input
                        type="color"
                        {...register('accent_color')}
                        className="w-12 h-10 border border-gray-300 rounded"
                      />
                      <input
                        type="text"
                        {...register('accent_color')}
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-lg"
                        placeholder="#10b981"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Background Color
                    </label>
                    <div className="flex items-center space-x-2">
                      <input
                        type="color"
                        {...register('background_color')}
                        className="w-12 h-10 border border-gray-300 rounded"
                      />
                      <input
                        type="text"
                        {...register('background_color')}
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-lg"
                        placeholder="#ffffff"
                      />
                    </div>
                  </div>
                </div>

                <div className="mt-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Logo URL
                  </label>
                  <input
                    type="url"
                    {...register('logo_url')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    placeholder="https://example.com/logo.png"
                  />
                </div>

                <div className="mt-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Company Name
                  </label>
                  <input
                    type="text"
                    {...register('company_name')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    placeholder="Your Company Name"
                  />
                </div>

                <div className="mt-4">
                  <label className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      {...register('show_branding')}
                      className="rounded"
                    />
                    <span className="text-sm font-medium text-gray-700">Show Branding</span>
                  </label>
                </div>
              </Card>
            )}

            {activeTab === 'content' && (
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Content & Messaging</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Chat Title
                    </label>
                    <input
                      type="text"
                      {...register('chat_title')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                      placeholder="AI Assistant"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Chat Subtitle
                    </label>
                    <input
                      type="text"
                      {...register('chat_subtitle')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                      placeholder="How can I help you today?"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Welcome Message
                    </label>
                    <textarea
                      {...register('welcome_message')}
                      rows={3}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                      placeholder="Hello! How can I assist you today?"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Input Placeholder
                    </label>
                    <input
                      type="text"
                      {...register('placeholder_text')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                      placeholder="Type your message..."
                    />
                  </div>
                </div>
              </Card>
            )}

            {/* Add other tab content here */}
          </form>
        </div>

        {/* Preview Panel */}
        {showPreview && (
          <div className="lg:col-span-1">
            <Card className="p-4 sticky top-4">
              <h3 className="text-lg font-semibold mb-4">Live Preview</h3>
              <div className="border rounded-lg p-4 bg-gray-50">
                <p className="text-sm text-gray-600">Chat preview would appear here...</p>
                {/* TODO: Implement live chat preview */}
              </div>
            </Card>
          </div>
        )}
      </div>
    </div>
  )
}

export default LiveConfiguration
