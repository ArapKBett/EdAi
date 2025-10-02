from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.services.google_classroom import GoogleClassroomService
from src.services.google_docs import GoogleDocsService
from src.services.clever import CleverService
from src.services.mcgraw_hill import McGrawHillService
from src.services.edpuzzle import EdpuzzleService
from src.ai.assistant import AIAssistant
from src.models.schemas import Assignment, Course, AnalysisRequest, QuestionHelpRequest
import asyncio
from typing import List, Dict, Any
import uvicorn

app = FastAPI(title="Edu AI Assistant", version="1.0.0", description="AI-powered educational assistant")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
classroom_service = GoogleClassroomService()
docs_service = GoogleDocsService()
ai_assistant = AIAssistant()

@app.get("/")
async def root():
    return {
        "message": "Edu AI Assistant API", 
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": __import__('datetime').datetime.now().isoformat()}

@app.get("/courses", response_model=List[Course])
async def get_courses():
    """Get all Google Classroom courses"""
    try:
        courses = classroom_service.get_courses()
        return courses
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching courses: {str(e)}")

@app.get("/courses/{course_id}/assignments", response_model=List[Assignment])
async def get_assignments(course_id: str):
    """Get assignments for a specific course"""
    try:
        assignments = classroom_service.get_assignments(course_id)
        return assignments
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching assignments: {str(e)}")

@app.post("/ai/analyze-assignment")
async def analyze_assignment(request: AnalysisRequest):
    """Get AI analysis and guidance for an assignment"""
    try:
        analysis = ai_assistant.analyze_assignment(request.assignment_description, request.context)
        return {"analysis": analysis}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing assignment: {str(e)}")

@app.post("/ai/help-with-question")
async def help_with_question(request: QuestionHelpRequest):
    """Get AI help for understanding a question"""
    try:
        help_response = ai_assistant.help_with_question(request.question, request.question_type)
        return {"help": help_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

@app.post("/docs/create")
async def create_document(title: str, content: str = ""):
    """Create a new Google Document"""
    try:
        document = docs_service.create_document(title, content)
        if document:
            return {"document": document, "message": "Document created successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to create document")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating document: {str(e)}")

@app.get("/clever/apps")
async def get_clever_apps():
    """Get available applications from Clever"""
    clever_service = CleverService()
    try:
        if await clever_service.login():
            apps = await clever_service.get_applications()
            await clever_service.close()
            return {"applications": apps}
        else:
            raise HTTPException(status_code=401, detail="Clever login failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/mcgraw-hill/assignments")
async def get_mcgraw_assignments():
    """Get assignments from McGraw Hill"""
    mcgraw_service = McGrawHillService()
    try:
        if await mcgraw_service.login():
            assignments = await mcgraw_service.get_assignments()
            await mcgraw_service.close()
            return {"assignments": assignments}
        else:
            raise HTTPException(status_code=401, detail="McGraw Hill login failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/edpuzzle/assignments")
async def get_edpuzzle_assignments():
    """Get video assignments from Edpuzzle"""
    edpuzzle_service = EdpuzzleService()
    try:
        if await edpuzzle_service.login():
            assignments = await edpuzzle_service.get_video_assignments()
            await edpuzzle_service.close()
            return {"assignments": assignments}
        else:
            raise HTTPException(status_code=401, detail="Edpuzzle login failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/services/status")
async def get_services_status():
    """Check status of all services"""
    status = {
        "google_classroom": "available",
        "google_docs": "available",
        "ai_assistant": "available" if ai_assistant.client else "unavailable",
        "clever": "available",
        "mcgraw_hill": "available",
        "edpuzzle": "available"
    }
    return {"services": status}

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
      )
