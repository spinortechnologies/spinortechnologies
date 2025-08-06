#!/bin/bash
set -e

# Docker entrypoint script for Quantitative Finance Assistant
# Supports multiple modes: gui, cli, full-system, papers, auto-service

echo "🚀 SPINOR TECHNOLOGIES - Quantitative Finance Assistant"
echo "📊 Container starting in mode: ${1:-cli}"

# Initialize directories
mkdir -p /app/knowledge_base /app/data/papers /app/logs /app/config

# Set permissions
chown -R $(id -u):$(id -g) /app/knowledge_base /app/data /app/logs /app/config 2>/dev/null || true

case "${1:-cli}" in
    "gui")
        echo "🖥️ Starting GUI mode..."
        # Check if DISPLAY is set for GUI
        if [ -z "$DISPLAY" ]; then
            echo "❌ DISPLAY not set. GUI mode requires X11 forwarding."
            echo "💡 Use: docker run -e DISPLAY=\$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix ..."
            exit 1
        fi
        exec python gui.py
        ;;
    "cli")
        echo "💬 Starting CLI interactive mode..."
        exec python demo_simple.py
        ;;
    "full-system"|"full")
        echo "🎮 Starting full system with menu..."
        exec python run_full_system.py
        ;;
    "papers")
        echo "📄 Starting paper download..."
        exec python realtime_papers.py
        ;;
    "auto-service"|"service")
        echo "🔄 Starting automatic paper service..."
        exec python auto_paper_service.py
        ;;
    "build-kb")
        echo "🏗️ Building knowledge base..."
        exec python build_kb.py
        ;;
    "bash"|"shell")
        echo "🐚 Starting bash shell..."
        exec /bin/bash
        ;;
    *)
        echo "❌ Unknown mode: $1"
        echo "📋 Available modes:"
        echo "   gui          - GUI interface (requires X11)"
        echo "   cli          - CLI interactive mode (default)"
        echo "   full-system  - Full system with menu"
        echo "   papers       - Download papers"
        echo "   auto-service - Automatic paper service"
        echo "   build-kb     - Build knowledge base"
        echo "   bash         - Shell access"
        exit 1
        ;;
esac
