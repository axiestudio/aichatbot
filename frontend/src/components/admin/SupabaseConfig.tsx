import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Eye, EyeOff, Save, TestTube, CheckCircle, XCircle, Plus, Trash2 } from 'lucide-react'
import { toast } from 'react-hot-toast'
import { SupabaseConfig as SupabaseConfigType } from '../../types'

const defaultConfig: SupabaseConfigType = {
  id: 'default',
  url: '',
  anonKey: '',
  serviceKey: '',
  tableName: 'knowledge_base',
  searchColumns: ['title', 'content'],
  isActive: false,
  createdAt: new Date(),
  updatedAt: new Date(),
}

export default function SupabaseConfig() {
  const [config, setConfig] = useState<SupabaseConfigType>(defaultConfig)
  const [showKeys, setShowKeys] = useState({ anon: false, service: false })
  const [isTestingConnection, setIsTestingConnection] = useState(false)
  const [connectionStatus, setConnectionStatus] = useState<'idle' | 'success' | 'error'>('idle')
  const [searchColumns, setSearchColumns] = useState<string[]>(defaultConfig.searchColumns)
  
  const { register, handleSubmit, formState: { errors } } = useForm<SupabaseConfigType>({
    defaultValues: config
  })

  const onSubmit = async (data: SupabaseConfigType) => {
    try {
      const configWithColumns = { ...data, searchColumns }
      setConfig(configWithColumns)
      toast.success('Supabase configuration saved successfully!')
    } catch (error) {
      toast.error('Failed to save Supabase configuration')
    }
  }

  const testConnection = async () => {
    setIsTestingConnection(true)
    setConnectionStatus('idle')
    
    try {
      // Simulate connection test
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      // In a real app, this would test the actual Supabase connection
      const success = Math.random() > 0.4 // 60% success rate for demo
      
      if (success) {
        setConnectionStatus('success')
        toast.success('Supabase connection successful!')
      } else {
        setConnectionStatus('error')
        toast.error('Supabase connection failed. Please check your credentials.')
      }
    } catch (error) {
      setConnectionStatus('error')
      toast.error('Failed to test Supabase connection')
    } finally {
      setIsTestingConnection(false)
    }
  }

  const addSearchColumn = () => {
    setSearchColumns([...searchColumns, ''])
  }

  const removeSearchColumn = (index: number) => {
    setSearchColumns(searchColumns.filter((_, i) => i !== index))
  }

  const updateSearchColumn = (index: number, value: string) => {
    const newColumns = [...searchColumns]
    newColumns[index] = value
    setSearchColumns(newColumns)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Supabase Configuration</h2>
          <p className="text-gray-600">Configure your Supabase database connection for RAG data storage</p>
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
        {/* Connection Details */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Connection Details</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Supabase URL
              </label>
              <input
                {...register('url', { 
                  required: 'Supabase URL is required',
                  pattern: {
                    value: /^https:\/\/[a-zA-Z0-9-]+\.supabase\.co$/,
                    message: 'Please enter a valid Supabase URL'
                  }
                })}
                type="url"
                className="input-field"
                placeholder="https://your-project.supabase.co"
              />
              {errors.url && (
                <p className="mt-1 text-sm text-red-600">{errors.url.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Anonymous Key
              </label>
              <div className="relative">
                <input
                  {...register('anonKey', { required: 'Anonymous key is required' })}
                  type={showKeys.anon ? 'text' : 'password'}
                  className="input-field pr-10"
                  placeholder="Enter your anonymous key"
                />
                <button
                  type="button"
                  onClick={() => setShowKeys(prev => ({ ...prev, anon: !prev.anon }))}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                >
                  {showKeys.anon ? (
                    <EyeOff className="h-5 w-5 text-gray-400" />
                  ) : (
                    <Eye className="h-5 w-5 text-gray-400" />
                  )}
                </button>
              </div>
              {errors.anonKey && (
                <p className="mt-1 text-sm text-red-600">{errors.anonKey.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Service Key (Optional)
              </label>
              <div className="relative">
                <input
                  {...register('serviceKey')}
                  type={showKeys.service ? 'text' : 'password'}
                  className="input-field pr-10"
                  placeholder="Enter your service key (for admin operations)"
                />
                <button
                  type="button"
                  onClick={() => setShowKeys(prev => ({ ...prev, service: !prev.service }))}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                >
                  {showKeys.service ? (
                    <EyeOff className="h-5 w-5 text-gray-400" />
                  ) : (
                    <Eye className="h-5 w-5 text-gray-400" />
                  )}
                </button>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Required for advanced operations like creating tables
              </p>
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

        {/* Table Configuration */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Table Configuration</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Table Name
              </label>
              <input
                {...register('tableName', { required: 'Table name is required' })}
                type="text"
                className="input-field"
                placeholder="knowledge_base"
              />
              {errors.tableName && (
                <p className="mt-1 text-sm text-red-600">{errors.tableName.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Search Columns
              </label>
              <div className="space-y-2">
                {searchColumns.map((column, index) => (
                  <div key={index} className="flex items-center space-x-2">
                    <input
                      type="text"
                      value={column}
                      onChange={(e) => updateSearchColumn(index, e.target.value)}
                      className="input-field flex-1"
                      placeholder="Column name (e.g., title, content)"
                    />
                    <button
                      type="button"
                      onClick={() => removeSearchColumn(index)}
                      className="p-2 text-red-600 hover:bg-red-50 rounded-lg"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                ))}
                <button
                  type="button"
                  onClick={addSearchColumn}
                  className="btn-secondary flex items-center"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Add Column
                </button>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Columns to search when retrieving relevant information
              </p>
            </div>
          </div>
        </div>

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

      {/* Setup Instructions */}
      <div className="card bg-green-50 border-green-200">
        <h3 className="text-lg font-semibold text-green-900 mb-2">Setup Instructions</h3>
        <div className="text-sm text-green-800 space-y-2">
          <p>1. Create a new project in Supabase</p>
          <p>2. Copy your project URL and API keys from Settings → API</p>
          <p>3. Create a table for your knowledge base with columns like 'title', 'content', 'metadata'</p>
          <p>4. Enable Row Level Security (RLS) if needed</p>
          <p>5. Test the connection to ensure everything works</p>
        </div>
      </div>
    </div>
  )
}
