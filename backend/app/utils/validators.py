import re
from typing import List, Optional
from fastapi import HTTPException, status

def validate_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password: str) -> bool:
    if len(password) < 8:
        return False
    if not re.search(r'[A-Za-z]', password):
        return False
    if not re.search(r'[0-9]', password):
        return False
    return True

def validate_file_type(filename: str, allowed_types: List[str]) -> bool:
    if not filename:
        return False
    extension = filename.split('.')[-1].lower()
    return extension in allowed_types

def validate_file_size(file_size: int, max_size: int) -> bool:
    return file_size <= max_size

def sanitize_input(text: str) -> str:
    if not text:
        return ""
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\']', '', text)
    return sanitized.strip()

def validate_config_id(config_id: str) -> bool:
    if not config_id:
        return False
    # Allow alphanumeric, hyphens, and underscores
    pattern = r'^[a-zA-Z0-9_-]+$'
    return re.match(pattern, config_id) is not None and len(config_id) <= 50
