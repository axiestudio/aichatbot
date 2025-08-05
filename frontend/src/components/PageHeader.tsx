import React from 'react'
import Button from './ui/Button'

interface PageHeaderProps {
  title: string
  description?: string
  children?: React.ReactNode
  actions?: React.ReactNode
}

const PageHeader: React.FC<PageHeaderProps> = ({
  title,
  description,
  children,
  actions
}) => {
  return (
    <div className="bg-white border-b border-gray-200">
      <div className="px-6 py-6">
        <div className="flex items-center justify-between">
          <div className="flex-1 min-w-0">
            <h1 className="text-2xl font-bold text-gray-900 tracking-tight">
              {title}
            </h1>
            {description && (
              <p className="mt-2 text-sm text-gray-600 max-w-2xl">
                {description}
              </p>
            )}
            {children && (
              <div className="mt-4">
                {children}
              </div>
            )}
          </div>
          
          {actions && (
            <div className="flex items-center space-x-3 ml-6">
              {actions}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default PageHeader
