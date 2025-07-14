# Multi-Model Configuration Guide

## Overview
The MAGPIE platform now supports 4 different Azure models, allowing different agents to use different models based on their specific requirements and capabilities.

## Available Models

| Model | Deployment Name | Use Case | Characteristics |
|-------|----------------|----------|-----------------|
| **GPT-4.1** | `azure/gpt-4.1` | Complex reasoning, routing decisions | High capability, higher cost |
| **GPT-4.1 Mini** | `azure/gpt-4.1-mini` | General conversation, casual chat | Balanced capability/cost |
| **GPT-4.1 Nano** | `azure/gpt-4.1-nano` | Focused tasks, query enhancement | Fast, cost-effective |
| **DeepSeek-R1-0528** | `azure/DeepSeek-R1-0528` | Technical queries, reasoning | 128K context, strong reasoning |

## Configuration Structure

### 1. Available Models Section
```env
# Available Models Configuration
AVAILABLE_MODELS_GPT41=azure/gpt-4.1
AVAILABLE_MODELS_GPT41_MINI=azure/gpt-4.1-mini
AVAILABLE_MODELS_GPT41_NANO=azure/gpt-4.1-nano
AVAILABLE_MODELS_DEEPSEEK=azure/DeepSeek-R1-0528
```

### 2. Agent-Specific Configuration
```env
# Master Coordinator - Handles routing decisions (needs strong reasoning)
MASTER_COORDINATOR_MODEL=azure/gpt-4.1

# Engineering Process Procedure Agent - Complex technical queries
ENGINEERING_PROCESS_AGENT_MODEL=azure/DeepSeek-R1-0528

# Query Enhancement Sub-Agent - Focused enhancement tasks
QUERY_ENHANCEMENT_AGENT_MODEL=azure/gpt-4.1-nano

# Databricks Query Sub-Agent - Technical query processing
DATABRICKS_QUERY_AGENT_MODEL=azure/gpt-4.1

# General Chat Agent - Casual conversation (cost-effective)
GENERAL_CHAT_AGENT_MODEL=azure/gpt-4.1-mini
```

### 3. Model Selection Strategy
```env
# Model Selection Strategy
MODEL_SELECTION_STRATEGY=agent_specific
```

## Model Selection Strategies

### `agent_specific` (Recommended)
- Each agent uses its specifically configured model
- Optimizes performance and cost for each use case
- Allows fine-tuned model selection per agent

### `default`
- All agents use `DEFAULT_LLM_MODEL`
- Simplified configuration
- Consistent behavior across all agents

### `environment` (Legacy)
- All agents use `AZURE_OPENAI_MODEL`
- Backward compatibility mode
- Single model for entire system

## Recommended Agent-Model Mappings

### Master Coordinator → GPT-4.1
- **Why**: Needs strong reasoning for intelligent routing decisions
- **Characteristics**: High capability for understanding user intent

### Engineering Process Procedure Agent → DeepSeek-R1-0528
- **Why**: Excellent for technical queries and aviation domain
- **Characteristics**: 128K context window, strong reasoning capabilities

### Query Enhancement Sub-Agent → GPT-4.1 Nano
- **Why**: Focused task of enhancing queries with aviation context
- **Characteristics**: Fast, cost-effective for specific enhancement tasks

### Databricks Query Sub-Agent → GPT-4.1
- **Why**: Needs reliable performance for technical query processing
- **Characteristics**: Proven reliability for complex technical tasks

### General Chat Agent → GPT-4.1 Mini
- **Why**: Cost-effective for casual conversation and general advice
- **Characteristics**: Good balance of capability and cost

## Migration from Single Model

### Backward Compatibility
The new configuration maintains full backward compatibility:

```env
# Legacy variables still work
AZURE_OPENAI_MODEL=azure/gpt-4.1
DEFAULT_LLM_MODEL=azure/gpt-4.1
```

### Migration Steps
1. **Keep existing configuration** - system continues to work
2. **Add agent-specific models** - gradually configure specific agents
3. **Set strategy to agent_specific** - enable multi-model support
4. **Test and validate** - ensure all agents work correctly

## Configuration Examples

### Development Setup (Single Model)
```env
MODEL_SELECTION_STRATEGY=default
DEFAULT_LLM_MODEL=azure/gpt-4.1-mini
```

### Production Setup (Multi-Model)
```env
MODEL_SELECTION_STRATEGY=agent_specific
MASTER_COORDINATOR_MODEL=azure/gpt-4.1
ENGINEERING_PROCESS_AGENT_MODEL=azure/DeepSeek-R1-0528
GENERAL_CHAT_AGENT_MODEL=azure/gpt-4.1-mini
# ... other agent configurations
```

### Cost-Optimized Setup
```env
MODEL_SELECTION_STRATEGY=agent_specific
MASTER_COORDINATOR_MODEL=azure/gpt-4.1-mini
ENGINEERING_PROCESS_AGENT_MODEL=azure/gpt-4.1-mini
GENERAL_CHAT_AGENT_MODEL=azure/gpt-4.1-nano
```

## Troubleshooting

### Common Issues

1. **Agent not using configured model**
   - Check `MODEL_SELECTION_STRATEGY=agent_specific`
   - Verify agent-specific environment variable is set

2. **Model not found error**
   - Ensure model deployment exists in Azure
   - Check model name format: `azure/deployment-name`

3. **Fallback behavior**
   - If agent-specific model fails, falls back to `DEFAULT_LLM_MODEL`
   - If default fails, falls back to `AZURE_OPENAI_MODEL`

### Validation
Use the test script to validate model configurations:
```bash
python test_deepseek_integration.py
```

## Next Steps
1. ✅ Configuration updated
2. 🔄 Implement model factory pattern
3. 🔄 Update agent initialization code
4. 🔄 Test multi-agent scenarios
