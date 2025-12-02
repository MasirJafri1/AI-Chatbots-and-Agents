import os
import tempfile
import streamlit as st
from embedchain import App
from embedchain.loaders.github import GithubLoader
from dotenv import load_dotenv
load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")          # YOUR GitHub token
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

if not GITHUB_TOKEN:
    st.warning("Set GITHUB_TOKEN in your environment to allow GitHub repo loading.")
if not GROQ_API_KEY:
    st.warning("Set GROQ_API_KEY in your environment to use Groq LLMs.")
if not HF_API_KEY:
    st.info("Set HF_API_KEY if you want to use HF's embedding models.")

def get_loader():
    loader = GithubLoader(
        config={
            "token": GITHUB_TOKEN
        }
    )
    return loader

if "loader" not in st.session_state:
    st.session_state['loader'] = get_loader()

loader = st.session_state.loader

def make_db_path():
    ret = tempfile.mkdtemp(suffix="_chroma")
    print(f"Created Chroma DB at {ret}")
    return ret

def embedchain_bot(db_path):
    return App.from_config(
        config={
            "llm": {
                "provider": "groq",
                "config": {
                    "api_key": GROQ_API_KEY,
                    "model": "openai/gpt-oss-120b",
                    "stream": True
                }
            },
            # use some good embedders for better results 
            "embedder": {
                "provider": "huggingface",
                "config": {
                    "model": "sentence-transformers/all-MiniLM-L6-v2",
                    "api_key": HF_API_KEY,
                }
            },
            "vectordb": {
                "provider": "chroma",
                "config": {
                    "dir": db_path
                }
            }
        }
    )

st.title("Chat with GitHub Repository")
st.caption("Embedchain + Groq LLM for generation, Google for embeddings, Chroma for vector DB")

if "app" not in st.session_state:
    st.session_state['app'] = embedchain_bot(make_db_path())

app = st.session_state.app

git_repo = st.text_input("Enter the GitHub Repo (owner/repo)", type="default", help="e.g. MasirJafri1/AI-Chatbots-and-Agents")
if git_repo and ("repos" not in st.session_state or git_repo not in st.session_state.get("repos", [])):
    if "repos" not in st.session_state:
        st.session_state["repos"] = [git_repo]
    else:
        st.session_state.repos.append(git_repo)

    try:
        st.info(f"Adding {git_repo} to knowledge base...")
        app.add("repo:" + git_repo + " " + "type:repo", data_type="github", loader=loader)
        st.success(f"Added {git_repo} to knowledge base!")
    except Exception as e:
        st.error(f"Failed to add repo: {e}")

prompt = st.text_input("Ask any question about the GitHub Repo", "")
if prompt:
    try:
        answer = app.chat(prompt)
        st.write(answer)
    except Exception as e:
        st.error(f"Chat failed: {e}")
