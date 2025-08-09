import React from 'react';
import { 
  MessageCircle, 
  Zap, 
  Shield, 
  Globe, 
  Code, 
  BarChart3,
  Palette,
  Settings,
  Lock,
  Smartphone,
  Cloud,
  Users
} from 'lucide-react';

interface Feature {
  icon: React.ReactNode;
  title: string;
  description: string;
  color: string;
}

const AxieFeatures = () => {
  const features: Feature[] = [
    {
      icon: <MessageCircle className="w-8 h-8" />,
      title: "Embeddable Chat Widget",
      description: "Drop-in chat widget that works on any website with just a few lines of code. Fully responsive and customizable.",
      color: "from-purple-500 to-pink-500"
    },
    {
      icon: <Zap className="w-8 h-8" />,
      title: "Real-time AI Responses",
      description: "Powered by GPT-4, Claude, and other leading AI models with sub-second response times and intelligent context awareness.",
      color: "from-blue-500 to-cyan-500"
    },
    {
      icon: <Shield className="w-8 h-8" />,
      title: "Enterprise Security",
      description: "Zero-trust architecture with threat detection, behavioral analysis, and enterprise-grade data protection.",
      color: "from-green-500 to-emerald-500"
    },
    {
      icon: <Globe className="w-8 h-8" />,
      title: "Multi-tenant Architecture",
      description: "Isolated environments for each client with custom branding, configurations, and complete data separation.",
      color: "from-orange-500 to-red-500"
    },
    {
      icon: <BarChart3 className="w-8 h-8" />,
      title: "Advanced Analytics",
      description: "Real-time insights, conversation analytics, performance metrics, and detailed reporting dashboards.",
      color: "from-indigo-500 to-purple-500"
    },
    {
      icon: <Code className="w-8 h-8" />,
      title: "Easy Integration",
      description: "RESTful APIs, webhooks, comprehensive documentation, and SDKs for popular platforms.",
      color: "from-teal-500 to-blue-500"
    },
    {
      icon: <Palette className="w-8 h-8" />,
      title: "White-label Branding",
      description: "Complete customization with your brand colors, logos, fonts, and messaging to match your identity.",
      color: "from-pink-500 to-rose-500"
    },
    {
      icon: <Settings className="w-8 h-8" />,
      title: "Admin Dashboard",
      description: "Powerful admin interface for managing configurations, monitoring conversations, and controlling access.",
      color: "from-gray-500 to-slate-500"
    },
    {
      icon: <Lock className="w-8 h-8" />,
      title: "Data Privacy",
      description: "GDPR compliant with end-to-end encryption, data residency options, and complete privacy controls.",
      color: "from-yellow-500 to-orange-500"
    },
    {
      icon: <Smartphone className="w-8 h-8" />,
      title: "Mobile Optimized",
      description: "Fully responsive design that works perfectly on desktop, tablet, and mobile devices.",
      color: "from-violet-500 to-purple-500"
    },
    {
      icon: <Cloud className="w-8 h-8" />,
      title: "Cloud Infrastructure",
      description: "Scalable cloud infrastructure with 99.9% uptime, global CDN, and automatic scaling.",
      color: "from-sky-500 to-blue-500"
    },
    {
      icon: <Users className="w-8 h-8" />,
      title: "Team Collaboration",
      description: "Multi-user support with role-based access control, team management, and collaboration tools.",
      color: "from-emerald-500 to-teal-500"
    }
  ];

  return (
    <section id="features" className="py-20 px-4 sm:px-6 lg:px-8 relative">
      {/* Background Effects */}
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-purple-500/5 to-transparent"></div>
      
      <div className="max-w-7xl mx-auto relative z-10">
        <div className="text-center mb-16">
          <div className="inline-flex items-center space-x-2 bg-purple-500/20 text-purple-300 px-4 py-2 rounded-full mb-6">
            <Zap className="w-4 h-4" />
            <span className="text-sm font-medium">Powerful Features</span>
          </div>
          
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
            Enterprise-Grade Features
          </h2>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto">
            Built for scale, security, and seamless integration. Everything you need to deploy 
            AI chat across your organization.
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div 
              key={index}
              className="group bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6 hover:bg-white/10 transition-all duration-300 hover:scale-105 hover:shadow-2xl"
            >
              {/* Icon with gradient background */}
              <div className={`inline-flex p-3 rounded-xl bg-gradient-to-r ${feature.color} mb-4 group-hover:scale-110 transition-transform duration-300`}>
                <div className="text-white">{feature.icon}</div>
              </div>
              
              <h3 className="text-xl font-semibold text-white mb-3 group-hover:text-purple-300 transition-colors">
                {feature.title}
              </h3>
              
              <p className="text-gray-300 leading-relaxed">
                {feature.description}
              </p>
            </div>
          ))}
        </div>

        {/* Additional Feature Highlights */}
        <div className="mt-20 grid md:grid-cols-3 gap-8">
          <div className="text-center">
            <div className="text-4xl font-bold text-white mb-2">99.9%</div>
            <div className="text-purple-300 font-medium mb-2">Uptime SLA</div>
            <div className="text-gray-400 text-sm">Enterprise reliability you can count on</div>
          </div>
          
          <div className="text-center">
            <div className="text-4xl font-bold text-white mb-2">&lt;200ms</div>
            <div className="text-purple-300 font-medium mb-2">Response Time</div>
            <div className="text-gray-400 text-sm">Lightning-fast AI responses</div>
          </div>
          
          <div className="text-center">
            <div className="text-4xl font-bold text-white mb-2">1000+</div>
            <div className="text-purple-300 font-medium mb-2">Conversations/sec</div>
            <div className="text-gray-400 text-sm">Handle massive scale effortlessly</div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default AxieFeatures;
