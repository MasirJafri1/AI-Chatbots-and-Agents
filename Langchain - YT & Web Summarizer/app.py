import validators
import streamlit as st
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import UnstructuredURLLoader
from youtube_transcript_api import YouTubeTranscriptApi
from pytube import YouTube
from langchain.schema import Document

# Streamlit app
st.set_page_config(page_title="Summarize Text from YT or Website", layout="wide")
st.title("Summarize Text from YouTube or Website")
st.subheader("Enter any URL to generate a summary")

st.info("📌 Note: Only YouTube videos that have captions/transcripts can be summarized.")

# Sidebar for API key input
with st.sidebar:
    groq_api_key = st.text_input("Groq API Key", value="", type="password")

# Main input
generic_url = st.text_input("Enter YouTube or Website URL", label_visibility="collapsed")

# Prompt template
prompt_template = """
Provide a detailed summary of the following content in around 300 words:
Content:
{text}
"""
prompt = PromptTemplate(template=prompt_template, input_variables=["text"])

def get_youtube_transcript(url: str):
    try:
        yt = YouTube(url)
        video_id = yt.video_id
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        text = " ".join([t["text"] for t in transcript])
        return text
    except Exception as e:
        raise Exception(f"Unable to load YouTube transcript: {e}")

# Summarize button
if st.button("Summarize"):
    if not groq_api_key.strip() or not generic_url.strip():
        st.error("Please provide all the information correctly")
    elif not validators.url(generic_url):
        st.error("Please enter a valid URL (YouTube or Website)")
    else:
        try:
            with st.spinner("Loading content..."):
                # Load content
                if "youtube.com" in generic_url or "youtu.be" in generic_url:
                    text_data = get_youtube_transcript(generic_url)
                    if not text_data:
                        st.error("Unable to summarize this video.")
                        st.stop()
                    docs = [Document(page_content=text_data)]
                else:
                    loader = UnstructuredURLLoader(
                        urls=[generic_url],
                        ssl_verify=False,
                        headers={
                            "User-Agent": (
                                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                "AppleWebKit/537.36 (KHTML, like Gecko) "
                                "Chrome/124.0.0.0 Safari/537.36"
                            ),
                        },
                    )
                    docs = loader.load()

                llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=groq_api_key)

                # Summarize
                chain = load_summarize_chain(llm, chain_type="stuff", prompt=prompt)
                output_summary = chain.invoke({"input_documents": docs})

                st.success("Summary Generated Successfully!")
                st.write(output_summary["output_text"])

        except Exception as e:
            st.error(f"{e}")
