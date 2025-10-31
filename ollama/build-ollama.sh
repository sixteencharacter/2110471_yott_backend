#!/bin/bash
set -e

echo "Starting Ollama server..."
ollama serve &
OLLAMA_PID=$!

echo "Waiting for Ollama server to be active..."
sleep 10

echo "Checking if Ollama is responding..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if ollama list > /dev/null 2>&1; then
        echo "Ollama server is ready!"
        break
    fi
    echo "Server not ready, retrying... (attempt $((attempt + 1))/$max_attempts)"
    sleep 2
    attempt=$((attempt + 1))
done

if [ $attempt -eq $max_attempts ]; then
    echo "Failed to start Ollama server"
    exit 1
fi

echo "Creating yott-agent model..."
ollama create "yott-agent" -f /root/.ollama/Modelfile
echo "yott-agent model created successfully!"

echo "Build completed!"