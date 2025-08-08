import os
import logging
from typing import AsyncGenerator, Optional
from contextlib import asynccontextmanager

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, Session

# SQLAlchemy version compatibility
try:
    from sqlalchemy.ext.asyncio import async_sessionmaker
    SQLALCHEMY_2_0 = True
except ImportError:
    # Fallback for SQLAlchemy 1.4
    SQLALCHEMY_2_0 = False
    def async_sessionmaker(engine, class_=AsyncSession, **kwargs):
        return sessionmaker(engine, class_=class_, **kwargs)
from sqlalchemy.pool import StaticPool

from app.core.config import settings
# Import Railway-compatible database models
try:
    from app.models.database import Base
    logger.info("✅ Using Railway-compatible database models")
except Exception as e:
    logger.warning(f"⚠️ Database models failed ({e}), trying full models")
    try:
        from app.models.database_full import Base
        logger.info("✅ Using full database models")
    except Exception as e2:
        logger.error(f"❌ All model imports failed: {e2}")
        # Create minimal Base for emergency fallback
        from sqlalchemy.ext.declarative import declarative_base
        Base = declarative_base()
        logger.warning("🚨 Using emergency minimal Base")

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Database connection and session management"""
    
    def __init__(self):
        self.async_engine = None
        self.sync_engine = None
        self.async_session_factory = None
        self.sync_session_factory = None
        self._initialized = False
    
    def initialize(self):
        """Initialize database connections"""
        if self._initialized:
            return
        
        try:
            # Determine database URL
            database_url = self._get_database_url()
            
            # Create async engine
            if database_url.startswith('sqlite'):
                # SQLite configuration
                self.async_engine = create_async_engine(
                    database_url,
                    poolclass=StaticPool,
                    connect_args={
                        "check_same_thread": False,
                        "timeout": 20
                    },
                    echo=settings.DEBUG
                )
                
                # Sync engine for migrations
                sync_url = database_url.replace('aiosqlite', 'sqlite')
                self.sync_engine = create_engine(
                    sync_url,
                    poolclass=StaticPool,
                    connect_args={"check_same_thread": False},
                    echo=settings.DEBUG
                )
            else:
                # PostgreSQL configuration
                self.async_engine = create_async_engine(
                    database_url,
                    pool_size=10,
                    max_overflow=20,
                    pool_pre_ping=True,
                    echo=settings.DEBUG
                )
                
                # Sync engine for migrations
                sync_url = database_url.replace('asyncpg', 'psycopg2')
                self.sync_engine = create_engine(
                    sync_url,
                    pool_size=10,
                    max_overflow=20,
                    pool_pre_ping=True,
                    echo=settings.DEBUG
                )
            
            # Create session factories
            self.async_session_factory = async_sessionmaker(
                self.async_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            self.sync_session_factory = sessionmaker(
                self.sync_engine,
                expire_on_commit=False
            )
            
            self._initialized = True
            logger.info(f"Database initialized: {database_url.split('@')[-1] if '@' in database_url else database_url}")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise
    
    def _get_database_url(self) -> str:
        """Get database URL from settings"""
        if settings.DATABASE_URL:
            return settings.DATABASE_URL
        
        # Default to SQLite for development
        db_path = os.path.join(os.getcwd(), "chatbot.db")
        return f"sqlite+aiosqlite:///{db_path}"
    
    @asynccontextmanager
    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get async database session"""
        if not self._initialized:
            self.initialize()
        
        async with self.async_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    def get_sync_session(self) -> Session:
        """Get sync database session"""
        if not self._initialized:
            self.initialize()
        
        return self.sync_session_factory()
    
    async def create_tables(self):
        """Create all database tables"""
        if not self._initialized:
            self.initialize()
        
        try:
            async with self.async_engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create database tables: {str(e)}")
            raise
    
    def create_tables_sync(self):
        """Create all database tables synchronously"""
        if not self._initialized:
            self.initialize()
        
        try:
            Base.metadata.create_all(self.sync_engine)
            logger.info("Database tables created successfully (sync)")
        except Exception as e:
            logger.error(f"Failed to create database tables (sync): {str(e)}")
            raise
    
    async def drop_tables(self):
        """Drop all database tables"""
        if not self._initialized:
            self.initialize()
        
        try:
            async with self.async_engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
            logger.info("Database tables dropped successfully")
        except Exception as e:
            logger.error(f"Failed to drop database tables: {str(e)}")
            raise
    
    async def check_connection(self) -> bool:
        """Check database connection"""
        if not self._initialized:
            self.initialize()
        
        try:
            async with self.async_engine.begin() as conn:
                await conn.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database connection check failed: {str(e)}")
            return False
    
    async def get_database_info(self) -> dict:
        """Get database information"""
        if not self._initialized:
            self.initialize()
        
        try:
            info = {
                "url": str(self.async_engine.url).split('@')[-1] if '@' in str(self.async_engine.url) else str(self.async_engine.url),
                "driver": self.async_engine.driver,
                "pool_size": getattr(self.async_engine.pool, 'size', None),
                "checked_out": getattr(self.async_engine.pool, 'checkedout', None),
                "overflow": getattr(self.async_engine.pool, 'overflow', None),
                "checked_in": getattr(self.async_engine.pool, 'checkedin', None),
            }
            
            # Test connection
            info["connected"] = await self.check_connection()
            
            return info
        except Exception as e:
            logger.error(f"Failed to get database info: {str(e)}")
            return {"error": str(e)}
    
    async def cleanup(self):
        """Cleanup database connections"""
        try:
            if self.async_engine:
                await self.async_engine.dispose()
            if self.sync_engine:
                self.sync_engine.dispose()
            logger.info("Database connections cleaned up")
        except Exception as e:
            logger.error(f"Error during database cleanup: {str(e)}")


