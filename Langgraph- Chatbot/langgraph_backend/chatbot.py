from langgraph.graph import StateGraph,START,END
from langchain_groq import ChatGroq
import os 
from dotenv import load_dotenv
from typing import TypedDict,Annotated
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
import sqlite3

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

llm = ChatGroq(model="llama-3.3-70b-versatile",api_key=groq_api_key)

class ChatState(TypedDict):
    messages : Annotated[list[BaseMessage],add_messages] 

def chat_node(state:ChatState):
    messages = state["messages"]
    response = llm.invoke(messages)
    return {"messages":[response]}

conn = sqlite3.connect(database="chatbot",check_same_thread=False)

checkpointer = SqliteSaver(conn=conn)

graph = StateGraph(ChatState)
graph.add_node("chat_node",chat_node)

graph.add_edge(START,"chat_node")
graph.add_edge("chat_node",END)

chatbot = graph.compile(checkpointer=checkpointer)


def retrieve_all_threads():
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']["thread_id"])
    return list(all_threads)