import React from 'react'

export interface BadgeProps {
  children: React.ReactNode
  variant?: 'default' | 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info'
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

const badgeVariants = {
  default: 'bg-gray-100 text-gray-800',
  primary: 'bg-primary-100 text-primary-800',
  secondary: 'bg-gray-100 text-gray-800',
  success: 'bg-green-100 text-green-800',
  warning: 'bg-yellow-100 text-yellow-800',
  error: 'bg-red-100 text-red-800',
  info: 'bg-blue-100 text-blue-800',
}

const badgeSizes = {
  sm: 'px-2 py-0.5 text-xs',
  md: 'px-2.5 py-1 text-sm',
  lg: 'px-3 py-1.5 text-base',
}

export function Badge({
  children,
  variant = 'default',
  size = 'md',
  className = '',
}: BadgeProps) {
  const baseClasses = 'inline-flex items-center font-medium rounded-full'
  const variantClasses = badgeVariants[variant]
  const sizeClasses = badgeSizes[size]

  return (
    <span className={`${baseClasses} ${variantClasses} ${sizeClasses} ${className}`}>
      {children}
    </span>
  )
}

// Convenience components for common badge types
export function PrimaryBadge(props: Omit<BadgeProps, 'variant'>) {
  return <Badge variant="primary" {...props} />
}

export function SuccessBadge(props: Omit<BadgeProps, 'variant'>) {
  return <Badge variant="success" {...props} />
}

export function WarningBadge(props: Omit<BadgeProps, 'variant'>) {
  return <Badge variant="warning" {...props} />
}

export function ErrorBadge(props: Omit<BadgeProps, 'variant'>) {
  return <Badge variant="error" {...props} />
}

export function InfoBadge(props: Omit<BadgeProps, 'variant'>) {
  return <Badge variant="info" {...props} />
}
