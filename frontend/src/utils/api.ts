import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosResponse } from 'axios'
import { API_BASE_URL, API_ENDPOINTS, ERROR_MESSAGES } from './constants'
import type { APIResponse, Agent, UploadedFile, ChatMessage, ChatSession, SystemStatus, AgentCapability } from '@/types'

// Create axios instance with default configuration
const createApiClient = (): AxiosInstance => {
  const client = axios.create({
    baseURL: API_BASE_URL,
    timeout: 30000, // 30 seconds
    headers: {
      'Content-Type': 'application/json',
    },
    withCredentials: true, // Include cookies for session management
  })

  // Request interceptor
  client.interceptors.request.use(
    (config) => {
      // Add timestamp to prevent caching
      if (config.method === 'get') {
        config.params = { ...config.params, _t: Date.now() }
      }
      
      // Add X-Requested-With header for CSRF protection
      config.headers['X-Requested-With'] = 'XMLHttpRequest'
      
      return config
    },
    (error) => {
      return Promise.reject(error)
    }
  )

  // Response interceptor
  client.interceptors.response.use(
    (response: AxiosResponse) => {
      return response
    },
    (error) => {
      // Handle common errors
      if (error.response?.status === 401) {
        // Handle authentication error
        console.error('Authentication required')
        // Could trigger a login flow here
      } else if (error.response?.status === 403) {
        // Handle authorization error
        console.error('Access forbidden')
      } else if (error.response?.status >= 500) {
        // Handle server errors
        console.error('Server error:', error.response?.data?.message || ERROR_MESSAGES.serverError)
      } else if (error.code === 'NETWORK_ERROR') {
        // Handle network errors
        console.error('Network error:', ERROR_MESSAGES.networkError)
      }
      
      return Promise.reject(error)
    }
  )

  return client
}

// Create the API client instance
const apiClient = createApiClient()

// Generic API request wrapper
async function apiRequest<T>(
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH',
  url: string,
  data?: any,
  config?: AxiosRequestConfig
): Promise<APIResponse<T>> {
  try {
    const response = await apiClient.request<APIResponse<T>>({
      method,
      url,
      data,
      ...config,
    })
    
    return response.data
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const errorMessage = error.response?.data?.error || error.response?.data?.message || error.message
      return {
        success: false,
        error: errorMessage,
      }
    }
    
    return {
      success: false,
      error: 'An unexpected error occurred',
    }
  }
}

// Agent API functions (Google ADK)
export const agentApi = {
  // Get all available agents (using ADK list-apps)
  getAgents: async (): Promise<APIResponse<Agent[]>> => {
    try {
      const response = await apiRequest<string[]>('GET', API_ENDPOINTS.listApps)
      if (response.success && response.data) {
        // Convert app names to Agent objects
        const agents: Agent[] = response.data.map(appName => ({
          id: appName,
          name: appName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
          description: `${appName} agent`,
          specialties: [], // Add required specialties field
          capabilities: [],
          model: 'gpt-4.1', // Default model
          status: 'available' as const
        }))
        return { success: true, data: agents }
      }
      return {
        success: false,
        error: response.error || 'Failed to get agents'
      }
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to get agents'
      }
    }
  },

  // Get current active agent (mock implementation)
  getCurrentAgent: async (): Promise<APIResponse<Agent>> => {
    const agentsResponse = await agentApi.getAgents()
    if (agentsResponse.success && agentsResponse.data && agentsResponse.data.length > 0) {
      const activeAgent = { ...agentsResponse.data[0], isActive: true }
      return { success: true, data: activeAgent }
    }
    return {
      success: false,
      error: 'No agents available'
    }
  },

  // Switch to a specific agent (enhanced implementation)
  switchAgent: async (agentId: string): Promise<APIResponse<Agent>> => {
    try {
      // First, get the list of available agents to validate the agentId
      const agentsResponse = await agentApi.getAgents()
      if (!agentsResponse.success || !agentsResponse.data) {
        return {
          success: false,
          error: 'Failed to get available agents'
        }
      }

      const agent = agentsResponse.data.find(a => a.id === agentId)
      if (!agent) {
        return {
          success: false,
          error: `Agent with ID ${agentId} not found`
        }
      }

      // For ADK, agent switching is handled by the master coordinator
      // We don't need to make a separate API call - the agent transfer happens
      // automatically during message processing based on the request content
      // For now, we'll just return success to update the UI state

      return {
        success: true,
        data: { ...agent, status: 'active' }
      }
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to switch agent'
      }
    }
  },

  // Get agent capabilities (mock implementation)
  getAgentCapabilities: async (_agentId: string): Promise<APIResponse<AgentCapability[]>> => {
    return {
      success: true,
      data: [
        { name: 'chat', description: 'Chat with users', category: 'communication', examples: [] },
        { name: 'analysis', description: 'Analyze data', category: 'data', examples: [] }
      ]
    }
  },
}

