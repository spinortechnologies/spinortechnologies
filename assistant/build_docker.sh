#!/bin/bash

echo "🚀 SPINOR TECHNOLOGIES - Docker Build Script"
echo "🐳 Building Quantitative Finance Assistant Container"
echo "="*60

# Build Docker image
echo "🔨 Building Docker image..."
docker-compose build

# Create directories for persistence
echo "📁 Creating persistent directories..."
mkdir -p knowledge_base data/papers logs config

# Set permissions
chmod 755 knowledge_base data logs config
chmod 755 data/papers

echo "✅ Build complete!"
echo ""
echo "🎯 Usage Examples:"
echo "="*40
echo "# CLI Mode (Default - Interactive)"
echo "docker-compose up quant-ai-cli"
echo ""
echo "# GUI Mode (requires X11 forwarding)"
echo "docker-compose --profile gui up quant-ai-gui"
echo ""
echo "# Full System Mode"
echo "docker-compose --profile full up quant-ai-full"
echo ""
echo "# Background Paper Service"
echo "docker-compose --profile papers up -d quant-ai-papers"
echo ""
echo "# One-time paper download"
echo "docker-compose run --rm quant-ai-cli papers"
echo ""
echo "# Build knowledge base"
echo "docker-compose run --rm quant-ai-cli build-kb"
echo ""
echo "# Shell access"
echo "docker-compose run --rm quant-ai-cli bash"
echo ""
echo "🚀 Quick Start: docker-compose up quant-ai-cli"