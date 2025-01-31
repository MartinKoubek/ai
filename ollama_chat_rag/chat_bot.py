import streamlit as st
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser

from langchain_core.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate,
    ChatPromptTemplate
)

st.title("DeepSeek Chat Bot")

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    selected_model = st.selectbox(
        "Choose Model",
        ["deepseek-r1:7b"],
        index=0
    )
    reasoning_enabled = st.toggle("Enable Reasoning", value=False)
    temperature = st.slider("Temperature", min_value=0.1, max_value=1.0, value=0.3, step=0.1)

    # Add a button to stop response
    if st.button("Stop response"):
        st.session_state.stop_response = True
        st.warning("Response generation stopped.")

    # Add a button to delete chat history
    if st.button("Delete Chat History"):
        st.session_state.message_log = [{"role": "ai", "content": "Hi! I'm DeepSeek. How can I help you code today? 💻"}]
        st.success("Chat history deleted!")


# initiate the chat engine

llm_engine=ChatOllama(
    model=selected_model,
    base_url="http://localhost:11434",
    temperature=temperature,
    streaming=True  # Enable streaming for incremental responses
)

# System prompt configuration
system_prompt = SystemMessagePromptTemplate.from_template(
    "You are an expert AI coding assistant. Provide concise, correct solutions "
    "with strategic print statements for debugging. Always respond in English."
    + (" Include reasoning for your solutions." if reasoning_enabled else " Do not include reasoning or explanations.")
)

# Session state management
if "message_log" not in st.session_state:
    st.session_state.message_log = [{"role": "ai", "content": "Hi! I'm DeepSeek. How can I help you code today? 💻"}]

# Initialize stop flag in session state
if "stop_response" not in st.session_state:
    st.session_state.stop_response = False

# Chat container
chat_container = st.container()

# Display chat messages
with chat_container:
    for message in st.session_state.message_log:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Chat input and processing
user_query = st.chat_input("Type your coding question here...")

def generate_ai_response(prompt_chain):
    processing_pipeline=prompt_chain | llm_engine | StrOutputParser()
    return processing_pipeline.invoke({})

def build_prompt_chain():
    prompt_sequence = [system_prompt]
    for msg in st.session_state.message_log:
        if msg["role"] == "user":
            prompt_sequence.append(HumanMessagePromptTemplate.from_template(msg["content"]))
        elif msg["role"] == "ai":
            prompt_sequence.append(AIMessagePromptTemplate.from_template(msg["content"]))
    return ChatPromptTemplate.from_messages(prompt_sequence)

if user_query:
    # Add user message to log
    st.session_state.message_log.append({"role": "user", "content": user_query})

    # Generate AI response
    with st.spinner("Processing..."):
        prompt_chain = build_prompt_chain()
        #ai_response = generate_ai_response(prompt_chain)

        processing_pipeline = prompt_chain | llm_engine

        # Stream the response
        response_container = st.empty()  # Placeholder for streaming response
        full_response = ""
        for chunk in processing_pipeline.stream({}):
            if st.session_state.stop_response:
                st.session_state.stop_response = False
                break  # Stop streaming if the stop button is clicked

            if hasattr(chunk, "content"):
                full_response += chunk.content
                response_container.markdown(full_response)


    # Add AI response to log
    st.session_state.message_log.append({"role": "ai", "content": full_response})

