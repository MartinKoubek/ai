import streamlit as st
import chromadb
from langchain_community.vectorstores import Chroma
from chromadb.config import Settings

from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_community.chat_models.oci_generative_ai import ChatOCIGenAI
from langchain_community.embeddings import OCIGenAIEmbeddings
from LoadProperties import LoadProperties

#In this demo we will explore using RetirvalQA chain to retrieve relevant documents and send these as a context in a query.
# We will use Chroma vectorstore.

#Step 1 - this will set up chain , to be called later

def create_chain(search_type="mmr", search_kwargs={"k": 5}, max_history_messages=5):
    properties = LoadProperties()
    client = chromadb.HttpClient(host="127.0.0.1",settings=Settings(allow_reset=True))
    embeddings = OCIGenAIEmbeddings(
    model_id=properties.getEmbeddingModelName(),
    service_endpoint=properties.getEndpoint(),
    compartment_id=properties.getCompartment(),
    )
    db = Chroma(client=client, embedding_function=embeddings)
    retv = db.as_retriever(serach_type=search_type, search_kwargs=search_kwargs)

    llm = ChatOCIGenAI(
        model_id=properties.getModelName(),
        service_endpoint=properties.getEndpoint(),
        compartment_id=properties.getCompartment(),
        model_kwargs={"max_tokens": 500, "prompt_truncation": "AUTO_PRESERVE_ORDER"}  # Enable truncation
        )
    memory = ConversationBufferMemory(
        llm=llm,
        memory_key="chat_history",
        return_messages=True,
        output_key='answer',
        max_memory_size=max_history_messages) # Limit chat history

    qa = ConversationalRetrievalChain.from_llm(
        llm,
        retriever=retv,
        memory=memory,
        return_source_documents=True)

    return qa

#Step 2 - create chain, here we create a ConversationalRetrievalChain.

chain = create_chain()

#Step 3 - here we declare a chat function
def chat(llm_chain, user_input):
    # generate a prediction for a prompt
    bot_json = llm_chain.invoke(user_input)
    print("bot json is ->", bot_json )
    return {"bot_response": bot_json}

#Step 4 - here we setup Streamlit text input and pass input text to chat function.
# chat function returns the response and we print it.

if __name__ == "__main__":
    st.subheader("Welcome to ChatBot with BUGDB")
    col1 , col2 = st.columns([4,1])

    # Add widgets for dynamic search_type and search_kwargs
    #st.sidebar.subheader("Search Settings")
    #search_type = st.sidebar.selectbox("Search Type", options=["mmr", "similarity", "hybrid"], index=0)
    #k_value = st.sidebar.slider("Number of Documents (k)", min_value=1, max_value=20, value=5)


    def initialize_session_state():
        if "llm_chain" not in st.session_state:
            st.session_state["llm_chain"] = create_chain()
            #st.session_state["llm_chain"] = create_chain(search_type=search_type, search_kwargs={"k": k_value})
            llm_chain = st.session_state["llm_chain"]
        else:
            llm_chain = st.session_state["llm_chain"]
        return llm_chain

    user_input = st.chat_input()
    with col1:
        #col1.subheader("------Ask me a question ------")
        #col2.subheader("References")
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if user_input:
            llm_chain = initialize_session_state()
            bot_response = chat(llm_chain, user_input)
            print("bot_response->\n", bot_response)
            st.session_state.messages.append({"role" : "chatbot", "content" : bot_response})

            for message in st.session_state.messages:
                st.markdown("**Question: " + message['content']['bot_response']['question'] + "**")

                st.write("Answer: ", message['content']['bot_response']['answer'])
            # with col2:
            #     st.chat_message("assistant")
            #     for doc in message['content']['bot_response']['source_documents']:
            #         st.write("Reference: ", doc.metadata['source'] )
