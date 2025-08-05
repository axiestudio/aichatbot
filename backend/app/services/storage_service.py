import os
import asyncio
import aiofiles
from typing import Optional, Dict, Any, BinaryIO
from pathlib import Path
import logging
import hashlib
import shutil
from datetime import datetime

# Cloud storage imports
try:
    import boto3
    from botocore.exceptions import ClientError
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False

try:
    from minio import Minio
    from minio.error import S3Error
    MINIO_AVAILABLE = True
except ImportError:
    MINIO_AVAILABLE = False

try:
    from azure.storage.blob import BlobServiceClient
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False

from app.core.config import settings

logger = logging.getLogger(__name__)


class StorageService:
    """Service for managing file storage (local, S3, MinIO, Azure)"""
    
    def __init__(self):
        self.storage_type = getattr(settings, 'STORAGE_TYPE', 'local')
        self.base_path = Path(getattr(settings, 'STORAGE_PATH', './storage'))
        self.base_path.mkdir(exist_ok=True)
        
        # Initialize cloud storage clients
        self._initialize_storage()
    
    def _initialize_storage(self):
        """Initialize storage backend based on configuration"""
        try:
            if self.storage_type == 'local':
                logger.info("Using local file storage")
                
            elif self.storage_type == 's3' and AWS_AVAILABLE:
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=getattr(settings, 'AWS_REGION', 'us-east-1')
                )
                self.s3_bucket = settings.AWS_S3_BUCKET
                logger.info(f"Using AWS S3 storage: {self.s3_bucket}")
                
            elif self.storage_type == 'minio' and MINIO_AVAILABLE:
                self.minio_client = Minio(
                    settings.MINIO_ENDPOINT,
                    access_key=settings.MINIO_ACCESS_KEY,
                    secret_key=settings.MINIO_SECRET_KEY,
                    secure=getattr(settings, 'MINIO_SECURE', True)
                )
                self.minio_bucket = settings.MINIO_BUCKET
                logger.info(f"Using MinIO storage: {self.minio_bucket}")
                
            elif self.storage_type == 'azure' and AZURE_AVAILABLE:
                self.azure_client = BlobServiceClient(
                    account_url=f"https://{settings.AZURE_ACCOUNT_NAME}.blob.core.windows.net",
                    credential=settings.AZURE_ACCOUNT_KEY
                )
                self.azure_container = settings.AZURE_CONTAINER
                logger.info(f"Using Azure Blob storage: {self.azure_container}")
                
            else:
                logger.warning(f"Storage type '{self.storage_type}' not available, falling back to local")
                self.storage_type = 'local'
                
        except Exception as e:
            logger.error(f"Error initializing storage: {str(e)}")
            logger.warning("Falling back to local storage")
            self.storage_type = 'local'
    
    async def store_file(
        self, 
        file_content: bytes, 
        file_path: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Store a file and return the storage path"""
        try:
            if self.storage_type == 'local':
                return await self._store_local(file_content, file_path, metadata)
            elif self.storage_type == 's3':
                return await self._store_s3(file_content, file_path, metadata)
            elif self.storage_type == 'minio':
                return await self._store_minio(file_content, file_path, metadata)
            elif self.storage_type == 'azure':
                return await self._store_azure(file_content, file_path, metadata)
            else:
                raise ValueError(f"Unsupported storage type: {self.storage_type}")
                
        except Exception as e:
            logger.error(f"Error storing file {file_path}: {str(e)}")
            raise
    
    async def retrieve_file(self, file_path: str) -> Optional[bytes]:
        """Retrieve a file from storage"""
        try:
            if self.storage_type == 'local':
                return await self._retrieve_local(file_path)
            elif self.storage_type == 's3':
                return await self._retrieve_s3(file_path)
            elif self.storage_type == 'minio':
                return await self._retrieve_minio(file_path)
            elif self.storage_type == 'azure':
                return await self._retrieve_azure(file_path)
            else:
                raise ValueError(f"Unsupported storage type: {self.storage_type}")
                
        except Exception as e:
            logger.error(f"Error retrieving file {file_path}: {str(e)}")
            return None
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete a file from storage"""
        try:
            if self.storage_type == 'local':
                return await self._delete_local(file_path)
            elif self.storage_type == 's3':
                return await self._delete_s3(file_path)
            elif self.storage_type == 'minio':
                return await self._delete_minio(file_path)
            elif self.storage_type == 'azure':
                return await self._delete_azure(file_path)
            else:
                raise ValueError(f"Unsupported storage type: {self.storage_type}")
                
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {str(e)}")
            return False
    
    async def file_exists(self, file_path: str) -> bool:
        """Check if a file exists in storage"""
        try:
            if self.storage_type == 'local':
                return await self._exists_local(file_path)
            elif self.storage_type == 's3':
                return await self._exists_s3(file_path)
            elif self.storage_type == 'minio':
                return await self._exists_minio(file_path)
            elif self.storage_type == 'azure':
                return await self._exists_azure(file_path)
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error checking file existence {file_path}: {str(e)}")
            return False
    
    async def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get file information (size, modified date, etc.)"""
        try:
            if self.storage_type == 'local':
                return await self._info_local(file_path)
            elif self.storage_type == 's3':
                return await self._info_s3(file_path)
            elif self.storage_type == 'minio':
                return await self._info_minio(file_path)
            elif self.storage_type == 'azure':
                return await self._info_azure(file_path)
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error getting file info {file_path}: {str(e)}")
            return None
    
    def generate_file_path(self, filename: str, prefix: str = "") -> str:
        """Generate a unique file path"""
        # Create a hash-based path to avoid conflicts
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        file_hash = hashlib.md5(f"{filename}{timestamp}".encode()).hexdigest()[:8]
        
        # Clean filename
        clean_filename = "".join(c for c in filename if c.isalnum() or c in "._-")
        
        if prefix:
            return f"{prefix}/{timestamp}_{file_hash}_{clean_filename}"
        else:
            return f"{timestamp}_{file_hash}_{clean_filename}"
    
    # Local storage methods
    
    async def _store_local(self, file_content: bytes, file_path: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Store file locally"""
        full_path = self.base_path / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        async with aiofiles.open(full_path, 'wb') as f:
            await f.write(file_content)
        
        # Store metadata if provided
        if metadata:
            metadata_path = full_path.with_suffix(full_path.suffix + '.meta')
            async with aiofiles.open(metadata_path, 'w') as f:
                import json
                await f.write(json.dumps(metadata, default=str))
        
        return str(full_path)
    
    async def _retrieve_local(self, file_path: str) -> Optional[bytes]:
        """Retrieve file from local storage"""
        full_path = self.base_path / file_path
        if not full_path.exists():
            return None
        
        async with aiofiles.open(full_path, 'rb') as f:
            return await f.read()
    
    async def _delete_local(self, file_path: str) -> bool:
        """Delete file from local storage"""
        full_path = self.base_path / file_path
        if full_path.exists():
            full_path.unlink()
            
            # Also delete metadata file if it exists
            metadata_path = full_path.with_suffix(full_path.suffix + '.meta')
            if metadata_path.exists():
                metadata_path.unlink()
            
            return True
        return False
    
    async def _exists_local(self, file_path: str) -> bool:
        """Check if file exists in local storage"""
        full_path = self.base_path / file_path
        return full_path.exists()
    
    async def _info_local(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get file info from local storage"""
        full_path = self.base_path / file_path
        if not full_path.exists():
            return None
        
        stat = full_path.stat()
        return {
            'size': stat.st_size,
            'modified': datetime.fromtimestamp(stat.st_mtime),
            'created': datetime.fromtimestamp(stat.st_ctime),
            'path': str(full_path)
        }
    
    # S3 storage methods (placeholder implementations)
    
    async def _store_s3(self, file_content: bytes, file_path: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Store file in S3"""
        if not AWS_AVAILABLE:
            raise RuntimeError("AWS SDK not available")
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: self.s3_client.put_object(
                Bucket=self.s3_bucket,
                Key=file_path,
                Body=file_content,
                Metadata=metadata or {}
            )
        )
        return f"s3://{self.s3_bucket}/{file_path}"
    
    async def _retrieve_s3(self, file_path: str) -> Optional[bytes]:
        """Retrieve file from S3"""
        if not AWS_AVAILABLE:
            return None
        
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.s3_client.get_object(Bucket=self.s3_bucket, Key=file_path)
            )
            return response['Body'].read()
        except ClientError:
            return None
    
    async def _delete_s3(self, file_path: str) -> bool:
        """Delete file from S3"""
        if not AWS_AVAILABLE:
            return False
        
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self.s3_client.delete_object(Bucket=self.s3_bucket, Key=file_path)
            )
            return True
        except ClientError:
            return False
    
    async def _exists_s3(self, file_path: str) -> bool:
        """Check if file exists in S3"""
        if not AWS_AVAILABLE:
            return False
        
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self.s3_client.head_object(Bucket=self.s3_bucket, Key=file_path)
            )
            return True
        except ClientError:
            return False
    
    async def _info_s3(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get file info from S3"""
        if not AWS_AVAILABLE:
            return None
        
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.s3_client.head_object(Bucket=self.s3_bucket, Key=file_path)
            )
            return {
                'size': response['ContentLength'],
                'modified': response['LastModified'],
                'etag': response['ETag'],
                'path': f"s3://{self.s3_bucket}/{file_path}"
            }
        except ClientError:
            return None
    
    # MinIO methods (similar to S3 but using MinIO client)
    # Azure methods (using Azure Blob Storage client)
    # Implementation details omitted for brevity but would follow similar patterns
    
    async def _store_minio(self, file_content: bytes, file_path: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Store file in MinIO - placeholder"""
        # Implementation would use self.minio_client
        raise NotImplementedError("MinIO storage not fully implemented")
    
    async def _retrieve_minio(self, file_path: str) -> Optional[bytes]:
        """Retrieve file from MinIO - placeholder"""
        raise NotImplementedError("MinIO storage not fully implemented")
    
    async def _delete_minio(self, file_path: str) -> bool:
        """Delete file from MinIO - placeholder"""
        raise NotImplementedError("MinIO storage not fully implemented")
    
    async def _exists_minio(self, file_path: str) -> bool:
        """Check if file exists in MinIO - placeholder"""
        raise NotImplementedError("MinIO storage not fully implemented")
    
    async def _info_minio(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get file info from MinIO - placeholder"""
        raise NotImplementedError("MinIO storage not fully implemented")
    
    # Azure Blob Storage methods - placeholders
    async def _store_azure(self, file_content: bytes, file_path: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Store file in Azure - placeholder"""
        raise NotImplementedError("Azure storage not fully implemented")
    
    async def _retrieve_azure(self, file_path: str) -> Optional[bytes]:
        """Retrieve file from Azure - placeholder"""
        raise NotImplementedError("Azure storage not fully implemented")
    
    async def _delete_azure(self, file_path: str) -> bool:
        """Delete file from Azure - placeholder"""
        raise NotImplementedError("Azure storage not fully implemented")
    
    async def _exists_azure(self, file_path: str) -> bool:
        """Check if file exists in Azure - placeholder"""
        raise NotImplementedError("Azure storage not fully implemented")
    
    async def _info_azure(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get file info from Azure - placeholder"""
        raise NotImplementedError("Azure storage not fully implemented")
