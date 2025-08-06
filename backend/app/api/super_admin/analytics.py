"""
Super Admin Global Analytics API - Enterprise Grade Monitoring
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json

from ...core.database import get_db
from ...core.auth import get_current_super_admin
from ...models.database import SuperAdmin, ChatInstance, InstanceAdmin, ApiConfiguration
from ...services.super_admin_monitoring import monitoring_service

router = APIRouter(prefix="/analytics", tags=["super-admin-analytics"])


class GlobalMetrics(BaseModel):
    total_instances: int
    active_instances: int
    total_admins: int
    total_monthly_messages: int
    total_api_configurations: int
    revenue_metrics: Dict[str, Any]
    growth_metrics: Dict[str, Any]


class InstancePerformance(BaseModel):
    instance_id: str
    instance_name: str
    subdomain: str
    plan_type: str
    monthly_messages: int
    message_limit: int
    usage_percentage: float
    last_activity: Optional[str]
    admin_count: int
    status: str


class RevenueAnalytics(BaseModel):
    total_revenue: float
    monthly_recurring_revenue: float
    revenue_by_plan: Dict[str, float]
    churn_rate: float
    growth_rate: float
    lifetime_value: float


class UsageAnalytics(BaseModel):
    total_messages_today: int
    total_messages_week: int
    total_messages_month: int
    average_messages_per_instance: float
    peak_usage_hours: List[Dict[str, Any]]
    top_performing_instances: List[InstancePerformance]


class SystemHealth(BaseModel):
    overall_status: str
    database_status: str
    api_response_time: float
    error_rate: float
    uptime_percentage: float
    active_connections: int
    memory_usage: float
    cpu_usage: float


@router.get("/global-metrics", response_model=GlobalMetrics)
async def get_global_metrics(
    db: Session = Depends(get_db),
    current_super_admin: SuperAdmin = Depends(get_current_super_admin)
):
    """Get comprehensive global platform metrics"""
    
    if not current_super_admin.can_view_all_analytics:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: cannot view analytics"
        )
    
    # Basic counts
    total_instances = db.query(ChatInstance).count()
    active_instances = db.query(ChatInstance).filter(ChatInstance.is_active == True).count()
    total_admins = db.query(InstanceAdmin).count()
    
    # Message metrics
    total_monthly_messages = db.query(func.sum(ChatInstance.current_monthly_messages)).scalar() or 0
    total_api_configs = db.query(ApiConfiguration).count()
    
    # Revenue metrics (simplified)
    plan_counts = db.query(ChatInstance.plan_type, func.count(ChatInstance.id)).group_by(ChatInstance.plan_type).all()
    revenue_metrics = calculate_revenue_metrics(plan_counts)
    
    # Growth metrics
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    new_instances_30d = db.query(ChatInstance).filter(ChatInstance.created_at >= thirty_days_ago).count()
    growth_metrics = {
        "new_instances_30d": new_instances_30d,
        "growth_rate": (new_instances_30d / max(total_instances - new_instances_30d, 1)) * 100
    }
    
    return GlobalMetrics(
        total_instances=total_instances,
        active_instances=active_instances,
        total_admins=total_admins,
        total_monthly_messages=total_monthly_messages,
        total_api_configurations=total_api_configs,
        revenue_metrics=revenue_metrics,
        growth_metrics=growth_metrics
    )


@router.get("/revenue", response_model=RevenueAnalytics)
async def get_revenue_analytics(
    db: Session = Depends(get_db),
    current_super_admin: SuperAdmin = Depends(get_current_super_admin)
):
    """Get detailed revenue analytics"""
    
    if not current_super_admin.can_manage_billing:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: cannot view billing analytics"
        )
    
    # Plan pricing (in a real app, this would come from a pricing table)
    plan_pricing = {"free": 0, "pro": 29, "enterprise": 99}
    
    # Calculate revenue by plan
    plan_counts = db.query(ChatInstance.plan_type, func.count(ChatInstance.id)).group_by(ChatInstance.plan_type).all()
    revenue_by_plan = {plan: count * plan_pricing.get(plan, 0) for plan, count in plan_counts}
    
    total_revenue = sum(revenue_by_plan.values())
    monthly_recurring_revenue = total_revenue  # Simplified
    
    # Calculate churn rate (simplified)
    total_instances = db.query(ChatInstance).count()
    inactive_instances = db.query(ChatInstance).filter(ChatInstance.is_active == False).count()
    churn_rate = (inactive_instances / max(total_instances, 1)) * 100
    
    # Growth rate
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    new_instances = db.query(ChatInstance).filter(ChatInstance.created_at >= thirty_days_ago).count()
    growth_rate = (new_instances / max(total_instances - new_instances, 1)) * 100
    
    # Lifetime value (simplified)
    lifetime_value = total_revenue / max(total_instances, 1)
    
    return RevenueAnalytics(
        total_revenue=total_revenue,
        monthly_recurring_revenue=monthly_recurring_revenue,
        revenue_by_plan=revenue_by_plan,
        churn_rate=churn_rate,
        growth_rate=growth_rate,
        lifetime_value=lifetime_value
    )


@router.get("/usage", response_model=UsageAnalytics)
async def get_usage_analytics(
    db: Session = Depends(get_db),
    current_super_admin: SuperAdmin = Depends(get_current_super_admin)
):
    """Get detailed usage analytics"""
    
    if not current_super_admin.can_view_all_analytics:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: cannot view analytics"
        )
    
    # Calculate usage metrics (simplified - in real app would use message logs)
    total_messages_month = db.query(func.sum(ChatInstance.current_monthly_messages)).scalar() or 0
    total_instances = db.query(ChatInstance).count()
    average_messages = total_messages_month / max(total_instances, 1)
    
    # Get top performing instances
    top_instances = db.query(ChatInstance).order_by(ChatInstance.current_monthly_messages.desc()).limit(10).all()
    
    top_performing_instances = []
    for instance in top_instances:
        admin_count = db.query(InstanceAdmin).filter(InstanceAdmin.instance_id == instance.id).count()
        usage_percentage = (instance.current_monthly_messages / max(instance.max_monthly_messages, 1)) * 100
        
        top_performing_instances.append(InstancePerformance(
            instance_id=instance.id,
            instance_name=instance.name,
            subdomain=instance.subdomain,
            plan_type=instance.plan_type,
            monthly_messages=instance.current_monthly_messages,
            message_limit=instance.max_monthly_messages,
            usage_percentage=min(usage_percentage, 100),
            last_activity=instance.updated_at.isoformat(),
            admin_count=admin_count,
            status="active" if instance.is_active else "inactive"
        ))
    
    return UsageAnalytics(
        total_messages_today=0,  # Would need message logs
        total_messages_week=0,   # Would need message logs
        total_messages_month=total_messages_month,
        average_messages_per_instance=average_messages,
        peak_usage_hours=[],     # Would need detailed logs
        top_performing_instances=top_performing_instances
    )


@router.get("/system-health", response_model=SystemHealth)
async def get_system_health(
    db: Session = Depends(get_db),
    current_super_admin: SuperAdmin = Depends(get_current_super_admin)
):
    """Get comprehensive system health metrics"""

    if not current_super_admin.can_view_all_analytics:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: cannot view system health"
        )

    # Get real-time platform health
    platform_health = await monitoring_service.get_platform_health()

    # Extract system health data
    system_data = platform_health.get("components", {}).get("system", {})
    db_data = platform_health.get("components", {}).get("database", {})

    return SystemHealth(
        overall_status=platform_health.get("overall_status", "unknown"),
        database_status=db_data.get("status", "unknown"),
        api_response_time=db_data.get("response_time_ms", 0),
        error_rate=0.1,  # Would come from error tracking
        uptime_percentage=99.9,  # Would come from monitoring system
        active_connections=db_data.get("table_counts", {}).get("instances", 0),
        memory_usage=system_data.get("memory_percent", 0),
        cpu_usage=system_data.get("cpu_percent", 0)
    )


@router.get("/platform-health")
async def get_platform_health(
    current_super_admin: SuperAdmin = Depends(get_current_super_admin)
):
    """Get comprehensive platform health with detailed monitoring"""

    if not current_super_admin.can_view_all_analytics:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: cannot view platform health"
        )

    return await monitoring_service.get_platform_health()


@router.get("/instances/{instance_id}/analytics")
async def get_instance_analytics(
    instance_id: str,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_super_admin: SuperAdmin = Depends(get_current_super_admin)
):
    """Get detailed analytics for specific instance"""
    
    if not current_super_admin.can_view_all_analytics:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: cannot view analytics"
        )
    
    instance = db.query(ChatInstance).filter(ChatInstance.id == instance_id).first()
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    
    # Get instance admins
    admins = db.query(InstanceAdmin).filter(InstanceAdmin.instance_id == instance_id).all()
    
    # Get API configurations
    api_configs = db.query(ApiConfiguration).filter(ApiConfiguration.instance_id == instance_id).all()
    
    return {
        "instance": InstanceResponse.from_orm(instance),
        "admins": [{"id": admin.id, "email": admin.email, "name": admin.name, "role": admin.role} for admin in admins],
        "api_configurations": [{"id": config.id, "name": config.name, "provider": config.provider} for config in api_configs],
        "usage_metrics": {
            "current_monthly_messages": instance.current_monthly_messages,
            "message_limit": instance.max_monthly_messages,
            "usage_percentage": (instance.current_monthly_messages / max(instance.max_monthly_messages, 1)) * 100
        }
    }


def calculate_revenue_metrics(plan_counts: List[tuple]) -> Dict[str, Any]:
    """Calculate revenue metrics from plan counts"""
    plan_pricing = {"free": 0, "pro": 29, "enterprise": 99}
    
    total_revenue = 0
    revenue_by_plan = {}
    
    for plan, count in plan_counts:
        revenue = count * plan_pricing.get(plan, 0)
        revenue_by_plan[plan] = revenue
        total_revenue += revenue
    
    return {
        "total_revenue": total_revenue,
        "revenue_by_plan": revenue_by_plan,
        "average_revenue_per_user": total_revenue / max(sum(count for _, count in plan_counts), 1)
    }
