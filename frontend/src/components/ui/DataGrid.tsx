import React, { useState } from 'react';
import { ChevronUp, ChevronDown } from 'lucide-react';

export interface DataGridColumn {
  key: string;
  title: string;
  width?: string;
  sortable?: boolean;
  align?: 'left' | 'center' | 'right';
  render?: (value: any, record: any) => React.ReactNode;
}

export interface DataGridProps {
  columns: DataGridColumn[];
  data: any[];
  className?: string;
  loading?: boolean;
  emptyText?: string;
  sortable?: boolean;
  onSort?: (key: string, direction: 'asc' | 'desc') => void;
}

const DataGrid: React.FC<DataGridProps> = ({
  columns,
  data,
  className = '',
  loading = false,
  emptyText = 'No data available',
  sortable = false,
  onSort
}) => {
  const [sortConfig, setSortConfig] = useState<{
    key: string;
    direction: 'asc' | 'desc';
  } | null>(null);

  const handleSort = (key: string) => {
    if (!sortable) return;
    
    let direction: 'asc' | 'desc' = 'asc';
    if (sortConfig && sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    
    setSortConfig({ key, direction });
    onSort?.(key, direction);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className={`overflow-x-auto ${className}`}>
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            {columns.map((column) => (
              <th
                key={column.key}
                className={`
                  px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider
                  ${column.align === 'center' ? 'text-center' : 
                    column.align === 'right' ? 'text-right' : 'text-left'}
                  ${sortable && column.sortable ? 'cursor-pointer hover:bg-gray-100' : ''}
                `}
                style={{ width: column.width }}
                onClick={() => column.sortable && handleSort(column.key)}
              >
                <div className="flex items-center space-x-1">
                  <span>{column.title}</span>
                  {sortable && column.sortable && (
                    <div className="flex flex-col">
                      <ChevronUp 
                        className={`w-3 h-3 ${
                          sortConfig?.key === column.key && sortConfig.direction === 'asc'
                            ? 'text-blue-600' : 'text-gray-400'
                        }`} 
                      />
                      <ChevronDown 
                        className={`w-3 h-3 -mt-1 ${
                          sortConfig?.key === column.key && sortConfig.direction === 'desc'
                            ? 'text-blue-600' : 'text-gray-400'
                        }`} 
                      />
                    </div>
                  )}
                </div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {data.length === 0 ? (
            <tr>
              <td
                colSpan={columns.length}
                className="px-6 py-4 text-center text-gray-500"
              >
                {emptyText}
              </td>
            </tr>
          ) : (
            data.map((record, index) => (
              <tr key={index} className="hover:bg-gray-50">
                {columns.map((column) => (
                  <td
                    key={column.key}
                    className={`
                      px-6 py-4 whitespace-nowrap text-sm text-gray-900
                      ${column.align === 'center' ? 'text-center' : 
                        column.align === 'right' ? 'text-right' : 'text-left'}
                    `}
                  >
                    {column.render 
                      ? column.render(record[column.key], record)
                      : record[column.key]
                    }
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
};

export default DataGrid;
