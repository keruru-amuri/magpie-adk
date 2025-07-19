import React, { useState, useRef, useEffect } from 'react'
import { Send, Paperclip, Bot, AlertCircle, Loader2, FileText } from 'lucide-react'
import { useAgent } from '@/stores/agentStore'
import { useChatStore } from '@/stores/chatStore'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'
import { AgentAvatar } from '@/components/ui/AgentAvatar'
import { FileUpload } from '@/components/upload/FileUpload'
import { chatApi } from '@/utils/api'
import type { ChatMessage, ChatInterfaceProps, UploadedFile } from '@/types'

export function ChatInterface({ className, sessionId }: ChatInterfaceProps) {
  const { activeAgent } = useAgent()
  const { activeSession, createSession } = useChatStore()
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [attachedFiles, setAttachedFiles] = useState<UploadedFile[]>([])
  const [streamingMessage, setStreamingMessage] = useState<ChatMessage | null>(null)
  const [showFileModal, setShowFileModal] = useState(false)
  const [availableFiles, setAvailableFiles] = useState<UploadedFile[]>([])
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([])
  const [selectedFiles, setSelectedFiles] = useState<Set<string>>(new Set())

  const messagesEndRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // Use messages from active session or empty array
  const messages = activeSession?.messages || []

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Load chat history on mount
  useEffect(() => {
    if (sessionId) {
      loadChatHistory()
    }
  }, [sessionId])

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`
    }
  }, [inputValue])

  // Create a session if none exists and we have an active agent
  useEffect(() => {
    if (!activeSession && activeAgent) {
      console.log('Creating new session for agent:', activeAgent.id)
      createSession(activeAgent.id)
    }
  }, [activeSession, activeAgent, createSession])

  const loadChatHistory = async () => {
    // Chat history is now managed by the chat store
    // This function is kept for backward compatibility but doesn't need to do anything
    // since the chat store handles session loading
  }

  const sendMessage = async () => {
    if (!inputValue.trim() || !activeAgent || !activeSession) return

    // Store attached files before clearing
    const currentAttachedFiles = [...attachedFiles]
    const messageContent = inputValue.trim()

    // Clear input and attachments immediately
    setInputValue('')
    setAttachedFiles([])
    setError(null)
    setIsLoading(true)

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      content: messageContent,
      role: 'user',
      timestamp: new Date(),
      agentId: activeAgent.id,
      attachments: currentAttachedFiles.length > 0 ? currentAttachedFiles : undefined,
    }

    // Add user message to the session via chat store
    const updatedSession = {
      ...activeSession,
      messages: [...activeSession.messages, userMessage],
      updatedAt: new Date()
    }

    // Update the session in the store temporarily
    useChatStore.setState(state => ({
      activeSession: updatedSession,
      sessions: state.sessions.map(s =>
        s.id === activeSession.id ? updatedSession : s
      )
    }))

    // Initialize streaming message
    const streamingMessageId = crypto.randomUUID()
    const initialStreamingMessage: ChatMessage = {
      id: streamingMessageId,
      content: '',
      role: 'assistant',
      timestamp: new Date(),
      agentId: activeAgent.id,
    }
    setStreamingMessage(initialStreamingMessage)

    try {
      // Use streaming API for real-time responses
      await chatApi.sendMessageStreaming(
        userMessage.content,
        activeAgent.id,
        currentAttachedFiles, // Pass the attached files
        // onChunk: Update streaming message content
        (chunk: string) => {
          setStreamingMessage(prev => prev ? {
            ...prev,
            content: prev.content + chunk
          } : null)
        },
        // onComplete: Finalize the message(s)
        (finalMessage: ChatMessage) => {
          // Check if this is the first message being added (to avoid duplicates)
          const currentMessages = useChatStore.getState().activeSession?.messages || []
          const userMessageExists = currentMessages.some(m => m.id === userMessage.id)

          if (!userMessageExists) {
            // First completion - add user message and this assistant message
            const finalUpdatedSession = {
              ...activeSession,
              messages: [...activeSession.messages, userMessage, finalMessage],
              updatedAt: new Date()
            }

            useChatStore.setState(state => ({
              activeSession: finalUpdatedSession,
              sessions: state.sessions.map(s =>
                s.id === activeSession.id ? finalUpdatedSession : s
              )
            }))
          } else {
            // Subsequent completion (agent transfer) - add only the assistant message
            const currentSession = useChatStore.getState().activeSession!
            const finalUpdatedSession = {
              ...currentSession,
              messages: [...currentSession.messages, finalMessage],
              updatedAt: new Date()
            }

            useChatStore.setState(state => ({
              activeSession: finalUpdatedSession,
              sessions: state.sessions.map(s =>
                s.id === activeSession.id ? finalUpdatedSession : s
              )
            }))
          }

          setStreamingMessage(null)
          setIsLoading(false)
        },
        // onError: Handle streaming errors
        (errorMsg: string) => {
          console.error('Streaming error:', errorMsg)
          setError('Failed to send message. Please try again.')

          // Add error message to chat store
          const errorMessage: ChatMessage = {
            id: crypto.randomUUID(),
            content: 'Sorry, I encountered an error processing your message. Please try again.',
            role: 'assistant',
            timestamp: new Date(),
            agentId: activeAgent.id,
          }

          const errorUpdatedSession = {
            ...activeSession,
            messages: [...activeSession.messages, userMessage, errorMessage],
            updatedAt: new Date()
          }

          useChatStore.setState(state => ({
            activeSession: errorUpdatedSession,
            sessions: state.sessions.map(s =>
              s.id === activeSession.id ? errorUpdatedSession : s
            )
          }))

          setStreamingMessage(null)
          setIsLoading(false)
        }
      )
    } catch (error) {
      console.error('Failed to send message:', error)
      setError('Failed to send message. Please try again.')

      // Add error message to chat store
      const errorMessage: ChatMessage = {
        id: crypto.randomUUID(),
        content: 'Sorry, I encountered an error processing your message. Please try again.',
        role: 'assistant',
        timestamp: new Date(),
        agentId: activeAgent.id,
      }

      const errorUpdatedSession = {
        ...activeSession,
        messages: [...activeSession.messages, userMessage, errorMessage],
        updatedAt: new Date()
      }

      useChatStore.setState(state => ({
        activeSession: errorUpdatedSession,
        sessions: state.sessions.map(s =>
          s.id === activeSession.id ? errorUpdatedSession : s
        )
      }))

      setStreamingMessage(null)
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const formatTimestamp = (timestamp: Date) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }

  const removeAttachment = (fileId: string) => {
    setAttachedFiles(prev => prev.filter(f => f.id !== fileId))
  }

  const handleFileUploaded = (file: UploadedFile) => {
    setUploadedFiles(prev => [...prev, file])
    setAvailableFiles(prev => [...prev, file])
  }



  const handleAttachFromUpload = () => {
    setSelectedFiles(new Set())
    setShowFileModal(true)
  }

  const toggleFileSelection = (fileId: string) => {
    setSelectedFiles(prev => {
      const newSet = new Set(prev)
      if (newSet.has(fileId)) {
        newSet.delete(fileId)
      } else {
        newSet.add(fileId)
      }
      return newSet
    })
  }

  const attachSelectedFiles = () => {
    const filesToAttach = availableFiles.filter(file => selectedFiles.has(file.id))
    setAttachedFiles(prev => [...prev, ...filesToAttach])
    setSelectedFiles(new Set())
    setShowFileModal(false)
  }



  return (
    <div className={`flex flex-col h-full bg-white ${className}`}>
      {/* Chat Header */}
      <div className="border-b border-gray-200 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2">
              <Bot className="w-5 h-5 text-primary-600" />
              <h3 className="font-medium text-gray-900">
                {activeAgent?.name || 'Chat'}
              </h3>
            </div>
            {activeAgent && (
              <Badge variant="primary" size="sm">
                {activeAgent.model}
              </Badge>
            )}
          </div>
          
          {messages.length > 0 && (
            <div className="text-sm text-gray-500">
              {messages.length} message{messages.length !== 1 ? 's' : ''}
            </div>
          )}
        </div>
        
        {activeAgent?.description && (
          <p className="text-sm text-gray-600 mt-2">
            {activeAgent.description}
          </p>
        )}
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && !isLoading && (
          <div className="text-center py-12">
            <Bot className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Start a conversation
            </h3>
            <p className="text-gray-600">
              Ask {activeAgent?.name || 'the agent'} anything to get started.
            </p>
          </div>
        )}

        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex items-start space-x-3 ${message.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}
          >
            {/* Agent Avatar */}
            <AgentAvatar
              agentId={message.agentId}
              role={message.role}
              size="md"
              className="mt-1"
            />

            {/* Message Content */}
            <div
              className={`max-w-3xl rounded-lg px-4 py-3 ${
                message.role === 'user'
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 text-gray-900'
              }`}
            >
              <div className="whitespace-pre-wrap break-words">
                {message.content}
              </div>

              {message.attachments && message.attachments.length > 0 && (
                <div className="mt-2 space-y-1">
                  {message.attachments.map((file) => (
                    <div
                      key={file.id}
                      className="text-xs opacity-75 flex items-center space-x-1"
                    >
                      <Paperclip className="w-3 h-3" />
                      <span>{file.name}</span>
                    </div>
                  ))}
                </div>
              )}

              <div className={`text-xs mt-2 ${
                message.role === 'user' ? 'text-primary-200' : 'text-gray-500'
              }`}>
                {formatTimestamp(message.timestamp)}
                {message.metadata?.model && (
                  <span className="ml-2">• {message.metadata.model}</span>
                )}
              </div>
            </div>
          </div>
        ))}

        {/* Streaming Message */}
        {streamingMessage && (
          <div className="flex items-start space-x-3">
            <AgentAvatar
              agentId={streamingMessage.agentId}
              role="assistant"
              size="md"
              className="mt-1"
            />
            <div className="max-w-3xl rounded-lg px-4 py-3 bg-gray-100 text-gray-900">
              <div className="whitespace-pre-wrap break-words">
                {streamingMessage.content}
                <span className="inline-block w-2 h-4 bg-gray-400 ml-1 animate-pulse" />
              </div>
              <div className="text-xs mt-2 text-gray-500">
                {formatTimestamp(streamingMessage.timestamp)} • Working...
              </div>
            </div>
          </div>
        )}

        {isLoading && !streamingMessage && (
          <div className="flex items-start space-x-3">
            <AgentAvatar
              agentId={activeAgent?.id}
              role="assistant"
              size="md"
              className="mt-1"
            />
            <div className="bg-gray-100 rounded-lg px-4 py-3">
              <div className="flex items-center space-x-2">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span className="text-gray-600">Working...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Error Display */}
      {error && (
        <div className="border-t border-red-200 bg-red-50 p-3">
          <div className="flex items-center space-x-2 text-red-700">
            <AlertCircle className="w-4 h-4" />
            <span className="text-sm">{error}</span>
            <button
              onClick={() => setError(null)}
              className="ml-auto text-red-500 hover:text-red-700"
            >
              ×
            </button>
          </div>
        </div>
      )}

      {/* Attached Files */}
      {attachedFiles.length > 0 && (
        <div className="border-t border-gray-200 p-3">
          <div className="flex flex-wrap gap-2">
            {attachedFiles.map((file) => (
              <div
                key={file.id}
                className="flex items-center space-x-2 bg-gray-100 rounded-lg px-3 py-1"
              >
                <Paperclip className="w-3 h-3 text-gray-500" />
                <span className="text-sm text-gray-700">{file.name}</span>
                <button
                  onClick={() => removeAttachment(file.id)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Input Area */}
      <div className="border-t border-gray-200 p-4">
        <div className="flex items-end space-x-3">
          <div className="flex-1">
            <textarea
              ref={textareaRef}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={`Message ${activeAgent?.name || 'agent'}...`}
              className="w-full resize-none border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              rows={1}
              style={{ maxHeight: '120px' }}
              disabled={isLoading}
            />
          </div>
          
          <div className="flex space-x-2">
            <Button
              variant="outline"
              size="sm"
              icon={<Paperclip className="w-4 h-4" />}
              disabled={isLoading}
              onClick={handleAttachFromUpload}
            >
              Attach
            </Button>
            
            <Button
              onClick={sendMessage}
              disabled={!inputValue.trim() || isLoading}
              loading={isLoading}
              icon={<Send className="w-4 h-4" />}
            >
              Send
            </Button>
          </div>
        </div>
      </div>

      {/* File Attachment Modal */}
      {showFileModal && (
        <Modal
          isOpen={showFileModal}
          onClose={() => setShowFileModal(false)}
          title="Attach Files"
          size="lg"
        >
          <div className="space-y-6">
            {/* Upload New Files */}
            <div>
              <h4 className="font-medium text-gray-900 mb-3">Upload New Files</h4>
              <FileUpload
                onFileUploaded={handleFileUploaded}
                className="border-dashed border-2 border-gray-300"
              />
            </div>

            {/* Select from Uploaded Files */}
            {availableFiles.length > 0 && (
              <div>
                <h4 className="font-medium text-gray-900 mb-3">
                  Select from Uploaded Files ({availableFiles.length})
                </h4>
                <div className="max-h-64 overflow-y-auto space-y-2">
                  {availableFiles.map((file) => (
                    <div
                      key={file.id}
                      className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                        selectedFiles.has(file.id)
                          ? 'border-primary-500 bg-primary-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                      onClick={() => toggleFileSelection(file.id)}
                    >
                      <div className="flex items-center space-x-3">
                        <input
                          type="checkbox"
                          checked={selectedFiles.has(file.id)}
                          onChange={() => toggleFileSelection(file.id)}
                          className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                        />
                        <div className="flex-1">
                          <div className="flex items-center space-x-2">
                            <FileText className="w-4 h-4 text-gray-400" />
                            <span className="text-sm font-medium text-gray-900">{file.name}</span>
                            <span className="text-xs text-gray-500">
                              ({(file.size / 1024).toFixed(1)} KB)
                            </span>
                          </div>
                          <div className="text-xs text-gray-500 mt-1">
                            {file.status === 'processed' && file.processedData?.rows && (
                              <span>{file.processedData.rows} rows</span>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="mt-4 flex justify-end space-x-2">
                  <Button
                    variant="outline"
                    onClick={() => setShowFileModal(false)}
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={attachSelectedFiles}
                    disabled={selectedFiles.size === 0}
                  >
                    Attach Selected ({selectedFiles.size})
                  </Button>
                </div>
              </div>
            )}

            {availableFiles.length === 0 && uploadedFiles.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                <Paperclip className="w-8 h-8 mx-auto mb-2" />
                <p>No files available. Upload files to attach them to your messages.</p>
              </div>
            )}
          </div>
        </Modal>
      )}
    </div>
  )
}
