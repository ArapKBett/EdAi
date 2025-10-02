# Edu AI Assistant

An AI-powered educational assistant that helps with Google Classroom, Clever portal applications (McGraw Hill, Edpuzzle), and provides AI-guided learning support.

## Features

- **Google Classroom Integration**: Access courses and assignments
- **Google Docs & Slides**: Create and manage documents and presentations
- **Clever Portal Support**: Access educational applications
- **McGraw Hill Integration**: Get assignments and course materials
- **Edpuzzle Integration**: Manage video assignments
- **AI Learning Assistant**: Get guidance and explanations for assignments
- **RESTful API**: Easy integration with other applications

## Quick Start

### Prerequisites

- Python 3.11+
- Google Cloud Project with Classroom, Docs, and Drive APIs enabled
- Clever, McGraw Hill, and Edpuzzle accounts
- OpenAI API key (optional, for AI features)

### Local Installation

1. **Clone and setup:**
`git clone https://github.com/ArapKBett/EdAi
cd EdAi
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate`



2. **Dependencies**

`pip install -r requirements.txt
playwright install chromium`


Google API Setup:
   · Go to Google Cloud Console
   · Create a new project or select existing one
   · Enable Google Classroom, Google Docs, Google Slides, and Google Drive APIs
   · Create OAuth 2.0 credentials (Desktop application)
   · Download credentials as credentials.json in project root

Environment configuration:

```bash
cp .env.example .env
# Edit .env with your actual credentials
```

Run the application:

```bash
python src/main.py
```

The API will be available at http://localhost:8000

Docker Installation

```bash
# Build and run with Docker Compose
docker-compose up -d

# Or build manually
docker build -t edu-ai-assistant .
docker run -p 8000:8000 edu-ai-assistant
```

API Documentation

Once running, visit:

· API Docs: http://localhost:8000/docs
· Redoc: http://localhost:8000/redoc

Key Endpoints

· GET /courses - List Google Classroom courses
· GET /courses/{course_id}/assignments - Get course assignments
· POST /ai/analyze-assignment - Get AI analysis for assignment
· POST /ai/help-with-question - Get AI help for questions
· GET /clever/apps - List available Clever applications
· GET /mcgraw-hill/assignments - Get McGraw Hill assignments
· GET /edpuzzle/assignments - Get Edpuzzle video assignments

Deployment

Render.com Deployment

1. Connect your GitHub repository to Render
2. Create a new Web Service
3. Configure build settings:
   · Build Command: pip install -r requirements.txt && playwright install chromium
   · Start Command: python src/main.py
4. Add environment variables in Render dashboard
5. Deploy

Environment Variables

See .env.example for all required environment variables.

Usage Examples

Using the API

```python
import requests

# Get courses
response = requests.get("http://localhost:8000/courses")
courses = response.json()

# Analyze assignment with AI
analysis_data = {
    "assignment_description": "Write an essay about climate change impacts",
    "context": "Environmental Science course"
}
response = requests.post("http://localhost:8000/ai/analyze-assignment", json=analysis_data)
analysis = response.json()
```

Using cURL

```bash
# Get health status
curl http://localhost:8000/health

# Get Clever applications
curl http://localhost:8000/clever/apps

# Analyze assignment
curl -X POST http://localhost:8000/ai/analyze-assignment \
  -H "Content-Type: application/json" \
  -d '{"assignment_description": "Your assignment here"}'
```
