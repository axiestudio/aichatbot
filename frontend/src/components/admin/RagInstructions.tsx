import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Save, FileText, Eye, RotateCcw } from 'lucide-react'
import { toast } from 'react-hot-toast'
import { RagInstruction } from '../../types'

const defaultInstruction: RagInstruction = {
  id: 'default',
  name: 'Default RAG Configuration',
  systemPrompt: `You are a helpful AI assistant. Use the provided context to answer user questions accurately and helpfully. If the context doesn't contain relevant information, politely say so and provide general guidance if appropriate.

Guidelines:
- Always be helpful and professional
- Use the context provided to give accurate answers
- If unsure, acknowledge uncertainty
- Keep responses concise but informative`,
  contextPrompt: `Context information:
{context}

Based on the above context, please answer the following question:
{question}`,
  maxContextLength: 2000,
  searchLimit: 5,
  isActive: true,
  createdAt: new Date(),
  updatedAt: new Date(),
}

const presetPrompts = [
  {
    name: 'Customer Support',
    systemPrompt: `You are a customer support AI assistant. Use the provided knowledge base to help customers with their questions and issues. Always be polite, helpful, and professional.

Guidelines:
- Prioritize customer satisfaction
- Provide step-by-step solutions when possible
- Escalate complex issues appropriately
- Use a friendly and empathetic tone`,
    contextPrompt: `Support documentation:
{context}

Customer question: {question}

Please provide a helpful response based on the documentation above.`
  },
  {
    name: 'Technical Documentation',
    systemPrompt: `You are a technical documentation assistant. Help users understand technical concepts and procedures using the provided documentation. Be precise and detailed in your explanations.

Guidelines:
- Provide accurate technical information
- Include code examples when relevant
- Explain complex concepts clearly
- Reference specific documentation sections`,
    contextPrompt: `Technical documentation:
{context}

Technical question: {question}

Please provide a detailed technical response based on the documentation.`
  },
  {
    name: 'Sales Assistant',
    systemPrompt: `You are a sales assistant AI. Help potential customers understand products and services using the provided information. Be persuasive but honest, and focus on customer needs.

Guidelines:
- Understand customer needs first
- Highlight relevant benefits
- Provide accurate product information
- Guide towards appropriate solutions`,
    contextPrompt: `Product information:
{context}

Customer inquiry: {question}

Please provide a helpful sales response based on the product information.`
  }
]

export default function RagInstructions() {
  const [instruction, setInstruction] = useState<RagInstruction>(defaultInstruction)
  const [showPreview, setShowPreview] = useState(false)
  
  const { register, handleSubmit, setValue, watch, reset } = useForm<RagInstruction>({
    defaultValues: instruction
  })

  const watchedValues = watch()

  const onSubmit = async (data: RagInstruction) => {
    try {
      setInstruction(data)
      toast.success('RAG instructions saved successfully!')
    } catch (error) {
      toast.error('Failed to save RAG instructions')
    }
  }

  const loadPreset = (preset: typeof presetPrompts[0]) => {
    setValue('systemPrompt', preset.systemPrompt)
    setValue('contextPrompt', preset.contextPrompt)
    toast.success(`Loaded ${preset.name} preset`)
  }

  const resetToDefaults = () => {
    reset(defaultInstruction)
    setInstruction(defaultInstruction)
    toast.success('Reset to default settings')
  }

  const generatePreview = () => {
    const sampleContext = "Our company offers 24/7 customer support through multiple channels including phone, email, and live chat. We have a comprehensive knowledge base with over 500 articles covering common questions and troubleshooting guides."
    const sampleQuestion = "What support options are available?"
    
    return watchedValues.contextPrompt
      .replace('{context}', sampleContext)
      .replace('{question}', sampleQuestion)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">RAG Instructions</h2>
          <p className="text-gray-600">Configure how your AI assistant processes and responds to queries</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => setShowPreview(!showPreview)}
            className="btn-secondary flex items-center"
          >
            <Eye className="w-4 h-4 mr-2" />
            {showPreview ? 'Hide Preview' : 'Show Preview'}
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
          {/* Preset Templates */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Start Templates</h3>
            <div className="grid grid-cols-1 gap-3">
              {presetPrompts.map((preset, index) => (
                <button
                  key={index}
                  onClick={() => loadPreset(preset)}
                  className="text-left p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <div className="font-medium text-gray-900">{preset.name}</div>
                  <div className="text-sm text-gray-500 mt-1">
                    {preset.systemPrompt.substring(0, 100)}...
                  </div>
                </button>
              ))}
            </div>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* Basic Settings */}
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Basic Settings</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Configuration Name
                  </label>
                  <input
                    {...register('name')}
                    type="text"
                    className="input-field"
                    placeholder="My RAG Configuration"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Max Context Length
                    </label>
                    <input
                      {...register('maxContextLength', { valueAsNumber: true })}
                      type="number"
                      min="500"
                      max="8000"
                      className="input-field"
                      placeholder="2000"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Search Results Limit
                    </label>
                    <input
                      {...register('searchLimit', { valueAsNumber: true })}
                      type="number"
                      min="1"
                      max="20"
                      className="input-field"
                      placeholder="5"
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* System Prompt */}
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">System Prompt</h3>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Instructions for AI Behavior
                </label>
                <textarea
                  {...register('systemPrompt')}
                  rows={8}
                  className="input-field"
                  placeholder="Define how the AI should behave and respond..."
                />
                <p className="text-xs text-gray-500 mt-1">
                  This defines the AI's personality, tone, and general behavior guidelines.
                </p>
              </div>
            </div>

            {/* Context Prompt */}
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Context Prompt Template</h3>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  How to Present Context and Questions
                </label>
                <textarea
                  {...register('contextPrompt')}
                  rows={6}
                  className="input-field"
                  placeholder="Use {context} and {question} placeholders..."
                />
                <p className="text-xs text-gray-500 mt-1">
                  Use {'{context}'} for retrieved information and {'{question}'} for user queries.
                </p>
              </div>
            </div>

            <button
              type="submit"
              className="btn-primary w-full flex items-center justify-center"
            >
              <Save className="w-4 h-4 mr-2" />
              Save Instructions
            </button>
          </form>
        </div>

        {/* Preview */}
        {showPreview && (
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Preview</h3>
            <div className="space-y-4">
              <div>
                <h4 className="font-medium text-gray-900 mb-2">System Prompt</h4>
                <div className="p-3 bg-gray-50 rounded-lg text-sm">
                  {watchedValues.systemPrompt || 'No system prompt defined'}
                </div>
              </div>
              
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Context Template (Sample)</h4>
                <div className="p-3 bg-blue-50 rounded-lg text-sm">
                  {generatePreview()}
                </div>
              </div>

              <div>
                <h4 className="font-medium text-gray-900 mb-2">Configuration</h4>
                <div className="text-sm space-y-1">
                  <p><span className="font-medium">Max Context:</span> {watchedValues.maxContextLength} characters</p>
                  <p><span className="font-medium">Search Limit:</span> {watchedValues.searchLimit} results</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Best Practices */}
      <div className="card bg-yellow-50 border-yellow-200">
        <h3 className="text-lg font-semibold text-yellow-900 mb-2">Best Practices</h3>
        <div className="text-sm text-yellow-800 space-y-2">
          <p>• Keep system prompts clear and specific about desired behavior</p>
          <p>• Use context templates that clearly separate retrieved information from questions</p>
          <p>• Test different prompt variations to optimize response quality</p>
          <p>• Balance context length with response relevance</p>
          <p>• Include guidelines for handling uncertain or missing information</p>
        </div>
      </div>
    </div>
  )
}
