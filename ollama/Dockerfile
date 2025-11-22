# Ultra-simple Dockerfile - just start Ollama
FROM ollama/ollama

# Copy Modelfile to a location
COPY Modelfile /tmp/Modelfile

# Just start Ollama directly - no custom models during build
EXPOSE 11434

# Use the default entrypoint from the base image
CMD ["serve"]