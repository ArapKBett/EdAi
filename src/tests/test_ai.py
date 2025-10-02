import pytest
from unittest.mock import Mock, patch
from src.ai.assistant import AIAssistant
from src.config.settings import settings

class TestAIAssistant:
    @pytest.fixture
    def ai_assistant(self):
        return AIAssistant()
    
    def test_initialization(self, ai_assistant):
        # Test that assistant initializes (may not have API key in test env)
        assert ai_assistant is not None
    
    @patch('src.ai.assistant.OpenAI')
    def test_analyze_assignment_with_mock(self, mock_openai, ai_assistant):
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices[0].message.content = '{"KEY_CONCEPTS": ["test"], "LEARNING_OBJECTIVES": "test"}'
        mock_openai.return_value.chat.completions.create.return_value = mock_response
        
        # Set API key for test
        ai_assistant.is_available = True
        ai_assistant.client = mock_openai.return_value
        
        result = ai_assistant.analyze_assignment("Test assignment")
        
        assert "KEY_CONCEPTS" in result
        assert isinstance(result, dict)
    
    def test_analyze_assignment_fallback(self, ai_assistant):
        # Test fallback when AI is unavailable
        ai_assistant.is_available = False
        
        result = ai_assistant.analyze_assignment("Test assignment")
        
        assert "KEY_CONCEPTS" in result
        assert result.get("AI_UNAVAILABLE") is True
    
    def test_help_with_question_fallback(self, ai_assistant):
        # Test fallback for question help
        ai_assistant.is_available = False
        
        result = ai_assistant.help_with_question("Test question")
        
        assert "QUESTION_BREAKDOWN" in result
        assert result.get("AI_UNAVAILABLE") is True