# Global database manager instance
db_manager = DatabaseManager()


# Dependency for FastAPI
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for database session"""
    async with db_manager.get_async_session() as session:
        yield session


# Initialize database on import
def init_database():
    """Initialize database on application startup"""
    try:
        db_manager.initialize()
        
        # Create tables if they don't exist
        if settings.ENVIRONMENT == "development":
            db_manager.create_tables_sync()
            logger.info("Development database initialized")
        
    except Exception as e:
        logger.error(f"Failed to initialize database on startup: {str(e)}")
        # Don't raise here to allow app to start without database


# Database utilities
class DatabaseUtils:
    """Database utility functions"""
    
    @staticmethod
    async def execute_raw_query(query: str, params: Optional[dict] = None):
        """Execute raw SQL query"""
        async with db_manager.get_async_session() as session:
            result = await session.execute(query, params or {})
            return result.fetchall()
    
    @staticmethod
    async def get_table_info(table_name: str) -> dict:
        """Get information about a specific table"""
        try:
            async with db_manager.get_async_session() as session:
                # Get table metadata
                metadata = MetaData()
                await session.run_sync(
                    lambda sync_session: metadata.reflect(bind=sync_session.bind, only=[table_name])
                )
                
                if table_name in metadata.tables:
                    table = metadata.tables[table_name]
                    return {
                        "name": table.name,
                        "columns": [
                            {
                                "name": col.name,
                                "type": str(col.type),
                                "nullable": col.nullable,
                                "primary_key": col.primary_key,
                                "foreign_keys": [str(fk) for fk in col.foreign_keys]
                            }
                            for col in table.columns
                        ],
                        "indexes": [
                            {
                                "name": idx.name,
                                "columns": [col.name for col in idx.columns],
                                "unique": idx.unique
                            }
                            for idx in table.indexes
                        ]
                    }
                else:
                    return {"error": f"Table {table_name} not found"}
                    
        except Exception as e:
            logger.error(f"Error getting table info for {table_name}: {str(e)}")
            return {"error": str(e)}
    
    @staticmethod
    async def get_database_stats() -> dict:
        """Get database statistics"""
        try:
            stats = {}
            
            # Get table row counts
            table_names = [
                'chat_sessions', 'chat_messages', 'documents', 'document_chunks',
                'security_events', 'audit_logs', 'user_sessions'
            ]
            
            async with db_manager.get_async_session() as session:
                for table_name in table_names:
                    try:
                        result = await session.execute(f"SELECT COUNT(*) FROM {table_name}")
                        count = result.scalar()
                        stats[f"{table_name}_count"] = count
                    except Exception:
                        stats[f"{table_name}_count"] = 0
                
                # Get database size (SQLite specific)
                try:
                    if 'sqlite' in str(db_manager.async_engine.url):
                        result = await session.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
                        size = result.scalar()
                        stats["database_size_bytes"] = size
                except Exception:
                    pass
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting database stats: {str(e)}")
            return {"error": str(e)}


# Export commonly used items
__all__ = [
    'db_manager',
    'get_db_session',
    'init_database',
    'DatabaseManager',
    'DatabaseUtils'
]
