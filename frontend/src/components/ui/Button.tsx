import React from 'react'

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost' | 'outline'
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl'
  loading?: boolean
  fullWidth?: boolean
  children: React.ReactNode
}

const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  loading = false,
  fullWidth = false,
  disabled,
  children,
  className = '',
  ...props
}) => {
  const baseClasses = `
    inline-flex items-center justify-center font-medium transition-all duration-200
    focus:outline-none focus:ring-2 focus:ring-offset-2
    disabled:opacity-50 disabled:cursor-not-allowed
    ${fullWidth ? 'w-full' : ''}
  `

  const variantClasses = {
    primary: `
      bg-blue-600 text-white border border-blue-600
      hover:bg-blue-700 hover:border-blue-700 active:bg-blue-800
      focus:ring-blue-500 shadow-sm hover:shadow-md
    `,
    secondary: `
      bg-white text-gray-700 border border-gray-300
      hover:bg-gray-50 hover:border-gray-400 active:bg-gray-100
      focus:ring-gray-500 shadow-sm hover:shadow-md
    `,
    outline: `
      bg-transparent text-blue-600 border border-blue-600
      hover:bg-blue-50 hover:border-blue-700 active:bg-blue-100
      focus:ring-blue-500
    `,
    danger: `
      bg-red-600 text-white border border-red-600
      hover:bg-red-700 hover:border-red-700 active:bg-red-800
      focus:ring-red-500 shadow-sm hover:shadow-md
    `,
    ghost: `
      bg-transparent text-gray-700 border border-transparent
      hover:bg-gray-100 active:bg-gray-200
      focus:ring-gray-500
    `
  }

  const sizeClasses = {
    xs: 'px-2.5 py-1.5 text-xs rounded-md',
    sm: 'px-3 py-2 text-sm rounded-md',
    md: 'px-4 py-2.5 text-sm rounded-lg',
    lg: 'px-6 py-3 text-base rounded-lg',
    xl: 'px-8 py-4 text-lg rounded-xl'
  }

  const classes = `${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${className}`.trim()

  return (
    <button
      className={classes}
      disabled={disabled || loading}
      {...props}
    >
      {loading && (
        <div className="w-4 h-4 mr-2 border-2 border-current border-t-transparent rounded-full animate-spin" />
      )}
      {children}
    </button>
  )
}

export default Button
