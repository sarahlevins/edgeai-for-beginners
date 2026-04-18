FROM mcr.microsoft.com/devcontainers/python:3.12

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Pull the model during build so it's baked into the image
RUN ollama serve & \
    sleep 5 && \
    ollama pull qwen3:8b && \
    kill %1

# Install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt -U
