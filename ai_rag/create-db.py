import os
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import OCIGenAIEmbeddings
from langchain_community.vectorstores import Chroma
from LoadProperties import LoadProperties

# Directory containing the .txt files
txt_directory = "bugdbdata"

# Initialize an empty list to store documents
documents = []

# Iterate through .txt files in the directory
for filename in os.listdir(txt_directory):
    if filename.endswith(".txt"):
        filepath = os.path.join(txt_directory, filename)
        loader = TextLoader(filepath)
        documents.extend(loader.load())

# Generate embeddings for the documents
properties = LoadProperties()

embedding_model = OCIGenAIEmbeddings(
    model_id=properties.getEmbeddingModelName(),
    service_endpoint=properties.getEndpoint(),
    compartment_id=properties.getCompartment(),
    model_kwargs={"truncate":True}
)

#Step 3 - since OCIGenAIEmbeddings accepts only 96 documents in one run , we will input documents in batches.
# Generate embeddings for the documents using OCI GenAI in batches of 96
db = Chroma(embedding_function=embedding_model , persist_directory="./chromadb")
retv = db.as_retriever()

batch_size = 96
for i in range(0, len(documents), batch_size):
    print(f"Processing batch {i}/{len(documents)}")
    batch = documents[i:i + batch_size]
    retv.add_documents(batch)

print("Documents have been loaded and stored in ChromaDB.")