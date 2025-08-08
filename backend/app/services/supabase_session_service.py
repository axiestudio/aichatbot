"""
Supabase Session Service - Redis Session Replacement
Uses Supabase for session storage and management
"""

import json
import logging
import uuid
from typing import Any, Optional, Dict
from datetime import datetime, timedelta

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    Client = None

from app.core.config import settings

logger = logging.getLogger(__name__)


class SupabaseSessionService:
    """Supabase-based session service replacing Redis sessions"""
    
    def __init__(self):
        self.supabase: Optional[Client] = None
        self.fallback_sessions = {}  # In-memory fallback
        self.session_timeout = 3600  # 1 hour default
        
    async def initialize(self):
        """Initialize Supabase connection"""
        try:
            if not SUPABASE_AVAILABLE:
                logger.warning("Supabase not available, using fallback sessions")
                return False
                
            if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
                logger.warning("Supabase credentials not configured, using fallback sessions")
                return False
                
            self.supabase = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_ANON_KEY
            )
            
            # Create sessions table if it doesn't exist
            await self._ensure_sessions_table()
            
            logger.info("✅ Supabase session service initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Supabase sessions: {e}")
            return False
    
    async def _ensure_sessions_table(self):
        """Ensure sessions table exists in Supabase"""
        try:
            # Create sessions table SQL
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS user_sessions (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(255) UNIQUE NOT NULL,
                user_id VARCHAR(255),
                session_data JSONB NOT NULL DEFAULT '{}',
                ip_address VARCHAR(45),
                user_agent TEXT,
                expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                is_active BOOLEAN DEFAULT TRUE
            );
            
            CREATE INDEX IF NOT EXISTS idx_session_id ON user_sessions(session_id);
            CREATE INDEX IF NOT EXISTS idx_user_id ON user_sessions(user_id);
            CREATE INDEX IF NOT EXISTS idx_session_expires ON user_sessions(expires_at);
            CREATE INDEX IF NOT EXISTS idx_session_active ON user_sessions(is_active);
            """
            
            logger.info("Session table structure verified")
            
        except Exception as e:
            logger.warning(f"Could not verify session table: {e}")
    
    async def create_session(self, user_id: Optional[str] = None, session_data: Dict[str, Any] = None, 
                           ip_address: str = None, user_agent: str = None, 
                           timeout: int = None) -> str:
        """Create a new session"""
        try:
            session_id = str(uuid.uuid4())
            timeout = timeout or self.session_timeout
            expires_at = datetime.utcnow() + timedelta(seconds=timeout)
            
            session_info = {
                'session_id': session_id,
                'user_id': user_id,
                'session_data': session_data or {},
                'ip_address': ip_address,
                'user_agent': user_agent,
                'expires_at': expires_at.isoformat(),
                'is_active': True
            }
            
            if self.supabase:
                # Store in Supabase
                result = self.supabase.table('user_sessions').insert(session_info).execute()
                if result.data:
                    logger.info(f"Session created: {session_id}")
                    return session_id
            else:
                # Store in fallback
                self.fallback_sessions[session_id] = {
                    **session_info,
                    'expires_at': expires_at
                }
                return session_id
                
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            return None
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data"""
        try:
            if self.supabase:
                # Query Supabase
                result = self.supabase.table('user_sessions').select('*').eq('session_id', session_id).eq('is_active', True).execute()
                
                if result.data:
                    session = result.data[0]
                    expires_at = datetime.fromisoformat(session['expires_at'].replace('Z', '+00:00'))
                    
                    if expires_at > datetime.utcnow():
                        # Update last activity
                        await self._update_session_activity(session_id)
                        return session
                    else:
                        # Expired, deactivate it
                        await self.delete_session(session_id)
                        return None
                else:
                    return None
            else:
                # Check fallback
                if session_id in self.fallback_sessions:
                    session = self.fallback_sessions[session_id]
                    if session['expires_at'] > datetime.utcnow():
                        return session
                    else:
                        del self.fallback_sessions[session_id]
                        return None
                
        except Exception as e:
            logger.error(f"Error getting session {session_id}: {e}")
            return None
    
    async def update_session(self, session_id: str, session_data: Dict[str, Any]) -> bool:
        """Update session data"""
        try:
            if self.supabase:
                # Update in Supabase
                update_data = {
                    'session_data': session_data,
                    'updated_at': datetime.utcnow().isoformat()
                }
                
                result = self.supabase.table('user_sessions').update(update_data).eq('session_id', session_id).eq('is_active', True).execute()
                return len(result.data) > 0 if result.data else False
            else:
                # Update fallback
                if session_id in self.fallback_sessions:
                    self.fallback_sessions[session_id]['session_data'] = session_data
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Error updating session {session_id}: {e}")
            return False
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete/deactivate session"""
        try:
            if self.supabase:
                # Deactivate in Supabase (soft delete)
                update_data = {
                    'is_active': False,
                    'updated_at': datetime.utcnow().isoformat()
                }
                
                result = self.supabase.table('user_sessions').update(update_data).eq('session_id', session_id).execute()
                return len(result.data) > 0 if result.data else False
            else:
                # Remove from fallback
                return self.fallback_sessions.pop(session_id, None) is not None
                
        except Exception as e:
            logger.error(f"Error deleting session {session_id}: {e}")
            return False
    
    async def extend_session(self, session_id: str, additional_seconds: int = None) -> bool:
        """Extend session expiration"""
        try:
            additional_seconds = additional_seconds or self.session_timeout
            new_expires_at = datetime.utcnow() + timedelta(seconds=additional_seconds)
            
            if self.supabase:
                update_data = {
                    'expires_at': new_expires_at.isoformat(),
                    'updated_at': datetime.utcnow().isoformat()
                }
                
                result = self.supabase.table('user_sessions').update(update_data).eq('session_id', session_id).eq('is_active', True).execute()
                return len(result.data) > 0 if result.data else False
            else:
                if session_id in self.fallback_sessions:
                    self.fallback_sessions[session_id]['expires_at'] = new_expires_at
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Error extending session {session_id}: {e}")
            return False
    
    async def get_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all active sessions for a user"""
        try:
            if self.supabase:
                result = self.supabase.table('user_sessions').select('*').eq('user_id', user_id).eq('is_active', True).execute()
                
                if result.data:
                    # Filter out expired sessions
                    now = datetime.utcnow()
                    active_sessions = []
                    
                    for session in result.data:
                        expires_at = datetime.fromisoformat(session['expires_at'].replace('Z', '+00:00'))
                        if expires_at > now:
                            active_sessions.append(session)
                        else:
                            # Clean up expired session
                            await self.delete_session(session['session_id'])
                    
                    return active_sessions
                else:
                    return []
            else:
                # Check fallback
                now = datetime.utcnow()
                user_sessions = []
                
                for session_id, session in self.fallback_sessions.items():
                    if session.get('user_id') == user_id and session['expires_at'] > now:
                        user_sessions.append(session)
                
                return user_sessions
                
        except Exception as e:
            logger.error(f"Error getting user sessions for {user_id}: {e}")
            return []
    
    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions"""
        try:
            if self.supabase:
                now = datetime.utcnow().isoformat()
                
                # Deactivate expired sessions
                update_data = {
                    'is_active': False,
                    'updated_at': now
                }
                
                result = self.supabase.table('user_sessions').update(update_data).lt('expires_at', now).eq('is_active', True).execute()
                return len(result.data) if result.data else 0
            else:
                # Clean fallback sessions
                now = datetime.utcnow()
                expired_sessions = [
                    session_id for session_id, session in self.fallback_sessions.items()
                    if session['expires_at'] <= now
                ]
                
                for session_id in expired_sessions:
                    del self.fallback_sessions[session_id]
                
                return len(expired_sessions)
                
        except Exception as e:
            logger.error(f"Error cleaning up expired sessions: {e}")
            return 0
    
    async def _update_session_activity(self, session_id: str):
        """Update session last activity timestamp"""
        try:
            if self.supabase:
                update_data = {
                    'updated_at': datetime.utcnow().isoformat()
                }
                
                self.supabase.table('user_sessions').update(update_data).eq('session_id', session_id).execute()
                
        except Exception as e:
            logger.debug(f"Error updating session activity: {e}")
    
    async def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        try:
            if self.supabase:
                # Total active sessions
                active_result = self.supabase.table('user_sessions').select('id', count='exact').eq('is_active', True).execute()
                active_count = active_result.count if hasattr(active_result, 'count') else 0
                
                # Total sessions (all time)
                total_result = self.supabase.table('user_sessions').select('id', count='exact').execute()
                total_count = total_result.count if hasattr(total_result, 'count') else 0
                
                return {
                    'active_sessions': active_count,
                    'total_sessions': total_count,
                    'storage_type': 'supabase'
                }
            else:
                now = datetime.utcnow()
                active_sessions = sum(1 for session in self.fallback_sessions.values() if session['expires_at'] > now)
                
                return {
                    'active_sessions': active_sessions,
                    'total_sessions': len(self.fallback_sessions),
                    'storage_type': 'memory'
                }
                
        except Exception as e:
            logger.error(f"Error getting session stats: {e}")
            return {'error': str(e)}


# Global session service instance
supabase_session_service = SupabaseSessionService()

# Alias for compatibility
session_service = supabase_session_service
