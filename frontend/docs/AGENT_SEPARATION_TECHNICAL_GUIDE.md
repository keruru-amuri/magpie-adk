# Agent Separation Technical Implementation Guide

## Overview

This guide provides detailed technical information about the agent separation feature implementation in the MAGPIE frontend, including code examples, debugging techniques, and troubleshooting steps.

## Core Implementation Files

### 1. Response Processing (`src/utils/api.ts`)

#### Enhanced Response Extraction
```typescript
function extractResponseContent(adkResponse: any, previousContent: string = ''): string {
  try {
    if (Array.isArray(adkResponse)) {
      let extractedContent = ''
      
      // Look for final agent response (text content)
      for (let i = adkResponse.length - 1; i >= 0; i--) {
        const event = adkResponse[i]
        if (event.content?.parts && Array.isArray(event.content.parts)) {
          for (const part of event.content.parts) {
            if (part.functionCall || part.functionResponse) continue
            
            if (part.text && typeof part.text === 'string') {
              extractedContent = part.text
              console.log('✅ Extracted text content from ADK response:', extractedContent.substring(0, 100) + '...')
              break
            }
          }
        }
        if (extractedContent) break
      }

      // Fallback: extract from function responses
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
      
      // Deduplication logic with JSON unwrapping
      if (extractedContent && previousContent) {
        let cleanExtractedContent = extractedContent
        
        // Handle JSON-wrapped content from Databricks
        try {
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
        
        // Skip if already contained in previous content
        if (previousContent.includes(cleanExtractedContent) || previousContent.includes(extractedContent)) {
          console.log('🔄 Skipping duplicate content:', cleanExtractedContent.substring(0, 100) + '...')
          return ''
        }
        
        return cleanExtractedContent
      }
      
      return extractedContent || ''
    }
    
    return typeof adkResponse === 'string' ? adkResponse : 'Response received from agent'
  } catch (error) {
    console.error('Error extracting response content:', error)
    return 'Error processing agent response'
  }
}
```

#### Agent Separation Logic
```typescript
function separateAgentResponses(combinedContent: string): { agentId: string; content: string }[] {
  const responses: { agentId: string; content: string }[] = []
  
  // Transfer pattern definitions
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
  
  // Pattern matching and content splitting
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
    // No transfer detected
    const agentId = chatApi.detectRespondingAgent(combinedContent, 'master_coordinator')
    responses.push({
      agentId,
      content: combinedContent
    })
  }
  
  return responses
}
```

### 2. Streaming Integration (`src/utils/api.ts`)

#### Enhanced Streaming Completion
```typescript
// In sendMessageStreaming function
if (eventData.trim() === '[DONE]') {
  const separatedResponses = separateAgentResponses(fullContent)
  
  if (separatedResponses.length > 1) {
    // Multiple agents - create separate messages
    const chatMessages: ChatMessage[] = separatedResponses.map(resp => ({
      id: crypto.randomUUID(),
      content: resp.content,
      role: 'assistant',
      timestamp: new Date(),
      agentId: resp.agentId
    }))
    
    console.log('📨 Created multiple messages for agent transfer:', 
      chatMessages.map(m => ({ 
        agentId: m.agentId, 
        contentPreview: m.content.substring(0, 50) + '...' 
      }))
    )
    
    // Call completion callback for each message
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
```

### 3. Chat Interface Updates (`src/components/ChatInterface.tsx`)

#### Multiple Message Handling
```typescript
// Enhanced completion callback
(finalMessage: ChatMessage) => {
  const currentMessages = useChatStore.getState().activeSession?.messages || []
  const userMessageExists = currentMessages.some(m => m.id === userMessage.id)
  
  if (!userMessageExists) {
    // First completion - add user message and assistant message
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
    // Subsequent completion (agent transfer) - add only assistant message
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
}
```

## Debugging and Troubleshooting

### Console Logging

The implementation provides comprehensive logging for debugging:

#### Response Extraction Logs
- `✅ Extracted text content from ADK response:` - Successfully extracted text from ADK response
- `✅ Extracted text from function response:` - Successfully extracted from function response
- `🧹 Unwrapped JSON content:` - JSON-wrapped content was detected and unwrapped
- `🔄 Skipping duplicate content:` - Duplicate content was detected and skipped

