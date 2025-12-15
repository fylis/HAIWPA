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
from haiwpa_mcp import format_suggested_workout
from fastmcp import Client
import json
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
        self.mcp_client = Client(f"{config.MCP_SERVER_URL}/mcp")

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

    def convert_validation_to_message(self, validation_results: str):
        res = "WORKOUT VALIDATION : \n"
        res += "RULE : \n"
        res += "At the beginning always write PROLOG VALIDATION with a YES (if approved=True) or NO (if approved=False) answer.\n and then give explanations based on the following validation results : \n "

        if not validation_results:
            return None

        for r in validation_results:
            muscle = r.get("muscle")
            date = r.get("date")

            validation = r.get("validation", {})
            approved = validation.get("approved")
            reason = validation.get("reason")
            max_rest_days = r.get("max_rest_days")

            if approved:
                res += f"- {muscle} on {date} : approved=True - {reason}\n"
            else:
                alternatives = validation.get("alternatives", [])
                res += f"- {muscle} on {date}: approved=False - {reason}\n"
                if alternatives:
                    alt = format_suggested_workout(alternatives)
                    res += f"  Suggested alternatives: {alt}\n"

                # Getting the max rest days
                res += f"Use this max rest days value : {max_rest_days} which is in days for the recent workout history. \n"

        return res + "Use those validation informations to answer."

    async def validate_workout_mcp(self, file_path: str = config.CONTEXT_FILE):
        try:
            async with self.mcp_client:
                result = await self.mcp_client.call_tool(
                    "validate_all_planned_workouts"
                )

                # Check if there is a result and returns the content from it because MCP returns a JSON format answer
                if result and result.content:
                    return json.loads(result.content[0].text)

                return result
        except Exception as e:
            # print(e)
            return None

    # Adds the user/bot message history to the current message and gets a response
    async def chat_with_history(self, current_message, history):
        # Used to store Prolog validation if there is any
        validation_context = ""

        # Printing fitness extraction informations from user prompts only if the message is related to fitness
        if self.is_fitness_related(current_message):
            print("Starting the extraction process...")
            fitness_sessions = self.extract_fitness_info(current_message)
            if fitness_sessions:
                for session in fitness_sessions:
                    session.print_extracted_info()
                    session.save_to_json(current_message)

                validation_results = await self.validate_workout_mcp()
                if validation_results:
                    validation_context = self.convert_validation_to_message(
                        validation_results
                    )

        # Converting Gradio history format to messages format before sending to the LLM
        messages = []
        if history:
            for msg in history:
                converted_message = self.gradio_to_messages(msg)
                if converted_message:
                    messages.append(converted_message)

        # role system used to add rules on how the LLM should answer
        if validation_context:
            messages.append({"role": "system", "content": validation_context})
            print("Validation context \n", validation_context, "\n")

        messages.append({"role": "user", "content": current_message})
        print("Message sent to LLM", messages)
        return self.chat(messages)
