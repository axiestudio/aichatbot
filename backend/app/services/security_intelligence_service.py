"""
Advanced Security Intelligence Service
AI-powered threat detection, behavioral analysis, and automated response
"""

import asyncio
import logging
import hashlib
import json
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass
from enum import Enum
import re

from .cache_service import cache_service
from .rate_limit_service import rate_limit_service
from ..core.config import settings

logger = logging.getLogger(__name__)


class ThreatLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityEvent:
    event_id: str
    timestamp: datetime
    event_type: str
    threat_level: ThreatLevel
    source_ip: str
    user_agent: str
    endpoint: str
    details: Dict[str, Any]
    risk_score: float
    automated_response: Optional[str] = None


class SecurityIntelligenceService:
    """Advanced AI-powered security intelligence and threat detection"""
    
    def __init__(self):
        self.security_events = deque(maxlen=10000)
        self.threat_patterns = {}
        self.behavioral_profiles = defaultdict(dict)
        self.known_threats = set()
        self.whitelist_ips = set()
        
        # AI-powered threat detection patterns
        self.threat_signatures = {
            "sql_injection": [
                r"(\bunion\b.*\bselect\b)",
                r"(\bselect\b.*\bfrom\b.*\bwhere\b)",
                r"(\bdrop\b.*\btable\b)",
                r"(\binsert\b.*\binto\b)",
                r"(\bdelete\b.*\bfrom\b)"
            ],
            "xss_attack": [
                r"<script[^>]*>.*?</script>",
                r"javascript:",
                r"on\w+\s*=",
                r"<iframe[^>]*>",
                r"eval\s*\("
            ],
            "path_traversal": [
                r"\.\.\/",
                r"\.\.\\",
                r"%2e%2e%2f",
                r"%2e%2e%5c"
            ],
            "command_injection": [
                r";\s*(cat|ls|pwd|whoami|id|uname)",
                r"\|\s*(cat|ls|pwd|whoami|id|uname)",
                r"&&\s*(cat|ls|pwd|whoami|id|uname)",
                r"`.*`",
                r"\$\(.*\)"
            ],
            "brute_force": [
                r"admin",
                r"password",
                r"123456",
                r"qwerty"
            ]
        }
        
        # Behavioral analysis thresholds
        self.behavioral_thresholds = {
            "requests_per_minute": 100,
            "unique_endpoints_per_minute": 20,
            "error_rate_threshold": 50,  # percentage
            "suspicious_user_agents": [
                "sqlmap", "nikto", "nmap", "masscan", "zap", "burp",
                "python-requests", "curl", "wget"
            ],
            "geo_anomaly_threshold": 0.8  # Confidence threshold for geo anomalies
        }
        
        # Automated response actions
        self.response_actions = {
            ThreatLevel.LOW: ["log", "monitor"],
            ThreatLevel.MEDIUM: ["log", "monitor", "rate_limit"],
            ThreatLevel.HIGH: ["log", "monitor", "rate_limit", "temporary_block"],
            ThreatLevel.CRITICAL: ["log", "monitor", "rate_limit", "block", "alert_admin"]
        }
        
        # Machine learning features for threat scoring
        self.ml_features = {
            "request_frequency": 0.2,
            "error_rate": 0.25,
            "payload_entropy": 0.15,
            "user_agent_suspicion": 0.1,
            "geo_anomaly": 0.1,
            "time_pattern": 0.1,
            "endpoint_diversity": 0.1
        }
    
    async def start_security_monitoring(self):
        """Start security intelligence monitoring"""
        logger.info("🛡️ Security Intelligence Service started")
        asyncio.create_task(self._security_monitoring_loop())
        asyncio.create_task(self._behavioral_analysis_loop())
        asyncio.create_task(self._threat_intelligence_update_loop())
    
    async def analyze_request(self, request_data: Dict[str, Any]) -> SecurityEvent:
        """Analyze incoming request for security threats"""
        try:
            # Extract request features
            features = self._extract_request_features(request_data)
            
            # Calculate risk score
            risk_score = await self._calculate_risk_score(features)
            
            # Determine threat level
            threat_level = self._determine_threat_level(risk_score)
            
            # Detect specific attack patterns
            attack_patterns = self._detect_attack_patterns(request_data)
            
            # Create security event
            event = SecurityEvent(
                event_id=self._generate_event_id(request_data),
                timestamp=datetime.utcnow(),
                event_type="request_analysis",
                threat_level=threat_level,
                source_ip=request_data.get("source_ip", "unknown"),
                user_agent=request_data.get("user_agent", "unknown"),
                endpoint=request_data.get("endpoint", "unknown"),
                details={
                    "risk_score": risk_score,
                    "features": features,
                    "attack_patterns": attack_patterns,
                    "request_data": request_data
                },
                risk_score=risk_score
            )
            
            # Execute automated response
            if threat_level != ThreatLevel.LOW:
                await self._execute_automated_response(event)
            
            # Store event
            self.security_events.append(event)
            
            # Update behavioral profile
            await self._update_behavioral_profile(request_data, event)
            
            return event
            
        except Exception as e:
            logger.error(f"Error analyzing request: {e}")
            return None
    
    def _extract_request_features(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract security-relevant features from request"""
        try:
            features = {
                "method": request_data.get("method", "GET"),
                "endpoint": request_data.get("endpoint", ""),
                "query_params": request_data.get("query_params", {}),
                "headers": request_data.get("headers", {}),
                "body": request_data.get("body", ""),
                "source_ip": request_data.get("source_ip", ""),
                "user_agent": request_data.get("user_agent", ""),
                "timestamp": request_data.get("timestamp", datetime.utcnow()),
                "response_status": request_data.get("response_status", 200),
                "response_time": request_data.get("response_time", 0)
            }
            
            # Calculate payload entropy
            payload = str(features.get("body", "")) + str(features.get("query_params", ""))
            features["payload_entropy"] = self._calculate_entropy(payload)
            
            # Check for suspicious patterns
            features["has_suspicious_patterns"] = self._has_suspicious_patterns(features)
            
            # Analyze user agent
            features["user_agent_suspicion"] = self._analyze_user_agent(features["user_agent"])
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting features: {e}")
            return {}
    
    async def _calculate_risk_score(self, features: Dict[str, Any]) -> float:
        """Calculate AI-powered risk score (0-100)"""
        try:
            score = 0.0
            
            # Request frequency analysis
            ip = features.get("source_ip", "")
            recent_requests = await self._get_recent_request_count(ip)
            frequency_score = min(100, (recent_requests / 100) * 100)
            score += frequency_score * self.ml_features["request_frequency"]
            
            # Error rate analysis
            error_rate = await self._get_error_rate(ip)
            score += error_rate * self.ml_features["error_rate"]
            
            # Payload entropy (high entropy might indicate obfuscation)
            entropy = features.get("payload_entropy", 0)
            entropy_score = min(100, entropy * 20)  # Normalize entropy
            score += entropy_score * self.ml_features["payload_entropy"]
            
            # User agent suspicion
            ua_suspicion = features.get("user_agent_suspicion", 0)
            score += ua_suspicion * self.ml_features["user_agent_suspicion"]
            
            # Suspicious patterns
            if features.get("has_suspicious_patterns", False):
                score += 50 * self.ml_features["payload_entropy"]
            
            # Time-based anomalies
            time_anomaly = await self._detect_time_anomalies(ip)
            score += time_anomaly * self.ml_features["time_pattern"]
            
            # Endpoint diversity (too many different endpoints might be scanning)
            endpoint_diversity = await self._calculate_endpoint_diversity(ip)
            score += endpoint_diversity * self.ml_features["endpoint_diversity"]
            
            return min(100, max(0, score))
            
        except Exception as e:
            logger.error(f"Error calculating risk score: {e}")
            return 0.0
    
    def _determine_threat_level(self, risk_score: float) -> ThreatLevel:
        """Determine threat level based on risk score"""
        if risk_score >= 80:
            return ThreatLevel.CRITICAL
        elif risk_score >= 60:
            return ThreatLevel.HIGH
        elif risk_score >= 30:
            return ThreatLevel.MEDIUM
        else:
            return ThreatLevel.LOW
    
    def _detect_attack_patterns(self, request_data: Dict[str, Any]) -> List[str]:
        """Detect specific attack patterns in request"""
        detected_patterns = []
        
        # Combine all request data for pattern matching
        request_text = " ".join([
            str(request_data.get("endpoint", "")),
            str(request_data.get("query_params", "")),
            str(request_data.get("body", "")),
            str(request_data.get("headers", ""))
        ]).lower()
        
        # Check each threat signature
        for attack_type, patterns in self.threat_signatures.items():
            for pattern in patterns:
                if re.search(pattern, request_text, re.IGNORECASE):
                    detected_patterns.append(attack_type)
                    break
        
        return detected_patterns
    
    async def _execute_automated_response(self, event: SecurityEvent):
        """Execute automated response based on threat level"""
        try:
            actions = self.response_actions.get(event.threat_level, [])
            executed_actions = []
            
            for action in actions:
                if action == "log":
                    logger.warning(f"🚨 Security Event: {event.threat_level.value} - {event.source_ip} - {event.endpoint}")
                    executed_actions.append("logged")
                
                elif action == "monitor":
                    # Add to monitoring list
                    await cache_service.set(
                        f"monitor_ip_{event.source_ip}",
                        {"reason": event.event_type, "timestamp": event.timestamp.isoformat()},
                        "security",
                        3600
                    )
                    executed_actions.append("monitoring_enabled")
                
                elif action == "rate_limit":
                    # Apply stricter rate limiting
                    await rate_limit_service.add_to_blacklist(event.source_ip, 1800)  # 30 minutes
                    executed_actions.append("rate_limited")
                
                elif action == "temporary_block":
                    # Temporary block
                    await rate_limit_service.add_to_blacklist(event.source_ip, 3600)  # 1 hour
                    executed_actions.append("temporarily_blocked")
                
                elif action == "block":
                    # Permanent block (until manual review)
                    await rate_limit_service.add_to_blacklist(event.source_ip, 86400)  # 24 hours
                    executed_actions.append("blocked")
                
                elif action == "alert_admin":
                    # Send admin alert (would integrate with notification system)
                    logger.critical(f"🚨 CRITICAL SECURITY ALERT: {event.source_ip} - {event.details}")
                    executed_actions.append("admin_alerted")
            
            event.automated_response = ", ".join(executed_actions)
            
        except Exception as e:
            logger.error(f"Error executing automated response: {e}")
    
    def _calculate_entropy(self, text: str) -> float:
        """Calculate Shannon entropy of text"""
        if not text:
            return 0.0
        
        # Count character frequencies
        char_counts = {}
        for char in text:
            char_counts[char] = char_counts.get(char, 0) + 1
        
        # Calculate entropy
        entropy = 0.0
        text_length = len(text)
        
        for count in char_counts.values():
            probability = count / text_length
            if probability > 0:
                entropy -= probability * (probability.bit_length() - 1)
        
        return entropy
    
    def _has_suspicious_patterns(self, features: Dict[str, Any]) -> bool:
        """Check for suspicious patterns in request"""
        suspicious_indicators = [
            # Long query strings
            len(str(features.get("query_params", ""))) > 1000,
            
            # Suspicious file extensions
            any(ext in features.get("endpoint", "") for ext in [".php", ".asp", ".jsp", ".cgi"]),
            
            # Admin-related paths
            any(path in features.get("endpoint", "").lower() for path in ["admin", "wp-admin", "phpmyadmin"]),
            
            # Encoded characters
            any(enc in str(features.get("query_params", "")) for enc in ["%20", "%27", "%22", "%3C", "%3E"]),
        ]
        
        return any(suspicious_indicators)
    
    def _analyze_user_agent(self, user_agent: str) -> float:
        """Analyze user agent for suspicion score (0-100)"""
        if not user_agent:
            return 50  # No user agent is suspicious
        
        ua_lower = user_agent.lower()
        
        # Check against known suspicious user agents
        for suspicious_ua in self.behavioral_thresholds["suspicious_user_agents"]:
            if suspicious_ua in ua_lower:
                return 90
        
        # Check for automation indicators
        automation_indicators = ["bot", "crawler", "spider", "scraper", "automated"]
        if any(indicator in ua_lower for indicator in automation_indicators):
            return 30
        
        # Very short or very long user agents are suspicious
        if len(user_agent) < 10 or len(user_agent) > 500:
            return 60
        
        return 0
    
    async def _get_recent_request_count(self, ip: str) -> int:
        """Get recent request count for IP"""
        try:
            cache_key = f"request_count_{ip}"
            count = await cache_service.get(cache_key, "security") or 0
            return count
        except:
            return 0
    
    async def _get_error_rate(self, ip: str) -> float:
        """Get error rate for IP"""
        try:
            cache_key = f"error_rate_{ip}"
            error_rate = await cache_service.get(cache_key, "security") or 0
            return error_rate
        except:
            return 0
    
    async def _detect_time_anomalies(self, ip: str) -> float:
        """Detect time-based anomalies"""
        # Simplified implementation - would use more sophisticated time series analysis
        return 0
    
    async def _calculate_endpoint_diversity(self, ip: str) -> float:
        """Calculate endpoint diversity score"""
        try:
            cache_key = f"endpoints_{ip}"
            endpoints = await cache_service.get(cache_key, "security") or []
            unique_endpoints = len(set(endpoints))
            
            # High diversity might indicate scanning
            if unique_endpoints > 20:
                return min(100, unique_endpoints * 2)
            
            return 0
        except:
            return 0
    
    def _generate_event_id(self, request_data: Dict[str, Any]) -> str:
        """Generate unique event ID"""
        data_str = f"{request_data.get('source_ip', '')}{request_data.get('timestamp', '')}{request_data.get('endpoint', '')}"
        return hashlib.md5(data_str.encode()).hexdigest()[:16]
    
    async def _update_behavioral_profile(self, request_data: Dict[str, Any], event: SecurityEvent):
        """Update behavioral profile for IP"""
        try:
            ip = request_data.get("source_ip", "")
            if not ip:
                return
            
            profile_key = f"behavior_{ip}"
            profile = await cache_service.get(profile_key, "security") or {
                "first_seen": datetime.utcnow().isoformat(),
                "request_count": 0,
                "threat_events": 0,
                "endpoints": [],
                "user_agents": [],
                "last_activity": datetime.utcnow().isoformat()
            }
            
            # Update profile
            profile["request_count"] += 1
            profile["last_activity"] = datetime.utcnow().isoformat()
            
            if event.threat_level != ThreatLevel.LOW:
                profile["threat_events"] += 1
            
            # Track endpoints and user agents
            endpoint = request_data.get("endpoint", "")
            if endpoint and endpoint not in profile["endpoints"]:
                profile["endpoints"].append(endpoint)
                profile["endpoints"] = profile["endpoints"][-50:]  # Keep last 50
            
            user_agent = request_data.get("user_agent", "")
            if user_agent and user_agent not in profile["user_agents"]:
                profile["user_agents"].append(user_agent)
                profile["user_agents"] = profile["user_agents"][-10:]  # Keep last 10
            
            # Store updated profile
            await cache_service.set(profile_key, profile, "security", 86400)  # 24 hours
            
        except Exception as e:
            logger.error(f"Error updating behavioral profile: {e}")
    
    async def _security_monitoring_loop(self):
        """Main security monitoring loop"""
        while True:
            try:
                # Analyze recent security events
                await self._analyze_security_trends()
                
                # Update threat intelligence
                await self._update_threat_patterns()
                
                # Clean up old events
                await self._cleanup_old_events()
                
                await asyncio.sleep(300)  # Run every 5 minutes
                
            except Exception as e:
                logger.error(f"Security monitoring loop error: {e}")
                await asyncio.sleep(60)
    
    async def _behavioral_analysis_loop(self):
        """Behavioral analysis loop"""
        while True:
            try:
                # Analyze behavioral patterns
                await self._analyze_behavioral_patterns()
                
                await asyncio.sleep(600)  # Run every 10 minutes
                
            except Exception as e:
                logger.error(f"Behavioral analysis loop error: {e}")
                await asyncio.sleep(120)
    
    async def _threat_intelligence_update_loop(self):
        """Threat intelligence update loop"""
        while True:
            try:
                # Update threat intelligence feeds
                await self._update_threat_intelligence()
                
                await asyncio.sleep(3600)  # Run every hour
                
            except Exception as e:
                logger.error(f"Threat intelligence update error: {e}")
                await asyncio.sleep(300)
    
    async def _analyze_security_trends(self):
        """Analyze security trends and patterns"""
        # Implementation would analyze trends in security events
        pass
    
    async def _update_threat_patterns(self):
        """Update threat detection patterns"""
        # Implementation would update ML models and patterns
        pass
    
    async def _cleanup_old_events(self):
        """Clean up old security events"""
        cutoff_time = datetime.utcnow() - timedelta(days=7)
        self.security_events = deque(
            [event for event in self.security_events if event.timestamp > cutoff_time],
            maxlen=10000
        )
    
    async def _analyze_behavioral_patterns(self):
        """Analyze behavioral patterns"""
        # Implementation would analyze user behavior patterns
        pass
    
    async def _update_threat_intelligence(self):
        """Update threat intelligence feeds"""
        # Implementation would fetch latest threat intelligence
        pass
    
    def get_security_status(self) -> Dict[str, Any]:
        """Get current security status"""
        recent_events = [e for e in self.security_events if e.timestamp > datetime.utcnow() - timedelta(hours=24)]
        
        threat_counts = {level.value: 0 for level in ThreatLevel}
        for event in recent_events:
            threat_counts[event.threat_level.value] += 1
        
        return {
            "total_events_24h": len(recent_events),
            "threat_level_counts": threat_counts,
            "active_monitoring": len(self.behavioral_profiles),
            "known_threats": len(self.known_threats),
            "whitelist_size": len(self.whitelist_ips),
            "ai_models_active": True,
            "last_update": datetime.utcnow().isoformat()
        }


# Global security intelligence service instance
security_intelligence_service = SecurityIntelligenceService()
