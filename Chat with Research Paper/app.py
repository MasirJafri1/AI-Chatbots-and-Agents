import streamlit as st
from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.arxiv import ArxivTools
from dotenv import load_dotenv
import os
load_dotenv()

os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

st.title("Chat with the Reasearch Paper")
st.caption("This app allows you to chat with the arXiv research paper using the groq model")

assistant = Agent(
model=Groq(id="openai/gpt-oss-120b",api_key=os.environ["GROQ_API_KEY"]),tools=[ArxivTools()]
)

query = st.text_input("Enter the Search Query",type="default")

if query:
    response = assistant.run(query,stream=False)
    st.write(response.content)