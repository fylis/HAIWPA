# HAIWPA
Hybrid AI Workout Planning Assistant

## Requirements
- llama.cpp with a compatible .gguf model
- Python
- uv

## How to use

1. Clone the repository
``` bash
git clone https://github.com/fylis/HAIWPA
```

2. Go to the HAIWPA folder
```bash
cd HAIWPA
```

3. Synchronize the virtual environment
```bash
uv sync
```

4. Launch the llama.cpp server
    
    4.1 Using llama-cpp-python library
    ```bash
    python -m llama_cpp.server --model model.gguf --host 0.0.0.0 --port 8000
    ```

    4.1 Manually, if you have installed llama.cpp on your computer
    ```bash
    llama-server -m model.gguf --host 0.0.0.0 --port 8000
    ```

5. Launch the HAIWPA Chatbot
```bash
python haiwpa_chat.py
```

6. Access the Chatbot threw a web browser with `http://localhost:7860/` address.