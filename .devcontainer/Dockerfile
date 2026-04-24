FROM mcr.microsoft.com/devcontainers/python:3.12

# Install Ollama
RUN apt-get update && apt-get install -y zstd && rm -rf /var/lib/apt/lists/*
RUN curl -fsSL https://ollama.com/install.sh | sh

# Pull the model during build so it's baked into the image
RUN ollama serve & \
    sleep 5 && \
    ollama pull qwen3:8b; \
    pkill ollama; exit 0

# Install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt -U
