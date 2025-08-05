import React from 'react'
import Card from './ui/Card'

interface StatsCardProps {
  title: string
  value: string | number
  change?: {
    value: string | number
    type: 'increase' | 'decrease' | 'neutral'
    period?: string
  }
  description?: string
  className?: string
}

const StatsCard: React.FC<StatsCardProps> = ({
  title,
  value,
  change,
  description,
  className = ''
}) => {
  const getChangeColor = (type: 'increase' | 'decrease' | 'neutral') => {
    switch (type) {
      case 'increase':
        return 'text-green-600'
      case 'decrease':
        return 'text-red-600'
      case 'neutral':
        return 'text-gray-600'
      default:
        return 'text-gray-600'
    }
  }

  const getChangeIcon = (type: 'increase' | 'decrease' | 'neutral') => {
    switch (type) {
      case 'increase':
        return (
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 17l9.2-9.2M17 17V7H7" />
          </svg>
        )
      case 'decrease':
        return (
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 7l-9.2 9.2M7 7v10h10" />
          </svg>
        )
      case 'neutral':
        return (
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
          </svg>
        )
      default:
        return null
    }
  }

  return (
    <Card className={`hover:shadow-professional-md transition-shadow duration-200 ${className}`}>
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-medium text-gray-600 uppercase tracking-wide">
            {title}
          </h3>
        </div>
        
        <div className="space-y-2">
          <p className="text-3xl font-bold text-gray-900">
            {typeof value === 'number' ? value.toLocaleString() : value}
          </p>
          
          {change && (
            <div className="flex items-center space-x-1">
              <span className={`flex items-center text-sm font-medium ${getChangeColor(change.type)}`}>
                {getChangeIcon(change.type)}
                <span className="ml-1">
                  {typeof change.value === 'number' ? change.value.toLocaleString() : change.value}
                </span>
              </span>
              {change.period && (
                <span className="text-sm text-gray-500">
                  {change.period}
                </span>
              )}
            </div>
          )}
          
          {description && (
            <p className="text-sm text-gray-600">
              {description}
            </p>
          )}
        </div>
      </div>
    </Card>
  )
}

export default StatsCard
