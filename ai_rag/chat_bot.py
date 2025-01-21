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
        model_kwargs={"max_tokens": 500, "prompt_truncation": "AUTO_PRESERVE_ORDER"},  # Enable truncation
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

    default_prompt = (
        "You are a helpful support engineer. Please answer questions based on the data stored in Chroma DB. "
        "If you can't find relevant information, let the user know."
        "\n\nSample Prompts for Guidance:\n"
        "1. 'You are a support engineer. Please use Chroma DB to answer the following question. If you don't find relevant data, say, \"I'm sorry, I couldn't find the information you requested.\"'\n"
        "2. 'Act as a database assistant with access to Chroma DB. Use the stored data to answer the following query, providing references for any information you retrieve. If data is unavailable, let the user know and suggest alternative sources.'\n"
        "3. 'As a support engineer, analyze the user's query and retrieve relevant documents from Chroma DB. Use these documents to generate a comprehensive answer. If no documents match the query, explain this to the user and avoid making assumptions.'\n"
        "4. 'You are tasked to fetch and summarize data stored in Chroma DB. For every answer, include a list of references from the source documents. If no data is found, respond with, \"No data available in the database for this query.\"'\n"
        "5. 'Your role is to assist users by answering their questions based on data stored in Chroma DB. Always ensure your answers are accurate and derived from the database. If you cannot find an answer, inform the user politely and offer to assist further.'"
    )

    # generate a prediction for a prompt
    bot_json = llm_chain.invoke(f"{default_prompt}\n\n{user_input}")
    print("bot json is ->", bot_json)

    # Extract the 'answer' and 'source_documents' keys
    answer = bot_json.get("answer", "No answer found.")
    source_documents = bot_json.get("source_documents", [])

    return {"bot_response": {"answer": answer, "source_documents": source_documents}}

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
                st.markdown("**Question: " + user_input + "**")

                st.write("Answer: ", message['content']['bot_response']['answer'])
            # with col2:
            #     st.chat_message("assistant")
            #     for doc in message['content']['bot_response']['source_documents']:
            #         st.write("Reference: ", doc.metadata['source'] )
