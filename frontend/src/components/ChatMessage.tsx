import React, { useState } from 'react'
import {
  Copy,
  Reply,
  MoreHorizontal,
  ThumbsUp,
  ThumbsDown,
  Heart,
  Download,
  Play,
  Pause,
  Image,
  FileText,
  Check,
  CheckCheck,
  Clock
} from 'lucide-react'
import { Message } from '../hooks/useChat'

interface ChatMessageProps {
  message: Message
  isTyping?: boolean
  onReply?: (message: Message) => void
  onReaction?: (messageId: string, reaction: string) => void
  onCopy?: (content: string) => void
  onDelete?: (messageId: string) => void
  showActions?: boolean
}

const ChatMessage: React.FC<ChatMessageProps> = ({
  message,
  isTyping = false,
  onReply,
  onReaction,
  onCopy,
  onDelete,
  showActions = true
}) => {
  const [showActionsMenu, setShowActionsMenu] = useState(false)
  const [isPlaying, setIsPlaying] = useState(false)

  const isUser = message.role === 'user'

  const formatTime = (timestamp: Date) => {
    return new Intl.DateTimeFormat('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    }).format(timestamp)
  }

  const handleCopy = () => {
    if (onCopy) {
      onCopy(message.content)
    } else {
      navigator.clipboard.writeText(message.content)
    }
    setShowActionsMenu(false)
  }

  const handleReaction = (reaction: string) => {
    if (onReaction) {
      onReaction(message.id, reaction)
    }
  }

  const renderAttachment = (attachment: any) => {
    if (attachment.type?.startsWith('image/')) {
      return (
        <div className="mt-2">
          <img
            src={attachment.url}
            alt={attachment.name}
            className="max-w-xs rounded-lg shadow-sm cursor-pointer hover:shadow-md transition-shadow"
            onClick={() => window.open(attachment.url, '_blank')}
          />
        </div>
      )
    }

    if (attachment.type?.startsWith('audio/')) {
      return (
        <div className="mt-2 flex items-center space-x-2 bg-gray-100 rounded-lg p-3">
          <button
            onClick={() => setIsPlaying(!isPlaying)}
            className="p-2 bg-blue-600 text-white rounded-full hover:bg-blue-700 transition-colors"
          >
            {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
          </button>
          <span className="text-sm text-gray-700">{attachment.name}</span>
        </div>
      )
    }

    return (
      <div className="mt-2 flex items-center space-x-2 bg-gray-100 rounded-lg p-3">
        <FileText className="w-5 h-5 text-gray-600" />
        <span className="text-sm text-gray-700">{attachment.name}</span>
        <button
          onClick={() => window.open(attachment.url, '_blank')}
          className="ml-auto p-1 text-gray-500 hover:text-blue-600 transition-colors"
        >
          <Download className="w-4 h-4" />
        </button>
      </div>
    )
  }

  const getStatusIcon = () => {
    if (!isUser) return null

    switch (message.status) {
      case 'sending':
        return <Clock className="w-3 h-3 text-gray-400" />
      case 'sent':
        return <Check className="w-3 h-3 text-gray-400" />
      case 'delivered':
        return <CheckCheck className="w-3 h-3 text-gray-400" />
      case 'read':
        return <CheckCheck className="w-3 h-3 text-blue-500" />
      default:
        return null
    }
  }

  return (
    <div className={`group flex ${isUser ? 'justify-end' : 'justify-start'} mb-6 fade-in`}>
      <div className={`flex flex-col ${isUser ? 'items-end' : 'items-start'} max-w-sm lg:max-w-md relative`}>
        {/* Reply indicator */}
        {message.reply_to && (
          <div className="mb-2 px-3 py-2 bg-gray-100 rounded-lg text-xs text-gray-600 border-l-2 border-blue-500">
            <div className="font-medium">Replying to:</div>
            <div className="truncate">{message.reply_to.content}</div>
          </div>
        )}

        {/* Message Bubble */}
        <div
          className={`
            relative px-4 py-3 rounded-2xl text-sm leading-relaxed shadow-professional
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
              <span className="text-xs text-gray-500 ml-2">Thinking...</span>
            </div>
          ) : (
            <>
              <p className="whitespace-pre-wrap">{message.content}</p>

              {/* Attachments */}
              {message.attachments?.map((attachment, index) => (
                <div key={index}>
                  {renderAttachment(attachment)}
                </div>
              ))}
            </>
          )}

          {/* Actions Menu */}
          {showActions && !isTyping && (
            <div className={`absolute top-0 ${isUser ? 'left-0 -translate-x-full' : 'right-0 translate-x-full'} opacity-0 group-hover:opacity-100 transition-opacity`}>
              <div className="flex items-center space-x-1 bg-white border border-gray-200 rounded-lg shadow-lg p-1 ml-2 mr-2">
                {/* Quick Reactions */}
                <button
                  onClick={() => handleReaction('👍')}
                  className="p-1 hover:bg-gray-100 rounded text-sm"
                  title="Like"
                >
                  👍
                </button>
                <button
                  onClick={() => handleReaction('❤️')}
                  className="p-1 hover:bg-gray-100 rounded text-sm"
                  title="Love"
                >
                  ❤️
                </button>

                {/* Reply */}
                {onReply && (
                  <button
                    onClick={() => onReply(message)}
                    className="p-1 hover:bg-gray-100 rounded"
                    title="Reply"
                  >
                    <Reply className="w-4 h-4 text-gray-600" />
                  </button>
                )}

                {/* Copy */}
                <button
                  onClick={handleCopy}
                  className="p-1 hover:bg-gray-100 rounded"
                  title="Copy"
                >
                  <Copy className="w-4 h-4 text-gray-600" />
                </button>

                {/* More Actions */}
                <div className="relative">
                  <button
                    onClick={() => setShowActionsMenu(!showActionsMenu)}
                    className="p-1 hover:bg-gray-100 rounded"
                    title="More actions"
                  >
                    <MoreHorizontal className="w-4 h-4 text-gray-600" />
                  </button>

                  {showActionsMenu && (
                    <div className="absolute top-8 right-0 bg-white border border-gray-200 rounded-lg shadow-lg py-1 z-10 min-w-32">
                      {isUser && onDelete && (
                        <button
                          onClick={() => {
                            onDelete(message.id)
                            setShowActionsMenu(false)
                          }}
                          className="w-full px-3 py-2 text-left text-sm text-red-600 hover:bg-red-50"
                        >
                          Delete
                        </button>
                      )}
                      <button
                        onClick={() => {
                          // Forward functionality
                          setShowActionsMenu(false)
                        }}
                        className="w-full px-3 py-2 text-left text-sm text-gray-700 hover:bg-gray-50"
                      >
                        Forward
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Reactions */}
        {message.reactions && message.reactions.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-1">
            {message.reactions.map((reaction, index) => (
              <button
                key={index}
                onClick={() => handleReaction(reaction.emoji)}
                className="flex items-center space-x-1 bg-gray-100 hover:bg-gray-200 rounded-full px-2 py-1 text-xs transition-colors"
              >
                <span>{reaction.emoji}</span>
                <span className="text-gray-600">{reaction.count}</span>
              </button>
            ))}
          </div>
        )}

        {/* Timestamp and Status */}
        {!isTyping && (
          <div className={`flex items-center space-x-1 mt-1 px-1 ${isUser ? 'flex-row-reverse space-x-reverse' : ''}`}>
            <span className="text-xs text-gray-500">
              {formatTime(message.timestamp)}
            </span>
            {getStatusIcon()}
          </div>
        )}
      </div>
    </div>
  )
}

export default ChatMessage
