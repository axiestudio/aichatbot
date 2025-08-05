import uuid
import json
from datetime import datetime
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

def generate_uuid() -> str:
    return str(uuid.uuid4())

def generate_short_id() -> str:
    return str(uuid.uuid4())[:8]

def serialize_datetime(dt: datetime) -> str:
    return dt.isoformat()

def parse_datetime(dt_str: str) -> datetime:
    return datetime.fromisoformat(dt_str)

def safe_json_loads(json_str: str, default: Any = None) -> Any:
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default

def safe_json_dumps(obj: Any, default: str = "{}") -> str:
    try:
        return json.dumps(obj, default=str)
    except (TypeError, ValueError):
        return default

def truncate_text(text: str, max_length: int = 100) -> str:
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    # Simple keyword extraction
    words = text.lower().split()
    # Filter out common stop words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'}
    keywords = [word for word in words if word not in stop_words and len(word) > 2]
    return keywords[:max_keywords]

def format_file_size(size_bytes: int) -> str:
    if size_bytes == 0:
        return "0B"
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.1f}{size_names[i]}"

def clean_text(text: str) -> str:
    if not text:
        return ""
    # Remove extra whitespace and normalize
    return " ".join(text.split())

def mask_sensitive_data(data: str, mask_char: str = "*", visible_chars: int = 4) -> str:
    if len(data) <= visible_chars:
        return mask_char * len(data)
    return data[:visible_chars] + mask_char * (len(data) - visible_chars)
