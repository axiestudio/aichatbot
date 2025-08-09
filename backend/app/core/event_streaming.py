"""
Enterprise Event Streaming Platform
Uber/Netflix-style event-driven architecture with real-time data processing
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Callable, AsyncGenerator
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque
import uuid
import time

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Event types in the system"""
    USER_MESSAGE = "user_message"
    AI_RESPONSE = "ai_response"
    SESSION_CREATED = "session_created"
    SESSION_ENDED = "session_ended"
    ERROR_OCCURRED = "error_occurred"
    PERFORMANCE_METRIC = "performance_metric"
    SECURITY_ALERT = "security_alert"
    SYSTEM_HEALTH = "system_health"
    CONFIGURATION_CHANGED = "configuration_changed"
    FILE_UPLOADED = "file_uploaded"
    CACHE_OPERATION = "cache_operation"
    DATABASE_OPERATION = "database_operation"


@dataclass
class Event:
    """Event data structure"""
    id: str
    type: EventType
    timestamp: datetime
    source_service: str
    data: Dict[str, Any]
    correlation_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    trace_id: Optional[str] = None
    version: str = "1.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        result['type'] = self.type.value
        return result


class EventStream:
    """
    High-performance event stream similar to Kafka
    """
    
    def __init__(self, name: str, max_size: int = 100000):
        self.name = name
        self.events = deque(maxlen=max_size)
        self.subscribers = []
        self.metrics = {
            "total_events": 0,
            "events_per_second": 0,
            "last_event_time": None,
            "subscriber_count": 0
        }
        self._lock = asyncio.Lock()
        
    async def publish(self, event: Event):
        """Publish event to stream"""
        async with self._lock:
            self.events.append(event)
            self.metrics["total_events"] += 1
            self.metrics["last_event_time"] = datetime.utcnow()
            
            # Calculate events per second
            if len(self.events) >= 2:
                time_diff = (self.events[-1].timestamp - self.events[-2].timestamp).total_seconds()
                if time_diff > 0:
                    self.metrics["events_per_second"] = 1 / time_diff
                    
        # Notify subscribers
        await self._notify_subscribers(event)
        
    async def _notify_subscribers(self, event: Event):
        """Notify all subscribers of new event"""
        for subscriber in self.subscribers:
            try:
                await subscriber(event)
            except Exception as e:
                logger.error(f"Subscriber notification failed: {e}")
                
    def subscribe(self, callback: Callable[[Event], None]):
        """Subscribe to events"""
        self.subscribers.append(callback)
        self.metrics["subscriber_count"] = len(self.subscribers)
        
    def unsubscribe(self, callback: Callable[[Event], None]):
        """Unsubscribe from events"""
        if callback in self.subscribers:
            self.subscribers.remove(callback)
            self.metrics["subscriber_count"] = len(self.subscribers)
            
    async def get_events(
        self, 
        event_type: Optional[EventType] = None,
        since: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Event]:
        """Get events with filtering"""
        async with self._lock:
            events = list(self.events)
            
        # Apply filters
        if event_type:
            events = [e for e in events if e.type == event_type]
            
        if since:
            events = [e for e in events if e.timestamp >= since]
            
        # Sort by timestamp (newest first) and limit
        events.sort(key=lambda e: e.timestamp, reverse=True)
        return events[:limit]
        
    def get_metrics(self) -> Dict[str, Any]:
        """Get stream metrics"""
        return {
            **self.metrics,
            "stream_name": self.name,
            "current_size": len(self.events),
            "max_size": self.events.maxlen
        }


