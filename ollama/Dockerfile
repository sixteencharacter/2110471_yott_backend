# Use official Python base image
FROM ollama/ollama

# Set working directory inside the container
WORKDIR /root/.ollama

# Copy only requirements first (for efficient caching)
COPY . .

# Install dependencies
RUN chmod +x build-ollama.sh && ./build-ollama.sh

# Expose Ollama default port
EXPOSE 11434

