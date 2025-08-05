from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum
import uuid


class DocumentType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    MD = "md"
    HTML = "html"
    CSV = "csv"
    XLSX = "xlsx"
    JSON = "json"


class DocumentStatus(str, Enum):
    UPLOADING = "uploading"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
    INDEXED = "indexed"
    ERROR = "error"


class DocumentChunk(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    document_id: str
    content: str = Field(..., min_length=1, max_length=8000)
    chunk_index: int = Field(..., ge=0)
    start_char: int = Field(..., ge=0)
    end_char: int = Field(..., ge=0)
    metadata: Optional[Dict[str, Any]] = None
    embedding: Optional[List[float]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DocumentMetadata(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    subject: Optional[str] = None
    keywords: Optional[List[str]] = None
    language: Optional[str] = "en"
    page_count: Optional[int] = None
    word_count: Optional[int] = None
    char_count: Optional[int] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    encoding: Optional[str] = None
    created_date: Optional[datetime] = None
    modified_date: Optional[datetime] = None


class Document(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str = Field(..., min_length=1, max_length=255)
    original_filename: str = Field(..., min_length=1, max_length=255)
    file_path: str = Field(..., min_length=1)
    file_size: int = Field(..., gt=0)
    file_type: DocumentType
    mime_type: str
    status: DocumentStatus = DocumentStatus.UPLOADING
    content: Optional[str] = None
    metadata: Optional[DocumentMetadata] = None
    chunks: Optional[List[DocumentChunk]] = None
    chunk_count: int = 0
    processing_error: Optional[str] = None
    config_id: Optional[str] = None
    uploaded_by: Optional[str] = None
    tags: Optional[List[str]] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None

    @validator('file_type', pre=True)
    def validate_file_type(cls, v, values):
        if isinstance(v, str):
            return DocumentType(v.lower())
        return v

    @validator('filename')
    def validate_filename(cls, v):
        # Remove any path separators for security
        return v.replace('/', '_').replace('\\', '_').replace('..', '_')


class DocumentUploadRequest(BaseModel):
    config_id: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    auto_process: bool = True
    chunk_size: int = Field(default=1000, ge=100, le=4000)
    chunk_overlap: int = Field(default=200, ge=0, le=1000)


class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    file_size: int
    status: DocumentStatus
    message: str
    upload_url: Optional[str] = None


class DocumentProcessRequest(BaseModel):
    document_id: str
    chunk_size: int = Field(default=1000, ge=100, le=4000)
    chunk_overlap: int = Field(default=200, ge=0, le=1000)
    generate_embeddings: bool = True
    extract_metadata: bool = True


class DocumentProcessResponse(BaseModel):
    document_id: str
    status: DocumentStatus
    chunk_count: int
    processing_time: Optional[float] = None
    message: str
    error: Optional[str] = None


class DocumentSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    config_id: Optional[str] = None
    document_ids: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    limit: int = Field(default=10, ge=1, le=50)
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    include_metadata: bool = True


class DocumentSearchResult(BaseModel):
    chunk_id: str
    document_id: str
    document_title: str
    content: str
    similarity_score: float
    chunk_index: int
    metadata: Optional[Dict[str, Any]] = None


class DocumentSearchResponse(BaseModel):
    query: str
    results: List[DocumentSearchResult]
    total_results: int
    search_time: float
    metadata: Optional[Dict[str, Any]] = None


class DocumentListRequest(BaseModel):
    config_id: Optional[str] = None
    status: Optional[DocumentStatus] = None
    tags: Optional[List[str]] = None
    search: Optional[str] = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    sort_by: str = Field(default="created_at")
    sort_order: str = Field(default="desc", regex="^(asc|desc)$")


class DocumentListResponse(BaseModel):
    documents: List[Document]
    total: int
    limit: int
    offset: int
    has_more: bool


class DocumentUpdateRequest(BaseModel):
    filename: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class DocumentDeleteRequest(BaseModel):
    document_ids: List[str] = Field(..., min_items=1)
    delete_files: bool = True
    delete_chunks: bool = True


class DocumentDeleteResponse(BaseModel):
    deleted_count: int
    failed_count: int
    errors: Optional[List[str]] = None
    message: str


class DocumentAnalytics(BaseModel):
    total_documents: int
    total_size: int
    documents_by_type: Dict[str, int]
    documents_by_status: Dict[str, int]
    average_processing_time: Optional[float] = None
    total_chunks: int
    storage_usage: Dict[str, Any]


class BulkDocumentOperation(BaseModel):
    operation: str = Field(..., regex="^(process|delete|reindex|update_tags)$")
    document_ids: List[str] = Field(..., min_items=1)
    parameters: Optional[Dict[str, Any]] = None


class BulkOperationResponse(BaseModel):
    operation: str
    total_documents: int
    successful: int
    failed: int
    errors: Optional[List[str]] = None
    task_id: Optional[str] = None
    estimated_completion: Optional[datetime] = None
