// Agent Types
export interface Agent {
  id: string
  name: string
  description: string
  specialties: string[]
  capabilities: string[]
  status: 'active' | 'available' | 'busy' | 'offline'
  model?: string
  lastActive?: Date
}

export interface AgentCapability {
  name: string
  description: string
  category: string
  examples: string[]
}

// File Upload Types
export interface UploadedFile {
  id: string
  name: string
  size: number
  type: string
  content?: string // For CSV files (workaround)
  uploadedAt: Date
  status: 'uploading' | 'uploaded' | 'processing' | 'processed' | 'error'
  processedData?: any
  errorMessage?: string
}

export interface FileUploadProgress {
  fileId: string
  progress: number
  stage: 'reading' | 'uploading' | 'processing' | 'complete'
}

// Chat Types
export interface ChatMessage {
  id: string
  content: string
  role: 'user' | 'assistant' | 'system'
  timestamp: Date
  agentId?: string
  attachments?: UploadedFile[]
  metadata?: {
    processingTime?: number
    model?: string
    tokens?: number
  }
}

export interface ChatSession {
  id: string
  title: string
  messages: ChatMessage[]
  agentId: string
  createdAt: Date
  updatedAt: Date
}

// API Types
export interface APIResponse<T = any> {
  success: boolean
  data?: T
  error?: string
  message?: string
}

export interface ChatMessageResponse extends APIResponse<ChatMessage> {
  allMessages?: ChatMessage[]
}

export interface SystemStatus {
  status: 'healthy' | 'degraded' | 'down'
  agents: {
    [agentId: string]: {
      status: Agent['status']
      lastHeartbeat: Date
      responseTime?: number
    }
  }
  services: {
    backend: 'online' | 'offline'
    database: 'online' | 'offline'
    mcp_servers: {
      [serverName: string]: 'online' | 'offline'
    }
  }
  uptime: number
}

// Store Types
export interface AgentStore {
  agents: Agent[]
  activeAgent: Agent | null // Always Master Coordinator for routing
  displayAgent: Agent | null // Agent shown in UI selector
  isLoading: boolean
  error: string | null

  // Actions
  setActiveAgent: (agent: Agent) => void
  setDisplayAgent: (agent: Agent) => void
  fetchAgents: () => Promise<void>
  switchAgent: (agentId: string) => Promise<void>
  getAgentCapabilities: (agentId: string) => Promise<AgentCapability[]>
}

export interface FileStore {
  files: UploadedFile[]
  uploadProgress: { [fileId: string]: FileUploadProgress }
  isUploading: boolean
  
  // Actions
  uploadFile: (file: File) => Promise<UploadedFile>
  uploadCSV: (file: File) => Promise<UploadedFile>
  removeFile: (fileId: string) => void
  getFileHistory: () => Promise<UploadedFile[]>
}

export interface ChatStore {
  sessions: ChatSession[]
  activeSession: ChatSession | null
  isLoading: boolean
  
  // Actions
  createSession: (agentId: string) => ChatSession
  sendMessage: (content: string, attachments?: UploadedFile[]) => Promise<void>
  loadSession: (sessionId: string) => Promise<void>
  deleteSession: (sessionId: string) => void
  setActiveSession: (session: ChatSession | null) => void
}

// Component Props Types
export interface AgentSelectorProps {
  className?: string
  onAgentChange?: (agent: Agent) => void
}

export interface FileUploadProps {
  className?: string
  maxFileSize?: number
  acceptedTypes?: string[]
  onFileUploaded?: (file: UploadedFile) => void
}

export interface ChatInterfaceProps {
  className?: string
  sessionId?: string
}

// Utility Types
export type LoadingState = 'idle' | 'loading' | 'success' | 'error'

export interface AsyncState<T> {
  data: T | null
  loading: boolean
  error: string | null
}

// Configuration Types
export interface AppConfig {
  apiBaseUrl: string
  maxFileSize: number
  supportedFileTypes: string[]
  defaultAgent: string
  features: {
    fileUpload: boolean
    csvWorkaround: boolean
    realTimeChat: boolean
    agentSwitching: boolean
  }
}