class EventProcessor:
    """
    Event processor for real-time analytics and reactions
    """
    
    def __init__(self, name: str):
        self.name = name
        self.processors = {}
        self.metrics = defaultdict(int)
        self.running = False
        
    def register_processor(self, event_type: EventType, processor: Callable[[Event], Any]):
        """Register event processor"""
        if event_type not in self.processors:
            self.processors[event_type] = []
        self.processors[event_type].append(processor)
        
    async def process_event(self, event: Event):
        """Process a single event"""
        if event.type in self.processors:
            for processor in self.processors[event.type]:
                try:
                    start_time = time.time()
                    
                    if asyncio.iscoroutinefunction(processor):
                        await processor(event)
                    else:
                        processor(event)
                        
                    processing_time = time.time() - start_time
                    self.metrics[f"{event.type.value}_processed"] += 1
                    self.metrics[f"{event.type.value}_processing_time"] += processing_time
                    
                except Exception as e:
                    logger.error(f"Event processing failed for {event.type}: {e}")
                    self.metrics[f"{event.type.value}_errors"] += 1
                    
    def get_metrics(self) -> Dict[str, Any]:
        """Get processor metrics"""
        return {
            "processor_name": self.name,
            "registered_processors": {
                event_type.value: len(processors) 
                for event_type, processors in self.processors.items()
            },
            "metrics": dict(self.metrics),
            "timestamp": datetime.utcnow().isoformat()
        }


class EventBus:
    """
    Central event bus for the entire application
    Similar to Uber's event streaming platform
    """
    
    def __init__(self):
        self.streams: Dict[str, EventStream] = {}
        self.processors: Dict[str, EventProcessor] = {}
        self.global_subscribers = []
        self.metrics = {
            "total_events_published": 0,
            "streams_created": 0,
            "processors_created": 0
        }
        
    def create_stream(self, name: str, max_size: int = 100000) -> EventStream:
        """Create a new event stream"""
        if name not in self.streams:
            self.streams[name] = EventStream(name, max_size)
            self.metrics["streams_created"] += 1
            logger.info(f"Created event stream: {name}")
            
        return self.streams[name]
        
    def get_stream(self, name: str) -> Optional[EventStream]:
        """Get existing stream"""
        return self.streams.get(name)
        
    def create_processor(self, name: str) -> EventProcessor:
        """Create a new event processor"""
        if name not in self.processors:
            self.processors[name] = EventProcessor(name)
            self.metrics["processors_created"] += 1
            logger.info(f"Created event processor: {name}")
            
        return self.processors[name]
        
    async def publish(
        self, 
        stream_name: str, 
        event_type: EventType, 
        data: Dict[str, Any],
        source_service: str = "unknown",
        **kwargs
    ):
        """Publish event to stream"""
        # Create event
        event = Event(
            id=str(uuid.uuid4()),
            type=event_type,
            timestamp=datetime.utcnow(),
            source_service=source_service,
            data=data,
            **kwargs
        )
        
        # Get or create stream
        stream = self.get_stream(stream_name)
        if not stream:
            stream = self.create_stream(stream_name)
            
        # Publish to stream
        await stream.publish(event)
        
        # Process with all processors
        for processor in self.processors.values():
            await processor.process_event(event)
            
        # Notify global subscribers
        for subscriber in self.global_subscribers:
            try:
                await subscriber(event)
            except Exception as e:
                logger.error(f"Global subscriber notification failed: {e}")
                
        self.metrics["total_events_published"] += 1
        
    def subscribe_global(self, callback: Callable[[Event], None]):
        """Subscribe to all events globally"""
        self.global_subscribers.append(callback)
        
    async def get_analytics(self) -> Dict[str, Any]:
        """Get comprehensive analytics"""
        analytics = {
            "timestamp": datetime.utcnow().isoformat(),
            "global_metrics": self.metrics,
            "streams": {},
            "processors": {},
            "event_types_summary": defaultdict(int)
        }
        
        # Stream analytics
        for name, stream in self.streams.items():
            analytics["streams"][name] = stream.get_metrics()
            
            # Count events by type in this stream
            for event in stream.events:
                analytics["event_types_summary"][event.type.value] += 1
                
        # Processor analytics
        for name, processor in self.processors.items():
            analytics["processors"][name] = processor.get_metrics()
            
        return analytics
        
    async def replay_events(
        self, 
        stream_name: str, 
        processor_name: str,
        since: Optional[datetime] = None
    ):
        """Replay events for a specific processor"""
        stream = self.get_stream(stream_name)
        processor = self.processors.get(processor_name)
        
        if not stream or not processor:
            raise ValueError("Stream or processor not found")
            
        events = await stream.get_events(since=since, limit=10000)
        
        logger.info(f"Replaying {len(events)} events for processor {processor_name}")
        
        for event in reversed(events):  # Replay in chronological order
            await processor.process_event(event)


