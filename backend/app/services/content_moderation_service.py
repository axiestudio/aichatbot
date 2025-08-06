"""
Advanced Content Moderation & AI Safety Service
Real-time content filtering, toxicity detection, and AI safety measures
"""

import asyncio
import logging
import re
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass
from enum import Enum
import hashlib

from .cache_service import cache_service
from .security_intelligence_service import security_intelligence_service
from ..core.config import settings

logger = logging.getLogger(__name__)


class ModerationAction(Enum):
    ALLOW = "allow"
    FLAG = "flag"
    BLOCK = "block"
    QUARANTINE = "quarantine"
    ESCALATE = "escalate"


class ToxicityLevel(Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    SEVERE = "severe"


class ContentCategory(Enum):
    SAFE = "safe"
    SPAM = "spam"
    HARASSMENT = "harassment"
    HATE_SPEECH = "hate_speech"
    VIOLENCE = "violence"
    SEXUAL_CONTENT = "sexual_content"
    SELF_HARM = "self_harm"
    ILLEGAL_ACTIVITY = "illegal_activity"
    MISINFORMATION = "misinformation"
    PERSONAL_INFO = "personal_info"
    MALWARE = "malware"


@dataclass
class ModerationResult:
    content_id: str
    content: str
    action: ModerationAction
    toxicity_level: ToxicityLevel
    categories: List[ContentCategory]
    confidence: float
    reasoning: str
    flagged_terms: List[str]
    ai_safety_score: float
    timestamp: datetime
    metadata: Dict[str, Any]


class ContentModerationService:
    """Advanced AI-powered content moderation and safety service"""
    
    def __init__(self):
        self.moderation_results = deque(maxlen=50000)
        self.user_violation_history = defaultdict(list)
        self.content_patterns = defaultdict(int)
        self.false_positive_feedback = deque(maxlen=1000)
        
        # Toxicity detection patterns
        self.toxicity_patterns = {
            ToxicityLevel.SEVERE: [
                r"\b(kill yourself|kys|die|suicide)\b",
                r"\b(terrorist|bomb|attack|murder)\b",
                r"\b(rape|molest|abuse)\b"
            ],
            ToxicityLevel.HIGH: [
                r"\b(hate|stupid|idiot|moron|retard)\b",
                r"\b(fuck|shit|damn|bitch|asshole)\b",
                r"\b(racist|nazi|fascist)\b"
            ],
            ToxicityLevel.MEDIUM: [
                r"\b(annoying|pathetic|loser|worthless)\b",
                r"\b(shut up|go away|get lost)\b"
            ],
            ToxicityLevel.LOW: [
                r"\b(weird|strange|odd|dumb)\b"
            ]
        }
        
        # Content category patterns
        self.category_patterns = {
            ContentCategory.SPAM: [
                r"(click here|buy now|limited time|act now)",
                r"(free money|get rich|make \$\d+)",
                r"(viagra|cialis|pharmacy|pills)",
                r"(lottery|winner|congratulations|prize)"
            ],
            ContentCategory.HARASSMENT: [
                r"(stalking|following|watching you)",
                r"(threatening|intimidating|scary)",
                r"(personal attack|targeting|bullying)"
            ],
            ContentCategory.HATE_SPEECH: [
                r"(racial slur|ethnic slur|religious hate)",
                r"(supremacist|extremist|radical)",
                r"(discrimination|prejudice|bigotry)"
            ],
            ContentCategory.VIOLENCE: [
                r"(violence|violent|fight|attack)",
                r"(weapon|gun|knife|bomb)",
                r"(hurt|harm|damage|destroy)"
            ],
            ContentCategory.SEXUAL_CONTENT: [
                r"(sexual|explicit|adult content)",
                r"(pornography|nude|naked)",
                r"(inappropriate|suggestive)"
            ],
            ContentCategory.PERSONAL_INFO: [
                r"(\d{3}-\d{2}-\d{4})",  # SSN pattern
                r"(\d{4}\s?\d{4}\s?\d{4}\s?\d{4})",  # Credit card pattern
                r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})",  # Email pattern
                r"(\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9})"  # Phone pattern
            ],
            ContentCategory.MISINFORMATION: [
                r"(fake news|conspiracy|hoax)",
                r"(covid.*fake|vaccine.*dangerous)",
                r"(election.*stolen|fraud.*voting)"
            ]
        }
        
        # AI safety patterns
        self.ai_safety_patterns = [
            r"(jailbreak|ignore.*instructions|bypass.*safety)",
            r"(pretend.*you.*are|roleplay.*as)",
            r"(system.*prompt|developer.*mode)",
            r"(override.*safety|disable.*filter)"
        ]
        
        # Allowed domains for links
        self.allowed_domains = {
            "youtube.com", "youtu.be", "github.com", "stackoverflow.com",
            "wikipedia.org", "google.com", "microsoft.com", "apple.com"
        }
        
        # Moderation thresholds
        self.thresholds = {
            "toxicity_block": 0.8,
            "toxicity_flag": 0.6,
            "ai_safety_block": 0.7,
            "personal_info_block": 0.9,
            "spam_block": 0.75
        }
    
    async def start_moderation_service(self):
        """Start content moderation service"""
        logger.info("🛡️ Content Moderation Service started")
        asyncio.create_task(self._moderation_monitoring_loop())
        asyncio.create_task(self._pattern_learning_loop())
        asyncio.create_task(self._violation_tracking_loop())
    
    async def moderate_content(self, content: str, user_id: str = None, context: Dict[str, Any] = None) -> ModerationResult:
        """Moderate content using AI-powered analysis"""
        try:
            content_id = hashlib.md5(f"{content}{user_id}{datetime.utcnow()}".encode()).hexdigest()
            
            # Analyze toxicity
            toxicity_level, toxicity_confidence = self._analyze_toxicity(content)
            
            # Categorize content
            categories = self._categorize_content(content)
            
            # Check AI safety
            ai_safety_score = self._check_ai_safety(content)
            
            # Detect flagged terms
            flagged_terms = self._detect_flagged_terms(content)
            
            # Calculate overall confidence
            confidence = self._calculate_confidence(toxicity_confidence, categories, ai_safety_score)
            
            # Determine action
            action = self._determine_action(toxicity_level, categories, ai_safety_score, user_id)
            
            # Generate reasoning
            reasoning = self._generate_reasoning(toxicity_level, categories, ai_safety_score, flagged_terms)
            
            result = ModerationResult(
                content_id=content_id,
                content=content[:500],  # Store first 500 chars for analysis
                action=action,
                toxicity_level=toxicity_level,
                categories=categories,
                confidence=confidence,
                reasoning=reasoning,
                flagged_terms=flagged_terms,
                ai_safety_score=ai_safety_score,
                timestamp=datetime.utcnow(),
                metadata={
                    "user_id": user_id,
                    "context": context or {},
                    "content_length": len(content)
                }
            )
            
            # Store result
            self.moderation_results.append(result)
            
            # Update user violation history if blocked
            if action in [ModerationAction.BLOCK, ModerationAction.QUARANTINE] and user_id:
                await self._update_violation_history(user_id, result)
            
            # Cache result
            await cache_service.set(
                f"moderation_{content_id}",
                {
                    "action": action.value,
                    "toxicity_level": toxicity_level.value,
                    "categories": [cat.value for cat in categories],
                    "confidence": confidence,
                    "ai_safety_score": ai_safety_score
                },
                "moderation",
                3600
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error moderating content: {e}")
            # Return safe default
            return ModerationResult(
                content_id="error",
                content="",
                action=ModerationAction.ALLOW,
                toxicity_level=ToxicityLevel.NONE,
                categories=[ContentCategory.SAFE],
                confidence=0.0,
                reasoning="Error in moderation",
                flagged_terms=[],
                ai_safety_score=1.0,
                timestamp=datetime.utcnow(),
                metadata={"error": str(e)}
            )
    
    def _analyze_toxicity(self, content: str) -> Tuple[ToxicityLevel, float]:
        """Analyze content toxicity level"""
        content_lower = content.lower()
        max_toxicity = ToxicityLevel.NONE
        max_confidence = 0.0
        
        for level, patterns in self.toxicity_patterns.items():
            matches = 0
            for pattern in patterns:
                if re.search(pattern, content_lower):
                    matches += 1
            
            if matches > 0:
                confidence = min(1.0, matches * 0.3)
                if level.value > max_toxicity.value or confidence > max_confidence:
                    max_toxicity = level
                    max_confidence = confidence
        
        return max_toxicity, max_confidence
    
    def _categorize_content(self, content: str) -> List[ContentCategory]:
        """Categorize content into safety categories"""
        content_lower = content.lower()
        categories = []
        
        for category, patterns in self.category_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content_lower):
                    categories.append(category)
                    break
        
        # Check for suspicious links
        if self._contains_suspicious_links(content):
            categories.append(ContentCategory.SPAM)
        
        # Default to safe if no categories found
        if not categories:
            categories.append(ContentCategory.SAFE)
        
        return categories
    
    def _check_ai_safety(self, content: str) -> float:
        """Check for AI safety violations (prompt injection, jailbreaking)"""
        content_lower = content.lower()
        safety_score = 1.0  # Start with safe
        
        for pattern in self.ai_safety_patterns:
            if re.search(pattern, content_lower):
                safety_score -= 0.3
        
        # Check for instruction-like patterns
        instruction_patterns = [
            r"(ignore|forget|disregard).*previous",
            r"new.*instructions?",
            r"system.*message",
            r"developer.*override"
        ]
        
        for pattern in instruction_patterns:
            if re.search(pattern, content_lower):
                safety_score -= 0.2
        
        return max(0.0, safety_score)
    
    def _detect_flagged_terms(self, content: str) -> List[str]:
        """Detect specific flagged terms"""
        flagged_terms = []
        content_lower = content.lower()
        
        # Combine all patterns
        all_patterns = []
        for patterns in self.toxicity_patterns.values():
            all_patterns.extend(patterns)
        for patterns in self.category_patterns.values():
            all_patterns.extend(patterns)
        
        for pattern in all_patterns:
            matches = re.findall(pattern, content_lower)
            flagged_terms.extend(matches)
        
        return list(set(flagged_terms))  # Remove duplicates
    
    def _contains_suspicious_links(self, content: str) -> bool:
        """Check for suspicious links"""
        # Simple URL detection
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, content)
        
        for url in urls:
            # Extract domain
            domain_match = re.search(r'://([^/]+)', url)
            if domain_match:
                domain = domain_match.group(1).lower()
                if domain not in self.allowed_domains:
                    return True
        
        return False
    
    def _calculate_confidence(self, toxicity_confidence: float, categories: List[ContentCategory], ai_safety_score: float) -> float:
        """Calculate overall confidence in moderation decision"""
        confidence = 0.5  # Base confidence
        
        # Toxicity confidence
        confidence += toxicity_confidence * 0.3
        
        # Category confidence
        if ContentCategory.SAFE not in categories:
            confidence += 0.2
        
        # AI safety confidence
        if ai_safety_score < 0.8:
            confidence += (1.0 - ai_safety_score) * 0.3
        
        return min(1.0, confidence)
    
    def _determine_action(self, toxicity_level: ToxicityLevel, categories: List[ContentCategory], ai_safety_score: float, user_id: str = None) -> ModerationAction:
        """Determine moderation action"""
        
        # Check AI safety first
        if ai_safety_score < self.thresholds["ai_safety_block"]:
            return ModerationAction.BLOCK
        
        # Check severe toxicity
        if toxicity_level == ToxicityLevel.SEVERE:
            return ModerationAction.BLOCK
        
        # Check high-risk categories
        high_risk_categories = [
            ContentCategory.HATE_SPEECH,
            ContentCategory.VIOLENCE,
            ContentCategory.ILLEGAL_ACTIVITY,
            ContentCategory.SELF_HARM
        ]
        
        if any(cat in categories for cat in high_risk_categories):
            return ModerationAction.BLOCK
        
        # Check personal info
        if ContentCategory.PERSONAL_INFO in categories:
            return ModerationAction.BLOCK
        
        # Check spam
        if ContentCategory.SPAM in categories:
            return ModerationAction.FLAG
        
        # Check medium toxicity
        if toxicity_level in [ToxicityLevel.HIGH, ToxicityLevel.MEDIUM]:
            return ModerationAction.FLAG
        
        # Check user violation history
        if user_id and self._check_user_violation_history(user_id):
            return ModerationAction.QUARANTINE
        
        return ModerationAction.ALLOW
    
    def _generate_reasoning(self, toxicity_level: ToxicityLevel, categories: List[ContentCategory], ai_safety_score: float, flagged_terms: List[str]) -> str:
        """Generate human-readable reasoning for moderation decision"""
        reasons = []
        
        if toxicity_level != ToxicityLevel.NONE:
            reasons.append(f"Toxicity level: {toxicity_level.value}")
        
        if ContentCategory.SAFE not in categories:
            category_names = [cat.value.replace("_", " ") for cat in categories]
            reasons.append(f"Categories: {', '.join(category_names)}")
        
        if ai_safety_score < 0.8:
            reasons.append(f"AI safety concern (score: {ai_safety_score:.2f})")
        
        if flagged_terms:
            reasons.append(f"Flagged terms detected: {len(flagged_terms)}")
        
        if not reasons:
            return "Content appears safe"
        
        return "; ".join(reasons)
    
    def _check_user_violation_history(self, user_id: str) -> bool:
        """Check if user has recent violations"""
        violations = self.user_violation_history.get(user_id, [])
        recent_violations = [
            v for v in violations 
            if v["timestamp"] > datetime.utcnow() - timedelta(hours=24)
        ]
        return len(recent_violations) >= 3  # 3 violations in 24 hours
    
    async def _update_violation_history(self, user_id: str, result: ModerationResult):
        """Update user violation history"""
        try:
            violation = {
                "content_id": result.content_id,
                "action": result.action.value,
                "toxicity_level": result.toxicity_level.value,
                "categories": [cat.value for cat in result.categories],
                "timestamp": result.timestamp
            }
            
            self.user_violation_history[user_id].append(violation)
            
            # Keep only last 50 violations per user
            if len(self.user_violation_history[user_id]) > 50:
                self.user_violation_history[user_id] = self.user_violation_history[user_id][-50:]
            
        except Exception as e:
            logger.error(f"Error updating violation history: {e}")
    
    async def report_false_positive(self, content_id: str, user_feedback: str):
        """Report false positive for model improvement"""
        try:
            feedback = {
                "content_id": content_id,
                "user_feedback": user_feedback,
                "timestamp": datetime.utcnow().isoformat(),
                "reported_by": "user"
            }
            
            self.false_positive_feedback.append(feedback)
            
            # Cache feedback
            await cache_service.set(
                f"false_positive_{content_id}",
                feedback,
                "moderation",
                86400  # 24 hours
            )
            
        except Exception as e:
            logger.error(f"Error reporting false positive: {e}")
    
    async def get_moderation_stats(self, timeframe_hours: int = 24) -> Dict[str, Any]:
        """Get moderation statistics"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=timeframe_hours)
            recent_results = [
                result for result in self.moderation_results 
                if result.timestamp > cutoff_time
            ]
            
            if not recent_results:
                return {"message": "No moderation data available"}
            
            # Calculate statistics
            total_content = len(recent_results)
            actions = defaultdict(int)
            toxicity_levels = defaultdict(int)
            categories = defaultdict(int)
            
            for result in recent_results:
                actions[result.action.value] += 1
                toxicity_levels[result.toxicity_level.value] += 1
                for category in result.categories:
                    categories[category.value] += 1
            
            avg_confidence = sum(r.confidence for r in recent_results) / total_content
            avg_ai_safety = sum(r.ai_safety_score for r in recent_results) / total_content
            
            return {
                "timeframe_hours": timeframe_hours,
                "total_content_moderated": total_content,
                "action_distribution": dict(actions),
                "toxicity_distribution": dict(toxicity_levels),
                "category_distribution": dict(categories),
                "average_confidence": round(avg_confidence, 3),
                "average_ai_safety_score": round(avg_ai_safety, 3),
                "block_rate": round((actions["block"] / total_content) * 100, 2),
                "flag_rate": round((actions["flag"] / total_content) * 100, 2),
                "false_positives_reported": len(self.false_positive_feedback),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting moderation stats: {e}")
            return {"error": str(e)}
    
    async def _moderation_monitoring_loop(self):
        """Main moderation monitoring loop"""
        while True:
            try:
                await self._monitor_moderation_health()
                await asyncio.sleep(300)  # Run every 5 minutes
            except Exception as e:
                logger.error(f"Moderation monitoring error: {e}")
                await asyncio.sleep(600)
    
    async def _pattern_learning_loop(self):
        """Pattern learning and model improvement loop"""
        while True:
            try:
                await self._update_moderation_patterns()
                await asyncio.sleep(3600)  # Run every hour
            except Exception as e:
                logger.error(f"Pattern learning error: {e}")
                await asyncio.sleep(1800)
    
    async def _violation_tracking_loop(self):
        """User violation tracking loop"""
        while True:
            try:
                await self._analyze_violation_patterns()
                await asyncio.sleep(1800)  # Run every 30 minutes
            except Exception as e:
                logger.error(f"Violation tracking error: {e}")
                await asyncio.sleep(900)
    
    async def _monitor_moderation_health(self):
        """Monitor moderation service health"""
        # Implementation would monitor service health
        pass
    
    async def _update_moderation_patterns(self):
        """Update moderation patterns based on feedback"""
        # Implementation would update ML patterns
        pass
    
    async def _analyze_violation_patterns(self):
        """Analyze user violation patterns"""
        # Implementation would analyze violation patterns
        pass


# Global content moderation service instance
content_moderation_service = ContentModerationService()
