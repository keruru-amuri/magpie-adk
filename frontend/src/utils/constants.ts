// API Configuration
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

// File Upload Configuration
export const FILE_UPLOAD_CONFIG = {
  maxFileSize: 10 * 1024 * 1024, // 10MB
  supportedTypes: {
    'text/csv': ['.csv'],
    'application/json': ['.json'],
    'text/plain': ['.txt'],
    'image/*': ['.png', '.jpg', '.jpeg', '.gif']
  },
  csvWorkaroundEnabled: true
} as const

// Agent Configuration
export const AGENT_CONFIG = {
  defaultAgent: 'master_coordinator',
  switchTimeout: 30000, // 30 seconds
  heartbeatInterval: 60000, // 1 minute
} as const

// Chat Configuration
export const CHAT_CONFIG = {
  maxMessageLength: 10000,
  messageHistoryLimit: 100,
  typingIndicatorTimeout: 3000,
  autoSaveInterval: 30000, // 30 seconds
} as const

// UI Configuration
export const UI_CONFIG = {
  animationDuration: 200,
  debounceDelay: 300,
  toastDuration: 5000,
  modalZIndex: 1000,
} as const

// Status Colors
export const STATUS_COLORS = {
  active: 'bg-green-500',
  available: 'bg-blue-500',
  busy: 'bg-yellow-500',
  offline: 'bg-gray-400',
  error: 'bg-red-500',
  success: 'bg-green-500',
  warning: 'bg-yellow-500',
  info: 'bg-blue-500',
} as const

// File Type Icons Mapping
export const FILE_TYPE_ICONS = {
  'text/csv': 'FileText',
  'application/json': 'FileText',
  'text/plain': 'FileText',
  'image/png': 'Image',
  'image/jpeg': 'Image',
  'image/jpg': 'Image',
  'image/gif': 'Image',
} as const

// Agent Icons Mapping
export const AGENT_ICONS = {
  master_coordinator: 'Settings',
  engineering_process_procedure_agent: 'Zap',
  data_scientist_agent: 'Database',
  general_chat_agent: 'MessageCircle',
  csv_cleaning_agent: 'FileText',
} as const

// API Endpoints (Google ADK)
export const API_ENDPOINTS = {
  // ADK endpoints
  listApps: '/list-apps',
  run: '/run',
  runSSE: '/run_sse',

  // Legacy endpoints (for compatibility)
  agents: '/list-apps',
  agentSwitch: '/run',
  agentCurrent: '/list-apps',
  agentCapabilities: '/list-apps',

  // File endpoints (not implemented in ADK)
  fileUpload: '/api/files/upload',
  fileUploadCSV: '/api/files/upload-csv',
  fileHistory: '/api/files',
  fileDelete: (fileId: string) => `/api/files/${fileId}`,

  // Chat endpoints (ADK)
  chatMessage: '/run',
  chatHistory: '/run',
  chatSession: '/run',

  // System endpoints (not implemented in ADK)
  systemStatus: '/api/system/status',
  systemInfo: '/api/system/info',
} as const

// Error Messages
export const ERROR_MESSAGES = {
  networkError: 'Network error. Please check your connection.',
  serverError: 'Server error. Please try again later.',
  fileUploadError: 'Failed to upload file. Please try again.',
  agentSwitchError: 'Failed to switch agent. Please try again.',
  chatError: 'Failed to send message. Please try again.',
  fileSizeError: 'File size exceeds the maximum limit.',
  fileTypeError: 'File type not supported.',
  sessionExpired: 'Session expired. Please refresh the page.',
} as const

// Success Messages
export const SUCCESS_MESSAGES = {
  fileUploaded: 'File uploaded successfully',
  agentSwitched: 'Agent switched successfully',
  messageSent: 'Message sent successfully',
  sessionCreated: 'New chat session created',
} as const

// Loading Messages
export const LOADING_MESSAGES = {
  uploadingFile: 'Uploading file...',
  switchingAgent: 'Switching agent...',
  sendingMessage: 'Sending message...',
  loadingAgents: 'Loading agents...',
  loadingHistory: 'Loading chat history...',
} as const

// Keyboard Shortcuts
export const KEYBOARD_SHORTCUTS = {
  sendMessage: 'Enter',
  newLine: 'Shift+Enter',
  focusInput: '/',
  clearChat: 'Ctrl+K',
  switchAgent: 'Ctrl+Shift+A',
} as const

// Local Storage Keys
export const STORAGE_KEYS = {
  activeAgent: 'magpie_active_agent',
  chatSessions: 'magpie_chat_sessions',
  userPreferences: 'magpie_user_preferences',
  uploadHistory: 'magpie_upload_history',
} as const

// Environment Variables
export const ENV = {
  isDevelopment: import.meta.env.DEV,
  isProduction: import.meta.env.PROD,
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL,
  appName: import.meta.env.VITE_APP_NAME || 'MAGPIE',
  appVersion: import.meta.env.VITE_APP_VERSION || '1.0.0',
  enableDebug: import.meta.env.VITE_ENABLE_DEBUG === 'true',
} as const
