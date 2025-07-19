# MAGPIE Multi-Agent Platform Frontend Specifications

## Table of Contents
1. [Technical Architecture Overview](#technical-architecture-overview)
2. [Agent Selection UX Component Specifications](#agent-selection-ux-component-specifications)
3. [File Upload Functionality Implementation](#file-upload-functionality-implementation)
4. [API Integration Specifications](#api-integration-specifications)
5. [Component Architecture and Development Guidelines](#component-architecture-and-development-guidelines)
6. [Development Workflow and Build Process](#development-workflow-and-build-process)
7. [Integration Requirements](#integration-requirements)

---

## Technical Architecture Overview

### Tech Stack
- **Runtime**: Node.js 22 LTS
- **Framework**: React 18.2.0 with TypeScript 5.3+
- **Build Tool**: Vite 5.0+ (optimized for Node.js 22)
- **Styling**: Tailwind CSS 3.4+ with custom MAGPIE brand colors
- **State Management**: Zustand 4.4+ for global state, React Query 5.0+ for server state
- **File Upload**: React Dropzone 14.0+
- **HTTP Client**: Axios 1.6+ with interceptors
- **Real-time**: Socket.io-client 4.7+ (future implementation)
- **Icons**: Lucide React 0.525+

### Project Structure
```
frontend/
├── public/
│   ├── vite.svg
│   └── avatars/                      # Agent avatar images (optional)
├── src/
│   ├── components/
│   │   ├── agents/
│   │   │   ├── AgentSelector.tsx
│   │   │   ├── AgentCard.tsx
│   │   │   └── AgentCapabilities.tsx
│   │   ├── upload/
│   │   │   ├── FileUpload.tsx
│   │   │   ├── FileList.tsx
│   │   │   └── UploadProgress.tsx
│   │   ├── ui/
│   │   │   ├── Button.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Badge.tsx
│   │   │   ├── Modal.tsx
│   │   │   └── AgentAvatar.tsx       # Agent avatar component
│   │   ├── Layout.tsx
│   │   └── ChatInterface.tsx
│   ├── hooks/
│   │   ├── useFileUpload.ts
│   │   ├── useChat.ts
│   │   └── useApi.ts
│   ├── stores/
│   │   ├── agentStore.tsx            # Includes useAgent functionality
│   │   ├── fileStore.ts
│   │   ├── chatStore.ts
│   │   └── enhancedChatStore.ts      # Backend sync capabilities
│   ├── types/
│   │   └── index.ts
│   ├── utils/
│   │   ├── api.ts
│   │   ├── fileUtils.ts
│   │   └── constants.ts
│   ├── App.tsx
│   ├── main.tsx
│   ├── index.css
│   └── vite-env.d.ts
├── package.json
├── vite.config.ts
├── tailwind.config.js
├── tsconfig.json
├── frontend_specifications.md
├── IMPLEMENTATION_STATUS.md
└── README.md
```

### Integration with MAGPIE Backend
- **Backend URL**: `http://localhost:8000` (Google ADK server)
- **Proxy Configuration**: Vite dev server proxies `/api/*` to backend
- **Communication**: RESTful API with JSON payloads
- **File Handling**: Special CSV workaround for ADK limitations
- **Authentication**: Session-based (handled by ADK)

### State Management Architecture
```typescript
// Global State (Zustand)
- agentStore: Dual agent system (activeAgent for routing, displayAgent for UI),
  available agents, switching logic, includes useAgent hook functionality
- fileStore: Uploaded files, upload progress, file history
- chatStore: Chat sessions, messages, real-time updates
- enhancedChatStore: Backend sync capabilities, persistent storage integration

// Server State (React Query)
- Agent data fetching and caching
- File upload mutations
- Chat message queries
- System status polling

// Dual Agent System Architecture
- activeAgent: Always Master Coordinator for backend routing
- displayAgent: User-selected specialist agent for UI display
- All messages route through Master Coordinator → Specialist Agent → User
```

---

## Agent Selection UX Component Specifications

### Visual Design Requirements

#### Agent Selector Interface
- **Location**: Top-right corner of the header
- **Default State**: Shows current active agent with status indicator
- **Interaction**: Click to open dropdown with all available agents
- **Dimensions**: Minimum 280px width for dropdown, auto height

#### Agent Display Format
```typescript
interface AgentDisplayProps {
  agent: {
    id: string
    name: string
    description: string
    specialties: string[]
    capabilities: string[]
    status: 'active' | 'available' | 'busy' | 'offline'
    model: string
    lastActive?: Date
  }
}
```

#### Status Indicators
- **Active**: Green dot (bg-green-500) - Currently selected agent
- **Available**: Blue dot (bg-blue-500) - Ready to handle requests
- **Busy**: Yellow dot (bg-yellow-500) - Processing requests
- **Offline**: Gray dot (bg-gray-400) - Not available

#### Agent Icons Mapping
```typescript
const agentIcons = {
  master_coordinator: Settings,        // Hidden from UI
  engineering_process_procedure_agent: Zap,
  data_scientist_agent: Database,
  general_chat_agent: MessageCircle,
  csv_cleaning_agent: FileText
}
```

#### Agent Avatar System
```typescript
interface AgentAvatarProps {
  agentId: string
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

// Avatar priority: Custom PNG > Lucide Icon > Fallback
// Custom avatars stored in /public/avatars/{agentId}.png
// Automatic fallback to Lucide React icons
// Color-coded by agent type for visual distinction
```

### MAGPIE Agents Configuration
1. **Master Coordinator** *(Hidden from UI - Backend routing only)*
   - Model: azure/o4-mini
   - Specialties: routing, coordination, delegation, system_management
   - Description: "Intelligent request routing and coordination across all specialized agents"
   - UI Display: Filtered out of user-facing agent selector

2. **Engineering Process Agent**
   - Model: DeepSeek-R1-0528
   - Specialties: aviation maintenance, aircraft MRO, regulatory compliance
   - Description: "Aviation MRO and engineering procedures with automatic query enhancement"
   - Avatar: Zap icon (orange theme)

3. **Data Scientist Agent**
   - Model: azure/o3-mini
   - Specialties: data analysis, SQL queries, business intelligence
   - Description: "Data analysis and business intelligence using Databricks integration"
   - Avatar: Database icon (blue theme)

4. **General Chat Agent**
   - Model: gpt-4.1-mini
   - Specialties: conversation, general help, advice, motivation
   - Description: "General conversation and assistance for casual interactions"
   - Avatar: MessageCircle icon (green theme)

5. **CSV Cleaning Agent** *(Optional - may not be implemented)*
   - Model: gpt-4.1-mini
   - Specialties: csv cleaning, data standardization, file processing
   - Description: "Specialized tool for cleaning and standardizing CSV files"

### Agent Switching Workflow
1. User clicks current agent display (shows displayAgent)
2. Dropdown opens showing only user-facing agents (Master Coordinator filtered out)
3. User selects new specialist agent
4. Loading state shows during switch
5. Frontend updates displayAgent for UI, keeps activeAgent as Master Coordinator
6. All messages route: User → Master Coordinator → Selected Specialist → User
7. Chat messages show specialist agent avatars for clear identification
8. Success: Update UI and close dropdown
9. Error: Show error message, revert to previous agent

### Dual Agent System Implementation
- **Backend Routing**: All messages go through Master Coordinator (activeAgent)
- **UI Display**: User sees and selects specialist agents (displayAgent)
- **Message Flow**: Master Coordinator intelligently routes to appropriate specialist
- **Visual Feedback**: Agent avatars show which specialist is responding
- **Session Management**: Each agent switch creates new session context

### Responsive Design Requirements
- **Desktop (≥1024px)**: Full agent cards with descriptions, collapsible sidebar
- **Tablet (768px-1023px)**: Compact cards with truncated descriptions, collapsible sidebar
- **Mobile (≤767px)**: Minimal cards with names only, overlay sidebar menu

### Sidebar Functionality
- **Collapsible Design**: Toggle between full (320px) and collapsed (64px) widths
- **Mobile Responsive**: Overlay menu for mobile devices with backdrop dismiss
- **Navigation Sections**: Chat history, agent status, system info, quick actions
- **Session Management**: "New Chat Session" button with active agent integration
- **Smooth Animations**: CSS transitions for collapse/expand and mobile menu slide-in

---

## File Upload Functionality Implementation

### React Dropzone Configuration
```typescript
const dropzoneConfig = {
  accept: {
    'text/csv': ['.csv'],
    'application/json': ['.json'],
    'text/plain': ['.txt'],
    'image/*': ['.png', '.jpg', '.jpeg', '.gif']
  },
  maxSize: 10 * 1024 * 1024, // 10MB
  multiple: true,
  onDrop: handleFileUpload
}
```

### CSV File Upload Workaround
**Problem**: Google ADK has limitations with CSV file uploads
**Solution**: Read CSV content in frontend before sending to backend

```typescript
const handleCSVUpload = async (file: File) => {
  // Step 1: Read file content in frontend
  const content = await file.text()
  
  // Step 2: Send processed data to backend
  const response = await axios.post('/api/files/upload-csv', {
    filename: file.name,
    content: content,
    size: file.size,
    type: file.type
  })
  
  // Step 3: Handle response and update UI
  return response.data
}
```

### File Type Support Matrix
| File Type | Extension | Max Size | Processing Method | Backend Endpoint |
|-----------|-----------|----------|-------------------|------------------|
| CSV | .csv | 10MB | Content reading | `/api/files/upload-csv` |
| JSON | .json | 10MB | Standard upload | `/api/files/upload` |
| Text | .txt | 10MB | Standard upload | `/api/files/upload` |
| Images | .png,.jpg,.jpeg,.gif | 10MB | Standard upload | `/api/files/upload` |

### Upload Progress Implementation
```typescript
interface UploadProgress {
  fileId: string
  progress: number // 0-100
  stage: 'reading' | 'uploading' | 'processing' | 'complete'
  error?: string
}

// Progress tracking for CSV files
const trackCSVProgress = (fileId: string) => {
  setProgress(fileId, 25, 'reading')    // File reading
  setProgress(fileId, 50, 'uploading')  // Sending to backend
  setProgress(fileId, 75, 'processing') // Backend processing
  setProgress(fileId, 100, 'complete')  // Finished
}
```

### Error Handling Strategy
- **File too large**: Show size limit message
- **Invalid file type**: List supported formats
- **Network error**: Retry mechanism with exponential backoff
- **Backend error**: Display server error message
- **CSV parsing error**: Show specific CSV format requirements

### Integration with Artifact Service
- Files are stored using ADK's artifact service
- File metadata tracked in frontend state
- File history persisted across sessions
- Integration with agent context for file processing

---

## API Integration Specifications

### Required API Endpoints

#### Agent Management
```typescript
// Get all available agents
GET /api/agents
Response: {
  success: boolean
  agents: Agent[]
}

// Switch to specific agent
POST /api/agents/switch
Body: { agentId: string }
Response: {
  success: boolean
  activeAgent: Agent
}

// Get current active agent
GET /api/agents/current
Response: {
  success: boolean
  agent: Agent
}

// Get agent capabilities
GET /api/agents/{agentId}/capabilities
Response: {
  success: boolean
  capabilities: AgentCapability[]
}
```

#### File Upload
```typescript
// Standard file upload
POST /api/files/upload
Body: FormData with file
Response: {
  success: boolean
  file: UploadedFile
}

// CSV file upload (workaround)
POST /api/files/upload-csv
Body: {
  filename: string
  content: string
  size: number
  type: string
}
Response: {
  success: boolean
  file: UploadedFile
  processedData?: any
}

// Get file history
GET /api/files
Response: {
  success: boolean
  files: UploadedFile[]
}

// Delete file
DELETE /api/files/{fileId}
Response: {
  success: boolean
}
```

#### Chat Interface
```typescript
// Send message
POST /api/chat/message
Body: {
  content: string
  agentId?: string
  attachments?: string[] // file IDs
}
Response: {
  success: boolean
  message: ChatMessage
}

// Get chat history
GET /api/chat/history?sessionId={sessionId}
Response: {
  success: boolean
  messages: ChatMessage[]
}

// Create new chat session
POST /api/chat/session
Body: { agentId: string }
Response: {
  success: boolean
  session: ChatSession
}
```

#### Chat Status Indicators
- **Unified Status Display**: Single "Working..." indicator for all processing states
- **User-Friendly Messaging**: Simplified status messages that hide technical implementation details
- **Visual Feedback**: Consistent spinner animations and timestamps across all states
- **State Management**: Prevents duplicate status indicators from displaying simultaneously
- **Agent Identification**: Agent avatars in chat messages show which specialist is responding

#### Streaming Chat Implementation
```typescript
// Real-time streaming via /run_sse endpoint
await chatApi.sendMessageStreaming(
  content,
  agentId,
  attachments,
  onChunk,    // Real-time content updates
  onComplete  // Final message handling with agent separation
)

// Agent separation logic for multiple responses
// Automatically creates separate chat bubbles for different agents
// Maintains conversation flow while showing agent transitions
```

#### System Status
```typescript
// Get system health
GET /api/system/status
Response: {
  success: boolean
  status: SystemStatus
}

// Get system information
GET /api/system/info
Response: {
  success: boolean
  info: {
    version: string
    agents: Agent[]
    features: string[]
  }
}
```

### Error Handling Patterns
```typescript
interface APIError {
  success: false
  error: string
  code?: string
  details?: any
}

// Standard error responses
400 Bad Request: Invalid request data
401 Unauthorized: Authentication required
403 Forbidden: Insufficient permissions
404 Not Found: Resource not found
429 Too Many Requests: Rate limit exceeded
500 Internal Server Error: Server error
503 Service Unavailable: Service temporarily down
```

### Request/Response Interceptors
```typescript
// Request interceptor
axios.interceptors.request.use(config => {
  config.headers['Content-Type'] = 'application/json'
  config.timeout = 30000 // 30 seconds
  return config
})

// Response interceptor
axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      // Handle authentication error
    }
    if (error.response?.status >= 500) {
      // Handle server error
    }
    return Promise.reject(error)
  }
)
```

### Retry Mechanism
```typescript
const retryConfig = {
  retries: 3,
  retryDelay: (retryCount) => Math.pow(2, retryCount) * 1000,
  retryCondition: (error) => {
    return error.response?.status >= 500 || error.code === 'NETWORK_ERROR'
  }
}
```

---

## Component Architecture and Development Guidelines

### TypeScript Interface Definitions
```typescript
// Core Types
interface Agent {
  id: string
  name: string
  description: string
  specialties: string[]
  capabilities: string[]
  status: 'active' | 'available' | 'busy' | 'offline'
  model: string
  lastActive?: Date
}

interface UploadedFile {
  id: string
  name: string
  size: number
  type: string
  content?: string // For CSV workaround
  uploadedAt: Date
  status: 'uploading' | 'uploaded' | 'processing' | 'processed' | 'error'
  processedData?: any
  errorMessage?: string
}

interface ChatMessage {
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

interface ChatStatus {
  isLoading: boolean
  streamingMessage: ChatMessage | null
  displayStatus: 'idle' | 'working' // Simplified status for user display
}

interface AgentAvatarProps {
  agentId: string
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

interface EnhancedChatStore extends ChatStore {
  // Backend sync capabilities
  syncWithBackend: (userId: string) => Promise<void>
  persistSessionToBackend: (session: ChatSession) => Promise<void>
  loadSessionFromBackend: (sessionId: string, userId: string) => Promise<ChatSession | null>
  enableBackendSync: boolean
  setBackendSync: (enabled: boolean) => void
}
```

### Component Prop Interfaces
```typescript
// Agent Selector Props
interface AgentSelectorProps {
  className?: string
  onAgentChange?: (agent: Agent) => void
  showCapabilities?: boolean
}

// File Upload Props
interface FileUploadProps {
  className?: string
  maxFileSize?: number
  acceptedTypes?: string[]
  onFileUploaded?: (file: UploadedFile) => void
  multiple?: boolean
}

// Chat Interface Props
interface ChatInterfaceProps {
  className?: string
  sessionId?: string
  agentId?: string
  onMessageSent?: (message: ChatMessage) => void
}
```

### Styling with Tailwind CSS

#### MAGPIE Brand Colors
```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          900: '#1e3a8a'
        },
        success: {
          50: '#f0fdf4',
          500: '#22c55e',
          600: '#16a34a'
        },
        warning: {
          50: '#fffbeb',
          500: '#f59e0b',
          600: '#d97706'
        },
        error: {
          50: '#fef2f2',
          500: '#ef4444',
          600: '#dc2626'
        }
      }
    }
  }
}
```

#### Component Styling Patterns
```typescript
// Button variants
const buttonVariants = {
  primary: 'bg-primary-600 text-white hover:bg-primary-700',
  secondary: 'bg-gray-100 text-gray-900 hover:bg-gray-200',
  outline: 'border border-gray-300 bg-white hover:bg-gray-50'
}

// Status indicators
const statusColors = {
  active: 'bg-green-500',
  available: 'bg-blue-500',
  busy: 'bg-yellow-500',
  offline: 'bg-gray-400'
}
```

### Code Organization Patterns

#### File Naming Conventions
- Components: PascalCase (e.g., `AgentSelector.tsx`)
- Hooks: camelCase with 'use' prefix (e.g., `useAgent.ts`)
- Utilities: camelCase (e.g., `fileUtils.ts`)
- Types: camelCase (e.g., `index.ts`)
- Constants: UPPER_SNAKE_CASE (e.g., `API_ENDPOINTS`)

#### Import Organization
```typescript
// 1. React and external libraries
import React, { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Upload, File } from 'lucide-react'

// 2. Internal utilities and types
import { api } from '@/utils/api'
import type { Agent, UploadedFile } from '@/types'

// 3. Internal components and hooks
import { useAgent } from '@/hooks/useAgent'
import { Button } from '@/components/ui/Button'
```

#### Component Structure Template
```typescript
interface ComponentProps {
  // Props interface
}

export function Component({ prop1, prop2 }: ComponentProps) {
  // 1. State declarations
  const [state, setState] = useState()
  
  // 2. Custom hooks
  const { data, loading } = useCustomHook()
  
  // 3. Event handlers
  const handleEvent = () => {
    // Handler logic
  }
  
  // 4. Effects
  useEffect(() => {
    // Effect logic
  }, [])
  
  // 5. Early returns
  if (loading) return <div>Loading...</div>
  
  // 6. Render
  return (
    <div className="component-container">
      {/* JSX content */}
    </div>
  )
}
```

---

## Development Workflow and Build Process

### Environment Setup
```bash
# Prerequisites
node --version  # Should be v22.x.x
npm --version   # Should be v10.x.x

# Install dependencies
cd frontend
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Development Scripts
```json
{
  "scripts": {
    "dev": "vite --host",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "tsc --noEmit",
    "type-check": "tsc --noEmit",
    "test": "vitest",
    "test:ui": "vitest --ui"
  }
}
```

### Build Configuration
```typescript
// vite.config.ts
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      }
    }
  },
  build: {
    target: 'esnext',
    outDir: 'dist',
    sourcemap: true
  }
})
```

### Testing Strategy

#### Unit Testing
- **Framework**: Vitest + React Testing Library
- **Coverage**: Aim for 80%+ coverage on components
- **Test Files**: `*.test.tsx` alongside components

#### Integration Testing
- **API Integration**: Mock API responses
- **Component Integration**: Test component interactions
- **File Upload**: Test CSV workaround functionality

#### E2E Testing (Future)
- **Framework**: Playwright
- **Scenarios**: Agent switching, file upload, chat flow

### Code Quality Standards

#### ESLint Configuration
```json
{
  "extends": [
    "@typescript-eslint/recommended",
    "plugin:react/recommended",
    "plugin:react-hooks/recommended"
  ],
  "rules": {
    "react/react-in-jsx-scope": "off",
    "@typescript-eslint/no-unused-vars": "error",
    "prefer-const": "error"
  }
}
```

#### Prettier Configuration
```json
{
  "semi": false,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5"
}
```

---

## Integration Requirements

### Vite Proxy Configuration
```typescript
// vite.config.ts
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, '/api')
      }
    }
  }
})
```

### Environment Variables
```bash
# .env.local
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_NAME=MAGPIE
VITE_APP_VERSION=1.0.0
VITE_ENABLE_DEBUG=true
```

### CORS Configuration
The Google ADK backend should be configured to allow requests from the frontend:
```python
# Backend CORS settings (handled by ADK)
ALLOWED_ORIGINS = [
  "http://localhost:3000",  # Vite dev server
  "http://127.0.0.1:3000"   # Alternative localhost
]
```

### Security Considerations
- **API Keys**: Never expose backend API keys in frontend
- **File Upload**: Validate file types and sizes on both frontend and backend
- **XSS Protection**: Sanitize user inputs and file contents
- **CSRF**: Use ADK's built-in CSRF protection

### Authentication Integration
```typescript
// Authentication with ADK session
const authConfig = {
  withCredentials: true,  // Include cookies
  headers: {
    'X-Requested-With': 'XMLHttpRequest'
  }
}
```

### Performance Optimization
- **Code Splitting**: Lazy load components
- **Bundle Analysis**: Monitor bundle size
- **Caching**: Use React Query for API caching
- **Image Optimization**: Optimize uploaded images

### Deployment Considerations
- **Build Output**: Static files in `dist/` directory
- **Routing**: Configure for SPA routing
- **Environment**: Production environment variables
- **CDN**: Consider CDN for static assets

---

## Conclusion

This document provides comprehensive specifications for the MAGPIE multi-agent platform frontend. The architecture is designed to be scalable, maintainable, and user-friendly while integrating seamlessly with the Google ADK backend.

For implementation guidance and current status, refer to:
- **Implementation Status**: `frontend/IMPLEMENTATION_STATUS.md`
- **Google ADK Documentation**: https://google.github.io/adk-docs/
- **Component Examples**: `frontend/src/components/`
- **API Integration**: `frontend/src/utils/api.ts`
