"""
Advanced Conversation Intelligence Service
AI-powered conversation analysis, sentiment tracking, and user intent recognition
"""

import asyncio
import logging
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass
from enum import Enum
import numpy as np

from .cache_service import cache_service
from ..core.database import get_db
from ..models.database import ChatMessage, ChatSession

logger = logging.getLogger(__name__)


class SentimentType(Enum):
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"


class IntentType(Enum):
    QUESTION = "question"
    COMPLAINT = "complaint"
    COMPLIMENT = "compliment"
    REQUEST = "request"
    INFORMATION = "information"
    SUPPORT = "support"
    FEEDBACK = "feedback"
    GREETING = "greeting"
    GOODBYE = "goodbye"
    UNKNOWN = "unknown"


@dataclass
class ConversationInsight:
    session_id: str
    message_id: str
    sentiment: SentimentType
    intent: IntentType
    confidence: float
    emotions: Dict[str, float]
    topics: List[str]
    urgency_score: float
    satisfaction_score: float
    complexity_score: float
    timestamp: datetime


class ConversationIntelligenceService:
    """Advanced AI-powered conversation analysis and intelligence"""
    
    def __init__(self):
        self.insights_cache = deque(maxlen=10000)
        self.conversation_patterns = defaultdict(list)
        self.user_profiles = defaultdict(dict)
        
        # Sentiment analysis patterns
        self.sentiment_patterns = {
            SentimentType.VERY_POSITIVE: [
                r"\b(amazing|excellent|fantastic|wonderful|perfect|love|brilliant|outstanding)\b",
                r"\b(thank you so much|really helpful|exactly what|solved my problem)\b"
            ],
            SentimentType.POSITIVE: [
                r"\b(good|great|nice|helpful|thanks|appreciate|useful|works)\b",
                r"\b(thank you|that helps|makes sense|got it)\b"
            ],
            SentimentType.NEGATIVE: [
                r"\b(bad|wrong|error|problem|issue|difficult|confused|frustrated)\b",
                r"\b(doesn't work|not working|can't|unable|failed)\b"
            ],
            SentimentType.VERY_NEGATIVE: [
                r"\b(terrible|awful|horrible|hate|worst|useless|broken|disaster)\b",
                r"\b(completely broken|total failure|waste of time|doesn't work at all)\b"
            ]
        }
        
        # Intent recognition patterns
        self.intent_patterns = {
            IntentType.QUESTION: [
                r"^(what|how|when|where|why|who|which|can you|could you|would you)",
                r"\?$",
                r"\b(explain|tell me|show me|help me understand)\b"
            ],
            IntentType.COMPLAINT: [
                r"\b(complaint|complain|problem|issue|bug|error|wrong|broken)\b",
                r"\b(not working|doesn't work|failed|can't)\b"
            ],
            IntentType.COMPLIMENT: [
                r"\b(great job|well done|excellent|amazing|fantastic|love it)\b",
                r"\b(thank you|thanks|appreciate|helpful)\b"
            ],
            IntentType.REQUEST: [
                r"\b(please|can you|could you|would you|I need|I want|I would like)\b",
                r"\b(help me|assist me|show me|guide me)\b"
            ],
            IntentType.GREETING: [
                r"^(hi|hello|hey|good morning|good afternoon|good evening)",
                r"\b(how are you|nice to meet)\b"
            ],
            IntentType.GOODBYE: [
                r"\b(bye|goodbye|see you|talk later|thanks again|that's all)\b",
                r"\b(have a good|take care|until next time)\b"
            ]
        }
        
        # Emotion detection patterns
        self.emotion_patterns = {
            "joy": [r"\b(happy|joy|excited|thrilled|delighted|pleased)\b"],
            "anger": [r"\b(angry|mad|furious|annoyed|irritated|frustrated)\b"],
            "fear": [r"\b(scared|afraid|worried|anxious|concerned|nervous)\b"],
            "sadness": [r"\b(sad|disappointed|upset|depressed|down)\b"],
            "surprise": [r"\b(surprised|shocked|amazed|astonished|wow)\b"],
            "trust": [r"\b(trust|confident|reliable|dependable|sure)\b"],
            "anticipation": [r"\b(excited|looking forward|can't wait|eager)\b"],
            "disgust": [r"\b(disgusted|gross|awful|terrible|horrible)\b"]
        }
        
        # Topic extraction keywords
        self.topic_keywords = {
            "technical_support": ["error", "bug", "issue", "problem", "fix", "troubleshoot"],
            "billing": ["payment", "bill", "charge", "cost", "price", "refund"],
            "account": ["login", "password", "account", "profile", "settings"],
            "features": ["feature", "function", "capability", "option", "setting"],
            "performance": ["slow", "fast", "speed", "performance", "lag", "delay"],
            "integration": ["api", "integration", "connect", "sync", "import", "export"],
            "security": ["security", "privacy", "safe", "protect", "encrypt", "secure"],
            "training": ["learn", "tutorial", "guide", "help", "documentation", "how-to"]
        }
    
    async def start_conversation_intelligence(self):
        """Start conversation intelligence monitoring"""
        logger.info("🧠 Conversation Intelligence Service started")
        asyncio.create_task(self._conversation_analysis_loop())
        asyncio.create_task(self._pattern_learning_loop())
        asyncio.create_task(self._user_profiling_loop())
    
    async def analyze_message(self, message: str, session_id: str, message_id: str, role: str) -> ConversationInsight:
        """Analyze a single message for sentiment, intent, and other insights"""
        try:
            if role != "user":  # Only analyze user messages
                return None
            
            # Sentiment analysis
            sentiment = self._analyze_sentiment(message)
            
            # Intent recognition
            intent = self._recognize_intent(message)
            
            # Emotion detection
            emotions = self._detect_emotions(message)
            
            # Topic extraction
            topics = self._extract_topics(message)
            
            # Calculate scores
            urgency_score = self._calculate_urgency_score(message, sentiment, intent)
            satisfaction_score = self._calculate_satisfaction_score(message, sentiment)
            complexity_score = self._calculate_complexity_score(message)
            
            # Calculate confidence
            confidence = self._calculate_confidence(sentiment, intent, emotions)
            
            insight = ConversationInsight(
                session_id=session_id,
                message_id=message_id,
                sentiment=sentiment,
                intent=intent,
                confidence=confidence,
                emotions=emotions,
                topics=topics,
                urgency_score=urgency_score,
                satisfaction_score=satisfaction_score,
                complexity_score=complexity_score,
                timestamp=datetime.utcnow()
            )
            
            # Store insight
            self.insights_cache.append(insight)
            
            # Update conversation patterns
            await self._update_conversation_patterns(session_id, insight)
            
            # Update user profile
            await self._update_user_profile(session_id, insight)
            
            # Cache insight
            await cache_service.set(
                f"conversation_insight_{message_id}",
                {
                    "sentiment": sentiment.value,
                    "intent": intent.value,
                    "confidence": confidence,
                    "emotions": emotions,
                    "topics": topics,
                    "urgency_score": urgency_score,
                    "satisfaction_score": satisfaction_score,
                    "complexity_score": complexity_score
                },
                "conversation",
                3600
            )
            
            return insight
            
        except Exception as e:
            logger.error(f"Error analyzing message: {e}")
            return None
    
    def _analyze_sentiment(self, message: str) -> SentimentType:
        """Analyze sentiment of message"""
        message_lower = message.lower()
        
        # Check for very positive
        for pattern in self.sentiment_patterns[SentimentType.VERY_POSITIVE]:
            if re.search(pattern, message_lower):
                return SentimentType.VERY_POSITIVE
        
        # Check for very negative
        for pattern in self.sentiment_patterns[SentimentType.VERY_NEGATIVE]:
            if re.search(pattern, message_lower):
                return SentimentType.VERY_NEGATIVE
        
        # Check for positive
        positive_count = 0
        for pattern in self.sentiment_patterns[SentimentType.POSITIVE]:
            if re.search(pattern, message_lower):
                positive_count += 1
        
        # Check for negative
        negative_count = 0
        for pattern in self.sentiment_patterns[SentimentType.NEGATIVE]:
            if re.search(pattern, message_lower):
                negative_count += 1
        
        if positive_count > negative_count:
            return SentimentType.POSITIVE
        elif negative_count > positive_count:
            return SentimentType.NEGATIVE
        else:
            return SentimentType.NEUTRAL
    
    def _recognize_intent(self, message: str) -> IntentType:
        """Recognize intent of message"""
        message_lower = message.lower().strip()
        
        # Check each intent pattern
        for intent_type, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    return intent_type
        
        return IntentType.UNKNOWN
    
    def _detect_emotions(self, message: str) -> Dict[str, float]:
        """Detect emotions in message"""
        message_lower = message.lower()
        emotions = {}
        
        for emotion, patterns in self.emotion_patterns.items():
            score = 0.0
            for pattern in patterns:
                matches = len(re.findall(pattern, message_lower))
                score += matches * 0.3  # Each match adds 0.3 to emotion score
            
            emotions[emotion] = min(1.0, score)  # Cap at 1.0
        
        return emotions
    
    def _extract_topics(self, message: str) -> List[str]:
        """Extract topics from message"""
        message_lower = message.lower()
        topics = []
        
        for topic, keywords in self.topic_keywords.items():
            for keyword in keywords:
                if keyword in message_lower:
                    topics.append(topic)
                    break
        
        return topics
    
    def _calculate_urgency_score(self, message: str, sentiment: SentimentType, intent: IntentType) -> float:
        """Calculate urgency score (0-1)"""
        score = 0.0
        message_lower = message.lower()
        
        # Sentiment contribution
        if sentiment == SentimentType.VERY_NEGATIVE:
            score += 0.4
        elif sentiment == SentimentType.NEGATIVE:
            score += 0.2
        
        # Intent contribution
        if intent == IntentType.COMPLAINT:
            score += 0.3
        elif intent == IntentType.REQUEST:
            score += 0.1
        
        # Urgency keywords
        urgency_keywords = ["urgent", "asap", "immediately", "emergency", "critical", "broken", "down"]
        for keyword in urgency_keywords:
            if keyword in message_lower:
                score += 0.2
                break
        
        # Exclamation marks
        exclamation_count = message.count("!")
        score += min(0.2, exclamation_count * 0.05)
        
        return min(1.0, score)
    
    def _calculate_satisfaction_score(self, message: str, sentiment: SentimentType) -> float:
        """Calculate satisfaction score (0-1)"""
        if sentiment == SentimentType.VERY_POSITIVE:
            return 1.0
        elif sentiment == SentimentType.POSITIVE:
            return 0.8
        elif sentiment == SentimentType.NEUTRAL:
            return 0.5
        elif sentiment == SentimentType.NEGATIVE:
            return 0.2
        else:  # VERY_NEGATIVE
            return 0.0
    
    def _calculate_complexity_score(self, message: str) -> float:
        """Calculate complexity score (0-1)"""
        # Length factor
        length_score = min(0.4, len(message) / 500)
        
        # Technical terms
        technical_terms = ["api", "integration", "database", "server", "configuration", "authentication"]
        tech_score = 0.0
        for term in technical_terms:
            if term in message.lower():
                tech_score += 0.1
        
        # Question complexity
        question_words = ["how", "why", "what", "when", "where", "which"]
        question_score = 0.0
        for word in question_words:
            if word in message.lower():
                question_score += 0.05
        
        return min(1.0, length_score + tech_score + question_score)
    
    def _calculate_confidence(self, sentiment: SentimentType, intent: IntentType, emotions: Dict[str, float]) -> float:
        """Calculate confidence in analysis"""
        confidence = 0.5  # Base confidence
        
        # Sentiment confidence
        if sentiment != SentimentType.NEUTRAL:
            confidence += 0.2
        
        # Intent confidence
        if intent != IntentType.UNKNOWN:
            confidence += 0.2
        
        # Emotion confidence
        max_emotion = max(emotions.values()) if emotions else 0
        confidence += max_emotion * 0.1
        
        return min(1.0, confidence)
    
    async def _update_conversation_patterns(self, session_id: str, insight: ConversationInsight):
        """Update conversation patterns for session"""
        try:
            patterns = self.conversation_patterns[session_id]
            patterns.append({
                "sentiment": insight.sentiment.value,
                "intent": insight.intent.value,
                "urgency": insight.urgency_score,
                "satisfaction": insight.satisfaction_score,
                "timestamp": insight.timestamp.isoformat()
            })
            
            # Keep only last 50 patterns per session
            if len(patterns) > 50:
                patterns.pop(0)
                
        except Exception as e:
            logger.error(f"Error updating conversation patterns: {e}")
    
    async def _update_user_profile(self, session_id: str, insight: ConversationInsight):
        """Update user profile based on insights"""
        try:
            profile = self.user_profiles[session_id]
            
            # Update sentiment history
            if "sentiment_history" not in profile:
                profile["sentiment_history"] = []
            profile["sentiment_history"].append(insight.sentiment.value)
            
            # Update intent history
            if "intent_history" not in profile:
                profile["intent_history"] = []
            profile["intent_history"].append(insight.intent.value)
            
            # Update average scores
            profile["avg_satisfaction"] = profile.get("avg_satisfaction", 0.5) * 0.9 + insight.satisfaction_score * 0.1
            profile["avg_urgency"] = profile.get("avg_urgency", 0.0) * 0.9 + insight.urgency_score * 0.1
            profile["avg_complexity"] = profile.get("avg_complexity", 0.0) * 0.9 + insight.complexity_score * 0.1
            
            # Update topics
            if "topics" not in profile:
                profile["topics"] = defaultdict(int)
            for topic in insight.topics:
                profile["topics"][topic] += 1
            
            profile["last_updated"] = datetime.utcnow().isoformat()
            
        except Exception as e:
            logger.error(f"Error updating user profile: {e}")
    
    async def get_conversation_summary(self, session_id: str) -> Dict[str, Any]:
        """Get conversation summary for session"""
        try:
            # Get insights for session
            session_insights = [
                insight for insight in self.insights_cache 
                if insight.session_id == session_id
            ]
            
            if not session_insights:
                return {"error": "No insights found for session"}
            
            # Calculate summary statistics
            sentiments = [insight.sentiment.value for insight in session_insights]
            intents = [insight.intent.value for insight in session_insights]
            
            avg_satisfaction = np.mean([insight.satisfaction_score for insight in session_insights])
            avg_urgency = np.mean([insight.urgency_score for insight in session_insights])
            avg_complexity = np.mean([insight.complexity_score for insight in session_insights])
            avg_confidence = np.mean([insight.confidence for insight in session_insights])
            
            # Get most common topics
            all_topics = []
            for insight in session_insights:
                all_topics.extend(insight.topics)
            
            topic_counts = defaultdict(int)
            for topic in all_topics:
                topic_counts[topic] += 1
            
            return {
                "session_id": session_id,
                "total_messages": len(session_insights),
                "sentiment_distribution": {
                    sentiment: sentiments.count(sentiment) for sentiment in set(sentiments)
                },
                "intent_distribution": {
                    intent: intents.count(intent) for intent in set(intents)
                },
                "average_scores": {
                    "satisfaction": round(avg_satisfaction, 2),
                    "urgency": round(avg_urgency, 2),
                    "complexity": round(avg_complexity, 2),
                    "confidence": round(avg_confidence, 2)
                },
                "top_topics": dict(sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:5]),
                "conversation_trend": self._analyze_conversation_trend(session_insights),
                "recommendations": self._generate_recommendations(session_insights)
            }
            
        except Exception as e:
            logger.error(f"Error getting conversation summary: {e}")
            return {"error": str(e)}
    
    def _analyze_conversation_trend(self, insights: List[ConversationInsight]) -> str:
        """Analyze overall conversation trend"""
        if len(insights) < 2:
            return "insufficient_data"
        
        # Compare first half vs second half satisfaction
        mid_point = len(insights) // 2
        first_half_satisfaction = np.mean([i.satisfaction_score for i in insights[:mid_point]])
        second_half_satisfaction = np.mean([i.satisfaction_score for i in insights[mid_point:]])
        
        if second_half_satisfaction > first_half_satisfaction + 0.1:
            return "improving"
        elif second_half_satisfaction < first_half_satisfaction - 0.1:
            return "declining"
        else:
            return "stable"
    
    def _generate_recommendations(self, insights: List[ConversationInsight]) -> List[str]:
        """Generate recommendations based on conversation analysis"""
        recommendations = []
        
        # Check for high urgency
        avg_urgency = np.mean([i.urgency_score for i in insights])
        if avg_urgency > 0.7:
            recommendations.append("High urgency detected - consider priority escalation")
        
        # Check for low satisfaction
        avg_satisfaction = np.mean([i.satisfaction_score for i in insights])
        if avg_satisfaction < 0.4:
            recommendations.append("Low satisfaction - consider human handoff")
        
        # Check for high complexity
        avg_complexity = np.mean([i.complexity_score for i in insights])
        if avg_complexity > 0.7:
            recommendations.append("High complexity conversation - provide detailed responses")
        
        # Check for repeated complaints
        complaint_count = sum(1 for i in insights if i.intent == IntentType.COMPLAINT)
        if complaint_count > len(insights) * 0.5:
            recommendations.append("Multiple complaints detected - escalate to support team")
        
        return recommendations
    
    async def _conversation_analysis_loop(self):
        """Main conversation analysis loop"""
        while True:
            try:
                # Analyze recent conversations
                await self._analyze_recent_conversations()
                await asyncio.sleep(300)  # Run every 5 minutes
            except Exception as e:
                logger.error(f"Conversation analysis loop error: {e}")
                await asyncio.sleep(60)
    
    async def _pattern_learning_loop(self):
        """Pattern learning loop"""
        while True:
            try:
                # Update ML patterns based on recent data
                await self._update_ml_patterns()
                await asyncio.sleep(3600)  # Run every hour
            except Exception as e:
                logger.error(f"Pattern learning loop error: {e}")
                await asyncio.sleep(300)
    
    async def _user_profiling_loop(self):
        """User profiling loop"""
        while True:
            try:
                # Update user profiles
                await self._update_user_profiles()
                await asyncio.sleep(1800)  # Run every 30 minutes
            except Exception as e:
                logger.error(f"User profiling loop error: {e}")
                await asyncio.sleep(300)
    
    async def _analyze_recent_conversations(self):
        """Analyze recent conversations for patterns"""
        # Implementation would analyze recent conversation data
        pass
    
    async def _update_ml_patterns(self):
        """Update machine learning patterns"""
        # Implementation would update ML models
        pass
    
    async def _update_user_profiles(self):
        """Update user profiles"""
        # Implementation would update user profiles
        pass


# Global conversation intelligence service instance
conversation_intelligence_service = ConversationIntelligenceService()
