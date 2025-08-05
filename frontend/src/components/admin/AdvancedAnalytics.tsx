import React, { useState, useEffect } from 'react';
import Card from '../ui/Card';
import Button from '../ui/Button';
import Badge from '../ui/Badge';
import ProgressBar from '../ui/ProgressBar';

interface AnalyticsData {
  chat_metrics: {
    total_sessions: number;
    active_sessions: number;
    total_messages: number;
    total_tokens: number;
    average_response_time: number;
    sessions_by_hour: Record<string, number>;
    popular_topics: Array<{ topic: string; count: number }>;
    error_rate: number;
  };
  document_metrics: {
    total_documents: number;
    processed_documents: number;
    total_chunks: number;
    storage_usage: number;
    documents_by_type: Record<string, number>;
    documents_by_status: Record<string, number>;
  };
  security_metrics: {
    blocked_ips: number;
    recent_events: number;
    failed_attempts: number;
    threat_types: Record<string, number>;
  };
  system_metrics: {
    uptime: number;
    memory_usage: number;
    cpu_usage: number;
    disk_usage: number;
    response_time: number;
  };
}

interface RecentActivity {
  id: string;
  type: 'chat' | 'document' | 'security' | 'system';
  message: string;
  timestamp: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
}

export const AdvancedAnalytics: React.FC = () => {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState<number | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [timeRange, setTimeRange] = useState('24h');

  useEffect(() => {
    loadAnalytics();
    
    if (autoRefresh) {
      const interval = setInterval(loadAnalytics, 30000); // Refresh every 30 seconds
      setRefreshInterval(interval as any);
    } else if (refreshInterval) {
      clearInterval(refreshInterval);
      setRefreshInterval(null);
    }

    return () => {
      if (refreshInterval) clearInterval(refreshInterval);
    };
  }, [autoRefresh]);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      
      // Load analytics data
      const analyticsResponse = await fetch(`/api/v1/admin/analytics?time_range=${timeRange}`);
      if (analyticsResponse.ok) {
        const analyticsData = await analyticsResponse.json();
        setAnalytics(analyticsData);
      }

      // Load recent activity
      const activityResponse = await fetch('/api/v1/admin/activity?limit=20');
      if (activityResponse.ok) {
        const activityData = await activityResponse.json();
        setRecentActivity(activityData);
      }

    } catch (error) {
      console.error('Error loading analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatNumber = (num: number): string => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
  };

  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDuration = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    return `${hours}h ${minutes}m ${secs}s`;
  };

  const getSeverityColor = (severity: string): 'default' | 'success' | 'warning' | 'error' | 'info' => {
    switch (severity) {
      case 'critical': return 'error';
      case 'high': return 'warning';
      case 'medium': return 'info';
      case 'low': return 'success';
      default: return 'default';
    }
  };

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'chat': return '💬';
      case 'document': return '📄';
      case 'security': return '🔒';
      case 'system': return '⚙️';
      default: return '📊';
    }
  };

  if (loading && !analytics) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading analytics...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Advanced Analytics</h2>
          <p className="text-gray-600">Comprehensive system monitoring and insights</p>
        </div>
        <div className="flex gap-3">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="1h">Last Hour</option>
            <option value="24h">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
          </select>
          <Button
            variant={autoRefresh ? "primary" : "outline"}
            onClick={() => setAutoRefresh(!autoRefresh)}
          >
            {autoRefresh ? "Auto-Refresh On" : "Auto-Refresh Off"}
          </Button>
          <Button onClick={loadAnalytics} disabled={loading}>
            {loading ? "Refreshing..." : "Refresh"}
          </Button>
        </div>
      </div>

      {/* System Health Overview */}
      {analytics?.system_metrics && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">System Health</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {formatDuration(analytics.system_metrics.uptime)}
              </div>
              <div className="text-sm text-gray-500">Uptime</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {analytics.system_metrics.memory_usage.toFixed(1)}%
              </div>
              <div className="text-sm text-gray-500">Memory Usage</div>
              <ProgressBar 
                progress={analytics.system_metrics.memory_usage} 
                size="sm" 
                variant={analytics.system_metrics.memory_usage > 80 ? "danger" : "default"}
              />
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {analytics.system_metrics.cpu_usage.toFixed(1)}%
              </div>
              <div className="text-sm text-gray-500">CPU Usage</div>
              <ProgressBar 
                progress={analytics.system_metrics.cpu_usage} 
                size="sm" 
                variant={analytics.system_metrics.cpu_usage > 80 ? "danger" : "default"}
              />
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">
                {analytics.system_metrics.disk_usage.toFixed(1)}%
              </div>
              <div className="text-sm text-gray-500">Disk Usage</div>
              <ProgressBar 
                progress={analytics.system_metrics.disk_usage} 
                size="sm" 
                variant={analytics.system_metrics.disk_usage > 90 ? "danger" : "default"}
              />
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-indigo-600">
                {analytics.system_metrics.response_time.toFixed(0)}ms
              </div>
              <div className="text-sm text-gray-500">Avg Response Time</div>
            </div>
          </div>
        </Card>
      )}

      {/* Key Metrics Grid */}
      {analytics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Chat Metrics */}
          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Sessions</p>
                <p className="text-2xl font-bold text-gray-900">
                  {formatNumber(analytics.chat_metrics.total_sessions)}
                </p>
              </div>
              <div className="text-3xl">💬</div>
            </div>
            <div className="mt-4 flex items-center text-sm">
              <span className="text-green-600 font-medium">
                {analytics.chat_metrics.active_sessions} active
              </span>
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Messages</p>
                <p className="text-2xl font-bold text-gray-900">
                  {formatNumber(analytics.chat_metrics.total_messages)}
                </p>
              </div>
              <div className="text-3xl">📨</div>
            </div>
            <div className="mt-4 flex items-center text-sm">
              <span className="text-blue-600 font-medium">
                {formatNumber(analytics.chat_metrics.total_tokens)} tokens
              </span>
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Documents</p>
                <p className="text-2xl font-bold text-gray-900">
                  {formatNumber(analytics.document_metrics.total_documents)}
                </p>
              </div>
              <div className="text-3xl">📄</div>
            </div>
            <div className="mt-4 flex items-center text-sm">
              <span className="text-purple-600 font-medium">
                {formatNumber(analytics.document_metrics.total_chunks)} chunks
              </span>
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Security Events</p>
                <p className="text-2xl font-bold text-gray-900">
                  {analytics.security_metrics.recent_events}
                </p>
              </div>
              <div className="text-3xl">🔒</div>
            </div>
            <div className="mt-4 flex items-center text-sm">
              <span className="text-red-600 font-medium">
                {analytics.security_metrics.blocked_ips} blocked IPs
              </span>
            </div>
          </Card>
        </div>
      )}

      {/* Detailed Analytics */}
      {analytics && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Chat Performance */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Chat Performance</h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Average Response Time</span>
                <span className="font-medium">
                  {analytics.chat_metrics.average_response_time.toFixed(2)}s
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Error Rate</span>
                <span className="font-medium text-red-600">
                  {(analytics.chat_metrics.error_rate * 100).toFixed(2)}%
                </span>
              </div>
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm text-gray-600">Popular Topics</span>
                </div>
                <div className="space-y-2">
                  {analytics.chat_metrics.popular_topics.slice(0, 5).map((topic, index) => (
                    <div key={index} className="flex justify-between items-center">
                      <span className="text-sm">{topic.topic}</span>
                      <Badge variant="default">{topic.count}</Badge>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </Card>

          {/* Document Analytics */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Document Analytics</h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Storage Usage</span>
                <span className="font-medium">
                  {formatBytes(analytics.document_metrics.storage_usage)}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Processing Rate</span>
                <span className="font-medium text-green-600">
                  {((analytics.document_metrics.processed_documents / analytics.document_metrics.total_documents) * 100).toFixed(1)}%
                </span>
              </div>
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm text-gray-600">By File Type</span>
                </div>
                <div className="space-y-2">
                  {Object.entries(analytics.document_metrics.documents_by_type).map(([type, count]) => (
                    <div key={type} className="flex justify-between items-center">
                      <span className="text-sm uppercase">{type}</span>
                      <Badge variant="default">{count}</Badge>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Recent Activity */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
        <div className="space-y-3">
          {recentActivity.length === 0 ? (
            <p className="text-gray-500 text-center py-4">No recent activity</p>
          ) : (
            recentActivity.map((activity) => (
              <div key={activity.id} className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                <div className="text-xl">{getActivityIcon(activity.type)}</div>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium">{activity.message}</span>
                    <Badge variant={getSeverityColor(activity.severity)} size="sm">
                      {activity.severity}
                    </Badge>
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    {new Date(activity.timestamp).toLocaleString()}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </Card>
    </div>
  );
};