// File API functions (Enhanced for ADK integration)
export const fileApi = {
  // Standard file upload (simulated for ADK compatibility)
  uploadFile: async (file: File, onProgress?: (progress: number) => void): Promise<APIResponse<UploadedFile>> => {
    try {
      // Simulate upload progress
      onProgress?.(0)

      // Read file content for processing
      const arrayBuffer = await file.arrayBuffer()
      const base64Content = btoa(String.fromCharCode(...new Uint8Array(arrayBuffer)))

      onProgress?.(50)

      // Create uploaded file response
      const uploadedFile: UploadedFile = {
        id: crypto.randomUUID(),
        name: file.name,
        size: file.size,
        type: file.type,
        uploadedAt: new Date(),
        status: 'uploaded',
        content: base64Content,
        processedData: {
          id: crypto.randomUUID(),
          filename: file.name,
          size: file.size,
          type: file.type,
          uploaded_at: new Date().toISOString(),
          status: 'ready'
        }
      }

      // Simulate upload delay
      await new Promise(resolve => setTimeout(resolve, 500))
      onProgress?.(100)

      return { success: true, data: uploadedFile }
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to upload file'
      }
    }
  },

  // CSV file upload with content reading workaround (ADK compatible)
  uploadCSV: async (
    file: File,
    content: string,
    onProgress?: (progress: number) => void
  ): Promise<APIResponse<UploadedFile>> => {
    try {
      onProgress?.(0)

      // Process CSV content - basic validation
      const lines = content.split('\n').filter(line => line.trim())
      if (lines.length === 0) {
        throw new Error('CSV file appears to be empty')
      }

      onProgress?.(50)

      // Create processed CSV file
      const uploadedFile: UploadedFile = {
        id: crypto.randomUUID(),
        name: file.name,
        size: file.size,
        type: file.type,
        uploadedAt: new Date(),
        status: 'processed',
        content: content,
        processedData: {
          id: crypto.randomUUID(),
          filename: file.name,
          size: file.size,
          type: file.type,
          uploaded_at: new Date().toISOString(),
          status: 'processed',
          rows: lines.length,
          headers: lines[0] ? lines[0].split(',').map(h => h.trim()) : [],
          preview: lines.slice(0, 5) // First 5 rows for preview
        }
      }

      // Simulate processing delay
      await new Promise(resolve => setTimeout(resolve, 1000))
      onProgress?.(100)

      return { success: true, data: uploadedFile }
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to upload CSV'
      }
    }
  },

  // Get file upload history (mock implementation)
  getFileHistory: async (): Promise<APIResponse<UploadedFile[]>> => {
    // For now, return empty array since we don't have persistent storage
    return {
      success: true,
      data: []
    }
  },

  // Delete a file (mock implementation)
  deleteFile: async (_fileId: string): Promise<APIResponse<void>> => {
    // For now, just return success
    return {
      success: true,
      data: undefined
    }
  },
}

