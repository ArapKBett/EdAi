import openai
from openai import OpenAI
import json
from src.config.settings import settings
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class AIAssistant:
    def __init__(self):
        self.client = None
        self.is_available = False
        self.initialize_client()
    
    def initialize_client(self):
        """Initialize OpenAI client if API key is available"""
        try:
            if settings.OPENAI_API_KEY:
                self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
                self.is_available = True
                logger.info("OpenAI client initialized successfully")
            else:
                logger.warning("OpenAI API key not found. AI features will be disabled.")
                self.is_available = False
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            self.is_available = False
    
    def analyze_assignment(self, assignment_description: str, context: str = "") -> Dict[str, Any]:
        """
        Analyze an assignment and provide learning guidance
        
        Args:
            assignment_description: The assignment text or description
            context: Additional context about the course or subject
            
        Returns:
            Dictionary containing analysis and guidance
        """
        if not self.is_available:
            return self._get_fallback_analysis(assignment_description)
        
        try:
            prompt = f"""
            You are an educational assistant that helps students understand assignments 
            without doing the work for them. Analyze this assignment and provide helpful guidance.
            
            ASSIGNMENT: {assignment_description}
            CONTEXT: {context}
            
            Please provide a structured analysis with the following sections:
            
            1. KEY_CONCEPTS: List the main concepts and topics this assignment covers
            2. LEARNING_OBJECTIVES: What the student should learn from this assignment
            3. STEP_BY_STEP_APPROACH: A suggested approach to complete the assignment
            4. COMMON_MISTAKES: Common errors students make with this type of assignment
            5. RESOURCES: Recommended learning resources (books, websites, videos)
            6. TIME_ESTIMATE: Estimated time needed to complete
            7. DIFFICULTY_LEVEL: Easy/Medium/Hard with explanation
            
            Return your response as valid JSON with these exact keys.
            """
            
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an experienced educator and tutor. Provide helpful, structured guidance without completing the assignment for the student."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=settings.AI_TEMPERATURE,
                max_tokens=1500
            )
            
            analysis_text = response.choices[0].message.content.strip()
            
            # Try to parse as JSON, fallback to text if invalid
            try:
                analysis = json.loads(analysis_text)
                logger.info("Successfully analyzed assignment with AI")
                return analysis
            except json.JSONDecodeError:
                logger.warning("AI response was not valid JSON, returning as text")
                return {"analysis": analysis_text}
                
        except Exception as e:
            logger.error(f"Error in AI assignment analysis: {e}")
            return self._get_fallback_analysis(assignment_description)
    
    def help_with_question(self, question: str, question_type: str = "multiple_choice") -> Dict[str, Any]:
        """
        Provide help with understanding a question without giving the answer
        
        Args:
            question: The question text
            question_type: Type of question (multiple_choice, essay, math, etc.)
            
        Returns:
            Dictionary containing explanation and guidance
        """
        if not self.is_available:
            return self._get_fallback_question_help(question, question_type)
        
        try:
            prompt = f"""
            You are a tutor helping a student understand a {question_type} question 
            without giving away the answer.
            
            QUESTION: {question}
            QUESTION_TYPE: {question_type}
            
            Please provide helpful guidance with the following structure:
            
            1. QUESTION_BREAKDOWN: Explain what the question is asking in simpler terms
            2. KEY_CONCEPTS: List the concepts needed to answer this question
            3. THINKING_PROCESS: Step-by-step approach to solve this type of question
            4. RELATED_EXAMPLES: Similar examples or practice problems
            5. CHECKING_WORK: How to verify the answer is correct
            6. LEARNING_TIPS: Strategies for mastering this type of question
            
            Return your response as valid JSON with these exact keys.
            Do not provide the direct answer to the question.
            """
            
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a patient tutor who explains concepts clearly without giving away answers. Encourage learning and understanding."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=settings.AI_TEMPERATURE,
                max_tokens=1200
            )
            
            help_text = response.choices[0].message.content.strip()
            
            try:
                help_data = json.loads(help_text)
                logger.info(f"Successfully provided help for {question_type} question")
                return help_data
            except json.JSONDecodeError:
                return {"explanation": help_text}
                
        except Exception as e:
            logger.error(f"Error in AI question help: {e}")
            return self._get_fallback_question_help(question, question_type)
    
    def generate_study_notes(self, topic: str, key_points: List[str] = None) -> Dict[str, Any]:
        """
        Generate study notes for a specific topic
        
        Args:
            topic: The topic to generate notes for
            key_points: Specific points to include
            
        Returns:
            Dictionary containing organized study notes
        """
        if not self.is_available:
            return {"topic": topic, "notes": f"Study notes for {topic} would be generated here with AI."}
        
        try:
            key_points_text = "\n".join(key_points) if key_points else "Cover the most important aspects."
            
            prompt = f"""
            Create comprehensive study notes for the following topic:
            
            TOPIC: {topic}
            KEY_POINTS_TO_COVER: {key_points_text}
            
            Please organize the notes as follows:
            
            1. OVERVIEW: Brief introduction to the topic
            2. KEY_DEFINITIONS: Important terms and definitions
            3. MAIN_CONCEPTS: Core concepts explained clearly
            4. EXAMPLES: Relevant examples and applications
            5. FORMULAS_EQUATIONS: Any important formulas (if applicable)
            6. STUDY_TIPS: Effective ways to study this topic
            7. PRACTICE_SUGGESTIONS: Ideas for practice and application
            
            Return as valid JSON with these exact keys.
            """
            
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert educator who creates clear, organized, and effective study materials."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.5,  # Lower temperature for more consistent study materials
                max_tokens=2000
            )
            
            notes_text = response.choices[0].message.content.strip()
            
            try:
                notes = json.loads(notes_text)
                logger.info(f"Successfully generated study notes for: {topic}")
                return notes
            except json.JSONDecodeError:
                return {"study_notes": notes_text}
                
        except Exception as e:
            logger.error(f"Error generating study notes: {e}")
            return {"topic": topic, "error": "Failed to generate study notes"}
    
    def _get_fallback_analysis(self, assignment_description: str) -> Dict[str, Any]:
        """Provide fallback analysis when AI is unavailable"""
        return {
            "KEY_CONCEPTS": ["Review the assignment instructions carefully"],
            "LEARNING_OBJECTIVES": "Understand and complete the assignment requirements",
            "STEP_BY_STEP_APPROACH": [
                "1. Read the assignment carefully",
                "2. Identify key requirements",
                "3. Research necessary information", 
                "4. Create an outline",
                "5. Complete each section",
                "6. Review and revise"
            ],
            "COMMON_MISTAKES": ["Not following instructions", "Poor time management"],
            "RESOURCES": ["Course textbook", "Class notes", "Online educational resources"],
            "TIME_ESTIMATE": "Varies based on assignment complexity",
            "DIFFICULTY_LEVEL": "Review assignment to determine difficulty",
            "AI_UNAVAILABLE": True
        }
    
    def _get_fallback_question_help(self, question: str, question_type: str) -> Dict[str, Any]:
        """Provide fallback help when AI is unavailable"""
        return {
            "QUESTION_BREAKDOWN": f"Read the question carefully: {question}",
            "KEY_CONCEPTS": ["Review related course materials"],
            "THINKING_PROCESS": [
                "Understand what the question is asking",
                "Recall relevant information",
                "Apply appropriate methods",
                "Verify your approach"
            ],
            "RELATED_EXAMPLES": "Check your textbook or notes for similar examples",
            "CHECKING_WORK": "Review each step of your solution",
            "LEARNING_TIPS": ["Practice similar problems", "Study key concepts"],
            "AI_UNAVAILABLE": True
      }
