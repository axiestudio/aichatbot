"""
Advanced Analytics API Endpoints
AI-powered analytics and insights endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from ....services.advanced_analytics_service import advanced_analytics_service
from ....services.ai_autoscaling_service import ai_autoscaling_service
from ....services.security_intelligence_service import security_intelligence_service
from ....core.dependencies import get_current_admin_user

router = APIRouter(prefix="/analytics", tags=["advanced_analytics"])


@router.get("/dashboard")
async def get_analytics_dashboard(
    instance_id: Optional[str] = Query(None, description="Instance ID for filtering"),
    current_user = Depends(get_current_admin_user)
):
    """Get comprehensive analytics dashboard data"""
    try:
        dashboard_data = await advanced_analytics_service.get_real_time_dashboard(instance_id)
        return dashboard_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard data: {str(e)}")


@router.get("/insights")
async def get_ai_insights(
    instance_id: Optional[str] = Query(None, description="Instance ID for filtering"),
    limit: int = Query(10, description="Maximum number of insights to return"),
    current_user = Depends(get_current_admin_user)
):
    """Get AI-generated insights"""
    try:
        insights = await advanced_analytics_service._get_ai_insights(instance_id)
        return {"insights": insights[:limit]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get insights: {str(e)}")


@router.get("/predictions")
async def get_predictions(
    instance_id: Optional[str] = Query(None, description="Instance ID for filtering"),
    prediction_type: Optional[str] = Query(None, description="Type of prediction (traffic, performance, capacity)"),
    current_user = Depends(get_current_admin_user)
):
    """Get predictive analytics"""
    try:
        predictions = await advanced_analytics_service._get_predictions(instance_id)
        
        if prediction_type and prediction_type in predictions:
            return {prediction_type: predictions[prediction_type]}
        
        return predictions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get predictions: {str(e)}")


@router.get("/health-score")
async def get_health_score(
    instance_id: Optional[str] = Query(None, description="Instance ID for filtering"),
    current_user = Depends(get_current_admin_user)
):
    """Get overall system health score"""
    try:
        health_score = await advanced_analytics_service._calculate_health_score(instance_id)
        return {
            "health_score": health_score,
            "timestamp": datetime.utcnow().isoformat(),
            "instance_id": instance_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get health score: {str(e)}")


@router.get("/user-analytics")
async def get_user_analytics(
    instance_id: Optional[str] = Query(None, description="Instance ID for filtering"),
    timeframe: str = Query("24h", description="Timeframe for analytics (1h, 24h, 7d, 30d)"),
    current_user = Depends(get_current_admin_user)
):
    """Get detailed user analytics"""
    try:
        user_analytics = await advanced_analytics_service._get_user_analytics(instance_id)
        return {
            "user_analytics": user_analytics,
            "timeframe": timeframe,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user analytics: {str(e)}")


@router.get("/performance-insights")
async def get_performance_insights(
    instance_id: Optional[str] = Query(None, description="Instance ID for filtering"),
    current_user = Depends(get_current_admin_user)
):
    """Get performance insights and anomalies"""
    try:
        performance_insights = await advanced_analytics_service._get_performance_insights(instance_id)
        return {
            "performance_insights": performance_insights,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance insights: {str(e)}")


@router.get("/business-metrics")
async def get_business_metrics(
    instance_id: Optional[str] = Query(None, description="Instance ID for filtering"),
    current_user = Depends(get_current_admin_user)
):
    """Get business intelligence metrics"""
    try:
        business_metrics = await advanced_analytics_service._get_business_metrics(instance_id)
        return {
            "business_metrics": business_metrics,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get business metrics: {str(e)}")


@router.get("/scaling-status")
async def get_scaling_status(
    current_user = Depends(get_current_admin_user)
):
    """Get AI auto-scaling status and decisions"""
    try:
        scaling_status = ai_autoscaling_service.get_scaling_status()
        return scaling_status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get scaling status: {str(e)}")


@router.get("/security-intelligence")
async def get_security_intelligence(
    current_user = Depends(get_current_admin_user)
):
    """Get security intelligence status"""
    try:
        security_status = security_intelligence_service.get_security_status()
        return security_status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get security intelligence: {str(e)}")


@router.get("/real-time-metrics")
async def get_real_time_metrics(
    instance_id: Optional[str] = Query(None, description="Instance ID for filtering"),
    current_user = Depends(get_current_admin_user)
):
    """Get real-time system metrics"""
    try:
        from ....services.performance_service import performance_service
        metrics = await performance_service.get_real_time_metrics()
        
        # Add analytics-specific metrics
        core_metrics = await advanced_analytics_service._get_core_metrics(instance_id)
        
        return {
            "system_metrics": metrics,
            "core_metrics": core_metrics,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get real-time metrics: {str(e)}")


@router.get("/anomaly-detection")
async def get_anomaly_detection(
    instance_id: Optional[str] = Query(None, description="Instance ID for filtering"),
    current_user = Depends(get_current_admin_user)
):
    """Get anomaly detection results"""
    try:
        # Get performance anomalies
        perf_anomalies = await advanced_analytics_service._detect_performance_anomalies(instance_id)
        
        # Get security anomalies
        security_events = security_intelligence_service.security_events
        recent_security_events = [
            event for event in security_events 
            if event.timestamp > datetime.utcnow() - timedelta(hours=24)
        ]
        
        return {
            "performance_anomalies": [
                {
                    "type": anomaly.insight_type,
                    "title": anomaly.title,
                    "description": anomaly.description,
                    "confidence": anomaly.confidence,
                    "impact": anomaly.impact
                }
                for anomaly in perf_anomalies
            ],
            "security_events": [
                {
                    "event_id": event.event_id,
                    "threat_level": event.threat_level.value,
                    "source_ip": event.source_ip,
                    "event_type": event.event_type,
                    "timestamp": event.timestamp.isoformat()
                }
                for event in recent_security_events[-10:]  # Last 10 events
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get anomaly detection: {str(e)}")


@router.get("/optimization-recommendations")
async def get_optimization_recommendations(
    instance_id: Optional[str] = Query(None, description="Instance ID for filtering"),
    current_user = Depends(get_current_admin_user)
):
    """Get AI-powered optimization recommendations"""
    try:
        # Get insights and filter for optimization recommendations
        insights = await advanced_analytics_service._get_ai_insights(instance_id)
        
        optimization_insights = [
            insight for insight in insights 
            if "optimization" in insight["title"].lower() or 
               "improve" in insight["description"].lower() or
               "enhance" in insight["recommendation"].lower()
        ]
        
        # Get scaling recommendations
        scaling_status = ai_autoscaling_service.get_scaling_status()
        
        return {
            "performance_optimizations": optimization_insights,
            "scaling_recommendations": {
                "current_instances": scaling_status["current_instances"],
                "recommended_action": "maintain" if scaling_status["current_instances"] == scaling_status["min_instances"] else "optimize",
                "ai_model_status": scaling_status["ai_model_status"]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get optimization recommendations: {str(e)}")


@router.get("/trend-analysis")
async def get_trend_analysis(
    instance_id: Optional[str] = Query(None, description="Instance ID for filtering"),
    metric: str = Query("all", description="Specific metric to analyze (traffic, performance, users, errors)"),
    timeframe: str = Query("24h", description="Timeframe for analysis (1h, 24h, 7d, 30d)"),
    current_user = Depends(get_current_admin_user)
):
    """Get trend analysis for various metrics"""
    try:
        # This would implement sophisticated trend analysis
        # For now, return sample trend data
        
        trends = {
            "traffic": {
                "direction": "increasing",
                "rate": 15.2,  # percentage
                "confidence": 0.87,
                "forecast": "continued_growth"
            },
            "performance": {
                "direction": "stable",
                "rate": 2.1,
                "confidence": 0.92,
                "forecast": "stable"
            },
            "users": {
                "direction": "increasing",
                "rate": 8.5,
                "confidence": 0.79,
                "forecast": "moderate_growth"
            },
            "errors": {
                "direction": "decreasing",
                "rate": -12.3,
                "confidence": 0.85,
                "forecast": "continued_improvement"
            }
        }
        
        if metric != "all" and metric in trends:
            return {metric: trends[metric], "timeframe": timeframe}
        
        return {"trends": trends, "timeframe": timeframe, "timestamp": datetime.utcnow().isoformat()}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get trend analysis: {str(e)}")


@router.get("/export")
async def export_analytics_data(
    instance_id: Optional[str] = Query(None, description="Instance ID for filtering"),
    format: str = Query("json", description="Export format (json, csv)"),
    timeframe: str = Query("24h", description="Timeframe for export"),
    current_user = Depends(get_current_admin_user)
):
    """Export analytics data"""
    try:
        # Get comprehensive dashboard data
        dashboard_data = await advanced_analytics_service.get_real_time_dashboard(instance_id)
        
        if format == "csv":
            # Convert to CSV format (simplified)
            return {
                "message": "CSV export not implemented yet",
                "data": dashboard_data
            }
        
        return {
            "export_format": format,
            "timeframe": timeframe,
            "exported_at": datetime.utcnow().isoformat(),
            "data": dashboard_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export analytics data: {str(e)}")
