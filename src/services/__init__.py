"""
Services package for educational platform integrations
"""

from .google_classroom import GoogleClassroomService
from .google_docs import GoogleDocsService
from .clever import CleverService
from .mcgraw_hill import McGrawHillService
from .edpuzzle import EdpuzzleService

__all__ = [
    'GoogleClassroomService',
    'GoogleDocsService', 
    'CleverService',
    'McGrawHillService',
    'EdpuzzleService'
]
