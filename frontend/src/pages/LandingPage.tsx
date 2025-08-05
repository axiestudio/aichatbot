import React, { useState, useEffect } from 'react';
import { MessageCircle, Settings } from 'lucide-react';
import ChatInterface from './ChatInterface';

export default function LandingPage() {
  const [isEmbedded, setIsEmbedded] = useState(false);

  useEffect(() => {
    // Check if running in iframe
    setIsEmbedded(window.self !== window.top);
  }, []);

  return (
    <div className={`min-h-screen bg-white ${isEmbedded ? 'p-0' : 'p-4'}`}>
      {/* Header - only show if not embedded */}
      {!isEmbedded && (
        <div className="flex justify-between items-center mb-4 px-4 py-2 bg-gray-50 rounded-lg">
          <div className="flex items-center space-x-2">
            <MessageCircle className="w-6 h-6 text-blue-500" />
            <h1 className="text-lg font-semibold text-gray-900">AI Chat Assistant</h1>
          </div>
          <a
            href="/admin"
            className="flex items-center space-x-1 px-3 py-1 text-sm text-gray-600 hover:text-gray-900 transition-colors"
          >
            <Settings className="w-4 h-4" />
            <span>Admin</span>
          </a>
        </div>
      )}

      {/* Chat Interface - Full Screen */}
      <div className={`${isEmbedded ? 'h-screen' : 'h-[calc(100vh-120px)]'} w-full`}>
        <ChatInterface />
      </div>
    </div>
  );
}
