import React, { useState, useEffect } from 'react'
import { 
  Zap, 
  Database, 
  MessageCircle, 
  FileText, 
  Settings, 
  ChevronDown, 
  ChevronRight,
  Info,
  CheckCircle,
  AlertCircle,
  Loader2
} from 'lucide-react'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { useAgent } from '@/stores/agentStore'
import type { Agent, AgentCapability } from '@/types'

const agentIcons: Record<string, React.ComponentType<any>> = {
  master_coordinator: Settings,
  engineering_process_procedure_agent: Zap,
  data_scientist_agent: Database,
  general_chat_agent: MessageCircle,
  csv_cleaning_agent: FileText,
}

const categoryIcons: Record<string, React.ComponentType<any>> = {
  communication: MessageCircle,
  data: Database,
  analysis: Zap,
  processing: FileText,
  system: Settings,
  general: Info,
}

interface AgentCapabilitiesProps {
  agent?: Agent
  agentId?: string
  showHeader?: boolean
  expandable?: boolean
  className?: string
}

export function AgentCapabilities({
  agent: propAgent,
  agentId,
  showHeader = true,
  expandable = false,
  className = ''
}: AgentCapabilitiesProps) {
  const { agents, getAgentCapabilities } = useAgent()
  const [capabilities, setCapabilities] = useState<AgentCapability[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set())

  // Determine which agent to use
  const agent = propAgent || agents.find(a => a.id === agentId)

  useEffect(() => {
    if (agent) {
      loadCapabilities()
    }
  }, [agent])

  const loadCapabilities = async () => {
    if (!agent) return

    setLoading(true)
    setError(null)
    
    try {
      const caps = await getAgentCapabilities(agent.id)
      setCapabilities(caps)
      
      // Auto-expand all categories if not expandable
      if (!expandable) {
        const categories = new Set(caps.map(cap => cap.category))
        setExpandedCategories(categories)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load capabilities')
    } finally {
      setLoading(false)
    }
  }

  const toggleCategory = (category: string) => {
    if (!expandable) return
    
    const newExpanded = new Set(expandedCategories)
    if (newExpanded.has(category)) {
      newExpanded.delete(category)
    } else {
      newExpanded.add(category)
    }
    setExpandedCategories(newExpanded)
  }

  const groupedCapabilities = capabilities.reduce((acc, capability) => {
    const category = capability.category || 'general'
    if (!acc[category]) {
      acc[category] = []
    }
    acc[category].push(capability)
    return acc
  }, {} as Record<string, AgentCapability[]>)

  const getAgentIcon = (agentId: string) => {
    return agentIcons[agentId] || Info
  }

  const getCategoryIcon = (category: string) => {
    return categoryIcons[category] || Info
  }

  if (!agent) {
    return (
      <Card className={`p-4 ${className}`}>
        <div className="text-center text-gray-500">
          <AlertCircle className="w-8 h-8 mx-auto mb-2" />
          <p>No agent selected</p>
        </div>
      </Card>
    )
  }

  const AgentIcon = getAgentIcon(agent.id)

  return (
    <Card className={`${className}`}>
      {showHeader && (
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-lg bg-primary-100 flex items-center justify-center">
              <AgentIcon className="w-5 h-5 text-primary-600" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-gray-900">{agent.name}</h3>
              <p className="text-sm text-gray-600">Agent Capabilities</p>
            </div>
            <Badge variant="primary" size="sm">
              {capabilities.length} capabilities
            </Badge>
          </div>
        </div>
      )}

      <div className="p-4">
        {loading && (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="w-6 h-6 animate-spin text-primary-600" />
            <span className="ml-2 text-gray-600">Loading capabilities...</span>
          </div>
        )}

        {error && (
          <div className="flex items-center space-x-2 p-3 bg-red-50 border border-red-200 rounded-lg">
            <AlertCircle className="w-5 h-5 text-red-500" />
            <span className="text-red-700">{error}</span>
            <Button
              variant="outline"
              size="sm"
              onClick={loadCapabilities}
              className="ml-auto"
            >
              Retry
            </Button>
          </div>
        )}

        {!loading && !error && capabilities.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            <Info className="w-8 h-8 mx-auto mb-2" />
            <p>No capabilities available for this agent</p>
          </div>
        )}

        {!loading && !error && capabilities.length > 0 && (
          <div className="space-y-4">
            {Object.entries(groupedCapabilities).map(([category, caps]) => {
              const CategoryIcon = getCategoryIcon(category)
              const isExpanded = expandedCategories.has(category)
              
              return (
                <div key={category} className="border border-gray-200 rounded-lg">
                  <div
                    className={`p-3 flex items-center justify-between ${
                      expandable ? 'cursor-pointer hover:bg-gray-50' : ''
                    }`}
                    onClick={() => expandable && toggleCategory(category)}
                  >
                    <div className="flex items-center space-x-3">
                      <CategoryIcon className="w-5 h-5 text-gray-600" />
                      <div>
                        <h4 className="font-medium text-gray-900 capitalize">
                          {category}
                        </h4>
                        <p className="text-xs text-gray-500">
                          {caps.length} capability{caps.length !== 1 ? 's' : ''}
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <Badge variant="secondary" size="sm">
                        {caps.length}
                      </Badge>
                      {expandable && (
                        isExpanded ? (
                          <ChevronDown className="w-4 h-4 text-gray-400" />
                        ) : (
                          <ChevronRight className="w-4 h-4 text-gray-400" />
                        )
                      )}
                    </div>
                  </div>
                  
                  {(!expandable || isExpanded) && (
                    <div className="border-t border-gray-200 p-3 space-y-3">
                      {caps.map((capability, index) => (
                        <div key={index} className="flex items-start space-x-3">
                          <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                          <div className="flex-1">
                            <h5 className="font-medium text-gray-900">
                              {capability.name}
                            </h5>
                            <p className="text-sm text-gray-600 mt-1">
                              {capability.description}
                            </p>
                            {capability.examples && capability.examples.length > 0 && (
                              <div className="mt-2">
                                <p className="text-xs font-medium text-gray-700 mb-1">
                                  Examples:
                                </p>
                                <ul className="text-xs text-gray-600 space-y-1">
                                  {capability.examples.slice(0, 3).map((example, idx) => (
                                    <li key={idx} className="flex items-start space-x-1">
                                      <span className="text-gray-400">•</span>
                                      <span>{example}</span>
                                    </li>
                                  ))}
                                  {capability.examples.length > 3 && (
                                    <li className="text-gray-500 italic">
                                      +{capability.examples.length - 3} more examples
                                    </li>
                                  )}
                                </ul>
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        )}
      </div>
    </Card>
  )
}
