import streamlit as st
import os
from agent import run_agent

st.set_page_config(page_title="AI Agent with RAG", layout="wide")
st.title("🤖 AI Agent with RAG & Tool Calling")

# Display current profile
profile = os.environ.get("LLM_PROFILE", "cloud")
st.sidebar.info(f"📍 Running in **{profile.upper()}** mode")
st.sidebar.write("Set `LLM_PROFILE=local` or `LLM_PROFILE=cloud` before starting the app")

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# User input
if user_input := st.chat_input("Ask a question about air quality, SOP documents, or other queries..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    with st.chat_message("user"):
        st.write(user_input)
    
    # Get agent response
    with st.chat_message("assistant"):
        response = run_agent(user_input)
        st.write(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
