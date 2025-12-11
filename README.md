# HAIWPA
Hybrid AI Workout Planning Assistant

## Architecture
![HAIWPA_Architecture](images/HAIWPA.png)

## Requirements
- [Llama.cpp](https://github.com/ggml-org/llama.cpp)
- [SWI-Prolog](https://www.swi-prolog.org/)
- [Python](https://www.python.org/)
- [uv](https://docs.astral.sh/uv/)
- Compatible [.gguf](https://huggingface.co/docs/hub/en/gguf) model, from [HuggingFace](https://huggingface.co/)
> We have used `LLama-3.2-3B` model for this project.

## How to use

1. Clone the repository
``` bash
git clone https://github.com/HEI-courses/303.1_2025_LLM_MCP_Prolog_integration
```

2. Go to the `303.1_2025_LLM_MCP_Prolog_integration` folder
```bash
cd 303.1_2025_LLM_MCP_Prolog_integration
```

3. Synchronize the virtual environment
```bash
uv sync
```

4. Launch the llama.cpp server

```bash
llama-server -m model.gguf --host 0.0.0.0 --port 8081
```
    
> ⚠️ **Note:** If you change the port, make sure to update `LLM_SERVER_1_URL` in `config.py` accordingly (e.g., `http://localhost:YOUR_PORT`)


5. Launch the HAIWPA Chatbot
```bash
python haiwpa_chat.py
```

6. Access the Chatbot threw a web browser with `http://localhost:7860/` address.