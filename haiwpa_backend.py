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

from openai import OpenAI
from haiwpa_workout import MultipleFitnessExtract
import config
import instructor


class HAIWPABackend:
    def __init__(self):
        self.client = OpenAI(
            base_url=f"{config.LLM_SERVER_1_URL}/v1", api_key=config.API_KEY
        )

        # Used for structured JSON extraction
        self.instructor_client = instructor.from_openai(
            OpenAI(base_url=f"{config.LLM_SERVER_1_URL}/v1", api_key=config.API_KEY),
            mode=instructor.Mode.JSON,
        )
        self.model_name = config.MODEL_ALIAS_1
        self.temperature = config.TEMPERATURE_1
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
        fitness_keywords = config.FITNESS_KEYWORDS
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
                response_model=MultipleFitnessExtract,
                temperature=config.TEMPERATURE_2,
                max_tokens=self.max_tokens,
                max_retries=3,
            )
            if response and hasattr(response, "sessions"):
                return response.sessions
            return None
        except Exception as e:
            print("Not able to extract fitness information")
            print(f"\nError: {e}")
            return None

    # Adds the user/bot message history to the current message and gets a response
    def chat_with_history(self, current_message, history):
        # Printing fitness extraction informations from user prompts only if the message is related to fitness
        if self.is_fitness_related(current_message):
            print("Starting the extraction process...")
            fitness_sessions = self.extract_fitness_info(current_message)
            if fitness_sessions:
                for session in fitness_sessions:
                    session.print_extracted_info()
                    session.save_to_json(current_message)

        # Converting Gradio history format to messages format before sending to the LLM
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
