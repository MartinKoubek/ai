import os
from langchain_ollama import ChatOllama
from langchain_core.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate,
    ChatPromptTemplate
)
from uuid import uuid4
# from langchain.evaluation import load_evaluator
from load_properties import LoadProperties

properties = LoadProperties()

unique_id = uuid4().hex[0:8]
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = f"DS ChatBot-854860df"
os.environ["LANGCHAIN_ENDPOINT"] = properties.langchain_endpoint
os.environ["LANGCHAIN_API_KEY"] = properties.langchain_key

class ChatBotCore:
    def __init__(self, model="deepseek-r1:7b", temperature=0.3, reasoning_enabled=False, system_prompt=""):
        self.model = model
        self.temperature = temperature
        self.reasoning_enabled = reasoning_enabled
        self._initialize_model()

        # self.evaluator = load_evaluator("qa")
        self.message_log = [{"role": "ai", "content": "Hi! I'm DeepSeek. How can I help you code today?"}]
        self.system_prompt = system_prompt

    def _initialize_model(self):
        self.llm_engine = ChatOllama(
            model=self.model,
            base_url="http://localhost:11434",
            temperature=self.temperature,
            streaming=True
        )

    def set_temperature(self, temperature):
        self.temperature = temperature
        self._initialize_model()

    def set_reasoning_enabled(self, reasoning_enabled):
        self.reasoning_enabled = reasoning_enabled

    def set_question(self, question):
        self.message_log.append({"role": "user", "content": question})

    def get_answer(self):
        for _ in self.get_streaming_answer():
            pass
        return self.message_log[-1]

    def get_streaming_answer(self):
        system_prompt = SystemMessagePromptTemplate.from_template(
            self.system_prompt + (" Include reasoning for your solutions." if self.reasoning_enabled else " Do not include reasoning or explanations.")
        )

        prompt_sequence = [system_prompt]
        for msg in self.message_log:
            if msg["role"] == "user":
                prompt_sequence.append(HumanMessagePromptTemplate.from_template(msg["content"]))
            elif msg["role"] == "ai":
                prompt_sequence.append(AIMessagePromptTemplate.from_template(msg["content"]))

        prompt_chain = ChatPromptTemplate.from_messages(prompt_sequence)
        processing_pipeline = prompt_chain | self.llm_engine

        full_response = ""
        for chunk in processing_pipeline.stream({}):
            if hasattr(chunk, "content"):
                full_response += chunk.content
                yield full_response

        self.message_log.append({"role": "ai", "content": full_response})

if __name__ == "__main__":
    system_prompt = "You are an expert AI coding assistant. Provide concise, correct solutions."
    chatbot = ChatBotCore(system_prompt=system_prompt)
    chatbot.set_question("Hello")
    print(chatbot.get_answer())
