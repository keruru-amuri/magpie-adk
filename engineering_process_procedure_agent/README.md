# Engineering Sequential Agent

This is a Google ADK Sequential Agent designed to address the limitation where multiple tools cannot be effectively reused within a single agent. It implements a two-stage pipeline for aircraft MRO (Maintenance, Repair, and Overhaul) and aviation engineering queries.

## Architecture

The Sequential Agent orchestrates two specialized subagents in a fixed order:

### 1. Query Enhancement Subagent
- **Purpose**: Transform user queries to include aviation engineering and MRO-specific context
- **Input**: Raw user query (e.g., "process of component robbing")
- **Output**: Enhanced query with aviation terminology, regulatory references (FAA/EASA), and MRO best practices
- **Function**: Acts as a preprocessing layer that enriches queries with domain expertise

### 2. Engineering Process Procedure Subagent
- **Purpose**: Process the enhanced query and interface with Databricks LLM endpoint
- **Input**: Enhanced query from the first subagent
- **Output**: Contextually accurate response from aviation knowledge base
- **Function**: Handles the actual Databricks communication and response formatting

## Sequential Flow

```
User Query → Query Enhancement Subagent → Enhanced Query → Engineering Process Procedure Subagent → Databricks LLM → Final Response
```

## Key Features

1. **Transparent Enhancement**: Enhancement happens seamlessly in the background - users receive better responses without seeing the enhancement process

2. **Fixed Execution Order**: Uses Google ADK's SequentialAgent to ensure proper tool execution order and data flow between stages

3. **State Management**: Output from each subagent is passed to the next via ADK's state management using `output_key`

4. **Aviation Specialization**: 
   - Aircraft maintenance procedures and troubleshooting
   - Aviation regulatory compliance (FAA, EASA, Part 145, etc.)
   - Aircraft safety protocols and SMS (Safety Management System)
   - MRO operations and reliability-centered maintenance (RCM)
   - Aviation engineering documentation and standards

5. **Query Classification**: Automatically classifies queries into aviation categories:
   - Maintenance
   - Troubleshooting  
   - Regulatory
   - Safety
   - General

## Directory Structure

```
engineering_sequential_agent/
├── __init__.py
├── agent.py                                    # Main Sequential Agent
├── README.md                                   # This file
└── sub_agents/
    ├── query_enhancement_agent/
    │   ├── __init__.py
    │   └── agent.py                           # Query Enhancement Subagent
    └── databricks_query_agent/
        ├── __init__.py
        └── agent.py                           # Databricks Query Subagent
```

## How It Works

1. **User Input**: User submits a query like "process of component robbing"

2. **Query Enhancement Stage**: 
   - QueryEnhancementAgent receives the raw query
   - Classifies the query type (maintenance, regulatory, etc.)
   - Enhances with aviation context, terminology, and best practices
   - Stores enhanced query in state with `output_key="enhanced_query"`

3. **Databricks Processing Stage**:
   - DatabricksQueryAgent receives enhanced query via state injection `{enhanced_query}`
   - Sends enhanced query to Databricks LLM serving endpoint
   - Returns contextually accurate response from aviation knowledge base

4. **Final Response**: User receives enhanced response without seeing the enhancement process

## Benefits of Sequential Agent Pattern

- **Addresses ADK Limitation**: Solves the issue where multiple tools cannot be effectively reused within a single agent
- **Deterministic Execution**: Ensures enhancement always happens before Databricks processing
- **Clean Separation of Concerns**: Each subagent has a single, focused responsibility
- **Maintainable Architecture**: Easy to modify or extend individual stages
- **Transparent to Users**: Complex processing happens behind the scenes

## Usage

The Sequential Agent is automatically used by the Master Coordinator when users ask aviation engineering questions. Users simply interact normally:

```
User: "What is the process of component robbing?"
System: [Automatically enhances query] → [Queries Databricks] → [Returns enhanced response]
```

## Configuration

The agent uses the same environment variables as the original implementation:
- `DATABRICKS_WORKSPACE_URL`: Your Databricks workspace URL
- `DATABRICKS_CLIENT_ID`: Service principal client ID
- `DATABRICKS_CLIENT_SECRET`: Service principal client secret
- `DATABRICKS_TENANT_ID`: Azure tenant ID
- `AZURE_OPENAI_*`: Azure OpenAI configuration for agent reasoning

## Integration

The Sequential Agent is integrated into the MAGPIE platform via the Master Coordinator, which routes aviation engineering queries to this agent automatically.
