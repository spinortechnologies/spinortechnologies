# 🐳 Docker Setup - Quantitative Finance Assistant

## SPINOR TECHNOLOGIES - Containerized Financial AI System

This directory contains a complete Docker setup for the Quantitative Finance Assistant with real-time paper capabilities.

---

## 🚀 Quick Start

### 1. Build the Container
```bash
./build_docker.sh
```

### 2. Run CLI Mode (Recommended)
```bash
docker-compose up quant-ai-cli
```

---

## 🎯 Available Modes

### 📱 CLI Mode (Default)
Interactive command-line interface with full functionality:
```bash
docker-compose up quant-ai-cli
```
**Features:**
- ✅ Interactive chat with AI
- ✅ Real-time paper downloads
- ✅ System status monitoring
- ✅ All commands available

### 🖥️ GUI Mode
Graphical interface (requires X11 forwarding on Linux):
```bash
# Linux
xhost +local:docker
docker-compose --profile gui up quant-ai-gui

# Windows/Mac
# Use X11 server like VcXsrv or XQuartz
```

### 🎮 Full System Mode
Complete system with interactive menu:
```bash
docker-compose --profile full up quant-ai-full
```

### 🔄 Automatic Paper Service
Background service for automatic paper downloads:
```bash
docker-compose --profile papers up -d quant-ai-papers
```

---

## 📋 Common Commands

### Development & Testing
```bash
# Shell access for debugging
docker-compose run --rm quant-ai-cli bash

# One-time paper download
docker-compose run --rm quant-ai-cli papers

# Build knowledge base
docker-compose run --rm quant-ai-cli build-kb

# System status check
docker-compose run --rm quant-ai-cli cli
# Then type 'status' in the CLI
```

### Production Deployment
```bash
# Start background paper service
docker-compose --profile papers up -d quant-ai-papers

# Start CLI service for users
docker-compose up -d quant-ai-cli

# View logs
docker-compose logs -f quant-ai-papers
docker-compose logs -f quant-ai-cli
```

---

## 💾 Data Persistence

The following directories are mounted as volumes for persistence:

| Directory | Purpose | Description |
|-----------|---------|-------------|
| `./knowledge_base/` | AI Vector Database | FAISS embeddings and indexes |
| `./data/papers/` | Downloaded Papers | JSON files with paper metadata |
| `./logs/` | System Logs | Application and service logs |
| `./config/` | Configuration | Environment and config files |

---

## 🔧 Configuration

### Environment Variables
```bash
# Set in docker-compose.yml or .env file
PYTHONUNBUFFERED=1          # Real-time output
DISPLAY=${DISPLAY}          # X11 display for GUI
QT_X11_NO_MITSHM=1         # PyQt5 compatibility
```

### Custom Configuration
```bash
# Create custom config
echo "UPDATE_FREQUENCY=6" > config/.env.papers
echo "MAX_PAPERS=20" >> config/.env.papers
echo "DAYS_BACK=14" >> config/.env.papers
```

---

## 🐛 Troubleshooting

### GUI Issues
```bash
# Linux: Allow X11 forwarding
xhost +local:docker

# Check DISPLAY variable
echo $DISPLAY

# Test GUI in container
docker-compose run --rm quant-ai-gui bash
# Inside container: echo $DISPLAY
```

### Permission Issues
```bash
# Fix volume permissions
sudo chown -R $(id -u):$(id -g) knowledge_base data logs config

# Check container user
docker-compose run --rm quant-ai-cli id
```

### Network Issues
```bash
# Check paper downloads
docker-compose run --rm quant-ai-cli papers

# Test network connectivity
docker-compose run --rm quant-ai-cli bash
# Inside container: curl -I https://export.arxiv.org/api/query
```

### Performance Issues
```bash
# Monitor resource usage
docker stats

# Check container logs
docker-compose logs quant-ai-cli

# Limit memory usage (add to service in docker-compose.yml)
deploy:
  resources:
    limits:
      memory: 2G
```

---

## 📊 Production Setup

### Complete Production Stack
```bash
# Start all services
docker-compose --profile papers --profile full up -d

# Or use specific services
docker-compose up -d quant-ai-papers  # Background papers
docker-compose up -d quant-ai-full    # Main application
```

### Monitoring
```bash
# View all logs
docker-compose logs -f

# Monitor paper service
docker-compose logs -f quant-ai-papers

# Check health
docker-compose ps
```

### Backup
```bash
# Backup persistent data
tar -czf backup-$(date +%Y%m%d).tar.gz knowledge_base data logs config

# Restore from backup
tar -xzf backup-20250806.tar.gz
```

---

## 🔄 Updates

### Update Container
```bash
# Rebuild after code changes
docker-compose build

# Update with new changes
docker-compose up --build quant-ai-cli
```

### Update Papers
```bash
# Manual update
docker-compose run --rm quant-ai-cli papers

# Check automatic service
docker-compose logs quant-ai-papers
```

---

## 📈 Performance Optimization

### Resource Limits
```yaml
# Add to docker-compose.yml services
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 4G
    reservations:
      memory: 1G
```

### GPU Support (Optional)
```yaml
# For GPU acceleration
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: 1
          capabilities: [gpu]
```

---

## 🚀 Quick Commands Reference

```bash
# Build
./build_docker.sh

# Start CLI (most common)
docker-compose up quant-ai-cli

# Background paper service
docker-compose --profile papers up -d quant-ai-papers

# Full system with menu
docker-compose --profile full up quant-ai-full

# GUI mode (Linux)
xhost +local:docker
docker-compose --profile gui up quant-ai-gui

# One-time operations
docker-compose run --rm quant-ai-cli papers    # Download papers
docker-compose run --rm quant-ai-cli build-kb  # Build knowledge base
docker-compose run --rm quant-ai-cli bash      # Shell access

# Logs and monitoring
docker-compose logs -f quant-ai-papers
docker-compose ps
docker stats
```

---

## 📞 Support

**Container Architecture**: Multi-mode Docker setup
**Base Image**: Python 3.10 slim
**Supported Modes**: CLI, GUI, Full System, Auto Service
**Persistence**: Volume mounts for all data
**Networking**: Isolated bridge network

**SPINOR TECHNOLOGIES - Containerized Financial AI v2.0** 🚀🐳
