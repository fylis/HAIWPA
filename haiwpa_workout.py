"""
HAIWPA Workout Extraction
A Pydantic model to extract fitness-related information from user input.

Source :
- https://python.useinstructor.com/blog/2024/03/07/open-source-local-structured-output-pydantic-json-openai/#groq
- https://www.youtube.com/watch?v=VllkW63LWbY
"""

from pydantic import BaseModel, Field
from typing import List
import datetime
import json
import os
import config


def today_date() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d")


# Class to extract fitness exercises, duration limits, recent training history, injuries from user input
# This function is based on https://www.youtube.com/watch?v=VllkW63LWbY
class FitnessExtract(BaseModel):
    muscle: str = Field(
        description="Muscle groups mentioned (chest, back, legs, shoulders, biceps, triceps, core, etc.)"
    )
    exercises: str = Field(
        description="Specific exercises mentioned (bench press, squats, curls, etc.)"
    )
    duration: float = Field(
        description="Duration in minutes for each exercise or workout session",
        default=0.0
    )
    date: str = Field(
        description=(
            "Date of the workout in YYYY-MM-DD format. "
            "Extract based on these rules: "
            f"Note : today's date is {today_date()}, use this a reference point. "
            f"- If user says 'today', 'now' or no date mentioned: use today's date which is {today_date()} "
            "- If user says 'yesterday': subtract 1 day from today "
            "- If user says 'X days ago': subtract X days from today "
            "- If user says 'tomorrow': add 1 day to today "
            "- If user says 'in X days': add X days to today "
            "- If user mentions date without year (e.g., '12-03', 'Dec 3'): use current year "
            "- If user gives DD.MM.YYYY or DD/MM/YYYY: convert to YYYY-MM-DD "
            "Always output in YYYY-MM-DD format."
        ),
        default=f"{today_date()}"
    )
    injuries: str = Field(
        description="Any injuries or pain mentioned to specific muscles. If there is no injuries, leave this field empty",
        default=""
    )
    entry_type: str = Field(
        description=(
            "Classification: completed/planned : "
            "- completed if the user said that he trained that muscle (using of past tenses, past date terms) "
            "- planned if there is a question about future muscle training or future date terms "
        )
    )

    # This function prints the extracted information in the console
    def print_extracted_info(self):
        print("=== Extracted Fitness Information ===")
        print(f'"muscle":"{self.muscle}"')
        print(f'"exercises":"{self.exercises}"')
        print(f'"duration":"{self.duration}"')
        print(f'"date":"{self.date}"')
        print(f'"injuries":"{self.injuries}"')
        print(f'"entry_type":"{self.entry_type}"')
        print("=====================================")

    # Function that saves the extracted information from the user prompt to a JSON file
    # This function was created using Claude
    def save_to_json(self, user_input: str):
        os.makedirs(config.DATA_FOLDER, exist_ok=True)

        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "user_input": user_input,
            "muscle": self.muscle,
            "exercises": self.exercises,
            "duration": self.duration,
            "date": self.date,
            "injuries": self.injuries,
            "entry_type": self.entry_type,
        }

        if os.path.exists(config.CONTEXT_FILE):
            try:
                with open(config.CONTEXT_FILE, "r") as f:
                    data = json.load(f)
            except json.JSONDecodeError:
                data = []
        else:
            data = []

        data.append(entry)
        with open(config.CONTEXT_FILE, "w") as f:
            json.dump(data, f, indent=2)

        print(f"Saved workout data to {config.CONTEXT_FILE}")


# Class to handle multiple training sessions extracted from user input
class MultipleFitnessExtract(BaseModel):
    sessions: List[FitnessExtract] = Field(
        description=(
            "CRITICAL: Extract ALL workout sessions from the input. "
            "RULES: "
            "1 - Each muscle = separate session "
            "2 - Past workout = completed, future question = planned "
            "3 - Different dates = separate sessions"
        )
    )
