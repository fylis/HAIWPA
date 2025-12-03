"""
Configuration settings for HAIWPA Chat Application.
"""

import os

# Configuration for HAIWPA Chat Application
SERVER_URL = "http://localhost:8000"
API_KEY = "haiwpa-key"

# Model configuration
MODEL_PATH = "models/Llama-3.2-3B-Instruct-Q5_K_M.gguf"
MODEL_ALIAS = "Llama 3.2 3B Instruct"
TEMPERATURE = 0.7  # Less randomness, more predictable
MAX_TOKEN = 512

# Gradio interface settings
GRADIO_SERVER_URL = "127.0.0.1"
GRADIO_SERVER_PORT = 7860

# JSON extraction context file
CONTEXT_FILE = "data/context.json"
