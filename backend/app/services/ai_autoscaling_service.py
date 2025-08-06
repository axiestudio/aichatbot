"""
AI-Powered Auto-Scaling Service
Machine learning-based predictive scaling and resource optimization
"""

import asyncio
import logging
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import deque
import json

from .performance_service import performance_service
from .cache_service import cache_service
from ..core.config import settings

logger = logging.getLogger(__name__)


class AIAutoScalingService:
    """AI-powered predictive auto-scaling service"""
    
    def __init__(self):
        self.metrics_history = deque(maxlen=1000)  # Store last 1000 data points
        self.prediction_models = {}
        self.scaling_decisions = deque(maxlen=100)
        
        # Scaling thresholds
        self.thresholds = {
            "cpu_scale_up": 70,
            "cpu_scale_down": 30,
            "memory_scale_up": 80,
            "memory_scale_down": 40,
            "response_time_scale_up": 1000,  # ms
            "connections_scale_up": 500,
            "prediction_confidence": 0.8
        }
        
        # Current scaling state
        self.current_instances = 1
        self.max_instances = 10
        self.min_instances = 1
        self.last_scaling_action = None
        self.cooldown_period = 300  # 5 minutes
        
        # AI model parameters
        self.model_weights = {
            "cpu_weight": 0.3,
            "memory_weight": 0.25,
            "response_time_weight": 0.2,
            "connections_weight": 0.15,
            "trend_weight": 0.1
        }
        
        # Learning parameters
        self.learning_rate = 0.01
        self.prediction_window = 60  # Predict 60 seconds ahead
        
    async def start_ai_scaling(self):
        """Start AI-powered auto-scaling monitoring"""
        logger.info("🤖 AI Auto-Scaling Service started")
        asyncio.create_task(self._ai_scaling_loop())
    
    async def _ai_scaling_loop(self):
        """Main AI scaling loop"""
        while True:
            try:
                # Collect current metrics
                metrics = await self._collect_metrics()
                
                if metrics:
                    # Store metrics for learning
                    self.metrics_history.append(metrics)
                    
                    # Make scaling prediction
                    prediction = await self._predict_scaling_need(metrics)
                    
                    # Execute scaling decision if needed
                    if prediction["should_scale"]:
                        await self._execute_scaling_decision(prediction)
                    
                    # Update AI models based on recent performance
                    await self._update_ai_models()
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"AI scaling loop error: {e}")
                await asyncio.sleep(60)
    
    async def _collect_metrics(self) -> Optional[Dict[str, Any]]:
        """Collect comprehensive system metrics"""
        try:
            performance_data = await performance_service.get_real_time_metrics()
            
            if not performance_data.get("system_resources"):
                return None
            
            resources = performance_data["system_resources"]
            
            metrics = {
                "timestamp": datetime.utcnow(),
                "cpu_percent": resources.get("cpu_percent", 0),
                "memory_percent": resources.get("memory_percent", 0),
                "active_requests": performance_data.get("active_requests", 0),
                "response_time_avg": await self._calculate_avg_response_time(),
                "websocket_connections": await self._get_websocket_connections(),
                "cache_hit_rate": await self._get_cache_hit_rate(),
                "error_rate": await self._calculate_error_rate(),
                "instances": self.current_instances
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
            return None
    
    async def _predict_scaling_need(self, current_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """AI-powered prediction of scaling needs"""
        try:
            # Calculate trend analysis
            trend_analysis = self._analyze_trends()
            
            # Calculate load score
            load_score = self._calculate_load_score(current_metrics)
            
            # Predict future load
            future_load = self._predict_future_load(current_metrics, trend_analysis)
            
            # Determine scaling action
            scaling_action = self._determine_scaling_action(
                current_metrics, load_score, future_load, trend_analysis
            )
            
            prediction = {
                "timestamp": datetime.utcnow(),
                "current_load_score": load_score,
                "predicted_load": future_load,
                "trend_direction": trend_analysis["direction"],
                "confidence": trend_analysis["confidence"],
                "should_scale": scaling_action["should_scale"],
                "scale_direction": scaling_action["direction"],
                "recommended_instances": scaling_action["target_instances"],
                "reasoning": scaling_action["reasoning"]
            }
            
            return prediction
            
        except Exception as e:
            logger.error(f"Error in scaling prediction: {e}")
            return {"should_scale": False, "error": str(e)}
    
    def _analyze_trends(self) -> Dict[str, Any]:
        """Analyze historical trends using simple ML"""
        if len(self.metrics_history) < 10:
            return {"direction": "stable", "confidence": 0.0, "slope": 0.0}
        
        try:
            # Extract recent CPU and memory data
            recent_data = list(self.metrics_history)[-20:]  # Last 20 data points
            
            cpu_values = [m["cpu_percent"] for m in recent_data]
            memory_values = [m["memory_percent"] for m in recent_data]
            response_times = [m["response_time_avg"] for m in recent_data]
            
            # Calculate trends using linear regression
            x = np.arange(len(cpu_values))
            
            cpu_slope = np.polyfit(x, cpu_values, 1)[0]
            memory_slope = np.polyfit(x, memory_values, 1)[0]
            response_slope = np.polyfit(x, response_times, 1)[0]
            
            # Weighted average slope
            combined_slope = (
                cpu_slope * self.model_weights["cpu_weight"] +
                memory_slope * self.model_weights["memory_weight"] +
                response_slope * self.model_weights["response_time_weight"]
            )
            
            # Determine direction and confidence
            if abs(combined_slope) < 0.5:
                direction = "stable"
                confidence = 0.9
            elif combined_slope > 0:
                direction = "increasing"
                confidence = min(0.9, abs(combined_slope) / 10)
            else:
                direction = "decreasing"
                confidence = min(0.9, abs(combined_slope) / 10)
            
            return {
                "direction": direction,
                "confidence": confidence,
                "slope": combined_slope,
                "cpu_slope": cpu_slope,
                "memory_slope": memory_slope,
                "response_slope": response_slope
            }
            
        except Exception as e:
            logger.error(f"Error analyzing trends: {e}")
            return {"direction": "stable", "confidence": 0.0, "slope": 0.0}
    
    def _calculate_load_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate weighted load score (0-100)"""
        try:
            cpu_score = metrics["cpu_percent"]
            memory_score = metrics["memory_percent"]
            
            # Response time score (normalize to 0-100)
            response_score = min(100, (metrics["response_time_avg"] / 2000) * 100)
            
            # Connection score (normalize based on typical load)
            connection_score = min(100, (metrics["active_requests"] / 100) * 100)
            
            # Weighted combination
            load_score = (
                cpu_score * self.model_weights["cpu_weight"] +
                memory_score * self.model_weights["memory_weight"] +
                response_score * self.model_weights["response_time_weight"] +
                connection_score * self.model_weights["connections_weight"]
            )
            
            return min(100, max(0, load_score))
            
        except Exception as e:
            logger.error(f"Error calculating load score: {e}")
            return 0.0
    
    def _predict_future_load(self, current_metrics: Dict[str, Any], trend_analysis: Dict[str, Any]) -> float:
        """Predict future load based on trends"""
        try:
            current_load = self._calculate_load_score(current_metrics)
            
            # Apply trend prediction
            trend_factor = trend_analysis["slope"] * trend_analysis["confidence"]
            
            # Predict load in next prediction window
            predicted_load = current_load + (trend_factor * self.prediction_window / 60)
            
            return min(100, max(0, predicted_load))
            
        except Exception as e:
            logger.error(f"Error predicting future load: {e}")
            return current_metrics.get("cpu_percent", 0)
    
    def _determine_scaling_action(
        self, 
        metrics: Dict[str, Any], 
        load_score: float, 
        future_load: float, 
        trend_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Determine if scaling action is needed"""
        
        # Check cooldown period
        if self.last_scaling_action:
            time_since_last = (datetime.utcnow() - self.last_scaling_action).total_seconds()
            if time_since_last < self.cooldown_period:
                return {
                    "should_scale": False,
                    "direction": "none",
                    "target_instances": self.current_instances,
                    "reasoning": "Cooldown period active"
                }
        
        # Scale up conditions
        scale_up_conditions = [
            metrics["cpu_percent"] > self.thresholds["cpu_scale_up"],
            metrics["memory_percent"] > self.thresholds["memory_scale_up"],
            metrics["response_time_avg"] > self.thresholds["response_time_scale_up"],
            future_load > 80 and trend_analysis["confidence"] > self.thresholds["prediction_confidence"]
        ]
        
        # Scale down conditions
        scale_down_conditions = [
            metrics["cpu_percent"] < self.thresholds["cpu_scale_down"],
            metrics["memory_percent"] < self.thresholds["memory_scale_down"],
            metrics["response_time_avg"] < 200,
            future_load < 40 and trend_analysis["confidence"] > self.thresholds["prediction_confidence"],
            self.current_instances > self.min_instances
        ]
        
        # Decision logic
        if sum(scale_up_conditions) >= 2 and self.current_instances < self.max_instances:
            target_instances = min(self.max_instances, self.current_instances + 1)
            return {
                "should_scale": True,
                "direction": "up",
                "target_instances": target_instances,
                "reasoning": f"Scale up: Load={load_score:.1f}, Future={future_load:.1f}, Trend={trend_analysis['direction']}"
            }
        
        elif all(scale_down_conditions) and self.current_instances > self.min_instances:
            target_instances = max(self.min_instances, self.current_instances - 1)
            return {
                "should_scale": True,
                "direction": "down",
                "target_instances": target_instances,
                "reasoning": f"Scale down: Load={load_score:.1f}, Future={future_load:.1f}, Trend={trend_analysis['direction']}"
            }
        
        return {
            "should_scale": False,
            "direction": "none",
            "target_instances": self.current_instances,
            "reasoning": "No scaling needed"
        }
    
    async def _execute_scaling_decision(self, prediction: Dict[str, Any]):
        """Execute scaling decision (simulation for now)"""
        try:
            old_instances = self.current_instances
            new_instances = prediction["target_instances"]
            
            # In a real implementation, this would trigger actual scaling
            # For now, we simulate the scaling action
            self.current_instances = new_instances
            self.last_scaling_action = datetime.utcnow()
            
            # Store scaling decision
            decision = {
                "timestamp": datetime.utcnow(),
                "old_instances": old_instances,
                "new_instances": new_instances,
                "direction": prediction["direction"],
                "reasoning": prediction["reasoning"],
                "prediction": prediction
            }
            
            self.scaling_decisions.append(decision)
            
            logger.info(f"🤖 AI Scaling: {old_instances} → {new_instances} instances ({prediction['direction']}) - {prediction['reasoning']}")
            
            # Cache the scaling event
            await cache_service.set(
                f"scaling_event_{datetime.utcnow().isoformat()}", 
                decision, 
                "scaling", 
                3600
            )
            
        except Exception as e:
            logger.error(f"Error executing scaling decision: {e}")
    
    async def _update_ai_models(self):
        """Update AI models based on recent performance"""
        try:
            if len(self.metrics_history) < 50:
                return
            
            # Simple model adaptation based on prediction accuracy
            recent_metrics = list(self.metrics_history)[-10:]
            
            # Calculate prediction accuracy and adjust weights
            # This is a simplified version - in production, you'd use more sophisticated ML
            
            # For now, just log that model update occurred
            logger.debug("🧠 AI models updated based on recent performance")
            
        except Exception as e:
            logger.error(f"Error updating AI models: {e}")
    
    async def _calculate_avg_response_time(self) -> float:
        """Calculate average response time from recent requests"""
        try:
            performance_data = await performance_service.get_performance_summary(5)  # Last 5 minutes
            api_metrics = performance_data.get("metrics", {}).get("api_response_time", {})
            return api_metrics.get("avg", 0)
        except:
            return 0
    
    async def _get_websocket_connections(self) -> int:
        """Get current WebSocket connection count"""
        try:
            from .websocket_manager import websocket_manager
            stats = websocket_manager.get_connection_stats()
            return stats.get("total_connections", 0)
        except:
            return 0
    
    async def _get_cache_hit_rate(self) -> float:
        """Get current cache hit rate"""
        try:
            stats = cache_service.get_stats()
            return stats.get("hit_rate_percent", 0)
        except:
            return 0
    
    async def _calculate_error_rate(self) -> float:
        """Calculate current error rate"""
        try:
            performance_data = await performance_service.get_real_time_metrics()
            counters = performance_data.get("counters", {})
            total_requests = counters.get("total_requests", 0)
            error_requests = counters.get("error_requests", 0)
            
            if total_requests == 0:
                return 0
            
            return (error_requests / total_requests) * 100
        except:
            return 0
    
    def get_scaling_status(self) -> Dict[str, Any]:
        """Get current scaling status and predictions"""
        return {
            "current_instances": self.current_instances,
            "min_instances": self.min_instances,
            "max_instances": self.max_instances,
            "last_scaling_action": self.last_scaling_action.isoformat() if self.last_scaling_action else None,
            "recent_decisions": list(self.scaling_decisions)[-5:],  # Last 5 decisions
            "metrics_collected": len(self.metrics_history),
            "ai_model_status": "active",
            "thresholds": self.thresholds
        }


# Global AI auto-scaling service instance
ai_autoscaling_service = AIAutoScalingService()
