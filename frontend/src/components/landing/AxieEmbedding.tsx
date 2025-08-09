import React, { useState } from 'react';
import { 
  Code, 
  Copy, 
  CheckCircle, 
  Settings, 
  Palette, 
  Monitor,
  Smartphone,
  Tablet,
  ExternalLink
} from 'lucide-react';
import { Link } from 'react-router-dom';

const AxieEmbedding = () => {
  const [activeTab, setActiveTab] = useState('html');
  const [copied, setCopied] = useState(false);
  const [selectedTheme, setSelectedTheme] = useState('auto');

  const embedCodes = {
    html: `<!-- Axie Studio Chat Widget -->
<script>
  window.chatWidgetConfig = {
    tenantId: 'your-tenant-id',
    position: 'bottom-right',
    theme: '${selectedTheme}',
    size: 'medium',
    showLauncher: true,
    autoOpen: false,
    customColors: {
      primary: '#8B5CF6',
      secondary: '#EC4899'
    }
  };
</script>
<script src="https://your-domain.com/api/v1/embed/your-tenant-id/widget.js" async></script>
<!-- End Chat Widget -->`,
    
    react: `import { AxieChatWidget } from '@axie-studio/chat-widget';

function App() {
  return (
    <div>
      {/* Your app content */}
      
      <AxieChatWidget
        tenantId="your-tenant-id"
        position="bottom-right"
        theme="${selectedTheme}"
        size="medium"
        showLauncher={true}
        autoOpen={false}
        customColors={{
          primary: '#8B5CF6',
          secondary: '#EC4899'
        }}
      />
    </div>
  );
}`,
    
    api: `// Initialize chat via API
const response = await fetch('https://your-domain.com/api/v1/embed/your-tenant-id/config');
const config = await response.json();

// Send message
const chatResponse = await fetch('https://your-domain.com/api/v1/chat/send', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer your-api-key'
  },
  body: JSON.stringify({
    message: 'Hello!',
    sessionId: 'unique-session-id',
    tenantId: 'your-tenant-id'
  })
});`
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(embedCodes[activeTab as keyof typeof embedCodes]);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const themes = [
    { id: 'auto', name: 'Auto', preview: 'bg-gradient-to-r from-gray-400 to-gray-600' },
    { id: 'light', name: 'Light', preview: 'bg-gradient-to-r from-gray-100 to-gray-300' },
    { id: 'dark', name: 'Dark', preview: 'bg-gradient-to-r from-gray-800 to-gray-900' },
    { id: 'purple', name: 'Purple', preview: 'bg-gradient-to-r from-purple-500 to-pink-500' },
    { id: 'blue', name: 'Blue', preview: 'bg-gradient-to-r from-blue-500 to-cyan-500' },
    { id: 'green', name: 'Green', preview: 'bg-gradient-to-r from-green-500 to-emerald-500' }
  ];

  return (
    <section id="embedding" className="py-20 px-4 sm:px-6 lg:px-8 bg-black/20">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <div className="inline-flex items-center space-x-2 bg-purple-500/20 text-purple-300 px-4 py-2 rounded-full mb-6">
            <Code className="w-4 h-4" />
            <span className="text-sm font-medium">Easy Integration</span>
          </div>
          
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
            Embed in Minutes
          </h2>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto">
            Get your AI chat widget running on any website with just a few lines of code. 
            Multiple integration options available.
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-12 items-start">
          {/* Code Examples */}
          <div>
            <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl overflow-hidden">
              {/* Tabs */}
              <div className="flex border-b border-white/10">
                {[
                  { id: 'html', name: 'HTML/JS', icon: <Code className="w-4 h-4" /> },
                  { id: 'react', name: 'React', icon: <Code className="w-4 h-4" /> },
                  { id: 'api', name: 'API', icon: <ExternalLink className="w-4 h-4" /> }
                ].map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex items-center space-x-2 px-6 py-4 font-medium transition-colors ${
                      activeTab === tab.id
                        ? 'bg-purple-600/20 text-purple-300 border-b-2 border-purple-500'
                        : 'text-gray-400 hover:text-white'
                    }`}
                  >
                    {tab.icon}
                    <span>{tab.name}</span>
                  </button>
                ))}
              </div>

              {/* Code Content */}
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
                
                <pre className="p-6 text-sm text-green-400 overflow-x-auto bg-gray-900/50">
                  <code>{embedCodes[activeTab as keyof typeof embedCodes]}</code>
                </pre>
              </div>
            </div>

            {/* Features List */}
            <div className="mt-8 grid md:grid-cols-2 gap-4">
              {[
                'Zero configuration required',
                'Automatic responsive design',
                'Custom branding support',
                'Real-time updates',
                'Analytics included',
                'GDPR compliant'
              ].map((feature, index) => (
                <div key={index} className="flex items-center space-x-2 text-green-400">
                  <CheckCircle className="w-5 h-5" />
                  <span>{feature}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Customization Panel */}
          <div className="space-y-8">
            {/* Theme Selector */}
            <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6">
              <h3 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2">
                <Palette className="w-5 h-5" />
                <span>Theme Customization</span>
              </h3>
              
              <div className="grid grid-cols-3 gap-3">
                {themes.map((theme) => (
                  <button
                    key={theme.id}
                    onClick={() => setSelectedTheme(theme.id)}
                    className={`p-3 rounded-lg border transition-all ${
                      selectedTheme === theme.id
                        ? 'border-purple-500 bg-purple-500/20'
                        : 'border-white/10 hover:border-white/20'
                    }`}
                  >
                    <div className={`w-full h-8 rounded ${theme.preview} mb-2`}></div>
                    <div className="text-sm text-white">{theme.name}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Device Preview */}
            <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6">
              <h3 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2">
                <Monitor className="w-5 h-5" />
                <span>Device Preview</span>
              </h3>
              
              <div className="flex justify-center space-x-4 mb-6">
                {[
                  { icon: <Monitor className="w-5 h-5" />, name: 'Desktop' },
                  { icon: <Tablet className="w-5 h-5" />, name: 'Tablet' },
                  { icon: <Smartphone className="w-5 h-5" />, name: 'Mobile' }
                ].map((device, index) => (
                  <div key={index} className="text-center">
                    <div className="text-purple-400 mb-1 flex justify-center">{device.icon}</div>
                    <div className="text-xs text-gray-400">{device.name}</div>
                  </div>
                ))}
              </div>
              
              <div className="bg-gray-900 rounded-lg p-4 text-center">
                <div className="text-gray-400 text-sm mb-2">Widget adapts to all screen sizes</div>
                <div className="inline-block bg-gradient-to-r from-purple-600 to-pink-600 text-white px-4 py-2 rounded-lg text-sm">
                  Chat Widget
                </div>
              </div>
            </div>

            {/* Admin Dashboard Link */}
            <div className="bg-gradient-to-r from-purple-600/20 to-pink-600/20 border border-purple-500/30 rounded-xl p-6">
              <h3 className="text-xl font-semibold text-white mb-2 flex items-center space-x-2">
                <Settings className="w-5 h-5" />
                <span>Admin Dashboard</span>
              </h3>
              <p className="text-gray-300 mb-4">
                Manage your chat widgets, customize branding, and monitor conversations from our powerful admin dashboard.
              </p>
              <Link 
                to="/admin/login" 
                className="inline-flex items-center space-x-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white px-6 py-3 rounded-lg font-medium hover:scale-105 transition-transform"
              >
                <Settings className="w-4 h-4" />
                <span>Access Admin Panel</span>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default AxieEmbedding;
