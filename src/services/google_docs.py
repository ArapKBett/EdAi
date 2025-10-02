from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from src.services.google_classroom import GoogleClassroomService
from src.config.settings import settings
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class GoogleDocsService(GoogleClassroomService):
    def __init__(self):
        super().__init__()
        self.docs_service = None
        self.slides_service = None
        self.drive_service = None
        self.initialize_services()
    
    def initialize_services(self):
        """Initialize Google Docs, Slides, and Drive services"""
        try:
            if self.creds:
                self.docs_service = build('docs', 'v1', credentials=self.creds)
                self.slides_service = build('slides', 'v1', credentials=self.creds)
                self.drive_service = build('drive', 'v3', credentials=self.creds)
                logger.info("Google Docs, Slides, and Drive services initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Google services: {e}")
    
    def create_document(self, title: str, content: str = "") -> Optional[Dict[str, Any]]:
        """Create a new Google Document"""
        try:
            if not self.docs_service:
                self.initialize_services()
                if not self.docs_service:
                    return None
            
            # Create the document
            document = self.docs_service.documents().create(
                body={'title': title}
            ).execute()
            
            document_id = document['documentId']
            
            # Add content if provided
            if content:
                requests = [
                    {
                        'insertText': {
                            'location': {'index': 1},
                            'text': content
                        }
                    }
                ]
                
                self.docs_service.documents().batchUpdate(
                    documentId=document_id,
                    body={'requests': requests}
                ).execute()
            
            logger.info(f"Created document: {title} (ID: {document_id})")
            return document
            
        except HttpError as error:
            logger.error(f"Google Docs API error: {error}")
            return None
        except Exception as e:
            logger.error(f"Error creating document: {e}")
            return None
    
    def update_document_content(self, document_id: str, content: str) -> bool:
        """Update content of an existing Google Document"""
        try:
            if not self.docs_service:
                return False
            
            requests = [
                {
                    'insertText': {
                        'location': {'index': 1},
                        'text': content
                    }
                }
            ]
            
            self.docs_service.documents().batchUpdate(
                documentId=document_id,
                body={'requests': requests}
            ).execute()
            
            logger.info(f"Updated document: {document_id}")
            return True
            
        except HttpError as error:
            logger.error(f"Google Docs API error: {error}")
            return False
        except Exception as e:
            logger.error(f"Error updating document: {e}")
            return False
    
    def get_document_content(self, document_id: str) -> Optional[str]:
        """Get content from a Google Document"""
        try:
            if not self.docs_service:
                return None
            
            document = self.docs_service.documents().get(
                documentId=document_id
            ).execute()
            
            content = ""
            for element in document.get('body', {}).get('content', []):
                if 'paragraph' in element:
                    for paragraph_element in element['paragraph']['elements']:
                        if 'textRun' in paragraph_element:
                            content += paragraph_element['textRun']['content']
            
            return content
            
        except HttpError as error:
            logger.error(f"Google Docs API error: {error}")
            return None
        except Exception as e:
            logger.error(f"Error getting document content: {e}")
            return None
    
    def create_presentation(self, title: str) -> Optional[Dict[str, Any]]:
        """Create a new Google Slides presentation"""
        try:
            if not self.slides_service:
                self.initialize_services()
                if not self.slides_service:
                    return None
            
            presentation = self.slides_service.presentations().create(
                body={'title': title}
            ).execute()
            
            logger.info(f"Created presentation: {title} (ID: {presentation['presentationId']})")
            return presentation
            
        except HttpError as error:
            logger.error(f"Google Slides API error: {error}")
            return None
        except Exception as e:
            logger.error(f"Error creating presentation: {e}")
            return None
    
    def add_slide(self, presentation_id: str, slide_layout: str = 'BLANK') -> bool:
        """Add a slide to a presentation"""
        try:
            if not self.slides_service:
                return False
            
            requests = [
                {
                    'createSlide': {
                        'slideLayoutReference': {
                            'predefinedLayout': slide_layout
                        }
                    }
                }
            ]
            
            self.slides_service.presentations().batchUpdate(
                presentationId=presentation_id,
                body={'requests': requests}
            ).execute()
            
            return True
            
        except HttpError as error:
            logger.error(f"Google Slides API error: {error}")
            return False
        except Exception as e:
            logger.error(f"Error adding slide: {e}")
            return False
    
    def share_document(self, document_id: str, email: str, role: str = 'writer') -> bool:
        """Share a document with specific email"""
        try:
            if not self.drive_service:
                self.initialize_services()
                if not self.drive_service:
                    return False
            
            permission = {
                'type': 'user',
                'role': role,
                'emailAddress': email
            }
            
            self.drive_service.permissions().create(
                fileId=document_id,
                body=permission,
                fields='id'
            ).execute()
            
            logger.info(f"Shared document {document_id} with {email}")
            return True
            
        except HttpError as error:
            logger.error(f"Google Drive API error: {error}")
            return False
        except Exception as e:
            logger.error(f"Error sharing document: {e}")
            return False
