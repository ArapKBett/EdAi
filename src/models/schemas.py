from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class AssignmentStatus(str, Enum):
    ASSIGNED = "assigned"
    COMPLETED = "completed"
    OVERDUE = "overdue"
    IN_PROGRESS = "in_progress"

class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    ESSAY = "essay"
    MATH = "math"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"

class Course(BaseModel):
    id: str = Field(..., description="Unique course identifier")
    name: str = Field(..., description="Course name")
    section: Optional[str] = Field(None, description="Course section")
    description: Optional[str] = Field(None, description="Course description")
    enrollment_code: Optional[str] = Field(None, description="Course enrollment code")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "course_123",
                "name": "Mathematics 101",
                "section": "Fall 2024",
                "description": "Introduction to Mathematics",
                "enrollment_code": "abc123"
            }
        }

class Assignment(BaseModel):
    id: str = Field(..., description="Unique assignment identifier")
    title: str = Field(..., description="Assignment title")
    description: Optional[str] = Field(None, description="Assignment description")
    due_date: Optional[str] = Field(None, description="Due date in ISO format")
    course_name: str = Field(..., description="Name of the course")
    status: str = Field(..., description="Assignment status")
    max_points: Optional[float] = Field(None, description="Maximum points possible")
    work_type: Optional[str] = Field(None, description="Type of work")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "assign_456",
                "title": "Algebra Homework 1",
                "description": "Complete problems 1-10",
                "due_date": "2024-01-15T23:59:00",
                "course_name": "Mathematics 101",
                "status": "assigned",
                "max_points": 100.0,
                "work_type": "ASSIGNMENT"
            }
        }

class AnalysisRequest(BaseModel):
    assignment_description: str = Field(..., description="The assignment to analyze")
    context: Optional[str] = Field("", description="Additional context about the assignment")
    
    class Config:
        schema_extra = {
            "example": {
                "assignment_description": "Write a 5-page essay about the causes of World War II",
                "context": "History 101 course, focusing on political and economic factors"
            }
        }

class QuestionHelpRequest(BaseModel):
    question: str = Field(..., description="The question to get help with")
    question_type: QuestionType = Field(QuestionType.MULTIPLE_CHOICE, description="Type of question")
    
    class Config:
        schema_extra = {
            "example": {
                "question": "What is the derivative of x^2?",
                "question_type": "math"
            }
        }

class AIAnalysisResponse(BaseModel):
    analysis: Dict[str, Any] = Field(..., description="AI analysis results")
    timestamp: str = Field(..., description="When the analysis was performed")
    
    class Config:
        schema_extra = {
            "example": {
                "analysis": {
                    "KEY_CONCEPTS": ["derivatives", "power rule"],
                    "LEARNING_OBJECTIVES": "Understand basic differentiation",
                    "STEP_BY_STEP_APPROACH": ["Identify the function", "Apply power rule"]
                },
                "timestamp": "2024-01-01T12:00:00Z"
            }
        }

class ServiceStatus(BaseModel):
    service: str = Field(..., description="Service name")
    status: str = Field(..., description="Service status")
    message: Optional[str] = Field(None, description="Additional status information")
    
    class Config:
        schema_extra = {
            "example": {
                "service": "google_classroom",
                "status": "available",
                "message": "Successfully connected"
            }
        }

class ApplicationInfo(BaseModel):
    name: str = Field(..., description="Application name")
    description: Optional[str] = Field(None, description="Application description")
    link: Optional[str] = Field(None, description="Application URL")
    icon: Optional[str] = Field(None, description="Application icon URL")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "McGraw Hill",
                "description": "Educational platform for course materials",
                "link": "https://connected.mcgraw-hill.com",
                "icon": "https://example.com/icon.png"
            }
  }
