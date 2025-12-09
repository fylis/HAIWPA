"""
Configuration settings for HAIWPA Chat Application.

All constants containing the number 1 are used for the main LLM model.
All constants containing the number 2 are used for the secondary LLM model which is used for the extraction of JSON data if needed.

"""

import os

# Configuration for HAIWPA Chat Application
LLM_SERVER_1_URL = "http://localhost:8000"
LLM_SERVER_2_URL = "http://localhost:8001"
MCP_SERVER_URL = "http://localhost:9000"
API_KEY = "haiwpa-key"

# Model configuration
MODEL_PATH_1 = "models/Llama-3.2-3B-Instruct-Q5_K_M.gguf"
MODEL_ALIAS_1 = "Llama 3.2 3B Instruct"
MODEL_PATH_2 = "models/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf"
MODEL_ALIAS_2 = "Llama 3.1 8B Instruct"
TEMPERATURE_1 = 0.7  # Less randomness, more predictable
TEMPERATURE_2 = 0.3
MAX_TOKEN = 512

# Gradio interface settings
GRADIO_SERVER_URL = "127.0.0.1"
GRADIO_SERVER_PORT = 7860

# JSON extraction context file
DATA_FOLDER = "data"
CONTEXT_FILE = "data/context.json"
