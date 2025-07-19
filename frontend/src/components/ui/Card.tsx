import React from 'react'

export interface CardProps {
  children: React.ReactNode
  className?: string
  padding?: 'none' | 'sm' | 'md' | 'lg'
  shadow?: 'none' | 'sm' | 'md' | 'lg'
  border?: boolean
  hover?: boolean
}

const paddingClasses = {
  none: '',
  sm: 'p-3',
  md: 'p-4',
  lg: 'p-6',
}

const shadowClasses = {
  none: '',
  sm: 'shadow-sm',
  md: 'shadow-md',
  lg: 'shadow-lg',
}

export function Card({
  children,
  className = '',
  padding = 'md',
  shadow = 'sm',
  border = true,
  hover = false,
}: CardProps) {
  const baseClasses = 'bg-white rounded-lg'
  const paddingClass = paddingClasses[padding]
  const shadowClass = shadowClasses[shadow]
  const borderClass = border ? 'border border-gray-200' : ''
  const hoverClass = hover ? 'hover:shadow-md transition-shadow duration-200' : ''

  return (
    <div className={`${baseClasses} ${paddingClass} ${shadowClass} ${borderClass} ${hoverClass} ${className}`}>
      {children}
    </div>
  )
}

export interface CardHeaderProps {
  children: React.ReactNode
  className?: string
}

export function CardHeader({ children, className = '' }: CardHeaderProps) {
  return (
    <div className={`border-b border-gray-200 pb-3 mb-4 ${className}`}>
      {children}
    </div>
  )
}

export interface CardTitleProps {
  children: React.ReactNode
  className?: string
  as?: 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6'
}

export function CardTitle({ children, className = '', as: Component = 'h3' }: CardTitleProps) {
  return (
    <Component className={`text-lg font-semibold text-gray-900 ${className}`}>
      {children}
    </Component>
  )
}

export interface CardContentProps {
  children: React.ReactNode
  className?: string
}

export function CardContent({ children, className = '' }: CardContentProps) {
  return (
    <div className={`text-gray-700 ${className}`}>
      {children}
    </div>
  )
}

export interface CardFooterProps {
  children: React.ReactNode
  className?: string
}

export function CardFooter({ children, className = '' }: CardFooterProps) {
  return (
    <div className={`border-t border-gray-200 pt-3 mt-4 ${className}`}>
      {children}
    </div>
  )
}
