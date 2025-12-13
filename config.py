"""
Configuration settings for HAIWPA Chat Application.

All constants containing the number 1 are used for the main LLM model.
All constants containing the number 2 are used for the secondary LLM model which is used for the extraction of JSON data if needed.

"""

import os

# Configuration for HAIWPA Chat Application
LLM_SERVER_1_URL = "http://localhost:8081"
MCP_SERVER_URL = "http://localhost:9000"
API_KEY = "haiwpa-key" # Used locally for authentication between services

# Model configuration
MODEL_PATH_1 = "models/Llama-3.2-3B-Instruct-Q5_K_M.gguf"
MODEL_ALIAS_1 = "Llama 3.2 3B Instruct"
TEMPERATURE_1 = 0.7  # Less randomness, more predictable
TEMPERATURE_2 = 0.3
MAX_TOKEN = 2048

# Gradio interface settings
GRADIO_SERVER_URL = "127.0.0.1"
GRADIO_SERVER_PORT = 7860

# JSON extraction context file
DATA_FOLDER = "data"
CONTEXT_FILE = "data/context.json"

# Fitness-related keywords
FITNESS_KEYWORDS = [
 "workout", "exercise", "training", "gym", "fitness",
 "muscle", "cardio", "strength", "injury", "rest",
 "squat", "bench", "deadlift", "curl", "press",
 "chest", "back", "legs", "arms", "shoulders",
 "biceps", "triceps", "abs", "core", "glutes",
 "run", "running", "jog", "swim", "cycling",
 "duration", "minutes", "hours", "sets", "reps",
]