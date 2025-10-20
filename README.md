# UiPath LangGraph Agent

A simple example showing the pre-built react agent from LangGraph with UiPath tools, retrieval and HITL from the uipath-langchain sdk.
This example highlights the value of extensibility through code, balanced with speed to value in using pre-built, enterprise-grade UiPath components.

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

## Setup

1. Clone the repository
2. Run `uv sync` to install dependencies
3. Run `uipath auth` command to authenticate (don't forget the `--staging` flag if you're authenticating to a staging env)
4. RUn `uipath init` command to initialize
4. Set input values in `input.json`
5. Run `uipath run agent --file input.json` command to test locally in your IDE

## Deployment

- `uipath pack` - Package the agent
- `uipath publish` - Publish the agent

## Running from UiPath Orchestrator

Once the agent has been published, you can run it from UiPath Orchestrator:

![Configuration](config.png)