// Memory API functions (MAGPIE Memory System)
export const memoryApi = {
  // Session management
  createSession: async (
    appName: string,
    userId: string,
    agentId: string,
    sessionId?: string,
    title?: string,
    initialState?: Record<string, any>,
    metadata?: Record<string, any>
  ): Promise<APIResponse<any>> => {
    try {
      const response = await apiClient.post('/api/memory/sessions', {
        app_name: appName,
        user_id: userId,
        agent_id: agentId,
        session_id: sessionId,
        title,
        initial_state: initialState,
        metadata
      })
      return response.data
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to create session'
      }
    }
  },

  getSession: async (
    appName: string,
    userId: string,
    sessionId: string,
    includeMessages: boolean = true,
    includeState: boolean = true
  ): Promise<APIResponse<any>> => {
    try {
      const response = await apiClient.get(
        `/api/memory/sessions/${appName}/${userId}/${sessionId}`,
        {
          params: {
            include_messages: includeMessages,
            include_state: includeState
          }
        }
      )
      return response.data
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to get session'
      }
    }
  },

  listSessions: async (
    appName: string,
    userId: string,
    activeOnly: boolean = false,
    limit: number = 50,
    offset: number = 0
  ): Promise<APIResponse<any[]>> => {
    try {
      const response = await apiClient.get(
        `/api/memory/sessions/${appName}/${userId}`,
        {
          params: {
            active_only: activeOnly,
            limit,
            offset
          }
        }
      )
      return response.data
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to list sessions'
      }
    }
  },

  updateSession: async (
    appName: string,
    userId: string,
    sessionId: string,
    updates: {
      title?: string
      agent_id?: string
      is_active?: boolean
      metadata?: Record<string, any>
    }
  ): Promise<APIResponse<any>> => {
    try {
      const response = await apiClient.put(
        `/api/memory/sessions/${appName}/${userId}/${sessionId}`,
        updates
      )
      return response.data
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to update session'
      }
    }
  },

  deleteSession: async (
    appName: string,
    userId: string,
    sessionId: string
  ): Promise<APIResponse<any>> => {
    try {
      const response = await apiClient.delete(
        `/api/memory/sessions/${appName}/${userId}/${sessionId}`
      )
      return response.data
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to delete session'
      }
    }
  },

  // Message management
  addMessage: async (
    sessionId: string,
    role: string,
    content: string,
    agentId?: string,
    metadata?: Record<string, any>
  ): Promise<APIResponse<any>> => {
    try {
      const response = await apiClient.post(
        `/api/memory/sessions/${sessionId}/messages`,
        {
          role,
          content,
          agent_id: agentId,
          metadata
        }
      )
      return response.data
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to add message'
      }
    }
  },

  // Session state management
  getSessionState: async (sessionId: string): Promise<APIResponse<any>> => {
    try {
      const response = await apiClient.get(`/api/memory/sessions/${sessionId}/state`)
      return response.data
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to get session state'
      }
    }
  },

  updateSessionState: async (
    sessionId: string,
    stateUpdates: Record<string, any>
  ): Promise<APIResponse<any>> => {
    try {
      const response = await apiClient.put(
        `/api/memory/sessions/${sessionId}/state`,
        { state_updates: stateUpdates }
      )
      return response.data
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to update session state'
      }
    }
  },

  // Memory management
  searchMemory: async (
    agentId: string,
    query: string,
    userId?: string,
    memoryTypes?: string[],
    limit: number = 10
  ): Promise<APIResponse<any[]>> => {
    try {
      const response = await apiClient.post('/api/memory/memories/search', {
        agent_id: agentId,
        query,
        user_id: userId,
        memory_types: memoryTypes,
        limit
      })
      return response.data
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to search memory'
      }
    }
  },

  extractSessionMemory: async (
    sessionId: string,
    memoryType: string = 'conversation_summary'
  ): Promise<APIResponse<any>> => {
    try {
      const response = await apiClient.post(
        `/api/memory/sessions/${sessionId}/extract-memory`,
        { memory_type: memoryType }
      )
      return response.data
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to extract session memory'
      }
    }
  }
}

// Session management for consistent ADK sessions
let currentSession: { appName: string; userId: string; sessionId: string } | null = null

