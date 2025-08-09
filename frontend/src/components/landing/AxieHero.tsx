import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  MessageCircle, 
  Sparkles, 
  Play, 
  Code, 
  ArrowRight,
  Menu,
  X
} from 'lucide-react';

const AxieHero = () => {
  const [isVisible, setIsVisible] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  useEffect(() => {
    setIsVisible(true);
  }, []);

  return (
    <>
      {/* Professional Navigation */}
      <nav className="fixed top-0 w-full z-50 bg-white/95 backdrop-blur-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              <img
                src="https://www.axiestudio.se/Axiestudiologo.jpg"
                alt="Axie Studio"
                className="h-8 w-8 rounded-lg object-cover"
              />
              <span className="text-xl font-semibold text-gray-900">Axie Studio</span>
            </div>
            
            {/* Professional Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-8">
              <a href="#features" className="text-gray-600 hover:text-gray-900 transition-colors font-medium">Features</a>
              <a href="#demo" className="text-gray-600 hover:text-gray-900 transition-colors font-medium">Demo</a>
              <a href="#pricing" className="text-gray-600 hover:text-gray-900 transition-colors font-medium">Pricing</a>
              <Link
                to="/admin/login"
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors font-medium"
              >
                Admin Login
              </Link>
            </div>

            {/* Mobile menu button */}
            <div className="md:hidden">
              <button
                onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                className="text-white p-2"
              >
                {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
              </button>
            </div>
          </div>

          {/* Mobile Navigation */}
          {isMobileMenuOpen && (
            <div className="md:hidden bg-black/90 backdrop-blur-md border-t border-white/10">
              <div className="px-2 pt-2 pb-3 space-y-1">
                <a href="#features" className="block px-3 py-2 text-gray-300 hover:text-white">Features</a>
                <a href="#demo" className="block px-3 py-2 text-gray-300 hover:text-white">Demo</a>
                <a href="#embedding" className="block px-3 py-2 text-gray-300 hover:text-white">Embedding</a>
                <a href="#pricing" className="block px-3 py-2 text-gray-300 hover:text-white">Pricing</a>
                <Link 
                  to="/admin/login" 
                  className="block px-3 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg mt-2"
                >
                  Admin Login
                </Link>
              </div>
            </div>
          )}
        </div>
      </nav>

      {/* Professional Hero Section */}
      <section className="pt-24 pb-16 px-4 sm:px-6 lg:px-8 bg-gradient-to-b from-gray-50 to-white">
        <div className="max-w-7xl mx-auto">
          <div className={`text-center transition-all duration-1000 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
            {/* Professional Badge */}
            <div className="inline-flex items-center space-x-2 bg-blue-50 text-blue-700 px-4 py-2 rounded-full mb-8 border border-blue-200">
              <MessageSquare className="w-4 h-4" />
              <span className="text-sm font-medium">Enterprise AI Chat Platform</span>
            </div>

            {/* Clean Main Heading */}
            <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold text-gray-900 mb-6 leading-tight">
              Professional AI Chat
              <br />
              <span className="text-blue-600">
                For Your Business
              </span>
            </h1>

            {/* Professional Subheading */}
            <p className="text-lg md:text-xl text-gray-600 mb-12 max-w-3xl mx-auto leading-relaxed">
              Deploy intelligent AI conversations on any website with enterprise-grade security,
              advanced analytics, and complete customization control.
            </p>
            
            {/* Professional CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-16">
              <Link
                to="/chat"
                className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-lg font-medium flex items-center space-x-2 transition-colors shadow-sm"
              >
                <Play className="w-5 h-5" />
                <span>Try Demo</span>
              </Link>
              <a
                href="#features"
                className="border border-gray-300 text-gray-700 hover:bg-gray-50 px-8 py-3 rounded-lg font-medium flex items-center space-x-2 transition-colors"
              >
                <ArrowRight className="w-5 h-5" />
                <span>Learn More</span>
              </a>
            </div>

            {/* Interactive Demo Preview */}
            <div className="max-w-4xl mx-auto">
              <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-8 shadow-2xl">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-xl font-semibold text-white">Live Chat Widget Preview</h3>
                  <div className="flex space-x-2">
                    <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                    <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                    <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  </div>
                </div>
                
                <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-xl p-6 min-h-[300px] flex items-center justify-center relative">
                  {/* Mock Website */}
                  <div className="absolute inset-4 bg-white rounded-lg opacity-10"></div>
                  
                  {/* Chat Widget */}
                  <div className="relative z-10 bg-white rounded-lg shadow-2xl w-80 h-96 flex flex-col">
                    {/* Chat Header */}
                    <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white p-4 rounded-t-lg">
                      <div className="flex items-center space-x-3">
                        <img 
                          src="https://www.axiestudio.se/Axiestudiologo.jpg" 
                          alt="Axie Studio" 
                          className="w-8 h-8 rounded-full"
                        />
                        <div>
                          <h4 className="font-semibold">AI Assistant</h4>
                          <p className="text-xs opacity-90">Powered by Axie Studio</p>
                        </div>
                      </div>
                    </div>
                    
                    {/* Chat Messages */}
                    <div className="flex-1 p-4 space-y-3 overflow-hidden">
                      <div className="bg-gray-100 rounded-lg p-3 max-w-[80%]">
                        <p className="text-sm text-gray-800">Hello! How can I help you today?</p>
                      </div>
                      <div className="bg-purple-100 rounded-lg p-3 max-w-[80%] ml-auto">
                        <p className="text-sm text-gray-800">Tell me about your services</p>
                      </div>
                      <div className="bg-gray-100 rounded-lg p-3 max-w-[80%]">
                        <p className="text-sm text-gray-800">I'd be happy to help! We offer enterprise AI chat solutions...</p>
                      </div>
                    </div>
                    
                    {/* Chat Input */}
                    <div className="p-4 border-t">
                      <div className="flex items-center space-x-2">
                        <input 
                          type="text" 
                          placeholder="Type your message..." 
                          className="flex-1 px-3 py-2 border rounded-lg text-sm"
                          disabled
                        />
                        <button className="bg-purple-600 text-white p-2 rounded-lg">
                          <ArrowRight className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </>
  );
};

export default AxieHero;
