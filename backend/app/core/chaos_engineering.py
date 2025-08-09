"""
Chaos Engineering Framework
Netflix-style chaos engineering for resilience testing
"""

import asyncio
import random
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import time

logger = logging.getLogger(__name__)


class ChaosType(Enum):
    """Types of chaos experiments"""
    LATENCY_INJECTION = "latency_injection"
    ERROR_INJECTION = "error_injection"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    NETWORK_PARTITION = "network_partition"
    SERVICE_FAILURE = "service_failure"
    DATABASE_SLOWDOWN = "database_slowdown"
    MEMORY_PRESSURE = "memory_pressure"
    CPU_SPIKE = "cpu_spike"


@dataclass
class ChaosExperiment:
    """Chaos experiment definition"""
    name: str
    chaos_type: ChaosType
    target_service: str
    probability: float  # 0.0 to 1.0
    duration_seconds: int
    parameters: Dict[str, Any]
    enabled: bool = True
    last_executed: Optional[datetime] = None
    execution_count: int = 0


class ChaosMonkey:
    """
    Netflix-style Chaos Monkey for resilience testing
    """
    
    def __init__(self):
        self.experiments: List[ChaosExperiment] = []
        self.active_chaos: Dict[str, Dict[str, Any]] = {}
        self.chaos_history: List[Dict[str, Any]] = []
        self.enabled = False
        self.safety_mode = True  # Prevents destructive chaos in production
        
    def register_experiment(self, experiment: ChaosExperiment):
        """Register a chaos experiment"""
        self.experiments.append(experiment)
        logger.info(f"Registered chaos experiment: {experiment.name}")
        
    def enable_chaos(self, safety_mode: bool = True):
        """Enable chaos engineering"""
        self.enabled = True
        self.safety_mode = safety_mode
        logger.warning(f"Chaos engineering enabled (safety_mode={safety_mode})")
        
    def disable_chaos(self):
        """Disable chaos engineering"""
        self.enabled = False
        logger.info("Chaos engineering disabled")
        
    async def start_chaos_loop(self):
        """Start the main chaos loop"""
        if not self.enabled:
            return
            
        logger.info("Starting chaos engineering loop")
        
        while self.enabled:
            try:
                await self._execute_chaos_round()
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Chaos loop error: {e}")
                await asyncio.sleep(120)
                
    async def _execute_chaos_round(self):
        """Execute one round of chaos experiments"""
        for experiment in self.experiments:
            if not experiment.enabled:
                continue
                
            # Check if experiment should run
            if random.random() < experiment.probability:
                await self._execute_experiment(experiment)
                
    async def _execute_experiment(self, experiment: ChaosExperiment):
        """Execute a specific chaos experiment"""
        if self.safety_mode and experiment.chaos_type in [
            ChaosType.SERVICE_FAILURE,
            ChaosType.RESOURCE_EXHAUSTION
        ]:
            logger.info(f"Skipping destructive experiment {experiment.name} (safety mode)")
            return
            
        logger.warning(f"Executing chaos experiment: {experiment.name}")
        
        chaos_id = f"{experiment.name}_{int(time.time())}"
        
        # Record experiment start
        chaos_record = {
            "id": chaos_id,
            "experiment": experiment.name,
            "type": experiment.chaos_type.value,
            "target": experiment.target_service,
            "start_time": datetime.utcnow(),
            "duration": experiment.duration_seconds,
            "parameters": experiment.parameters,
            "status": "running"
        }
        
        self.active_chaos[chaos_id] = chaos_record
        self.chaos_history.append(chaos_record)
        
        try:
            # Execute the chaos based on type
            if experiment.chaos_type == ChaosType.LATENCY_INJECTION:
                await self._inject_latency(experiment)
            elif experiment.chaos_type == ChaosType.ERROR_INJECTION:
                await self._inject_errors(experiment)
            elif experiment.chaos_type == ChaosType.DATABASE_SLOWDOWN:
                await self._slowdown_database(experiment)
            elif experiment.chaos_type == ChaosType.MEMORY_PRESSURE:
                await self._create_memory_pressure(experiment)
            elif experiment.chaos_type == ChaosType.CPU_SPIKE:
                await self._create_cpu_spike(experiment)
                
            # Update experiment
            experiment.last_executed = datetime.utcnow()
            experiment.execution_count += 1
            
            # Mark as completed
            chaos_record["status"] = "completed"
            chaos_record["end_time"] = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Chaos experiment {experiment.name} failed: {e}")
            chaos_record["status"] = "failed"
            chaos_record["error"] = str(e)
            chaos_record["end_time"] = datetime.utcnow()
            
        finally:
            # Remove from active chaos
            if chaos_id in self.active_chaos:
                del self.active_chaos[chaos_id]
                
    async def _inject_latency(self, experiment: ChaosExperiment):
        """Inject artificial latency"""
        latency_ms = experiment.parameters.get("latency_ms", 1000)
        
        # This would integrate with your service layer to add delays
        logger.info(f"Injecting {latency_ms}ms latency to {experiment.target_service}")
        
        # Simulate latency injection for duration
        await asyncio.sleep(experiment.duration_seconds)
        
    async def _inject_errors(self, experiment: ChaosExperiment):
        """Inject artificial errors"""
        error_rate = experiment.parameters.get("error_rate", 0.1)
        error_type = experiment.parameters.get("error_type", "generic")
        
        logger.info(f"Injecting {error_rate*100}% error rate to {experiment.target_service}")
        
        # This would integrate with your service layer to inject errors
        await asyncio.sleep(experiment.duration_seconds)
        
    async def _slowdown_database(self, experiment: ChaosExperiment):
        """Simulate database slowdown"""
        slowdown_factor = experiment.parameters.get("slowdown_factor", 2.0)
        
        logger.info(f"Slowing down database by factor {slowdown_factor}")
        
        # This would integrate with your database layer
        await asyncio.sleep(experiment.duration_seconds)
        
    async def _create_memory_pressure(self, experiment: ChaosExperiment):
        """Create memory pressure"""
        memory_mb = experiment.parameters.get("memory_mb", 100)
        
        logger.info(f"Creating {memory_mb}MB memory pressure")
        
        # Allocate memory to create pressure
        memory_hog = []
        try:
            for _ in range(memory_mb):
                memory_hog.append(b'0' * 1024 * 1024)  # 1MB chunks
                
            await asyncio.sleep(experiment.duration_seconds)
            
        finally:
            # Clean up memory
            del memory_hog
            
    async def _create_cpu_spike(self, experiment: ChaosExperiment):
        """Create CPU spike"""
        cpu_intensity = experiment.parameters.get("cpu_intensity", 0.5)
        
        logger.info(f"Creating CPU spike with intensity {cpu_intensity}")
        
        end_time = time.time() + experiment.duration_seconds
        
        while time.time() < end_time:
            # Busy wait to consume CPU
            start = time.time()
            while time.time() - start < cpu_intensity:
                pass
            await asyncio.sleep(1 - cpu_intensity)
            
    def get_chaos_status(self) -> Dict[str, Any]:
        """Get current chaos status"""
        return {
            "enabled": self.enabled,
            "safety_mode": self.safety_mode,
            "active_experiments": len(self.active_chaos),
            "total_experiments": len(self.experiments),
            "enabled_experiments": len([e for e in self.experiments if e.enabled]),
            "active_chaos": list(self.active_chaos.values()),
            "recent_history": self.chaos_history[-10:],  # Last 10 experiments
            "timestamp": datetime.utcnow().isoformat()
        }
        
    def create_default_experiments(self):
        """Create default chaos experiments"""
        experiments = [
            ChaosExperiment(
                name="api_latency_spike",
                chaos_type=ChaosType.LATENCY_INJECTION,
                target_service="api",
                probability=0.05,  # 5% chance per minute
                duration_seconds=30,
                parameters={"latency_ms": 2000}
            ),
            ChaosExperiment(
                name="database_slowdown",
                chaos_type=ChaosType.DATABASE_SLOWDOWN,
                target_service="database",
                probability=0.02,  # 2% chance per minute
                duration_seconds=60,
                parameters={"slowdown_factor": 3.0}
            ),
            ChaosExperiment(
                name="ai_service_errors",
                chaos_type=ChaosType.ERROR_INJECTION,
                target_service="ai_service",
                probability=0.03,  # 3% chance per minute
                duration_seconds=45,
                parameters={"error_rate": 0.2, "error_type": "timeout"}
            ),
            ChaosExperiment(
                name="memory_pressure_test",
                chaos_type=ChaosType.MEMORY_PRESSURE,
                target_service="application",
                probability=0.01,  # 1% chance per minute
                duration_seconds=120,
                parameters={"memory_mb": 200}
            ),
            ChaosExperiment(
                name="cpu_spike_test",
                chaos_type=ChaosType.CPU_SPIKE,
                target_service="application",
                probability=0.01,  # 1% chance per minute
                duration_seconds=60,
                parameters={"cpu_intensity": 0.8}
            )
        ]
        
        for experiment in experiments:
            self.register_experiment(experiment)


