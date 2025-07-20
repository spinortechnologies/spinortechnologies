#!/bin/bash

# Build Docker image
docker-compose build

# Create knowledge base directory
mkdir -p knowledge_base

# Build knowledge base (optional)
read -p "Do you want to build the knowledge base now? (This may take hours) [y/N]: " choice
if [[ $choice =~ ^[Yy]$ ]]; then
    docker run --rm -v $(pwd)/knowledge_base:/app/knowledge_base \
        quant-ai python build_kb.py
fi

echo "Setup complete. Run with: docker-compose up"