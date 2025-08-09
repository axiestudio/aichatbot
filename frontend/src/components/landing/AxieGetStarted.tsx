import React from 'react';
import { Link } from 'react-router-dom';
import {
  ArrowRight,
  MessageCircle,
  Settings,
  Code,
  Sparkles,
  CheckCircle,
  Mail,
  Phone
} from 'lucide-react';

interface Step {
  number: string;
  title: string;
  description: string;
  icon: React.ReactNode;
}

interface Plan {
  name: string;
  price: string;
  period: string;
  description: string;
  features: string[];
  cta: string;
  popular: boolean;
  tier: string;
}

const AxieGetStarted: React.FC = () => {
  const steps: Step[] = [
    {
      number: "01",
      title: "Sign Up",
      description: "Create your admin account and get instant access to the dashboard",
      icon: <Settings className="w-6 h-6" />
    },
    {
      number: "02", 
      title: "Customize",
      description: "Configure your chat widget with your branding and preferences",
      icon: <MessageCircle className="w-6 h-6" />
    },
    {
      number: "03",
      title: "Embed",
      description: "Copy the embed code and add it to your website in minutes",
      icon: <Code className="w-6 h-6" />
    }
  ];

  const plans: Plan[] = [
    {
      name: "Free",
      price: "$0",
      period: "/month",
      description: "Try Axie Studio with branding",
      features: [
        "1,000 conversations/month",
        "Shows 'Powered by Axie Studio'",
        "Basic customization",
        "Email support",
        "Standard AI models"
      ],
      cta: "Start Free",
      popular: false,
      tier: "free"
    },
    {
      name: "Premium",
      price: "$49",
      period: "/month",
      description: "🚀 Remove branding & unlock premium features",
      features: [
        "✨ Remove 'Powered by Axie Studio'",
        "10,000 conversations/month",
        "Advanced customization",
        "Priority support",
        "Premium AI models",
        "Advanced analytics",
        "API access",
        "14-day free trial"
      ],
      cta: "Remove Branding",
      popular: true,
      tier: "premium"
    },
    {
      name: "Enterprise",
      price: "Custom",
      period: "",
      description: "Complete white-label solution",
      features: [
        "✨ Complete branding removal",
        "🎨 Your logo & custom branding",
        "Unlimited conversations",
        "Custom domain support",
        "24/7 dedicated support",
        "Custom AI training",
        "Advanced security & SLA",
        "White-label reseller rights"
      ],
      cta: "Contact Sales",
      popular: false,
      tier: "enterprise"
    }
  ];

  return (
    <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-r from-purple-600/10 to-pink-600/10">
      <div className="max-w-7xl mx-auto">
        {/* Get Started Steps */}
        <div className="text-center mb-20">
          <div className="inline-flex items-center space-x-2 bg-purple-500/20 text-purple-300 px-4 py-2 rounded-full mb-6">
            <Sparkles className="w-4 h-4" />
            <span className="text-sm font-medium">Get Started</span>
          </div>
          
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
            Launch in 3 Simple Steps
          </h2>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto mb-12">
            Get your AI chat widget up and running in minutes, not hours. 
            No technical expertise required.
          </p>

          <div className="grid md:grid-cols-3 gap-8 mb-12">
            {steps.map((step, index) => (
              <div key={index} className="relative">
                {/* Connection Line */}
                {index < steps.length - 1 && (
                  <div className="hidden md:block absolute top-12 left-full w-full h-0.5 bg-gradient-to-r from-purple-500 to-pink-500 z-0"></div>
                )}
                
                <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-8 relative z-10 hover:bg-white/10 transition-all">
                  <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white w-16 h-16 rounded-xl flex items-center justify-center mx-auto mb-6">
                    {step.icon}
                  </div>
                  
                  <div className="text-purple-300 font-bold text-lg mb-2">{step.number}</div>
                  <h3 className="text-xl font-semibold text-white mb-3">{step.title}</h3>
                  <p className="text-gray-300">{step.description}</p>
                </div>
              </div>
            ))}
          </div>

          <Link 
            to="/admin/login" 
            className="inline-flex items-center space-x-2 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white px-8 py-4 rounded-xl font-semibold transition-all transform hover:scale-105 text-lg"
          >
            <Settings className="w-5 h-5" />
            <span>Start Your Free Trial</span>
            <ArrowRight className="w-5 h-5" />
          </Link>
        </div>

        {/* Pricing Section */}
        <div id="pricing" className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
            Simple, Transparent Pricing
          </h2>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto mb-12">
            Choose the plan that fits your needs. All plans include a 14-day free trial.
          </p>

          <div className="grid md:grid-cols-3 gap-8">
            {plans.map((plan, index) => (
              <div 
                key={index}
                className={`relative bg-white/5 backdrop-blur-sm border rounded-xl p-8 hover:bg-white/10 transition-all ${
                  plan.popular 
                    ? 'border-purple-500 scale-105' 
                    : 'border-white/10'
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-6 py-2 rounded-full text-sm font-medium">
                      Most Popular
                    </div>
                  </div>
                )}
                
                <div className="text-center mb-8">
                  <h3 className="text-2xl font-bold text-white mb-2">{plan.name}</h3>
                  <p className="text-gray-400 mb-4">{plan.description}</p>
                  <div className="flex items-baseline justify-center">
                    <span className="text-4xl font-bold text-white">{plan.price}</span>
                    <span className="text-gray-400 ml-1">{plan.period}</span>
                  </div>
                </div>

                <ul className="space-y-3 mb-8">
                  {plan.features.map((feature, featureIndex) => (
                    <li key={featureIndex} className="flex items-center space-x-3">
                      <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0" />
                      <span className="text-gray-300">{feature}</span>
                    </li>
                  ))}
                </ul>

                <Link
                  to={plan.tier === "enterprise" ? "mailto:contact@axiestudio.se" :
                      plan.tier === "free" ? "/admin/login" : "/admin/billing"}
                  className={`block w-full text-center py-3 px-6 rounded-lg font-semibold transition-all ${
                    plan.popular
                      ? 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white'
                      : 'border border-white/20 text-white hover:bg-white/10'
                  }`}
                >
                  {plan.cta}
                </Link>
              </div>
            ))}
          </div>
        </div>

        {/* Contact Section */}
        <div className="bg-gradient-to-r from-purple-600/20 to-pink-600/20 border border-purple-500/30 rounded-xl p-8 text-center">
          <h3 className="text-2xl font-bold text-white mb-4">
            Need a Custom Solution?
          </h3>
          <p className="text-gray-300 mb-6 max-w-2xl mx-auto">
            Our enterprise team can help you build a custom AI chat solution 
            tailored to your specific needs and requirements.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a 
              href="mailto:contact@axiestudio.se"
              className="inline-flex items-center space-x-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white px-6 py-3 rounded-lg font-medium hover:scale-105 transition-transform"
            >
              <Mail className="w-4 h-4" />
              <span>contact@axiestudio.se</span>
            </a>
            
            <a 
              href="tel:+46123456789"
              className="inline-flex items-center space-x-2 border border-white/20 text-white px-6 py-3 rounded-lg font-medium hover:bg-white/10 transition-colors"
            >
              <Phone className="w-4 h-4" />
              <span>Schedule a Call</span>
            </a>
          </div>
        </div>
      </div>
    </section>
  );
};

export default AxieGetStarted;
