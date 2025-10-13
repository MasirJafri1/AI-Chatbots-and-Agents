from langgraph.graph import StateGraph,START,END
from langchain_groq import ChatGroq
import os 
from dotenv import load_dotenv
from typing import TypedDict,Annotated
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

llm = ChatGroq(model="llama-3.3-70b-versatile",api_key=groq_api_key)

class ChatState(TypedDict):
    messages : Annotated[list[BaseMessage],add_messages] 

def chat_node(state:ChatState):
    messages = state["messages"]
    response = llm.invoke(messages)
    return {"messages":[response]}

checkpointer = InMemorySaver()

graph = StateGraph(ChatState)
graph.add_node("chat_node",chat_node)

graph.add_edge(START,"chat_node")
graph.add_edge("chat_node",END)

chatbot = graph.compile(checkpointer=checkpointer)