// Chat API functions (Google ADK)
export const chatApi = {
  // Clear current session (useful when switching agents)
  clearSession: () => {
    console.log('🧹 Clearing current ADK session')
    currentSession = null
  },
  // Initialize or get existing session
  getOrCreateSession: async (agentId: string): Promise<{ appName: string; userId: string; sessionId: string }> => {
    const appName = agentId || 'master_coordinator'

    // If we have a current session for the same agent, reuse it
    if (currentSession && currentSession.appName === appName) {
      return currentSession
    }

    // Create new session
    const userId = 'user_magpie'  // Use consistent user ID
    const sessionId = `session_${appName}_${Date.now()}`

    try {
      const sessionEndpoint = `/apps/${appName}/users/${userId}/sessions/${sessionId}`
      const sessionResponse = await apiClient.post(sessionEndpoint, { state: {} })

      if (sessionResponse.status !== 200) {
        throw new Error('Failed to create session: HTTP ' + sessionResponse.status)
      }

      // Store current session for reuse
      currentSession = { appName, userId, sessionId }
      console.log('✅ Created/reusing ADK session:', currentSession)

      return currentSession
    } catch (error) {
      console.error('❌ Failed to create ADK session:', error)
      throw error
    }
  },

  // Detect which agent actually responded based on response content
  detectRespondingAgent: (responseContent: string, initialAgent: string): string => {
    console.log(`🔍 Detecting agent from response:`, {
      initialAgent,
      contentPreview: responseContent.substring(0, 100) + '...'
    })

    // Agent detection patterns based on response content
    const agentPatterns = {
      'data_scientist_agent': [
        /databricks/i,
        /sql query/i,
        /data analysis/i,
        /business intelligence/i,
        /analytics/i,
        /dataset/i,
        /dataframe/i
      ],
      'engineering_process_procedure_agent': [
        /aircraft/i,
        /aviation/i,
        /maintenance/i,
        /mro/i,
        /engineering/i,
        /procedure/i,
        /regulatory/i,
        /faa/i,
        /easa/i,
        /troubleshooting/i
      ],
      'general_chat_agent': [
        /conversation/i,
        /chat/i,
        /general/i,
        /advice/i,
        /motivation/i
      ]
    }

    // Check for explicit transfer messages and agent identification
    const transferPatterns = [
      /transferring to (\w+)/i,
      /transfer.*to.*(\w+_agent)/i,
      /connected to the (\w+\s*\w*\s*\w*)\s*agent/i,
      /you are now connected to the (\w+\s*\w*\s*\w*)\s*agent/i,
      /(\w+\s*\w*\s*\w*)\s*agent.*assist you/i
    ]

    for (const pattern of transferPatterns) {
      const match = responseContent.match(pattern)
      if (match) {
        const targetAgent = match[1].toLowerCase().replace(/\s+/g, '_')
        console.log(`🔍 Transfer pattern matched: "${match[0]}" → agent: "${targetAgent}"`)

        if (targetAgent.includes('data') || targetAgent.includes('scientist')) {
          console.log(`🔄 Detected transfer to data_scientist_agent`)
          return 'data_scientist_agent'
        }
        if (targetAgent.includes('engineering') || targetAgent.includes('process')) {
          console.log(`🔄 Detected transfer to engineering_process_procedure_agent`)
          return 'engineering_process_procedure_agent'
        }
        if (targetAgent.includes('general') || targetAgent.includes('chat')) {
          console.log(`🔄 Detected transfer to general_chat_agent`)
          return 'general_chat_agent'
        }
      }
    }

    // Score each agent based on content patterns
    const scores = Object.entries(agentPatterns).map(([agentId, patterns]) => {
      const score = patterns.reduce((total, pattern) => {
        return total + (pattern.test(responseContent) ? 1 : 0)
      }, 0)
      return { agentId, score }
    })

    // Find the agent with the highest score
    const bestMatch = scores.reduce((best, current) =>
      current.score > best.score ? current : best
    )

    // Only change agent if we have a confident match (score > 0)
    // and it's different from the initial agent
    if (bestMatch.score > 0 && bestMatch.agentId !== initialAgent) {
      console.log(`🔄 Detected agent transfer: ${initialAgent} → ${bestMatch.agentId} (score: ${bestMatch.score})`)
      return bestMatch.agentId
    }

    // Default to initial agent if no clear transfer detected
    console.log(`🔄 No agent transfer detected, staying with: ${initialAgent}`)
    return initialAgent
  },

  // Send a message using ADK format
  sendMessage: async (
    content: string,
    agentId?: string,
    attachments?: UploadedFile[]
  ): Promise<APIResponse<ChatMessage>> => {
    try {
      // Get or create consistent session
      const { appName, userId, sessionId } = await chatApi.getOrCreateSession(agentId || 'master_coordinator')

      // Step 2: Prepare message content with file attachments
      let enhancedContent = content

      if (attachments && attachments.length > 0) {
        const fileContents: string[] = []

        for (const file of attachments) {
          if (file.content) {
            // Include file content in the message
            let fileSection = `\n\n--- Attached File: ${file.name} ---`
            fileSection += `\nFile Type: ${file.type}`
            fileSection += `\nFile Size: ${file.size} bytes`

            if (file.type === 'text/csv' || file.name.endsWith('.csv')) {
              fileSection += `\nRows: ${file.processedData?.rows || 'Unknown'}`
              fileSection += `\nHeaders: ${file.processedData?.headers?.join(', ') || 'Unknown'}`
              fileSection += `\n\nCSV Content:\n${file.content}`
            } else if (file.type === 'application/json' || file.name.endsWith('.json')) {
              fileSection += `\n\nJSON Content:\n${file.content}`
            } else if (file.type === 'text/plain' || file.name.endsWith('.txt')) {
              fileSection += `\n\nText Content:\n${file.content}`
            } else {
              fileSection += `\n\nFile Content:\n${file.content}`
            }

            fileSection += `\n--- End of ${file.name} ---\n`
            fileContents.push(fileSection)
          }
        }

        if (fileContents.length > 0) {
          enhancedContent += fileContents.join('\n')
        }
      }

      // Step 3: Send message to the session (using consistent session)
      const adkRequest = {
        appName,
        userId,
        sessionId,
        newMessage: {
          role: 'user',
          parts: [{ text: enhancedContent }]
        }
      }

      console.log('📤 Sending message to ADK session:', { appName, userId, sessionId, content: content.substring(0, 50) + '...' })
      const response = await apiClient.post(API_ENDPOINTS.run, adkRequest)

      if (response.status === 200 && response.data) {
        const responseContent = extractResponseContent(response.data)

        // Separate agent responses if this is a transfer scenario
        const separatedResponses = separateAgentResponses(responseContent)

        if (separatedResponses.length > 1) {
          // Multiple agents responded - create separate messages
          const chatMessages: ChatMessage[] = separatedResponses.map(resp => ({
            id: crypto.randomUUID(),
            content: resp.content,
            role: 'assistant',
            timestamp: new Date(),
            agentId: resp.agentId,
            attachments: attachments ? [] : undefined
          }))

          // Return the last message as primary, but include all messages
          return {
            success: true,
            data: chatMessages[chatMessages.length - 1],
            allMessages: chatMessages
          }
        } else {
          // Single agent response
          const agentResponse = separatedResponses[0]
          const chatMessage: ChatMessage = {
            id: crypto.randomUUID(),
            content: agentResponse.content,
            role: 'assistant',
            timestamp: new Date(),
            agentId: agentResponse.agentId,
            attachments: attachments ? [] : undefined
          }
          return { success: true, data: chatMessage }
        }
      }

      throw new Error('Failed to send message: HTTP ' + response.status)
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to send message'
      }
    }
  },

  // Send a message with streaming response using SSE
  sendMessageStreaming: async (
    content: string,
    agentId?: string,
    attachments?: UploadedFile[],
    onChunk?: (chunk: string) => void,
    onComplete?: (fullMessage: ChatMessage) => void,
    onError?: (error: string) => void
  ): Promise<void> => {
    try {
      // Get or create consistent session
      const { appName, userId, sessionId } = await chatApi.getOrCreateSession(agentId || 'master_coordinator')

      // Step 2: Prepare message content with file attachments
      let enhancedContent = content

      if (attachments && attachments.length > 0) {
        const fileContents: string[] = []

        for (const file of attachments) {
          if (file.content) {
            // Include file content in the message
            let fileSection = `\n\n--- Attached File: ${file.name} ---`
            fileSection += `\nFile Type: ${file.type}`
            fileSection += `\nFile Size: ${file.size} bytes`

            if (file.type === 'text/csv' || file.name.endsWith('.csv')) {
              fileSection += `\nRows: ${file.processedData?.rows || 'Unknown'}`
              fileSection += `\nHeaders: ${file.processedData?.headers?.join(', ') || 'Unknown'}`
              fileSection += `\n\nCSV Content:\n${file.content}`
            } else if (file.type === 'application/json' || file.name.endsWith('.json')) {
              fileSection += `\n\nJSON Content:\n${file.content}`
            } else if (file.type === 'text/plain' || file.name.endsWith('.txt')) {
              fileSection += `\n\nText Content:\n${file.content}`
            } else {
              fileSection += `\n\nFile Content:\n${file.content}`
            }

            fileSection += `\n--- End of ${file.name} ---\n`
            fileContents.push(fileSection)
          }
        }

        if (fileContents.length > 0) {
          enhancedContent += fileContents.join('\n')
        }
      }

      // Step 3: Prepare ADK request
      const adkRequest = {
        appName,
        userId,
        sessionId,
        newMessage: {
          role: 'user',
          parts: [{ text: enhancedContent }]
        }
      }

      console.log('📤 Sending streaming message to ADK session:', { appName, userId, sessionId, content: content.substring(0, 50) + '...' })

      let fullContent = ''
      let messageId = crypto.randomUUID()

      // Step 4: Use fetch with streaming for ADK SSE endpoint
      const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.runSSE}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'text/event-stream',
          'Cache-Control': 'no-cache',
        },
        body: JSON.stringify(adkRequest),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const reader = response.body?.getReader()
      if (!reader) {
        throw new Error('No response body reader available')
      }

      const decoder = new TextDecoder()
      let buffer = ''

      try {
        while (true) {
          const { done, value } = await reader.read()

          if (done) break

          // Decode the chunk and add to buffer
          buffer += decoder.decode(value, { stream: true })

          // Process complete SSE events
          const lines = buffer.split('\n')
          buffer = lines.pop() || '' // Keep incomplete line in buffer

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const eventData = line.slice(6) // Remove 'data: ' prefix
                if (eventData.trim() === '[DONE]') {
                  // Stream completed - separate agent responses if this is a transfer scenario
                  const separatedResponses = separateAgentResponses(fullContent)

                  if (separatedResponses.length > 1) {
                    // Multiple agents responded - create separate messages
                    const chatMessages: ChatMessage[] = separatedResponses.map(resp => ({
                      id: crypto.randomUUID(),
                      content: resp.content,
                      role: 'assistant',
                      timestamp: new Date(),
                      agentId: resp.agentId
                    }))

                    console.log('📨 Created multiple messages for agent transfer:', chatMessages.map(m => ({ agentId: m.agentId, contentPreview: m.content.substring(0, 50) + '...' })))

                    // Call onComplete for each message
                    chatMessages.forEach(msg => onComplete?.(msg))
                    return
                  } else {
                    // Single agent response
                    const agentResponse = separatedResponses[0]
                    const chatMessage: ChatMessage = {
                      id: messageId,
                      content: agentResponse.content,
                      role: 'assistant',
                      timestamp: new Date(),
                      agentId: agentResponse.agentId
                    }
                    onComplete?.(chatMessage)
                    return
                  }
                }

                const data = JSON.parse(eventData)

                // Extract content from ADK streaming response with deduplication
                const chunkContent = extractResponseContent([data], fullContent)
                if (chunkContent && chunkContent !== 'Response received from agent' && chunkContent !== 'Error processing agent response') {
                  fullContent += chunkContent
                  onChunk?.(chunkContent)
                }
              } catch (parseError) {
                console.warn('Failed to parse SSE event:', parseError)
              }
            }
          }
        }

        // If we reach here without [DONE], complete with what we have
        if (fullContent) {
          // Separate agent responses if this is a transfer scenario
          const separatedResponses = separateAgentResponses(fullContent)

          if (separatedResponses.length > 1) {
            // Multiple agents responded - create separate messages
            const chatMessages: ChatMessage[] = separatedResponses.map(resp => ({
              id: crypto.randomUUID(),
              content: resp.content,
              role: 'assistant',
              timestamp: new Date(),
              agentId: resp.agentId
            }))

            // Call onComplete for each message
            chatMessages.forEach(msg => onComplete?.(msg))
          } else {
            // Single agent response
            const agentResponse = separatedResponses[0]
            const chatMessage: ChatMessage = {
              id: messageId,
              content: agentResponse.content,
              role: 'assistant',
              timestamp: new Date(),
              agentId: agentResponse.agentId
            }
            onComplete?.(chatMessage)
          }
        }

      } finally {
        reader.releaseLock()
      }

    } catch (error) {
      onError?.(error instanceof Error ? error.message : 'Failed to send streaming message')
    }
  },

  // Get chat history (mock implementation)
  getChatHistory: async (_sessionId?: string): Promise<APIResponse<ChatMessage[]>> => {
    return {
      success: true,
      data: []
    }
  },

  // Create a new chat session (mock implementation)
  createSession: async (agentId: string): Promise<APIResponse<ChatSession>> => {
    const session: ChatSession = {
      id: 'session_' + Date.now(),
      title: `Chat with ${agentId}`,
      messages: [],
      agentId,
      createdAt: new Date(),
      updatedAt: new Date()
    }
    return { success: true, data: session }
  },
}