#### Agent Separation Logs
- `🔄 Agent transfer detected:` - Transfer pattern was matched and content separated
- `📨 Created multiple messages for agent transfer:` - Multiple chat messages created for separated agents

### Common Issues and Solutions

#### Issue 1: Duplicate Content Still Appearing
**Symptoms**: Same content appears twice in chat
**Debug Steps**:
1. Check console for `🔄 Skipping duplicate content` messages
2. Verify `previousContent` parameter is being passed correctly
3. Check if JSON unwrapping is working (`🧹 Unwrapped JSON content`)

**Solution**: Ensure `extractResponseContent` is called with `previousContent` parameter

#### Issue 2: Agent Separation Not Working
**Symptoms**: Transfer responses appear in single bubble
**Debug Steps**:
1. Check console for `🔄 Agent transfer detected` messages
2. Verify transfer pattern regex matches the actual content
3. Check if `separateAgentResponses` is being called

**Solution**: Update transfer patterns or verify content format

#### Issue 3: Multiple User Messages
**Symptoms**: User message appears multiple times
**Debug Steps**:
1. Check completion callback logic
2. Verify `userMessageExists` check is working
3. Monitor state updates

**Solution**: Ensure proper duplicate prevention in completion callback

### Testing Scenarios

#### Test 1: Basic Agent Transfer
```typescript
// Test message
"Please transfer me to the engineering process agent. What is component label booking?"

// Expected behavior
// 1. User message appears
// 2. Master Coordinator response in separate bubble
// 3. Engineering Process Agent response in separate bubble
// 4. No duplicate content
```

#### Test 2: Non-Transfer Response
```typescript
// Test message
"Hello, how are you?"

// Expected behavior
// 1. User message appears
// 2. Single agent response (no separation)
// 3. Correct agent attribution
```

#### Test 3: Complex Transfer with Long Response
```typescript
// Test message with long specialist response
"Transfer to engineering agent and explain aircraft maintenance procedures"

// Expected behavior
// 1. Clean separation despite long content
// 2. No truncation of transfer message
// 3. Complete specialist response
```

## Performance Considerations

### Optimization Strategies

1. **Efficient Pattern Matching**: Use optimized regex patterns
2. **Content Caching**: Cache processed responses to avoid reprocessing
3. **Lazy Loading**: Load chat history incrementally
4. **Memory Management**: Clean up old messages in long conversations

### Memory Usage

- **Message Storage**: Each message stores minimal required data
- **Content Deduplication**: Prevents memory bloat from duplicate content
- **Session Management**: Efficient session state updates

## Future Enhancements

### Planned Improvements

1. **Dynamic Pattern Detection**: Auto-learn transfer patterns
2. **Enhanced Visual Indicators**: Better agent identification
3. **Performance Monitoring**: Track separation performance
4. **Advanced Deduplication**: Semantic similarity detection

### Extension Points

1. **Custom Transfer Patterns**: Easy addition of new agent types
2. **Response Processors**: Pluggable response processing pipeline
3. **Visual Customization**: Configurable agent appearance
4. **Analytics Integration**: Track agent interaction patterns

## API Reference

### Key Functions

#### `extractResponseContent(adkResponse, previousContent)`
- **Purpose**: Extract and deduplicate content from ADK responses
- **Parameters**: 
  - `adkResponse`: Raw ADK response object
  - `previousContent`: Previously extracted content for deduplication
- **Returns**: Cleaned, deduplicated content string

#### `separateAgentResponses(combinedContent)`
- **Purpose**: Separate combined agent responses into individual messages
- **Parameters**: 
  - `combinedContent`: Combined response content from multiple agents
- **Returns**: Array of `{agentId, content}` objects

#### `sendMessageStreaming(content, agentId, attachments, onChunk, onComplete)`
- **Purpose**: Send message with streaming response and agent separation
- **Parameters**: 
  - `content`: Message content
  - `agentId`: Target agent ID
  - `attachments`: File attachments
  - `onChunk`: Streaming content callback
  - `onComplete`: Final message completion callback (called multiple times for agent separation)

This technical guide provides the foundation for understanding, debugging, and extending the agent separation feature in the MAGPIE frontend.
