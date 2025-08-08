from typing import Dict, Any, List, Optional
import logging
import openai
import anthropic
import numpy as np

# Optional sentence transformers import
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SentenceTransformer = None
    SENTENCE_TRANSFORMERS_AVAILABLE = False

from app.core.config import settings
from app.services.supabase_service import SupabaseService
from app.services.config_service import ConfigService, RagInstruction, ApiConfig, SupabaseConfig

logger = logging.getLogger(__name__)


class RAGService:
    """Retrieval-Augmented Generation service"""
    
    def __init__(self):
        self.supabase_service = SupabaseService()
        self.config_service = ConfigService()
        self.embedding_model = None
        self._initialize_embedding_model()
    
    def _initialize_embedding_model(self):
        """Initialize the embedding model for semantic search"""
        try:
            self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
            logger.info(f"Embedding model {settings.EMBEDDING_MODEL} initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize embedding model: {e}")
    
    async def generate_response(
        self, 
        message: str, 
        session_id: str,
        config_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a response using RAG"""
        try:
            # Get configurations
            rag_instruction = await self._get_rag_instruction(config_id)
            api_config = await self._get_api_config(config_id)
            supabase_config = await self._get_supabase_config(config_id)
            
            # Retrieve relevant context
            context_data = await self._retrieve_context(
                message, 
                supabase_config, 
                rag_instruction
            )
            
            # Generate response using AI
            response = await self._generate_ai_response(
                message,
                context_data,
                rag_instruction,
                api_config
            )
            
            return {
                "response": response,
                "sources": context_data.get("sources", []),
                "metadata": {
                    "context_length": len(context_data.get("context", "")),
                    "sources_count": len(context_data.get("sources", [])),
                    "model_used": api_config.model if api_config else "default"
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating RAG response: {e}")
            return {
                "response": "I apologize, but I encountered an error while processing your request. Please try again.",
                "sources": [],
                "metadata": {"error": str(e)}
            }
    
    async def _get_rag_instruction(self, config_id: Optional[str]) -> RagInstruction:
        """Get RAG instruction configuration"""
        if config_id:
            instruction = await self.config_service.get_rag_instruction(config_id)
            if instruction:
                return instruction
        
        # Return default instruction
        from datetime import datetime
        return RagInstruction(
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
            max_context_length=settings.DEFAULT_MAX_CONTEXT_LENGTH,
            search_limit=settings.DEFAULT_SEARCH_LIMIT,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    
    async def _get_api_config(self, config_id: Optional[str]) -> Optional[ApiConfig]:
        """Get API configuration"""
        if config_id:
            return await self.config_service.get_api_config(config_id)
        return None
    
    async def _get_supabase_config(self, config_id: Optional[str]) -> Optional[SupabaseConfig]:
        """Get Supabase configuration"""
        if config_id:
            return await self.config_service.get_supabase_config(config_id)
        return None
    
    async def _retrieve_context(
        self, 
        query: str, 
        supabase_config: Optional[SupabaseConfig],
        rag_instruction: RagInstruction
    ) -> Dict[str, Any]:
        """Retrieve relevant context from knowledge base"""
        try:
            if not supabase_config:
                logger.info("No Supabase configuration found, using empty context")
                return {"context": "", "sources": []}
            
            # Configure Supabase service
            self.supabase_service.configure(supabase_config)
            
            # Search for relevant documents
            search_results = await self.supabase_service.search_knowledge_base(
                query=query,
                table_name=supabase_config.table_name,
                search_columns=supabase_config.search_columns,
                limit=rag_instruction.search_limit
            )
            
            # Process and format context
            context_parts = []
            sources = []
            
            for result in search_results:
                # Extract content based on available columns
                content = ""
                if "content" in result:
                    content = result["content"]
                elif "text" in result:
                    content = result["text"]
                elif "description" in result:
                    content = result["description"]
                
                if content:
                    context_parts.append(content)
                    sources.append({
                        "id": result.get("id"),
                        "title": result.get("title", "Untitled"),
                        "content": content[:200] + "..." if len(content) > 200 else content
                    })
            
            # Combine context and limit length
            full_context = "\n\n".join(context_parts)
            if len(full_context) > rag_instruction.max_context_length:
                full_context = full_context[:rag_instruction.max_context_length] + "..."
            
            return {
                "context": full_context,
                "sources": sources
            }
            
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return {"context": "", "sources": []}
    
    async def _generate_ai_response(
        self,
        message: str,
        context_data: Dict[str, Any],
        rag_instruction: RagInstruction,
        api_config: Optional[ApiConfig]
    ) -> str:
        """Generate AI response using the configured provider"""
        try:
            # Format the prompt
            context = context_data.get("context", "")
            formatted_prompt = rag_instruction.context_prompt.format(
                context=context,
                question=message
            )
            
            if api_config and api_config.api_key:
                return await self._call_ai_api(formatted_prompt, rag_instruction, api_config)
            else:
                return await self._generate_fallback_response(message, context)
                
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return "I apologize, but I'm having trouble generating a response right now. Please try again later."
    
    async def _call_ai_api(
        self, 
        prompt: str, 
        rag_instruction: RagInstruction,
        api_config: ApiConfig
    ) -> str:
        """Call the configured AI API"""
        try:
            if api_config.provider == "openai":
                return await self._call_openai(prompt, rag_instruction, api_config)
            elif api_config.provider == "anthropic":
                return await self._call_anthropic(prompt, rag_instruction, api_config)
            else:
                return await self._call_custom_api(prompt, rag_instruction, api_config)
        except Exception as e:
            logger.error(f"Error calling AI API: {e}")
            raise
    
    async def _call_openai(
        self, 
        prompt: str, 
        rag_instruction: RagInstruction,
        api_config: ApiConfig
    ) -> str:
        """Call OpenAI API"""
        client = openai.AsyncOpenAI(api_key=api_config.api_key)
        
        response = await client.chat.completions.create(
            model=api_config.model,
            messages=[
                {"role": "system", "content": rag_instruction.system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=api_config.temperature,
            max_tokens=api_config.max_tokens
        )
        
        return response.choices[0].message.content
    
    async def _call_anthropic(
        self, 
        prompt: str, 
        rag_instruction: RagInstruction,
        api_config: ApiConfig
    ) -> str:
        """Call Anthropic API"""
        client = anthropic.AsyncAnthropic(api_key=api_config.api_key)
        
        response = await client.messages.create(
            model=api_config.model,
            max_tokens=api_config.max_tokens,
            temperature=api_config.temperature,
            system=rag_instruction.system_prompt,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.content[0].text
    
    async def _call_custom_api(
        self, 
        prompt: str, 
        rag_instruction: RagInstruction,
        api_config: ApiConfig
    ) -> str:
        """Call custom API endpoint"""
        # Placeholder for custom API implementation
        logger.warning("Custom API not implemented")
        return "Custom API response not available"
    
    async def _generate_fallback_response(self, message: str, context: str) -> str:
        """Generate a fallback response when no AI API is configured"""
        if context:
            return f"Based on the available information: {context[:500]}... I found some relevant information, but I need an AI API to be configured to provide a proper response to your question: '{message}'"
        else:
            return "I'd be happy to help you, but I need both a knowledge base and an AI API to be configured to provide accurate responses. Please contact an administrator to set up the system."
