import React, { useState, useEffect } from 'react'
import { 
  Activity, 
  Server, 
  Database, 
  Wifi, 
  AlertTriangle, 
  CheckCircle, 
  XCircle,
  TrendingUp,
  TrendingDown,
  RefreshCw,
  Clock,
  Cpu,
  HardDrive,
  MemoryStick
} from 'lucide-react'
import Card from '../ui/Card'
import Button from '../ui/Button'
import Badge from '../ui/Badge'

interface SystemHealth {
  status: string
  timestamp: string
  uptime_seconds: number
  version: string
  environment: string
  checks: {
    database: any
    redis: any
    system_resources: any
    websocket: any
    external_apis: any
    security: any
    performance: any
  }
}

interface PerformanceMetrics {
  timestamp: string
  active_requests: number
  system_resources: {
    cpu_percent: number
    memory_percent: number
    disk_percent: number
    process_memory_mb: number
  }
  counters: Record<string, number>
  cache_stats: {
    hits: number
    misses: number
    hit_rate_percent: number
    total_requests: number
  }
}

const SystemMonitoring: React.FC = () => {
  const [health, setHealth] = useState<SystemHealth | null>(null)
  const [performance, setPerformance] = useState<PerformanceMetrics | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date())

  useEffect(() => {
    loadSystemData()
    
    let interval: NodeJS.Timeout
    if (autoRefresh) {
      interval = setInterval(loadSystemData, 30000) // Refresh every 30 seconds
    }
    
    return () => {
      if (interval) clearInterval(interval)
    }
  }, [autoRefresh])

  const loadSystemData = async () => {
    try {
      const token = localStorage.getItem('adminToken')
      
      const [healthResponse, performanceResponse] = await Promise.all([
        fetch('/api/v1/health/detailed', {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch('/api/v1/health/metrics', {
          headers: { 'Authorization': `Bearer ${token}` }
        })
      ])

      if (healthResponse.ok) {
        const healthData = await healthResponse.json()
        setHealth(healthData)
      }

      if (performanceResponse.ok) {
        const performanceData = await performanceResponse.json()
        setPerformance(performanceData)
      }

      setLastUpdate(new Date())
    } catch (error) {
      console.error('Failed to load system data:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="w-5 h-5 text-green-500" />
      case 'degraded':
        return <AlertTriangle className="w-5 h-5 text-yellow-500" />
      case 'critical':
        return <XCircle className="w-5 h-5 text-red-500" />
      default:
        return <Activity className="w-5 h-5 text-gray-500" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'success'
      case 'degraded': return 'warning'
      case 'critical': return 'error'
      default: return 'default'
    }
  }

  const formatUptime = (seconds: number) => {
    const days = Math.floor(seconds / 86400)
    const hours = Math.floor((seconds % 86400) / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    
    if (days > 0) {
      return `${days}d ${hours}h ${minutes}m`
    } else if (hours > 0) {
      return `${hours}h ${minutes}m`
    } else {
      return `${minutes}m`
    }
  }

  const formatBytes = (bytes: number) => {
    const sizes = ['B', 'KB', 'MB', 'GB']
    if (bytes === 0) return '0 B'
    const i = Math.floor(Math.log(bytes) / Math.log(1024))
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">System Monitoring</h1>
          <p className="text-gray-600">Real-time system health and performance metrics</p>
        </div>
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2 text-sm text-gray-500">
            <Clock className="w-4 h-4" />
            <span>Last updated: {lastUpdate.toLocaleTimeString()}</span>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={autoRefresh ? 'bg-green-50 border-green-200' : ''}
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${autoRefresh ? 'animate-spin' : ''}`} />
            Auto Refresh
          </Button>
          <Button size="sm" onClick={loadSystemData}>
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh Now
          </Button>
        </div>
      </div>

      {/* Overall Status */}
      {health && (
        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              {getStatusIcon(health.status)}
              <div>
                <h3 className="text-lg font-semibold text-gray-900">System Status</h3>
                <p className="text-gray-600">Overall system health: {health.status}</p>
              </div>
            </div>
            <Badge variant={getStatusColor(health.status)}>
              {health.status.toUpperCase()}
            </Badge>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">
                {formatUptime(health.uptime_seconds)}
              </div>
              <div className="text-sm text-gray-500">Uptime</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">{health.version}</div>
              <div className="text-sm text-gray-500">Version</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">{health.environment}</div>
              <div className="text-sm text-gray-500">Environment</div>
            </div>
          </div>
        </Card>
      )}

      {/* System Resources */}
      {performance && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">CPU Usage</p>
                <p className="text-2xl font-bold text-gray-900">
                  {performance.system_resources.cpu_percent.toFixed(1)}%
                </p>
              </div>
              <Cpu className="w-8 h-8 text-blue-600" />
            </div>
            <div className="mt-2">
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className={`h-2 rounded-full ${
                    performance.system_resources.cpu_percent > 80 ? 'bg-red-500' :
                    performance.system_resources.cpu_percent > 60 ? 'bg-yellow-500' : 'bg-green-500'
                  }`}
                  style={{ width: `${Math.min(performance.system_resources.cpu_percent, 100)}%` }}
                ></div>
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Memory Usage</p>
                <p className="text-2xl font-bold text-gray-900">
                  {performance.system_resources.memory_percent.toFixed(1)}%
                </p>
              </div>
              <MemoryStick className="w-8 h-8 text-green-600" />
            </div>
            <div className="mt-2">
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className={`h-2 rounded-full ${
                    performance.system_resources.memory_percent > 80 ? 'bg-red-500' :
                    performance.system_resources.memory_percent > 60 ? 'bg-yellow-500' : 'bg-green-500'
                  }`}
                  style={{ width: `${Math.min(performance.system_resources.memory_percent, 100)}%` }}
                ></div>
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Disk Usage</p>
                <p className="text-2xl font-bold text-gray-900">
                  {performance.system_resources.disk_percent.toFixed(1)}%
                </p>
              </div>
              <HardDrive className="w-8 h-8 text-purple-600" />
            </div>
            <div className="mt-2">
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className={`h-2 rounded-full ${
                    performance.system_resources.disk_percent > 80 ? 'bg-red-500' :
                    performance.system_resources.disk_percent > 60 ? 'bg-yellow-500' : 'bg-green-500'
                  }`}
                  style={{ width: `${Math.min(performance.system_resources.disk_percent, 100)}%` }}
                ></div>
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Active Requests</p>
                <p className="text-2xl font-bold text-gray-900">
                  {performance.active_requests}
                </p>
              </div>
              <Activity className="w-8 h-8 text-orange-600" />
            </div>
            <div className="mt-2">
              <p className="text-sm text-gray-500">
                Process Memory: {formatBytes(performance.system_resources.process_memory_mb * 1024 * 1024)}
              </p>
            </div>
          </Card>
        </div>
      )}

      {/* Service Health Checks */}
      {health && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {Object.entries(health.checks).map(([service, check]) => (
            <Card key={service} className="p-6">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-2">
                  {service === 'database' && <Database className="w-5 h-5" />}
                  {service === 'redis' && <Server className="w-5 h-5" />}
                  {service === 'websocket' && <Wifi className="w-5 h-5" />}
                  {!['database', 'redis', 'websocket'].includes(service) && <Activity className="w-5 h-5" />}
                  <h4 className="font-medium text-gray-900 capitalize">{service.replace('_', ' ')}</h4>
                </div>
                <Badge variant={getStatusColor(check.status)}>
                  {check.status}
                </Badge>
              </div>
              
              <div className="space-y-2 text-sm">
                {check.response_time_ms && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">Response Time:</span>
                    <span className="font-medium">{check.response_time_ms}ms</span>
                  </div>
                )}
                {check.total_connections && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">Connections:</span>
                    <span className="font-medium">{check.total_connections}</span>
                  </div>
                )}
                {check.error && (
                  <div className="text-red-600 text-xs">{check.error}</div>
                )}
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Cache Performance */}
      {performance?.cache_stats && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Cache Performance</h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {performance.cache_stats.hit_rate_percent.toFixed(1)}%
              </div>
              <div className="text-sm text-gray-500">Hit Rate</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {performance.cache_stats.hits.toLocaleString()}
              </div>
              <div className="text-sm text-gray-500">Cache Hits</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">
                {performance.cache_stats.misses.toLocaleString()}
              </div>
              <div className="text-sm text-gray-500">Cache Misses</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">
                {performance.cache_stats.total_requests.toLocaleString()}
              </div>
              <div className="text-sm text-gray-500">Total Requests</div>
            </div>
          </div>
        </Card>
      )}
    </div>
  )
}

export default SystemMonitoring
