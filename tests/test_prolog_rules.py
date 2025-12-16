"""
Unit Tests for Prolog Rules (workout_rules.pl)

Tests direct PySwip queries to the Prolog knowledge base.

Run with: pytest tests/test_prolog_rules.py -v
Servers required: None
"""

import pytest
import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyswip import Prolog


@pytest.fixture(scope="module")
def prolog():
    """Initialize Prolog engine and load workout rules"""
    pl = Prolog()
    rules_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "workout_rules.pl")
    pl.consult(rules_path)
    return pl


def date_to_timestamp(date_str: str) -> int:
    """Convert YYYY-MM-DD to UNIX timestamp"""
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return int(dt.timestamp())


def days_ago_timestamp(days: int) -> int:
    """Get timestamp for N days ago"""
    dt = datetime.now() - timedelta(days=days)
    return int(dt.timestamp())


def today_timestamp() -> int:
    """Get today's timestamp"""
    return int(datetime.now().timestamp())


class TestConnectionTest:
    """Tests for Prolog connection"""

    def test_connection_test_succeeds(self, prolog):
        """Should successfully run connection_test predicate"""
        result = list(prolog.query("connection_test."))
        assert result == [{}]  # Empty dict means query succeeded


class TestMuscleGroups:
    """Tests for muscle_group/1 predicate"""

    def test_valid_muscle_groups(self, prolog):
        """Should recognize all valid muscle groups"""
        valid_muscles = ["chest", "biceps", "legs", "back", "shoulders", 
                        "triceps", "abdominals", "calves", "glutes"]
        
        for muscle in valid_muscles:
            result = list(prolog.query(f"muscle_group({muscle})."))
            assert result == [{}], f"muscle_group({muscle}) should be valid"

    def test_invalid_muscle_group(self, prolog):
        """Should reject invalid muscle group"""
        result = list(prolog.query("muscle_group(neck)."))
        assert result == [], "neck should not be a valid muscle group"


class TestRestDayRequired:
    """Tests for rest_day_required/2 predicate"""

    def test_one_day_rest_muscles(self, prolog):
        """Should require 1 day rest for small muscles"""
        one_day_muscles = ["biceps", "triceps", "abdominals", "calves"]
        
        for muscle in one_day_muscles:
            result = list(prolog.query(f"rest_day_required({muscle}, Days)."))
            assert len(result) == 1
            assert result[0]["Days"] == 1, f"{muscle} should require 1 day rest"

    def test_two_day_rest_muscles(self, prolog):
        """Should require 2 days rest for large muscles"""
        two_day_muscles = ["chest", "back", "shoulders", "legs", "glutes"]
        
        for muscle in two_day_muscles:
            result = list(prolog.query(f"rest_day_required({muscle}, Days)."))
            assert len(result) == 1
            assert result[0]["Days"] == 2, f"{muscle} should require 2 days rest"


class TestInjuryRecoveryDays:
    """Tests for injury_recovery_days/2 predicate"""

    def test_14_day_recovery_muscles(self, prolog):
        """Should require 14 days recovery for small muscles"""
        muscles_14_days = ["biceps", "triceps", "calves"]
        
        for muscle in muscles_14_days:
            result = list(prolog.query(f"injury_recovery_days({muscle}, Days)."))
            assert len(result) == 1
            assert result[0]["Days"] == 14, f"{muscle} should require 14 days recovery"

    def test_21_day_recovery_muscles(self, prolog):
        """Should require 21 days recovery for medium muscles"""
        muscles_21_days = ["abdominals", "shoulders"]
        
        for muscle in muscles_21_days:
            result = list(prolog.query(f"injury_recovery_days({muscle}, Days)."))
            assert len(result) == 1
            assert result[0]["Days"] == 21, f"{muscle} should require 21 days recovery"

    def test_28_day_recovery_muscles(self, prolog):
        """Should require 28 days recovery for large muscles"""
        muscles_28_days = ["chest", "back", "legs", "glutes"]
        
        for muscle in muscles_28_days:
            result = list(prolog.query(f"injury_recovery_days({muscle}, Days)."))
            assert len(result) == 1
            assert result[0]["Days"] == 28, f"{muscle} should require 28 days recovery"