// Helper function to separate agent responses from combined content
function separateAgentResponses(combinedContent: string): { agentId: string; content: string }[] {
  const responses: { agentId: string; content: string }[] = []

  // Look for transfer patterns that indicate agent switching
  const transferPatterns = [
    {
      pattern: /I'll transfer you to our Engineering Process Procedure Agent.*?(?:Databricks integration\.)/i,
      targetAgent: 'engineering_process_procedure_agent'
    },
    {
      pattern: /I'll transfer you to our Data Scientist Agent.*?(?:integration\.)/i,
      targetAgent: 'data_scientist_agent'
    },
    {
      pattern: /I'll transfer you to our General Chat Agent.*?(?:conversations\.)/i,
      targetAgent: 'general_chat_agent'
    }
  ]

  // Check if this is a transfer scenario
  let transferMatch = null
  let transferEndIndex = -1
  let targetAgent = ''

  for (const transferPattern of transferPatterns) {
    const match = combinedContent.match(transferPattern.pattern)
    if (match) {
      transferMatch = match
      targetAgent = transferPattern.targetAgent
      transferEndIndex = (match.index || 0) + match[0].length
      break
    }
  }

  if (transferMatch && transferEndIndex > 0) {
    // Split into transfer message and actual response
    const transferMessage = combinedContent.substring(0, transferEndIndex).trim()
    const actualResponse = combinedContent.substring(transferEndIndex).trim()

    console.log('🔄 Agent transfer detected:', {
      transferMessage: transferMessage.substring(0, 100) + '...',
      actualResponse: actualResponse.substring(0, 100) + '...',
      targetAgent
    })

    if (transferMessage) {
      responses.push({
        agentId: 'master_coordinator',
        content: transferMessage
      })
    }

    if (actualResponse) {
      responses.push({
        agentId: targetAgent,
        content: actualResponse
      })
    }
  } else {
    // No transfer detected, treat as single response
    const agentId = chatApi.detectRespondingAgent(combinedContent, 'master_coordinator')
    responses.push({
      agentId,
      content: combinedContent
    })
  }

  return responses
}

