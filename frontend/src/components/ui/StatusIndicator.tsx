import React from 'react'
import { CheckCircle, XCircle, AlertTriangle, Clock, Minus } from 'lucide-react'
import { cn } from '../../utils/cn'

export interface StatusIndicatorProps {
  status: 'healthy' | 'unhealthy' | 'warning' | 'pending' | 'unknown'
  label?: string
  size?: 'sm' | 'md' | 'lg'
  showIcon?: boolean
  showLabel?: boolean
  className?: string
}

const StatusIndicator: React.FC<StatusIndicatorProps> = ({
  status,
  label,
  size = 'md',
  showIcon = true,
  showLabel = true,
  className
}) => {
  const statusConfig = {
    healthy: {
      icon: CheckCircle,
      color: 'text-green-600',
      bgColor: 'bg-green-100',
      borderColor: 'border-green-200',
      label: label || 'Healthy'
    },
    unhealthy: {
      icon: XCircle,
      color: 'text-red-600',
      bgColor: 'bg-red-100',
      borderColor: 'border-red-200',
      label: label || 'Unhealthy'
    },
    warning: {
      icon: AlertTriangle,
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-100',
      borderColor: 'border-yellow-200',
      label: label || 'Warning'
    },
    pending: {
      icon: Clock,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
      borderColor: 'border-blue-200',
      label: label || 'Pending'
    },
    unknown: {
      icon: Minus,
      color: 'text-gray-600',
      bgColor: 'bg-gray-100',
      borderColor: 'border-gray-200',
      label: label || 'Unknown'
    }
  }

  const sizeClasses = {
    sm: {
      container: 'px-2 py-1 text-xs',
      icon: 'w-3 h-3',
      spacing: 'gap-1'
    },
    md: {
      container: 'px-3 py-1.5 text-sm',
      icon: 'w-4 h-4',
      spacing: 'gap-1.5'
    },
    lg: {
      container: 'px-4 py-2 text-base',
      icon: 'w-5 h-5',
      spacing: 'gap-2'
    }
  }

  const config = statusConfig[status]
  const sizeConfig = sizeClasses[size]
  const Icon = config.icon

  return (
    <div
      className={cn(
        'inline-flex items-center rounded-full border font-medium',
        config.bgColor,
        config.borderColor,
        sizeConfig.container,
        sizeConfig.spacing,
        className
      )}
    >
      {showIcon && (
        <Icon className={cn(config.color, sizeConfig.icon)} />
      )}
      {showLabel && (
        <span className={config.color}>
          {config.label}
        </span>
      )}
    </div>
  )
}

export default StatusIndicator
