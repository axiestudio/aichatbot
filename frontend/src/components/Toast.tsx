import React from 'react'
import { toast } from 'react-hot-toast'
import { CheckCircle, XCircle, AlertCircle, Info } from 'lucide-react'

export const showToast = {
  success: (message: string) => {
    toast.success(message, {
      icon: <CheckCircle className="w-5 h-5" />,
      style: {
        background: '#10b981',
        color: '#fff',
      },
    })
  },
  
  error: (message: string) => {
    toast.error(message, {
      icon: <XCircle className="w-5 h-5" />,
      style: {
        background: '#ef4444',
        color: '#fff',
      },
    })
  },
  
  warning: (message: string) => {
    toast(message, {
      icon: <AlertCircle className="w-5 h-5" />,
      style: {
        background: '#f59e0b',
        color: '#fff',
      },
    })
  },
  
  info: (message: string) => {
    toast(message, {
      icon: <Info className="w-5 h-5" />,
      style: {
        background: '#3b82f6',
        color: '#fff',
      },
    })
  },
}

export default showToast
