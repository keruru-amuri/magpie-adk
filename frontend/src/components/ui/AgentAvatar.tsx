import React, { useState } from 'react'
import { User, Zap, Database, MessageCircle, FileText, Settings } from 'lucide-react'

interface AgentAvatarProps {
  agentId?: string
  role: 'user' | 'assistant' | 'system'
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

const agentIcons: Record<string, React.ComponentType<any>> = {
  master_coordinator: Settings,
  engineering_process_procedure_agent: Zap,
  data_scientist_agent: Database,
  general_chat_agent: MessageCircle,
  csv_cleaning_agent: FileText,
}

const agentColors: Record<string, string> = {
  master_coordinator: 'text-purple-600 bg-purple-100',
  engineering_process_procedure_agent: 'text-orange-600 bg-orange-100',
  data_scientist_agent: 'text-blue-600 bg-blue-100',
  general_chat_agent: 'text-green-600 bg-green-100',
  csv_cleaning_agent: 'text-indigo-600 bg-indigo-100',
}

export function AgentAvatar({ agentId, role, size = 'md', className = '' }: AgentAvatarProps) {
  const [imageError, setImageError] = useState(false)

  const sizeClasses = {
    sm: 'w-6 h-6',
    md: 'w-8 h-8',
    lg: 'w-10 h-10'
  }

  const iconSizeClasses = {
    sm: 'w-3 h-3',
    md: 'w-4 h-4',
    lg: 'w-5 h-5'
  }

  // User avatar
  if (role === 'user') {
    return (
      <div className={`${sizeClasses[size]} rounded-full bg-primary-100 flex items-center justify-center flex-shrink-0 ${className}`}>
        <User className={`${iconSizeClasses[size]} text-primary-600`} />
      </div>
    )
  }

  // System messages use a neutral icon
  if (role === 'system') {
    return (
      <div className={`${sizeClasses[size]} rounded-full bg-gray-100 flex items-center justify-center flex-shrink-0 ${className}`}>
        <Settings className={`${iconSizeClasses[size]} text-gray-600`} />
      </div>
    )
  }

  // Assistant avatar - try custom image first, fallback to icon
  const avatarImagePath = agentId ? `/avatars/${agentId}.png` : null
  const IconComponent = agentId ? (agentIcons[agentId] || Settings) : Settings
  const colorClasses = agentId ? (agentColors[agentId] || 'text-gray-600 bg-gray-100') : 'text-gray-600 bg-gray-100'

  // If we have an agent ID and no image error, try to show custom avatar
  if (agentId && avatarImagePath && !imageError) {
    return (
      <div className={`${sizeClasses[size]} rounded-full overflow-hidden flex-shrink-0 ${className}`}>
        <img
          src={avatarImagePath}
          alt={`${agentId} avatar`}
          className="w-full h-full object-cover"
          onError={() => setImageError(true)}
        />
      </div>
    )
  }

  // Fallback to icon
  return (
    <div className={`${sizeClasses[size]} rounded-full ${colorClasses} flex items-center justify-center flex-shrink-0 ${className}`}>
      <IconComponent className={iconSizeClasses[size]} />
    </div>
  )
}
