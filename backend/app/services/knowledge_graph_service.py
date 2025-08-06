"""
Advanced Knowledge Graph Service
Dynamic knowledge extraction, entity linking, and semantic understanding
"""

import asyncio
import logging
import json
import re
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
import hashlib

from .cache_service import cache_service
from ..core.database import get_db
from ..models.database import ChatMessage, Document

logger = logging.getLogger(__name__)


@dataclass
class Entity:
    entity_id: str
    name: str
    entity_type: str
    confidence: float
    aliases: List[str]
    properties: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


@dataclass
class Relationship:
    relationship_id: str
    source_entity_id: str
    target_entity_id: str
    relationship_type: str
    confidence: float
    properties: Dict[str, Any]
    created_at: datetime


@dataclass
class KnowledgeNode:
    node_id: str
    entity: Entity
    relationships: List[Relationship]
    context_score: float
    relevance_score: float
    last_accessed: datetime


class KnowledgeGraphService:
    """Advanced knowledge graph for semantic understanding and entity management"""
    
    def __init__(self):
        self.entities = {}  # entity_id -> Entity
        self.relationships = {}  # relationship_id -> Relationship
        self.entity_index = defaultdict(set)  # entity_type -> set of entity_ids
        self.name_index = defaultdict(set)  # normalized_name -> set of entity_ids
        self.knowledge_cache = {}
        self.extraction_patterns = {}
        
        # Entity types and patterns
        self.entity_patterns = {
            "person": [
                r"\b([A-Z][a-z]+ [A-Z][a-z]+)\b",  # First Last
                r"\b(Mr\.|Mrs\.|Dr\.|Prof\.)\s+([A-Z][a-z]+)\b"
            ],
            "organization": [
                r"\b([A-Z][a-z]+ (?:Inc|Corp|LLC|Ltd|Company|Corporation))\b",
                r"\b(Microsoft|Google|Apple|Amazon|Meta|OpenAI|Anthropic)\b"
            ],
            "location": [
                r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,\s*[A-Z]{2})\b",  # City, State
                r"\b(New York|Los Angeles|Chicago|Houston|Phoenix)\b"
            ],
            "technology": [
                r"\b(Python|JavaScript|React|Node\.js|Docker|Kubernetes)\b",
                r"\b(API|REST|GraphQL|WebSocket|HTTP|HTTPS)\b"
            ],
            "concept": [
                r"\b(machine learning|artificial intelligence|deep learning)\b",
                r"\b(blockchain|cryptocurrency|cloud computing)\b"
            ],
            "product": [
                r"\b(iPhone|Android|Windows|macOS|Linux)\b",
                r"\b(ChatGPT|Claude|Bard|Copilot)\b"
            ]
        }
        
        # Relationship patterns
        self.relationship_patterns = {
            "works_at": [
                r"(\w+)\s+(?:works at|employed by|employee of)\s+(\w+)",
                r"(\w+)\s+is\s+(?:a|an)\s+\w+\s+at\s+(\w+)"
            ],
            "located_in": [
                r"(\w+)\s+(?:is located in|is in|located at)\s+(\w+)",
                r"(\w+),\s+(\w+)"  # City, State pattern
            ],
            "part_of": [
                r"(\w+)\s+(?:is part of|belongs to|is a component of)\s+(\w+)",
                r"(\w+)\s+(?:includes|contains|has)\s+(\w+)"
            ],
            "similar_to": [
                r"(\w+)\s+(?:is similar to|is like|resembles)\s+(\w+)",
                r"(\w+)\s+and\s+(\w+)\s+are\s+(?:similar|alike)"
            ],
            "created_by": [
                r"(\w+)\s+(?:was created by|was developed by|was made by)\s+(\w+)",
                r"(\w+)\s+(?:created|developed|made)\s+(\w+)"
            ]
        }
        
        # Semantic similarity cache
        self.similarity_cache = {}
        
        # Knowledge extraction statistics
        self.extraction_stats = {
            "entities_extracted": 0,
            "relationships_discovered": 0,
            "knowledge_queries": 0,
            "cache_hits": 0
        }
    
    async def start_knowledge_service(self):
        """Start knowledge graph service"""
        logger.info("🧠 Knowledge Graph Service started")
        asyncio.create_task(self._knowledge_processing_loop())
        asyncio.create_task(self._entity_linking_loop())
        asyncio.create_task(self._knowledge_optimization_loop())
    
    async def extract_knowledge_from_text(self, text: str, source_id: str = None) -> Dict[str, Any]:
        """Extract entities and relationships from text"""
        try:
            # Extract entities
            entities = await self._extract_entities(text)
            
            # Extract relationships
            relationships = await self._extract_relationships(text, entities)
            
            # Store in knowledge graph
            stored_entities = []
            stored_relationships = []
            
            for entity_data in entities:
                entity = await self._store_entity(entity_data, source_id)
                if entity:
                    stored_entities.append(entity)
            
            for rel_data in relationships:
                relationship = await self._store_relationship(rel_data, source_id)
                if relationship:
                    stored_relationships.append(relationship)
            
            # Update statistics
            self.extraction_stats["entities_extracted"] += len(stored_entities)
            self.extraction_stats["relationships_discovered"] += len(stored_relationships)
            
            return {
                "entities": [asdict(e) for e in stored_entities],
                "relationships": [asdict(r) for r in stored_relationships],
                "extraction_stats": {
                    "entities_found": len(entities),
                    "entities_stored": len(stored_entities),
                    "relationships_found": len(relationships),
                    "relationships_stored": len(stored_relationships)
                }
            }
            
        except Exception as e:
            logger.error(f"Error extracting knowledge: {e}")
            return {"error": str(e)}
    
    async def _extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract entities from text using pattern matching"""
        entities = []
        text_lower = text.lower()
        
        for entity_type, patterns in self.entity_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    entity_name = match.group(1) if match.groups() else match.group(0)
                    
                    # Calculate confidence based on pattern specificity
                    confidence = self._calculate_entity_confidence(entity_name, entity_type, text)
                    
                    entities.append({
                        "name": entity_name.strip(),
                        "type": entity_type,
                        "confidence": confidence,
                        "position": match.span(),
                        "context": text[max(0, match.start()-50):match.end()+50]
                    })
        
        # Remove duplicates and low-confidence entities
        entities = self._deduplicate_entities(entities)
        return [e for e in entities if e["confidence"] > 0.3]
    
    async def _extract_relationships(self, text: str, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract relationships between entities"""
        relationships = []
        
        # Create entity lookup
        entity_names = {e["name"].lower(): e for e in entities}
        
        for rel_type, patterns in self.relationship_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    if len(match.groups()) >= 2:
                        source_name = match.group(1).strip()
                        target_name = match.group(2).strip()
                        
                        # Check if both entities exist
                        source_entity = entity_names.get(source_name.lower())
                        target_entity = entity_names.get(target_name.lower())
                        
                        if source_entity and target_entity:
                            confidence = self._calculate_relationship_confidence(
                                source_name, target_name, rel_type, text
                            )
                            
                            relationships.append({
                                "source_name": source_name,
                                "target_name": target_name,
                                "type": rel_type,
                                "confidence": confidence,
                                "context": text[max(0, match.start()-50):match.end()+50]
                            })
        
        return relationships
    
    def _calculate_entity_confidence(self, entity_name: str, entity_type: str, context: str) -> float:
        """Calculate confidence score for entity extraction"""
        confidence = 0.5  # Base confidence
        
        # Length factor
        if len(entity_name) > 2:
            confidence += 0.1
        
        # Capitalization factor
        if entity_name[0].isupper():
            confidence += 0.1
        
        # Context factor
        if entity_type in context.lower():
            confidence += 0.2
        
        # Known entity factor
        if self._is_known_entity(entity_name, entity_type):
            confidence += 0.3
        
        return min(1.0, confidence)
    
    def _calculate_relationship_confidence(self, source: str, target: str, rel_type: str, context: str) -> float:
        """Calculate confidence score for relationship extraction"""
        confidence = 0.4  # Base confidence
        
        # Distance factor (closer entities are more likely related)
        source_pos = context.lower().find(source.lower())
        target_pos = context.lower().find(target.lower())
        
        if source_pos != -1 and target_pos != -1:
            distance = abs(source_pos - target_pos)
            if distance < 50:
                confidence += 0.3
            elif distance < 100:
                confidence += 0.2
        
        # Relationship type factor
        if rel_type in ["works_at", "located_in", "created_by"]:
            confidence += 0.2
        
        return min(1.0, confidence)
    
    def _deduplicate_entities(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate entities"""
        seen = set()
        unique_entities = []
        
        for entity in entities:
            key = (entity["name"].lower(), entity["type"])
            if key not in seen:
                seen.add(key)
                unique_entities.append(entity)
        
        return unique_entities
    
    def _is_known_entity(self, name: str, entity_type: str) -> bool:
        """Check if entity is already known in the graph"""
        normalized_name = name.lower().strip()
        return normalized_name in self.name_index
    
    async def _store_entity(self, entity_data: Dict[str, Any], source_id: str = None) -> Optional[Entity]:
        """Store entity in knowledge graph"""
        try:
            entity_name = entity_data["name"]
            entity_type = entity_data["type"]
            
            # Check if entity already exists
            existing_entity_id = self._find_existing_entity(entity_name, entity_type)
            
            if existing_entity_id:
                # Update existing entity
                entity = self.entities[existing_entity_id]
                entity.confidence = max(entity.confidence, entity_data["confidence"])
                entity.updated_at = datetime.utcnow()
                
                # Add new alias if different
                if entity_name not in entity.aliases:
                    entity.aliases.append(entity_name)
                
                return entity
            else:
                # Create new entity
                entity_id = hashlib.md5(f"{entity_name}_{entity_type}_{datetime.utcnow()}".encode()).hexdigest()
                
                entity = Entity(
                    entity_id=entity_id,
                    name=entity_name,
                    entity_type=entity_type,
                    confidence=entity_data["confidence"],
                    aliases=[entity_name],
                    properties={
                        "source_id": source_id,
                        "context": entity_data.get("context", ""),
                        "position": entity_data.get("position")
                    },
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                # Store entity
                self.entities[entity_id] = entity
                self.entity_index[entity_type].add(entity_id)
                self.name_index[entity_name.lower()].add(entity_id)
                
                return entity
                
        except Exception as e:
            logger.error(f"Error storing entity: {e}")
            return None
    
    async def _store_relationship(self, rel_data: Dict[str, Any], source_id: str = None) -> Optional[Relationship]:
        """Store relationship in knowledge graph"""
        try:
            source_name = rel_data["source_name"]
            target_name = rel_data["target_name"]
            rel_type = rel_data["type"]
            
            # Find entity IDs
            source_entity_id = self._find_existing_entity(source_name, None)
            target_entity_id = self._find_existing_entity(target_name, None)
            
            if not source_entity_id or not target_entity_id:
                return None
            
            # Check if relationship already exists
            existing_rel = self._find_existing_relationship(source_entity_id, target_entity_id, rel_type)
            if existing_rel:
                # Update confidence
                existing_rel.confidence = max(existing_rel.confidence, rel_data["confidence"])
                return existing_rel
            
            # Create new relationship
            rel_id = hashlib.md5(f"{source_entity_id}_{target_entity_id}_{rel_type}_{datetime.utcnow()}".encode()).hexdigest()
            
            relationship = Relationship(
                relationship_id=rel_id,
                source_entity_id=source_entity_id,
                target_entity_id=target_entity_id,
                relationship_type=rel_type,
                confidence=rel_data["confidence"],
                properties={
                    "source_id": source_id,
                    "context": rel_data.get("context", "")
                },
                created_at=datetime.utcnow()
            )
            
            self.relationships[rel_id] = relationship
            return relationship
            
        except Exception as e:
            logger.error(f"Error storing relationship: {e}")
            return None
    
    def _find_existing_entity(self, name: str, entity_type: str = None) -> Optional[str]:
        """Find existing entity by name and type"""
        normalized_name = name.lower().strip()
        
        if normalized_name in self.name_index:
            entity_ids = self.name_index[normalized_name]
            
            if entity_type:
                # Filter by type
                for entity_id in entity_ids:
                    entity = self.entities.get(entity_id)
                    if entity and entity.entity_type == entity_type:
                        return entity_id
            else:
                # Return first match
                return next(iter(entity_ids), None)
        
        return None
    
    def _find_existing_relationship(self, source_id: str, target_id: str, rel_type: str) -> Optional[Relationship]:
        """Find existing relationship"""
        for relationship in self.relationships.values():
            if (relationship.source_entity_id == source_id and 
                relationship.target_entity_id == target_id and 
                relationship.relationship_type == rel_type):
                return relationship
        return None
    
    async def query_knowledge(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Query knowledge graph"""
        try:
            self.extraction_stats["knowledge_queries"] += 1
            
            # Check cache first
            cache_key = f"knowledge_query_{hashlib.md5(query.encode()).hexdigest()}"
            cached_result = await cache_service.get(cache_key, "knowledge")
            
            if cached_result:
                self.extraction_stats["cache_hits"] += 1
                return cached_result
            
            query_lower = query.lower()
            results = {
                "entities": [],
                "relationships": [],
                "suggestions": []
            }
            
            # Search entities
            for entity in self.entities.values():
                if (query_lower in entity.name.lower() or 
                    any(query_lower in alias.lower() for alias in entity.aliases)):
                    
                    results["entities"].append({
                        "entity_id": entity.entity_id,
                        "name": entity.name,
                        "type": entity.entity_type,
                        "confidence": entity.confidence,
                        "aliases": entity.aliases
                    })
            
            # Search relationships
            for relationship in self.relationships.values():
                source_entity = self.entities.get(relationship.source_entity_id)
                target_entity = self.entities.get(relationship.target_entity_id)
                
                if source_entity and target_entity:
                    if (query_lower in source_entity.name.lower() or 
                        query_lower in target_entity.name.lower() or
                        query_lower in relationship.relationship_type):
                        
                        results["relationships"].append({
                            "relationship_id": relationship.relationship_id,
                            "source": source_entity.name,
                            "target": target_entity.name,
                            "type": relationship.relationship_type,
                            "confidence": relationship.confidence
                        })
            
            # Generate suggestions
            results["suggestions"] = self._generate_suggestions(query, results)
            
            # Limit results
            results["entities"] = results["entities"][:limit]
            results["relationships"] = results["relationships"][:limit]
            
            # Cache result
            await cache_service.set(cache_key, results, "knowledge", 3600)
            
            return results
            
        except Exception as e:
            logger.error(f"Error querying knowledge: {e}")
            return {"error": str(e)}
    
    def _generate_suggestions(self, query: str, results: Dict[str, Any]) -> List[str]:
        """Generate query suggestions based on knowledge graph"""
        suggestions = []
        
        # Suggest related entities
        for entity in results["entities"][:3]:
            suggestions.append(f"Tell me more about {entity['name']}")
            
            # Find related entities
            for relationship in self.relationships.values():
                if relationship.source_entity_id == entity["entity_id"]:
                    target_entity = self.entities.get(relationship.target_entity_id)
                    if target_entity:
                        suggestions.append(f"How is {entity['name']} related to {target_entity.name}?")
        
        return suggestions[:5]  # Limit to 5 suggestions
    
    async def get_entity_details(self, entity_id: str) -> Dict[str, Any]:
        """Get detailed information about an entity"""
        try:
            entity = self.entities.get(entity_id)
            if not entity:
                return {"error": "Entity not found"}
            
            # Find all relationships
            relationships = []
            for relationship in self.relationships.values():
                if (relationship.source_entity_id == entity_id or 
                    relationship.target_entity_id == entity_id):
                    
                    # Get related entity
                    related_entity_id = (relationship.target_entity_id 
                                       if relationship.source_entity_id == entity_id 
                                       else relationship.source_entity_id)
                    
                    related_entity = self.entities.get(related_entity_id)
                    if related_entity:
                        relationships.append({
                            "relationship_type": relationship.relationship_type,
                            "related_entity": {
                                "id": related_entity.entity_id,
                                "name": related_entity.name,
                                "type": related_entity.entity_type
                            },
                            "direction": "outgoing" if relationship.source_entity_id == entity_id else "incoming",
                            "confidence": relationship.confidence
                        })
            
            return {
                "entity": asdict(entity),
                "relationships": relationships,
                "relationship_count": len(relationships),
                "last_accessed": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting entity details: {e}")
            return {"error": str(e)}
    
    async def get_knowledge_stats(self) -> Dict[str, Any]:
        """Get knowledge graph statistics"""
        try:
            entity_type_counts = defaultdict(int)
            relationship_type_counts = defaultdict(int)
            
            for entity in self.entities.values():
                entity_type_counts[entity.entity_type] += 1
            
            for relationship in self.relationships.values():
                relationship_type_counts[relationship.relationship_type] += 1
            
            return {
                "total_entities": len(self.entities),
                "total_relationships": len(self.relationships),
                "entity_types": dict(entity_type_counts),
                "relationship_types": dict(relationship_type_counts),
                "extraction_stats": self.extraction_stats,
                "cache_size": len(self.knowledge_cache),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting knowledge stats: {e}")
            return {"error": str(e)}
    
    async def _knowledge_processing_loop(self):
        """Main knowledge processing loop"""
        while True:
            try:
                await self._process_pending_knowledge()
                await asyncio.sleep(300)  # Run every 5 minutes
            except Exception as e:
                logger.error(f"Knowledge processing error: {e}")
                await asyncio.sleep(600)
    
    async def _entity_linking_loop(self):
        """Entity linking and disambiguation loop"""
        while True:
            try:
                await self._link_similar_entities()
                await asyncio.sleep(1800)  # Run every 30 minutes
            except Exception as e:
                logger.error(f"Entity linking error: {e}")
                await asyncio.sleep(900)
    
    async def _knowledge_optimization_loop(self):
        """Knowledge graph optimization loop"""
        while True:
            try:
                await self._optimize_knowledge_graph()
                await asyncio.sleep(3600)  # Run every hour
            except Exception as e:
                logger.error(f"Knowledge optimization error: {e}")
                await asyncio.sleep(1800)
    
    async def _process_pending_knowledge(self):
        """Process pending knowledge extraction tasks"""
        # Implementation would process pending tasks
        pass
    
    async def _link_similar_entities(self):
        """Link similar entities and resolve duplicates"""
        # Implementation would link similar entities
        pass
    
    async def _optimize_knowledge_graph(self):
        """Optimize knowledge graph structure and performance"""
        # Implementation would optimize the graph
        pass


# Global knowledge graph service instance
knowledge_graph_service = KnowledgeGraphService()
