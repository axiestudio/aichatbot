import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Eye, Save, RotateCcw } from 'lucide-react'
import { toast } from 'react-hot-toast'
import { ChatConfig } from '../../types'

const defaultConfig: ChatConfig = {
  id: 'default',
  name: 'My Chatbot',
  primaryColor: '#3b82f6',
  secondaryColor: '#e5e7eb',
  fontFamily: 'Inter',
  fontSize: 14,
  borderRadius: 12,
  position: 'bottom-right',
  welcomeMessage: 'Hello! How can I help you today?',
  placeholder: 'Type your message...',
  height: 500,
  width: 350,
  isActive: true,
  createdAt: new Date(),
  updatedAt: new Date(),
}

export default function ChatDesign() {
  const [config, setConfig] = useState<ChatConfig>(defaultConfig)
  const [isPreviewOpen, setIsPreviewOpen] = useState(false)
  
  const { register, handleSubmit, watch, reset } = useForm<ChatConfig>({
    defaultValues: config
  })

  const watchedValues = watch()

  const onSubmit = async (data: ChatConfig) => {
    try {
      // In a real app, this would save to backend
      setConfig(data)
      toast.success('Chat design saved successfully!')
    } catch (error) {
      toast.error('Failed to save chat design')
    }
  }

  const resetToDefaults = () => {
    reset(defaultConfig)
    setConfig(defaultConfig)
    toast.success('Reset to default settings')
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Chat Design</h2>
          <p className="text-gray-600">Customize the appearance and behavior of your chat interface</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => setIsPreviewOpen(!isPreviewOpen)}
            className="btn-secondary flex items-center"
          >
            <Eye className="w-4 h-4 mr-2" />
            {isPreviewOpen ? 'Hide Preview' : 'Show Preview'}
          </button>
          <button
            onClick={resetToDefaults}
            className="btn-secondary flex items-center"
          >
            <RotateCcw className="w-4 h-4 mr-2" />
            Reset
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Configuration Form */}
        <div className="space-y-6">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* Basic Settings */}
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Basic Settings</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Chatbot Name
                  </label>
                  <input
                    {...register('name')}
                    type="text"
                    className="input-field"
                    placeholder="My Chatbot"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Welcome Message
                  </label>
                  <textarea
                    {...register('welcomeMessage')}
                    rows={3}
                    className="input-field"
                    placeholder="Hello! How can I help you today?"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Input Placeholder
                  </label>
                  <input
                    {...register('placeholder')}
                    type="text"
                    className="input-field"
                    placeholder="Type your message..."
                  />
                </div>
              </div>
            </div>

            {/* Appearance */}
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Appearance</h3>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Primary Color
                    </label>
                    <input
                      {...register('primaryColor')}
                      type="color"
                      className="w-full h-10 rounded-lg border border-gray-300"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Secondary Color
                    </label>
                    <input
                      {...register('secondaryColor')}
                      type="color"
                      className="w-full h-10 rounded-lg border border-gray-300"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Font Family
                  </label>
                  <select {...register('fontFamily')} className="input-field">
                    <option value="Inter">Inter</option>
                    <option value="Arial">Arial</option>
                    <option value="Helvetica">Helvetica</option>
                    <option value="Georgia">Georgia</option>
                    <option value="Times New Roman">Times New Roman</option>
                  </select>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Font Size (px)
                    </label>
                    <input
                      {...register('fontSize', { valueAsNumber: true })}
                      type="number"
                      min="10"
                      max="20"
                      className="input-field"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Border Radius (px)
                    </label>
                    <input
                      {...register('borderRadius', { valueAsNumber: true })}
                      type="number"
                      min="0"
                      max="25"
                      className="input-field"
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Layout */}
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Layout</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Position
                  </label>
                  <select {...register('position')} className="input-field">
                    <option value="bottom-right">Bottom Right</option>
                    <option value="bottom-left">Bottom Left</option>
                    <option value="top-right">Top Right</option>
                    <option value="top-left">Top Left</option>
                  </select>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Width (px)
                    </label>
                    <input
                      {...register('width', { valueAsNumber: true })}
                      type="number"
                      min="300"
                      max="500"
                      className="input-field"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Height (px)
                    </label>
                    <input
                      {...register('height', { valueAsNumber: true })}
                      type="number"
                      min="400"
                      max="700"
                      className="input-field"
                    />
                  </div>
                </div>
              </div>
            </div>

            <button
              type="submit"
              className="btn-primary w-full flex items-center justify-center"
            >
              <Save className="w-4 h-4 mr-2" />
              Save Configuration
            </button>
          </form>
        </div>

        {/* Live Preview */}
        {isPreviewOpen && (
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Live Preview</h3>
            <div className="relative bg-gray-100 rounded-lg p-4 h-96 overflow-hidden">
              <div 
                className="absolute bg-white shadow-lg rounded-lg flex flex-col"
                style={{
                  width: Math.min(watchedValues.width || 350, 300),
                  height: Math.min(watchedValues.height || 500, 350),
                  borderRadius: watchedValues.borderRadius || 12,
                  fontFamily: watchedValues.fontFamily || 'Inter',
                  fontSize: watchedValues.fontSize || 14,
                  bottom: '16px',
                  right: '16px'
                }}
              >
                {/* Header */}
                <div 
                  className="p-3 text-white rounded-t-lg"
                  style={{ 
                    backgroundColor: watchedValues.primaryColor || '#3b82f6',
                    borderRadius: `${watchedValues.borderRadius || 12}px ${watchedValues.borderRadius || 12}px 0 0`
                  }}
                >
                  <h4 className="font-semibold text-sm">{watchedValues.name || 'My Chatbot'}</h4>
                </div>

                {/* Messages */}
                <div className="flex-1 p-3 space-y-2">
                  <div className="flex justify-start">
                    <div 
                      className="px-3 py-2 rounded-lg text-sm max-w-[80%]"
                      style={{ 
                        backgroundColor: watchedValues.secondaryColor || '#e5e7eb',
                        borderRadius: watchedValues.borderRadius || 12
                      }}
                    >
                      {watchedValues.welcomeMessage || 'Hello! How can I help you today?'}
                    </div>
                  </div>
                  <div className="flex justify-end">
                    <div 
                      className="px-3 py-2 rounded-lg text-sm text-white max-w-[80%]"
                      style={{ 
                        backgroundColor: watchedValues.primaryColor || '#3b82f6',
                        borderRadius: watchedValues.borderRadius || 12
                      }}
                    >
                      This is a sample message
                    </div>
                  </div>
                </div>

                {/* Input */}
                <div className="p-3 border-t border-gray-200">
                  <div className="flex items-center gap-2">
                    <input
                      type="text"
                      placeholder={watchedValues.placeholder || 'Type your message...'}
                      className="flex-1 px-2 py-1 text-sm border border-gray-300 rounded"
                      style={{ borderRadius: watchedValues.borderRadius || 12 }}
                      disabled
                    />
                    <button
                      className="p-1 text-white rounded"
                      style={{ 
                        backgroundColor: watchedValues.primaryColor || '#3b82f6',
                        borderRadius: watchedValues.borderRadius || 12
                      }}
                      disabled
                    >
                      →
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
