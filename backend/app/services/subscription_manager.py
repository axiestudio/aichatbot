from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import json
import stripe
import os
import logging

from ..models.subscription import Subscription, SubscriptionPlan, SubscriptionTier, SubscriptionStatus, DEFAULT_PLANS
from ..core.database import get_db
from .email_service import email_service

logger = logging.getLogger(__name__)

# Configure Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_...")

class SubscriptionManager:
    def __init__(self):
        self.stripe_enabled = bool(os.getenv("STRIPE_SECRET_KEY"))
    
    async def get_subscription(self, tenant_id: str, db: Session) -> Optional[Subscription]:
        """Get subscription for a tenant"""
        return db.query(Subscription).filter(Subscription.tenant_id == tenant_id).first()
    
    async def create_subscription(self, tenant_id: str, tier: str = SubscriptionTier.FREE, db: Session = None) -> Subscription:
        """Create a new subscription for a tenant"""
        
        # Get plan details
        plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.tier == tier).first()
        if not plan:
            # Create default free plan if not exists
            plan = await self.create_default_plans(db)
            plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.tier == SubscriptionTier.FREE).first()
        
        # Create subscription
        subscription = Subscription(
            tenant_id=tenant_id,
            tier=tier,
            status=SubscriptionStatus.ACTIVE,
            remove_branding=plan.remove_branding,
            custom_branding_enabled=plan.custom_branding,
            white_label_enabled=plan.white_label,
            monthly_conversations_limit=plan.conversations_limit,
            price_per_month=plan.price_monthly
        )
        
        # Add 14-day trial for premium tiers
        if tier != SubscriptionTier.FREE:
            subscription.trial_ends_at = datetime.utcnow() + timedelta(days=14)
            subscription.status = SubscriptionStatus.TRIALING
        
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
        
        return subscription
    
    async def upgrade_subscription(self, tenant_id: str, new_tier: str, db: Session) -> Dict[str, Any]:
        """Upgrade a subscription to a new tier"""
        
        subscription = await self.get_subscription(tenant_id, db)
        if not subscription:
            subscription = await self.create_subscription(tenant_id, SubscriptionTier.FREE, db)
        
        plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.tier == new_tier).first()
        if not plan:
            raise ValueError(f"Plan not found for tier: {new_tier}")
        
        # Update subscription
        old_tier = subscription.tier
        subscription.tier = new_tier
        subscription.remove_branding = plan.remove_branding
        subscription.custom_branding_enabled = plan.custom_branding
        subscription.white_label_enabled = plan.white_label
        subscription.monthly_conversations_limit = plan.conversations_limit
        subscription.price_per_month = plan.price_monthly
        subscription.updated_at = datetime.utcnow()
        
        # Start trial for premium upgrades
        if new_tier != SubscriptionTier.FREE and old_tier == SubscriptionTier.FREE:
            subscription.trial_ends_at = datetime.utcnow() + timedelta(days=14)
            subscription.status = SubscriptionStatus.TRIALING
        
        db.commit()
        db.refresh(subscription)

        # Send email notification for upgrade
        try:
            plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.tier == new_tier).first()
            if plan and new_tier != SubscriptionTier.FREE:
                # Send upgrade confirmation email
                user_email = f"{tenant_id}@axiestudio.se"  # Replace with actual user email lookup
                email_service.send_payment_confirmation(
                    to_email=user_email,
                    user_name=tenant_id,
                    plan_name=plan.name,
                    amount=plan.price_monthly
                )
        except Exception as e:
            logger.error(f"Failed to send upgrade confirmation email: {e}")

        return {
            "success": True,
            "message": f"Subscription upgraded from {old_tier} to {new_tier}",
            "subscription": subscription,
            "trial_days": subscription.days_until_trial_end if subscription.is_trial_active else 0
        }
    
    async def check_branding_permissions(self, tenant_id: str, db: Session) -> Dict[str, bool]:
        """Check what branding permissions a tenant has"""
        
        subscription = await self.get_subscription(tenant_id, db)
        if not subscription:
            # Create free subscription if none exists
            subscription = await self.create_subscription(tenant_id, SubscriptionTier.FREE, db)
        
        return {
            "can_remove_branding": subscription.can_remove_branding or subscription.is_trial_active,
            "can_custom_brand": subscription.custom_branding_enabled or subscription.is_trial_active,
            "can_white_label": subscription.white_label_enabled or subscription.is_trial_active,
            "is_trial": subscription.is_trial_active,
            "trial_days_left": subscription.days_until_trial_end,
            "tier": subscription.tier,
            "usage_percentage": subscription.usage_percentage,
            "usage_exceeded": subscription.is_usage_exceeded
        }
    
    async def track_conversation_usage(self, tenant_id: str, db: Session) -> bool:
        """Track a conversation and check if limit is exceeded"""
        
        subscription = await self.get_subscription(tenant_id, db)
        if not subscription:
            subscription = await self.create_subscription(tenant_id, SubscriptionTier.FREE, db)
        
        # Increment usage
        subscription.monthly_conversations_used += 1
        db.commit()
        
        # Check if limit exceeded (unlimited = -1)
        if subscription.monthly_conversations_limit == -1:
            return True  # Unlimited
        
        return subscription.monthly_conversations_used <= subscription.monthly_conversations_limit
    
    async def reset_monthly_usage(self, tenant_id: str, db: Session):
        """Reset monthly usage (called by cron job)"""
        
        subscription = await self.get_subscription(tenant_id, db)
        if subscription:
            subscription.monthly_conversations_used = 0
            subscription.current_period_start = datetime.utcnow()
            subscription.current_period_end = datetime.utcnow() + timedelta(days=30)
            db.commit()
    
    async def create_stripe_checkout_session(self, tenant_id: str, tier: str, billing_cycle: str = "monthly", db: Session = None) -> Dict[str, Any]:
        """Create Stripe checkout session for subscription upgrade"""

        if not self.stripe_enabled:
            return {"error": "Stripe not configured"}

        try:
            # Get plan
            plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.tier == tier).first()
            if not plan:
                return {"error": "Plan not found"}
            
            # Get price ID
            price_id = plan.stripe_price_id_monthly if billing_cycle == "monthly" else plan.stripe_price_id_yearly
            if not price_id:
                return {"error": "Stripe price not configured"}
            
            # Create checkout session
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/admin/billing/success?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/admin/billing/cancel",
                client_reference_id=tenant_id,
                metadata={
                    'tenant_id': tenant_id,
                    'tier': tier,
                    'billing_cycle': billing_cycle
                }
            )
            
            return {
                "checkout_url": session.url,
                "session_id": session.id
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def handle_stripe_webhook(self, event: Dict[str, Any], db: Session) -> bool:
        """Handle Stripe webhook events"""
        
        try:
            if event['type'] == 'checkout.session.completed':
                session = event['data']['object']
                tenant_id = session['client_reference_id']
                tier = session['metadata']['tier']
                
                # Upgrade subscription
                await self.upgrade_subscription(tenant_id, tier, db)
                
                # Update Stripe IDs
                subscription = await self.get_subscription(tenant_id, db)
                subscription.stripe_customer_id = session['customer']
                subscription.stripe_subscription_id = session['subscription']
                subscription.status = SubscriptionStatus.ACTIVE
                db.commit()
                
                return True
                
            elif event['type'] == 'invoice.payment_failed':
                # Handle failed payment
                subscription_id = event['data']['object']['subscription']
                subscription = db.query(Subscription).filter(
                    Subscription.stripe_subscription_id == subscription_id
                ).first()
                
                if subscription:
                    subscription.status = SubscriptionStatus.PAST_DUE
                    db.commit()
                
                return True
                
        except Exception as e:
            print(f"Stripe webhook error: {e}")
            return False
        
        return True
    
    async def create_default_plans(self, db: Session) -> List[SubscriptionPlan]:
        """Create default subscription plans"""
        
        plans = []
        for plan_data in DEFAULT_PLANS:
            existing = db.query(SubscriptionPlan).filter(
                SubscriptionPlan.tier == plan_data["tier"]
            ).first()
            
            if not existing:
                plan = SubscriptionPlan(**plan_data)
                db.add(plan)
                plans.append(plan)
        
        db.commit()
        return plans
    
    async def get_all_plans(self, db: Session) -> List[SubscriptionPlan]:
        """Get all available subscription plans"""
        return db.query(SubscriptionPlan).filter(SubscriptionPlan.active == True).all()

# Global subscription manager instance
subscription_manager = SubscriptionManager()
