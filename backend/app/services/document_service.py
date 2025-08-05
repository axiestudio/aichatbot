import os
import uuid
import asyncio
import aiofiles
import mimetypes
from typing import List, Optional, Dict, Any, BinaryIO
from datetime import datetime
import logging
from pathlib import Path

from fastapi import UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import (
    Document, DocumentChunk, DocumentMetadata, DocumentType, DocumentStatus,
    DocumentUploadRequest, DocumentUploadResponse, DocumentProcessRequest,
    DocumentProcessResponse, DocumentSearchRequest, DocumentSearchResponse,
    DocumentListRequest, DocumentListResponse, DocumentAnalytics
)
from app.services.file_processor import FileProcessor
from app.services.embedding_service import EmbeddingService
from app.services.storage_service import StorageService
from app.core.config import settings

logger = logging.getLogger(__name__)


class DocumentService:
    """Service for managing document upload, processing, and retrieval"""
    
    def __init__(self):
        self.file_processor = FileProcessor()
        self.embedding_service = EmbeddingService()
        self.storage_service = StorageService()
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(exist_ok=True)
        
        # In-memory storage for demo - replace with database in production
        self.documents: Dict[str, Document] = {}
        self.chunks: Dict[str, List[DocumentChunk]] = {}
    
    async def upload_document(
        self, 
        file: UploadFile, 
        request: DocumentUploadRequest
    ) -> DocumentUploadResponse:
        """Upload and optionally process a document"""
        try:
            # Validate file
            await self._validate_upload(file)
            
            # Generate document ID and file path
            document_id = str(uuid.uuid4())
            file_extension = Path(file.filename).suffix.lower()
            safe_filename = f"{document_id}{file_extension}"
            file_path = self.upload_dir / safe_filename
            
            # Determine file type
            file_type = self._get_file_type(file.filename, file.content_type)
            
            # Save file to disk
            file_size = await self._save_uploaded_file(file, file_path)
            
            # Create document record
            document = Document(
                id=document_id,
                filename=safe_filename,
                original_filename=file.filename,
                file_path=str(file_path),
                file_size=file_size,
                file_type=file_type,
                mime_type=file.content_type or "application/octet-stream",
                status=DocumentStatus.UPLOADING,
                config_id=request.config_id,
                tags=request.tags,
                created_at=datetime.utcnow()
            )
            
            # Store document
            self.documents[document_id] = document
            
            # Auto-process if requested
            if request.auto_process:
                asyncio.create_task(self._process_document_async(
                    document_id, 
                    request.chunk_size, 
                    request.chunk_overlap
                ))
                document.status = DocumentStatus.PROCESSING
            
            logger.info(f"Document uploaded successfully: {document_id}")
            
            return DocumentUploadResponse(
                document_id=document_id,
                filename=file.filename,
                file_size=file_size,
                status=document.status,
                message="Document uploaded successfully"
            )
            
        except Exception as e:
            logger.error(f"Error uploading document: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
    
    async def process_document(
        self, 
        request: DocumentProcessRequest
    ) -> DocumentProcessResponse:
        """Process a document for RAG indexing"""
        try:
            document = self.documents.get(request.document_id)
            if not document:
                raise HTTPException(status_code=404, detail="Document not found")
            
            if document.status == DocumentStatus.PROCESSING:
                return DocumentProcessResponse(
                    document_id=request.document_id,
                    status=DocumentStatus.PROCESSING,
                    chunk_count=0,
                    message="Document is already being processed"
                )
            
            start_time = datetime.utcnow()
            document.status = DocumentStatus.PROCESSING
            
            try:
                # Extract text content
                content = await self.file_processor.extract_text(
                    document.file_path, 
                    document.file_type
                )
                
                # Extract metadata if requested
                if request.extract_metadata:
                    metadata = await self.file_processor.extract_metadata(
                        document.file_path, 
                        document.file_type
                    )
                    document.metadata = metadata
                
                # Chunk the content
                chunks = await self.file_processor.chunk_text(
                    content,
                    chunk_size=request.chunk_size,
                    chunk_overlap=request.chunk_overlap,
                    document_id=request.document_id
                )
                
                # Generate embeddings if requested
                if request.generate_embeddings:
                    for chunk in chunks:
                        chunk.embedding = await self.embedding_service.generate_embedding(
                            chunk.content
                        )
                
                # Store chunks
                self.chunks[request.document_id] = chunks
                document.chunks = chunks
                document.chunk_count = len(chunks)
                document.content = content
                document.status = DocumentStatus.PROCESSED
                document.processed_at = datetime.utcnow()
                
                processing_time = (datetime.utcnow() - start_time).total_seconds()
                
                logger.info(f"Document processed successfully: {request.document_id}")
                
                return DocumentProcessResponse(
                    document_id=request.document_id,
                    status=DocumentStatus.PROCESSED,
                    chunk_count=len(chunks),
                    processing_time=processing_time,
                    message="Document processed successfully"
                )
                
            except Exception as e:
                document.status = DocumentStatus.FAILED
                document.processing_error = str(e)
                logger.error(f"Error processing document {request.document_id}: {str(e)}")
                
                return DocumentProcessResponse(
                    document_id=request.document_id,
                    status=DocumentStatus.FAILED,
                    chunk_count=0,
                    message="Document processing failed",
                    error=str(e)
                )
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in process_document: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
    
    async def search_documents(
        self, 
        request: DocumentSearchRequest
    ) -> DocumentSearchResponse:
        """Search through processed documents"""
        try:
            start_time = datetime.utcnow()
            
            # Generate query embedding
            query_embedding = await self.embedding_service.generate_embedding(request.query)
            
            # Search through chunks
            results = []
            for doc_id, chunks in self.chunks.items():
                document = self.documents.get(doc_id)
                if not document or not document.is_active:
                    continue
                
                # Filter by document IDs if specified
                if request.document_ids and doc_id not in request.document_ids:
                    continue
                
                # Filter by config ID if specified
                if request.config_id and document.config_id != request.config_id:
                    continue
                
                # Filter by tags if specified
                if request.tags and not any(tag in (document.tags or []) for tag in request.tags):
                    continue
                
                # Calculate similarity for each chunk
                for chunk in chunks:
                    if chunk.embedding:
                        similarity = self.embedding_service.calculate_similarity(
                            query_embedding, 
                            chunk.embedding
                        )
                        
                        if similarity >= request.similarity_threshold:
                            results.append({
                                'chunk_id': chunk.id,
                                'document_id': doc_id,
                                'document_title': document.original_filename,
                                'content': chunk.content,
                                'similarity_score': similarity,
                                'chunk_index': chunk.chunk_index,
                                'metadata': chunk.metadata if request.include_metadata else None
                            })
            
            # Sort by similarity score
            results.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            # Limit results
            results = results[:request.limit]
            
            search_time = (datetime.utcnow() - start_time).total_seconds()
            
            return DocumentSearchResponse(
                query=request.query,
                results=results,
                total_results=len(results),
                search_time=search_time
            )
            
        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
    
    async def list_documents(
        self, 
        request: DocumentListRequest
    ) -> DocumentListResponse:
        """List documents with filtering and pagination"""
        try:
            # Filter documents
            filtered_docs = []
            for document in self.documents.values():
                # Apply filters
                if request.config_id and document.config_id != request.config_id:
                    continue
                if request.status and document.status != request.status:
                    continue
                if request.tags and not any(tag in (document.tags or []) for tag in request.tags):
                    continue
                if request.search and request.search.lower() not in document.original_filename.lower():
                    continue
                
                filtered_docs.append(document)
            
            # Sort documents
            reverse = request.sort_order == "desc"
            filtered_docs.sort(
                key=lambda x: getattr(x, request.sort_by, x.created_at), 
                reverse=reverse
            )
            
            # Paginate
            total = len(filtered_docs)
            start = request.offset
            end = start + request.limit
            paginated_docs = filtered_docs[start:end]
            
            return DocumentListResponse(
                documents=paginated_docs,
                total=total,
                limit=request.limit,
                offset=request.offset,
                has_more=end < total
            )
            
        except Exception as e:
            logger.error(f"Error listing documents: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Listing failed: {str(e)}")
    
    async def get_document(self, document_id: str) -> Optional[Document]:
        """Get a document by ID"""
        return self.documents.get(document_id)
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete a document and its associated data"""
        try:
            document = self.documents.get(document_id)
            if not document:
                return False
            
            # Delete file from disk
            try:
                os.remove(document.file_path)
            except FileNotFoundError:
                pass
            
            # Delete chunks
            if document_id in self.chunks:
                del self.chunks[document_id]
            
            # Delete document record
            del self.documents[document_id]
            
            logger.info(f"Document deleted: {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {str(e)}")
            return False
    
    async def get_analytics(self) -> DocumentAnalytics:
        """Get document analytics"""
        try:
            total_documents = len(self.documents)
            total_size = sum(doc.file_size for doc in self.documents.values())
            
            # Count by type
            by_type = {}
            for doc in self.documents.values():
                doc_type = doc.file_type.value
                by_type[doc_type] = by_type.get(doc_type, 0) + 1
            
            # Count by status
            by_status = {}
            for doc in self.documents.values():
                status = doc.status.value
                by_status[status] = by_status.get(status, 0) + 1
            
            # Calculate total chunks
            total_chunks = sum(len(chunks) for chunks in self.chunks.values())
            
            return DocumentAnalytics(
                total_documents=total_documents,
                total_size=total_size,
                documents_by_type=by_type,
                documents_by_status=by_status,
                total_chunks=total_chunks,
                storage_usage={
                    "disk_usage": total_size,
                    "upload_dir": str(self.upload_dir)
                }
            )
            
        except Exception as e:
            logger.error(f"Error getting analytics: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Analytics failed: {str(e)}")
    
    # Private helper methods
    
    async def _validate_upload(self, file: UploadFile):
        """Validate uploaded file"""
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        # Check file size
        if hasattr(file, 'size') and file.size > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=413, 
                detail=f"File too large. Max size: {settings.MAX_UPLOAD_SIZE} bytes"
            )
        
        # Check file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400, 
                detail=f"File type not allowed. Allowed: {settings.ALLOWED_EXTENSIONS}"
            )
    
    def _get_file_type(self, filename: str, content_type: str) -> DocumentType:
        """Determine file type from filename and content type"""
        file_ext = Path(filename).suffix.lower()
        
        type_mapping = {
            '.pdf': DocumentType.PDF,
            '.docx': DocumentType.DOCX,
            '.doc': DocumentType.DOCX,
            '.txt': DocumentType.TXT,
            '.md': DocumentType.MD,
            '.html': DocumentType.HTML,
            '.htm': DocumentType.HTML,
            '.csv': DocumentType.CSV,
            '.xlsx': DocumentType.XLSX,
            '.xls': DocumentType.XLSX,
            '.json': DocumentType.JSON
        }
        
        return type_mapping.get(file_ext, DocumentType.TXT)
    
    async def _save_uploaded_file(self, file: UploadFile, file_path: Path) -> int:
        """Save uploaded file to disk and return file size"""
        file_size = 0
        async with aiofiles.open(file_path, 'wb') as f:
            while chunk := await file.read(8192):
                await f.write(chunk)
                file_size += len(chunk)
        return file_size
    
    async def _process_document_async(
        self, 
        document_id: str, 
        chunk_size: int, 
        chunk_overlap: int
    ):
        """Process document asynchronously"""
        try:
            request = DocumentProcessRequest(
                document_id=document_id,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                generate_embeddings=True,
                extract_metadata=True
            )
            await self.process_document(request)
        except Exception as e:
            logger.error(f"Async processing failed for {document_id}: {str(e)}")
            if document_id in self.documents:
                self.documents[document_id].status = DocumentStatus.FAILED
                self.documents[document_id].processing_error = str(e)
