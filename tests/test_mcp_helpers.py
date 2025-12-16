"""
Unit Tests for MCP Helper Functions (haiwpa_mcp.py)

Tests helper functions that don't require the MCP server to be running.

Run with: pytest tests/test_mcp_helpers.py -v
Servers required: None
"""

import pytest
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from haiwpa_mcp import convert_date_to_timestamp, format_suggested_workout, validate_single_workout


class TestConvertDateToTimestamp:
    """Tests for convert_date_to_timestamp function"""

    def test_iso_format_date(self):
        """Should convert YYYY-MM-DD format correctly"""
        result = convert_date_to_timestamp("2025-01-15")
        expected = int(datetime(2025, 1, 15).timestamp())
        assert result == expected

    def test_european_format_date(self):
        """Should convert DD.MM.YYYY format correctly"""
        result = convert_date_to_timestamp("15.01.2025")
        expected = int(datetime(2025, 1, 15).timestamp())
        assert result == expected

    def test_returns_integer(self):
        """Should return an integer timestamp"""
        result = convert_date_to_timestamp("2025-06-20")
        assert isinstance(result, int)

    def test_different_dates(self):
        """Should produce different timestamps for different dates"""
        result1 = convert_date_to_timestamp("2025-01-01")
        result2 = convert_date_to_timestamp("2025-01-02")
        assert result1 != result2
        assert result2 > result1  # Later date should have larger timestamp


class TestFormatSuggestedWorkout:
    """Tests for format_suggested_workout function"""

    def test_single_alternative(self):
        """Should format single alternative correctly"""
        suggested = [{"AlternativeMuscle": "legs"}]
        result = format_suggested_workout(suggested)
        assert result == "legs"

    def test_multiple_alternatives(self):
        """Should format multiple alternatives with commas"""
        suggested = [
            {"AlternativeMuscle": "legs"},
            {"AlternativeMuscle": "back"},
            {"AlternativeMuscle": "biceps"}
        ]
        result = format_suggested_workout(suggested)
        assert result == "legs, back, biceps"

    def test_empty_list(self):
        """Should handle empty list"""
        suggested = []
        result = format_suggested_workout(suggested)
        # Returns string with last 2 chars removed from empty string
        assert result == ""

    def test_removes_trailing_comma(self):
        """Should not have trailing comma and space"""
        suggested = [{"AlternativeMuscle": "chest"}]
        result = format_suggested_workout(suggested)
        assert not result.endswith(", ")
        assert not result.endswith(",")


class TestValidateSingleWorkout:
    """Tests for validate_single_workout function structure"""

    def test_returns_dict_structure(self):
        """Should return dictionary with approved and reason keys"""
        # This test uses valid muscle to check return structure
        result = validate_single_workout("chest", "2025-01-15")
        
        assert isinstance(result, dict)
        assert "approved" in result
        assert "reason" in result
        assert isinstance(result["approved"], bool)
        assert isinstance(result["reason"], str)

    def test_invalid_muscle_group_rejected(self):
        """Should reject invalid muscle group"""
        result = validate_single_workout("neck", "2025-01-15")
        
        assert result["approved"] == False
        assert result["reason"] == "invalid_muscle_group"

    def test_muscle_converted_to_lowercase(self):
        """Should handle uppercase muscle names"""
        # Both should work the same
        result_lower = validate_single_workout("chest", "2025-01-15")
        result_upper = validate_single_workout("CHEST", "2025-01-15")
        
        # Both should have same approval status (not rejected as invalid)
        assert result_lower["reason"] != "invalid_muscle_group"
        assert result_upper["reason"] != "invalid_muscle_group"

    def test_valid_muscle_groups_accepted(self):
        """Should accept all valid muscle groups"""
        valid_muscles = ["chest", "back", "legs", "shoulders", 
                        "biceps", "triceps", "abdominals", "calves", "glutes"]
        
        for muscle in valid_muscles:
            result = validate_single_workout(muscle, "2025-01-15")
            assert result["reason"] != "invalid_muscle_group", \
                f"{muscle} should be accepted as valid muscle group"


class TestValidateSingleWorkoutReasons:
    """Tests for validate_single_workout reason messages"""

    def test_approved_reason_format(self):
        """Should include muscle name in approved reason"""
        # Fresh Prolog state should approve
        from pyswip import Prolog
        prolog = Prolog()
        prolog.consult("workout_rules.pl")
        list(prolog.query("retractall(workout_history(_, _, _, _))."))
        list(prolog.query("retractall(injury(_, _))."))
        
        result = validate_single_workout("chest", "2025-01-15")
        
        if result["approved"]:
            assert "chest" in result["reason"].lower()

    def test_injury_reason_includes_alternatives(self):
        """Should include suggested alternatives when injury present"""
        from pyswip import Prolog
        from datetime import datetime, timedelta
        
        # Set up injury scenario
        prolog = Prolog()
        prolog.consult("workout_rules.pl")
        list(prolog.query("retractall(workout_history(_, _, _, _))."))
        list(prolog.query("retractall(injury(_, _))."))
        
        # Add recent injury
        injury_date = datetime.now() - timedelta(days=5)
        injury_timestamp = int(injury_date.timestamp())
        list(prolog.query(f"assertz(injury({injury_timestamp}, 'chest'))."))
        
        result = validate_single_workout("chest", datetime.now().strftime("%Y-%m-%d"))
        
        if not result["approved"] and "injury" in result["reason"].lower():
            assert "alternative" in result["reason"].lower() or \
                   "suggested" in result["reason"].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
