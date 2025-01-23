from langchain_core.messages import HumanMessage, BaseMessage, SystemMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_ollama import ChatOllama
from typing import Optional, List
from .tools.rag_law_tool import get_law_rag_answer
from .tools.rag_system_tool import get_system_rag_answer
from langchain_openai import ChatOpenAI
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper
from langchain_community.tools.tavily_search.tool import TavilySearchResults

def create_agent_executor():
    """
    Create an agent executor with a memory module and a model instance.
    
    Returns:
        agent_executor: A configured agent executor ready to handle queries.
    """
    memory = MemorySaver()
    # Tools should be placed at "root/tools/..."
    search = TavilySearchAPIWrapper()
    tavily_tool = TavilySearchResults(api_wrapper=search, max_results=2)
    tools = [get_law_rag_answer, get_system_rag_answer, tavily_tool]
    # You can change the LLM model in here
    # model = ChatOllama(model="llama3.2", temperature=0.8)
    model = ChatOpenAI(model="gpt-4o", temperature=0.8)
    agent_executor = create_react_agent(model, tools, checkpointer=memory)

    return agent_executor 

def get_agent_answer(question: str,thread_id: Optional[str]= "anon",history: Optional[List[BaseMessage]] = None):
    """
    Run the agent for a specific user session and process its responses.
    
    Args:
        question: Input the question to agent
        thread_id: Optional thread ID for session tracking.
        history: Optional list of prior messages for context initialization.
    """
    agent_executor = create_agent_executor()
    config = {"configurable": {"thread_id": thread_id}}  # Configuration for session ID
    
    if history is not None :
        agent_executor.update_state(config, {"messages": history})

    sys_prompt = '''
        採用繁體中文回應，你是船舶安全助理。請以清晰、簡潔、準確的方式回答用戶的問題。
        你可以呼叫tools來查詢文件，或者直接回答用戶的問題。
        查詢文件請以關鍵字開頭，加上相關內容系統採用 RAG 模型協助查詢。
    '''
    agent_executor.update_state(config, {"messages": SystemMessage(content=sys_prompt)})
    response = agent_executor.invoke({"messages": [HumanMessage(content=question)]}, config)

    return response['messages'][-1].content

def cmd_agent():
    """
    Run the agent in a command-line interactive session, allowing users to ask questions.
    Users can type 'Q' or 'q' to exit the conversation.
    """
    # Initialize the agent executor and session configurations
    agent_executor = create_agent_executor()
    thread_id = "anon"  # Default thread ID for session tracking
    history: List[BaseMessage] = []  # To keep the history of the conversation
    config = {"configurable": {"thread_id": thread_id}}

    # Initial system prompt (you can customize this)
    sys_prompt = '''
    You are a helpful assistant. Answer the user's questions concisely and accurately.
    '''
    agent_executor.update_state(config, {"messages": [SystemMessage(content=sys_prompt)]})
    
    print("Interactive Agent (type 'Q' or 'q' to quit):\n")
    
    while True:
        # User input
        question = input("You: ").strip()
        if question.lower() == 'q':
            print("Exiting... Goodbye!")
            break
        
        # Add user's input to the history
        history.append(HumanMessage(content=question))
        
        # Update the agent's state with the latest history
        agent_executor.update_state(config, {"messages": history})

        # Get the agent's response
        response = agent_executor.invoke({"messages": [HumanMessage(content=question)]}, config)
        ai_message = response['messages'][-1].content
        
        # Add the agent's response to the history
        history.append(AIMessage(content=ai_message))
        
        # Print the agent's response
        print(f"AI: {ai_message}")
    
if __name__=="__main__":
    cmd_agent()
    