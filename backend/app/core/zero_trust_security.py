"""
Zero Trust Security Architecture
Google/Netflix-style zero trust security with comprehensive threat detection
"""

import asyncio
import hashlib
import hmac
import jwt
import time
import logging
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import ipaddress
import re
import json

logger = logging.getLogger(__name__)


class ThreatLevel(Enum):
    """Threat severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityAction(Enum):
    """Security actions to take"""
    ALLOW = "allow"
    CHALLENGE = "challenge"
    BLOCK = "block"
    QUARANTINE = "quarantine"


@dataclass
class SecurityContext:
    """Security context for requests"""
    user_id: Optional[str]
    session_id: Optional[str]
    ip_address: str
    user_agent: str
    timestamp: datetime
    trust_score: float  # 0.0 to 1.0
    risk_factors: List[str]
    authentication_method: str
    device_fingerprint: Optional[str] = None
    geolocation: Optional[Dict[str, str]] = None


@dataclass
class ThreatDetection:
    """Threat detection result"""
    threat_id: str
    threat_type: str
    threat_level: ThreatLevel
    confidence: float
    description: str
    indicators: List[str]
    recommended_action: SecurityAction
    context: SecurityContext


class DeviceFingerprinting:
    """
    Device fingerprinting for zero trust verification
    """
    
    def __init__(self):
        self.known_devices = {}
        self.suspicious_patterns = [
            r"bot|crawler|spider|scraper",
            r"curl|wget|python-requests",
            r"automated|headless"
        ]
        
    def generate_fingerprint(self, headers: Dict[str, str], ip: str) -> str:
        """Generate device fingerprint"""
        fingerprint_data = {
            "user_agent": headers.get("user-agent", ""),
            "accept": headers.get("accept", ""),
            "accept_language": headers.get("accept-language", ""),
            "accept_encoding": headers.get("accept-encoding", ""),
            "ip_class": str(ipaddress.ip_address(ip).is_private),
        }
        
        fingerprint_string = json.dumps(fingerprint_data, sort_keys=True)
        return hashlib.sha256(fingerprint_string.encode()).hexdigest()
        
    def is_suspicious_device(self, fingerprint: str, headers: Dict[str, str]) -> bool:
        """Check if device appears suspicious"""
        user_agent = headers.get("user-agent", "").lower()
        
        # Check for bot patterns
        for pattern in self.suspicious_patterns:
            if re.search(pattern, user_agent, re.IGNORECASE):
                return True
                
        # Check for missing common headers
        required_headers = ["user-agent", "accept"]
        missing_headers = [h for h in required_headers if h not in headers]
        
        return len(missing_headers) > 0
        
    def update_device_trust(self, fingerprint: str, trust_delta: float):
        """Update device trust score"""
        if fingerprint not in self.known_devices:
            self.known_devices[fingerprint] = {
                "trust_score": 0.5,
                "first_seen": datetime.utcnow(),
                "last_seen": datetime.utcnow(),
                "interaction_count": 0
            }
            
        device = self.known_devices[fingerprint]
        device["trust_score"] = max(0.0, min(1.0, device["trust_score"] + trust_delta))
        device["last_seen"] = datetime.utcnow()
        device["interaction_count"] += 1


class BehaviorAnalyzer:
    """
    Behavioral analysis for anomaly detection
    """
    
    def __init__(self):
        self.user_baselines = {}
        self.session_patterns = {}
        
    def analyze_user_behavior(self, user_id: str, action: str, context: Dict[str, Any]) -> float:
        """Analyze user behavior and return anomaly score (0.0 = normal, 1.0 = highly anomalous)"""
        if user_id not in self.user_baselines:
            self.user_baselines[user_id] = {
                "actions": [],
                "typical_hours": set(),
                "typical_ips": set(),
                "action_frequency": {},
                "last_activity": datetime.utcnow()
            }
            
        baseline = self.user_baselines[user_id]
        anomaly_score = 0.0
        
        # Check time-based anomalies
        current_hour = datetime.utcnow().hour
        if baseline["typical_hours"] and current_hour not in baseline["typical_hours"]:
            anomaly_score += 0.3
            
        # Check IP-based anomalies
        current_ip = context.get("ip_address")
        if current_ip and baseline["typical_ips"] and current_ip not in baseline["typical_ips"]:
            anomaly_score += 0.4
            
        # Check action frequency anomalies
        if action in baseline["action_frequency"]:
            typical_frequency = baseline["action_frequency"][action]
            time_since_last = (datetime.utcnow() - baseline["last_activity"]).total_seconds()
            
            if time_since_last < typical_frequency * 0.1:  # Too frequent
                anomaly_score += 0.5
                
        # Update baseline
        baseline["actions"].append({
            "action": action,
            "timestamp": datetime.utcnow(),
            "context": context
        })
        baseline["typical_hours"].add(current_hour)
        if current_ip:
            baseline["typical_ips"].add(current_ip)
        baseline["last_activity"] = datetime.utcnow()
        
        # Keep only recent actions (last 30 days)
        cutoff = datetime.utcnow() - timedelta(days=30)
        baseline["actions"] = [
            a for a in baseline["actions"] 
            if a["timestamp"] > cutoff
        ]
        
        return min(1.0, anomaly_score)
        
    def analyze_session_pattern(self, session_id: str, events: List[Dict[str, Any]]) -> float:
        """Analyze session pattern for anomalies"""
        if not events:
            return 0.0
            
        anomaly_score = 0.0
        
        # Check for rapid-fire requests
        timestamps = [e.get("timestamp") for e in events if e.get("timestamp")]
        if len(timestamps) >= 2:
            intervals = []
            for i in range(1, len(timestamps)):
                interval = (timestamps[i] - timestamps[i-1]).total_seconds()
                intervals.append(interval)
                
            avg_interval = sum(intervals) / len(intervals)
            if avg_interval < 0.1:  # Less than 100ms between requests
                anomaly_score += 0.6
                
        # Check for unusual request patterns
        actions = [e.get("action") for e in events]
        unique_actions = set(actions)
        
        if len(unique_actions) == 1 and len(actions) > 10:  # Repetitive actions
            anomaly_score += 0.4
            
        return min(1.0, anomaly_score)


class ThreatIntelligence:
    """
    Threat intelligence and reputation system
    """
    
    def __init__(self):
        self.malicious_ips = set()
        self.suspicious_patterns = []
        self.reputation_cache = {}
        
    async def check_ip_reputation(self, ip: str) -> Dict[str, Any]:
        """Check IP reputation"""
        if ip in self.reputation_cache:
            cached = self.reputation_cache[ip]
            if datetime.utcnow() - cached["timestamp"] < timedelta(hours=1):
                return cached["data"]
                
        # Basic reputation check
        reputation = {
            "is_malicious": ip in self.malicious_ips,
            "is_tor": False,  # Would integrate with Tor exit node list
            "is_vpn": False,  # Would integrate with VPN detection service
            "country": "unknown",  # Would integrate with GeoIP service
            "asn": "unknown",
            "risk_score": 0.0
        }
        
        # Calculate risk score
        if reputation["is_malicious"]:
            reputation["risk_score"] += 0.8
        if reputation["is_tor"]:
            reputation["risk_score"] += 0.3
        if reputation["is_vpn"]:
            reputation["risk_score"] += 0.2
            
        # Cache result
        self.reputation_cache[ip] = {
            "data": reputation,
            "timestamp": datetime.utcnow()
        }
        
        return reputation
        
    def add_malicious_ip(self, ip: str, reason: str):
        """Add IP to malicious list"""
        self.malicious_ips.add(ip)
        logger.warning(f"Added malicious IP {ip}: {reason}")
        
    def check_payload_threats(self, payload: str) -> List[str]:
        """Check payload for threat indicators"""
        threats = []
        
        # SQL injection patterns
        sql_patterns = [
            r"union\s+select",
            r"drop\s+table",
            r"insert\s+into",
            r"delete\s+from",
            r"update\s+.*\s+set",
            r"exec\s*\(",
            r"script\s*:",
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, payload, re.IGNORECASE):
                threats.append(f"SQL injection pattern: {pattern}")
                
        # XSS patterns
        xss_patterns = [
            r"<script",
            r"javascript:",
            r"onload\s*=",
            r"onerror\s*=",
            r"eval\s*\(",
        ]
        
        for pattern in xss_patterns:
            if re.search(pattern, payload, re.IGNORECASE):
                threats.append(f"XSS pattern: {pattern}")
                
        # Command injection patterns
        cmd_patterns = [
            r";\s*rm\s+",
            r";\s*cat\s+",
            r";\s*ls\s+",
            r"\|\s*nc\s+",
            r"&&\s*curl",
        ]
        
        for pattern in cmd_patterns:
            if re.search(pattern, payload, re.IGNORECASE):
                threats.append(f"Command injection pattern: {pattern}")
                
        return threats


class ZeroTrustEngine:
    """
    Main zero trust security engine
    """
    
    def __init__(self):
        self.device_fingerprinting = DeviceFingerprinting()
        self.behavior_analyzer = BehaviorAnalyzer()
        self.threat_intelligence = ThreatIntelligence()
        self.active_threats = {}
        self.security_policies = {}
        
    async def evaluate_request(
        self, 
        user_id: Optional[str],
        session_id: Optional[str],
        ip_address: str,
        headers: Dict[str, str],
        payload: Optional[str] = None,
        action: str = "unknown"
    ) -> SecurityContext:
        """Evaluate request and generate security context"""
        
        # Generate device fingerprint
        device_fingerprint = self.device_fingerprinting.generate_fingerprint(headers, ip_address)
        
        # Check IP reputation
        ip_reputation = await self.threat_intelligence.check_ip_reputation(ip_address)
        
        # Analyze behavior
        behavior_anomaly = 0.0
        if user_id:
            behavior_anomaly = self.behavior_analyzer.analyze_user_behavior(
                user_id, action, {"ip_address": ip_address}
            )
            
        # Check for suspicious device
        is_suspicious_device = self.device_fingerprinting.is_suspicious_device(
            device_fingerprint, headers
        )
        
        # Check payload threats
        payload_threats = []
        if payload:
            payload_threats = self.threat_intelligence.check_payload_threats(payload)
            
        # Calculate trust score
        trust_score = 1.0
        risk_factors = []
        
        # IP reputation factors
        trust_score -= ip_reputation["risk_score"] * 0.4
        if ip_reputation["is_malicious"]:
            risk_factors.append("malicious_ip")
        if ip_reputation["is_tor"]:
            risk_factors.append("tor_exit_node")
        if ip_reputation["is_vpn"]:
            risk_factors.append("vpn_connection")
            
        # Device factors
        if is_suspicious_device:
            trust_score -= 0.3
            risk_factors.append("suspicious_device")
            
        # Behavioral factors
        trust_score -= behavior_anomaly * 0.3
        if behavior_anomaly > 0.5:
            risk_factors.append("anomalous_behavior")
            
        # Payload factors
        if payload_threats:
            trust_score -= 0.5
            risk_factors.extend(payload_threats)
            
        trust_score = max(0.0, trust_score)
        
        return SecurityContext(
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=headers.get("user-agent", ""),
            timestamp=datetime.utcnow(),
            trust_score=trust_score,
            risk_factors=risk_factors,
            authentication_method="unknown",
            device_fingerprint=device_fingerprint
        )
        
    async def detect_threats(self, context: SecurityContext) -> List[ThreatDetection]:
        """Detect threats based on security context"""
        threats = []
        
        # Low trust score threat
        if context.trust_score < 0.3:
            threats.append(ThreatDetection(
                threat_id=f"low_trust_{int(time.time())}",
                threat_type="low_trust_score",
                threat_level=ThreatLevel.HIGH,
                confidence=1.0 - context.trust_score,
                description=f"Low trust score: {context.trust_score:.2f}",
                indicators=context.risk_factors,
                recommended_action=SecurityAction.CHALLENGE,
                context=context
            ))
            
        # Multiple risk factors
        if len(context.risk_factors) >= 3:
            threats.append(ThreatDetection(
                threat_id=f"multiple_risks_{int(time.time())}",
                threat_type="multiple_risk_factors",
                threat_level=ThreatLevel.MEDIUM,
                confidence=min(1.0, len(context.risk_factors) * 0.2),
                description=f"Multiple risk factors detected: {', '.join(context.risk_factors)}",
                indicators=context.risk_factors,
                recommended_action=SecurityAction.CHALLENGE,
                context=context
            ))
            
        # Malicious patterns
        malicious_patterns = [r for r in context.risk_factors if "injection" in r or "xss" in r]
        if malicious_patterns:
            threats.append(ThreatDetection(
                threat_id=f"malicious_payload_{int(time.time())}",
                threat_type="malicious_payload",
                threat_level=ThreatLevel.CRITICAL,
                confidence=1.0,
                description="Malicious payload patterns detected",
                indicators=malicious_patterns,
                recommended_action=SecurityAction.BLOCK,
                context=context
            ))
            
        return threats
        
    async def enforce_policy(self, threats: List[ThreatDetection]) -> SecurityAction:
        """Enforce security policy based on threats"""
        if not threats:
            return SecurityAction.ALLOW
            
        # Find highest threat level
        max_threat_level = max(threat.threat_level for threat in threats)
        
        if max_threat_level == ThreatLevel.CRITICAL:
            return SecurityAction.BLOCK
        elif max_threat_level == ThreatLevel.HIGH:
            return SecurityAction.CHALLENGE
        elif max_threat_level == ThreatLevel.MEDIUM:
            return SecurityAction.CHALLENGE
        else:
            return SecurityAction.ALLOW
            
    def get_security_metrics(self) -> Dict[str, Any]:
        """Get security metrics"""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "known_devices": len(self.device_fingerprinting.known_devices),
            "malicious_ips": len(self.threat_intelligence.malicious_ips),
            "active_threats": len(self.active_threats),
            "user_baselines": len(self.behavior_analyzer.user_baselines),
            "reputation_cache_size": len(self.threat_intelligence.reputation_cache)
        }


# Global zero trust engine
zero_trust_engine = ZeroTrustEngine()
