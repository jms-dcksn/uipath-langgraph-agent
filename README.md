# UiPath LangGraph Agent

A simple example showing the pre-built react agent from LangGraph with UiPath managed LLMs (AITL) and Context Grounding using the uipath-langchain sdk.
This example highlights the value of extensibility through code, and interoperability with enterprise-grade UiPath artifacts.

UiPath SDK docs: https://uipath.github.io/uipath-python/

## Agent Flow

```mermaid
---
config:
  flowchart:
    curve: linear
---
graph TD;
	__start__([<p>__start__</p>]):::first
	uipath_agent(uipath_agent)
	tool_node(uipath_context_grounding)
	__end__([<p>__end__</p>]):::last
	__start__ --> uipath_agent;
	uipath_agent -->|"needs tool"| tool_node;
	tool_node --> uipath_agent;
	uipath_agent -->|"complete"| __end__;
	classDef default fill:#f2f0ff,line-height:1.2
	classDef first fill-opacity:0
	classDef last fill:#bfb6fc
```

## Prerequisites

- **Python 3.10+**: Download from [python.org](https://www.python.org/downloads/) or use your system package manager
- **uv package manager**: Install with `pip install uv` or follow [uv installation guide](https://docs.astral.sh/uv/getting-started/installation/)

## Setup

1. Clone the repository (note this will create a folder in the current directory where your terminal is pointing)
   ```bash
   git clone https://github.com/jms-dcksn/uipath-langgraph-agent.git
   ```
2. Navigate to the project folder:
   ```bash
   cd uipath-langgraph-agent
   ```
3. Run `uv sync` to install dependencies:
   ```bash
   uv sync
   ```
4. Activate the virtual environment:
   - **Windows**: `.venv\Scripts\activate`
   - **macOS/Linux**: `source .venv/bin/activate`
5. Run `uipath auth` command to authenticate (don't forget the `--staging` flag if you're authenticating to a staging env):
   ```bash
   uipath auth
   ```
6. Run `uipath init` command to initialize:
   ```bash
   uipath init
   ```
7. (Optional) Set input values in `input.json` if you want to test locally
8. (Optional) Run `uipath run agent --file input.json` command to test locally in your IDE

## Deployment

- Modify the pyproject.toml file --> Append your initials to the name field e.g. name = "uipath-langgraph-agent-initials"
- `uipath pack` - Package the agent
- `uipath publish` - Publish the agent

## Running from UiPath Orchestrator

Once the agent has been published, you can run it from UiPath Orchestrator.
1. Create a process from the published package in your preferred folder.
2. Run the process
3. Enter the uesr and system prompts
4. Set the Context Grounding index name
5. Copy the folder path 

![Configuration](config.png)