import React, { useState } from 'react'
import { ChevronDown, User, Zap, Database, MessageCircle, FileText, Settings } from 'lucide-react'
import { useAgent } from '@/stores/agentStore'
import type { Agent, AgentSelectorProps } from '@/types'

const agentIcons: Record<string, React.ComponentType<any>> = {
  master_coordinator: Settings,
  engineering_process_procedure_agent: Zap,
  data_scientist_agent: Database,
  general_chat_agent: MessageCircle,
  csv_cleaning_agent: FileText,
}

export function AgentSelector({ className, onAgentChange }: AgentSelectorProps) {
  const { agents, displayAgent, switchAgent, isLoading } = useAgent()
  const [isOpen, setIsOpen] = useState(false)

  const handleAgentSwitch = async (agent: Agent) => {
    if (agent.id === displayAgent?.id) return
    
    try {
      await switchAgent(agent.id)
      onAgentChange?.(agent)
      setIsOpen(false)
    } catch (error) {
      console.error('Failed to switch agent:', error)
    }
  }

  const getStatusColor = (status: Agent['status']) => {
    switch (status) {
      case 'active':
        return 'bg-green-500'
      case 'available':
        return 'bg-blue-500'
      case 'busy':
        return 'bg-yellow-500'
      case 'offline':
        return 'bg-gray-400'
      default:
        return 'bg-gray-400'
    }
  }

  const getAgentIcon = (agentId: string) => {
    const IconComponent = agentIcons[agentId] || User
    return IconComponent
  }

  if (!displayAgent) {
    return (
      <div className="flex items-center space-x-2 text-gray-500">
        <div className="animate-pulse">Loading agents...</div>
      </div>
    )
  }

  return (
    <div className={`relative ${className}`}>
      {/* Current Agent Display */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        disabled={isLoading}
        className="flex items-center space-x-3 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors disabled:opacity-50"
      >
        <div className="flex items-center space-x-2">
          <div className="relative">
            {React.createElement(getAgentIcon(displayAgent.id), {
              className: "w-5 h-5 text-gray-600"
            })}
            <div className={`absolute -bottom-1 -right-1 w-3 h-3 rounded-full border-2 border-white ${getStatusColor(displayAgent.status)}`} />
          </div>
          <div className="text-left">
            <div className="font-medium text-gray-900">{displayAgent.name}</div>
            <div className="text-xs text-gray-500 capitalize">{displayAgent.status}</div>
          </div>
        </div>
        <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {/* Agent Selection Dropdown */}
      {isOpen && (
        <div className="absolute top-full left-0 mt-2 w-80 bg-white border border-gray-200 rounded-lg shadow-lg z-50">
          <div className="p-3 border-b border-gray-100">
            <h3 className="font-medium text-gray-900">Select Agent</h3>
            <p className="text-xs text-gray-500 mt-1">Choose a specialized agent for your task</p>
          </div>
          
          <div className="max-h-96 overflow-y-auto">
            {agents.map((agent) => {
              const IconComponent = getAgentIcon(agent.id)
              const isActive = agent.id === displayAgent.id
              
              return (
                <button
                  key={agent.id}
                  onClick={() => handleAgentSwitch(agent)}
                  disabled={isLoading || agent.status === 'offline'}
                  className={`w-full p-4 text-left hover:bg-gray-50 focus:outline-none focus:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${
                    isActive ? 'bg-primary-50 border-r-2 border-primary-500' : ''
                  }`}
                >
                  <div className="flex items-start space-x-3">
                    <div className="relative flex-shrink-0">
                      <IconComponent className={`w-6 h-6 ${isActive ? 'text-primary-600' : 'text-gray-600'}`} />
                      <div className={`absolute -bottom-1 -right-1 w-3 h-3 rounded-full border-2 border-white ${getStatusColor(agent.status)}`} />
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <h4 className={`font-medium truncate ${isActive ? 'text-primary-900' : 'text-gray-900'}`}>
                          {agent.name}
                        </h4>
                        {isActive && (
                          <span className="badge-primary text-xs">Active</span>
                        )}
                      </div>
                      
                      <p className="text-sm text-gray-600 mt-1 line-clamp-2">
                        {agent.description}
                      </p>
                      
                      <div className="flex flex-wrap gap-1 mt-2">
                        {agent.specialties.slice(0, 3).map((specialty) => (
                          <span
                            key={specialty}
                            className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800"
                          >
                            {specialty}
                          </span>
                        ))}
                        {agent.specialties.length > 3 && (
                          <span className="text-xs text-gray-500">
                            +{agent.specialties.length - 3} more
                          </span>
                        )}
                      </div>
                      
                      {agent.model && (
                        <div className="text-xs text-gray-500 mt-1">
                          Model: {agent.model}
                        </div>
                      )}
                    </div>
                  </div>
                </button>
              )
            })}
          </div>
          
          <div className="p-3 border-t border-gray-100 bg-gray-50">
            <button
              onClick={() => setIsOpen(false)}
              className="text-sm text-gray-600 hover:text-gray-800"
            >
              Close
            </button>
          </div>
        </div>
      )}
      
      {/* Overlay to close dropdown */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setIsOpen(false)}
        />
      )}
    </div>
  )
}
