FROM python:3.10-slim-bullseye

# Install system dependencies for PyQt5 and GUI support
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1-mesa-glx \
    libxcb-xinerama0 \
    libxkbcommon-x11-0 \
    poppler-utils \
    fonts-dejavu \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
ENV KNOWLEDGE_BASE=/app/knowledge_base
ENV DISPLAY=host.docker.internal:0.0

VOLUME /app/knowledge_base

ENTRYPOINT ["python", "gui.py"]