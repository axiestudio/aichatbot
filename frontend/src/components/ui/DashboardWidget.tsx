import React from 'react'
import { LucideIcon, MoreVertical, RefreshCw } from 'lucide-react'
import { cn } from '../../utils/cn'
import Card from './Card'
import Button from './Button'

export interface DashboardWidgetProps {
  title: string
  subtitle?: string
  icon?: LucideIcon
  children: React.ReactNode
  actions?: Array<{
    label: string
    onClick: () => void
    icon?: LucideIcon
  }>
  loading?: boolean
  error?: string
  onRefresh?: () => void
  className?: string
  headerClassName?: string
  contentClassName?: string
}

const DashboardWidget: React.FC<DashboardWidgetProps> = ({
  title,
  subtitle,
  icon: Icon,
  children,
  actions = [],
  loading = false,
  error,
  onRefresh,
  className,
  headerClassName,
  contentClassName
}) => {
  return (
    <Card className={cn('overflow-hidden', className)}>
      {/* Header */}
      <div className={cn(
        'flex items-center justify-between p-6 border-b border-gray-200',
        headerClassName
      )}>
        <div className="flex items-center space-x-3">
          {Icon && (
            <div className="flex-shrink-0">
              <Icon className="w-5 h-5 text-gray-600" />
            </div>
          )}
          <div>
            <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
            {subtitle && (
              <p className="text-sm text-gray-500">{subtitle}</p>
            )}
          </div>
        </div>

        <div className="flex items-center space-x-2">
          {onRefresh && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onRefresh}
              disabled={loading}
              className="p-2"
            >
              <RefreshCw className={cn(
                'w-4 h-4',
                loading && 'animate-spin'
              )} />
            </Button>
          )}

          {actions.length > 0 && (
            <div className="relative">
              <Button
                variant="ghost"
                size="sm"
                className="p-2"
              >
                <MoreVertical className="w-4 h-4" />
              </Button>
              {/* TODO: Add dropdown menu for actions */}
            </div>
          )}
        </div>
      </div>

      {/* Content */}
      <div className={cn('p-6', contentClassName)}>
        {loading ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        ) : error ? (
          <div className="flex flex-col items-center justify-center py-8 text-center">
            <div className="text-red-500 mb-2">
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <p className="text-sm text-gray-600">{error}</p>
            {onRefresh && (
              <Button
                variant="outline"
                size="sm"
                onClick={onRefresh}
                className="mt-3"
              >
                Try Again
              </Button>
            )}
          </div>
        ) : (
          children
        )}
      </div>
    </Card>
  )
}

export default DashboardWidget
