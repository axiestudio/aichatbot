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
      {/* Navigation */}
      <nav className="fixed top-0 w-full z-50 bg-black/20 backdrop-blur-md border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              <img 
                src="https://www.axiestudio.se/Axiestudiologo.jpg" 
                alt="Axie Studio" 
                className="h-10 w-10 rounded-lg object-cover"
              />
              <div className="flex flex-col">
                <span className="text-xl font-bold text-white">Axie Studio</span>
                <span className="text-xs text-purple-300">AI Chat Platform</span>
              </div>
            </div>
            
            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-8">
              <a href="#features" className="text-gray-300 hover:text-white transition-colors">Features</a>
              <a href="#demo" className="text-gray-300 hover:text-white transition-colors">Demo</a>
              <a href="#embedding" className="text-gray-300 hover:text-white transition-colors">Embedding</a>
              <a href="#pricing" className="text-gray-300 hover:text-white transition-colors">Pricing</a>
              <Link 
                to="/admin/login" 
                className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white px-6 py-2 rounded-lg transition-all transform hover:scale-105 font-medium"
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

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
        {/* Background Effects */}
        <div className="absolute inset-0 bg-gradient-to-r from-purple-500/10 to-pink-500/10 blur-3xl"></div>
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-pink-500/20 rounded-full blur-3xl"></div>

        <div className="max-w-7xl mx-auto relative z-10">
          <div className={`text-center transition-all duration-1000 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
            {/* Badge */}
            <div className="inline-flex items-center space-x-2 bg-purple-500/20 text-purple-300 px-6 py-3 rounded-full mb-8 border border-purple-500/30">
              <Sparkles className="w-5 h-5" />
              <span className="text-sm font-medium">Enterprise AI Chat Platform</span>
            </div>
            
            {/* Main Heading */}
            <h1 className="text-5xl md:text-7xl lg:text-8xl font-bold text-white mb-6 leading-tight">
              Embed AI Chat
              <br />
              <span className="bg-gradient-to-r from-purple-400 via-pink-400 to-purple-400 bg-clip-text text-transparent">
                Anywhere
              </span>
            </h1>
            
            {/* Subheading */}
            <p className="text-xl md:text-2xl text-gray-300 mb-12 max-w-4xl mx-auto leading-relaxed">
              The most advanced embeddable AI chat platform. Deploy intelligent conversations 
              on any website with enterprise-grade security and customization.
            </p>
            
            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-6 justify-center items-center mb-16">
              <Link 
                to="/chat" 
                className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white px-10 py-5 rounded-xl font-semibold flex items-center space-x-3 transition-all transform hover:scale-105 text-lg shadow-2xl"
              >
                <Play className="w-6 h-6" />
                <span>Try Live Demo</span>
              </Link>
              <a 
                href="#embedding" 
                className="border-2 border-white/20 text-white px-10 py-5 rounded-xl font-semibold hover:bg-white/10 transition-colors flex items-center space-x-3 text-lg"
              >
                <Code className="w-6 h-6" />
                <span>Get Embed Code</span>
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
