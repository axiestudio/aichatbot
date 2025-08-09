"""
Subscription API - Premium branding and billing management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import stripe
import os

from ....core.database import get_db
from ....services.subscription_manager import subscription_manager
from ....services.tenant_manager import tenant_manager
from ....models.subscription import SubscriptionTier, SubscriptionStatus

router = APIRouter(prefix="/subscription", tags=["subscription"])

@router.get("/{tenant_id}/status")
async def get_subscription_status(
    tenant_id: str,
    db: Session = Depends(get_db)
):
    """Get current subscription status and branding permissions"""
    
    try:
        # Validate tenant
        tenant_info = await tenant_manager.get_tenant_by_id(tenant_id)
        if not tenant_info:
            raise HTTPException(status_code=404, detail="Tenant not found")
        
        # Get subscription
        subscription = await subscription_manager.get_subscription(tenant_id, db)
        if not subscription:
            subscription = await subscription_manager.create_subscription(tenant_id, SubscriptionTier.FREE, db)
        
        # Get branding permissions
        permissions = await subscription_manager.check_branding_permissions(tenant_id, db)
        
        return {
            "subscription": {
                "id": subscription.id,
                "tenantId": subscription.tenant_id,
                "tier": subscription.tier,
                "status": subscription.status,
                "pricePerMonth": subscription.price_per_month,
                "createdAt": subscription.created_at.isoformat(),
                "currentPeriodStart": subscription.current_period_start.isoformat(),
                "currentPeriodEnd": subscription.current_period_end.isoformat(),
                "trialEndsAt": subscription.trial_ends_at.isoformat() if subscription.trial_ends_at else None
            },
            "permissions": permissions,
            "usage": {
                "conversationsUsed": subscription.monthly_conversations_used,
                "conversationsLimit": subscription.monthly_conversations_limit,
                "usagePercentage": subscription.usage_percentage,
                "unlimited": subscription.monthly_conversations_limit == -1
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get subscription status: {str(e)}")

@router.get("/plans")
async def get_subscription_plans(db: Session = Depends(get_db)):
    """Get all available subscription plans"""
    
    try:
        plans = await subscription_manager.get_all_plans(db)
        
        return {
            "plans": [
                {
                    "id": plan.id,
                    "name": plan.name,
                    "tier": plan.tier,
                    "description": plan.description,
                    "priceMonthly": plan.price_monthly,
                    "priceYearly": plan.price_yearly,
                    "features": {
                        "removeBranding": plan.remove_branding,
                        "customBranding": plan.custom_branding,
                        "whiteLabel": plan.white_label,
                        "conversationsLimit": plan.conversations_limit,
                        "advancedAnalytics": plan.analytics_advanced,
                        "prioritySupport": plan.priority_support,
                        "apiAccess": plan.api_access
                    },
                    "popular": plan.tier == SubscriptionTier.PREMIUM
                }
                for plan in plans
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get plans: {str(e)}")

@router.post("/{tenant_id}/upgrade")
async def upgrade_subscription(
    tenant_id: str,
    upgrade_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Upgrade subscription to a new tier"""
    
    try:
        # Validate tenant
        tenant_info = await tenant_manager.get_tenant_by_id(tenant_id)
        if not tenant_info:
            raise HTTPException(status_code=404, detail="Tenant not found")
        
        new_tier = upgrade_data.get("tier")
        if not new_tier or new_tier not in [SubscriptionTier.FREE, SubscriptionTier.PREMIUM, SubscriptionTier.ENTERPRISE]:
            raise HTTPException(status_code=400, detail="Invalid tier")
        
        # Upgrade subscription
        result = await subscription_manager.upgrade_subscription(tenant_id, new_tier, db)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upgrade subscription: {str(e)}")

