import React from 'react';

export interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  color?: 'primary' | 'secondary' | 'white' | 'gray';
  className?: string;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'md',
  color = 'primary',
  className = ''
}) => {
  const getSizeClasses = () => {
    switch (size) {
      case 'sm':
        return 'w-4 h-4';
      case 'lg':
        return 'w-8 h-8';
      case 'xl':
        return 'w-12 h-12';
      default:
        return 'w-6 h-6';
    }
  };

  const getColorClasses = () => {
    switch (color) {
      case 'secondary':
        return 'border-gray-300 border-t-gray-600';
      case 'white':
        return 'border-white/30 border-t-white';
      case 'gray':
        return 'border-gray-200 border-t-gray-500';
      default:
        return 'border-blue-200 border-t-blue-600';
    }
  };

  return (
    <div
      className={`
        animate-spin rounded-full border-2 ${getSizeClasses()} ${getColorClasses()} ${className}
      `}
      role="status"
      aria-label="Loading"
    >
      <span className="sr-only">Loading...</span>
    </div>
  );
};

export default LoadingSpinner;
