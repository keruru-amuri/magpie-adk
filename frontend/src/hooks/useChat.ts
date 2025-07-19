import { useState, useCallback, useEffect } from 'react'
import { useChatStore } from '@/stores/chatStore'
import { useAgent } from '@/stores/agentStore'
import type { ChatSession, ChatMessage, UploadedFile } from '@/types'

export interface UseChatOptions {
  autoCreateSession?: boolean
  sessionId?: string
}

export interface UseChatReturn {
  // Session management
  activeSession: ChatSession | null
  sessions: ChatSession[]
  createSession: (agentId?: string) => ChatSession
  loadSession: (sessionId: string) => Promise<void>
  deleteSession: (sessionId: string) => void
  
  // Message management
  messages: ChatMessage[]
  sendMessage: (content: string, attachments?: UploadedFile[]) => Promise<void>
  
  // State
  isLoading: boolean
  error: string | null
  clearError: () => void
  
  // Utilities
  canSendMessage: boolean
  messageCount: number
}

export function useChat(options: UseChatOptions = {}): UseChatReturn {
  const { autoCreateSession = true, sessionId } = options
  const { activeAgent } = useAgent()
  const {
    sessions,
    activeSession,
    isLoading,
    createSession: createChatSession,
    sendMessage: sendChatMessage,
    loadSession: loadChatSession,
    deleteSession: deleteChatSession,

  } = useChatStore()

  const [error, setError] = useState<string | null>(null)

  // Auto-create session when agent changes
  useEffect(() => {
    if (autoCreateSession && activeAgent && !activeSession) {
      createChatSession(activeAgent.id)
    }
  }, [activeAgent, activeSession, autoCreateSession, createChatSession])

  // Load specific session if provided
  useEffect(() => {
    if (sessionId && sessionId !== activeSession?.id) {
      loadChatSession(sessionId)
    }
  }, [sessionId, activeSession?.id, loadChatSession])

  const clearError = useCallback(() => {
    setError(null)
  }, [])

  const createSession = useCallback((agentId?: string) => {
    const targetAgentId = agentId || activeAgent?.id
    if (!targetAgentId) {
      throw new Error('No agent available for session creation')
    }
    
    setError(null)
    return createChatSession(targetAgentId)
  }, [activeAgent?.id, createChatSession])

  const loadSession = useCallback(async (sessionId: string) => {
    try {
      setError(null)
      await loadChatSession(sessionId)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load session'
      setError(errorMessage)
      throw err
    }
  }, [loadChatSession])

  const deleteSession = useCallback((sessionId: string) => {
    setError(null)
    deleteChatSession(sessionId)
  }, [deleteChatSession])

  const sendMessage = useCallback(async (content: string, attachments?: UploadedFile[]) => {
    if (!activeSession) {
      const errorMessage = 'No active session'
      setError(errorMessage)
      throw new Error(errorMessage)
    }

    if (!content.trim()) {
      const errorMessage = 'Message content cannot be empty'
      setError(errorMessage)
      throw new Error(errorMessage)
    }

    try {
      setError(null)
      await sendChatMessage(content, attachments)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to send message'
      setError(errorMessage)
      throw err
    }
  }, [activeSession, sendChatMessage])

  const canSendMessage = Boolean(
    activeSession && 
    activeAgent && 
    !isLoading
  )

  const messages = activeSession?.messages || []
  const messageCount = messages.length

  return {
    // Session management
    activeSession,
    sessions,
    createSession,
    loadSession,
    deleteSession,
    
    // Message management
    messages,
    sendMessage,
    
    // State
    isLoading,
    error,
    clearError,
    
    // Utilities
    canSendMessage,
    messageCount
  }
}

// Hook for managing chat history
export function useChatHistory() {
  const { sessions } = useChatStore()

  const getSessionsByAgent = useCallback((agentId: string) => {
    return sessions.filter(session => session.agentId === agentId)
  }, [sessions])

  const getRecentSessions = useCallback((limit: number = 10) => {
    return sessions
      .sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime())
      .slice(0, limit)
  }, [sessions])

  const searchSessions = useCallback((query: string) => {
    const lowercaseQuery = query.toLowerCase()
    return sessions.filter(session => 
      session.title.toLowerCase().includes(lowercaseQuery) ||
      session.messages.some(message => 
        message.content.toLowerCase().includes(lowercaseQuery)
      )
    )
  }, [sessions])

  return {
    sessions,
    getSessionsByAgent,
    getRecentSessions,
    searchSessions,
    totalSessions: sessions.length
  }
}

// Hook for typing indicators and real-time features
export function useChatRealtime() {
  const [isTyping, setIsTyping] = useState(false)
  const [typingUsers] = useState<string[]>([])

  // Simulate typing indicator (would be replaced with real WebSocket implementation)
  const startTyping = useCallback(() => {
    setIsTyping(true)
    // Auto-stop typing after 3 seconds
    setTimeout(() => setIsTyping(false), 3000)
  }, [])

  const stopTyping = useCallback(() => {
    setIsTyping(false)
  }, [])

  return {
    isTyping,
    typingUsers,
    startTyping,
    stopTyping
  }
}

// Hook for message formatting and utilities
export function useMessageUtils() {
  const formatTimestamp = useCallback((timestamp: Date) => {
    const now = new Date()
    const messageDate = new Date(timestamp)
    const diffInHours = (now.getTime() - messageDate.getTime()) / (1000 * 60 * 60)

    if (diffInHours < 1) {
      return messageDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    } else if (diffInHours < 24) {
      return messageDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    } else {
      return messageDate.toLocaleDateString()
    }
  }, [])

  const getMessagePreview = useCallback((content: string, maxLength: number = 100) => {
    if (content.length <= maxLength) return content
    return content.substring(0, maxLength) + '...'
  }, [])

  const countTokens = useCallback((content: string) => {
    // Simple token estimation (would be replaced with actual tokenizer)
    return Math.ceil(content.length / 4)
  }, [])

  return {
    formatTimestamp,
    getMessagePreview,
    countTokens
  }
}
