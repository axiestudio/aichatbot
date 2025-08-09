import React, { useState, useEffect } from 'react';
import {
  Code,
  Copy,
  CheckCircle,
  Settings,
  Palette,
  Monitor,
  Smartphone,
  Tablet,
  ExternalLink,
  Eye,
  Download,
  Share,
  Globe,
  Lock,
  Zap,
  RefreshCw,
  Save,
  TestTube,
  Activity,
  Users,
  MessageSquare,
  BarChart3,
  AlertCircle
} from 'lucide-react';
import { useAuthStore } from '../../stores/authStore';
import { useClientStore } from '../../stores/clientStore';
import { toast } from 'react-hot-toast';

// Declare global Window interface for initAxieChatWidget
declare global {
  interface Window {
    initAxieChatWidget?: (config: any) => void;
  }
}

const EmbedManager = () => {
  const { user } = useAuthStore();
  const {
    chatConfig,
    activeEmbeds,
    liveSessions,
    analytics,
    generateEmbedCode,
    testEmbedConnection,
    updateChatConfig,
    loadActiveEmbeds,
    loadLiveSessions
  } = useClientStore();

  const [activeTab, setActiveTab] = useState('html');
  const [copied, setCopied] = useState(false);
  const [loading, setLoading] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testDomain, setTestDomain] = useState('');

  const [embedConfig, setEmbedConfig] = useState({
    position: 'bottom-right',
    theme: 'auto',
    size: 'medium',
    showLauncher: true,
    autoOpen: false,
    customColors: {
      primary: '#8B5CF6',
      secondary: '#EC4899',
      background: '#FFFFFF',
      text: '#1F2937'
    },
    launcherText: 'Chat with us',
    allowedDomains: '',
    customCSS: '',
    showPoweredBy: true,
    animation: 'slide',
    closeOnOutsideClick: true
  });

  const tenantId = user?.tenantId || user?.id || 'demo-tenant';
  const baseUrl = window.location.origin;

  // Load current configuration on mount
  useEffect(() => {
    loadEmbedConfig();
    loadEmbedStats();
  }, [tenantId]);

  // API Functions
  const loadEmbedConfig = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/v1/embed/${tenantId}/config`);
      if (response.ok) {
        const config = await response.json();
        setEmbedConfig(prev => ({
          ...prev,
          ...config.branding,
          customColors: {
            ...prev.customColors,
            ...config.branding?.colors
          }
        }));
      }
    } catch (error) {
      console.error('Failed to load embed config:', error);
    } finally {
      setLoading(false);
    }
  };

  const saveEmbedConfig = async () => {
    try {
      setSaving(true);
      const response = await fetch(`/api/v1/embed/${tenantId}/customize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(embedConfig)
      });

      if (response.ok) {
        // Show success message
        alert('Configuration saved successfully!');
      } else {
        throw new Error('Failed to save configuration');
      }
    } catch (error) {
      console.error('Failed to save embed config:', error);
      alert('Failed to save configuration. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const loadEmbedStats = async () => {
    try {
      const response = await fetch(`/api/v1/embed/${tenantId}/analytics`);
      if (response.ok) {
        const stats = await response.json();
        setEmbedStats(stats);
      }
    } catch (error) {
      console.error('Failed to load embed stats:', error);
    }
  };

  const testWidget = async () => {
    try {
      setTesting(true);
      // Create a test widget instance
      const testConfig = {
        ...embedConfig,
        tenantId: tenantId,
        autoOpen: true
      };

      // Initialize test widget
      if (window.initAxieChatWidget) {
        window.initAxieChatWidget(testConfig);
      } else {
        alert('Widget script not loaded. Please refresh the page and try again.');
      }
    } catch (error) {
      console.error('Failed to test widget:', error);
      alert('Failed to test widget. Please check the configuration.');
    } finally {
      setTesting(false);
    }
  };

  const embedCodes = {
    html: `<!-- Axie Studio Chat Widget v2.0 -->
<script>
  window.chatWidgetConfig = {
    tenantId: '${tenantId}',
    position: '${embedConfig.position}',
    theme: '${embedConfig.theme}',
    size: '${embedConfig.size}',
    showLauncher: ${embedConfig.showLauncher},
    autoOpen: ${embedConfig.autoOpen},
    launcherText: '${embedConfig.launcherText}',
    customColors: {
      primary: '${embedConfig.customColors.primary}',
      secondary: '${embedConfig.customColors.secondary}',
      background: '${embedConfig.customColors.background}',
      text: '${embedConfig.customColors.text}'
    },
    showPoweredBy: ${embedConfig.showPoweredBy},
    animation: '${embedConfig.animation}',
    closeOnOutsideClick: ${embedConfig.closeOnOutsideClick},
    allowedDomains: [${embedConfig.allowedDomains.split('\n').filter(d => d.trim()).map(d => `'${d.trim()}'`).join(', ')}]
  };
</script>
<script src="${baseUrl}/api/v1/embed/${tenantId}/widget.js" async></script>
<!-- End Axie Studio Chat Widget -->`,
    
    react: `import { AxieChatWidget } from '@axie-studio/chat-widget';

function App() {
  return (
    <div>
      {/* Your app content */}

      <AxieChatWidget
        tenantId="${tenantId}"
        position="${embedConfig.position}"
        theme="${embedConfig.theme}"
        size="${embedConfig.size}"
        showLauncher={${embedConfig.showLauncher}}
        autoOpen={${embedConfig.autoOpen}}
        launcherText="${embedConfig.launcherText}"
        customColors={{
          primary: '${embedConfig.customColors.primary}',
          secondary: '${embedConfig.customColors.secondary}',
          background: '${embedConfig.customColors.background}',
          text: '${embedConfig.customColors.text}'
        }}
        showPoweredBy={${embedConfig.showPoweredBy}}
        animation="${embedConfig.animation}"
        closeOnOutsideClick={${embedConfig.closeOnOutsideClick}}
        allowedDomains={[${embedConfig.allowedDomains.split('\n').filter(d => d.trim()).map(d => `'${d.trim()}'`).join(', ')}]}
      />
    </div>
  );
}`,
    
    api: `// Initialize chat via API
const response = await fetch('${baseUrl}/api/v1/embed/${tenantId}/config');
const config = await response.json();

// Send message
const chatResponse = await fetch('${baseUrl}/api/v1/chat/send', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer your-api-key'
  },
  body: JSON.stringify({
    message: 'Hello!',
    sessionId: 'unique-session-id',
    tenantId: '${tenantId}'
  })
});`,

    iframe: `<!-- Direct iframe embedding -->
<iframe 
  src="${baseUrl}/chat?embed=true&tenant=${tenantId}&theme=${embedConfig.theme}"
  width="400" 
  height="600"
  frameborder="0"
  style="border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);"
  allow="microphone; camera"
></iframe>`
  };

  const copyToClipboard = async () => {
    try {
      const codeToCopy = activeTab === 'html' ? generateEmbedCode() : embedCodes[activeTab as keyof typeof embedCodes];
      await navigator.clipboard.writeText(codeToCopy);
      setCopied(true);
      toast.success('Embed code copied to clipboard!');
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      toast.error('Failed to copy embed code');
    }
  };

  const positions = [
    { id: 'bottom-right', name: 'Bottom Right', preview: 'justify-end items-end' },
    { id: 'bottom-left', name: 'Bottom Left', preview: 'justify-start items-end' },
    { id: 'top-right', name: 'Top Right', preview: 'justify-end items-start' },
    { id: 'top-left', name: 'Top Left', preview: 'justify-start items-start' }
  ];

  const themes = [
    { id: 'auto', name: 'Auto', preview: 'bg-gradient-to-r from-gray-400 to-gray-600' },
    { id: 'light', name: 'Light', preview: 'bg-gradient-to-r from-gray-100 to-gray-300' },
    { id: 'dark', name: 'Dark', preview: 'bg-gradient-to-r from-gray-800 to-gray-900' },
    { id: 'purple', name: 'Purple', preview: 'bg-gradient-to-r from-purple-500 to-pink-500' },
    { id: 'blue', name: 'Blue', preview: 'bg-gradient-to-r from-blue-500 to-cyan-500' },
    { id: 'green', name: 'Green', preview: 'bg-gradient-to-r from-green-500 to-emerald-500' }
  ];

  const sizes = [
    { id: 'small', name: 'Small', width: '320px', height: '400px' },
    { id: 'medium', name: 'Medium', width: '380px', height: '500px' },
    { id: 'large', name: 'Large', width: '450px', height: '600px' }
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 flex items-center space-x-2">
              <Code className="w-6 h-6 text-purple-600" />
              <span>Embed Manager</span>
            </h1>
            <p className="text-gray-600 mt-1">
              Generate embed codes and customize your chat widget for any website
            </p>
          </div>
          
          <div className="flex space-x-3">
            <button
              onClick={testWidget}
              disabled={testing}
              className="flex items-center space-x-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
            >
              {testing ? <RefreshCw className="w-4 h-4 animate-spin" /> : <TestTube className="w-4 h-4" />}
              <span>{testing ? 'Testing...' : 'Test Widget'}</span>
            </button>
            <button
              onClick={saveEmbedConfig}
              disabled={saving}
              className="flex items-center space-x-2 bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50"
            >
              {saving ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
              <span>{saving ? 'Saving...' : 'Save Config'}</span>
            </button>
            <button
              onClick={() => setPreviewMode(!previewMode)}
              className="flex items-center space-x-2 border border-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <Eye className="w-4 h-4" />
              <span>{previewMode ? 'Hide Preview' : 'Show Preview'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Real-time Monitoring */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Embeds</p>
              <p className="text-3xl font-bold text-gray-900">{activeEmbeds.length}</p>
            </div>
            <Globe className="w-8 h-8 text-blue-600" />
          </div>
          <div className="mt-4">
            <div className="text-sm text-gray-500">
              {activeEmbeds.reduce((sum, embed) => sum + embed.visitors, 0)} active visitors
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Live Sessions</p>
              <p className="text-3xl font-bold text-gray-900">{liveSessions.filter(s => s.isActive).length}</p>
            </div>
            <Users className="w-8 h-8 text-green-600" />
          </div>
          <div className="mt-4">
            <div className="text-sm text-gray-500">
              {liveSessions.length} total sessions today
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Messages Today</p>
              <p className="text-3xl font-bold text-gray-900">{analytics?.totalMessages || 0}</p>
            </div>
            <MessageSquare className="w-8 h-8 text-purple-600" />
          </div>
          <div className="mt-4">
            <div className="text-sm text-gray-500">
              Avg {analytics?.avgSessionDuration || 0} min per session
            </div>
          </div>
        </div>
      </div>

      {/* Active Embeds List */}
      {activeEmbeds.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
            <Activity className="w-5 h-5" />
            <span>Active Embeds</span>
          </h3>
          <div className="space-y-3">
            {activeEmbeds.map((embed) => (
              <div key={embed.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  <div>
                    <div className="font-medium text-gray-900">{embed.domain}</div>
                    <div className="text-sm text-gray-500">
                      Last seen: {new Date(embed.lastSeen).toLocaleTimeString()}
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-medium text-gray-900">{embed.visitors} visitors</div>
                  <div className="text-sm text-gray-500">Active now</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="grid lg:grid-cols-2 gap-8">
        {/* Configuration Panel */}
        <div className="space-y-6">
          {/* Widget Configuration */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
              <Settings className="w-5 h-5" />
              <span>Widget Configuration</span>
            </h2>
            
            <div className="space-y-4">
              {/* Position */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Position</label>
                <div className="grid grid-cols-2 gap-2">
                  {positions.map((position) => (
                    <button
                      key={position.id}
                      onClick={() => setEmbedConfig({...embedConfig, position: position.id})}
                      className={`p-3 rounded-lg border text-sm transition-all ${
                        embedConfig.position === position.id
                          ? 'border-purple-500 bg-purple-50 text-purple-700'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      {position.name}
                    </button>
                  ))}
                </div>
              </div>

              {/* Theme */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Theme</label>
                <div className="grid grid-cols-3 gap-2">
                  {themes.map((theme) => (
                    <button
                      key={theme.id}
                      onClick={() => setEmbedConfig({...embedConfig, theme: theme.id})}
                      className={`p-3 rounded-lg border transition-all ${
                        embedConfig.theme === theme.id
                          ? 'border-purple-500 bg-purple-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <div className={`w-full h-6 rounded ${theme.preview} mb-1`}></div>
                      <div className="text-xs text-gray-600">{theme.name}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Size */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Size</label>
                <div className="grid grid-cols-3 gap-2">
                  {sizes.map((size) => (
                    <button
                      key={size.id}
                      onClick={() => setEmbedConfig({...embedConfig, size: size.id})}
                      className={`p-3 rounded-lg border text-sm transition-all ${
                        embedConfig.size === size.id
                          ? 'border-purple-500 bg-purple-50 text-purple-700'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <div className="font-medium">{size.name}</div>
                      <div className="text-xs text-gray-500">{size.width} × {size.height}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Options */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <label className="text-sm font-medium text-gray-700">Show Launcher</label>
                  <button
                    onClick={() => setEmbedConfig({...embedConfig, showLauncher: !embedConfig.showLauncher})}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                      embedConfig.showLauncher ? 'bg-purple-600' : 'bg-gray-200'
                    }`}
                  >
                    <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      embedConfig.showLauncher ? 'translate-x-6' : 'translate-x-1'
                    }`} />
                  </button>
                </div>

                <div className="flex items-center justify-between">
                  <label className="text-sm font-medium text-gray-700">Auto Open</label>
                  <button
                    onClick={() => setEmbedConfig({...embedConfig, autoOpen: !embedConfig.autoOpen})}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                      embedConfig.autoOpen ? 'bg-purple-600' : 'bg-gray-200'
                    }`}
                  >
                    <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      embedConfig.autoOpen ? 'translate-x-6' : 'translate-x-1'
                    }`} />
                  </button>
                </div>

                <div className="flex items-center justify-between">
                  <label className="text-sm font-medium text-gray-700">Show "Powered by Axie Studio"</label>
                  <button
                    onClick={() => setEmbedConfig({...embedConfig, showPoweredBy: !embedConfig.showPoweredBy})}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                      embedConfig.showPoweredBy ? 'bg-purple-600' : 'bg-gray-200'
                    }`}
                  >
                    <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      embedConfig.showPoweredBy ? 'translate-x-6' : 'translate-x-1'
                    }`} />
                  </button>
                </div>

                <div className="flex items-center justify-between">
                  <label className="text-sm font-medium text-gray-700">Close on Outside Click</label>
                  <button
                    onClick={() => setEmbedConfig({...embedConfig, closeOnOutsideClick: !embedConfig.closeOnOutsideClick})}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                      embedConfig.closeOnOutsideClick ? 'bg-purple-600' : 'bg-gray-200'
                    }`}
                  >
                    <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      embedConfig.closeOnOutsideClick ? 'translate-x-6' : 'translate-x-1'
                    }`} />
                  </button>
                </div>
              </div>

              {/* Launcher Text */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Launcher Text</label>
                <input
                  type="text"
                  value={embedConfig.launcherText}
                  onChange={(e) => setEmbedConfig({...embedConfig, launcherText: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>

              {/* Custom Colors */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Custom Colors</label>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">Primary</label>
                    <div className="flex items-center space-x-2">
                      <input
                        type="color"
                        value={embedConfig.customColors.primary}
                        onChange={(e) => setEmbedConfig({
                          ...embedConfig,
                          customColors: {...embedConfig.customColors, primary: e.target.value}
                        })}
                        className="w-8 h-8 rounded border border-gray-300"
                      />
                      <input
                        type="text"
                        value={embedConfig.customColors.primary}
                        onChange={(e) => setEmbedConfig({
                          ...embedConfig,
                          customColors: {...embedConfig.customColors, primary: e.target.value}
                        })}
                        className="flex-1 px-2 py-1 text-sm border border-gray-300 rounded"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">Secondary</label>
                    <div className="flex items-center space-x-2">
                      <input
                        type="color"
                        value={embedConfig.customColors.secondary}
                        onChange={(e) => setEmbedConfig({
                          ...embedConfig,
                          customColors: {...embedConfig.customColors, secondary: e.target.value}
                        })}
                        className="w-8 h-8 rounded border border-gray-300"
                      />
                      <input
                        type="text"
                        value={embedConfig.customColors.secondary}
                        onChange={(e) => setEmbedConfig({
                          ...embedConfig,
                          customColors: {...embedConfig.customColors, secondary: e.target.value}
                        })}
                        className="flex-1 px-2 py-1 text-sm border border-gray-300 rounded"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">Background</label>
                    <div className="flex items-center space-x-2">
                      <input
                        type="color"
                        value={embedConfig.customColors.background}
                        onChange={(e) => setEmbedConfig({
                          ...embedConfig,
                          customColors: {...embedConfig.customColors, background: e.target.value}
                        })}
                        className="w-8 h-8 rounded border border-gray-300"
                      />
                      <input
                        type="text"
                        value={embedConfig.customColors.background}
                        onChange={(e) => setEmbedConfig({
                          ...embedConfig,
                          customColors: {...embedConfig.customColors, background: e.target.value}
                        })}
                        className="flex-1 px-2 py-1 text-sm border border-gray-300 rounded"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">Text</label>
                    <div className="flex items-center space-x-2">
                      <input
                        type="color"
                        value={embedConfig.customColors.text}
                        onChange={(e) => setEmbedConfig({
                          ...embedConfig,
                          customColors: {...embedConfig.customColors, text: e.target.value}
                        })}
                        className="w-8 h-8 rounded border border-gray-300"
                      />
                      <input
                        type="text"
                        value={embedConfig.customColors.text}
                        onChange={(e) => setEmbedConfig({
                          ...embedConfig,
                          customColors: {...embedConfig.customColors, text: e.target.value}
                        })}
                        className="flex-1 px-2 py-1 text-sm border border-gray-300 rounded"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Security Settings */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
              <Lock className="w-5 h-5" />
              <span>Security Settings</span>
            </h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Allowed Domains (Optional)
                </label>
                <textarea
                  value={embedConfig.allowedDomains}
                  onChange={(e) => setEmbedConfig({...embedConfig, allowedDomains: e.target.value})}
                  placeholder="example.com&#10;subdomain.example.com&#10;*.example.com"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                  rows={3}
                />
                <p className="text-xs text-gray-500 mt-1">
                  Leave empty to allow all domains. One domain per line. Use *.domain.com for subdomains.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Code Generation */}
        <div className="space-y-6">
          {/* Embed Code */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
            <div className="border-b border-gray-200">
              <div className="flex">
                {[
                  { id: 'html', name: 'HTML/JS', icon: <Code className="w-4 h-4" /> },
                  { id: 'react', name: 'React', icon: <Code className="w-4 h-4" /> },
                  { id: 'api', name: 'API', icon: <ExternalLink className="w-4 h-4" /> },
                  { id: 'iframe', name: 'iFrame', icon: <Monitor className="w-4 h-4" /> }
                ].map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex items-center space-x-2 px-4 py-3 font-medium transition-colors ${
                      activeTab === tab.id
                        ? 'bg-purple-50 text-purple-600 border-b-2 border-purple-600'
                        : 'text-gray-500 hover:text-gray-700'
                    }`}
                  >
                    {tab.icon}
                    <span>{tab.name}</span>
                  </button>
                ))}
              </div>
            </div>

            <div className="relative">
              <div className="absolute top-4 right-4 z-10">
                <button
                  onClick={copyToClipboard}
                  className="flex items-center space-x-2 bg-gray-800 hover:bg-gray-700 text-white px-3 py-2 rounded-lg transition-colors"
                >
                  {copied ? <CheckCircle className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                  <span className="text-sm">{copied ? 'Copied!' : 'Copy'}</span>
                </button>
              </div>
              
              <pre className="p-6 text-sm text-green-400 overflow-x-auto bg-gray-900 min-h-[300px]">
                <code>{activeTab === 'html' ? generateEmbedCode() : embedCodes[activeTab as keyof typeof embedCodes]}</code>
              </pre>
            </div>
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
              <div className="flex items-center space-x-2">
                <Globe className="w-5 h-5 text-blue-600" />
                <div>
                  <div className="text-sm text-gray-600">Active Embeds</div>
                  <div className="text-xl font-semibold text-gray-900">
                    {loading ? '...' : embedStats.activeEmbeds}
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
              <div className="flex items-center space-x-2">
                <BarChart3 className="w-5 h-5 text-green-600" />
                <div>
                  <div className="text-sm text-gray-600">This Month</div>
                  <div className="text-xl font-semibold text-gray-900">
                    {loading ? '...' : embedStats.monthlyConversations.toLocaleString()}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Live Preview */}
          {previewMode && (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mt-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
                <Eye className="w-5 h-5" />
                <span>Live Widget Preview</span>
              </h3>

              <div className="bg-gray-100 rounded-lg p-8 min-h-[400px] relative">
                <div className="text-center text-gray-500 mb-4">
                  Preview of your chat widget on a website
                </div>

                {/* Mock website content */}
                <div className="bg-white rounded-lg p-6 shadow-sm">
                  <div className="h-4 bg-gray-200 rounded mb-2"></div>
                  <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                  <div className="h-4 bg-gray-200 rounded w-1/2"></div>
                </div>

                {/* Widget preview would be positioned here */}
                <div className="absolute bottom-4 right-4">
                  <div
                    className="w-16 h-16 rounded-full flex items-center justify-center text-white shadow-lg cursor-pointer"
                    style={{
                      background: `linear-gradient(135deg, ${embedConfig.customColors.primary}, ${embedConfig.customColors.secondary})`
                    }}
                  >
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                      <path d="M8 10h.01M12 10h.01M16 10h.01"></path>
                    </svg>
                  </div>
                </div>
              </div>

              <div className="mt-4 text-sm text-gray-600">
                <AlertCircle className="w-4 h-4 inline mr-1" />
                This is a visual preview. Use "Test Widget" to see the actual functionality.
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default EmbedManager;