// Helper function to extract content from ADK response with deduplication
function extractResponseContent(adkResponse: any, previousContent: string = ''): string {
  try {
    // ADK returns an array of events, find the last event with model response
    if (Array.isArray(adkResponse)) {
      let extractedContent = ''

      // Look for the final agent response (usually the last item with text content)
      for (let i = adkResponse.length - 1; i >= 0; i--) {
        const event = adkResponse[i]

        // Skip function calls and function responses, look for final text responses
        if (event.content?.parts && Array.isArray(event.content.parts)) {
          for (const part of event.content.parts) {
            // Skip function calls and function responses
            if (part.functionCall || part.functionResponse) {
              continue
            }

            // Look for actual text content
            if (part.text && typeof part.text === 'string') {
              extractedContent = part.text
              console.log('✅ Extracted text content from ADK response:', extractedContent.substring(0, 100) + '...')
              break
            }
          }
        }

        // Also check for direct text content
        if (!extractedContent && event.content?.text && typeof event.content.text === 'string') {
          extractedContent = event.content.text
          console.log('✅ Extracted direct text content from ADK response:', extractedContent.substring(0, 100) + '...')
        }

        if (extractedContent) break
      }

      // If no text found in the standard way, try to extract from function responses
      // This handles cases where the agent's final response is in a function response
      if (!extractedContent) {
        for (let i = adkResponse.length - 1; i >= 0; i--) {
          const event = adkResponse[i]
          if (event.content?.parts && Array.isArray(event.content.parts)) {
            for (const part of event.content.parts) {
              if (part.functionResponse?.response?.result && typeof part.functionResponse.response.result === 'string') {
                extractedContent = part.functionResponse.response.result
                console.log('✅ Extracted text from function response:', extractedContent.substring(0, 100) + '...')
                break
              }
            }
          }
          if (extractedContent) break
        }
      }

      // Deduplication: Check if this content is already in previousContent
      if (extractedContent && previousContent) {
        // Handle JSON-wrapped content
        let cleanExtractedContent = extractedContent
        try {
          // Check if the extracted content is JSON-wrapped
          if (extractedContent.startsWith('{"result":')) {
            const parsed = JSON.parse(extractedContent)
            if (parsed.result && typeof parsed.result === 'string') {
              cleanExtractedContent = parsed.result
              console.log('🧹 Unwrapped JSON content:', cleanExtractedContent.substring(0, 100) + '...')
            }
          }
        } catch (e) {
          // Not JSON, use as-is
        }

        // If the extracted content is already contained in previous content, don't return it
        if (previousContent.includes(cleanExtractedContent) || previousContent.includes(extractedContent)) {
          console.log('🔄 Skipping duplicate content:', cleanExtractedContent.substring(0, 100) + '...')
          return ''
        }

        // If the previous content is contained in the new content, return only the new part
        if (cleanExtractedContent.includes(previousContent) || extractedContent.includes(previousContent)) {
          const newPart = cleanExtractedContent.replace(previousContent, '').trim()
          if (newPart) {
            console.log('✂️ Extracted new content part:', newPart.substring(0, 100) + '...')
            return newPart
          }
          return ''
        }

        // Return the clean content (unwrapped if it was JSON)
        return cleanExtractedContent
      }

      return extractedContent || ''
    }

    // Fallback: try to extract any text content
    if (typeof adkResponse === 'string') {
      return adkResponse
    }

    console.warn('Could not extract content from ADK response:', adkResponse)
    return 'Response received from agent'
  } catch (error) {
    console.error('Error extracting response content:', error)
    return 'Error processing agent response'
  }
}

