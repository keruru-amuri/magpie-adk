import React from 'react'
import { User, Zap, Database, MessageCircle, FileText, Settings, Clock } from 'lucide-react'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import type { Agent } from '@/types'

const agentIcons: Record<string, React.ComponentType<any>> = {
  master_coordinator: Settings,
  engineering_process_procedure_agent: Zap,
  data_scientist_agent: Database,
  general_chat_agent: MessageCircle,
  csv_cleaning_agent: FileText,
}

interface AgentCardProps {
  agent: Agent
  isActive?: boolean
  onSelect?: (agent: Agent) => void
  onViewCapabilities?: (agent: Agent) => void
  showActions?: boolean
  compact?: boolean
  className?: string
}

export function AgentCard({
  agent,
  isActive = false,
  onSelect,
  onViewCapabilities,
  showActions = true,
  compact = false,
  className = ''
}: AgentCardProps) {
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

  const formatLastActive = (lastActive?: Date) => {
    if (!lastActive) return 'Never'
    const now = new Date()
    const diff = now.getTime() - lastActive.getTime()
    const minutes = Math.floor(diff / 60000)
    const hours = Math.floor(minutes / 60)
    const days = Math.floor(hours / 24)

    if (days > 0) return `${days}d ago`
    if (hours > 0) return `${hours}h ago`
    if (minutes > 0) return `${minutes}m ago`
    return 'Just now'
  }

  const IconComponent = getAgentIcon(agent.id)

  if (compact) {
    return (
      <div
        className={`p-3 border rounded-lg cursor-pointer transition-all hover:shadow-md ${
          isActive 
            ? 'border-primary-500 bg-primary-50 shadow-sm' 
            : 'border-gray-200 bg-white hover:border-gray-300'
        } ${className}`}
        onClick={() => onSelect?.(agent)}
      >
        <div className="flex items-center space-x-3">
          <div className="relative flex-shrink-0">
            <IconComponent className={`w-5 h-5 ${isActive ? 'text-primary-600' : 'text-gray-600'}`} />
            <div className={`absolute -bottom-1 -right-1 w-3 h-3 rounded-full border-2 border-white ${getStatusColor(agent.status)}`} />
          </div>
          
          <div className="flex-1 min-w-0">
            <h4 className={`font-medium truncate ${isActive ? 'text-primary-900' : 'text-gray-900'}`}>
              {agent.name}
            </h4>
            <p className="text-xs text-gray-500 truncate">
              {agent.specialties.slice(0, 2).join(', ')}
              {agent.specialties.length > 2 && '...'}
            </p>
          </div>
          
          {isActive && (
            <Badge variant="primary" size="sm">
              Active
            </Badge>
          )}
        </div>
      </div>
    )
  }

  return (
    <div
      className={`p-4 border rounded-lg transition-all hover:shadow-md ${
        isActive 
          ? 'border-primary-500 bg-primary-50 shadow-sm' 
          : 'border-gray-200 bg-white hover:border-gray-300'
      } ${className}`}
    >
      <div className="flex items-start space-x-4">
        <div className="relative flex-shrink-0">
          <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
            isActive ? 'bg-primary-100' : 'bg-gray-100'
          }`}>
            <IconComponent className={`w-6 h-6 ${isActive ? 'text-primary-600' : 'text-gray-600'}`} />
          </div>
          <div className={`absolute -bottom-1 -right-1 w-4 h-4 rounded-full border-2 border-white ${getStatusColor(agent.status)}`} />
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-2">
            <h3 className={`font-semibold text-lg ${isActive ? 'text-primary-900' : 'text-gray-900'}`}>
              {agent.name}
            </h3>
            {isActive && (
              <Badge variant="primary">
                Active
              </Badge>
            )}
          </div>
          
          <p className="text-gray-600 text-sm mb-3 line-clamp-2">
            {agent.description}
          </p>
          
          {/* Specialties */}
          <div className="mb-3">
            <div className="flex flex-wrap gap-1">
              {agent.specialties.slice(0, 4).map((specialty) => (
                <span
                  key={specialty}
                  className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-gray-100 text-gray-700"
                >
                  {specialty}
                </span>
              ))}
              {agent.specialties.length > 4 && (
                <span className="text-xs text-gray-500 px-2 py-1">
                  +{agent.specialties.length - 4} more
                </span>
              )}
            </div>
          </div>
          
          {/* Model and Status Info */}
          <div className="flex items-center justify-between text-xs text-gray-500 mb-3">
            <div className="flex items-center space-x-3">
              {agent.model && (
                <span className="font-medium">
                  Model: {agent.model}
                </span>
              )}
              <span className="capitalize">
                Status: {agent.status}
              </span>
            </div>
            {agent.lastActive && (
              <div className="flex items-center space-x-1">
                <Clock className="w-3 h-3" />
                <span>{formatLastActive(agent.lastActive)}</span>
              </div>
            )}
          </div>
          
          {/* Actions */}
          {showActions && (
            <div className="flex space-x-2">
              {!isActive && onSelect && (
                <Button
                  size="sm"
                  onClick={() => onSelect(agent)}
                  disabled={agent.status === 'offline'}
                >
                  Select Agent
                </Button>
              )}
              {onViewCapabilities && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onViewCapabilities(agent)}
                >
                  View Capabilities
                </Button>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