class RealTimeAnalytics:
    """
    Real-time analytics engine for event streams
    """
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.analytics_processor = event_bus.create_processor("real_time_analytics")
        self.metrics_cache = {}
        self.time_windows = [60, 300, 900, 3600]  # 1min, 5min, 15min, 1hour
        
        # Register analytics processors
        self._register_analytics_processors()
        
    def _register_analytics_processors(self):
        """Register analytics event processors"""
        self.analytics_processor.register_processor(
            EventType.USER_MESSAGE,
            self._process_user_message
        )
        
        self.analytics_processor.register_processor(
            EventType.AI_RESPONSE,
            self._process_ai_response
        )
        
        self.analytics_processor.register_processor(
            EventType.ERROR_OCCURRED,
            self._process_error
        )
        
        self.analytics_processor.register_processor(
            EventType.PERFORMANCE_METRIC,
            self._process_performance_metric
        )
        
    async def _process_user_message(self, event: Event):
        """Process user message for analytics"""
        # Update message counts
        self._increment_metric("user_messages_total")
        self._increment_metric(f"user_messages_by_session_{event.session_id}")
        
        # Track message length
        message_length = len(event.data.get("message", ""))
        self._update_metric("message_length_avg", message_length)
        
    async def _process_ai_response(self, event: Event):
        """Process AI response for analytics"""
        self._increment_metric("ai_responses_total")
        
        # Track response time
        response_time = event.data.get("response_time_ms", 0)
        self._update_metric("ai_response_time_avg", response_time)
        
        # Track tokens used
        tokens = event.data.get("tokens_used", 0)
        self._increment_metric("ai_tokens_total", tokens)
        
    async def _process_error(self, event: Event):
        """Process error for analytics"""
        self._increment_metric("errors_total")
        
        error_type = event.data.get("error_type", "unknown")
        self._increment_metric(f"errors_by_type_{error_type}")
        
    async def _process_performance_metric(self, event: Event):
        """Process performance metric"""
        metric_name = event.data.get("metric_name")
        metric_value = event.data.get("metric_value")
        
        if metric_name and metric_value is not None:
            self._update_metric(f"performance_{metric_name}", metric_value)
            
    def _increment_metric(self, metric_name: str, value: int = 1):
        """Increment a counter metric"""
        if metric_name not in self.metrics_cache:
            self.metrics_cache[metric_name] = 0
        self.metrics_cache[metric_name] += value
        
    def _update_metric(self, metric_name: str, value: float):
        """Update an average metric"""
        avg_key = f"{metric_name}_avg"
        count_key = f"{metric_name}_count"
        
        if avg_key not in self.metrics_cache:
            self.metrics_cache[avg_key] = 0
            self.metrics_cache[count_key] = 0
            
        count = self.metrics_cache[count_key]
        current_avg = self.metrics_cache[avg_key]
        
        # Calculate new average
        new_avg = (current_avg * count + value) / (count + 1)
        
        self.metrics_cache[avg_key] = new_avg
        self.metrics_cache[count_key] = count + 1
        
    def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get real-time metrics"""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": dict(self.metrics_cache),
            "processor_metrics": self.analytics_processor.get_metrics()
        }


# Global event bus instance
event_bus = EventBus()
real_time_analytics = RealTimeAnalytics(event_bus)
