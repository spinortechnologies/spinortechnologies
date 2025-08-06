FROM python:3.10-slim-bullseye

# Install system dependencies for PyQt5, GUI support, and utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1-mesa-glx \
    libxcb-xinerama0 \
    libxkbcommon-x11-0 \
    poppler-utils \
    fonts-dejavu \
    curl \
    wget \
    cron \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/knowledge_base /app/data/papers /app/logs /app/config

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV KNOWLEDGE_BASE=/app/knowledge_base
ENV DISPLAY=host.docker.internal:0.0
ENV PYTHONPATH=/app

# Create volumes for persistent data
VOLUME ["/app/knowledge_base", "/app/data", "/app/logs", "/app/config"]

# Make scripts executable
RUN chmod +x /app/*.py

# Default entrypoint script
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["cli"]