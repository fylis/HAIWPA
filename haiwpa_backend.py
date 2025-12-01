"""
HAIWPA Backend
It uses a OpenAI client to interact with the HAIWPA model server.
This module defines the HAIWPABackend class, which provides methods to send prompts
to the model and receive responses, including handling message history.

Source :
- https://github.com/abetlen/llama-cpp-python/blob/main/examples/notebooks/Functions.ipynb
- https://llama.developer.meta.com/docs/features/compatibility/

Assistant : Claude
"""

from openai import OpenAI
import config


class HAIWPABackend:
    def __init__(self):
        self.client = OpenAI(base_url=f"{config.SERVER_URL}/v1", api_key=config.API_KEY)
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

    # Adds the user/bot message history to the current message and gets a response
    def chat_with_history(self, current_message, history):
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
                text = content[0].get("text", "") # Extracting the actual text
                return {"role": role, "content": text} # Return in OpenAI API format

        return None
