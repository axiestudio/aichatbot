import asyncio
import numpy as np
from typing import List, Optional, Dict, Any
import logging
from functools import lru_cache

# Embedding model imports
from sentence_transformers import SentenceTransformer
import openai
from openai import AsyncOpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating and managing text embeddings"""
    
    def __init__(self):
        self.model_name = getattr(settings, 'EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
        self.embedding_provider = getattr(settings, 'EMBEDDING_PROVIDER', 'sentence_transformers')
        self.embedding_dimension = 384  # Default for all-MiniLM-L6-v2
        
        # Initialize embedding model
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the embedding model based on configuration"""
        try:
            if self.embedding_provider == 'sentence_transformers':
                self.model = SentenceTransformer(self.model_name)
                self.embedding_dimension = self.model.get_sentence_embedding_dimension()
                logger.info(f"Initialized SentenceTransformer model: {self.model_name}")
                
            elif self.embedding_provider == 'openai':
                self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
                self.model_name = getattr(settings, 'OPENAI_EMBEDDING_MODEL', 'text-embedding-ada-002')
                self.embedding_dimension = 1536  # Default for text-embedding-ada-002
                logger.info(f"Initialized OpenAI embedding model: {self.model_name}")
                
            else:
                raise ValueError(f"Unsupported embedding provider: {self.embedding_provider}")
                
        except Exception as e:
            logger.error(f"Error initializing embedding model: {str(e)}")
            # Fallback to a basic model
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.embedding_provider = 'sentence_transformers'
            self.embedding_dimension = 384
            logger.warning("Falling back to default SentenceTransformer model")
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        try:
            if not text or not text.strip():
                return [0.0] * self.embedding_dimension
            
            # Clean and truncate text if necessary
            text = self._preprocess_text(text)
            
            if self.embedding_provider == 'sentence_transformers':
                return await self._generate_sentence_transformer_embedding(text)
            elif self.embedding_provider == 'openai':
                return await self._generate_openai_embedding(text)
            else:
                raise ValueError(f"Unsupported embedding provider: {self.embedding_provider}")
                
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            # Return zero vector as fallback
            return [0.0] * self.embedding_dimension
    
    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts efficiently"""
        try:
            if not texts:
                return []
            
            # Clean and preprocess texts
            processed_texts = [self._preprocess_text(text) for text in texts]
            
            if self.embedding_provider == 'sentence_transformers':
                return await self._generate_sentence_transformer_embeddings_batch(processed_texts)
            elif self.embedding_provider == 'openai':
                return await self._generate_openai_embeddings_batch(processed_texts)
            else:
                raise ValueError(f"Unsupported embedding provider: {self.embedding_provider}")
                
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {str(e)}")
            # Return zero vectors as fallback
            return [[0.0] * self.embedding_dimension for _ in texts]
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        try:
            # Convert to numpy arrays
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Calculate cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            
            # Ensure similarity is between 0 and 1
            return max(0.0, min(1.0, (similarity + 1) / 2))
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            return 0.0
    
    def find_most_similar(
        self, 
        query_embedding: List[float], 
        candidate_embeddings: List[List[float]], 
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Find the most similar embeddings to a query embedding"""
        try:
            similarities = []
            
            for i, candidate in enumerate(candidate_embeddings):
                similarity = self.calculate_similarity(query_embedding, candidate)
                similarities.append({
                    'index': i,
                    'similarity': similarity
                })
            
            # Sort by similarity (descending)
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            
            # Return top k results
            return similarities[:top_k]
            
        except Exception as e:
            logger.error(f"Error finding most similar: {str(e)}")
            return []
    
    async def cluster_embeddings(
        self, 
        embeddings: List[List[float]], 
        n_clusters: int = 5
    ) -> List[int]:
        """Cluster embeddings using K-means"""
        try:
            from sklearn.cluster import KMeans
            
            if len(embeddings) < n_clusters:
                # If we have fewer embeddings than clusters, assign each to its own cluster
                return list(range(len(embeddings)))
            
            # Convert to numpy array
            embedding_matrix = np.array(embeddings)
            
            # Perform K-means clustering
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(embedding_matrix)
            
            return cluster_labels.tolist()
            
        except Exception as e:
            logger.error(f"Error clustering embeddings: {str(e)}")
            # Return all embeddings in cluster 0 as fallback
            return [0] * len(embeddings)
    
    # Private methods for different embedding providers
    
    async def _generate_sentence_transformer_embedding(self, text: str) -> List[float]:
        """Generate embedding using SentenceTransformer"""
        try:
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(
                None, 
                lambda: self.model.encode(text, convert_to_tensor=False)
            )
            return embedding.tolist()
            
        except Exception as e:
            logger.error(f"Error with SentenceTransformer embedding: {str(e)}")
            raise
    
    async def _generate_sentence_transformer_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using SentenceTransformer in batch"""
        try:
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(
                None, 
                lambda: self.model.encode(texts, convert_to_tensor=False, batch_size=32)
            )
            return embeddings.tolist()
            
        except Exception as e:
            logger.error(f"Error with SentenceTransformer batch embeddings: {str(e)}")
            raise
    
    async def _generate_openai_embedding(self, text: str) -> List[float]:
        """Generate embedding using OpenAI API"""
        try:
            response = await self.openai_client.embeddings.create(
                model=self.model_name,
                input=text
            )
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"Error with OpenAI embedding: {str(e)}")
            raise
    
    async def _generate_openai_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using OpenAI API in batch"""
        try:
            # OpenAI API supports batch processing
            response = await self.openai_client.embeddings.create(
                model=self.model_name,
                input=texts
            )
            return [item.embedding for item in response.data]
            
        except Exception as e:
            logger.error(f"Error with OpenAI batch embeddings: {str(e)}")
            raise
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text before embedding generation"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Truncate if too long (model-specific limits)
        max_length = 8192  # Conservative limit
        if len(text) > max_length:
            text = text[:max_length]
            logger.warning(f"Text truncated to {max_length} characters for embedding")
        
        return text
    
    @lru_cache(maxsize=1000)
    def _cached_embedding(self, text: str) -> List[float]:
        """Cache embeddings for frequently used texts"""
        # This is a synchronous version for caching
        # In practice, you might want to use a more sophisticated caching mechanism
        pass
    
    def get_embedding_info(self) -> Dict[str, Any]:
        """Get information about the current embedding configuration"""
        return {
            'provider': self.embedding_provider,
            'model_name': self.model_name,
            'embedding_dimension': self.embedding_dimension,
            'max_sequence_length': getattr(self.model, 'max_seq_length', 'unknown') if hasattr(self, 'model') else 'unknown'
        }
    
    async def health_check(self) -> bool:
        """Check if the embedding service is working correctly"""
        try:
            test_text = "This is a test sentence for health check."
            embedding = await self.generate_embedding(test_text)
            
            # Verify embedding has correct dimension and is not all zeros
            if len(embedding) == self.embedding_dimension and any(x != 0 for x in embedding):
                return True
            else:
                logger.error("Health check failed: Invalid embedding generated")
                return False
                
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False