@router.post("/{tenant_id}/checkout")
async def create_checkout_session(
    tenant_id: str,
    checkout_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Create Stripe checkout session for subscription upgrade"""
    
    try:
        # Validate tenant
        tenant_info = await tenant_manager.get_tenant_by_id(tenant_id)
        if not tenant_info:
            raise HTTPException(status_code=404, detail="Tenant not found")
        
        tier = checkout_data.get("tier")
        billing_cycle = checkout_data.get("billingCycle", "monthly")
        
        if not tier or tier not in [SubscriptionTier.PREMIUM, SubscriptionTier.ENTERPRISE]:
            raise HTTPException(status_code=400, detail="Invalid tier for checkout")
        
        # Create Stripe checkout session
        result = await subscription_manager.create_stripe_checkout_session(tenant_id, tier, billing_cycle)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create checkout session: {str(e)}")

@router.post("/webhook/stripe")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle Stripe webhook events"""
    
    try:
        payload = await request.body()
        sig_header = request.headers.get('stripe-signature')
        endpoint_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
        
        if not endpoint_secret:
            raise HTTPException(status_code=400, detail="Webhook secret not configured")
        
        # Verify webhook signature
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid payload")
        except stripe.error.SignatureVerificationError:
            raise HTTPException(status_code=400, detail="Invalid signature")
        
        # Handle the event
        success = await subscription_manager.handle_stripe_webhook(event, db)
        
        if success:
            return {"status": "success"}
        else:
            raise HTTPException(status_code=400, detail="Failed to process webhook")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Webhook error: {str(e)}")

@router.get("/{tenant_id}/billing-portal")
async def create_billing_portal_session(
    tenant_id: str,
    db: Session = Depends(get_db)
):
    """Create Stripe billing portal session for subscription management"""
    
    try:
        # Validate tenant
        tenant_info = await tenant_manager.get_tenant_by_id(tenant_id)
        if not tenant_info:
            raise HTTPException(status_code=404, detail="Tenant not found")
        
        # Get subscription
        subscription = await subscription_manager.get_subscription(tenant_id, db)
        if not subscription or not subscription.stripe_customer_id:
            raise HTTPException(status_code=400, detail="No active subscription found")
        
        # Create billing portal session
        session = stripe.billing_portal.Session.create(
            customer=subscription.stripe_customer_id,
            return_url=f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/admin/billing"
        )
        
        return {"url": session.url}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create billing portal: {str(e)}")

@router.post("/{tenant_id}/cancel")
async def cancel_subscription(
    tenant_id: str,
    db: Session = Depends(get_db)
):
    """Cancel subscription (downgrade to free tier)"""
    
    try:
        # Validate tenant
        tenant_info = await tenant_manager.get_tenant_by_id(tenant_id)
        if not tenant_info:
            raise HTTPException(status_code=404, detail="Tenant not found")
        
        # Get subscription
        subscription = await subscription_manager.get_subscription(tenant_id, db)
        if not subscription:
            raise HTTPException(status_code=400, detail="No subscription found")
        
        # Cancel Stripe subscription if exists
        if subscription.stripe_subscription_id:
            stripe.Subscription.delete(subscription.stripe_subscription_id)
        
        # Downgrade to free tier
        result = await subscription_manager.upgrade_subscription(tenant_id, SubscriptionTier.FREE, db)
        
        return {
            "success": True,
            "message": "Subscription canceled successfully",
            "subscription": result["subscription"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cancel subscription: {str(e)}")

@router.get("/{tenant_id}/trial/start")
async def start_trial(
    tenant_id: str,
    trial_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Start a premium trial"""
    
    try:
        # Validate tenant
        tenant_info = await tenant_manager.get_tenant_by_id(tenant_id)
        if not tenant_info:
            raise HTTPException(status_code=404, detail="Tenant not found")
        
        tier = trial_data.get("tier", SubscriptionTier.PREMIUM)
        
        # Upgrade to trial
        result = await subscription_manager.upgrade_subscription(tenant_id, tier, db)
        
        return {
            "success": True,
            "message": f"14-day {tier} trial started",
            "trialDaysLeft": result["trial_days"],
            "subscription": result["subscription"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start trial: {str(e)}")
