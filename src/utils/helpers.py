import logging
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
from src.config.settings import settings

def setup_logging(level: int = logging.INFO) -> None:
    """Setup logging configuration"""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('edu_ai_assistant.log')
        ]
    )

def validate_credentials() -> Dict[str, bool]:
    """Validate that all required credentials are available"""
    validation = {}
    
    # Check Google credentials
    validation['google_credentials'] = os.path.exists(settings.GOOGLE_CLIENT_SECRET_FILE)
    
    # Check AI credentials
    validation['ai_credentials'] = bool(settings.OPENAI_API_KEY)
    
    # Check platform credentials
    validation['clever_credentials'] = all([
        settings.CLEVER_USERNAME,
        settings.CLEVER_PASSWORD
    ])
    
    validation['mcgraw_hill_credentials'] = all([
        settings.MCGRAW_HILL_USERNAME, 
        settings.MCGRAW_HILL_PASSWORD
    ])
    
    validation['edpuzzle_credentials'] = all([
        settings.EDPUZZLE_USERNAME,
        settings.EDPUZZLE_PASSWORD
    ])
    
    return validation

def format_timestamp(timestamp: Optional[str] = None) -> str:
    """Format timestamp for consistent display"""
    if timestamp:
        try:
            # Try to parse various timestamp formats
            if 'T' in timestamp:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            else:
                dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except (ValueError, TypeError):
            return timestamp
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def safe_json_loads(json_string: str, default: Any = None) -> Any:
    """Safely parse JSON string with fallback"""
    try:
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError):
        return default

def format_assignment_due_date(due_date_str: str) -> str:
    """Format assignment due date for display"""
    if not due_date_str:
        return "No due date"
    
    try:
        # Handle various date formats
        if 'T' in due_date_str:
            dt = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
        else:
            # Try common date formats
            for fmt in ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%m/%d/%Y']:
                try:
                    dt = datetime.strptime(due_date_str, fmt)
                    break
                except ValueError:
                    continue
            else:
                return due_date_str  # Return original if no format matches
        
        return dt.strftime('%B %d, %Y at %I:%M %p')
    except (ValueError, TypeError):
        return due_date_str

def calculate_time_remaining(due_date_str: str) -> str:
    """Calculate time remaining until due date"""
    if not due_date_str:
        return "No due date"
    
    try:
        if 'T' in due_date_str:
            due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
        else:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d %H:%M:%S')
        
        now = datetime.now()
        time_diff = due_date - now
        
        if time_diff.total_seconds() < 0:
            return "Overdue"
        
        days = time_diff.days
        hours = time_diff.seconds // 3600
        
        if days > 0:
            return f"{days} days, {hours} hours"
        elif hours > 0:
            minutes = (time_diff.seconds % 3600) // 60
            return f"{hours} hours, {minutes} minutes"
        else:
            minutes = time_diff.seconds // 60
            return f"{minutes} minutes"
            
    except (ValueError, TypeError):
        return "Unknown"

def sanitize_filename(filename: str) -> str:
    """Sanitize filename to remove invalid characters"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename[:255]  # Limit length

def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"
