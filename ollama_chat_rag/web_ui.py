import streamlit as st
from chat_bot_core import ChatBotCore

class WebUi:
    def __init__(self):
        st.title("DeepSeek Chat Bot")
        with st.sidebar:
            st.header("⚙️ Configuration")
            self.model = st.selectbox("Choose Model", ["deepseek-r1:7b"], index=0)
            self.reasoning_enabled = st.toggle("Enable Reasoning", value=False)
            self.temperature = st.slider("Temperature", min_value=0.1, max_value=1.0, value=0.3, step=0.1)
            if st.button("Delete Chat History"):
                st.session_state.message_log = [{"role": "ai", "content": "Hi! I'm DeepSeek. How can I help you code today?"}]
                st.success("Chat history deleted!")

        if "message_log" not in st.session_state:
            st.session_state.message_log = [{"role": "ai", "content": "Hi! I'm DeepSeek. How can I help you code today?"}]

        system_prompt = "You are an expert AI coding assistant. Provide concise, correct solutions."
        self.chatbot = ChatBotCore(self.model, self.temperature, self.reasoning_enabled, system_prompt=system_prompt)

    def run(self):
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.message_log:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        user_query = st.chat_input("Type your coding question here...")
        if user_query:
            st.session_state.message_log.append({"role": "user", "content": user_query})
            self.chatbot.set_question(user_query)

            response_container = st.empty()
            full_response = ""
            for chunk in self.chatbot.get_streaming_answer():
                full_response = chunk  # Get latest streamed content
                response_container.markdown(full_response)

            st.session_state.message_log.append({"role": "ai", "content": full_response})

if __name__ == "__main__":
    webui = WebUi()
    webui.run()
