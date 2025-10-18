from uipath_langchain.chat.models import UiPathAzureChatOpenAI
from langgraph.graph import START, StateGraph, MessagesState, END
from langgraph.prebuilt import create_react_agent
from langchain.tools.retriever import create_retriever_tool
from uipath_langchain.retrievers import ContextGroundingRetriever
from pydantic import BaseModel
from uipath import UiPath

# Create UiPath client
client = UiPath()

# Define the input and output schemas
class StateSchema(BaseModel):
    user_prompt: str = "What is the capital of France?"
    system_prompt: str = "You are a helpful assistant that can answer questions and help with tasks. Use tools provided to you to answer the user's question."
    response: str = ""
    index_name: str = ""
    folder_path: str = ""
    number_of_results: int = 3

class GraphInput(BaseModel):
    user_prompt: str
    system_prompt: str
    index_name: str = ""
    folder_path: str = ""
    number_of_results: int = 3

class GraphOutput(BaseModel):
    response: str

# Set model to use UiPath AI Trust Layer connection
llm_model = UiPathAzureChatOpenAI(
                    model="gpt-4o-2024-08-06",
                    temperature=0,
                    max_tokens=4000,
                    timeout=30,
                    max_retries=2
                    )


# Create core agent that will use tools dynamically
def create_agent_with_retriever(index_name: str, folder_path: str, number_of_results: int, system_prompt: str):
    tools = []
    
    # Only create retriever tool if both index_name and folder_path are provided
    if index_name and folder_path:
        # Create retriever tool for Context Grounding connection
        retriever = ContextGroundingRetriever(
                        index_name=index_name,
                        folder_path=folder_path,
                        number_of_results=number_of_results
                        )
        retriever_tool = create_retriever_tool(
            retriever,
            "Context",
           """
           Use this tool to search for relevant information in the context.
           """
        )
        tools.append(retriever_tool)
    
    return create_react_agent(
                llm_model, 
                tools=tools, 
                prompt=system_prompt,
            )

#Define the asynchronous function for the UiPath agent
async def uipath_agent(state: StateSchema) -> StateSchema:
    # Create agent with retriever configuration from state
    agent = create_agent_with_retriever(
        state.index_name,
        state.folder_path, 
        state.number_of_results,
        state.system_prompt
    )
    # Invoke the agent with the user prompt
    result = await agent.ainvoke(MessagesState(messages=[{"role": "user", "content": state.user_prompt}]))
    return StateSchema(response=result["messages"][-1].content)

# Build the state graph
builder = StateGraph(state_schema=StateSchema, input=GraphInput, output=GraphOutput)

builder.add_node("uipath_agent", uipath_agent)

builder.add_edge(START, "uipath_agent")

builder.add_edge("uipath_agent", END)

# Compile the graph
graph = builder.compile()
