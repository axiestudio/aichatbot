import React, { useState, useEffect } from 'react';
import { 
  CreditCard, 
  Crown, 
  Zap, 
  Check, 
  X, 
  Star,
  Calendar,
  TrendingUp,
  Shield,
  Sparkles,
  AlertTriangle,
  ExternalLink,
  RefreshCw
} from 'lucide-react';
import { useAuthStore } from '../../stores/authStore';

const BillingManager = () => {
  const { user } = useAuthStore();
  const [loading, setLoading] = useState(false);
  const [subscription, setSubscription] = useState(null);
  const [plans, setPlans] = useState([]);
  const [upgrading, setUpgrading] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState(null);
  const [billingCycle, setBillingCycle] = useState('monthly');

  const tenantId = user?.tenantId || user?.id || 'demo-tenant';

  useEffect(() => {
    loadSubscriptionData();
    loadPlans();
  }, [tenantId]);

  const loadSubscriptionData = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/v1/subscription/${tenantId}/status`);
      if (response.ok) {
        const data = await response.json();
        setSubscription(data);
      }
    } catch (error) {
      console.error('Failed to load subscription:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadPlans = async () => {
    try {
      const response = await fetch('/api/v1/subscription/plans');
      if (response.ok) {
        const data = await response.json();
        setPlans(data.plans);
      }
    } catch (error) {
      console.error('Failed to load plans:', error);
    }
  };

  const handleUpgrade = async (planTier) => {
    try {
      setUpgrading(true);
      setSelectedPlan(planTier);

      if (planTier === 'free') {
        // Direct downgrade to free
        const response = await fetch(`/api/v1/subscription/${tenantId}/upgrade`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ tier: planTier })
        });

        if (response.ok) {
          await loadSubscriptionData();
          alert('Successfully downgraded to free tier');
        }
      } else {
        // Create Stripe checkout for premium tiers
        const response = await fetch(`/api/v1/subscription/${tenantId}/checkout`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            tier: planTier,
            billingCycle: billingCycle
          })
        });

        if (response.ok) {
          const data = await response.json();
          // Redirect to Stripe checkout
          window.location.href = data.checkout_url;
        } else {
          throw new Error('Failed to create checkout session');
        }
      }
    } catch (error) {
      console.error('Failed to upgrade:', error);
      alert('Failed to upgrade subscription. Please try again.');
    } finally {
      setUpgrading(false);
      setSelectedPlan(null);
    }
  };

  const startTrial = async (tier) => {
    try {
      const response = await fetch(`/api/v1/subscription/${tenantId}/trial/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tier })
      });

      if (response.ok) {
        await loadSubscriptionData();
        alert('14-day trial started! You can now remove branding.');
      }
    } catch (error) {
      console.error('Failed to start trial:', error);
      alert('Failed to start trial. Please try again.');
    }
  };

  const openBillingPortal = async () => {
    try {
      const response = await fetch(`/api/v1/subscription/${tenantId}/billing-portal`);
      if (response.ok) {
        const data = await response.json();
        window.open(data.url, '_blank');
      }
    } catch (error) {
      console.error('Failed to open billing portal:', error);
    }
  };

  const getTierIcon = (tier) => {
    switch (tier) {
      case 'free': return <Zap className="w-5 h-5" />;
      case 'premium': return <Crown className="w-5 h-5" />;
      case 'enterprise': return <Star className="w-5 h-5" />;
      default: return <Zap className="w-5 h-5" />;
    }
  };

  const getTierColor = (tier) => {
    switch (tier) {
      case 'free': return 'text-gray-600';
      case 'premium': return 'text-purple-600';
      case 'enterprise': return 'text-yellow-600';
      default: return 'text-gray-600';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-8 h-8 animate-spin text-purple-600" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 flex items-center space-x-2">
              <CreditCard className="w-6 h-6 text-purple-600" />
              <span>Billing & Subscription</span>
            </h1>
            <p className="text-gray-600 mt-1">
              Manage your subscription and remove Axie Studio branding
            </p>
          </div>
          
          {subscription?.subscription?.stripe_customer_id && (
            <button 
              onClick={openBillingPortal}
              className="flex items-center space-x-2 border border-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <ExternalLink className="w-4 h-4" />
              <span>Billing Portal</span>
            </button>
          )}
        </div>
      </div>

      {/* Current Subscription Status */}
      {subscription && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Current Subscription</h2>
          
          <div className="grid md:grid-cols-3 gap-6">
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center space-x-2 mb-2">
                {getTierIcon(subscription.subscription.tier)}
                <span className={`font-semibold capitalize ${getTierColor(subscription.subscription.tier)}`}>
                  {subscription.subscription.tier} Plan
                </span>
              </div>
              <div className="text-2xl font-bold text-gray-900">
                ${subscription.subscription.pricePerMonth}/month
              </div>
            </div>
            
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center space-x-2 mb-2">
                <TrendingUp className="w-5 h-5 text-green-600" />
                <span className="font-semibold text-gray-700">Usage</span>
              </div>
              <div className="text-2xl font-bold text-gray-900">
                {subscription.usage.unlimited ? 'Unlimited' : 
                  `${subscription.usage.conversationsUsed}/${subscription.usage.conversationsLimit}`
                }
              </div>
              {!subscription.usage.unlimited && (
                <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                  <div 
                    className="bg-green-600 h-2 rounded-full" 
                    style={{ width: `${Math.min(100, subscription.usage.usagePercentage)}%` }}
                  ></div>
                </div>
              )}
            </div>
            
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center space-x-2 mb-2">
                <Shield className="w-5 h-5 text-blue-600" />
                <span className="font-semibold text-gray-700">Branding</span>
              </div>
              <div className="text-sm">
                {subscription.permissions.canRemoveBranding ? (
                  <span className="text-green-600 font-semibold">✓ Branding Removed</span>
                ) : (
                  <span className="text-orange-600 font-semibold">⚠ Shows "Powered by Axie Studio"</span>
                )}
              </div>
              {subscription.permissions.isTrial && (
                <div className="text-xs text-blue-600 mt-1">
                  Trial: {subscription.permissions.trialDaysLeft} days left
                </div>
              )}
            </div>
          </div>

          {/* Trial Banner */}
          {subscription.permissions.isTrial && (
            <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-center space-x-2">
                <Sparkles className="w-5 h-5 text-blue-600" />
                <span className="font-semibold text-blue-900">
                  Premium Trial Active - {subscription.permissions.trialDaysLeft} days remaining
                </span>
              </div>
              <p className="text-blue-700 text-sm mt-1">
                You're currently enjoying premium features including removed branding. 
                Upgrade before your trial ends to keep these features.
              </p>
            </div>
          )}

          {/* Usage Warning */}
          {subscription.usage.usagePercentage > 80 && !subscription.usage.unlimited && (
            <div className="mt-6 bg-orange-50 border border-orange-200 rounded-lg p-4">
              <div className="flex items-center space-x-2">
                <AlertTriangle className="w-5 h-5 text-orange-600" />
                <span className="font-semibold text-orange-900">
                  Usage Warning
                </span>
              </div>
              <p className="text-orange-700 text-sm mt-1">
                You've used {subscription.usage.usagePercentage.toFixed(1)}% of your monthly conversation limit. 
                Consider upgrading to avoid service interruption.
              </p>
            </div>
          )}
        </div>
      )}

      {/* Subscription Plans */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="text-center mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            💰 Remove "Powered by Axie Studio" Branding
          </h2>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Upgrade to Premium or Enterprise to remove our branding from your chat widget 
            and provide a completely white-label experience for your customers.
          </p>
          
          {/* Billing Cycle Toggle */}
          <div className="flex items-center justify-center space-x-4 mt-6">
            <span className={`text-sm ${billingCycle === 'monthly' ? 'text-gray-900 font-semibold' : 'text-gray-500'}`}>
              Monthly
            </span>
            <button
              onClick={() => setBillingCycle(billingCycle === 'monthly' ? 'yearly' : 'monthly')}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                billingCycle === 'yearly' ? 'bg-purple-600' : 'bg-gray-200'
              }`}
            >
              <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                billingCycle === 'yearly' ? 'translate-x-6' : 'translate-x-1'
              }`} />
            </button>
            <span className={`text-sm ${billingCycle === 'yearly' ? 'text-gray-900 font-semibold' : 'text-gray-500'}`}>
              Yearly
              <span className="text-green-600 text-xs ml-1">(Save 17%)</span>
            </span>
          </div>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {plans.map((plan) => (
            <div 
              key={plan.id}
              className={`relative border rounded-xl p-6 ${
                plan.popular 
                  ? 'border-purple-500 bg-purple-50' 
                  : 'border-gray-200 bg-white'
              }`}
            >
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                  <div className="bg-purple-600 text-white px-4 py-1 rounded-full text-sm font-medium">
                    Most Popular
                  </div>
                </div>
              )}
              
              <div className="text-center mb-6">
                <div className={`inline-flex p-3 rounded-xl mb-4 ${getTierColor(plan.tier)}`}>
                  {getTierIcon(plan.tier)}
                </div>
                <h3 className="text-xl font-bold text-gray-900">{plan.name}</h3>
                <p className="text-gray-600 text-sm mt-1">{plan.description}</p>
                
                <div className="mt-4">
                  <div className="text-3xl font-bold text-gray-900">
                    ${billingCycle === 'monthly' ? plan.priceMonthly : Math.round(plan.priceYearly / 12)}
                  </div>
                  <div className="text-gray-500 text-sm">
                    per month{billingCycle === 'yearly' && ', billed yearly'}
                  </div>
                </div>
              </div>

              <ul className="space-y-3 mb-6">
                <li className="flex items-center space-x-2">
                  {plan.features.removeBranding ? (
                    <Check className="w-4 h-4 text-green-600" />
                  ) : (
                    <X className="w-4 h-4 text-red-500" />
                  )}
                  <span className="text-sm">Remove "Powered by Axie Studio"</span>
                </li>
                <li className="flex items-center space-x-2">
                  {plan.features.customBranding ? (
                    <Check className="w-4 h-4 text-green-600" />
                  ) : (
                    <X className="w-4 h-4 text-red-500" />
                  )}
                  <span className="text-sm">Custom branding & colors</span>
                </li>
                <li className="flex items-center space-x-2">
                  <Check className="w-4 h-4 text-green-600" />
                  <span className="text-sm">
                    {plan.features.conversationsLimit === -1 
                      ? 'Unlimited conversations' 
                      : `${plan.features.conversationsLimit.toLocaleString()} conversations/month`
                    }
                  </span>
                </li>
                <li className="flex items-center space-x-2">
                  {plan.features.advancedAnalytics ? (
                    <Check className="w-4 h-4 text-green-600" />
                  ) : (
                    <X className="w-4 h-4 text-red-500" />
                  )}
                  <span className="text-sm">Advanced analytics</span>
                </li>
                <li className="flex items-center space-x-2">
                  {plan.features.prioritySupport ? (
                    <Check className="w-4 h-4 text-green-600" />
                  ) : (
                    <X className="w-4 h-4 text-red-500" />
                  )}
                  <span className="text-sm">Priority support</span>
                </li>
              </ul>

              <div className="space-y-2">
                {subscription?.subscription?.tier === plan.tier ? (
                  <div className="w-full bg-gray-100 text-gray-600 py-3 px-4 rounded-lg text-center font-medium">
                    Current Plan
                  </div>
                ) : (
                  <>
                    <button
                      onClick={() => handleUpgrade(plan.tier)}
                      disabled={upgrading && selectedPlan === plan.tier}
                      className={`w-full py-3 px-4 rounded-lg font-medium transition-all ${
                        plan.popular
                          ? 'bg-purple-600 hover:bg-purple-700 text-white'
                          : 'border border-gray-300 text-gray-700 hover:bg-gray-50'
                      } disabled:opacity-50`}
                    >
                      {upgrading && selectedPlan === plan.tier ? (
                        <RefreshCw className="w-4 h-4 animate-spin mx-auto" />
                      ) : (
                        plan.tier === 'free' ? 'Downgrade' : 'Upgrade Now'
                      )}
                    </button>
                    
                    {plan.tier !== 'free' && subscription?.subscription?.tier === 'free' && (
                      <button
                        onClick={() => startTrial(plan.tier)}
                        className="w-full py-2 px-4 text-sm border border-purple-300 text-purple-600 rounded-lg hover:bg-purple-50 transition-colors"
                      >
                        Start 14-Day Free Trial
                      </button>
                    )}
                  </>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Branding Comparison */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-6">
          🎨 Branding Comparison
        </h2>
        
        <div className="grid md:grid-cols-2 gap-8">
          <div>
            <h3 className="font-semibold text-gray-900 mb-4 flex items-center space-x-2">
              <X className="w-5 h-5 text-red-500" />
              <span>Free Tier (With Branding)</span>
            </h3>
            <div className="bg-gray-100 rounded-lg p-4">
              <div className="bg-white rounded-lg shadow-sm p-4">
                <div className="flex items-center space-x-2 mb-2">
                  <img 
                    src="https://www.axiestudio.se/Axiestudiologo.jpg" 
                    alt="Axie Studio" 
                    className="w-6 h-6 rounded"
                  />
                  <div>
                    <div className="font-semibold text-sm">AI Assistant</div>
                    <div className="text-xs text-gray-600">Powered by Axie Studio</div>
                  </div>
                </div>
                <div className="text-xs text-gray-500">
                  Shows Axie Studio branding to your customers
                </div>
              </div>
            </div>
          </div>
          
          <div>
            <h3 className="font-semibold text-gray-900 mb-4 flex items-center space-x-2">
              <Check className="w-5 h-5 text-green-600" />
              <span>Premium/Enterprise (No Branding)</span>
            </h3>
            <div className="bg-green-50 rounded-lg p-4">
              <div className="bg-white rounded-lg shadow-sm p-4">
                <div className="flex items-center space-x-2 mb-2">
                  <div className="w-6 h-6 bg-blue-600 rounded flex items-center justify-center text-white text-xs font-bold">
                    Y
                  </div>
                  <div>
                    <div className="font-semibold text-sm">Your Assistant</div>
                  </div>
                </div>
                <div className="text-xs text-gray-500">
                  Clean, professional appearance with your branding only
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BillingManager;
