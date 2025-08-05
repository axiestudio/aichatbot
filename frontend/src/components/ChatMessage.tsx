import React from 'react'
import { Message } from '../hooks/useChat'

interface ChatMessageProps {
  message: Message
  isTyping?: boolean
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message, isTyping = false }) => {
  const isUser = message.role === 'user'

  const formatTime = (timestamp: Date) => {
    return new Intl.DateTimeFormat('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    }).format(timestamp)
  }

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-6 fade-in`}>
      <div className={`flex flex-col ${isUser ? 'items-end' : 'items-start'} max-w-sm lg:max-w-md`}>
        {/* Message Bubble */}
        <div
          className={`
            px-4 py-3 rounded-2xl text-sm leading-relaxed shadow-professional
            ${isUser
              ? 'bg-blue-600 text-white'
              : 'bg-white text-gray-900 border border-gray-200'
            }
            ${isTyping ? 'pulse-subtle' : ''}
          `}
        >
          {isTyping ? (
            <div className="flex items-center space-x-1">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>
              <span className="text-xs text-gray-500 ml-2">Thinking</span>
            </div>
          ) : (
            <p className="whitespace-pre-wrap">{message.content}</p>
          )}
        </div>

        {/* Timestamp */}
        {!isTyping && (
          <div className={`mt-1 px-1 ${isUser ? 'text-right' : 'text-left'}`}>
            <span className="text-xs text-gray-500">
              {formatTime(message.timestamp)}
            </span>
          </div>
        )}
      </div>
    </div>
  )
}

export default ChatMessage
