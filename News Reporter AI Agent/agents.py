from crewai import Agent,LLM
from dotenv import load_dotenv
from tools import tool
import os

load_dotenv()
from langchain_google_genai import ChatGoogleGenerativeAI
import os

llm = LLM(model="gemini-2.0-flash")   # use CrewAI's LLM API so CrewAI can manage litellm fallback

researcher = Agent(
    role="Senior Researcher",
    goal="uncover ground breaking technologies in {topic}",
    verbose=True,
    memory=True,
    backstory=(
        "Driven by curiosity, you're at the forefront of innovation,eager to explore and share knowledge that could change the world"
    ),
    tools=[tool],
    llm=llm,
    allow_delegation=True
)

writer = Agent(
    role="Writer",
    goal="Narrate compelling tech stories about the {topic}",
    verbose=True,
    memory=True,
    backstory=(
        "With a flair for simplifying complex topics, you craft engaging narratives that are captative and educate, bringing new discoveries to light in an accessible manner"
    ),
    tools=[tool],
    llm=llm,
    allow_delegation=False
)
