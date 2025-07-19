import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'
import { chatApi } from '@/utils/api'
import { STORAGE_KEYS } from '@/utils/constants'
import type { ChatStore, ChatSession, ChatMessage, UploadedFile } from '@/types'

export const useChatStore = create<ChatStore>()(
  devtools(
    persist(
      (set, get) => ({
        sessions: [],
        activeSession: null,
        isLoading: false,

        createSession: (agentId: string): ChatSession => {
          // Clear any existing ADK session when creating a new one
          chatApi.clearSession()

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

          console.log('✅ Created new chat session for agent:', agentId)

          // Try to create session on backend
          chatApi.createSession(agentId).then(response => {
            if (response.success && response.data) {
              set(state => ({
                sessions: state.sessions.map(s =>
                  s.id === newSession.id
                    ? { ...s, ...response.data, id: newSession.id }
                    : s
                ),
                activeSession: state.activeSession?.id === newSession.id
                  ? { ...newSession, ...response.data, id: newSession.id }
                  : state.activeSession
              }))
            }
          }).catch(error => {
            console.error('Failed to create session on backend:', error)
          })

          return newSession
        },

        sendMessage: async (content: string, attachments?: UploadedFile[]): Promise<void> => {
          const { activeSession } = get()
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

          try {
            // Send message to backend
            const response = await chatApi.sendMessage(
              content,
              activeSession.agentId,
              attachments
            )

            if (response.success && response.data) {
              // Handle multiple messages if agent transfer occurred
              const messagesToAdd = (response as any).allMessages || [response.data]

              set(state => ({
                sessions: state.sessions.map(s =>
                  s.id === activeSession.id
                    ? {
                        ...s,
                        messages: [...s.messages, ...messagesToAdd],
                        updatedAt: new Date()
                      }
                    : s
                ),
                activeSession: {
                  ...state.activeSession!,
                  messages: [...state.activeSession!.messages, ...messagesToAdd],
                  updatedAt: new Date()
                },
                isLoading: false
              }))
            } else {
              throw new Error(response.error || 'Failed to send message')
            }
          } catch (error) {
            set({ isLoading: false })
            
            // Add error message
            const errorMessage: ChatMessage = {
              id: crypto.randomUUID(),
              content: 'Sorry, I encountered an error processing your message. Please try again.',
              role: 'assistant',
              timestamp: new Date(),
              agentId: activeSession.agentId,
            }

            set(state => ({
              sessions: state.sessions.map(s => 
                s.id === activeSession.id 
                  ? {
                      ...s,
                      messages: [...s.messages, errorMessage],
                      updatedAt: new Date()
                    }
                  : s
              ),
              activeSession: {
                ...state.activeSession!,
                messages: [...state.activeSession!.messages, errorMessage],
                updatedAt: new Date()
              }
            }))

            throw error
          }
        },

        loadSession: async (sessionId: string): Promise<void> => {
          set({ isLoading: true })

          try {
            // Find session in local storage first
            const localSession = get().sessions.find(s => s.id === sessionId)
            if (localSession) {
              set({ activeSession: localSession, isLoading: false })
            }

            // Try to load from backend
            const response = await chatApi.getChatHistory(sessionId)
            if (response.success && response.data) {
              const messages = response.data

              if (localSession) {
                // Update existing session with backend data
                const updatedSession = {
                  ...localSession,
                  messages,
                  updatedAt: new Date()
                }

                set(state => ({
                  sessions: state.sessions.map(s => 
                    s.id === sessionId ? updatedSession : s
                  ),
                  activeSession: updatedSession,
                  isLoading: false
                }))
              } else {
                // Create new session from backend data
                const newSession: ChatSession = {
                  id: sessionId,
                  title: `Chat Session`,
                  messages,
                  agentId: messages[0]?.agentId || 'unknown',
                  createdAt: messages[0]?.timestamp || new Date(),
                  updatedAt: new Date(),
                }

                set(state => ({
                  sessions: [newSession, ...state.sessions],
                  activeSession: newSession,
                  isLoading: false
                }))
              }
            } else {
              set({ isLoading: false })
            }
          } catch (error) {
            console.error('Failed to load session:', error)
            set({ isLoading: false })
          }
        },

        deleteSession: (sessionId: string) => {
          set(state => {
            const newSessions = state.sessions.filter(s => s.id !== sessionId)
            const newActiveSession = state.activeSession?.id === sessionId 
              ? (newSessions[0] || null)
              : state.activeSession

            return {
              sessions: newSessions,
              activeSession: newActiveSession
            }
          })
        },

        // Additional helper methods
        setActiveSession: (session: ChatSession | null) => {
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
        },

        clearAllSessions: () => {
          set({ sessions: [], activeSession: null })
        },

        getSessionsByAgent: (agentId: string) => {
          return get().sessions.filter(s => s.agentId === agentId)
        }
      }),
      {
        name: STORAGE_KEYS.chatSessions,
        partialize: (state) => ({
          sessions: state.sessions,
          // Don't persist activeSession to avoid stale state
        }),
      }
    ),
    {
      name: 'chat-store',
    }
  )
)
