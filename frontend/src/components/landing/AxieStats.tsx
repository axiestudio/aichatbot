import React from 'react';
import { 
  Shield, 
  Zap, 
  Users, 
  Globe,
  MessageCircle,
  BarChart3,
  Clock,
  Award
} from 'lucide-react';

const AxieStats = () => {
  const stats = [
    {
      number: "99.9%",
      label: "Uptime SLA",
      description: "Enterprise reliability you can count on",
      icon: <Shield className="w-8 h-8" />,
      color: "from-green-500 to-emerald-500"
    },
    {
      number: "<200ms",
      label: "Response Time",
      description: "Lightning-fast AI responses",
      icon: <Zap className="w-8 h-8" />,
      color: "from-yellow-500 to-orange-500"
    },
    {
      number: "1000+",
      label: "Conversations/sec",
      description: "Handle massive scale effortlessly",
      icon: <Users className="w-8 h-8" />,
      color: "from-blue-500 to-cyan-500"
    },
    {
      number: "50+",
      label: "Languages",
      description: "Global reach with multilingual support",
      icon: <Globe className="w-8 h-8" />,
      color: "from-purple-500 to-pink-500"
    }
  ];

  const achievements = [
    {
      title: "Enterprise Ready",
      description: "SOC 2 Type II compliant with enterprise-grade security",
      icon: <Award className="w-6 h-6" />
    },
    {
      title: "24/7 Monitoring",
      description: "Continuous monitoring with real-time alerting",
      icon: <Clock className="w-6 h-6" />
    },
    {
      title: "Global Scale",
      description: "Deployed across 6 continents with edge computing",
      icon: <Globe className="w-6 h-6" />
    },
    {
      title: "AI-Powered",
      description: "Latest GPT-4 and Claude models with custom fine-tuning",
      icon: <MessageCircle className="w-6 h-6" />
    }
  ];

  return (
    <section className="py-20 px-4 sm:px-6 lg:px-8 relative">
      {/* Background Effects */}
      <div className="absolute inset-0 bg-gradient-to-r from-purple-500/5 via-transparent to-pink-500/5"></div>
      
      <div className="max-w-7xl mx-auto relative z-10">
        <div className="text-center mb-16">
          <div className="inline-flex items-center space-x-2 bg-purple-500/20 text-purple-300 px-4 py-2 rounded-full mb-6">
            <BarChart3 className="w-4 h-4" />
            <span className="text-sm font-medium">Performance Metrics</span>
          </div>
          
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
            Built for Enterprise Scale
          </h2>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto">
            Trusted by companies worldwide with industry-leading performance, 
            security, and reliability metrics.
          </p>
        </div>

        {/* Main Stats */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 mb-16">
          {stats.map((stat, index) => (
            <div 
              key={index}
              className="group bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-8 text-center hover:bg-white/10 transition-all duration-300 hover:scale-105"
            >
              <div className={`inline-flex p-4 rounded-xl bg-gradient-to-r ${stat.color} mb-6 group-hover:scale-110 transition-transform duration-300`}>
                <div className="text-white">{stat.icon}</div>
              </div>
              
              <div className="text-4xl md:text-5xl font-bold text-white mb-2 group-hover:text-purple-300 transition-colors">
                {stat.number}
              </div>
              
              <div className="text-lg font-semibold text-purple-300 mb-2">
                {stat.label}
              </div>
              
              <div className="text-sm text-gray-400">
                {stat.description}
              </div>
            </div>
          ))}
        </div>

        {/* Achievements Grid */}
        <div className="grid md:grid-cols-2 gap-8 mb-16">
          {achievements.map((achievement, index) => (
            <div 
              key={index}
              className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6 flex items-start space-x-4 hover:bg-white/10 transition-all"
            >
              <div className="bg-gradient-to-r from-purple-600 to-pink-600 p-3 rounded-lg flex-shrink-0">
                <div className="text-white">{achievement.icon}</div>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white mb-2">{achievement.title}</h3>
                <p className="text-gray-300">{achievement.description}</p>
              </div>
            </div>
          ))}
        </div>

        {/* Trust Indicators */}
        <div className="bg-gradient-to-r from-purple-600/10 to-pink-600/10 border border-purple-500/20 rounded-xl p-8">
          <div className="text-center mb-8">
            <h3 className="text-2xl font-bold text-white mb-4">Trusted by Industry Leaders</h3>
            <p className="text-gray-300">Join hundreds of companies using Axie Studio's AI chat platform</p>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 items-center opacity-60">
            {/* Placeholder for company logos */}
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="bg-white/10 rounded-lg h-16 flex items-center justify-center">
                <div className="text-white/50 font-semibold">Company {i}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Additional Metrics */}
        <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
          <div>
            <div className="text-3xl font-bold text-white mb-2">500M+</div>
            <div className="text-purple-300 font-medium mb-1">Messages Processed</div>
            <div className="text-gray-400 text-sm">Across all platforms</div>
          </div>
          
          <div>
            <div className="text-3xl font-bold text-white mb-2">150+</div>
            <div className="text-purple-300 font-medium mb-1">Countries</div>
            <div className="text-gray-400 text-sm">Global deployment</div>
          </div>
          
          <div>
            <div className="text-3xl font-bold text-white mb-2">4.9/5</div>
            <div className="text-purple-300 font-medium mb-1">Customer Rating</div>
            <div className="text-gray-400 text-sm">Based on 1000+ reviews</div>
          </div>
          
          <div>
            <div className="text-3xl font-bold text-white mb-2">24/7</div>
            <div className="text-purple-300 font-medium mb-1">Support</div>
            <div className="text-gray-400 text-sm">Enterprise support included</div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default AxieStats;
