from typing import Optional, Dict, Any
import logging
from datetime import datetime
import openai
import anthropic

from app.models.config import ApiConfig, SupabaseConfig, RagInstruction
from app.models.chat import ChatConfig
from app.services.supabase_service import SupabaseService

logger = logging.getLogger(__name__)


class ConfigService:
    """Service for managing system configurations"""
    
    def __init__(self):
        # In-memory storage for demo purposes
        # In production, this would use a proper database
        self.api_configs: Dict[str, ApiConfig] = {}
        self.supabase_configs: Dict[str, SupabaseConfig] = {}
        self.rag_instructions: Dict[str, RagInstruction] = {}
        self.chat_configs: Dict[str, ChatConfig] = {}
        self.supabase_service = SupabaseService()
        self._initialize_defaults()
    
    def _initialize_defaults(self):
        """Initialize default configurations"""
        # Default RAG instruction
        default_rag = RagInstruction(
            id="default",
            name="Default RAG Configuration",
            system_prompt="""You are a helpful AI assistant. Use the provided context to answer user questions accurately and helpfully. If the context doesn't contain relevant information, politely say so and provide general guidance if appropriate.

Guidelines:
- Always be helpful and professional
- Use the context provided to give accurate answers
- If unsure, acknowledge uncertainty
- Keep responses concise but informative""",
            context_prompt="""Context information:
{context}

Based on the above context, please answer the following question:
{question}""",
            max_context_length=2000,
            search_limit=5,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self.rag_instructions["default"] = default_rag
    
    # API Configuration Methods
    async def create_api_config(self, config: ApiConfig) -> ApiConfig:
        """Create a new API configuration"""
        config.created_at = datetime.utcnow()
        config.updated_at = datetime.utcnow()
        self.api_configs[config.id] = config
        logger.info(f"Created API config: {config.id}")
        return config
    
    async def get_api_config(self, config_id: str) -> Optional[ApiConfig]:
        """Get API configuration by ID"""
        return self.api_configs.get(config_id)
    
    async def update_api_config(
        self, 
        config_id: str, 
        config: ApiConfig
    ) -> Optional[ApiConfig]:
        """Update an existing API configuration"""
        if config_id not in self.api_configs:
            return None
        
        config.id = config_id
        config.updated_at = datetime.utcnow()
        self.api_configs[config_id] = config
        logger.info(f"Updated API config: {config_id}")
        return config
    
    async def test_api_connection(self, config: ApiConfig) -> bool:
        """Test API connection with given configuration"""
        try:
            if config.provider == "openai":
                return await self._test_openai_connection(config)
            elif config.provider == "anthropic":
                return await self._test_anthropic_connection(config)
            else:
                return await self._test_custom_api_connection(config)
        except Exception as e:
            logger.error(f"API connection test failed: {e}")
            return False
    
    async def _test_openai_connection(self, config: ApiConfig) -> bool:
        """Test OpenAI API connection"""
        try:
            client = openai.AsyncOpenAI(api_key=config.api_key)
            response = await client.chat.completions.create(
                model=config.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            return True
        except Exception as e:
            logger.error(f"OpenAI connection test failed: {e}")
            return False
    
    async def _test_anthropic_connection(self, config: ApiConfig) -> bool:
        """Test Anthropic API connection"""
        try:
            client = anthropic.AsyncAnthropic(api_key=config.api_key)
            response = await client.messages.create(
                model=config.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Hello"}]
            )
            return True
        except Exception as e:
            logger.error(f"Anthropic connection test failed: {e}")
            return False
    
    async def _test_custom_api_connection(self, config: ApiConfig) -> bool:
        """Test custom API connection"""
        # Placeholder for custom API testing
        logger.info("Custom API connection test not implemented")
        return False
    
    # Supabase Configuration Methods
    async def create_supabase_config(self, config: SupabaseConfig) -> SupabaseConfig:
        """Create a new Supabase configuration"""
        config.created_at = datetime.utcnow()
        config.updated_at = datetime.utcnow()
        self.supabase_configs[config.id] = config
        logger.info(f"Created Supabase config: {config.id}")
        return config
    
    async def get_supabase_config(self, config_id: str) -> Optional[SupabaseConfig]:
        """Get Supabase configuration by ID"""
        return self.supabase_configs.get(config_id)
    
    async def update_supabase_config(
        self, 
        config_id: str, 
        config: SupabaseConfig
    ) -> Optional[SupabaseConfig]:
        """Update an existing Supabase configuration"""
        if config_id not in self.supabase_configs:
            return None
        
        config.id = config_id
        config.updated_at = datetime.utcnow()
        self.supabase_configs[config_id] = config
        logger.info(f"Updated Supabase config: {config_id}")
        return config
    
    async def test_supabase_connection(self, config: SupabaseConfig) -> bool:
        """Test Supabase connection with given configuration"""
        return await self.supabase_service.test_connection(config)
    
    # RAG Instructions Methods
    async def create_rag_instruction(self, instruction: RagInstruction) -> RagInstruction:
        """Create a new RAG instruction"""
        instruction.created_at = datetime.utcnow()
        instruction.updated_at = datetime.utcnow()
        self.rag_instructions[instruction.id] = instruction
        logger.info(f"Created RAG instruction: {instruction.id}")
        return instruction
    
    async def get_rag_instruction(self, instruction_id: str) -> Optional[RagInstruction]:
        """Get RAG instruction by ID"""
        return self.rag_instructions.get(instruction_id)
    
    async def update_rag_instruction(
        self, 
        instruction_id: str, 
        instruction: RagInstruction
    ) -> Optional[RagInstruction]:
        """Update an existing RAG instruction"""
        if instruction_id not in self.rag_instructions:
            return None
        
        instruction.id = instruction_id
        instruction.updated_at = datetime.utcnow()
        self.rag_instructions[instruction_id] = instruction
        logger.info(f"Updated RAG instruction: {instruction_id}")
        return instruction
    
    # Chat Configuration Methods
    async def create_chat_config(self, config: ChatConfig) -> ChatConfig:
        """Create a new chat configuration"""
        config.created_at = datetime.utcnow()
        config.updated_at = datetime.utcnow()
        self.chat_configs[config.id] = config
        logger.info(f"Created chat config: {config.id}")
        return config
    
    async def get_chat_config(self, config_id: str) -> Optional[ChatConfig]:
        """Get chat configuration by ID"""
        return self.chat_configs.get(config_id)
    
    async def update_chat_config(
        self, 
        config_id: str, 
        config: ChatConfig
    ) -> Optional[ChatConfig]:
        """Update an existing chat configuration"""
        if config_id not in self.chat_configs:
            return None
        
        config.id = config_id
        config.updated_at = datetime.utcnow()
        self.chat_configs[config_id] = config
        logger.info(f"Updated chat config: {config_id}")
        return config
    
    # Utility Methods
    async def get_active_configurations(self) -> Dict[str, Any]:
        """Get all active configurations"""
        return {
            "api_configs": [config for config in self.api_configs.values() if config.is_active],
            "supabase_configs": [config for config in self.supabase_configs.values() if config.is_active],
            "rag_instructions": [instruction for instruction in self.rag_instructions.values() if instruction.is_active],
            "chat_configs": [config for config in self.chat_configs.values() if config.is_active]
        }
