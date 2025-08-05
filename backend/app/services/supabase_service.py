from typing import List, Dict, Any, Optional
import logging
from supabase import create_client, Client
from app.core.config import settings
from app.models.config import SupabaseConfig

logger = logging.getLogger(__name__)


class SupabaseService:
    """Service for interacting with Supabase database"""
    
    def __init__(self):
        self.client: Optional[Client] = None
        self.config: Optional[SupabaseConfig] = None
        self._initialize_default_client()
    
    def _initialize_default_client(self):
        """Initialize default Supabase client if credentials are available"""
        if settings.SUPABASE_URL and settings.SUPABASE_ANON_KEY:
            try:
                self.client = create_client(
                    settings.SUPABASE_URL,
                    settings.SUPABASE_ANON_KEY
                )
                logger.info("Default Supabase client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize default Supabase client: {e}")
    
    def configure(self, config: SupabaseConfig):
        """Configure Supabase client with provided configuration"""
        try:
            self.client = create_client(config.url, config.anon_key)
            self.config = config
            logger.info(f"Supabase client configured for {config.url}")
        except Exception as e:
            logger.error(f"Failed to configure Supabase client: {e}")
            raise
    
    async def test_connection(self, config: SupabaseConfig) -> bool:
        """Test Supabase connection with given configuration"""
        try:
            test_client = create_client(config.url, config.anon_key)
            
            # Try to perform a simple query to test connection
            result = test_client.table(config.table_name).select("*").limit(1).execute()
            
            logger.info("Supabase connection test successful")
            return True
        except Exception as e:
            logger.error(f"Supabase connection test failed: {e}")
            return False
    
    async def search_knowledge_base(
        self, 
        query: str, 
        table_name: str = None,
        search_columns: List[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Search the knowledge base for relevant information"""
        if not self.client:
            raise ValueError("Supabase client not configured")
        
        table_name = table_name or (self.config.table_name if self.config else "knowledge_base")
        search_columns = search_columns or (self.config.search_columns if self.config else ["title", "content"])
        
        try:
            # Build search query using text search
            search_query = self.client.table(table_name)
            
            # Use full-text search if available, otherwise use ilike
            for i, column in enumerate(search_columns):
                if i == 0:
                    search_query = search_query.select("*").ilike(column, f"%{query}%")
                else:
                    search_query = search_query.or_(f"{column}.ilike.%{query}%")
            
            result = search_query.limit(limit).execute()
            
            logger.info(f"Knowledge base search returned {len(result.data)} results")
            return result.data
            
        except Exception as e:
            logger.error(f"Knowledge base search failed: {e}")
            return []
    
    async def insert_knowledge_item(
        self, 
        data: Dict[str, Any], 
        table_name: str = None
    ) -> Dict[str, Any]:
        """Insert a new item into the knowledge base"""
        if not self.client:
            raise ValueError("Supabase client not configured")
        
        table_name = table_name or (self.config.table_name if self.config else "knowledge_base")
        
        try:
            result = self.client.table(table_name).insert(data).execute()
            logger.info(f"Inserted new knowledge item into {table_name}")
            return result.data[0] if result.data else {}
        except Exception as e:
            logger.error(f"Failed to insert knowledge item: {e}")
            raise
    
    async def update_knowledge_item(
        self, 
        item_id: str, 
        data: Dict[str, Any], 
        table_name: str = None
    ) -> Dict[str, Any]:
        """Update an existing knowledge base item"""
        if not self.client:
            raise ValueError("Supabase client not configured")
        
        table_name = table_name or (self.config.table_name if self.config else "knowledge_base")
        
        try:
            result = self.client.table(table_name).update(data).eq("id", item_id).execute()
            logger.info(f"Updated knowledge item {item_id} in {table_name}")
            return result.data[0] if result.data else {}
        except Exception as e:
            logger.error(f"Failed to update knowledge item: {e}")
            raise
    
    async def delete_knowledge_item(
        self, 
        item_id: str, 
        table_name: str = None
    ) -> bool:
        """Delete a knowledge base item"""
        if not self.client:
            raise ValueError("Supabase client not configured")
        
        table_name = table_name or (self.config.table_name if self.config else "knowledge_base")
        
        try:
            result = self.client.table(table_name).delete().eq("id", item_id).execute()
            logger.info(f"Deleted knowledge item {item_id} from {table_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete knowledge item: {e}")
            return False
    
    async def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """Get the schema of a table"""
        if not self.client:
            raise ValueError("Supabase client not configured")
        
        try:
            # This is a simplified version - in a real implementation,
            # you might want to use Supabase's admin API or PostgreSQL introspection
            result = self.client.table(table_name).select("*").limit(1).execute()
            
            if result.data:
                columns = list(result.data[0].keys())
                return {"table": table_name, "columns": columns}
            else:
                return {"table": table_name, "columns": []}
                
        except Exception as e:
            logger.error(f"Failed to get table schema: {e}")
            return {"table": table_name, "columns": [], "error": str(e)}
    
    async def create_knowledge_base_table(self, table_name: str = "knowledge_base") -> bool:
        """Create a basic knowledge base table structure"""
        if not self.client:
            raise ValueError("Supabase client not configured")
        
        # Note: This would typically be done through Supabase dashboard or SQL
        # This is a placeholder for the actual table creation logic
        logger.info(f"Knowledge base table creation requested for {table_name}")
        logger.info("Please create the table manually in Supabase with columns: id, title, content, metadata, created_at, updated_at")
        return True
