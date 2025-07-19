import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'
import { chatApi, memoryApi } from '@/utils/api'
import { STORAGE_KEYS } from '@/utils/constants'
import type { ChatStore, ChatSession, ChatMessage, UploadedFile } from '@/types'

// Enhanced chat store that bridges frontend localStorage with backend database
export const useEnhancedChatStore = create<ChatStore & {
  // Additional methods for backend integration
  syncWithBackend: (userId: string) => Promise<void>
  persistSessionToBackend: (session: ChatSession) => Promise<void>
  loadSessionFromBackend: (sessionId: string, userId: string) => Promise<ChatSession | null>
  enableBackendSync: boolean
  setBackendSync: (enabled: boolean) => void
}>()(
  devtools(
    persist(
      (set, get) => ({
        sessions: [],
        activeSession: null,
        isLoading: false,
        enableBackendSync: true, // Enable backend sync by default

        setBackendSync: (enabled: boolean) => {
          set({ enableBackendSync: enabled })
        },

        createSession: (agentId: string): ChatSession => {
          const newSession: ChatSession = {
            id: crypto.randomUUID(),
            title: `Chat with ${agentId}`,
            messages: [],
            agentId,
            createdAt: new Date(),
            updatedAt: new Date(),
          }

          set(state => ({
            sessions: [newSession, ...state.sessions],
            activeSession: newSession
          }))

          // Persist to backend if enabled
          const { enableBackendSync, persistSessionToBackend } = get()
          if (enableBackendSync) {
            persistSessionToBackend(newSession).catch(console.error)
          }

          return newSession
        },

        setActiveSession: (sessionId: string | null) => {
          const { sessions } = get()
          const session = sessionId ? sessions.find(s => s.id === sessionId) : null
          set({ activeSession: session })
        },

        updateSessionTitle: (sessionId: string, title: string) => {
          set(state => ({
            sessions: state.sessions.map(s => 
              s.id === sessionId ? { ...s, title, updatedAt: new Date() } : s
            ),
            activeSession: state.activeSession?.id === sessionId 
              ? { ...state.activeSession, title, updatedAt: new Date() }
              : state.activeSession
          }))

          // Update backend if enabled
          const { enableBackendSync } = get()
          if (enableBackendSync) {
            const session = get().sessions.find(s => s.id === sessionId)
            if (session) {
              memoryApi.updateSession(
                'master_coordinator', // Default app name
                'current_user', // Default user ID
                sessionId,
                { title }
              ).catch(console.error)
            }
          }
        },

        sendMessage: async (content: string, attachments?: UploadedFile[]): Promise<void> => {
          const { activeSession, enableBackendSync } = get()
          if (!activeSession) {
            throw new Error('No active session')
          }

          const userMessage: ChatMessage = {
            id: crypto.randomUUID(),
            content,
            role: 'user',
            timestamp: new Date(),
            agentId: activeSession.agentId,
            attachments,
          }

          // Add user message to session
          set(state => ({
            sessions: state.sessions.map(s => 
              s.id === activeSession.id 
                ? {
                    ...s,
                    messages: [...s.messages, userMessage],
                    updatedAt: new Date()
                  }
                : s
            ),
            activeSession: {
              ...activeSession,
              messages: [...activeSession.messages, userMessage],
              updatedAt: new Date()
            },
            isLoading: true
          }))

          // Persist user message to backend
          if (enableBackendSync) {
            try {
              await memoryApi.addMessage(
                activeSession.id,
                'user',
                content,
                activeSession.agentId,
                { attachments }
              )
            } catch (error) {
              console.error('Failed to persist user message to backend:', error)
            }
          }

          try {
            // Send message using existing ADK API
            const response = await chatApi.sendMessage(content, activeSession.agentId, attachments)
            
            if (response.success && response.data) {
              const assistantMessage = response.data

              // Add assistant response to session
              set(state => ({
                sessions: state.sessions.map(s => 
                  s.id === activeSession.id 
                    ? {
                        ...s,
                        messages: [...s.messages, assistantMessage],
                        updatedAt: new Date()
                      }
                    : s
                ),
                activeSession: {
                  ...activeSession,
                  messages: [...activeSession.messages, assistantMessage],
                  updatedAt: new Date()
                },
                isLoading: false
              }))

              // Persist assistant message to backend
              if (enableBackendSync) {
                try {
                  await memoryApi.addMessage(
                    activeSession.id,
                    'assistant',
                    assistantMessage.content,
                    assistantMessage.agentId,
                    assistantMessage.metadata
                  )
                } catch (error) {
                  console.error('Failed to persist assistant message to backend:', error)
                }
              }
            } else {
              throw new Error(response.error || 'Failed to send message')
            }
          } catch (error) {
            set({ isLoading: false })
            throw error
          }
        },

        sendMessageStreaming: async (
          content: string,
          onChunk: (chunk: string) => void,
          attachments?: UploadedFile[]
        ): Promise<void> => {
          const { activeSession, enableBackendSync } = get()
          if (!activeSession) {
            throw new Error('No active session')
          }

          const userMessage: ChatMessage = {
            id: crypto.randomUUID(),
            content,
            role: 'user',
            timestamp: new Date(),
            agentId: activeSession.agentId,
            attachments,
          }

          // Add user message
          set(state => ({
            sessions: state.sessions.map(s => 
              s.id === activeSession.id 
                ? {
                    ...s,
                    messages: [...s.messages, userMessage],
                    updatedAt: new Date()
                  }
                : s
            ),
            activeSession: {
              ...activeSession,
              messages: [...activeSession.messages, userMessage],
              updatedAt: new Date()
            },
            isLoading: true
          }))

          // Persist user message to backend
          if (enableBackendSync) {
            try {
              await memoryApi.addMessage(
                activeSession.id,
                'user',
                content,
                activeSession.agentId,
                { attachments }
              )
            } catch (error) {
              console.error('Failed to persist user message to backend:', error)
            }
          }

          try {
            let assistantContent = ''
            const assistantMessageId = crypto.randomUUID()

            // Create initial assistant message
            const assistantMessage: ChatMessage = {
              id: assistantMessageId,
              content: '',
              role: 'assistant',
              timestamp: new Date(),
              agentId: activeSession.agentId,
            }

            // Add empty assistant message
            set(state => ({
              sessions: state.sessions.map(s => 
                s.id === activeSession.id 
                  ? {
                      ...s,
                      messages: [...s.messages, assistantMessage],
                      updatedAt: new Date()
                    }
                  : s
              ),
              activeSession: {
                ...activeSession,
                messages: [...activeSession.messages, assistantMessage],
                updatedAt: new Date()
              }
            }))

            // Stream response
            await chatApi.sendMessageStreaming(
              content,
              (chunk: string) => {
                assistantContent += chunk
                onChunk(chunk)

                // Update assistant message with new content
                set(state => ({
                  sessions: state.sessions.map(s => 
                    s.id === activeSession.id 
                      ? {
                          ...s,
                          messages: s.messages.map(m => 
                            m.id === assistantMessageId 
                              ? { ...m, content: assistantContent }
                              : m
                          ),
                          updatedAt: new Date()
                        }
                      : s
                  ),
                  activeSession: state.activeSession ? {
                    ...state.activeSession,
                    messages: state.activeSession.messages.map(m => 
                      m.id === assistantMessageId 
                        ? { ...m, content: assistantContent }
                        : m
                    ),
                    updatedAt: new Date()
                  } : null
                }))
              },
              activeSession.agentId,
              attachments
            )

            // Persist final assistant message to backend
            if (enableBackendSync && assistantContent) {
              try {
                await memoryApi.addMessage(
                  activeSession.id,
                  'assistant',
                  assistantContent,
                  activeSession.agentId
                )
              } catch (error) {
                console.error('Failed to persist streamed message to backend:', error)
              }
            }

            set({ isLoading: false })
          } catch (error) {
            set({ isLoading: false })
            throw error
          }
        },

        deleteSession: (sessionId: string) => {
          const { enableBackendSync } = get()
          
          set(state => ({
            sessions: state.sessions.filter(s => s.id !== sessionId),
            activeSession: state.activeSession?.id === sessionId ? null : state.activeSession
          }))

          // Delete from backend if enabled
          if (enableBackendSync) {
            memoryApi.deleteSession(
              'master_coordinator',
              'current_user',
              sessionId
            ).catch(console.error)
          }
        },

        clearAllSessions: () => {
          set({ sessions: [], activeSession: null })
        },

        getSessionsByAgent: (agentId: string) => {
          return get().sessions.filter(s => s.agentId === agentId)
        },

        // Backend integration methods
        syncWithBackend: async (userId: string) => {
          try {
            const response = await memoryApi.listSessions(
              'master_coordinator',
              userId,
              false, // Include inactive sessions
              100 // Limit
            )

            if (response.success && response.data) {
              const backendSessions: ChatSession[] = response.data.map((session: any) => ({
                id: session.id,
                title: session.title || `Chat with ${session.agent_id}`,
                messages: session.messages || [],
                agentId: session.agent_id,
                createdAt: new Date(session.created_at),
                updatedAt: new Date(session.updated_at),
              }))

              // Merge with local sessions (backend takes precedence)
              const { sessions: localSessions } = get()
              const mergedSessions = [...backendSessions]
              
              // Add local sessions that don't exist in backend
              for (const localSession of localSessions) {
                if (!backendSessions.find(bs => bs.id === localSession.id)) {
                  mergedSessions.push(localSession)
                }
              }

              set({ sessions: mergedSessions })
            }
          } catch (error) {
            console.error('Failed to sync with backend:', error)
          }
        },

        persistSessionToBackend: async (session: ChatSession) => {
          try {
            await memoryApi.createSession(
              'master_coordinator',
              'current_user',
              session.agentId,
              session.id,
              session.title,
              {}, // Initial state
              { createdAt: session.createdAt.toISOString() }
            )
          } catch (error) {
            console.error('Failed to persist session to backend:', error)
          }
        },

        loadSessionFromBackend: async (sessionId: string, userId: string): Promise<ChatSession | null> => {
          try {
            const response = await memoryApi.getSession(
              'master_coordinator',
              userId,
              sessionId,
              true, // Include messages
              false // Don't need state for now
            )

            if (response.success && response.data) {
              const sessionData = response.data
              return {
                id: sessionData.id,
                title: sessionData.title,
                messages: sessionData.messages || [],
                agentId: sessionData.agent_id,
                createdAt: new Date(sessionData.created_at),
                updatedAt: new Date(sessionData.updated_at),
              }
            }
          } catch (error) {
            console.error('Failed to load session from backend:', error)
          }
          return null
        },
      }),
      {
        name: STORAGE_KEYS.chatSessions,
        partialize: (state) => ({
          sessions: state.sessions,
          enableBackendSync: state.enableBackendSync,
          // Don't persist activeSession to avoid stale state
        }),
      }
    ),
    {
      name: 'enhanced-chat-store',
    }
  )
)
