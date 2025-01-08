# Use a base image with Python 3
FROM python:3.13-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libfreetype6-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir oci \
                               oracle-ads \
                               langchain \
                               chromadb \
                               faiss-cpu \
                               streamlit \
                               python-multipart \
                               pydantic \
                               pypdf \
                               langchain_community

# Copy the local project files into the container
COPY . /app


# Copy the OCI config folder to the container
COPY oci /root/.oci
RUN chmod -R 600 /root/.oci

# Expose the port for the Chroma server
EXPOSE 8000
EXPOSE 8511

# Set the default command to run Chroma server on port 80
CMD ["sh", "-c", "chroma run --host 0.0.0.0 --port 8000 --path chromadb & streamlit run chat_bot.py --server.address 0.0.0.0 --server.port 8501"]
