import React, { useState, useEffect } from 'react'
import { Routes, Route, Link, useNavigate } from 'react-router-dom'
import { 
  Plus, 
  Search, 
  Filter, 
  MoreVertical, 
  Building2, 
  Users, 
  Activity, 
  Settings,
  Trash2,
  Edit,
  ExternalLink,
  Crown,
  AlertTriangle
} from 'lucide-react'
import Card from '../ui/Card'
import Button from '../ui/Button'
import Badge from '../ui/Badge'

interface ChatInstance {
  id: string
  name: string
  subdomain: string
  domain?: string
  description: string
  owner_email: string
  owner_name: string
  is_active: boolean
  max_monthly_messages: number
  current_monthly_messages: number
  plan_type: string
  primary_color: string
  secondary_color: string
  created_at: string
  updated_at: string
}

const InstanceManagement: React.FC = () => {
  const [instances, setInstances] = useState<ChatInstance[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterPlan, setFilterPlan] = useState('all')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    loadInstances()
  }, [])

  const loadInstances = async () => {
    try {
      const response = await fetch('/api/v1/super-admin/instances/', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('superAdminToken')}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setInstances(data)
      }
    } catch (error) {
      console.error('Failed to load instances:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const filteredInstances = instances.filter(instance => {
    const matchesSearch = instance.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         instance.subdomain.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         instance.owner_email.toLowerCase().includes(searchTerm.toLowerCase())
    
    const matchesPlan = filterPlan === 'all' || instance.plan_type === filterPlan
    
    return matchesSearch && matchesPlan
  })

  const getPlanBadgeVariant = (plan: string) => {
    switch (plan) {
      case 'enterprise': return 'default'
      case 'pro': return 'info'
      case 'free': return 'warning'
      default: return 'default'
    }
  }

  const getUsageColor = (percentage: number) => {
    if (percentage >= 90) return 'text-red-600'
    if (percentage >= 75) return 'text-yellow-600'
    return 'text-green-600'
  }

  const handleDeleteInstance = async (instanceId: string) => {
    if (!confirm('Are you sure you want to delete this instance? This action cannot be undone.')) {
      return
    }

    try {
      const response = await fetch(`/api/v1/super-admin/instances/${instanceId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('superAdminToken')}`
        }
      })

      if (response.ok) {
        setInstances(instances.filter(i => i.id !== instanceId))
      }
    } catch (error) {
      console.error('Failed to delete instance:', error)
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Instance Management</h1>
          <p className="text-gray-600">Manage all chat instances across the platform</p>
        </div>
        <Button 
          onClick={() => setShowCreateModal(true)}
          className="flex items-center space-x-2"
        >
          <Plus className="w-4 h-4" />
          <span>Create Instance</span>
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Instances</p>
              <p className="text-2xl font-bold text-gray-900">{instances.length}</p>
            </div>
            <Building2 className="w-8 h-8 text-blue-600" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Instances</p>
              <p className="text-2xl font-bold text-green-600">
                {instances.filter(i => i.is_active).length}
              </p>
            </div>
            <Activity className="w-8 h-8 text-green-600" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Enterprise Plans</p>
              <p className="text-2xl font-bold text-purple-600">
                {instances.filter(i => i.plan_type === 'enterprise').length}
              </p>
            </div>
            <Crown className="w-8 h-8 text-purple-600" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">High Usage</p>
              <p className="text-2xl font-bold text-orange-600">
                {instances.filter(i => (i.current_monthly_messages / i.max_monthly_messages) > 0.8).length}
              </p>
            </div>
            <AlertTriangle className="w-8 h-8 text-orange-600" />
          </div>
        </Card>
      </div>

      {/* Filters */}
      <Card className="p-6">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
          <div className="flex items-center space-x-4">
            <div className="relative">
              <Search className="w-5 h-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Search instances..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>

            <select
              value={filterPlan}
              onChange={(e) => setFilterPlan(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              <option value="all">All Plans</option>
              <option value="free">Free</option>
              <option value="pro">Professional</option>
              <option value="enterprise">Enterprise</option>
            </select>
          </div>

          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-600">
              Showing {filteredInstances.length} of {instances.length} instances
            </span>
          </div>
        </div>
      </Card>

      {/* Instances Table */}
      <Card className="overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Instance
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Owner
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Plan
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Usage
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredInstances.map((instance) => {
                const usagePercentage = (instance.current_monthly_messages / instance.max_monthly_messages) * 100
                
                return (
                  <tr key={instance.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">{instance.name}</div>
                        <div className="text-sm text-gray-500">{instance.subdomain}.chatbot.com</div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">{instance.owner_name}</div>
                        <div className="text-sm text-gray-500">{instance.owner_email}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <Badge variant={getPlanBadgeVariant(instance.plan_type)}>
                        {instance.plan_type.toUpperCase()}
                      </Badge>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className={`text-sm font-medium ${getUsageColor(usagePercentage)}`}>
                          {instance.current_monthly_messages.toLocaleString()} / {instance.max_monthly_messages.toLocaleString()}
                        </div>
                        <div className="text-sm text-gray-500">
                          {usagePercentage.toFixed(1)}% used
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <Badge variant={instance.is_active ? 'success' : 'error'}>
                        {instance.is_active ? 'Active' : 'Inactive'}
                      </Badge>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex items-center space-x-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => window.open(`https://${instance.subdomain}.chatbot.com`, '_blank')}
                        >
                          <ExternalLink className="w-4 h-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => navigate(`/super-admin/instances/${instance.id}`)}
                        >
                          <Settings className="w-4 h-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleDeleteInstance(instance.id)}
                          className="text-red-600 hover:text-red-700"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Create Instance Modal would go here */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">Create New Instance</h3>
            <p className="text-gray-600 mb-4">Instance creation form would go here...</p>
            <div className="flex justify-end space-x-2">
              <Button variant="outline" onClick={() => setShowCreateModal(false)}>
                Cancel
              </Button>
              <Button onClick={() => setShowCreateModal(false)}>
                Create
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default InstanceManagement
