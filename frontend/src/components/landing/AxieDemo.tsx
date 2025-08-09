import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  Play, 
  MessageCircle, 
  ArrowRight, 
  Zap,
  Users,
  BarChart3,
  Settings
} from 'lucide-react';

const AxieDemo = () => {
  const [activeDemo, setActiveDemo] = useState('chat');

  const demoOptions = [
    {
      id: 'chat',
      name: 'Live Chat',
      icon: <MessageCircle className="w-5 h-5" />,
      description: 'Experience our AI chat interface'
    },
    {
      id: 'admin',
      name: 'Admin Panel',
      icon: <Settings className="w-5 h-5" />,
      description: 'See the admin dashboard'
    },
    {
      id: 'analytics',
      name: 'Analytics',
      icon: <BarChart3 className="w-5 h-5" />,
      description: 'View conversation insights'
    }
  ];

  return (
    <section id="demo" className="py-20 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <div className="inline-flex items-center space-x-2 bg-purple-500/20 text-purple-300 px-4 py-2 rounded-full mb-6">
            <Play className="w-4 h-4" />
            <span className="text-sm font-medium">Live Demo</span>
          </div>
          
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
            See It In Action
          </h2>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto">
            Experience the power of our embeddable AI chat platform. Try the live demo 
            or explore the admin interface.
          </p>
        </div>

        {/* Demo Selector */}
        <div className="flex justify-center mb-12">
          <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-2 flex space-x-2">
            {demoOptions.map((option) => (
              <button
                key={option.id}
                onClick={() => setActiveDemo(option.id)}
                className={`flex items-center space-x-2 px-6 py-3 rounded-lg transition-all ${
                  activeDemo === option.id
                    ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white'
                    : 'text-gray-400 hover:text-white hover:bg-white/10'
                }`}
              >
                {option.icon}
                <span className="font-medium">{option.name}</span>
              </button>
            ))}
          </div>
        </div>

        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Demo Description */}
          <div>
            {activeDemo === 'chat' && (
              <>
                <h3 className="text-3xl font-bold text-white mb-6">
                  Interactive AI Chat Demo
                </h3>
                <p className="text-lg text-gray-300 mb-8">
                  Experience our AI-powered chat interface with real-time responses, 
                  context awareness, and natural conversation flow. See how easy it is 
                  for your customers to get instant help.
                </p>
                <div className="space-y-4 mb-8">
                  {[
                    'Real-time AI responses',
                    'Context-aware conversations',
                    'Multi-language support',
                    'File upload capabilities',
                    'Conversation history',
                    'Custom branding'
                  ].map((feature, index) => (
                    <div key={index} className="flex items-center space-x-3">
                      <div className="w-2 h-2 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full"></div>
                      <span className="text-gray-300">{feature}</span>
                    </div>
                  ))}
                </div>
              </>
            )}

            {activeDemo === 'admin' && (
              <>
                <h3 className="text-3xl font-bold text-white mb-6">
                  Admin Dashboard Demo
                </h3>
                <p className="text-lg text-gray-300 mb-8">
                  Explore our comprehensive admin interface where you can manage 
                  chat configurations, monitor conversations, customize branding, 
                  and generate embed codes for your websites.
                </p>
                <div className="space-y-4 mb-8">
                  {[
                    'Chat widget configuration',
                    'Brand customization',
                    'Conversation monitoring',
                    'Analytics dashboard',
                    'User management',
                    'API key management'
                  ].map((feature, index) => (
                    <div key={index} className="flex items-center space-x-3">
                      <div className="w-2 h-2 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-full"></div>
                      <span className="text-gray-300">{feature}</span>
                    </div>
                  ))}
                </div>
              </>
            )}

            {activeDemo === 'analytics' && (
              <>
                <h3 className="text-3xl font-bold text-white mb-6">
                  Analytics & Insights Demo
                </h3>
                <p className="text-lg text-gray-300 mb-8">
                  Discover powerful analytics that help you understand customer 
                  interactions, optimize conversation flows, and measure the 
                  effectiveness of your AI chat implementation.
                </p>
                <div className="space-y-4 mb-8">
                  {[
                    'Conversation analytics',
                    'Response time metrics',
                    'User satisfaction scores',
                    'Popular topics tracking',
                    'Performance insights',
                    'Custom reports'
                  ].map((feature, index) => (
                    <div key={index} className="flex items-center space-x-3">
                      <div className="w-2 h-2 bg-gradient-to-r from-green-500 to-emerald-500 rounded-full"></div>
                      <span className="text-gray-300">{feature}</span>
                    </div>
                  ))}
                </div>
              </>
            )}

            <div className="flex flex-col sm:flex-row gap-4">
              <Link 
                to={activeDemo === 'chat' ? '/chat' : '/admin/login'}
                className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white px-8 py-4 rounded-xl font-semibold flex items-center justify-center space-x-2 transition-all transform hover:scale-105"
              >
                <Play className="w-5 h-5" />
                <span>Try {demoOptions.find(d => d.id === activeDemo)?.name} Demo</span>
                <ArrowRight className="w-5 h-5" />
              </Link>
              
              {activeDemo === 'chat' && (
                <Link 
                  to="/admin/login"
                  className="border border-white/20 text-white px-8 py-4 rounded-xl font-semibold hover:bg-white/10 transition-colors flex items-center justify-center space-x-2"
                >
                  <Settings className="w-5 h-5" />
                  <span>Admin Access</span>
                </Link>
              )}
            </div>
          </div>

          {/* Demo Preview */}
          <div className="bg-gradient-to-br from-purple-500/20 to-pink-500/20 rounded-xl p-8 border border-purple-500/30">
            {activeDemo === 'chat' && (
              <div className="bg-white rounded-lg shadow-2xl overflow-hidden">
                {/* Chat Header */}
                <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white p-4">
                  <div className="flex items-center space-x-3">
                    <img 
                      src="https://www.axiestudio.se/Axiestudiologo.jpg" 
                      alt="Axie Studio" 
                      className="w-10 h-10 rounded-full object-cover"
                    />
                    <div>
                      <h4 className="font-semibold">AI Assistant</h4>
                      <p className="text-sm opacity-90">Powered by Axie Studio</p>
                    </div>
                    <div className="ml-auto flex items-center space-x-1">
                      <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                      <span className="text-xs">Online</span>
                    </div>
                  </div>
                </div>
                
                {/* Chat Messages */}
                <div className="h-80 p-4 space-y-4 overflow-y-auto bg-gray-50">
                  <div className="flex items-start space-x-3">
                    <div className="w-8 h-8 bg-gradient-to-r from-purple-600 to-pink-600 rounded-full flex items-center justify-center">
                      <MessageCircle className="w-4 h-4 text-white" />
                    </div>
                    <div className="bg-white rounded-lg p-3 shadow-sm max-w-[80%]">
                      <p className="text-sm text-gray-800">Hello! I'm your AI assistant. How can I help you today?</p>
                    </div>
                  </div>
                  
                  <div className="flex items-start space-x-3 justify-end">
                    <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg p-3 max-w-[80%]">
                      <p className="text-sm">I'd like to know more about your AI chat platform</p>
                    </div>
                    <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
                      <Users className="w-4 h-4 text-gray-600" />
                    </div>
                  </div>
                  
                  <div className="flex items-start space-x-3">
                    <div className="w-8 h-8 bg-gradient-to-r from-purple-600 to-pink-600 rounded-full flex items-center justify-center">
                      <MessageCircle className="w-4 h-4 text-white" />
                    </div>
                    <div className="bg-white rounded-lg p-3 shadow-sm max-w-[80%]">
                      <p className="text-sm text-gray-800">Great! Our platform offers enterprise-grade AI chat solutions with easy embedding, custom branding, and powerful analytics. Would you like to see a live demo?</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2 text-gray-500 text-xs">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                    </div>
                    <span>AI is typing...</span>
                  </div>
                </div>
                
                {/* Chat Input */}
                <div className="p-4 border-t bg-white">
                  <div className="flex items-center space-x-3">
                    <input 
                      type="text" 
                      placeholder="Type your message..." 
                      className="flex-1 px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                      disabled
                    />
                    <button className="bg-gradient-to-r from-purple-600 to-pink-600 text-white p-3 rounded-lg hover:scale-105 transition-transform">
                      <ArrowRight className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              </div>
            )}

            {activeDemo === 'admin' && (
              <div className="bg-gray-900 rounded-lg p-6 text-center">
                <div className="text-white text-lg font-semibold mb-4">Admin Dashboard Preview</div>
                <div className="grid grid-cols-2 gap-4 mb-6">
                  <div className="bg-purple-600/20 rounded-lg p-4">
                    <div className="text-purple-300 text-sm">Active Chats</div>
                    <div className="text-white text-2xl font-bold">247</div>
                  </div>
                  <div className="bg-blue-600/20 rounded-lg p-4">
                    <div className="text-blue-300 text-sm">Response Time</div>
                    <div className="text-white text-2xl font-bold">0.8s</div>
                  </div>
                </div>
                <Link 
                  to="/admin/login" 
                  className="inline-flex items-center space-x-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white px-6 py-3 rounded-lg font-medium hover:scale-105 transition-transform"
                >
                  <Settings className="w-4 h-4" />
                  <span>Access Full Dashboard</span>
                </Link>
              </div>
            )}

            {activeDemo === 'analytics' && (
              <div className="bg-gray-900 rounded-lg p-6">
                <div className="text-white text-lg font-semibold mb-4 text-center">Analytics Overview</div>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-300">Conversations Today</span>
                    <span className="text-green-400 font-semibold">+23%</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div className="bg-gradient-to-r from-green-500 to-emerald-500 h-2 rounded-full" style={{width: '75%'}}></div>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-300">Satisfaction Score</span>
                    <span className="text-blue-400 font-semibold">4.8/5</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div className="bg-gradient-to-r from-blue-500 to-cyan-500 h-2 rounded-full" style={{width: '96%'}}></div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
};

export default AxieDemo;
