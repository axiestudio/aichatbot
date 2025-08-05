from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import StreamingResponse
from typing import List, Optional, Dict, Any
import logging
import json
from datetime import datetime

from app.models.document import (
    Document, DocumentUploadRequest, DocumentUploadResponse,
    DocumentProcessRequest, DocumentProcessResponse,
    DocumentSearchRequest, DocumentSearchResponse,
    DocumentListRequest, DocumentListResponse,
    DocumentUpdateRequest, DocumentDeleteRequest, DocumentDeleteResponse,
    DocumentAnalytics, BulkDocumentOperation, BulkOperationResponse
)
from app.services.document_service import DocumentService
from app.core.dependencies import get_document_service
from app.middleware.security import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    config_id: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),  # JSON string of tags
    auto_process: bool = Form(True),
    chunk_size: int = Form(1000),
    chunk_overlap: int = Form(200),
    document_service: DocumentService = Depends(get_document_service),
    current_user: Optional[str] = Depends(get_current_user)
):
    """Upload a document for RAG processing"""
    try:
        # Parse tags if provided
        parsed_tags = None
        if tags:
            try:
                parsed_tags = json.loads(tags)
            except json.JSONDecodeError:
                parsed_tags = [tag.strip() for tag in tags.split(',')]
        
        # Create upload request
        upload_request = DocumentUploadRequest(
            config_id=config_id,
            tags=parsed_tags,
            auto_process=auto_process,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        
        # Upload document
        response = await document_service.upload_document(file, upload_request)
        
        logger.info(f"Document uploaded by user {current_user}: {response.document_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/process", response_model=DocumentProcessResponse)
async def process_document(
    request: DocumentProcessRequest,
    document_service: DocumentService = Depends(get_document_service),
    current_user: Optional[str] = Depends(get_current_user)
):
    """Process a document for RAG indexing"""
    try:
        response = await document_service.process_document(request)
        logger.info(f"Document processed by user {current_user}: {request.document_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@router.post("/search", response_model=DocumentSearchResponse)
async def search_documents(
    request: DocumentSearchRequest,
    document_service: DocumentService = Depends(get_document_service)
):
    """Search through processed documents"""
    try:
        response = await document_service.search_documents(request)
        logger.info(f"Document search performed: '{request.query}' - {response.total_results} results")
        return response
        
    except Exception as e:
        logger.error(f"Error searching documents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    config_id: Optional[str] = None,
    status: Optional[str] = None,
    tags: Optional[str] = None,  # Comma-separated tags
    search: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    document_service: DocumentService = Depends(get_document_service)
):
    """List documents with filtering and pagination"""
    try:
        # Parse tags if provided
        parsed_tags = None
        if tags:
            parsed_tags = [tag.strip() for tag in tags.split(',')]
        
        # Create list request
        list_request = DocumentListRequest(
            config_id=config_id,
            status=status,
            tags=parsed_tags,
            search=search,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        response = await document_service.list_documents(list_request)
        return response
        
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Listing failed: {str(e)}")


@router.get("/{document_id}", response_model=Document)
async def get_document(
    document_id: str,
    document_service: DocumentService = Depends(get_document_service)
):
    """Get a specific document by ID"""
    try:
        document = await document_service.get_document(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return document
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document {document_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get document: {str(e)}")


@router.put("/{document_id}", response_model=Document)
async def update_document(
    document_id: str,
    request: DocumentUpdateRequest,
    document_service: DocumentService = Depends(get_document_service),
    current_user: Optional[str] = Depends(get_current_user)
):
    """Update document metadata"""
    try:
        document = await document_service.get_document(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Update fields if provided
        if request.filename is not None:
            document.filename = request.filename
        if request.tags is not None:
            document.tags = request.tags
        if request.metadata is not None:
            if document.metadata:
                document.metadata.__dict__.update(request.metadata)
            else:
                document.metadata = request.metadata
        if request.is_active is not None:
            document.is_active = request.is_active
        
        document.updated_at = datetime.utcnow()
        
        logger.info(f"Document updated by user {current_user}: {document_id}")
        return document
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating document {document_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    document_service: DocumentService = Depends(get_document_service),
    current_user: Optional[str] = Depends(get_current_user)
):
    """Delete a document"""
    try:
        success = await document_service.delete_document(document_id)
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        
        logger.info(f"Document deleted by user {current_user}: {document_id}")
        return {"message": "Document deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document {document_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}")


@router.post("/bulk-delete", response_model=DocumentDeleteResponse)
async def bulk_delete_documents(
    request: DocumentDeleteRequest,
    document_service: DocumentService = Depends(get_document_service),
    current_user: Optional[str] = Depends(get_current_user)
):
    """Delete multiple documents"""
    try:
        deleted_count = 0
        failed_count = 0
        errors = []
        
        for document_id in request.document_ids:
            try:
                success = await document_service.delete_document(document_id)
                if success:
                    deleted_count += 1
                else:
                    failed_count += 1
                    errors.append(f"Document {document_id} not found")
            except Exception as e:
                failed_count += 1
                errors.append(f"Error deleting {document_id}: {str(e)}")
        
        logger.info(f"Bulk delete by user {current_user}: {deleted_count} deleted, {failed_count} failed")
        
        return DocumentDeleteResponse(
            deleted_count=deleted_count,
            failed_count=failed_count,
            errors=errors if errors else None,
            message=f"Deleted {deleted_count} documents, {failed_count} failed"
        )
        
    except Exception as e:
        logger.error(f"Error in bulk delete: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Bulk delete failed: {str(e)}")


@router.get("/analytics/summary", response_model=DocumentAnalytics)
async def get_document_analytics(
    document_service: DocumentService = Depends(get_document_service)
):
    """Get document analytics and statistics"""
    try:
        analytics = await document_service.get_analytics()
        return analytics
        
    except Exception as e:
        logger.error(f"Error getting document analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analytics failed: {str(e)}")


@router.get("/{document_id}/download")
async def download_document(
    document_id: str,
    document_service: DocumentService = Depends(get_document_service)
):
    """Download a document file"""
    try:
        document = await document_service.get_document(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Get file content from storage
        file_content = await document_service.storage_service.retrieve_file(document.file_path)
        if not file_content:
            raise HTTPException(status_code=404, detail="File not found in storage")
        
        # Create streaming response
        def generate():
            yield file_content
        
        return StreamingResponse(
            generate(),
            media_type=document.mime_type,
            headers={
                "Content-Disposition": f"attachment; filename={document.original_filename}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading document {document_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")


@router.post("/bulk-operation", response_model=BulkOperationResponse)
async def bulk_document_operation(
    request: BulkDocumentOperation,
    background_tasks: BackgroundTasks,
    document_service: DocumentService = Depends(get_document_service),
    current_user: Optional[str] = Depends(get_current_user)
):
    """Perform bulk operations on documents"""
    try:
        if request.operation == "process":
            # Process multiple documents
            successful = 0
            failed = 0
            errors = []
            
            for document_id in request.document_ids:
                try:
                    process_request = DocumentProcessRequest(
                        document_id=document_id,
                        chunk_size=request.parameters.get('chunk_size', 1000),
                        chunk_overlap=request.parameters.get('chunk_overlap', 200),
                        generate_embeddings=request.parameters.get('generate_embeddings', True),
                        extract_metadata=request.parameters.get('extract_metadata', True)
                    )
                    await document_service.process_document(process_request)
                    successful += 1
                except Exception as e:
                    failed += 1
                    errors.append(f"Error processing {document_id}: {str(e)}")
            
            return BulkOperationResponse(
                operation=request.operation,
                total_documents=len(request.document_ids),
                successful=successful,
                failed=failed,
                errors=errors if errors else None
            )
        
        elif request.operation == "delete":
            # Delete multiple documents
            delete_request = DocumentDeleteRequest(
                document_ids=request.document_ids,
                delete_files=request.parameters.get('delete_files', True),
                delete_chunks=request.parameters.get('delete_chunks', True)
            )
            response = await bulk_delete_documents(delete_request, document_service, current_user)
            
            return BulkOperationResponse(
                operation=request.operation,
                total_documents=len(request.document_ids),
                successful=response.deleted_count,
                failed=response.failed_count,
                errors=response.errors
            )
        
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported operation: {request.operation}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in bulk operation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Bulk operation failed: {str(e)}")


@router.get("/{document_id}/chunks")
async def get_document_chunks(
    document_id: str,
    limit: int = 50,
    offset: int = 0,
    document_service: DocumentService = Depends(get_document_service)
):
    """Get chunks for a specific document"""
    try:
        document = await document_service.get_document(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        chunks = document_service.chunks.get(document_id, [])
        
        # Apply pagination
        total = len(chunks)
        paginated_chunks = chunks[offset:offset + limit]
        
        return {
            "document_id": document_id,
            "chunks": paginated_chunks,
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting chunks for document {document_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get chunks: {str(e)}")


@router.post("/{document_id}/reprocess")
async def reprocess_document(
    document_id: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    generate_embeddings: bool = True,
    document_service: DocumentService = Depends(get_document_service),
    current_user: Optional[str] = Depends(get_current_user)
):
    """Reprocess a document with new parameters"""
    try:
        document = await document_service.get_document(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Create reprocess request
        process_request = DocumentProcessRequest(
            document_id=document_id,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            generate_embeddings=generate_embeddings,
            extract_metadata=True
        )
        
        response = await document_service.process_document(process_request)
        
        logger.info(f"Document reprocessed by user {current_user}: {document_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reprocessing document {document_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Reprocessing failed: {str(e)}")
