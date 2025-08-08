/**
 * Enterprise UI Component Library - Centralized exports
 * 
 * This file provides a single entry point for all UI components,
 * making imports cleaner and more maintainable across the application.
 */

// Core UI Components
export { default as Button } from './Button'
export { default as Card } from './Card'
export { default as Badge } from './Badge'
export { default as Input } from './Input'
export { ProgressBar } from './ProgressBar'

// Layout Components
export { default as Modal } from './Modal'
export { default as Tooltip } from './Tooltip'
export { default as Dropdown } from './Dropdown'

// Form Components
export { default as Select } from './Select'
export { default as Checkbox } from './Checkbox'
export { default as RadioGroup } from './RadioGroup'
export { default as Switch } from './Switch'

// Data Display Components
export { default as Table } from './Table'
export { default as DataGrid } from './DataGrid'
export { default as Chart } from './Chart'
export { default as Metric } from './Metric'

// Feedback Components
export { default as Alert } from './Alert'
export { default as Toast } from './Toast'
export { default as LoadingSpinner } from './LoadingSpinner'
export { default as Skeleton } from './Skeleton'

// Navigation Components
export { default as Tabs } from './Tabs'
export { default as Breadcrumb } from './Breadcrumb'
export { default as Pagination } from './Pagination'

// Enterprise Components
export { default as StatusIndicator } from './StatusIndicator'
export { default as MetricCard } from './MetricCard'
export { default as DashboardWidget } from './DashboardWidget'

// Types
export type { ButtonProps } from './Button'
export type { CardProps } from './Card'
export type { BadgeProps } from './Badge'
export type { InputProps } from './Input'
export type { ProgressBarProps } from './ProgressBar'

// Design System Constants
export const DESIGN_TOKENS = {
  colors: {
    primary: {
      50: '#eff6ff',
      100: '#dbeafe',
      500: '#3b82f6',
      600: '#2563eb',
      700: '#1d4ed8',
      900: '#1e3a8a',
    },
    gray: {
      50: '#f9fafb',
      100: '#f3f4f6',
      200: '#e5e7eb',
      300: '#d1d5db',
      400: '#9ca3af',
      500: '#6b7280',
      600: '#4b5563',
      700: '#374151',
      800: '#1f2937',
      900: '#111827',
    },
    success: {
      50: '#ecfdf5',
      100: '#d1fae5',
      500: '#10b981',
      600: '#059669',
      700: '#047857',
    },
    warning: {
      50: '#fffbeb',
      100: '#fef3c7',
      500: '#f59e0b',
      600: '#d97706',
      700: '#b45309',
    },
    error: {
      50: '#fef2f2',
      100: '#fee2e2',
      500: '#ef4444',
      600: '#dc2626',
      700: '#b91c1c',
    },
  },
  spacing: {
    xs: '0.25rem',
    sm: '0.5rem',
    md: '1rem',
    lg: '1.5rem',
    xl: '2rem',
    '2xl': '3rem',
    '3xl': '4rem',
  },
  borderRadius: {
    none: '0',
    sm: '0.125rem',
    md: '0.375rem',
    lg: '0.5rem',
    xl: '0.75rem',
    '2xl': '1rem',
    full: '9999px',
  },
  shadows: {
    sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
    md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
    lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
    xl: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
  },
  typography: {
    fontFamily: {
      sans: ['Inter', 'system-ui', 'sans-serif'],
      mono: ['JetBrains Mono', 'monospace'],
    },
    fontSize: {
      xs: ['0.75rem', { lineHeight: '1rem' }],
      sm: ['0.875rem', { lineHeight: '1.25rem' }],
      base: ['1rem', { lineHeight: '1.5rem' }],
      lg: ['1.125rem', { lineHeight: '1.75rem' }],
      xl: ['1.25rem', { lineHeight: '1.75rem' }],
      '2xl': ['1.5rem', { lineHeight: '2rem' }],
      '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
      '4xl': ['2.25rem', { lineHeight: '2.5rem' }],
    },
    fontWeight: {
      normal: '400',
      medium: '500',
      semibold: '600',
      bold: '700',
    },
  },
  animation: {
    duration: {
      fast: '150ms',
      normal: '200ms',
      slow: '300ms',
    },
    easing: {
      ease: 'cubic-bezier(0.4, 0, 0.2, 1)',
      easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
      easeOut: 'cubic-bezier(0, 0, 0.2, 1)',
      easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
    },
  },
} as const

// Component Size Variants
export const SIZE_VARIANTS = {
  xs: 'xs',
  sm: 'sm',
  md: 'md',
  lg: 'lg',
  xl: 'xl',
} as const

// Component Color Variants
export const COLOR_VARIANTS = {
  primary: 'primary',
  secondary: 'secondary',
  success: 'success',
  warning: 'warning',
  error: 'error',
  gray: 'gray',
} as const

// Component State Variants
export const STATE_VARIANTS = {
  default: 'default',
  hover: 'hover',
  active: 'active',
  disabled: 'disabled',
  loading: 'loading',
} as const

// Utility function for consistent class name generation
export const createVariantClasses = (
  base: string,
  variants: Record<string, string>,
  defaultVariant: string = 'default'
) => {
  return (variant: string = defaultVariant) => {
    return `${base} ${variants[variant] || variants[defaultVariant]}`
  }
}

// Common component patterns
export const COMMON_PATTERNS = {
  // Focus ring for accessibility
  focusRing: 'focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500',
  
  // Transition for smooth interactions
  transition: 'transition-all duration-200 ease-in-out',
  
  // Disabled state
  disabled: 'disabled:opacity-50 disabled:cursor-not-allowed',
  
  // Loading state
  loading: 'cursor-wait opacity-75',
  
  // Interactive element
  interactive: 'cursor-pointer hover:opacity-80 active:opacity-90',
  
  // Card shadow
  cardShadow: 'shadow-sm hover:shadow-md transition-shadow duration-200',
  
  // Border
  border: 'border border-gray-200',
  
  // Rounded corners
  rounded: 'rounded-lg',
  
  // Flex center
  flexCenter: 'flex items-center justify-center',
  
  // Text truncate
  truncate: 'truncate',
  
  // Screen reader only
  srOnly: 'sr-only',
} as const

// Responsive breakpoints
export const BREAKPOINTS = {
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  '2xl': '1536px',
} as const

// Z-index scale
export const Z_INDEX = {
  dropdown: 1000,
  sticky: 1020,
  fixed: 1030,
  modalBackdrop: 1040,
  modal: 1050,
  popover: 1060,
  tooltip: 1070,
  toast: 1080,
} as const
