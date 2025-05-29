from uipath_langchain.chat.models import UiPathAzureChatOpenAI
from langchain_core.messages import HumanMessage, ToolMessage
from langgraph.graph import START, StateGraph, MessagesState, END
from langgraph.prebuilt import create_react_agent
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
from langgraph.types import interrupt, Command
from langchain.tools.retriever import create_retriever_tool
from uipath_langchain.retrievers import ContextGroundingRetriever
from pydantic import BaseModel
from uipath import UiPath
from uipath.models import CreateAction, InvokeProcess

# Create UiPath client
client = UiPath()

# Define the input and output schemas
class GraphInput(BaseModel):
    query: str

class GraphOutput(BaseModel):
    response: str

class State(MessagesState):
    message: str

# Set model to use UiPath AI Trust Layer connection
llm_model = UiPathAzureChatOpenAI(
                    model="gpt-4o-2024-08-06",
                    temperature=0,
                    max_tokens=4000,
                    timeout=30,
                    max_retries=2
                    )

#llm_model = ChatOpenAI(model="gpt-4o")

# Set System Prompt for agent
system_prompt = '''You are an expert security analyst. You provide helpful context to junior analysts by describing the 
meaning of security codes and mapping them to internal controls using your external knowledge.
Follow this process:
1. Use your web search tool to find helpful info to summarize the overall meaning of the given NIST code for the user. Remember,
this user is likely a 25 year old new graduate from college, so they need a lot of detailed explanation in simple terms.

2. Use your context for technical requirement mappings to tell the user what internal requirements are mapped to this control.

Return the response as a JSON structure with codeExplanation (str - explanation of the NIST code) and techRequirements (list of tech requirements - 
list of mapped technical requirements).

IMPORTANT: If you determine that the NIST code provided as the input is not a valid NIST code you MUST escalate using your escalation tool.'''

# Create retriever tool for Context Grounding connection
retriever = ContextGroundingRetriever(
                index_name = "TRMappings",
                folder_path="Demos/EFX",
                number_of_results=3
                )
retriever_tool = create_retriever_tool(
    retriever,
    "ContextforTechnicalReqMappings",
   """
   Use this tool to search for mappings of NIST codes to technical requirement IDs.
   """
)

# Set up the Tavily search tool
# tavily_tool = TavilySearchResults(max_results=5)

@tool
def invoke_uipath_process(query: str) -> str:
    """This is your web search tool to research the NIST code."""
    agent_response = interrupt(InvokeProcess(
        name="WebSearchRPA",
        process_folder_path="Shared",
        input_arguments={"query": query}))
    print(agent_response)
    agent_message = ToolMessage(content=agent_response["results"])
    return Command(update={"messages": [agent_message]})

# Set up the human in the loop tool. This is used as a tool by the react agent to escalate to a human. 
# The agent decides when to use the escalation.
@tool
def human_in_the_loop(query: str) -> str:
    """This is your escalation tool to use if the NIST code provided is not valid."""
    action_data = interrupt(CreateAction(
        app_name="Agent Handler - IM",
        title="Escalation from Langgraph Agent",
        data={
                "Question": query,
                "AgentName": "LangGraph Agent",
                "Priority": "Low",
                "AssignedTeam": "The humans"
                },
        app_folder_path="Demos"
        ))
    
    return Command(update={"messages": [HumanMessage(content=action_data["Answer"])]})

tools = [retriever_tool,invoke_uipath_process, human_in_the_loop]

# Create core agent that will use tools dynamically
agent = create_react_agent(
            llm_model, 
            tools=tools, 
            prompt=system_prompt,
        )

#Define the asynchronous function for the UiPath agent
async def uipath_agent(state: GraphInput) -> GraphOutput:

    user_message = f'''Please process this request: {state.query}'''
    
    new_state = MessagesState(messages=[{"role": "user", "content": user_message}])

    result = await agent.ainvoke(new_state)

    return GraphOutput(response=result["messages"][-1].content)

# Build the state graph
builder = StateGraph(input=GraphInput, output=GraphOutput)

builder.add_node("uipath_agent", uipath_agent)

builder.add_edge(START, "uipath_agent")

builder.add_edge("uipath_agent", END)

# Compile the graph
graph = builder.compile()
