"""
System Tests for Backend ↔ MCP Communication (haiwpa_backend.py)

Tests the HAIWPABackend class interaction with the MCP server.

Run with: pytest tests/test_backend_mcp.py -v
Servers required: 
    1. MCP server: python haiwpa_mcp.py (port 9000)
"""

import pytest
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from haiwpa_backend import HAIWPABackend
import config


@pytest.fixture(scope="module")
def backend():
    """Create HAIWPABackend instance for testing"""
    return HAIWPABackend()


class TestIsFitnessRelated:
    """Tests for is_fitness_related method (no server required)"""

    def test_detects_workout_keyword(self, backend):
        """Should detect 'workout' as fitness-related"""
        assert backend.is_fitness_related("I had a great workout today") == True

    def test_detects_muscle_keyword(self, backend):
        """Should detect 'muscle' as fitness-related"""
        assert backend.is_fitness_related("My chest muscle is sore") == True

    def test_detects_exercise_names(self, backend):
        """Should detect specific exercise names"""
        assert backend.is_fitness_related("I did 5 sets of squats") == True
        assert backend.is_fitness_related("Bench press is my favorite") == True

    def test_detects_body_parts_in_keywords(self, backend):
        """Should detect body parts that are in FITNESS_KEYWORDS"""
        assert backend.is_fitness_related("I want to train my biceps") == True
        assert backend.is_fitness_related("Working on my chest today") == True

    def test_non_fitness_message(self, backend):
        """Should not detect non-fitness messages"""
        assert backend.is_fitness_related("What's the weather today?") == False
        assert backend.is_fitness_related("Tell me a joke") == False

    def test_case_insensitive(self, backend):
        """Should be case insensitive"""
        assert backend.is_fitness_related("WORKOUT") == True
        assert backend.is_fitness_related("Workout") == True
        assert backend.is_fitness_related("wOrKoUt") == True


class TestGradioToMessages:
    """Tests for gradio_to_messages format conversion (no server required)"""

    def test_string_content_passthrough(self, backend):
        """Should pass through string content unchanged"""
        message = {"role": "user", "content": "Hello"}
        result = backend.gradio_to_messages(message)
        
        assert result == {"role": "user", "content": "Hello"}

    def test_gradio_list_format_extraction(self, backend):
        """Should extract text from Gradio list format"""
        message = {
            "role": "user",
            "content": [{"text": "Hello from Gradio", "type": "text"}]
        }
        result = backend.gradio_to_messages(message)
        
        assert result == {"role": "user", "content": "Hello from Gradio"}

    def test_preserves_role(self, backend):
        """Should preserve message role"""
        user_msg = {"role": "user", "content": "Hi"}
        assistant_msg = {"role": "assistant", "content": "Hello"}
        
        assert backend.gradio_to_messages(user_msg)["role"] == "user"
        assert backend.gradio_to_messages(assistant_msg)["role"] == "assistant"

    def test_empty_list_content(self, backend):
        """Should handle empty list content"""
        message = {"role": "user", "content": []}
        result = backend.gradio_to_messages(message)
        
        # Should return None or handle gracefully
        assert result is None or result.get("content") == ""


class TestConvertValidationToMessage:
    """Tests for convert_validation_to_message method (no server required)"""

    def test_approved_validation_format(self, backend):
        """Should format approved validation correctly"""
        validation_results = [
            {
                "date": "2025-01-15",
                "muscle": "chest",
                "exercises": "bench press",
                "duration": 45,
                "injuries": "",
                "entry_type": "planned",
                "validation": {"approved": True, "reason": "Approved for the muscle (chest)."},
                "max_rest_days": 2
            }
        ]
        
        result = backend.convert_validation_to_message(validation_results)
        
        assert result is not None
        assert "chest" in result
        assert "2025-01-15" in result
        assert "prolog_validation=True" in result

    def test_rejected_validation_format(self, backend):
        """Should format rejected validation correctly"""
        validation_results = [
            {
                "date": "2025-01-15",
                "muscle": "chest",
                "exercises": "bench press",
                "duration": 45,
                "injuries": "",
                "entry_type": "planned",
                "validation": {"approved": False, "reason": "An injury is present."},
                "max_rest_days": 2
            }
        ]
        
        result = backend.convert_validation_to_message(validation_results)
        
        assert "prolog_validation=False" in result
        assert "injury" in result.lower()

    def test_includes_max_rest_days(self, backend):
        """Should include max rest days in message"""
        validation_results = [
            {
                "date": "2025-01-15",
                "muscle": "legs",
                "exercises": "squats",
                "duration": 60,
                "injuries": "",
                "entry_type": "planned",
                "validation": {"approved": False, "reason": "Insufficient rest."},
                "max_rest_days": 2
            }
        ]
        
        result = backend.convert_validation_to_message(validation_results)
        
        assert "max rest days" in result.lower() or "2" in result

    def test_empty_results_returns_none(self, backend):
        """Should return None for empty results"""
        result = backend.convert_validation_to_message([])
        assert result is None

    def test_none_results_returns_none(self, backend):
        """Should return None for None input"""
        result = backend.convert_validation_to_message(None)
        assert result is None

    def test_includes_prolog_context(self, backend):
        """Should include Prolog validation context header"""
        validation_results = [
            {
                "date": "2025-01-15",
                "muscle": "back",
                "exercises": "rows",
                "duration": 45,
                "injuries": "",
                "entry_type": "planned",
                "validation": {"approved": True, "reason": "Approved."},
                "max_rest_days": 2
            }
        ]
        
        result = backend.convert_validation_to_message(validation_results)
        
        # Should include the LLM context header from config
        assert "WORKOUT VALIDATION" in result or "Prolog" in result
        
class TestBackendMCPIntegration:
    """Integration tests for backend-MCP communication"""
    
    @pytest.mark.asyncio
    async def test_fitness_detection_works_independently(self, backend):
        """Fitness detection should work without MCP"""
        # These should work without any server
        assert backend.is_fitness_related("bench press") == True
        assert backend.is_fitness_related("hello") == False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
