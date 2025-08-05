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
  })

  it('renders assistant message correctly', () => {
    const assistantMessage: Message = {
      ...mockMessage,
      role: 'assistant'
    }

    render(<ChatMessage message={assistantMessage} />)

    expect(screen.getByText('Hello, world!')).toBeInTheDocument()
  })

  it('handles message data structure', () => {
    expect(mockMessage.content).toBe('Hello, world!')
    expect(mockMessage.role).toBe('user')
    expect(mockMessage.id).toBe('1')
  })
})
