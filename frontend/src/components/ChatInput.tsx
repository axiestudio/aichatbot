import React, { useState, KeyboardEvent, useRef, useEffect, useCallback } from 'react'
import {
  Paperclip,
  Smile,
  Mic,
  MicOff,
  Image,
  FileText,
  X,
  Send,
  Loader2
} from 'lucide-react'

interface ChatInputProps {
  onSendMessage: (message: string, attachments?: File[]) => void
  onTyping?: (isTyping: boolean) => void
  disabled?: boolean
  placeholder?: string
  maxLength?: number
  allowAttachments?: boolean
  allowVoiceInput?: boolean
  supportedFileTypes?: string[]
}

const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  onTyping,
  disabled = false,
  placeholder = "Type your message...",
  maxLength = 1000,
  allowAttachments = true,
  allowVoiceInput = true,
  supportedFileTypes = ['.pdf', '.txt', '.docx', '.jpg', '.png', '.gif']
}) => {
  const [message, setMessage] = useState('')
  const [attachments, setAttachments] = useState<File[]>([])
  const [isRecording, setIsRecording] = useState(false)
  const [showEmojiPicker, setShowEmojiPicker] = useState(false)
  const [isTyping, setIsTyping] = useState(false)

  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const typingTimeoutRef = useRef<NodeJS.Timeout>()
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if ((message.trim() || attachments.length > 0) && !disabled) {
      onSendMessage(message.trim(), attachments)
      setMessage('')
      setAttachments([])
      resetTextareaHeight()
      handleTypingStop()
    }
  }

  const handleTypingStart = useCallback(() => {
    if (!isTyping && onTyping) {
      setIsTyping(true)
      onTyping(true)
    }

    // Clear existing timeout
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current)
    }

    // Set new timeout to stop typing indicator
    typingTimeoutRef.current = setTimeout(() => {
      handleTypingStop()
    }, 2000)
  }, [isTyping, onTyping])

  const handleTypingStop = useCallback(() => {
    if (isTyping && onTyping) {
      setIsTyping(false)
      onTyping(false)
    }
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current)
    }
  }, [isTyping, onTyping])

  const handleMessageChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMessage(e.target.value)
    handleTypingStart()
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

  // File upload handling
  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || [])
    const validFiles = files.filter(file => {
      const extension = '.' + file.name.split('.').pop()?.toLowerCase()
      return supportedFileTypes.includes(extension) && file.size <= 10 * 1024 * 1024 // 10MB limit
    })

    setAttachments(prev => [...prev, ...validFiles])
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const removeAttachment = (index: number) => {
    setAttachments(prev => prev.filter((_, i) => i !== index))
  }

  // Voice recording
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mediaRecorder = new MediaRecorder(stream)
      mediaRecorderRef.current = mediaRecorder

      const chunks: BlobPart[] = []
      mediaRecorder.ondataavailable = (e) => chunks.push(e.data)
      mediaRecorder.onstop = () => {
        const blob = new Blob(chunks, { type: 'audio/wav' })
        const file = new File([blob], `voice-${Date.now()}.wav`, { type: 'audio/wav' })
        setAttachments(prev => [...prev, file])
        stream.getTracks().forEach(track => track.stop())
      }

      mediaRecorder.start()
      setIsRecording(true)
    } catch (error) {
      console.error('Error starting recording:', error)
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
    }
  }

  // Emoji handling
  const insertEmoji = (emoji: string) => {
    const textarea = textareaRef.current
    if (textarea) {
      const start = textarea.selectionStart
      const end = textarea.selectionEnd
      const newMessage = message.slice(0, start) + emoji + message.slice(end)
      setMessage(newMessage)

      // Reset cursor position
      setTimeout(() => {
        textarea.selectionStart = textarea.selectionEnd = start + emoji.length
        textarea.focus()
      }, 0)
    }
    setShowEmojiPicker(false)
  }

  useEffect(() => {
    adjustTextareaHeight()
  }, [message])

  useEffect(() => {
    return () => {
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current)
      }
    }
  }, [])

  const isMessageValid = message.trim().length > 0 || attachments.length > 0
  const isOverLimit = message.length > maxLength

  return (
    <div className="border-t border-gray-200 bg-white">
      {/* Attachments Preview */}
      {attachments.length > 0 && (
        <div className="px-6 py-3 border-b border-gray-100">
          <div className="flex flex-wrap gap-2">
            {attachments.map((file, index) => (
              <div key={index} className="flex items-center space-x-2 bg-gray-100 rounded-lg px-3 py-2">
                {file.type.startsWith('image/') ? (
                  <Image className="w-4 h-4 text-blue-600" />
                ) : file.type.startsWith('audio/') ? (
                  <Mic className="w-4 h-4 text-green-600" />
                ) : (
                  <FileText className="w-4 h-4 text-gray-600" />
                )}
                <span className="text-sm text-gray-700 truncate max-w-32">
                  {file.name}
                </span>
                <button
                  type="button"
                  onClick={() => removeAttachment(index)}
                  className="text-gray-400 hover:text-red-500 transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="px-6 py-4">
        <form onSubmit={handleSubmit} className="space-y-3">
          {/* Message Input */}
          <div className="flex items-end space-x-3">
            <div className="flex-1 relative">
              <textarea
                ref={textareaRef}
                value={message}
                onChange={handleMessageChange}
                onKeyPress={handleKeyPress}
                placeholder={placeholder}
                disabled={disabled}
                maxLength={maxLength}
                className={`
                  w-full px-4 py-3 pr-12 text-sm bg-gray-50 border border-gray-200 rounded-2xl
                  placeholder-gray-500 resize-none transition-all duration-200
                  focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 focus:bg-white
                  disabled:opacity-50 disabled:cursor-not-allowed
                  ${isMessageValid && !isOverLimit ? 'border-blue-200 bg-blue-50' : ''}
                  ${isOverLimit ? 'border-red-200 bg-red-50' : ''}
                `}
                rows={1}
                style={{
                  minHeight: '48px',
                  maxHeight: '120px',
                  lineHeight: '1.5'
                }}
              />

              {/* Character Count */}
              {message.length > maxLength * 0.8 && (
                <div className={`absolute bottom-1 right-3 text-xs ${
                  isOverLimit ? 'text-red-500' : 'text-gray-400'
                }`}>
                  {message.length}/{maxLength}
                </div>
              )}
            </div>

            {/* Action Buttons */}
            <div className="flex items-center space-x-2">
              {/* File Upload */}
              {allowAttachments && (
                <>
                  <input
                    ref={fileInputRef}
                    type="file"
                    multiple
                    accept={supportedFileTypes.join(',')}
                    onChange={handleFileSelect}
                    className="hidden"
                  />
                  <button
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    disabled={disabled}
                    className="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors disabled:opacity-50"
                    title="Attach file"
                  >
                    <Paperclip className="w-5 h-5" />
                  </button>
                </>
              )}

              {/* Emoji Picker */}
              <div className="relative">
                <button
                  type="button"
                  onClick={() => setShowEmojiPicker(!showEmojiPicker)}
                  disabled={disabled}
                  className="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors disabled:opacity-50"
                  title="Add emoji"
                >
                  <Smile className="w-5 h-5" />
                </button>

                {/* Simple Emoji Picker */}
                {showEmojiPicker && (
                  <div className="absolute bottom-12 right-0 bg-white border border-gray-200 rounded-lg shadow-lg p-3 z-10">
                    <div className="grid grid-cols-6 gap-1">
                      {['😀', '😂', '😍', '🤔', '👍', '👎', '❤️', '🎉', '🔥', '💯', '😊', '😢'].map(emoji => (
                        <button
                          key={emoji}
                          type="button"
                          onClick={() => insertEmoji(emoji)}
                          className="p-2 hover:bg-gray-100 rounded text-lg"
                        >
                          {emoji}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Voice Recording */}
              {allowVoiceInput && (
                <button
                  type="button"
                  onClick={isRecording ? stopRecording : startRecording}
                  disabled={disabled}
                  className={`p-2 rounded-lg transition-colors disabled:opacity-50 ${
                    isRecording
                      ? 'text-red-600 bg-red-50 hover:bg-red-100'
                      : 'text-gray-500 hover:text-blue-600 hover:bg-blue-50'
                  }`}
                  title={isRecording ? "Stop recording" : "Start voice recording"}
                >
                  {isRecording ? (
                    <MicOff className="w-5 h-5 animate-pulse" />
                  ) : (
                    <Mic className="w-5 h-5" />
                  )}
                </button>
              )}

              {/* Send Button */}
              <button
                type="submit"
                disabled={!isMessageValid || disabled || isOverLimit}
                className={`
                  flex items-center justify-center w-10 h-10 rounded-full transition-all duration-200
                  ${isMessageValid && !disabled && !isOverLimit
                    ? 'bg-blue-600 hover:bg-blue-700 text-white shadow-lg hover:shadow-xl transform hover:scale-105'
                    : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                  }
                `}
                title="Send message"
              >
                {disabled ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <Send className="w-5 h-5" />
                )}
              </button>
            </div>
          </div>
        </form>

          {/* Input Hints */}
          <div className="mt-2 flex items-center justify-between text-xs text-gray-500">
            <span>Press Enter to send, Shift + Enter for new line</span>
            {disabled && (
              <span className="text-orange-500">Please wait...</span>
            )}
          </div>
        </div>
      </div>
    )
}

export default ChatInput
