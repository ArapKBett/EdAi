import os
from dotenv import load_dotenv
from typing import List

load_dotenv()

class Settings:
    # Google API Configuration
    GOOGLE_CLIENT_SECRET_FILE: str = os.getenv('GOOGLE_CLIENT_SECRET_FILE', 'credentials.json')
    GOOGLE_TOKEN_FILE: str = os.getenv('GOOGLE_TOKEN_FILE', 'token.pickle')
    
    # Google API Scopes
    SCOPES: List[str] = [
        'https://www.googleapis.com/auth/classroom.courses.readonly',
        'https://www.googleapis.com/auth/classroom.coursework.me',
        'https://www.googleapis.com/auth/classroom.coursework.students',
        'https://www.googleapis.com/auth/documents',
        'https://www.googleapis.com/auth/presentations',
        'https://www.googleapis.com/auth/drive.file'
    ]
    
    # AI Configuration
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY', '')
    OPENAI_MODEL: str = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
    AI_TEMPERATURE: float = float(os.getenv('AI_TEMPERATURE', '0.7'))
    
    # Platform Credentials
    CLEVER_USERNAME: str = os.getenv('CLEVER_USERNAME', '')
    CLEVER_PASSWORD: str = os.getenv('CLEVER_PASSWORD', '')
    MCGRAW_HILL_USERNAME: str = os.getenv('MCGRAW_HILL_USERNAME', '')
    MCGRAW_HILL_PASSWORD: str = os.getenv('MCGRAW_HILL_PASSWORD', '')
    EDPUZZLE_USERNAME: str = os.getenv('EDPUZZLE_USERNAME', '')
    EDPUZZLE_PASSWORD: str = os.getenv('EDPUZZLE_PASSWORD', '')
    
    # Application Settings
    DEBUG: bool = os.getenv('DEBUG', 'False').lower() == 'true'
    PORT: int = int(os.getenv('PORT', '8000'))
    HOST: str = os.getenv('HOST', '0.0.0.0')
    
    # Security
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'your-secret-key-here')
    
    # Rate Limiting
    REQUESTS_PER_MINUTE: int = int(os.getenv('REQUESTS_PER_MINUTE', '60'))
    
    @property
    def is_ai_available(self) -> bool:
        """Check if AI features are available"""
        return bool(self.OPENAI_API_KEY)
    
    @property
    def is_google_available(self) -> bool:
        """Check if Google services are available"""
        return os.path.exists(self.GOOGLE_CLIENT_SECRET_FILE)

# Global settings instance
settings = Settings()