// System API functions
export const systemApi = {
  // Get system status
  getStatus: async (): Promise<APIResponse<SystemStatus>> => {
    return apiRequest<SystemStatus>('GET', API_ENDPOINTS.systemStatus)
  },

  // Get system information
  getInfo: async (): Promise<APIResponse<any>> => {
    return apiRequest<any>('GET', API_ENDPOINTS.systemInfo)
  },
}

// Utility functions
export const apiUtils = {
  // Check if response is successful
  isSuccess: <T>(response: APIResponse<T>): response is APIResponse<T> & { success: true; data: T } => {
    return response.success && response.data !== undefined
  },

  // Extract error message from response
  getErrorMessage: (response: APIResponse<any>): string => {
    return response.error || 'An unknown error occurred'
  },

  // Retry a request with exponential backoff
  retryRequest: async <T>(
    requestFn: () => Promise<APIResponse<T>>,
    maxRetries: number = 3,
    baseDelay: number = 1000
  ): Promise<APIResponse<T>> => {
    let lastError: APIResponse<T>

    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        const result = await requestFn()
        if (result.success) {
          return result
        }
        lastError = result
      } catch (error) {
        lastError = {
          success: false,
          error: error instanceof Error ? error.message : 'Request failed',
        }
      }

      if (attempt < maxRetries) {
        const delay = baseDelay * Math.pow(2, attempt)
        await new Promise(resolve => setTimeout(resolve, delay))
      }
    }

    return lastError!
  },
}

// Export the configured axios instance for direct use if needed
export { apiClient }

// Export all API functions as a single object
export const api = {
  agent: agentApi,
  file: fileApi,
  chat: chatApi,
  system: systemApi,
  utils: apiUtils,
}
