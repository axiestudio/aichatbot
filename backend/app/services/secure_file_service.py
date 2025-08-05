"""
Secure File Upload Service
Production-ready file handling with security scanning and validation
"""

import os
import hashlib
import mimetypes
import subprocess
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
import magic
from PIL import Image
import aiofiles
from fastapi import UploadFile, HTTPException

from app.core.config import settings
from app.services.error_tracking_service import error_tracker
from app.services.unified_monitoring_service import unified_monitoring

logger = logging.getLogger(__name__)


class SecureFileService:
    """Secure file upload and processing service"""
    
    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        
        # File type configurations
        self.allowed_extensions = {
            '.pdf': 'application/pdf',
            '.txt': 'text/plain',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.doc': 'application/msword',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.mp3': 'audio/mpeg',
            '.wav': 'audio/wav',
            '.ogg': 'audio/ogg'
        }
        
        # Security limits
        self.max_file_size = settings.MAX_FILE_SIZE  # 10MB default
        self.max_files_per_upload = 10
        self.quarantine_dir = self.upload_dir / "quarantine"
        self.quarantine_dir.mkdir(exist_ok=True)
    
    async def upload_files(
        self,
        files: List[UploadFile],
        user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Upload multiple files with security validation"""
        
        if len(files) > self.max_files_per_upload:
            raise HTTPException(
                status_code=400,
                detail=f"Too many files. Maximum {self.max_files_per_upload} files allowed"
            )
        
        results = []
        
        for file in files:
            try:
                result = await self.upload_single_file(file, user_id, session_id)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to upload file {file.filename}: {e}")
                results.append({
                    "filename": file.filename,
                    "status": "error",
                    "error": str(e)
                })
        
        return results
    
    async def upload_single_file(
        self,
        file: UploadFile,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Upload a single file with comprehensive security checks"""
        
        start_time = datetime.utcnow()
        
        try:
            # Basic validation
            if not file.filename:
                raise ValueError("No filename provided")
            
            # Check file size
            file_content = await file.read()
            if len(file_content) > self.max_file_size:
                raise ValueError(f"File too large. Maximum size: {self.max_file_size / 1024 / 1024:.1f}MB")
            
            # Reset file pointer
            await file.seek(0)
            
            # Validate file extension
            file_extension = Path(file.filename).suffix.lower()
            if file_extension not in self.allowed_extensions:
                raise ValueError(f"File type not allowed: {file_extension}")
            
            # Validate MIME type
            detected_mime = magic.from_buffer(file_content, mime=True)
            expected_mime = self.allowed_extensions[file_extension]
            
            if not self._is_mime_type_valid(detected_mime, expected_mime):
                raise ValueError(f"File content doesn't match extension. Detected: {detected_mime}")
            
            # Generate secure filename
            file_hash = hashlib.sha256(file_content).hexdigest()[:16]
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            secure_filename = f"{timestamp}_{file_hash}_{file.filename}"
            
            # Create user directory
            user_dir = self.upload_dir / (user_id or "anonymous")
            user_dir.mkdir(exist_ok=True)
            
            file_path = user_dir / secure_filename
            
            # Virus scan
            scan_result = await self._scan_file_content(file_content, file.filename)
            if not scan_result["safe"]:
                # Move to quarantine
                quarantine_path = self.quarantine_dir / secure_filename
                async with aiofiles.open(quarantine_path, 'wb') as f:
                    await f.write(file_content)
                
                logger.warning(f"File quarantined: {file.filename} - {scan_result['reason']}")
                raise ValueError(f"File failed security scan: {scan_result['reason']}")
            
            # Additional validation for images
            if file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                await self._validate_image(file_content)
            
            # Save file
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(file_content)
            
            # Generate file metadata
            file_metadata = {
                "original_filename": file.filename,
                "secure_filename": secure_filename,
                "file_path": str(file_path),
                "file_size": len(file_content),
                "mime_type": detected_mime,
                "file_hash": file_hash,
                "upload_timestamp": start_time.isoformat(),
                "user_id": user_id,
                "session_id": session_id,
                "scan_result": scan_result
            }
            
            # Track upload metrics
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            unified_monitoring.track_business_metric(
                "file_uploads",
                1,
                {
                    "file_type": file_extension,
                    "file_size_mb": len(file_content) / 1024 / 1024,
                    "processing_time": processing_time,
                    "user_id": user_id or "anonymous"
                }
            )
            
            logger.info(f"File uploaded successfully: {file.filename} -> {secure_filename}")
            
            return {
                "status": "success",
                "filename": file.filename,
                "secure_filename": secure_filename,
                "file_id": file_hash,
                "file_size": len(file_content),
                "mime_type": detected_mime,
                "upload_url": f"/api/v1/files/{file_hash}",
                "metadata": file_metadata
            }
            
        except Exception as e:
            # Track upload errors
            error_tracker.track_error(
                e,
                context={
                    "operation": "file_upload",
                    "filename": file.filename,
                    "user_id": user_id,
                    "session_id": session_id
                },
                severity="warning"
            )
            
            raise HTTPException(status_code=400, detail=str(e))
    
    async def _scan_file_content(self, content: bytes, filename: str) -> Dict[str, Any]:
        """Scan file content for malware and threats"""
        
        try:
            # Basic content analysis
            scan_result = {
                "safe": True,
                "reason": None,
                "scanner": "basic",
                "scan_time": datetime.utcnow().isoformat()
            }
            
            # Check for suspicious patterns
            suspicious_patterns = [
                b'<script',
                b'javascript:',
                b'vbscript:',
                b'onload=',
                b'onerror=',
                b'eval(',
                b'document.write',
                b'<?php',
                b'<%',
                b'exec(',
                b'system(',
                b'shell_exec'
            ]
            
            content_lower = content.lower()
            for pattern in suspicious_patterns:
                if pattern in content_lower:
                    scan_result["safe"] = False
                    scan_result["reason"] = f"Suspicious pattern detected: {pattern.decode('utf-8', errors='ignore')}"
                    break
            
            # Check file size anomalies
            if len(content) == 0:
                scan_result["safe"] = False
                scan_result["reason"] = "Empty file"
            
            # Additional checks for executables
            if content.startswith(b'MZ') or content.startswith(b'\x7fELF'):
                scan_result["safe"] = False
                scan_result["reason"] = "Executable file detected"
            
            # ClamAV integration (if available)
            if self._is_clamav_available():
                clamav_result = await self._scan_with_clamav(content)
                if not clamav_result["safe"]:
                    scan_result.update(clamav_result)
            
            return scan_result
            
        except Exception as e:
            logger.error(f"File scan error: {e}")
            return {
                "safe": False,
                "reason": f"Scan error: {str(e)}",
                "scanner": "error"
            }
    
    def _is_clamav_available(self) -> bool:
        """Check if ClamAV is available for scanning"""
        try:
            result = subprocess.run(['clamdscan', '--version'], 
                                  capture_output=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    async def _scan_with_clamav(self, content: bytes) -> Dict[str, Any]:
        """Scan file content with ClamAV"""
        try:
            # Write content to temporary file
            temp_file = self.upload_dir / f"temp_scan_{datetime.utcnow().timestamp()}"
            
            async with aiofiles.open(temp_file, 'wb') as f:
                await f.write(content)
            
            # Run ClamAV scan
            result = subprocess.run(
                ['clamdscan', '--no-summary', str(temp_file)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Clean up temp file
            temp_file.unlink(missing_ok=True)
            
            if result.returncode == 0:
                return {"safe": True, "scanner": "clamav"}
            else:
                return {
                    "safe": False,
                    "reason": f"ClamAV detected threat: {result.stdout.strip()}",
                    "scanner": "clamav"
                }
                
        except Exception as e:
            logger.error(f"ClamAV scan error: {e}")
            return {
                "safe": False,
                "reason": f"ClamAV scan failed: {str(e)}",
                "scanner": "clamav_error"
            }
    
    async def _validate_image(self, content: bytes):
        """Validate image files for additional security"""
        try:
            # Use PIL to validate image
            from io import BytesIO
            image = Image.open(BytesIO(content))
            
            # Verify image can be processed
            image.verify()
            
            # Check for reasonable dimensions
            if hasattr(image, 'size'):
                width, height = image.size
                if width > 10000 or height > 10000:
                    raise ValueError("Image dimensions too large")
                if width < 1 or height < 1:
                    raise ValueError("Invalid image dimensions")
            
        except Exception as e:
            raise ValueError(f"Invalid image file: {str(e)}")
    
    def _is_mime_type_valid(self, detected: str, expected: str) -> bool:
        """Check if detected MIME type matches expected"""
        # Handle common variations
        mime_variations = {
            'application/pdf': ['application/pdf'],
            'text/plain': ['text/plain', 'text/x-python', 'text/x-script'],
            'image/jpeg': ['image/jpeg', 'image/jpg'],
            'image/png': ['image/png'],
            'audio/mpeg': ['audio/mpeg', 'audio/mp3'],
            'audio/wav': ['audio/wav', 'audio/x-wav']
        }
        
        allowed_types = mime_variations.get(expected, [expected])
        return detected in allowed_types
    
    async def get_file(self, file_id: str, user_id: Optional[str] = None) -> Tuple[Path, Dict[str, Any]]:
        """Get file by ID with access control"""
        try:
            # In a real implementation, this would query the database
            # For now, we'll simulate file lookup
            user_dir = self.upload_dir / (user_id or "anonymous")

            # Find file by hash in filename
            for file_path in user_dir.glob(f"*{file_id}*"):
                if file_path.is_file():
                    metadata = {
                        "original_filename": file_path.name.split("_", 2)[-1] if "_" in file_path.name else file_path.name,
                        "file_size": file_path.stat().st_size,
                        "mime_type": mimetypes.guess_type(str(file_path))[0],
                        "upload_timestamp": datetime.fromtimestamp(file_path.stat().st_ctime).isoformat(),
                        "user_id": user_id,
                        "file_extension": file_path.suffix
                    }
                    return file_path, metadata

            raise FileNotFoundError(f"File {file_id} not found")

        except Exception as e:
            logger.error(f"Error getting file {file_id}: {e}")
            raise

    async def delete_file(self, file_id: str, user_id: Optional[str] = None) -> bool:
        """Delete file with access control"""
        try:
            file_path, metadata = await self.get_file(file_id, user_id)

            # Check access control
            if metadata.get("user_id") != user_id:
                return False

            # Delete file
            file_path.unlink(missing_ok=True)

            logger.info(f"File deleted: {file_id} by user {user_id}")
            return True

        except FileNotFoundError:
            return False
        except Exception as e:
            logger.error(f"Error deleting file {file_id}: {e}")
            return False

    async def list_user_files(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 20,
        file_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List files for a user with pagination"""
        try:
            user_dir = self.upload_dir / user_id
            if not user_dir.exists():
                return []

            files = []
            for file_path in user_dir.glob("*"):
                if file_path.is_file():
                    # Extract file hash from filename
                    parts = file_path.name.split("_")
                    file_hash = parts[1] if len(parts) >= 2 else "unknown"

                    file_info = {
                        "file_id": file_hash,
                        "filename": parts[-1] if len(parts) >= 3 else file_path.name,
                        "file_size": file_path.stat().st_size,
                        "mime_type": mimetypes.guess_type(str(file_path))[0],
                        "uploaded_at": datetime.fromtimestamp(file_path.stat().st_ctime).isoformat(),
                        "file_extension": file_path.suffix
                    }

                    # Filter by file type if specified
                    if file_type and not file_path.suffix.lower().endswith(file_type.lower()):
                        continue

                    files.append(file_info)

            # Sort by upload date (newest first)
            files.sort(key=lambda x: x["uploaded_at"], reverse=True)

            # Apply pagination
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size

            return files[start_idx:end_idx]

        except Exception as e:
            logger.error(f"Error listing files for user {user_id}: {e}")
            return []

    async def get_user_file_stats(self, user_id: str) -> Dict[str, Any]:
        """Get file statistics for a user"""
        try:
            user_dir = self.upload_dir / user_id
            if not user_dir.exists():
                return {
                    "total_files": 0,
                    "total_size": 0,
                    "file_types": {},
                    "recent_uploads": [],
                    "quota_used_percent": 0
                }

            total_files = 0
            total_size = 0
            file_types = {}
            recent_uploads = []

            for file_path in user_dir.glob("*"):
                if file_path.is_file():
                    total_files += 1
                    file_size = file_path.stat().st_size
                    total_size += file_size

                    # Count file types
                    ext = file_path.suffix.lower()
                    file_types[ext] = file_types.get(ext, 0) + 1

                    # Track recent uploads (last 7 days)
                    upload_time = datetime.fromtimestamp(file_path.stat().st_ctime)
                    if upload_time > datetime.utcnow() - timedelta(days=7):
                        recent_uploads.append({
                            "filename": file_path.name.split("_", 2)[-1] if "_" in file_path.name else file_path.name,
                            "size": file_size,
                            "uploaded_at": upload_time.isoformat()
                        })

            # Sort recent uploads by date
            recent_uploads.sort(key=lambda x: x["uploaded_at"], reverse=True)

            # Calculate quota usage (assuming 1GB quota)
            quota_limit = 1024 * 1024 * 1024  # 1GB
            quota_used_percent = (total_size / quota_limit) * 100 if quota_limit > 0 else 0

            return {
                "total_files": total_files,
                "total_size": total_size,
                "file_types": file_types,
                "recent_uploads": recent_uploads[:10],  # Last 10
                "quota_used_percent": min(quota_used_percent, 100)
            }

        except Exception as e:
            logger.error(f"Error getting file stats for user {user_id}: {e}")
            return {
                "total_files": 0,
                "total_size": 0,
                "file_types": {},
                "recent_uploads": [],
                "quota_used_percent": 0
            }

    async def rescan_file(self, file_id: str) -> Dict[str, Any]:
        """Rescan a file for security threats"""
        try:
            # Find file by ID
            for user_dir in self.upload_dir.iterdir():
                if user_dir.is_dir():
                    for file_path in user_dir.glob(f"*{file_id}*"):
                        if file_path.is_file():
                            # Read file content
                            async with aiofiles.open(file_path, 'rb') as f:
                                content = await f.read()

                            # Rescan
                            scan_result = await self._scan_file_content(content, file_path.name)

                            logger.info(f"File rescanned: {file_id} - Result: {scan_result}")
                            return scan_result

            raise FileNotFoundError(f"File {file_id} not found for rescanning")

        except Exception as e:
            logger.error(f"Error rescanning file {file_id}: {e}")
            return {
                "safe": False,
                "reason": f"Rescan error: {str(e)}",
                "scanner": "error"
            }


# Global secure file service instance
secure_file_service = SecureFileService()
