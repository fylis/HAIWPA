"""
HAIWPA MCP Sever
This FastMCP server is designed to load data from JSON files and send it to a SWI-Prolog engine.
After processing, it returns the results back to the client.

Source :
- https://gofastmcp.com/getting-started/quickstart
- https://www.youtube.com/watch?v=aiH79Q-LGjY


Assistant: Claude and Copilot
"""

from fastmcp import FastMCP
from pyswip import Prolog
from datetime import datetime
import json
import config
import os


mcp = FastMCP("HAIWPA MCP Server")
prolog = Prolog()

# Load Prolog knowledge base
prolog.consult("workout_rules.pl")

# Unit test to check if the connexion worked
list(prolog.query("connection_test."))


# Used to convert a US date to UNIX timestamp
def convert_date_to_timestamp(date_str: str):
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return int(dt.timestamp())  # Convert to UNIX timestamp


# Used to have a formatted string from the muscle group alternative list
def format_suggested_workout(suggested_workout):
    res = ""
    for r in suggested_workout:
        res += r["AlternativeMuscle"] + ", "
    res = res[:-2]
    return res


# Prolog query to suggest alternative muscle groups to work on if there is an injury or insufficient rest
def suggest_workout(muscle: str, date: str):
    suggested_workout = list(
        prolog.query(
            f"suggest_alternative({muscle}, {convert_date_to_timestamp(date)}, AlternativeMuscle)."
        )
    )
    res = format_suggested_workout(suggested_workout)
    return res


# Load JSON workout context from file and assert into Prolog knowledge base
def load_json_workout_context(file_path=config.CONTEXT_FILE):
    # Check if file exists
    if not os.path.exists(file_path):
        return

    # Clearing previous data in SWI-Prolog
    list(prolog.query("retractall(workout_history(_, _, _, _))."))
    list(prolog.query("retractall(injury(_, _))."))

    planned_workout = []

    # Load JSON data
    with open(file_path, "r") as f:
        data = json.load(f)

    # JSON data parsing
    for entry in data:
        date = entry["date"]
        muscle = entry["muscle"].lower()
        exercises = entry["exercises"]
        duration = entry["duration"]
        injuries = entry["injuries"]
        entry_type = entry["entry_type"]

        # Checking if there is at least a date and muscle group
        if not date or not muscle:
            continue

        # Workout history assertion to Prolog
        if entry_type == "completed":
            query = f"assertz(workout_history({convert_date_to_timestamp(date)}, '{muscle}', '{exercises}', {duration}))"
            list(prolog.query(query))

            # Injuries assertion to Prolog
            if injuries and injuries.strip():
                query = (
                    f"assertz(injury({convert_date_to_timestamp(date)}, '{muscle}'))"
                )
                list(prolog.query(query))

        # Planned workouts list
        elif entry_type == "planned":
            planned_workout.append(
                {
                    "date": date,
                    "muscle": muscle,
                    "exercises": exercises,
                    "duration": duration,
                    "injuries": injuries,
                    "entry_type": entry_type,
                }
            )

    return planned_workout


# Validate if a workout for a specific muscle group is allowed on a given date (yes/no).
# It returns {"approved": bool, "reason": str}
def validate_single_workout(muscle: str, date: str):
    # All atoms/muscles groups, etc. are in lowercase in SWI-Prolog
    muscle = muscle.lower()

    # Checking if muscle group is valid
    if not list(prolog.query(f"muscle_group({muscle}).")):
        return {"approved": False, "reason": "invalid_muscle_group"}

    query = f"can_workout({muscle}, {convert_date_to_timestamp(date)}, Reason)."
    results = list(prolog.query(query))

    if results:
        reason = results[0]["Reason"]
        print(f"Prolog result : {reason}")

        # Workout allowed
        if reason == "workout_allowed":
            return {"approved": True, "reason": f"Approved for the muscle ({muscle})."}
        
        # Present injury on a muscle that we want to retrain
        elif reason == "injury_present":
            suggested_workout_res = suggest_workout(muscle, date)
            return {
                "approved": False,
                "reason": f"An injury is present. Suggested alternatives : {suggested_workout_res}",
            }
        
        # If one of the muscles that is often trained together with the target muscle is injured 
        elif reason == "trained_together_injured":
            suggested_workout_res = suggest_workout(muscle, date)
            injured_muscle = list(
                prolog.query(
                    f"trained_together_has_injury({muscle}, {convert_date_to_timestamp(date)}, InjuredMuscle)."
                )
            )

            # Check if we can extract the injured muscle name
            if not injured_muscle:
                return {
                    "approved": False,
                    "reason": f"Not possible to train {muscle}, because a muscle that is often trained with it is injured. Suggested alternatives : {suggested_workout_res}",
                }
            else:
                # Extracting the injured muscle name
                injured_muscle_name = injured_muscle[0]["InjuredMuscle"]
                return {
                    "approved": False,
                    "reason": f"Not possible to train {muscle}, because the muscle {injured_muscle_name} that is often trained with it is injured. Suggested alternatives : {suggested_workout_res}",
                }

        # Not enough rest since last training
        elif reason == "insufficient_rest":
            suggested_workout_res = suggest_workout(muscle, date)
            return {
                "approved": False,
                "reason": f"Insufficient rest on the muscle group. Suggested alternatives : {suggested_workout_res}",
            }

    # Check if workout is allowed
    return {"approved": False, "reason": "Unknown reason"}


# MCP Tool to validate all planned workouts from the JSON context file
@mcp.tool()
def validate_all_planned_workouts():
    planned_workouts = load_json_workout_context()
    results = []
    max_rest_days = 0

    if not planned_workouts:
        return results

    max_rest_days_query = list(prolog.query("suggested_rest_days(MaxRestDays)."))
    max_rest_days = max_rest_days_query[0]["MaxRestDays"]
    if not max_rest_days:
        max_rest_days = 1

    for workout in planned_workouts:
        validation = validate_single_workout(workout["muscle"], workout["date"])
        results.append(
            {
                "date": workout["date"],
                "muscle": workout["muscle"],
                "exercises": workout["exercises"],
                "duration": workout["duration"],
                "injuries": workout["injuries"],
                "entry_type": workout["entry_type"],
                "validation": validation,
                "max_rest_days": max_rest_days,
            }
        )

    return results

if __name__ == "__main__":
    mcp.run()
