import React, { useState, KeyboardEvent, useRef, useEffect } from 'react'

interface ChatInputProps {
  onSendMessage: (message: string) => void
  disabled?: boolean
  placeholder?: string
}

const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  disabled = false,
  placeholder = "Type your message..."
}) => {
  const [message, setMessage] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (message.trim() && !disabled) {
      onSendMessage(message.trim())
      setMessage('')
      resetTextareaHeight()
    }
  }

  const handleKeyPress = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  const resetTextareaHeight = () => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
    }
  }

  const adjustTextareaHeight = () => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      const scrollHeight = textareaRef.current.scrollHeight
      const maxHeight = 120 // 5 lines approximately
      textareaRef.current.style.height = `${Math.min(scrollHeight, maxHeight)}px`
    }
  }

  useEffect(() => {
    adjustTextareaHeight()
  }, [message])

  const isMessageValid = message.trim().length > 0

  return (
    <div className="border-t border-gray-200 bg-white px-6 py-4">
      <form onSubmit={handleSubmit} className="flex items-end space-x-3">
        {/* Message Input */}
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={placeholder}
            disabled={disabled}
            className={`
              w-full px-4 py-3 pr-12 text-sm bg-gray-50 border border-gray-200 rounded-2xl
              placeholder-gray-500 resize-none transition-all duration-200
              focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 focus:bg-white
              disabled:opacity-50 disabled:cursor-not-allowed
              ${isMessageValid ? 'border-blue-200 bg-blue-50' : ''}
            `}
            rows={1}
            style={{
              minHeight: '48px',
              maxHeight: '120px',
              lineHeight: '1.5'
            }}
          />

          {/* Character Count (optional) */}
          {message.length > 100 && (
            <div className="absolute bottom-1 right-3 text-xs text-gray-400">
              {message.length}/1000
            </div>
          )}
        </div>

        {/* Send Button */}
        <button
          type="submit"
          disabled={!isMessageValid || disabled}
          className={`
            flex items-center justify-center w-12 h-12 rounded-2xl font-medium text-sm
            transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2
            ${isMessageValid && !disabled
              ? 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500 shadow-sm hover:shadow-md transform hover:scale-105'
              : 'bg-gray-200 text-gray-400 cursor-not-allowed'
            }
          `}
          title="Send message"
        >
          <svg
            className="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
            />
          </svg>
        </button>
      </form>

      {/* Input Hints */}
      <div className="mt-2 flex items-center justify-between text-xs text-gray-500">
        <span>Press Enter to send, Shift + Enter for new line</span>
        {disabled && (
          <span className="text-orange-500">Please wait...</span>
        )}
      </div>
    </div>
  )
}

export default ChatInput
