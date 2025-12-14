"""
HAIWPA Chat Application
A Gradio-based chat interface for interacting with the HAIWPA backend.
It uses the HAIWPABackend class to handle chat functionality with the `chat_with_history` function.

Source :
- https://www.gradio.app/guides/creating-a-chatbot-fast

Assistant : Claude
"""

import gradio as gr
from haiwpa_backend import HAIWPABackend
import config

backend = HAIWPABackend()


async def chat_function(user_input, history):
    return await backend.chat_with_history(user_input, history)


def create_interface():
    demo = gr.ChatInterface(
        fn=chat_function, title="HAIWPA Chat", description="Chat with the HAIWPA model."
    )
    return demo


def launch():
    demo = create_interface()
    demo.launch(
        server_name=config.GRADIO_SERVER_URL, server_port=config.GRADIO_SERVER_PORT
    )


if __name__ == "__main__":
    launch()
