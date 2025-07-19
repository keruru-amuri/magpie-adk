# MAGPIE Frontend

Modern React 18 + TypeScript frontend for the MAGPIE (MAG Platform for Intelligent Execution) multi-agent platform.

## Features

### Core Functionality ✅
- **Real-time Chat Interface**: Streaming responses with typing indicators
- **Multi-Agent Support**: Seamless switching between specialized agents
- **Agent Separation**: Visual separation of agent responses in separate chat bubbles
- **File Upload**: Support for CSV, JSON, TXT, and image files
- **Session Management**: Persistent chat sessions with history
- **Responsive Design**: Mobile-friendly interface with collapsible sidebar

### Recent Improvements ✅
- **✅ Agent Separation (2025-01-19)**: Master Coordinator and specialist agents display in separate chat bubbles
- **✅ Response Deduplication (2025-01-19)**: Eliminated duplicate content in agent responses
- **✅ Enhanced Response Parsing**: Improved ADK response extraction with JSON unwrapping
- **✅ Better UX**: Clear visual indicators for agent transfers and responses

## Architecture

### Component Structure
```
src/
├── components/
│   ├── ChatInterface.tsx          # Main chat interface with streaming
│   ├── AgentSelector.tsx          # Agent selection and status
│   ├── FileUpload.tsx            # File upload handling
│   └── ui/                       # Reusable UI components
├── stores/
│   ├── chatStore.ts              # Chat state management
│   ├── agentStore.tsx            # Agent state management
│   └── fileStore.ts              # File upload state
├── utils/
│   ├── api.ts                    # API communication with ADK
│   └── fileUtils.ts              # File processing utilities
└── types/
    └── index.ts                  # TypeScript type definitions
```

### Key Technologies
- **React 18**: Modern React with concurrent features
- **TypeScript**: Type-safe development
- **Zustand**: Lightweight state management
- **Tailwind CSS**: Utility-first styling
- **Lucide React**: Modern icon library
- **Vite**: Fast development and build tool

## Agent Separation Implementation

### Overview
The frontend implements sophisticated agent separation logic to display responses from different agents in separate chat bubbles, providing clear visual distinction between agent interactions.

### Key Components

#### 1. Response Extraction (`utils/api.ts`)
```typescript
function extractResponseContent(adkResponse: any, previousContent: string = ''): string {
  // Enhanced extraction with deduplication
  // - Handles JSON-wrapped responses from Databricks
  // - Prevents duplicate content extraction
  // - Provides detailed logging for debugging
}
```

#### 2. Agent Separation (`utils/api.ts`)
```typescript
function separateAgentResponses(combinedContent: string): { agentId: string; content: string }[] {
  // Detects agent transfer patterns
  // - Master Coordinator → Engineering Process Agent
  // - Master Coordinator → Data Scientist Agent
  // - Master Coordinator → General Chat Agent
  // Returns array of separated responses with correct agent attribution
}
```

#### 3. Streaming Handler (`components/ChatInterface.tsx`)
```typescript
// Enhanced completion callback for multiple messages
(finalMessage: ChatMessage) => {
  // Handles both single responses and agent transfers
  // - Prevents duplicate user messages
  // - Adds multiple agent responses separately
  // - Updates chat state correctly
}
```

### Transfer Pattern Detection

The system recognizes these transfer patterns:

1. **Engineering Process Agent**:
   ```
   "I'll transfer you to our Engineering Process Procedure Agent who specializes in aircraft MRO..."
   ```

2. **Data Scientist Agent**:
   ```
   "I'll transfer you to our Data Scientist Agent who specializes in..."
   ```

3. **General Chat Agent**:
   ```
   "I'll transfer you to our General Chat Agent for..."
   ```

### Visual Indicators

- **Agent Avatars**: Different avatars for each agent type
- **Agent Names**: Clear agent identification in message headers
- **Timestamps**: Individual timestamps for each response
- **Separate Bubbles**: Distinct chat bubbles for each agent

## API Integration

### ADK Communication
The frontend communicates with the Google ADK backend through:

#### Streaming API (`sendMessageStreaming`)
```typescript
await chatApi.sendMessageStreaming(
  content,
  agentId,
  attachments,
  onChunk,    // Real-time content updates
  onComplete  // Final message handling with agent separation
)
```

#### Session Management
```typescript
// Create/reuse ADK sessions
const session = await chatApi.createOrReuseSession(agentId, userId)

// Handle session state
const sessionState = {
  appName: agentId,
  userId: 'user_magpie',
  sessionId: `session_${agentId}_${timestamp}`
}
```

### Response Processing Flow

