"""
HAIWPA Backend
It uses a OpenAI client to interact with the HAIWPA model server.
This module defines the HAIWPABackend class, which provides methods to send prompts
to the model and receive responses, including handling message history.

Source :
- https://github.com/abetlen/llama-cpp-python/blob/main/examples/notebooks/Functions.ipynb
- https://llama.developer.meta.com/docs/features/compatibility/
- https://python.useinstructor.com/blog/2024/03/07/open-source-local-structured-output-pydantic-json-openai/#groq

Assistant : Claude
"""

from typing import List
from openai import OpenAI
import instructor
from pydantic import BaseModel, Field
import config


# Class to extract fitness exercises, duration limits, recent training history, injuries from user input
# This function is based on https://www.youtube.com/watch?v=VllkW63LWbY
class FitnessExtract(BaseModel):
    muscle: List[str] = Field(
        description="You have to find a muscle group from the user input"
    )
    duration: List[float] = Field(
        description="You have to find the duration in fraction of hours from the user input that is encoded as a float for each muscle group"
    )

    # Still have to work on :

    # exercises: List[str] = Field(
    #     description="You have to find exercises related to the muscle group"
    # )
    # duration_limits: List[str] = Field(
    #     alias="durationLimits",
    #     description="You have to find duration limits for the exercises from the user input, the format has to be in fraction of hours like 0.1 for 6 minutes, 0.5 for 30 minutes, 1 for 1 hour",
    # )
    # recent_training_history: List[str] = Field(
    #     alias="recentTrainingHistory",
    #     description="You have to get the history of recent training from the user input, the format has to be muscle, exercise, duration, date",
    # )
    # injuries: List[str] = Field(
    #     description="You have to find injuries from the user input for each muscle if there is any, if not return an empty list"
    # )


class HAIWPABackend:
    def __init__(self):
        self.client = OpenAI(base_url=f"{config.SERVER_URL}/v1", api_key=config.API_KEY)

        # Used for structured JSON extraction
        self.instructor_client = instructor.from_openai(
            OpenAI(base_url=f"{config.SERVER_URL}/v1", api_key=config.API_KEY),
            mode=instructor.Mode.JSON,
        )
        self.model_name = config.MODEL_ALIAS
        self.temperature = config.TEMPERATURE
        self.max_tokens = config.MAX_TOKEN

    # Wait for a response from the model after the prompt is sent
    # This function is based on https://github.com/abetlen/llama-cpp-python/blob/main/examples/notebooks/Functions.ipynb
    def chat(self, messages):
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            # Used to extract content.text from llama.cpp
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"

    # Check if message contains fitness-related keywords
    def is_fitness_related(self, message: str) -> bool:
        """Check if message contains fitness-related keywords"""
        fitness_keywords = [
            "workout",
            "exercise",
            "training",
            "gym",
            "fitness",
            "muscle",
            "cardio",
            "strength",
            "injury",
            "rest",
            "squat",
            "bench",
            "deadlift",
            "curl",
            "press",
            "chest",
            "back",
            "legs",
            "arms",
            "shoulders",
            "biceps",
            "triceps",
            "abs",
            "core",
            "glutes",
            "run",
            "running",
            "jog",
            "swim",
            "cycling",
            "duration",
            "minutes",
            "hours",
            "sets",
            "reps",
        ]
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in fitness_keywords)

    # Extract fitness information from user input using structured JSON extraction
    # This function is based on https://www.youtube.com/watch?v=VllkW63LWbY
    def extract_fitness_info(self, user_input):
        try:
            response = self.instructor_client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "user",
                        "content": f"Extract fitness information from the following input:\n{user_input} using a JSON format",
                    }
                ],
                response_model=FitnessExtract,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            return response
        except Exception as e:
            return f"Error: {str(e)}"

    # Adds the user/bot message history to the current message and gets a response
    def chat_with_history(self, current_message, history):
        # Printing fitness extraction informations from user prompts only if the message is related to fitness
        if self.is_fitness_related(current_message):
            fitness_info = self.extract_fitness_info(current_message)
            print("=====================================")
            print("=== Extracted Fitness Information ===")
            if fitness_info:
                print(f"Muscle: {fitness_info.muscle}")
                print(f"Duration: {fitness_info.duration} hours")
            print("=====================================")

        messages = []
        if history:
            for msg in history:
                converted_message = self.gradio_to_messages(msg)
                if converted_message:
                    messages.append(converted_message)
        messages.append({"role": "user", "content": current_message})

        return self.chat(messages)

    # Converting Gradio response format to messages format
    # Gradio's chat interface contains more informations in content like the `type` and the actual `text` when OpenAI API format contains only a string in `content`.
    def gradio_to_messages(self, message):
        role = message.get("role")
        content = message.get("content")

        # Content is already a string (OpenAI API format)
        if isinstance(content, str):
            return {"role": role, "content": content}

        # Content is a list (Gradio format)
        if isinstance(content, list):
            if len(content) > 0 and isinstance(content[0], dict):
                text = content[0].get("text", "")  # Extracting the actual text
                return {"role": role, "content": text}  # Return in OpenAI API format

        return None
