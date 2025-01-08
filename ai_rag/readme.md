# Streamlit ChatBot with Dynamic Retrieval and AI Responses with RAG

## Overview
- This project demonstrates how to process .txt files from a directory, generate embeddings using Oracle Cloud Infrastructure's (OCI) GenAI Embeddings, and store them in a Chroma vector database for efficient retrieval.
- This project demonstrates the creation of an interactive chatbot using Streamlit and a Conversational Retrieval Chain powered by AI. It leverages Chroma as a vector store for document retrieval and incorporates OCI Generative AI models to provide intelligent and context-aware responses to user queries. The bot dynamically adjusts retrieval settings and handles token limits effectively.

## Features
- **Interactive Chat Interface**: Built using Streamlit for real-time question-answering.
- **Dynamic Retrieval Settings**: Adjust retrieval parameters like `search_type` and `k` (number of documents retrieved).
- **AI-Powered Responses**: Uses OCI Generative AI models for context-aware answers.
- **Conversation Memory**: Maintains a history of the last N messages to provide contextual responses.
- **Token Management**: Automatically handles token limits using truncation and history trimming.

## Components
### 1. Chroma Vector Store
- **Purpose**: Stores embeddings for document retrieval.
- **Configuration**: Connects via `chromadb.HttpClient`.

### 2. OCI Generative AI
- **Purpose**: Generates intelligent responses based on the retrieved documents and user queries.
- **Key Parameters**:
  - `max_tokens`: Set to 1500 for generating detailed answers.
  - `prompt_truncation`: Ensures input size stays within token limits.

### 3. Streamlit Interface
- **Dynamic Settings**:
  - `search_type`: Choose from "mmr", "similarity", or "hybrid".
  - `k`: Adjust the number of retrieved documents (1-20).
- **Chat Input**: Users can type questions, and the bot responds interactively.

### 4. Conversation Buffer Memory
- **Purpose**: Retains chat history for contextual understanding.
- **Limit**: Keeps only the last 5 messages to manage token usage.

## Setup Instructions

### Prerequisites
- Python 3.8+
- Required libraries:
  - `streamlit`
  - `chromadb`
  - `langchain_community`
  - `langchain chromadb oci-sdk`
- Proper configuration for OCI Generative AI models.

### Installation
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure the `LoadProperties` class to include the necessary API keys and endpoints for OCI.

### Create dataset
1. Run the Script
```
python download_bugdb.py
```

### Create chromadb
Ensure your .txt files are stored in a directory, which will be specified in the script (txt_directory).

1. Load Text Files:
The script reads .txt files from the specified directory and loads their contents.

2. Generate Embeddings:
Using the OCI GenAI Embeddings model, the script processes the documents in batches of 96 (due to API constraints).

3. Store in ChromaDB:
The embeddings are stored in a Chroma vector database, enabling efficient retrieval for later queries.

4. Persist Database:
The Chroma database is saved to a directory (chroma_db_directory) for persistence.

5. Run the Script
```
python create-db.py
```

### Running the Application
1. Start Chroma
   ```
   chroma run --host 0.0.0.0 --port 8000 --path chromadb
   ```
3. Start the Streamlit server:
   ```bash
   streamlit run <filename>.py
   ```
4. Open the application in your browser (usually at `http://localhost:8501`).

### Running the Application in docker
```
docker build -t chat-bot-db:latest .
docker save -o chat-bot-db.tar chat-bot-db:latest
...
docker load -i chat-bot-db.tar
docker run -d  -p 8000:8000 -p 8501:8501 chat-bot-db
```
   
### Adjusting Settings
- Use the **sidebar** to modify `search_type` and `k` dynamically during runtime.

## Code Walkthrough

### `create_chain`
- Initializes the Chroma vector store and the Conversational Retrieval Chain.
- Configures the AI model with token truncation and a maximum token limit.

### `initialize_session_state`
- Ensures that the LLM chain is properly initialized and stored in Streamlit's session state.

### `chat` Function
- Handles the interaction with the AI model and returns responses.

### Streamlit Interface
- Displays the chat interface and manages user input and bot responses.
- Trims chat history to the last 5 messages to stay within token limits.

## Customization
- Modify `max_tokens` in `create_chain` for different response lengths.
- Adjust `max_history_messages` to control how much chat history is retained.
- Add additional widgets in Streamlit to capture other retrieval parameters.

## Troubleshooting
- **Token Limit Exceeded**:
  - Reduce `k` (number of documents).
  - Increase truncation by lowering `max_history_messages`.

## Future Improvements
- Integrate additional AI models for more advanced capabilities.
- Expand the interface to support file uploads for custom document retrieval.
- Add multilingual support for queries and responses.

---

Feel free to explore and extend the chatbot functionality as needed!

