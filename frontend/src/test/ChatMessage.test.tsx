import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import ChatMessage from '../components/ChatMessage'
import { Message } from '../hooks/useChat'

describe('ChatMessage', () => {
  const mockMessage: Message = {
    id: '1',
    content: 'Hello, world!',
    role: 'user',
    timestamp: new Date('2023-01-01T12:00:00Z')
  }

  it('renders user message correctly', () => {
    render(<ChatMessage message={mockMessage} />)
    
    expect(screen.getByText('Hello, world!')).toBeInTheDocument()
    expect(screen.getByText('12:00:00 PM')).toBeInTheDocument()
  })

  it('renders assistant message correctly', () => {
    const assistantMessage: Message = {
      ...mockMessage,
      role: 'assistant'
    }
    
    render(<ChatMessage message={assistantMessage} />)
    
    expect(screen.getByText('Hello, world!')).toBeInTheDocument()
  })

  it('applies correct styling for user messages', () => {
    render(<ChatMessage message={mockMessage} />)
    
    const messageContainer = screen.getByText('Hello, world!').closest('div')
    expect(messageContainer).toHaveClass('bg-blue-500', 'text-white')
  })

  it('applies correct styling for assistant messages', () => {
    const assistantMessage: Message = {
      ...mockMessage,
      role: 'assistant'
    }
    
    render(<ChatMessage message={assistantMessage} />)
    
    const messageContainer = screen.getByText('Hello, world!').closest('div')
    expect(messageContainer).toHaveClass('bg-gray-200', 'text-gray-800')
  })
})
