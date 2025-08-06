import React, { useState } from 'react'
import { Settings, Shield, Users, Database, Bell, Lock } from 'lucide-react'
import Card from '../ui/Card'
import Button from '../ui/Button'

const SuperAdminSettings: React.FC = () => {
  const [activeTab, setActiveTab] = useState('general')

  const tabs = [
    { id: 'general', name: 'General', icon: Settings },
    { id: 'security', name: 'Security', icon: Shield },
    { id: 'users', name: 'Super Admins', icon: Users },
    { id: 'system', name: 'System', icon: Database },
    { id: 'notifications', name: 'Notifications', icon: Bell }
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Super Admin Settings</h1>
        <p className="text-gray-600">Configure platform-wide settings and preferences</p>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => {
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                  activeTab === tab.id
                    ? 'border-purple-500 text-purple-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.name}</span>
              </button>
            )
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="space-y-6">
        {activeTab === 'general' && (
          <Card className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">General Settings</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Platform Name
                </label>
                <input
                  type="text"
                  defaultValue="AI Chatbot Platform"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Default Instance Limit
                </label>
                <input
                  type="number"
                  defaultValue="1000"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                />
              </div>
              <Button>Save Changes</Button>
            </div>
          </Card>
        )}

        {activeTab === 'security' && (
          <Card className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Security Settings</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="font-medium text-gray-900">Two-Factor Authentication</h4>
                  <p className="text-sm text-gray-600">Require 2FA for all super admin accounts</p>
                </div>
                <input type="checkbox" className="rounded" />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="font-medium text-gray-900">Session Timeout</h4>
                  <p className="text-sm text-gray-600">Auto-logout after inactivity</p>
                </div>
                <select className="px-3 py-2 border border-gray-300 rounded-lg">
                  <option>30 minutes</option>
                  <option>1 hour</option>
                  <option>4 hours</option>
                  <option>8 hours</option>
                </select>
              </div>
              <Button>Update Security</Button>
            </div>
          </Card>
        )}

        {activeTab === 'users' && (
          <Card className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Super Admin Users</h3>
              <Button>Add Super Admin</Button>
            </div>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div>
                  <h4 className="font-medium text-gray-900">John Doe</h4>
                  <p className="text-sm text-gray-600">john@company.com</p>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded">Active</span>
                  <Button size="sm" variant="outline">Edit</Button>
                </div>
              </div>
            </div>
          </Card>
        )}

        {activeTab === 'system' && (
          <Card className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">System Configuration</h3>
            <div className="space-y-4">
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Database Status</h4>
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  <span className="text-sm text-gray-600">Connected and healthy</span>
                </div>
              </div>
              <div>
                <h4 className="font-medium text-gray-900 mb-2">System Maintenance</h4>
                <Button variant="outline">Schedule Maintenance</Button>
              </div>
            </div>
          </Card>
        )}

        {activeTab === 'notifications' && (
          <Card className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Notification Settings</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="font-medium text-gray-900">Usage Alerts</h4>
                  <p className="text-sm text-gray-600">Get notified when instances approach limits</p>
                </div>
                <input type="checkbox" defaultChecked className="rounded" />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="font-medium text-gray-900">Revenue Reports</h4>
                  <p className="text-sm text-gray-600">Weekly revenue summary emails</p>
                </div>
                <input type="checkbox" defaultChecked className="rounded" />
              </div>
              <Button>Save Preferences</Button>
            </div>
          </Card>
        )}
      </div>
    </div>
  )
}

export default SuperAdminSettings
