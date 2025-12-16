"""
Unit Tests for Workout Extraction (haiwpa_workout.py)

Tests the FitnessExtract and MultipleFitnessExtract Pydantic models.

Run with: pytest tests/test_workout_extraction.py -v
Servers required: None
"""

import pytest
import json
import os
import sys
import datetime
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from haiwpa_workout import FitnessExtract, MultipleFitnessExtract, today_date


class TestTodayDate:
    """Tests for today_date helper function"""

    def test_today_date_format(self):
        """Should return date in YYYY-MM-DD format"""
        result = today_date()
        # Check format with regex pattern
        assert len(result) == 10
        assert result[4] == "-"
        assert result[7] == "-"

    def test_today_date_matches_datetime(self):
        """Should match current date from datetime module"""
        result = today_date()
        expected = datetime.datetime.now().strftime("%Y-%m-%d")
        assert result == expected


class TestFitnessExtract:
    """Tests for FitnessExtract Pydantic model"""

    def test_create_basic_fitness_extract(self):
        """Should create a valid FitnessExtract instance"""
        extract = FitnessExtract(
            muscle="chest",
            exercises="bench press",
            duration=45.0,
            date="2025-01-15",
            injuries="",
            entry_type="completed"
        )
        assert extract.muscle == "chest"
        assert extract.exercises == "bench press"
        assert extract.duration == 45.0
        assert extract.date == "2025-01-15"
        assert extract.injuries == ""
        assert extract.entry_type == "completed"

    def test_default_duration_is_zero(self):
        """Should default duration to 0.0 if not provided"""
        extract = FitnessExtract(
            muscle="legs",
            exercises="squats",
            date="2025-01-15",
            entry_type="planned"
        )
        assert extract.duration == 0.0

    def test_json_serialization(self):
        """Should serialize to JSON correctly"""
        extract = FitnessExtract(
            muscle="back",
            exercises="deadlift",
            duration=60.0,
            date="2025-01-15",
            injuries="",
            entry_type="completed"
        )
        json_str = extract.model_dump_json()
        data = json.loads(json_str)
        
        assert data["muscle"] == "back"
        assert data["exercises"] == "deadlift"
        assert data["duration"] == 60.0

    def test_save_to_json_creates_file(self):
        """Should create JSON file and save workout data"""
        import config
        
        # Use temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            original_data_folder = config.DATA_FOLDER
            original_context_file = config.CONTEXT_FILE
            
            config.DATA_FOLDER = tmpdir
            config.CONTEXT_FILE = os.path.join(tmpdir, "test_context.json")
            
            try:
                extract = FitnessExtract(
                    muscle="biceps",
                    exercises="curls",
                    duration=30.0,
                    date="2025-01-15",
                    injuries="",
                    entry_type="completed"
                )
                extract.save_to_json("I trained biceps today")
                
                # Verify file was created
                assert os.path.exists(config.CONTEXT_FILE)
                
                # Verify content
                with open(config.CONTEXT_FILE, "r") as f:
                    data = json.load(f)
                
                assert len(data) == 1
                assert data[0]["muscle"] == "biceps"
                assert data[0]["exercises"] == "curls"
                assert data[0]["user_input"] == "I trained biceps today"
            finally:
                config.DATA_FOLDER = original_data_folder
                config.CONTEXT_FILE = original_context_file

    def test_save_to_json_appends_to_existing(self):
        """Should append to existing JSON file"""
        import config
        
        with tempfile.TemporaryDirectory() as tmpdir:
            original_data_folder = config.DATA_FOLDER
            original_context_file = config.CONTEXT_FILE
            
            config.DATA_FOLDER = tmpdir
            config.CONTEXT_FILE = os.path.join(tmpdir, "test_context.json")
            
            try:
                # First entry
                extract1 = FitnessExtract(
                    muscle="chest",
                    exercises="bench press",
                    duration=45.0,
                    date="2025-01-15",
                    injuries="",
                    entry_type="completed"
                )
                extract1.save_to_json("Chest day")
                
                # Second entry
                extract2 = FitnessExtract(
                    muscle="back",
                    exercises="rows",
                    duration=50.0,
                    date="2025-01-16",
                    injuries="",
                    entry_type="planned"
                )
                extract2.save_to_json("Planning back tomorrow")
                
                # Verify both entries exist
                with open(config.CONTEXT_FILE, "r") as f:
                    data = json.load(f)
                
                assert len(data) == 2
                assert data[0]["muscle"] == "chest"
                assert data[1]["muscle"] == "back"
            finally:
                config.DATA_FOLDER = original_data_folder
                config.CONTEXT_FILE = original_context_file

    def test_default_duration_used_when_not_provided(self):
        """Should use default duration (0.0) when not provided"""
        import config
        
        with tempfile.TemporaryDirectory() as tmpdir:
            original_data_folder = config.DATA_FOLDER
            original_context_file = config.CONTEXT_FILE
            
            config.DATA_FOLDER = tmpdir
            config.CONTEXT_FILE = os.path.join(tmpdir, "test_context.json")
            
            try:
                # Create without specifying duration - should use default 0.0
                extract = FitnessExtract(
                    muscle="shoulders",
                    exercises="lateral raises",
                    date="2025-01-15",
                    injuries="",
                    entry_type="completed"
                )
                extract.save_to_json("Shoulder workout")
                
                with open(config.CONTEXT_FILE, "r") as f:
                    data = json.load(f)
                
                assert data[0]["duration"] == 0.0
            finally:
                config.DATA_FOLDER = original_data_folder
                config.CONTEXT_FILE = original_context_file


class TestMultipleFitnessExtract:
    """Tests for MultipleFitnessExtract Pydantic model"""

    def test_create_multiple_sessions(self):
        """Should create instance with multiple sessions"""
        sessions = [
            FitnessExtract(
                muscle="chest",
                exercises="bench press",
                duration=45.0,
                date="2025-01-15",
                injuries="",
                entry_type="completed"
            ),
            FitnessExtract(
                muscle="triceps",
                exercises="tricep dips",
                duration=20.0,
                date="2025-01-15",
                injuries="",
                entry_type="completed"
            )
        ]
        
        multi = MultipleFitnessExtract(sessions=sessions)
        
        assert len(multi.sessions) == 2
        assert multi.sessions[0].muscle == "chest"
        assert multi.sessions[1].muscle == "triceps"

    def test_empty_sessions_list(self):
        """Should allow empty sessions list"""
        multi = MultipleFitnessExtract(sessions=[])
        assert len(multi.sessions) == 0

    def test_json_serialization_multiple(self):
        """Should serialize multiple sessions to JSON correctly"""
        sessions = [
            FitnessExtract(
                muscle="legs",
                exercises="squats",
                duration=60.0,
                date="2025-01-15",
                injuries="",
                entry_type="completed"
            )
        ]
        
        multi = MultipleFitnessExtract(sessions=sessions)
        json_str = multi.model_dump_json()
        data = json.loads(json_str)
        
        assert "sessions" in data
        assert len(data["sessions"]) == 1
        assert data["sessions"][0]["muscle"] == "legs"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
