"""
Super Admin Billing & Subscription Management API - Enterprise SaaS
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import uuid

from ...core.database import get_db
from ...core.auth import get_current_super_admin
from ...models.database import SuperAdmin, ChatInstance

router = APIRouter(prefix="/billing", tags=["super-admin-billing"])


class PlanLimits(BaseModel):
    monthly_messages: int
    api_configurations: int
    custom_domain: bool
    priority_support: bool
    analytics_retention_days: int
    white_label: bool


class SubscriptionPlan(BaseModel):
    id: str
    name: str
    price_monthly: float
    price_yearly: float
    limits: PlanLimits
    features: List[str]
    is_popular: bool = False


class BillingInfo(BaseModel):
    instance_id: str
    plan_type: str
    billing_email: str
    next_billing_date: Optional[str]
    amount_due: float
    payment_status: str
    usage_this_month: Dict[str, Any]


class UsageAlert(BaseModel):
    instance_id: str
    instance_name: str
    alert_type: str  # "approaching_limit", "over_limit", "payment_failed"
    message: str
    severity: str  # "low", "medium", "high", "critical"
    created_at: str


class RevenueReport(BaseModel):
    period: str
    total_revenue: float
    new_revenue: float
    churned_revenue: float
    net_revenue: float
    customer_count: int
    average_revenue_per_user: float
    churn_rate: float


# Predefined subscription plans
SUBSCRIPTION_PLANS = [
    SubscriptionPlan(
        id="free",
        name="Free",
        price_monthly=0,
        price_yearly=0,
        limits=PlanLimits(
            monthly_messages=1000,
            api_configurations=1,
            custom_domain=False,
            priority_support=False,
            analytics_retention_days=7,
            white_label=False
        ),
        features=[
            "1,000 messages/month",
            "1 AI provider",
            "Basic analytics",
            "Community support"
        ]
    ),
    SubscriptionPlan(
        id="pro",
        name="Professional",
        price_monthly=29,
        price_yearly=290,
        limits=PlanLimits(
            monthly_messages=10000,
            api_configurations=5,
            custom_domain=True,
            priority_support=True,
            analytics_retention_days=30,
            white_label=False
        ),
        features=[
            "10,000 messages/month",
            "5 AI providers",
            "Advanced analytics",
            "Custom domain",
            "Priority support",
            "API access"
        ],
        is_popular=True
    ),
    SubscriptionPlan(
        id="enterprise",
        name="Enterprise",
        price_monthly=99,
        price_yearly=990,
        limits=PlanLimits(
            monthly_messages=100000,
            api_configurations=999,
            custom_domain=True,
            priority_support=True,
            analytics_retention_days=365,
            white_label=True
        ),
        features=[
            "100,000 messages/month",
            "Unlimited AI providers",
            "Full analytics suite",
            "Custom domain",
            "White-label solution",
            "Dedicated support",
            "SLA guarantee",
            "Custom integrations"
        ]
    )
]


@router.get("/plans", response_model=List[SubscriptionPlan])
async def get_subscription_plans(
    current_super_admin: SuperAdmin = Depends(get_current_super_admin)
):
    """Get all available subscription plans"""
    return SUBSCRIPTION_PLANS


@router.get("/overview")
async def get_billing_overview(
    db: Session = Depends(get_db),
    current_super_admin: SuperAdmin = Depends(get_current_super_admin)
):
    """Get comprehensive billing overview"""
    
    if not current_super_admin.can_manage_billing:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: cannot manage billing"
        )
    
    # Calculate revenue metrics
    plan_counts = db.query(ChatInstance.plan_type, db.func.count(ChatInstance.id)).group_by(ChatInstance.plan_type).all()
    
    total_revenue = 0
    revenue_by_plan = {}
    
    for plan, count in plan_counts:
        plan_obj = next((p for p in SUBSCRIPTION_PLANS if p.id == plan), None)
        if plan_obj:
            monthly_revenue = count * plan_obj.price_monthly
            revenue_by_plan[plan] = {
                "count": count,
                "monthly_revenue": monthly_revenue,
                "yearly_potential": count * plan_obj.price_yearly
            }
            total_revenue += monthly_revenue
    
    # Get instances approaching limits
    approaching_limit = []
    for instance in db.query(ChatInstance).filter(ChatInstance.is_active == True).all():
        usage_percentage = (instance.current_monthly_messages / max(instance.max_monthly_messages, 1)) * 100
        if usage_percentage > 80:
            approaching_limit.append({
                "instance_id": instance.id,
                "name": instance.name,
                "usage_percentage": usage_percentage,
                "plan_type": instance.plan_type
            })
    
    return {
        "total_monthly_revenue": total_revenue,
        "total_yearly_potential": sum(data["yearly_potential"] for data in revenue_by_plan.values()),
        "revenue_by_plan": revenue_by_plan,
        "total_customers": sum(data["count"] for data in revenue_by_plan.values()),
        "approaching_limit": approaching_limit,
        "churn_risk": len([i for i in approaching_limit if i["usage_percentage"] > 95])
    }


@router.get("/instances", response_model=List[BillingInfo])
async def get_billing_info_all_instances(
    db: Session = Depends(get_db),
    current_super_admin: SuperAdmin = Depends(get_current_super_admin)
):
    """Get billing information for all instances"""
    
    if not current_super_admin.can_manage_billing:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: cannot manage billing"
        )
    
    instances = db.query(ChatInstance).all()
    billing_info = []
    
    for instance in instances:
        plan_obj = next((p for p in SUBSCRIPTION_PLANS if p.id == instance.plan_type), None)
        amount_due = plan_obj.price_monthly if plan_obj else 0
        
        # Calculate next billing date (simplified)
        next_billing = datetime.utcnow() + timedelta(days=30)
        
        billing_info.append(BillingInfo(
            instance_id=instance.id,
            plan_type=instance.plan_type,
            billing_email=instance.billing_email or instance.owner_email,
            next_billing_date=next_billing.isoformat(),
            amount_due=amount_due,
            payment_status="active" if instance.is_active else "suspended",
            usage_this_month={
                "messages": instance.current_monthly_messages,
                "limit": instance.max_monthly_messages,
                "percentage": (instance.current_monthly_messages / max(instance.max_monthly_messages, 1)) * 100
            }
        ))
    
    return billing_info


@router.post("/instances/{instance_id}/change-plan")
async def change_instance_plan(
    instance_id: str,
    new_plan: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_super_admin: SuperAdmin = Depends(get_current_super_admin)
):
    """Change subscription plan for an instance"""
    
    if not current_super_admin.can_manage_billing:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: cannot manage billing"
        )
    
    instance = db.query(ChatInstance).filter(ChatInstance.id == instance_id).first()
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    
    # Validate new plan
    plan_obj = next((p for p in SUBSCRIPTION_PLANS if p.id == new_plan), None)
    if not plan_obj:
        raise HTTPException(status_code=400, detail="Invalid plan")
    
    old_plan = instance.plan_type
    
    # Update instance
    instance.plan_type = new_plan
    instance.max_monthly_messages = plan_obj.limits.monthly_messages
    db.commit()
    
    # Send notification email
    background_tasks.add_task(
        send_plan_change_notification,
        instance.owner_email,
        instance.name,
        old_plan,
        new_plan
    )
    
    return {
        "message": "Plan changed successfully",
        "old_plan": old_plan,
        "new_plan": new_plan,
        "new_limits": plan_obj.limits.dict()
    }


@router.get("/alerts", response_model=List[UsageAlert])
async def get_usage_alerts(
    severity: Optional[str] = None,
    db: Session = Depends(get_db),
    current_super_admin: SuperAdmin = Depends(get_current_super_admin)
):
    """Get usage alerts and notifications"""
    
    if not current_super_admin.can_view_all_analytics:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: cannot view alerts"
        )
    
    alerts = []
    
    # Check for instances approaching limits
    for instance in db.query(ChatInstance).filter(ChatInstance.is_active == True).all():
        usage_percentage = (instance.current_monthly_messages / max(instance.max_monthly_messages, 1)) * 100
        
        if usage_percentage > 95:
            alerts.append(UsageAlert(
                instance_id=instance.id,
                instance_name=instance.name,
                alert_type="over_limit",
                message=f"Instance '{instance.name}' has exceeded 95% of message limit",
                severity="critical",
                created_at=datetime.utcnow().isoformat()
            ))
        elif usage_percentage > 80:
            alerts.append(UsageAlert(
                instance_id=instance.id,
                instance_name=instance.name,
                alert_type="approaching_limit",
                message=f"Instance '{instance.name}' is approaching message limit ({usage_percentage:.1f}%)",
                severity="medium",
                created_at=datetime.utcnow().isoformat()
            ))
    
    # Filter by severity if specified
    if severity:
        alerts = [alert for alert in alerts if alert.severity == severity]
    
    return alerts


@router.post("/reports/revenue")
async def generate_revenue_report(
    start_date: str,
    end_date: str,
    db: Session = Depends(get_db),
    current_super_admin: SuperAdmin = Depends(get_current_super_admin)
):
    """Generate detailed revenue report"""
    
    if not current_super_admin.can_manage_billing:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: cannot generate reports"
        )
    
    # Parse dates
    try:
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")
    
    # Calculate metrics for the period
    instances_in_period = db.query(ChatInstance).filter(
        ChatInstance.created_at.between(start, end)
    ).all()
    
    total_revenue = 0
    customer_count = len(instances_in_period)
    
    for instance in instances_in_period:
        plan_obj = next((p for p in SUBSCRIPTION_PLANS if p.id == instance.plan_type), None)
        if plan_obj:
            total_revenue += plan_obj.price_monthly
    
    average_revenue_per_user = total_revenue / max(customer_count, 1)
    
    return RevenueReport(
        period=f"{start_date} to {end_date}",
        total_revenue=total_revenue,
        new_revenue=total_revenue,  # Simplified
        churned_revenue=0,  # Would need churn tracking
        net_revenue=total_revenue,
        customer_count=customer_count,
        average_revenue_per_user=average_revenue_per_user,
        churn_rate=0  # Would need churn tracking
    )


def send_plan_change_notification(email: str, instance_name: str, old_plan: str, new_plan: str):
    """Send plan change notification email"""
    # TODO: Implement email sending
    print(f"Plan changed for {instance_name}: {old_plan} -> {new_plan}")
    print(f"Notification sent to: {email}")