class ResilienceValidator:
    """
    Validate system resilience during chaos experiments
    """
    
    def __init__(self):
        self.validation_rules = []
        self.validation_results = []
        
    def add_validation_rule(self, name: str, check_function: Callable, threshold: float):
        """Add a validation rule"""
        self.validation_rules.append({
            "name": name,
            "check_function": check_function,
            "threshold": threshold
        })
        
    async def validate_resilience(self) -> Dict[str, Any]:
        """Validate system resilience"""
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_resilience": "unknown",
            "validations": [],
            "score": 0.0
        }
        
        passed_validations = 0
        
        for rule in self.validation_rules:
            try:
                result = await rule["check_function"]()
                passed = result >= rule["threshold"]
                
                validation_result = {
                    "name": rule["name"],
                    "result": result,
                    "threshold": rule["threshold"],
                    "passed": passed,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                results["validations"].append(validation_result)
                
                if passed:
                    passed_validations += 1
                    
            except Exception as e:
                logger.error(f"Validation rule {rule['name']} failed: {e}")
                results["validations"].append({
                    "name": rule["name"],
                    "error": str(e),
                    "passed": False,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
        # Calculate overall score
        if self.validation_rules:
            results["score"] = passed_validations / len(self.validation_rules)
            
            if results["score"] >= 0.9:
                results["overall_resilience"] = "excellent"
            elif results["score"] >= 0.7:
                results["overall_resilience"] = "good"
            elif results["score"] >= 0.5:
                results["overall_resilience"] = "fair"
            else:
                results["overall_resilience"] = "poor"
                
        self.validation_results.append(results)
        return results


# Global chaos monkey instance
chaos_monkey = ChaosMonkey()
resilience_validator = ResilienceValidator()