class TestTrainedTogether:
    """Tests for trained_together/2 predicate"""

    def test_chest_trained_with_triceps(self, prolog):
        """Should recognize chest is trained with triceps"""
        result = list(prolog.query("trained_together(chest, triceps)."))
        assert result == [{}]

    def test_back_trained_with_biceps(self, prolog):
        """Should recognize back is trained with biceps"""
        result = list(prolog.query("trained_together(back, biceps)."))
        assert result == [{}]

    def test_legs_trained_with_glutes(self, prolog):
        """Should recognize legs is trained with glutes"""
        result = list(prolog.query("trained_together(legs, glutes)."))
        assert result == [{}]

    def test_unrelated_muscles_not_trained_together(self, prolog):
        """Should not have unrelated muscles as trained_together"""
        result = list(prolog.query("trained_together(chest, legs)."))
        assert result == []


class TestExercises:
    """Tests for exercise/2 predicate"""

    def test_bench_press_is_chest(self, prolog):
        """Should map bench press to chest"""
        result = list(prolog.query("exercise('bench press', Muscle)."))
        assert len(result) == 1
        assert result[0]["Muscle"] == "chest"

    def test_squats_is_legs(self, prolog):
        """Should map squats to legs"""
        result = list(prolog.query("exercise(squats, Muscle)."))
        assert len(result) == 1
        assert result[0]["Muscle"] == "legs"

    def test_curls_is_biceps(self, prolog):
        """Should map curls to biceps"""
        result = list(prolog.query("exercise(curls, Muscle)."))
        assert len(result) == 1
        assert result[0]["Muscle"] == "biceps"


class TestCanWorkout:
    """Tests for can_workout/3 predicate (the core validation logic)"""

    def test_workout_allowed_no_history(self, prolog):
        """Should allow workout when no history exists"""
        # Clear any existing data
        list(prolog.query("retractall(workout_history(_, _, _, _))."))
        list(prolog.query("retractall(injury(_, _))."))
        
        today = today_timestamp()
        result = list(prolog.query(f"can_workout(chest, {today}, Reason)."))
        
        assert len(result) == 1
        assert result[0]["Reason"] == "workout_allowed"

    def test_injury_present_blocks_workout(self, prolog):
        """Should block workout when injury is present"""
        # Clear and set up injury
        list(prolog.query("retractall(workout_history(_, _, _, _))."))
        list(prolog.query("retractall(injury(_, _))."))
        
        # Add injury from 5 days ago (within 28-day recovery for chest)
        injury_date = days_ago_timestamp(5)
        list(prolog.query(f"assertz(injury({injury_date}, 'chest'))."))
        
        today = today_timestamp()
        result = list(prolog.query(f"can_workout(chest, {today}, Reason)."))
        
        assert len(result) >= 1
        assert result[0]["Reason"] == "injury_present"

    def test_insufficient_rest_blocks_workout(self, prolog):
        """Should block workout when insufficient rest"""
        # Clear and set up recent workout
        list(prolog.query("retractall(workout_history(_, _, _, _))."))
        list(prolog.query("retractall(injury(_, _))."))
        
        # Add workout from yesterday (within 2-day rest requirement for chest)
        yesterday = days_ago_timestamp(1)
        list(prolog.query(f"assertz(workout_history({yesterday}, 'chest', 'bench press', 45))."))
        
        today = today_timestamp()
        result = list(prolog.query(f"can_workout(chest, {today}, Reason)."))
        
        assert len(result) >= 1
        assert result[0]["Reason"] == "insufficient_rest"

    def test_trained_together_injury_blocks_workout(self, prolog):
        """Should block workout when synergistic muscle is injured"""
        # Clear and set up injury on related muscle
        list(prolog.query("retractall(workout_history(_, _, _, _))."))
        list(prolog.query("retractall(injury(_, _))."))
        
        # Add injury to biceps (trained together with back)
        injury_date = days_ago_timestamp(5)
        list(prolog.query(f"assertz(injury({injury_date}, 'biceps'))."))
        
        today = today_timestamp()
        result = list(prolog.query(f"can_workout(back, {today}, Reason)."))
        
        assert len(result) >= 1
        assert result[0]["Reason"] == "trained_together_injured"

    def test_workout_allowed_after_sufficient_rest(self, prolog):
        """Should allow workout after sufficient rest period"""
        # Clear and set up old workout
        list(prolog.query("retractall(workout_history(_, _, _, _))."))
        list(prolog.query("retractall(injury(_, _))."))
        
        # Add workout from 5 days ago (more than 2-day rest requirement for chest)
        old_date = days_ago_timestamp(5)
        list(prolog.query(f"assertz(workout_history({old_date}, 'chest', 'bench press', 45))."))
        
        today = today_timestamp()
        result = list(prolog.query(f"can_workout(chest, {today}, Reason)."))
        
        assert len(result) == 1
        assert result[0]["Reason"] == "workout_allowed"


