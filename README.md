![!HAIWPA_Banner](images/HAIWPA_banner.png)

# HAIWPA
Hybrid AI Workout Planning Assistant is developped in the [Informatique et systèmes de communication](https://isc.hevs.ch/learn) Bachelor's degree program for the semester project.

## Overview
This project aims to develop a smart workout planning assistant that understands natural language requests from users and verifies whether a training session is appropriate based on physiological and logical constraints.

The core objective is to demonstrate a hybrid AI approach that combines symbolic reasoning (constraint logic programming) with generative models. By ensuring that **logical decisions computed by Prolog always take priority over generative output**, the system minimizes hallucinations commonly seen with standalone LLM usage. The LLM must not introduce unsupported conclusions or overlook constraint violations detected by symbolic reasoning.

## Table of contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Requirements](#requirements)
- [How to use | User guide](#how-to-use--user-guide)
- [Documentation](#documentation)

## Architecture
The architecture of this project is composed with :

- **Gradio web interface** provides a chat-based user interface using the ChatInterface model. It enables interaction with natural language.
- **Python backend** is the central orchestration layer connecting all components. It handles the interaction flow between the Gradio interface, the LLM, and the MCP server. The main components are saving the LLM extracted information to the `context.json` file, interacting as an MCP client with the MCP server, as well as waiting for the Prolog answer to resend it to the LLM.
- **Llama.cpp** is the local LLM used to answer user queries with two different scenarios:
    * **Extracting workout information** in a JSON format.
    * **Answering** the user based on the Prolog reasoning.
- **FastMCP server** is used to transform information from the `context.json` file to Prolog queries as well as to send them to SWI-Prolog.
- **SWI-Prolog** is the Symbolic AI part in this project, which is meant to accept or refuse a workout based on the workout history and the future workouts of the user. To do this, simple predicates were created to answer the FastMCP queries.

![HAIWPA_Architecture](images/HAIWPA.png)

## Requirements
- [Llama.cpp](https://github.com/ggml-org/llama.cpp)
- [SWI-Prolog](https://www.swi-prolog.org/)
- [Python](https://www.python.org/)
- [uv](https://docs.astral.sh/uv/)
- [.gguf](https://huggingface.co/docs/hub/en/gguf) model

> Be sure, that `uv` is installed and added to the environment PATH.

> Llama.cpp contains multiple version to install, depending on the computer hardware, be sure to install the appropriate one (GPU or CPU).

> The LLM model used for this project is [`Llama-3.2-3B-Instruct-GGUF`](https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF), downloaded from [HuggingFace](https://huggingface.co/).

## How to use | User guide
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

4. Launch the Llama.cpp server in a terminal.

```bash
llama-server -m model.gguf --host 0.0.0.0 --port 8081
```
    
> ⚠️ **Note:** Please make sure that the port used in this command is the same as in `LLM_SERVER_1_URL` that can be found in `config.py`, if not, update it accordingly (e.g., `http://localhost:YOUR_PORT`)

5. Launch the FastMCP server.
```bash
uv run fastmcp run haiwpa_mcp.py --transport http --port 9000
```

6. Launch the HAIWPA Chatbot.
```bash
uv run haiwpa_chat.py
```

7. Access the Chatbot threw a web browser with [`http://localhost:7860/`](http://localhost:7860/) address.

![!Gradio interface](images/gradio_interface.png)

## Developper guide
This section is for developpers that would be interested to update or modify the actual project.

### Code structure
Here is a short description for each folder/file that can be found after the repository clone.
```bash
├── data/                   # Folder containing workout history
├──── context.json          # Workout history and future workout(s)
├── images/                 # Folder containing images for the README.md
├── config.py               # Constants file
├── haiwpa_backend.py       # Backend module
├── haiwpa_chat.py          # Gradio web interface module
├── haiwpa_mcp.py           # MCP Server used to interact with SWI-Prolog
├── haiwpa_workout.py       # Workout extraction to `context.json` file
├── pyproject.toml          # Project configuration file
├── README.md               # Project overview, user guide, developper guide, etc.
└── workout_rules.pl        # SWI-Prolog predicates
```

### Workflow

### config.py
This file contains constants used along all modules.

```python
LLM_SERVER_1_URL = "http://localhost:8081"
MCP_SERVER_URL = "http://localhost:9000"
GRADIO_SERVER_URL = "127.0.0.1"
...
FITNESS_KEYWORDS = "biceps, triceps, ..."
LLM_CONTEXT_FOR_ANSWER =  "WORKOUT VALIDATION :\n" + ...
```

### haiwpa_backend.py

### haiwpa_chat.py
This module uses the `gradio` library, the `HAIWPABackend` class from `haiwpa_backend.py`, and the `config` module.

It provides the Gradio ChatInterface for user interaction with the local LLM. The `chat_function()` function handles the communication between the user and the backend.

This function takes the user input (a prompt written in natural language) and the conversation history (empty at the beginning) as parameters.

```python
# Main function which is used to answer user prompts with message history
async def chat_function(user_input, history):
    return await backend.chat_with_history(user_input, history)
```

The function that makes the interaction between the Gradio Interface and the backend is found in `create_interface()`.

```python
def create_interface():
    demo = gr.ChatInterface(
        fn=chat_function, title="HAIWPA Chat", description="Chat with the HAIWPA model."
    )
    return demo
```

### haiwpa_workout.py
This module uses Pydantic's `BaseModel` and `Field` as main components to extract information from the user's natural language prompt.

When the system detects a fitness-related message (via the backend's `is_fitness_related()` function), it calls the Llama.cpp server to extract the following fields:

```python
# Class to extract fitness exercises, duration limits, recent training history, injuries from user input
muscle: str = Field(description="...")
exercises: str = Field(description="...")
duration: float = Field(description="...", default=0.0)
date: str = Field(description="...", default={today_date()})
injuries: str = Field(description="...", default="")
entry_type: str = Field(description="...")
```

The most important part in this file is the description of each field. Since the LLM is a statistical system that predicts output based on input context, the goal is to extract information from the prompt without hallucination. To achieve this, we need to ensure that the LLM understands correctly what has to be done and how it should be formatted.

The muscle, exercises, injuries as well as the duration are normally easy to extract, because it is straightforward, we do not need to manipulate them.

However, the **date** field is more vulnerable to errors. By default, the LLM does not know what "today", "yesterday", or "in some days" means. This information must be provided explicitly. For this project, the `today_date()` function was created to inject the current date when the user sends the prompt.

This function returns a date in the US format like `2025-12-16`.
```python
def today_date() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d")
```

The next description that is as important as the date is the **entry_type**. It defines whether the user is talking about a past workout or a future one. This distinction is crucial for the MCP server to determine which muscle groups require Prolog validation.

Once, the extraction done, the next is to save it for future uses like the MCP conversion to Prolog. It could be done without saving into the JSON file, but it helps with debug.

Here is an example of correctly extracted content that is saved in the `context.json` :
```json
[
    {
        "timestamp": "2025-12-16T09:37:16.861858",
        "user_input": "Hello, I worked biceps curls for 10 minutes today. I want to know if I can work my triceps today?",
        "muscle": "biceps",
        "exercises": "biceps curls",
        "duration": 10.0,
        "date": "2025-12-16",
        "injuries": "",
        "entry_type": "completed"
    },
    {
        "timestamp": "2025-12-16T09:37:16.861858",
        "user_input": "Hello, I worked biceps curls for 10 minutes today. I want to know if I can work my triceps today?",
        "muscle": "triceps",
        "exercises": "",
        "duration": 0.0,
        "date": "2025-12-16",
        "injuries": "",
        "entry_type": "planned"
    },
  ...
]
```

### haiwpa_mcp.py
This module contains the FastMCP server, the JSON input reading, and serves as a bridge between the backend and SWI-Prolog.

It uses the `fastmcp` library to create the FastMCP server and the `pyswip` library to interact with SWI-Prolog.

At the beginning, a check is performed to ensure that Prolog rules are accessible by using the `connection_test` query.

```python
# Load Prolog knowledge base
prolog.consult("workout_rules.pl")

# Unit test to check if the connexion with Prolog worked
list(prolog.query("connection_test."))
```

If we do not see :
```bash
Workout rules module loaded successfully.
```

Then the connection failed and we will not be able to interact with SWI-Prolog.

Once the connection is established, the next step is cleaning the SWI-Prolog knowledge base and initializing it with workout history. The `load_json_workout_context()` function handles this.

It requires the JSON file path found in the config file as `config.CONTEXT_FILE`.
```python
# Load JSON workout context from file and assert into Prolog knowledge base
def load_json_workout_context(file_path=config.CONTEXT_FILE):
    ...
    # Clearing previous data in SWI-Prolog
    list(prolog.query("retractall(workout_history(_, _, _, _))."))
    list(prolog.query("retractall(injury(_, _))."))

    planned_workout = []

    # Load JSON data
    with open(file_path, "r") as f:
        data = json.load(f)

    # JSON data parsing
    for entry in data:
        ...
        entry_type = entry["entry_type"]
        ...
        if entry_type == "completed":
        elif entry_type == "planned":

    return planned_workout
```

From there, the workout history is sent to Prolog. The next step is to validate a muscle based on its name and the date the user wants to train it. The `validate_single_workout()` function handles this.

```python
# Validate if a workout for a specific muscle group is allowed on a given date (yes/no).
# It returns {"approved": bool, "reason": str}
def validate_single_workout(muscle: str, date: str):
    ...

    query = f"can_workout(...)."
    results = list(prolog.query(query))

    if results:
        reason = results[0]["Reason"]

        if reason == "workout_allowed":
        elif reason == "injury_present":
        elif reason == "trained_together_injured":
        elif reason == "insufficient_rest":
        ...

    return ...
```

At this point, the MCP server has the answer from Prolog reasoning and needs to send it to the backend. Before doing so, the **Reason** must be reformatted into a natural language explanation instead of raw Prolog predicate results. This provides more context for the LLM rather than just keywords.

The last part of this module is the `validate_all_planned_workouts()` function, which validates all planned muscle workouts instead of just one. This is the main MCP function and requires the `@mcp.tool()` decorator so that an MCP client can call it.

```python
# MCP Tool to validate all planned workouts from the JSON context file
# It returns a list of validation results for each planned workout
@mcp.tool()
def validate_all_planned_workouts():
    planned_workouts = load_json_workout_context()
    results = []
    max_rest_days = 0

    if not planned_workouts:
        return results

    # Getting the max rest from Prolog
    max_rest_days_query = list(prolog.query("suggested_rest_days(MaxRestDays)."))
    max_rest_days = max_rest_days_query[0]["MaxRestDays"]
    ...

    for workout in planned_workouts:
        validation = validate_single_workout(workout["muscle"], workout["date"])
        results.append(
            ...
        )

    return results
```

Prolog works with UNIX timestamps, but dates in `context.json` are saved in ISO format. The `convert_date_to_timestamp()` function ensures correct conversion before sending data to Prolog. It also handles EU format dates (DD.MM.YYYY) by converting them to ISO format first.

```python
# Used to convert a US date to UNIX timestamp
def convert_date_to_timestamp(date_str: str):
    # if date_str looks like "DD.MM.YYYY", convert it to the format "YYYY-MM-DD"
    if "." in date_str:
        day, month, year = date_str.split(".")
        date_str = f"{year}-{month}-{day}"
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return int(dt.timestamp())  # Convert to UNIX timestamp
```

There are also two helper functions:
- `suggest_workout()` - Sends a query to Prolog that returns a list of suggested alternatives for a muscle group that cannot be trained (due to injury or insufficient rest).
- `format_suggested_workout()` - Formats the list of alternatives into a comma-separated string.

### workout_rules.pl
This Prolog file contains all the symbolic AI part with predicats, etc.

### Unit tests

## Future upgrades
For future upgrades, I would like to implement the following improvements:
- More realistic Prolog rules, enabling better reasoning based on real-world information rather than synthetic data.
- Additional MCP tools for interacting with the SWI-Prolog knowledge base, such as simple queries to retrieve all exercises targeting a specific muscle group (e.g., biceps), the minimum required rest days, and similar information.
- An improved mechanism for saving context.json and updating workout statuses from “planned” to “completed” automatically after a certain time. Currently, the file must be cleared for the system to function properly, as it stores all fitness-related information extracted from user prompts that could be falsified.
- A more robust method for extracting dates and times from user prompts. At present, when a user provides a date, the time is ignored. This can lead to inconsistencies, for example when a workout completed at 23:59 is considered valid again at midnight, since only the day (ISO format) is being checked and not the full timestamp.

## Conclusion

## Acknowledgements
For the proper monitoring of the project, the instructions provided, and for answering all questions related to the project, whether concerning progress or code, I would like to thank **Davide Calvaresi** and **Elia Pacioni**. I would also like to thank them for providing access to a computational server and for all the intermediate meetings and suggestions, which were very helpful throughout the project.

## Sources
- [LLaMa : OpenAI compatibility](https://llama.developer.meta.com/docs/features/compatibility/)
- [Instructor : Structured Output for Open Source and Local LLMs](https://python.useinstructor.com/blog/2024/03/07/open-source-local-structured-output-pydantic-json-openai/#groq)
- [Gradio : Creating a Chatbot Fast](https://www.gradio.app/guides/creating-a-chatbot-fast)
- [FastMCP : Quickstart](https://gofastmcp.com/getting-started/quickstart)
- [YouTube : MCP Complete Tutorial - Connect Local AI Agent (Ollama) to Tools with MCP Server and Client
](https://www.youtube.com/watch?v=aiH79Q-LGjY)
- [YouTube : LLMs + Instructor: Generate Structured Output in Python Easily](https://www.youtube.com/watch?v=VllkW63LWbY)
- [SWI-Prolog : Predicate findall/3](https://www.swi-prolog.org/pldoc/man?predicate=findall/3)
- [SWI-Prolog : Predicate max_list/2](https://www.swi-prolog.org/pldoc/man?predicate=max_list/2)
- Claude AI was used for error analyzing, debugging and suggesting code updates.
- ChatGPT was used to create the **lama doing bench press** image which is used in the banner.