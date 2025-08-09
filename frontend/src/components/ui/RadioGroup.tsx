import React from 'react';

export interface RadioOption {
  value: string;
  label: string;
  disabled?: boolean;
}

export interface RadioGroupProps {
  options: RadioOption[];
  value?: string;
  onChange: (value: string) => void;
  name: string;
  className?: string;
  disabled?: boolean;
  required?: boolean;
}

const RadioGroup: React.FC<RadioGroupProps> = ({
  options,
  value,
  onChange,
  name,
  className = '',
  disabled = false,
  required = false
}) => {
  return (
    <div className={`space-y-2 ${className}`}>
      {options.map((option) => (
        <div key={option.value} className="flex items-center">
          <input
            type="radio"
            id={`${name}-${option.value}`}
            name={name}
            value={option.value}
            checked={value === option.value}
            onChange={(e) => onChange(e.target.value)}
            disabled={disabled || option.disabled}
            required={required}
            className={`
              w-4 h-4 text-blue-600 border-gray-300 
              focus:ring-blue-500 focus:ring-2
              ${disabled || option.disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
            `}
          />
          <label
            htmlFor={`${name}-${option.value}`}
            className={`
              ml-2 text-sm text-gray-700
              ${disabled || option.disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
            `}
          >
            {option.label}
          </label>
        </div>
      ))}
    </div>
  );
};

export default RadioGroup;