class TestSuggestAlternative:
    """Tests for suggest_alternative/3 predicate"""

    def test_suggests_alternative_when_injured(self, prolog):
        """Should suggest alternative muscles when target is injured"""
        # Clear and set up injury
        list(prolog.query("retractall(workout_history(_, _, _, _))."))
        list(prolog.query("retractall(injury(_, _))."))
        
        injury_date = days_ago_timestamp(5)
        list(prolog.query(f"assertz(injury({injury_date}, 'chest'))."))
        
        today = today_timestamp()
        result = list(prolog.query(f"suggest_alternative(chest, {today}, Alternative)."))
        
        assert len(result) > 0, "Should suggest at least one alternative"
        
        # Alternatives should not include chest or muscles trained with chest
        alternatives = [r["Alternative"] for r in result]
        assert "chest" not in alternatives
        # Triceps, shoulders, abdominals are trained with chest, should not be suggested
        assert "triceps" not in alternatives
        assert "shoulders" not in alternatives

    def test_suggests_alternative_when_insufficient_rest(self, prolog):
        """Should suggest alternative muscles when insufficient rest"""
        # Clear and set up recent workout
        list(prolog.query("retractall(workout_history(_, _, _, _))."))
        list(prolog.query("retractall(injury(_, _))."))
        
        yesterday = days_ago_timestamp(1)
        list(prolog.query(f"assertz(workout_history({yesterday}, 'legs', 'squats', 60))."))
        
        today = today_timestamp()
        result = list(prolog.query(f"suggest_alternative(legs, {today}, Alternative)."))
        
        assert len(result) > 0, "Should suggest at least one alternative"
        
        alternatives = [r["Alternative"] for r in result]
        assert "legs" not in alternatives


class TestHasInjury:
    """Tests for has_injury/2 predicate with date arithmetic"""

    def test_has_injury_within_recovery_period(self, prolog):
        """Should detect injury within recovery period"""
        list(prolog.query("retractall(injury(_, _))."))
        
        # Injury 10 days ago (within 14-day recovery for biceps)
        injury_date = days_ago_timestamp(10)
        list(prolog.query(f"assertz(injury({injury_date}, 'biceps'))."))
        
        today = today_timestamp()
        result = list(prolog.query(f"has_injury(biceps, {today})."))
        
        assert result == [{}], "Should detect injury within recovery period"

    def test_no_injury_after_recovery_period(self, prolog):
        """Should not detect injury after recovery period"""
        list(prolog.query("retractall(injury(_, _))."))
        
        # Injury 20 days ago (past 14-day recovery for biceps)
        injury_date = days_ago_timestamp(20)
        list(prolog.query(f"assertz(injury({injury_date}, 'biceps'))."))
        
        today = today_timestamp()
        result = list(prolog.query(f"has_injury(biceps, {today})."))
        
        assert result == [], "Should not detect injury after recovery period"


class TestSufficientRest:
    """Tests for sufficient_rest/3 predicate"""

    def test_sufficient_rest_after_required_days(self, prolog):
        """Should confirm sufficient rest after required days"""
        # Workout 3 days ago for chest (requires 2 days)
        workout_date = days_ago_timestamp(3)
        today = today_timestamp()
        
        result = list(prolog.query(f"sufficient_rest(chest, {workout_date}, {today})."))
        assert result == [{}], "3 days should be sufficient rest for chest (requires 2)"

    def test_insufficient_rest_before_required_days(self, prolog):
        """Should fail when rest period not met"""
        # Workout 1 day ago for chest (requires 2 days)
        workout_date = days_ago_timestamp(1)
        today = today_timestamp()
        
        result = list(prolog.query(f"sufficient_rest(chest, {workout_date}, {today})."))
        assert result == [], "1 day should not be sufficient rest for chest (requires 2)"


class TestDaysBetween:
    """Tests for days_between/3 predicate"""

    def test_days_between_calculation(self, prolog):
        """Should calculate correct days between timestamps"""
        date1 = days_ago_timestamp(5)
        date2 = today_timestamp()
        
        result = list(prolog.query(f"days_between({date1}, {date2}, Days)."))
        
        assert len(result) == 1
        # Allow for some rounding variance
        assert 4 <= result[0]["Days"] <= 6


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
