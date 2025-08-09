import React, { useState } from 'react';

export interface TabItem {
  id: string;
  label: string;
  content: React.ReactNode;
  disabled?: boolean;
}

export interface TabsProps {
  items: TabItem[];
  defaultActiveTab?: string;
  onChange?: (tabId: string) => void;
  className?: string;
  variant?: 'default' | 'pills' | 'underline';
}

const Tabs: React.FC<TabsProps> = ({
  items,
  defaultActiveTab,
  onChange,
  className = '',
  variant = 'default'
}) => {
  const [activeTab, setActiveTab] = useState(defaultActiveTab || items[0]?.id);

  const handleTabChange = (tabId: string) => {
    setActiveTab(tabId);
    onChange?.(tabId);
  };

  const getTabClasses = (item: TabItem, isActive: boolean) => {
    const baseClasses = 'px-4 py-2 text-sm font-medium transition-colors duration-200';
    
    if (item.disabled) {
      return `${baseClasses} text-gray-400 cursor-not-allowed`;
    }

    switch (variant) {
      case 'pills':
        return `${baseClasses} rounded-lg ${
          isActive 
            ? 'bg-blue-600 text-white' 
            : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
        }`;
      case 'underline':
        return `${baseClasses} border-b-2 ${
          isActive 
            ? 'border-blue-600 text-blue-600' 
            : 'border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300'
        }`;
      default:
        return `${baseClasses} border border-gray-300 ${
          isActive 
            ? 'bg-white text-blue-600 border-blue-600' 
            : 'bg-gray-50 text-gray-600 hover:text-gray-900 hover:bg-gray-100'
        } ${items.indexOf(item) === 0 ? 'rounded-l-lg' : ''} ${
          items.indexOf(item) === items.length - 1 ? 'rounded-r-lg' : ''
        }`;
    }
  };

  const activeItem = items.find(item => item.id === activeTab);

  return (
    <div className={className}>
      <div className={`flex ${variant === 'pills' ? 'space-x-1' : ''}`}>
        {items.map((item) => (
          <button
            key={item.id}
            onClick={() => !item.disabled && handleTabChange(item.id)}
            disabled={item.disabled}
            className={getTabClasses(item, activeTab === item.id)}
          >
            {item.label}
          </button>
        ))}
      </div>
      
      <div className="mt-4">
        {activeItem?.content}
      </div>
    </div>
  );
};

export default Tabs;