1. **User Input**: Message sent to current agent
2. **ADK Processing**: Backend processes with potential agent transfer
3. **Response Streaming**: Real-time content updates via SSE
4. **Content Extraction**: Parse ADK response structure
5. **Deduplication**: Remove duplicate content (JSON unwrapping)
6. **Agent Separation**: Split combined responses by agent
7. **UI Update**: Display separate chat bubbles for each agent

## State Management

### Chat Store (`stores/chatStore.ts`)
```typescript
interface ChatState {
  sessions: ChatSession[]
  activeSession: ChatSession | null
  isLoading: boolean
  
  // Actions
  createSession: (agentId: string) => Promise<ChatSession>
  sendMessage: (content: string, attachments?: UploadedFile[]) => Promise<void>
  loadSession: (sessionId: string) => Promise<void>
}
```

### Agent Store (`stores/agentStore.tsx`)
```typescript
interface AgentState {
  agents: Agent[]
  activeAgent: Agent | null
  isLoading: boolean
  
  // Actions
  fetchAgents: () => Promise<void>
  setActiveAgent: (agent: Agent) => void
}
```

## File Upload System

### Supported Formats
- **CSV**: Processed and converted for ADK compatibility
- **JSON**: Direct upload with validation
- **TXT**: Plain text file support
- **Images**: JPG, PNG, GIF support

### Upload Flow
1. **File Selection**: Drag & drop or click to select
2. **Validation**: Check file type and size limits
3. **Processing**: Convert CSV to compatible format
4. **Attachment**: Include with message to ADK
5. **Display**: Show file info in chat interface

## Development

### Setup
```bash
cd frontend
npm install
npm run dev
```

### Build
```bash
npm run build
npm run preview
```

### Environment Variables
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_NAME=MAGPIE
```

### Key Scripts
- `npm run dev`: Development server with hot reload
- `npm run build`: Production build
- `npm run preview`: Preview production build
- `npm run lint`: ESLint checking
- `npm run type-check`: TypeScript validation

## Testing

### Manual Testing Scenarios

#### Agent Separation Test
1. Send message: "Please transfer me to the engineering process agent. What is component label booking?"
2. Verify: Master Coordinator response in separate bubble
3. Verify: Engineering Process Agent response in separate bubble
4. Verify: No duplicate content in either response

#### File Upload Test
1. Upload CSV file with aviation data
2. Verify: File processed correctly
3. Send message referencing uploaded data
4. Verify: Agent can access and process file content

#### Session Management Test
1. Create new session
2. Send multiple messages
3. Switch to different agent
4. Return to original session
5. Verify: Message history preserved

## Troubleshooting

### Common Issues

#### Duplicate Responses
- **Symptom**: Same content appears twice in chat
- **Solution**: Check `extractResponseContent` deduplication logic
- **Debug**: Look for `🔄 Skipping duplicate content` in console

#### Agent Separation Not Working
- **Symptom**: Transfer responses in single bubble
- **Solution**: Verify transfer pattern detection in `separateAgentResponses`
- **Debug**: Look for `🔄 Agent transfer detected` in console

#### File Upload Failures
- **Symptom**: Files not uploading or processing
- **Solution**: Check file size limits and format validation
- **Debug**: Monitor network requests and file processing logs

### Debug Logging

The frontend provides comprehensive logging:
- `✅ Extracted text content`: Response extraction success
- `🧹 Unwrapped JSON content`: JSON response processing
- `🔄 Skipping duplicate content`: Deduplication working
- `🔄 Agent transfer detected`: Agent separation triggered
- `📨 Created multiple messages`: Multiple agent responses created

## Future Enhancements

### Planned Features
- **Real-time Collaboration**: Multiple users in same session
- **Voice Input**: Speech-to-text integration
- **Advanced File Processing**: PDF, Excel support
- **Agent Avatars**: Custom avatars for each agent type
- **Message Reactions**: Like/dislike agent responses
- **Export Functionality**: Save conversations as PDF/Word

### Technical Improvements
- **Performance Optimization**: Virtual scrolling for long conversations
- **Offline Support**: PWA capabilities with offline message queue
- **Enhanced Accessibility**: Screen reader optimization
- **Mobile App**: React Native version
- **Advanced Analytics**: User interaction tracking

## Contributing

### Code Style
- Use TypeScript for all new components
- Follow React hooks patterns
- Implement proper error boundaries
- Add comprehensive logging for debugging

### Component Guidelines
- Keep components focused and reusable
- Use Zustand for state management
- Implement proper loading states
- Handle errors gracefully

### Testing Requirements
- Test agent separation scenarios
- Verify file upload functionality
- Check responsive design
- Validate accessibility features
