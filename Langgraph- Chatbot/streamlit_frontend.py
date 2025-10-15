import streamlit as st
from langgraph_backend.chatbot import chatbot,retrieve_all_threads
from langchain_core.messages import HumanMessage,AIMessage
import uuid

def gen_thread_id():
    thread_id  = uuid.uuid4()
    return thread_id

def reset_chat():
    thread_id = gen_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history'] = []

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

def load_convo(thread_id):
    state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
    return state.values.get("messages", []) 

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = gen_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = retrieve_all_threads()

add_thread(st.session_state['thread_id'])

st.sidebar.title("Langgraph Chatbot")

if st.sidebar.button("New Chat"):
    reset_chat()

st.sidebar.header("My conversations")

for thread_id in st.session_state['chat_threads']:
    if st.sidebar.button(str(thread_id)):
        st.session_state['thread_id'] = thread_id
        messages = load_convo(thread_id)

        temp_msgs = []

        for message in messages:
            if isinstance(message,HumanMessage):
                role = 'user'
            else:
                role = 'assistant'
            temp_msgs.append({'role':role,'content':message.content})

        st.session_state['message_history'] = temp_msgs



for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])


user_input = st.chat_input("type here")

if user_input:

    # first add the message to message history 
    st.session_state['message_history'].append({"role":"user","content":user_input})
    with st.chat_message("user"):
        st.text(user_input)

    CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']},
              "metadata":{
                  "thread_id": st.session_state["thread_id"]
              },
              "run_name":"chat_turn"
              }

    # first add the message to message history 
    
    with st.chat_message("assistant"):

        def ai_only_stream():
        
            for message_chunk,metadata in chatbot.stream(
                {'messages':[HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode='messages'
            ):
                if isinstance(message_chunk,AIMessage):
                    yield message_chunk.content
        ai_message = st.write_stream(ai_only_stream())

    st.session_state['message_history'].append({"role":"assistant","content":ai_message})
