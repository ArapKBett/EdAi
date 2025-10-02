import pickle
import os
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from src.config.settings import settings
from src.models.schemas import Assignment, Course
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class GoogleClassroomService:
    def __init__(self):
        self.creds = None
        self.service = None
        self.authenticate()
    
    def authenticate(self) -> bool:
        """Authenticate with Google Classroom API"""
        try:
            # Check if token exists and is valid
            if os.path.exists(settings.GOOGLE_TOKEN_FILE):
                with open(settings.GOOGLE_TOKEN_FILE, 'rb') as token:
                    self.creds = pickle.load(token)
            
            # If there are no (valid) credentials available, let the user log in.
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    if not os.path.exists(settings.GOOGLE_CLIENT_SECRET_FILE):
                        logger.error(f"Google client secret file not found: {settings.GOOGLE_CLIENT_SECRET_FILE}")
                        return False
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        settings.GOOGLE_CLIENT_SECRET_FILE, settings.SCOPES)
                    self.creds = flow.run_local_server(port=0)
                
                # Save the credentials for the next run
                with open(settings.GOOGLE_TOKEN_FILE, 'wb') as token:
                    pickle.dump(self.creds, token)
            
            self.service = build('classroom', 'v1', credentials=self.creds)
            logger.info("Successfully authenticated with Google Classroom")
            return True
            
        except Exception as e:
            logger.error(f"Google Classroom authentication failed: {e}")
            return False
    
    def get_courses(self) -> List[Course]:
        """Get list of courses from Google Classroom"""
        try:
            if not self.service:
                if not self.authenticate():
                    return []
            
            results = self.service.courses().list(
                pageSize=20,
                courseStates=['ACTIVE']
            ).execute()
            
            courses_data = results.get('courses', [])
            
            courses = []
            for course_data in courses_data:
                course = Course(
                    id=course_data['id'],
                    name=course_data['name'],
                    section=course_data.get('section', ''),
                    description=course_data.get('description', ''),
                    enrollment_code=course_data.get('enrollmentCode', '')
                )
                courses.append(course)
            
            logger.info(f"Retrieved {len(courses)} courses")
            return courses
            
        except HttpError as error:
            logger.error(f"Google Classroom API error: {error}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error getting courses: {e}")
            return []
    
    def get_assignments(self, course_id: str) -> List[Assignment]:
        """Get assignments for a specific course"""
        try:
            if not self.service:
                if not self.authenticate():
                    return []
            
            # Get course work
            coursework_result = self.service.courses().courseWork().list(
                courseId=course_id,
                pageSize=20,
                orderBy='dueDate desc'
            ).execute()
            
            assignments_data = coursework_result.get('courseWork', [])
            
            assignments = []
            for work in assignments_data:
                # Parse due date if available
                due_date = None
                if work.get('dueDate'):
                    due_date_str = f"{work['dueDate']['year']}-{work['dueDate']['month']}-{work['dueDate']['day']}"
                    if work.get('dueTime'):
                        due_date_str += f" {work['dueTime']['hours']}:{work['dueTime']['minutes']}:00"
                    due_date = due_date_str
                
                assignment = Assignment(
                    id=work['id'],
                    title=work['title'],
                    description=work.get('description', ''),
                    due_date=due_date,
                    course_name=work.get('courseId', ''),
                    status=work.get('state', 'PUBLISHED'),
                    max_points=work.get('maxPoints'),
                    work_type=work.get('workType', 'ASSIGNMENT')
                )
                assignments.append(assignment)
            
            logger.info(f"Retrieved {len(assignments)} assignments for course {course_id}")
            return assignments
            
        except HttpError as error:
            logger.error(f"Google Classroom API error for course {course_id}: {error}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error getting assignments: {e}")
            return []
    
    def get_assignment_details(self, course_id: str, assignment_id: str) -> Optional[dict]:
        """Get detailed information about a specific assignment"""
        try:
            if not self.service:
                if not self.authenticate():
                    return None
            
            assignment = self.service.courses().courseWork().get(
                courseId=course_id,
                id=assignment_id
            ).execute()
            
            return assignment
            
        except HttpError as error:
            logger.error(f"Error getting assignment details: {error}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting assignment details: {e}")
            return None
    
    def submit_assignment(self, course_id: str, assignment_id: str, submission_data: dict) -> bool:
        """Submit an assignment (placeholder - requires proper implementation)"""
        try:
            logger.info(f"Submission attempt for assignment {assignment_id} in course {course_id}")
            # Note: Actual submission implementation would require proper file handling
            # and compliance with Google Classroom API guidelines
            return True
        except Exception as e:
            logger.error(f"Error submitting assignment: {e}")
            return False
