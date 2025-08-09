import React from 'react';

export interface SkeletonProps {
  width?: string | number;
  height?: string | number;
  className?: string;
  variant?: 'text' | 'rectangular' | 'circular';
  animation?: 'pulse' | 'wave' | 'none';
}

const Skeleton: React.FC<SkeletonProps> = ({
  width,
  height,
  className = '',
  variant = 'text',
  animation = 'pulse'
}) => {
  const getVariantClasses = () => {
    switch (variant) {
      case 'circular':
        return 'rounded-full';
      case 'rectangular':
        return 'rounded';
      default:
        return 'rounded';
    }
  };

  const getAnimationClasses = () => {
    switch (animation) {
      case 'wave':
        return 'animate-pulse bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 bg-[length:200%_100%] animate-[wave_1.5s_ease-in-out_infinite]';
      case 'none':
        return 'bg-gray-200';
      default:
        return 'animate-pulse bg-gray-200';
    }
  };

  const getDefaultDimensions = () => {
    if (variant === 'text') {
      return {
        width: width || '100%',
        height: height || '1rem'
      };
    }
    return {
      width: width || '100%',
      height: height || '2rem'
    };
  };

  const dimensions = getDefaultDimensions();

  return (
    <div
      className={`
        ${getVariantClasses()}
        ${getAnimationClasses()}
        ${className}
      `}
      style={{
        width: dimensions.width,
        height: dimensions.height
      }}
      role="status"
      aria-label="Loading content"
    >
      <span className="sr-only">Loading...</span>
    </div>
  );
};

export default Skeleton;
