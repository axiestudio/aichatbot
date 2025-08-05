from typing import List, Dict, Any
import logging
from datetime import datetime, timedelta
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for generating analytics and insights"""
    
    def __init__(self):
        # In-memory storage for demo purposes
        # In production, this would query a proper analytics database
        self.chat_events: List[Dict[str, Any]] = []
        self._generate_mock_data()
    
    def _generate_mock_data(self):
        """Generate mock analytics data for demonstration"""
        base_date = datetime.utcnow() - timedelta(days=30)
        
        # Generate mock chat events
        for i in range(500):
            event_date = base_date + timedelta(
                days=i % 30,
                hours=i % 24,
                minutes=i % 60
            )
            
            self.chat_events.append({
                "type": "chat_started",
                "timestamp": event_date,
                "session_id": f"session_{i}",
                "user_id": f"user_{i % 100}",
                "metadata": {}
            })
            
            # Add some messages
            for j in range((i % 5) + 1):
                self.chat_events.append({
                    "type": "message_sent",
                    "timestamp": event_date + timedelta(minutes=j),
                    "session_id": f"session_{i}",
                    "user_id": f"user_{i % 100}",
                    "role": "user" if j % 2 == 0 else "assistant",
                    "content": self._get_mock_message(j),
                    "metadata": {}
                })
    
    def _get_mock_message(self, index: int) -> str:
        """Get mock message content"""
        user_messages = [
            "How do I reset my password?",
            "What are your business hours?",
            "How can I contact support?",
            "Where can I find pricing information?",
            "How do I cancel my subscription?",
            "What payment methods do you accept?",
            "How do I update my profile?",
            "Can you help me with technical issues?",
            "What features are available?",
            "How do I get started?"
        ]
        
        assistant_messages = [
            "I can help you reset your password. Please follow these steps...",
            "Our business hours are Monday to Friday, 9 AM to 6 PM EST.",
            "You can contact our support team through email or live chat.",
            "You can find our pricing information on our website's pricing page.",
            "To cancel your subscription, please go to your account settings.",
            "We accept all major credit cards and PayPal.",
            "You can update your profile in the account settings section.",
            "I'd be happy to help with technical issues. What specific problem are you experiencing?",
            "Our platform offers many features including analytics, automation, and integrations.",
            "To get started, please create an account and follow our onboarding guide."
        ]
        
        if index % 2 == 0:
            return user_messages[index % len(user_messages)]
        else:
            return assistant_messages[index % len(assistant_messages)]
    
    async def get_overview(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get analytics overview for the specified date range"""
        filtered_events = [
            event for event in self.chat_events
            if start_date <= event["timestamp"] <= end_date
        ]
        
        chat_sessions = set()
        total_messages = 0
        user_messages = 0
        
        for event in filtered_events:
            if event["type"] == "chat_started":
                chat_sessions.add(event["session_id"])
            elif event["type"] == "message_sent":
                total_messages += 1
                if event.get("role") == "user":
                    user_messages += 1
        
        # Calculate average session length (mock calculation)
        avg_session_length = 4.2  # minutes
        
        return {
            "total_chats": len(chat_sessions),
            "total_messages": total_messages,
            "user_messages": user_messages,
            "assistant_messages": total_messages - user_messages,
            "average_session_length": avg_session_length,
            "active_users": len(set(event["user_id"] for event in filtered_events)),
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            }
        }
    
    async def get_daily_stats(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Get daily statistics for the specified date range"""
        daily_stats = defaultdict(lambda: {"chats": 0, "messages": 0})
        
        for event in self.chat_events:
            if start_date <= event["timestamp"] <= end_date:
                date_key = event["timestamp"].date().isoformat()
                
                if event["type"] == "chat_started":
                    daily_stats[date_key]["chats"] += 1
                elif event["type"] == "message_sent":
                    daily_stats[date_key]["messages"] += 1
        
        # Convert to list and sort by date
        result = []
        current_date = start_date.date()
        while current_date <= end_date.date():
            date_key = current_date.isoformat()
            result.append({
                "date": date_key,
                "chats": daily_stats[date_key]["chats"],
                "messages": daily_stats[date_key]["messages"]
            })
            current_date += timedelta(days=1)
        
        return result
    
    async def get_top_questions(
        self, 
        start_date: datetime, 
        end_date: datetime,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get most frequently asked questions"""
        user_messages = []
        
        for event in self.chat_events:
            if (start_date <= event["timestamp"] <= end_date and 
                event["type"] == "message_sent" and 
                event.get("role") == "user"):
                user_messages.append(event["content"])
        
        # Count message frequencies
        message_counts = Counter(user_messages)
        
        # Return top questions
        top_questions = []
        for message, count in message_counts.most_common(limit):
            top_questions.append({
                "question": message,
                "count": count
            })
        
        return top_questions
    
    async def get_performance_metrics(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get performance metrics"""
        # Mock performance data
        return {
            "user_satisfaction": 94.0,  # percentage
            "average_response_time": 1.2,  # seconds
            "resolution_rate": 87.0,  # percentage
            "first_response_time": 0.8,  # seconds
            "escalation_rate": 5.2,  # percentage
            "completion_rate": 92.5  # percentage
        }
    
    async def get_usage_patterns(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get usage patterns and trends"""
        hourly_distribution = defaultdict(int)
        daily_distribution = defaultdict(int)
        topic_distribution = defaultdict(int)
        
        for event in self.chat_events:
            if (start_date <= event["timestamp"] <= end_date and 
                event["type"] == "chat_started"):
                
                hour = event["timestamp"].hour
                day = event["timestamp"].strftime("%A")
                
                hourly_distribution[hour] += 1
                daily_distribution[day] += 1
        
        # Mock topic distribution
        topics = {
            "Account Support": 35,
            "Product Information": 28,
            "Technical Issues": 22,
            "General Inquiries": 15
        }
        
        # Find peak hours
        peak_hours = []
        sorted_hours = sorted(hourly_distribution.items(), key=lambda x: x[1], reverse=True)
        for hour, count in sorted_hours[:3]:
            if count > 0:
                peak_hours.append({
                    "hour": f"{hour:02d}:00 - {hour+1:02d}:00",
                    "activity": "High" if count > 20 else "Medium" if count > 10 else "Low"
                })
        
        return {
            "peak_hours": peak_hours,
            "daily_distribution": dict(daily_distribution),
            "hourly_distribution": dict(hourly_distribution),
            "topic_distribution": topics
        }
    
    async def record_chat_event(
        self, 
        event_type: str, 
        session_id: str,
        user_id: str = None,
        metadata: Dict[str, Any] = None
    ):
        """Record a chat event for analytics"""
        event = {
            "type": event_type,
            "timestamp": datetime.utcnow(),
            "session_id": session_id,
            "user_id": user_id,
            "metadata": metadata or {}
        }
        
        self.chat_events.append(event)
        logger.info(f"Recorded analytics event: {event_type}")
    
    async def get_export_data(
        self, 
        start_date: datetime, 
        end_date: datetime,
        format: str = "csv"
    ) -> Dict[str, Any]:
        """Get data for export in specified format"""
        daily_stats = await self.get_daily_stats(start_date, end_date)
        overview = await self.get_overview(start_date, end_date)
        top_questions = await self.get_top_questions(start_date, end_date)
        
        return {
            "daily_stats": daily_stats,
            "overview": overview,
            "top_questions": top_questions,
            "export_timestamp": datetime.utcnow().isoformat(),
            "format": format
        }
