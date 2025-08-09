from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text
from datetime import datetime, timedelta
from enum import Enum
from ..core.database import Base

class SubscriptionTier(str, Enum):
    FREE = "free"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    CANCELED = "canceled"
    PAST_DUE = "past_due"
    TRIALING = "trialing"
    INCOMPLETE = "incomplete"

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, unique=True, index=True, nullable=False)
    
    # Subscription Details
    tier = Column(String, default=SubscriptionTier.FREE)
    status = Column(String, default=SubscriptionStatus.ACTIVE)
    
    # Branding Controls
    remove_branding = Column(Boolean, default=False)
    custom_branding_enabled = Column(Boolean, default=False)
    white_label_enabled = Column(Boolean, default=False)
    
    # Billing Information
    stripe_customer_id = Column(String, nullable=True)
    stripe_subscription_id = Column(String, nullable=True)
    price_per_month = Column(Float, default=0.0)
    
    # Usage Limits
    monthly_conversations_limit = Column(Integer, default=1000)  # Free tier limit
    monthly_conversations_used = Column(Integer, default=0)
    
    # Dates
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    trial_ends_at = Column(DateTime, nullable=True)
    current_period_start = Column(DateTime, default=datetime.utcnow)
    current_period_end = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(days=30))
    
    # Features
    features = Column(Text, nullable=True)  # JSON string of enabled features
    
    def __repr__(self):
        return f"<Subscription(tenant_id='{self.tenant_id}', tier='{self.tier}', status='{self.status}')>"
    
    @property
    def is_premium(self):
        return self.tier in [SubscriptionTier.PREMIUM, SubscriptionTier.ENTERPRISE]
    
    @property
    def can_remove_branding(self):
        return self.is_premium and self.remove_branding
    
    @property
    def is_trial_active(self):
        if not self.trial_ends_at:
            return False
        return datetime.utcnow() < self.trial_ends_at
    
    @property
    def days_until_trial_end(self):
        if not self.trial_ends_at:
            return 0
        delta = self.trial_ends_at - datetime.utcnow()
        return max(0, delta.days)
    
    @property
    def usage_percentage(self):
        if self.monthly_conversations_limit == 0:
            return 0
        return min(100, (self.monthly_conversations_used / self.monthly_conversations_limit) * 100)
    
    @property
    def is_usage_exceeded(self):
        return self.monthly_conversations_used >= self.monthly_conversations_limit

class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Plan Details
    name = Column(String, nullable=False)  # "Free", "Premium", "Enterprise"
    tier = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Pricing
    price_monthly = Column(Float, default=0.0)
    price_yearly = Column(Float, default=0.0)
    
    # Features
    remove_branding = Column(Boolean, default=False)
    custom_branding = Column(Boolean, default=False)
    white_label = Column(Boolean, default=False)
    conversations_limit = Column(Integer, default=1000)
    analytics_advanced = Column(Boolean, default=False)
    priority_support = Column(Boolean, default=False)
    api_access = Column(Boolean, default=True)
    
    # Stripe Integration
    stripe_price_id_monthly = Column(String, nullable=True)
    stripe_price_id_yearly = Column(String, nullable=True)
    
    # Status
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<SubscriptionPlan(name='{self.name}', tier='{self.tier}', price_monthly={self.price_monthly})>"

# Default subscription plans
DEFAULT_PLANS = [
    {
        "name": "Free",
        "tier": SubscriptionTier.FREE,
        "description": "Perfect for trying out Axie Studio",
        "price_monthly": 0.0,
        "price_yearly": 0.0,
        "remove_branding": False,
        "custom_branding": False,
        "white_label": False,
        "conversations_limit": 1000,
        "analytics_advanced": False,
        "priority_support": False,
        "api_access": True,
        "stripe_product_id": "prod_Spru2NddCYhUxd"
    },
    {
        "name": "Premium",
        "tier": SubscriptionTier.PREMIUM,
        "description": "🚀 Remove 'Powered by Axie Studio' branding",
        "price_monthly": 49.0,
        "price_yearly": 490.0,  # 2 months free
        "remove_branding": True,
        "custom_branding": True,
        "white_label": False,
        "conversations_limit": 10000,
        "analytics_advanced": True,
        "priority_support": True,
        "api_access": True,
        "stripe_product_id": "prod_SpruWu0jXkSvVm"
    },
    {
        "name": "Enterprise",
        "tier": SubscriptionTier.ENTERPRISE,
        "description": "Complete white-label solution with unlimited usage",
        "price_monthly": 199.0,
        "price_yearly": 1990.0,  # 2 months free
        "remove_branding": True,
        "custom_branding": True,
        "white_label": True,
        "conversations_limit": -1,  # Unlimited
        "analytics_advanced": True,
        "priority_support": True,
        "api_access": True,
        "stripe_product_id": "prod_Sprvt6O6yYHL3E"
    }
]
