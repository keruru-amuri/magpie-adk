import React, { type ReactNode } from 'react'
import { create } from 'zustand'
import { devtools } from 'zustand/middleware'
import { agentApi, chatApi } from '@/utils/api'
import type { Agent, AgentCapability, AgentStore } from '@/types'

// Default agents based on MAGPIE platform
const defaultAgents: Agent[] = [
  {
    id: 'master_coordinator',
    name: 'Master Coordinator',
    description: 'Intelligent request routing and coordination across all specialized agents',
    specialties: ['routing', 'coordination', 'delegation', 'system_management'],
    capabilities: ['agent_routing', 'system_status', 'request_analysis', 'intelligent_delegation'],
    status: 'active',
    model: 'gpt-4.1'
  },
  {
    id: 'engineering_process_procedure_agent',
    name: 'Engineering Process Agent',
    description: 'Aviation MRO and engineering procedures with automatic query enhancement',
    specialties: ['aviation maintenance', 'aircraft MRO', 'regulatory compliance'],
    capabilities: ['query_enhancement', 'databricks_integration', 'aviation_expertise', 'regulatory_knowledge'],
    status: 'available',
    model: 'DeepSeek-R1-0528'
  },
  {
    id: 'data_scientist_agent',
    name: 'Data Scientist Agent',
    description: 'Data analysis and business intelligence using Databricks integration',
    specialties: ['data analysis', 'SQL queries', 'business intelligence', 'statistical analysis'],
    capabilities: ['databricks_queries', 'data_visualization', 'statistical_analysis', 'cluster_management'],
    status: 'available',
    model: 'gpt-4.1' // Can be switched to DeepSeek
  },
  {
    id: 'general_chat_agent',
    name: 'General Chat Agent',
    description: 'General conversation and assistance for casual interactions',
    specialties: ['conversation', 'general help', 'advice', 'motivation'],
    capabilities: ['casual_conversation', 'general_assistance', 'motivation', 'agent_transfer'],
    status: 'available',
    model: 'gpt-4.1-mini'
  },
  {
    id: 'csv_cleaning_agent',
    name: 'CSV Cleaning Agent',
    description: 'Specialized tool for cleaning and standardizing CSV files',
    specialties: ['csv cleaning', 'data standardization', 'file processing', 'data validation'],
    capabilities: ['csv_processing', 'data_cleaning', 'schema_validation', 'format_standardization'],
    status: 'available',
    model: 'gpt-4.1-mini'
  }
]

// Filter out Master Coordinator from user-facing agent list
const getUserFacingAgents = (agents: Agent[]) =>
  agents.filter(agent => agent.id !== 'master_coordinator')

// Create the Zustand store
export const useAgent = create<AgentStore>()(
  devtools(
    (set, get) => ({
      agents: getUserFacingAgents(defaultAgents),
      activeAgent: defaultAgents.find(agent => agent.id === 'master_coordinator') || defaultAgents[0], // Always Master Coordinator
      displayAgent: getUserFacingAgents(defaultAgents)[0], // First user-facing agent for UI display
      isLoading: false,
      error: null,

      setActiveAgent: (agent: Agent) => {
        // Clear ADK session when switching agents to ensure fresh conversation context
        chatApi.clearSession()
        console.log('🔄 Switching to agent:', agent.id)
        set({ activeAgent: agent }, false, 'setActiveAgent')
      },

      setDisplayAgent: (agent: Agent) => {
        // Clear ADK session when switching display agents too
        chatApi.clearSession()
        console.log('🔄 Switching display agent to:', agent.id)
        set({ displayAgent: agent }, false, 'setDisplayAgent')
      },

      fetchAgents: async () => {
        set({ isLoading: true, error: null })
        try {
          const response = await agentApi.getAgents()
          if (response.success && response.data) {
            const allAgents = response.data
            const userFacingAgents = getUserFacingAgents(allAgents)
            set({
              agents: userFacingAgents,
              isLoading: false,
              // Always keep Master Coordinator as active agent for routing
              activeAgent: allAgents.find((a: Agent) => a.id === 'master_coordinator') || allAgents[0],
              // Keep current display agent if it exists in the new list
              displayAgent: userFacingAgents.find((a: Agent) => a.id === get().displayAgent?.id) || userFacingAgents[0]
            })
          } else {
            throw new Error(response.error || 'Failed to fetch agents')
          }
        } catch (error) {
          console.error('Failed to fetch agents:', error)
          const fallbackAgents = getUserFacingAgents(defaultAgents)
          set({
            error: 'Failed to fetch agents. Using default configuration.',
            isLoading: false,
            agents: fallbackAgents,
            activeAgent: defaultAgents.find(agent => agent.id === 'master_coordinator') || defaultAgents[0],
            displayAgent: fallbackAgents[0]
          })
        }
      },

      switchAgent: async (agentId: string) => {
        // This updates the display agent (what shows in UI) while keeping
        // Master Coordinator as the active agent for actual message routing

        const agent = get().agents.find(a => a.id === agentId)
        if (!agent) {
          set({ error: `Agent with ID ${agentId} not found` })
          return
        }

        set({ isLoading: true, error: null })
        try {
          console.log(`Display agent changed to: ${agent.name}. Master Coordinator still handles routing.`)

          // Update display agent for UI purposes
          set({
            displayAgent: agent,
            isLoading: false,
            // Update the agent status in the list for UI purposes
            agents: get().agents.map(a => ({
              ...a,
              status: a.id === agentId ? 'active' : (a.status === 'active' ? 'available' : a.status)
            }))
          })
        } catch (error) {
          console.error('Failed to switch display agent:', error)
          set({
            error: 'Failed to switch agent. Please try again.',
            isLoading: false
          })
        }
      },

      getAgentCapabilities: async (agentId: string): Promise<AgentCapability[]> => {
        try {
          const response = await agentApi.getAgentCapabilities(agentId)
          if (response.success && response.data) {
            return response.data
          }
          throw new Error(response.error || 'Failed to fetch capabilities')
        } catch (error) {
          console.error('Failed to fetch agent capabilities:', error)

          // Return default capabilities based on agent
          const agent = get().agents.find(a => a.id === agentId)
          if (!agent) return []

          return agent.capabilities.map(cap => ({
            name: cap,
            description: `${cap} capability`,
            category: 'general',
            examples: []
          }))
        }
      }
    }),
    {
      name: 'agent-store',
    }
  )
)

// Provider component for initialization
export function AgentProvider({ children }: { children: ReactNode }) {
  const fetchAgents = useAgent(state => state.fetchAgents)

  // Initialize agents on mount
  React.useEffect(() => {
    fetchAgents()
  }, [fetchAgents])

  return <>{children}</>
}
