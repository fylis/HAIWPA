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
list(prolog.query("connexion_test."))


def convert_date_to_timestamp(date_str: str):
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return int(dt.timestamp())


def load_data_from_json(file_path=config.CONTEXT_FILE):
    # Check if file exists
    if not os.path.exists(file_path):
        return

    # Clearing previous data in SWI-Prolog
    list(prolog.query("retractall(workout_history(_, _, _, _))."))
    list(prolog.query("retractall(injury(_, _))."))

    # Load JSON data
    with open(file_path, "r") as f:
        data = json.load(f)

    for entry in data:
        date = entry["date"]
        muscle = entry["muscle"].lower()
        exercises = entry["exercises"]
        duration = entry["duration"]
        injuries = entry["injuries"]

        # Workout history assertion
        if date and muscle:
            query = f"assertz(workout_history({convert_date_to_timestamp(date)}, '{muscle}', '{exercises}', {duration}))"
            list(prolog.query(query))

        # Injuries assertion
        if injuries and injuries.strip():
            query = f"assertz(injury({convert_date_to_timestamp(date)}, '{muscle}'))"
            list(prolog.query(query))


def validate_workout(muscle: str, date: str):
    """
    Validate if a workout for a specific muscle group is allowed on a given date (yes/no).
    Returns {"approved": bool, "reason": str}
    """
    load_data_from_json()

    # All atoms/muscles groups, etc. are in lowercase in SWI-Prolog
    muscle = muscle.lower()

    # Checking if muscle group is valid
    if not list(prolog.query(f"muscle_group({muscle}).")):
        return {"approved": False, "reason": "invalid_muscle_group"}

    query = f"can_workout({muscle}, {convert_date_to_timestamp(date)}, Reason)."
    results = list(prolog.query(query))

    if results:
        reason = results[0]["Reason"]
        # print(f"Prolog result : {reason}")

        if reason == "workout_allowed":
            return {"approved": True, "reason": "Approved for the muscle group."}
        elif reason == "injury_present":
            return {"approved": False, "reason": "An injury is present."}
        elif reason == "insufficient_rest":
            return {"approved": False, "reason": "Insufficient rest on the muscle group."}

    # Check if workout is allowed
    return {"approved": False, "reason": "Unknown reason"}


load_data_from_json()
print(validate_workout("biceps", "2025-12-09"))

# if __name__ == "__main__":
#     mcp.run()
