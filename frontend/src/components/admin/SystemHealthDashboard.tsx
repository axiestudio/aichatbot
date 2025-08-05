import React, { useState, useEffect } from 'react';
import { Activity, Server, Database, Zap, AlertTriangle, CheckCircle, XCircle } from 'lucide-react';
import Card from '../ui/Card';
import Badge from '../ui/Badge';
import ProgressBar from '../ui/ProgressBar';

interface SystemMetrics {
  cpu: {
    usage: number;
    cores: number;
    load: number[];
  };
  memory: {
    used: number;
    total: number;
    percentage: number;
  };
  disk: {
    used: number;
    total: number;
    percentage: number;
  };
  network: {
    bytesIn: number;
    bytesOut: number;
    connectionsActive: number;
  };
  database: {
    connections: number;
    maxConnections: number;
    queryTime: number;
    slowQueries: number;
  };
  api: {
    requestsPerMinute: number;
    averageResponseTime: number;
    errorRate: number;
    activeUsers: number;
  };
}

interface HealthStatus {
  overall: 'healthy' | 'warning' | 'critical';
  services: {
    api: 'up' | 'down' | 'degraded';
    database: 'up' | 'down' | 'degraded';
    redis: 'up' | 'down' | 'degraded';
    storage: 'up' | 'down' | 'degraded';
  };
  alerts: Array<{
    id: string;
    type: 'warning' | 'error' | 'critical';
    message: string;
    timestamp: string;
  }>;
}

export default function SystemHealthDashboard() {
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null);
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  useEffect(() => {
    fetchSystemMetrics();
    const interval = setInterval(fetchSystemMetrics, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchSystemMetrics = async () => {
    try {
      const [metricsResponse, healthResponse] = await Promise.all([
        fetch('/api/v1/admin/metrics/system'),
        fetch('/api/v1/admin/health/detailed')
      ]);

      if (metricsResponse.ok && healthResponse.ok) {
        const metricsData = await metricsResponse.json();
        const healthData = await healthResponse.json();
        
        setMetrics(metricsData);
        setHealth(healthData);
        setLastUpdate(new Date());
      }
    } catch (error) {
      console.error('Failed to fetch system metrics:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'up':
      case 'healthy':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'warning':
      case 'degraded':
        return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
      case 'down':
      case 'critical':
        return <XCircle className="w-5 h-5 text-red-500" />;
      default:
        return <Activity className="w-5 h-5 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'up':
      case 'healthy':
        return 'green';
      case 'warning':
      case 'degraded':
        return 'yellow';
      case 'down':
      case 'critical':
        return 'red';
      default:
        return 'gray';
    }
  };

  const formatBytes = (bytes: number) => {
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    if (bytes === 0) return '0 B';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Overall Health Status */}
      <Card>
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold">System Health Overview</h2>
            <div className="flex items-center space-x-2">
              {getStatusIcon(health?.overall || 'unknown')}
              <Badge color={getStatusColor(health?.overall || 'gray')}>
                {health?.overall?.toUpperCase() || 'UNKNOWN'}
              </Badge>
            </div>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {health?.services && Object.entries(health.services).map(([service, status]) => (
              <div key={service} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-2">
                  <Server className="w-4 h-4 text-gray-600" />
                  <span className="text-sm font-medium capitalize">{service}</span>
                </div>
                {getStatusIcon(status)}
              </div>
            ))}
          </div>
          
          <div className="mt-4 text-sm text-gray-500">
            Last updated: {lastUpdate.toLocaleTimeString()}
          </div>
        </div>
      </Card>

      {/* System Resources */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* CPU Usage */}
        <Card>
          <div className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium">CPU Usage</h3>
              <Zap className="w-5 h-5 text-blue-500" />
            </div>
            
            {metrics?.cpu && (
              <div className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span>Usage</span>
                  <span>{metrics.cpu.usage.toFixed(1)}%</span>
                </div>
                <ProgressBar 
                  progress={metrics.cpu.usage} 
                  color={metrics.cpu.usage > 80 ? 'red' : metrics.cpu.usage > 60 ? 'yellow' : 'green'}
                />
                
                <div className="grid grid-cols-2 gap-2 text-sm text-gray-600">
                  <div>Cores: {metrics.cpu.cores}</div>
                  <div>Load: {metrics.cpu.load[0]?.toFixed(2) || 'N/A'}</div>
                </div>
              </div>
            )}
          </div>
        </Card>

        {/* Memory Usage */}
        <Card>
          <div className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium">Memory Usage</h3>
              <Database className="w-5 h-5 text-green-500" />
            </div>
            
            {metrics?.memory && (
              <div className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span>Used</span>
                  <span>{formatBytes(metrics.memory.used)} / {formatBytes(metrics.memory.total)}</span>
                </div>
                <ProgressBar 
                  progress={metrics.memory.percentage} 
                  color={metrics.memory.percentage > 85 ? 'red' : metrics.memory.percentage > 70 ? 'yellow' : 'green'}
                />
                
                <div className="text-sm text-gray-600">
                  {metrics.memory.percentage.toFixed(1)}% utilized
                </div>
              </div>
            )}
          </div>
        </Card>

        {/* Disk Usage */}
        <Card>
          <div className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium">Disk Usage</h3>
              <Server className="w-5 h-5 text-purple-500" />
            </div>
            
            {metrics?.disk && (
              <div className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span>Used</span>
                  <span>{formatBytes(metrics.disk.used)} / {formatBytes(metrics.disk.total)}</span>
                </div>
                <ProgressBar 
                  progress={metrics.disk.percentage} 
                  color={metrics.disk.percentage > 90 ? 'red' : metrics.disk.percentage > 75 ? 'yellow' : 'green'}
                />
                
                <div className="text-sm text-gray-600">
                  {metrics.disk.percentage.toFixed(1)}% utilized
                </div>
              </div>
            )}
          </div>
        </Card>
      </div>

      {/* API Performance */}
      <Card>
        <div className="p-6">
          <h3 className="text-lg font-medium mb-4">API Performance</h3>
          
          {metrics?.api && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">{metrics.api.requestsPerMinute}</div>
                <div className="text-sm text-gray-600">Requests/min</div>
              </div>
              
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">{metrics.api.averageResponseTime}ms</div>
                <div className="text-sm text-gray-600">Avg Response</div>
              </div>
              
              <div className="text-center p-4 bg-yellow-50 rounded-lg">
                <div className="text-2xl font-bold text-yellow-600">{metrics.api.errorRate.toFixed(2)}%</div>
                <div className="text-sm text-gray-600">Error Rate</div>
              </div>
              
              <div className="text-center p-4 bg-purple-50 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">{metrics.api.activeUsers}</div>
                <div className="text-sm text-gray-600">Active Users</div>
              </div>
            </div>
          )}
        </div>
      </Card>

      {/* Active Alerts */}
      {health?.alerts && health.alerts.length > 0 && (
        <Card>
          <div className="p-6">
            <h3 className="text-lg font-medium mb-4">Active Alerts</h3>
            
            <div className="space-y-3">
              {health.alerts.map((alert) => (
                <div 
                  key={alert.id}
                  className={`p-4 rounded-lg border-l-4 ${
                    alert.type === 'critical' ? 'bg-red-50 border-red-500' :
                    alert.type === 'error' ? 'bg-orange-50 border-orange-500' :
                    'bg-yellow-50 border-yellow-500'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(alert.type)}
                      <span className="font-medium">{alert.message}</span>
                    </div>
                    <span className="text-sm text-gray-500">
                      {new Date(alert.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}
