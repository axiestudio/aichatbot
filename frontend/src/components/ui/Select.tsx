import React from 'react';

export interface SelectOption {
  value: string;
  label: string;
  disabled?: boolean;
}

export interface SelectProps {
  options: SelectOption[];
  value?: string;
  placeholder?: string;
  onChange: (value: string) => void;
  className?: string;
  disabled?: boolean;
  required?: boolean;
  name?: string;
  id?: string;
}

const Select: React.FC<SelectProps> = ({
  options,
  value,
  placeholder,
  onChange,
  className = '',
  disabled = false,
  required = false,
  name,
  id
}) => {
  return (
    <select
      id={id}
      name={name}
      value={value || ''}
      onChange={(e) => onChange(e.target.value)}
      disabled={disabled}
      required={required}
      className={`
        w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm
        focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
        ${disabled ? 'bg-gray-100 cursor-not-allowed' : 'cursor-pointer'}
        ${className}
      `}
    >
      {placeholder && (
        <option value="" disabled>
          {placeholder}
        </option>
      )}
      {options.map((option) => (
        <option
          key={option.value}
          value={option.value}
          disabled={option.disabled}
        >
          {option.label}
        </option>
      ))}
    </select>
  );
};

export default Select;
