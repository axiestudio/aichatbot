import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Eye, EyeOff, Save, TestTube, CheckCircle, XCircle } from 'lucide-react'
import toast from 'react-hot-toast'
import { ApiConfig as ApiConfigType } from '../../types'

const defaultConfig: ApiConfigType = {
  id: 'default',
  provider: 'openai',
  apiKey: '',
  model: 'gpt-3.5-turbo',
  temperature: 0.7,
  maxTokens: 1000,
  isActive: false,
  createdAt: new Date(),
  updatedAt: new Date(),
}

export default function ApiConfig() {
  const [config, setConfig] = useState<ApiConfigType>(defaultConfig)
  const [showApiKey, setShowApiKey] = useState(false)
  const [isTestingConnection, setIsTestingConnection] = useState(false)
  const [connectionStatus, setConnectionStatus] = useState<'idle' | 'success' | 'error'>('idle')
  
  const { register, handleSubmit, watch, formState: { errors } } = useForm<ApiConfigType>({
    defaultValues: config
  })

  const watchedProvider = watch('provider')

  const onSubmit = async (data: ApiConfigType) => {
    try {
      // In a real app, this would save to backend
      setConfig(data)
      toast.success('API configuration saved successfully!')
    } catch (error) {
      toast.error('Failed to save API configuration')
    }
  }

  const testConnection = async () => {
    setIsTestingConnection(true)
    setConnectionStatus('idle')
    
    try {
      // Simulate API test
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      // In a real app, this would test the actual API connection
      const success = Math.random() > 0.3 // 70% success rate for demo
      
      if (success) {
        setConnectionStatus('success')
        toast.success('API connection successful!')
      } else {
        setConnectionStatus('error')
        toast.error('API connection failed. Please check your credentials.')
      }
    } catch (error) {
      setConnectionStatus('error')
      toast.error('Failed to test API connection')
    } finally {
      setIsTestingConnection(false)
    }
  }

  const getModelOptions = (provider: string) => {
    switch (provider) {
      case 'openai':
        return [
          { value: 'gpt-4', label: 'GPT-4' },
          { value: 'gpt-4-turbo-preview', label: 'GPT-4 Turbo' },
          { value: 'gpt-3.5-turbo', label: 'GPT-3.5 Turbo' },
        ]
      case 'anthropic':
        return [
          { value: 'claude-3-opus-20240229', label: 'Claude 3 Opus' },
          { value: 'claude-3-sonnet-20240229', label: 'Claude 3 Sonnet' },
          { value: 'claude-3-haiku-20240307', label: 'Claude 3 Haiku' },
        ]
      case 'custom':
        return [
          { value: 'custom-model', label: 'Custom Model' },
        ]
      default:
        return []
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">API Configuration</h2>
          <p className="text-gray-600">Configure your AI provider settings and API credentials</p>
        </div>
        <div className="flex items-center space-x-3">
          {connectionStatus === 'success' && (
            <div className="flex items-center text-green-600">
              <CheckCircle className="w-5 h-5 mr-2" />
              <span className="text-sm">Connected</span>
            </div>
          )}
          {connectionStatus === 'error' && (
            <div className="flex items-center text-red-600">
              <XCircle className="w-5 h-5 mr-2" />
              <span className="text-sm">Connection Failed</span>
            </div>
          )}
        </div>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Provider Selection */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">AI Provider</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Provider
              </label>
              <select {...register('provider')} className="input-field">
                <option value="openai">OpenAI</option>
                <option value="anthropic">Anthropic</option>
                <option value="custom">Custom API</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Model
              </label>
              <select {...register('model')} className="input-field">
                {getModelOptions(watchedProvider).map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* API Credentials */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">API Credentials</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                API Key
              </label>
              <div className="relative">
                <input
                  {...register('apiKey', { required: 'API Key is required' })}
                  type={showApiKey ? 'text' : 'password'}
                  className="input-field pr-10"
                  placeholder="Enter your API key"
                />
                <button
                  type="button"
                  onClick={() => setShowApiKey(!showApiKey)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                >
                  {showApiKey ? (
                    <EyeOff className="h-5 w-5 text-gray-400" />
                  ) : (
                    <Eye className="h-5 w-5 text-gray-400" />
                  )}
                </button>
              </div>
              {errors.apiKey && (
                <p className="mt-1 text-sm text-red-600">{errors.apiKey.message}</p>
              )}
            </div>

            <button
              type="button"
              onClick={testConnection}
              disabled={isTestingConnection}
              className="btn-secondary flex items-center"
            >
              <TestTube className="w-4 h-4 mr-2" />
              {isTestingConnection ? 'Testing...' : 'Test Connection'}
            </button>
          </div>
        </div>

        {/* Model Parameters */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Model Parameters</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Temperature: {watch('temperature')}
              </label>
              <input
                {...register('temperature', {
                  valueAsNumber: true,
                  min: 0,
                  max: 2,
                  step: 0.1
                })}
                type="range"
                min="0"
                max="2"
                step="0.1"
                className="w-full"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>More Focused</span>
                <span>More Creative</span>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Max Tokens
              </label>
              <input
                {...register('maxTokens', {
                  valueAsNumber: true,
                  min: 100,
                  max: 4000
                })}
                type="number"
                min="100"
                max="4000"
                className="input-field"
                placeholder="1000"
              />
              <p className="text-xs text-gray-500 mt-1">
                Maximum number of tokens in the response
              </p>
            </div>
          </div>
        </div>

        {/* Provider-specific settings */}
        {watchedProvider === 'custom' && (
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Custom API Settings</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  API Endpoint URL
                </label>
                <input
                  type="url"
                  className="input-field"
                  placeholder="https://api.example.com/v1/chat/completions"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Custom Headers (JSON)
                </label>
                <textarea
                  rows={3}
                  className="input-field"
                  placeholder='{"Authorization": "Bearer your-token"}'
                />
              </div>
            </div>
          </div>
        )}

        <div className="flex justify-end space-x-3">
          <button
            type="submit"
            className="btn-primary flex items-center"
          >
            <Save className="w-4 h-4 mr-2" />
            Save Configuration
          </button>
        </div>
      </form>

      {/* Usage Guidelines */}
      <div className="card bg-blue-50 border-blue-200">
        <h3 className="text-lg font-semibold text-blue-900 mb-2">Usage Guidelines</h3>
        <div className="text-sm text-blue-800 space-y-2">
          <p>• Keep your API keys secure and never share them publicly</p>
          <p>• Monitor your API usage to avoid unexpected charges</p>
          <p>• Test your configuration before deploying to production</p>
          <p>• Consider rate limiting for high-traffic applications</p>
        </div>
      </div>
    </div>
  )
}
