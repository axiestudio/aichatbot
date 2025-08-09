import React from 'react'
import { LucideIcon, TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { cn } from '../../utils/cn'
import Card from './Card'

export interface MetricCardProps {
  title: string
  value: string | number
  subtitle?: string
  icon?: LucideIcon
  trend?: {
    value: number
    label?: string
    direction?: 'up' | 'down' | 'neutral'
  }
  variant?: 'default' | 'success' | 'warning' | 'error' | 'info'
  size?: 'sm' | 'md' | 'lg'
  loading?: boolean
  className?: string
  onClick?: () => void
}

const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  variant = 'default',
  size = 'md',
  loading = false,
  className = '',
  onClick
}) => {
  const variantClasses: Record<string, string> = {
    default: 'border-gray-200',
    success: 'border-green-200 bg-green-50',
    warning: 'border-yellow-200 bg-yellow-50',
    error: 'border-red-200 bg-red-50',
    info: 'border-blue-200 bg-blue-50'
  }

  const iconVariantClasses: Record<string, string> = {
    default: 'text-gray-600',
    success: 'text-green-600',
    warning: 'text-yellow-600',
    error: 'text-red-600',
    info: 'text-blue-600'
  }

  const sizeClasses: Record<string, string> = {
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8'
  }

  const valueSizeClasses: Record<string, string> = {
    sm: 'text-xl font-semibold',
    md: 'text-2xl font-bold',
    lg: 'text-3xl font-bold'
  }

  const getTrendIcon = () => {
    if (!trend) return null
    
    switch (trend.direction) {
      case 'up':
        return <TrendingUp className="w-4 h-4 text-green-600" />
      case 'down':
        return <TrendingDown className="w-4 h-4 text-red-600" />
      default:
        return <Minus className="w-4 h-4 text-gray-600" />
    }
  }

  const getTrendColor = () => {
    if (!trend) return 'text-gray-600'
    
    switch (trend.direction) {
      case 'up':
        return 'text-green-600'
      case 'down':
        return 'text-red-600'
      default:
        return 'text-gray-600'
    }
  }

  if (loading) {
    return (
      <Card className={cn(sizeClasses[size], variantClasses[variant], className)}>
        <div className="animate-pulse">
          <div className="flex items-center justify-between mb-2">
            <div className="h-4 bg-gray-200 rounded w-1/2"></div>
            {Icon && <div className="h-5 w-5 bg-gray-200 rounded"></div>}
          </div>
          <div className="h-8 bg-gray-200 rounded w-3/4 mb-1"></div>
          {subtitle && <div className="h-3 bg-gray-200 rounded w-1/2"></div>}
          {trend && (
            <div className="flex items-center mt-2">
              <div className="h-4 w-4 bg-gray-200 rounded mr-1"></div>
              <div className="h-3 bg-gray-200 rounded w-16"></div>
            </div>
          )}
        </div>
      </Card>
    )
  }

  const CardWrapper = onClick ? 'button' : 'div';

  return (
    <CardWrapper
      className={cn(
        'w-full text-left',
        onClick && 'cursor-pointer hover:shadow-md transition-shadow duration-200'
      )}
      onClick={onClick}
    >
      <Card
        className={cn(
          sizeClasses[size],
          variantClasses[variant],
          className
        )}
      >
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-medium text-gray-600 truncate">{title}</h3>
        {Icon && (
          <Icon className={cn('w-5 h-5', iconVariantClasses[variant])} />
        )}
      </div>
      
      <div className={cn('text-gray-900 mb-1', valueSizeClasses[size])}>
        {typeof value === 'number' ? value.toLocaleString() : value}
      </div>
      
      {subtitle && (
        <p className="text-xs text-gray-500 mb-2">{subtitle}</p>
      )}
      
      {trend && (
        <div className="flex items-center">
          {getTrendIcon()}
          <span className={cn('text-sm font-medium ml-1', getTrendColor())}>
            {trend.value > 0 ? '+' : ''}{trend.value}%
            {trend.label && (
              <span className="text-gray-500 font-normal ml-1">{trend.label}</span>
            )}
          </span>
        </div>
      )}
    </Card>
    </CardWrapper>
  )
}

export default MetricCard
