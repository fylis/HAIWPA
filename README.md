![!HAIWPA_Banner](images/HAIWPA_banner.png)

# HAIWPA
Hybrid AI Workout Planning Assistant is a project developped for the semester project in the Informatique et systèmes de communication Bachelor's degree program.

## Architecture
![HAIWPA_Architecture](images/HAIWPA.png)

## Requirements
- [Llama.cpp](https://github.com/ggml-org/llama.cpp)
- [SWI-Prolog](https://www.swi-prolog.org/)
- [Python](https://www.python.org/)
- [uv](https://docs.astral.sh/uv/)
- [.gguf](https://huggingface.co/docs/hub/en/gguf) model

> Be sure, that `uv` is installed and added to the environment PATH.

> The LLM model used for this project is [`Llama-3.2-3B-Instruct-GGUF`](https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF), downloaded from [HuggingFace](https://huggingface.co/).

## How to use / User guide

1. Clone the repository.
``` bash
git clone https://github.com/HEI-courses/303.1_2025_LLM_MCP_Prolog_integration
```

2. Go to the `303.1_2025_LLM_MCP_Prolog_integration` folder.
```bash
cd 303.1_2025_LLM_MCP_Prolog_integration
```

3. Synchronize the virtual environment.
```bash
uv sync
```

4. Launch the llama.cpp server.

```bash
llama-server -m model.gguf --host 0.0.0.0 --port 8081
```
    
> ⚠️ **Note:** If you change the port, make sure to update `LLM_SERVER_1_URL` in `config.py` accordingly (e.g., `http://localhost:YOUR_PORT`)

5. Launch the FastMCP server.
```bash
uv run fastmcp run haiwpa_mcp.py --transport http --port 9000
```

6. Launch the HAIWPA Chatbot.
```bash
uv run haiwpa_chat.py
```

7. Access the Chatbot threw a web browser with [`http://localhost:7860/`](http://localhost:7860/) address.