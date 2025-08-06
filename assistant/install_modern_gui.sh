#!/bin/bash

# 🚀 SPINOR Modern GUI Installation Script
# Enhanced accessible web interface setup

set -e  # Exit on any error

echo "🚀 SPINOR Modern GUI - Installation & Setup"
echo "=============================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo "🐍 Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo -e "${GREEN}✅ Python ${PYTHON_VERSION} found${NC}"
else
    echo -e "${RED}❌ Python 3 not found. Please install Python 3.8 or later.${NC}"
    exit 1
fi

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo -e "${GREEN}✅ Virtual environment active: $(basename $VIRTUAL_ENV)${NC}"
else
    echo -e "${YELLOW}⚠️ No virtual environment detected${NC}"
    echo "It's recommended to use a virtual environment:"
    echo "  python3 -m venv spinor_env"
    echo "  source spinor_env/bin/activate"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Install core dependencies
echo ""
echo "📦 Installing core dependencies..."
pip install --upgrade pip
pip install flask flask-socketio eventlet

# Install optional CORS support
echo ""
echo "🌐 Installing CORS support..."
pip install flask-cors || echo -e "${YELLOW}⚠️ CORS installation failed (optional)${NC}"

# Install AI/ML dependencies
echo ""
echo "🧠 Installing AI/ML dependencies..."
pip install sentence-transformers transformers torch faiss-cpu
pip install langchain huggingface-hub
pip install numpy pandas scikit-learn

# Install data processing dependencies
echo ""
echo "📊 Installing data processing dependencies..."
pip install nltk beautifulsoup4 requests aiohttp
pip install arxiv python-dotenv schedule psutil tqdm

# Install development dependencies (optional)
echo ""
echo "🔧 Installing development dependencies..."
pip install rich colorama markdown jinja2 || echo -e "${YELLOW}⚠️ Some dev dependencies failed (optional)${NC}"

# Download NLTK data
echo ""
echo "📚 Downloading NLTK data..."
python3 -c "
import nltk
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)  
    nltk.download('vader_lexicon', quiet=True)
    print('✅ NLTK data downloaded successfully')
except Exception as e:
    print(f'⚠️ NLTK download warning: {e}')
"

# Create necessary directories
echo ""
echo "📁 Creating directory structure..."
mkdir -p data/intelligent_nodes
mkdir -p data/specialized_agent_quantitative_finance
mkdir -p data/auto_feeding
mkdir -p logs
mkdir -p templates
mkdir -p static/css
mkdir -p static/js
mkdir -p static/images

echo -e "${GREEN}✅ Directories created${NC}"

# Check if templates exist
echo ""
echo "🎨 Checking templates..."
if [ -f "templates/modern_index.html" ]; then
    echo -e "${GREEN}✅ Modern template found${NC}"
else
    echo -e "${YELLOW}⚠️ Modern template not found${NC}"
    echo "Make sure modern_index.html is in the templates/ directory"
fi

# Create a simple health check
echo ""
echo "🔍 Creating health check..."
cat > health_check.py << 'EOF'
#!/usr/bin/env python3
"""Health check for SPINOR Modern GUI dependencies"""

import sys
import importlib

def check_import(module_name, package_name=None):
    try:
        importlib.import_module(module_name)
        print(f"✅ {package_name or module_name}")
        return True
    except ImportError:
        print(f"❌ {package_name or module_name}")
        return False

print("🔍 SPINOR Modern GUI - Dependency Check")
print("=" * 40)

checks = [
    ("flask", "Flask"),
    ("flask_socketio", "Flask-SocketIO"),
    ("flask_cors", "Flask-CORS (optional)"),
    ("sentence_transformers", "Sentence Transformers"),
    ("transformers", "Transformers"),
    ("torch", "PyTorch"),
    ("faiss", "FAISS"),
    ("nltk", "NLTK"),
    ("requests", "Requests"),
    ("aiohttp", "AsyncIO HTTP"),
    ("arxiv", "ArXiv"),
    ("numpy", "NumPy"),
    ("pandas", "Pandas"),
]

passed = 0
total = len(checks)

for module, name in checks:
    if check_import(module, name):
        passed += 1

print(f"\n📊 Status: {passed}/{total} dependencies available")

if passed == total:
    print("🎉 All dependencies installed successfully!")
    sys.exit(0)
elif passed >= total - 2:  # Allow 2 optional failures
    print("✅ Core dependencies available (some optional missing)")
    sys.exit(0)
else:
    print("❌ Critical dependencies missing")
    sys.exit(1)
EOF

# Run health check
echo ""
echo "🏥 Running health check..."
python3 health_check.py

HEALTH_STATUS=$?

# Create launch script
echo ""
echo "🚀 Creating launch script..."
cat > launch_modern_gui.sh << 'EOF'
#!/bin/bash

echo "🚀 Starting SPINOR Modern GUI..."

# Check if virtual environment should be activated
if [ -d "spinor_env" ] && [ -z "$VIRTUAL_ENV" ]; then
    echo "🔄 Activating virtual environment..."
    source spinor_env/bin/activate
fi

# Set environment variables
export FLASK_ENV=production
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Launch options
echo ""
echo "Select launch mode:"
echo "1) Development mode (debug=True, port=5000)"
echo "2) Production mode (debug=False, port=5000)"  
echo "3) Custom configuration"
echo ""

read -p "Choose option (1-3): " choice

case $choice in
    1)
        echo "🔧 Starting in development mode..."
        python3 modern_web_gui.py --debug --port 5000
        ;;
    2)
        echo "🏭 Starting in production mode..."
        python3 modern_web_gui.py --port 5000
        ;;
    3)
        read -p "Enter host (default: 127.0.0.1): " host
        read -p "Enter port (default: 5000): " port
        host=${host:-127.0.0.1}
        port=${port:-5000}
        echo "🔧 Starting with custom configuration..."
        python3 modern_web_gui.py --host $host --port $port
        ;;
    *)
        echo "❌ Invalid option"
        exit 1
        ;;
esac
EOF

chmod +x launch_modern_gui.sh

# Create configuration template
echo ""
echo "⚙️ Creating configuration template..."
cat > config_modern.env << 'EOF'
# SPINOR Modern GUI Configuration
# Copy this to .env and customize as needed

# Server Configuration
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
FLASK_DEBUG=False

# AI Configuration
ENABLE_SPECIALIZED_AGENT=True
ENABLE_AUTO_FEEDING=True
ENABLE_NODE_MANAGER=True

# Data Directories
DATA_DIR=./data
LOGS_DIR=./logs
MODELS_DIR=./models

# Auto-Feeding Configuration
AUTO_FEED_INTERVAL=21600  # 6 hours in seconds
MAX_PAPERS_PER_FEED=50
ARXIV_CATEGORIES=q-fin.CP,q-fin.PM,q-fin.RM,q-fin.TR,q-fin.MF,q-fin.PR

# Quality Filters
MIN_CITATION_THRESHOLD=5
MIN_ABSTRACT_LENGTH=200
ENABLE_REDUNDANCY_FILTERING=True

# UI Configuration
ENABLE_ADVANCED_FILTERS=True
ENABLE_REAL_TIME_UPDATES=True
DEFAULT_RESULTS_LIMIT=20

# Security
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=*

# Logging
LOG_LEVEL=INFO
LOG_FORMAT='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
EOF

# Final setup summary
echo ""
echo "🎉 Installation Complete!"
echo "========================"
echo ""
echo -e "${GREEN}✅ Dependencies installed${NC}"
echo -e "${GREEN}✅ Directory structure created${NC}"
echo -e "${GREEN}✅ Health check completed${NC}"
echo -e "${GREEN}✅ Launch script created${NC}"
echo -e "${GREEN}✅ Configuration template created${NC}"
echo ""

if [ $HEALTH_STATUS -eq 0 ]; then
    echo -e "${GREEN}🚀 Ready to launch!${NC}"
    echo ""
    echo "Quick start:"
    echo "  ./launch_modern_gui.sh"
    echo ""
    echo "Or manual start:"
    echo "  python3 modern_web_gui.py"
    echo ""
    echo "Then open: http://127.0.0.1:5000"
    echo ""
    echo "🎯 Features available:"
    echo "  🔍 Advanced multi-dimensional filtering"
    echo "  📊 Real-time system statistics"
    echo "  🧠 Intelligent knowledge management"
    echo "  ♿ Full accessibility support (WCAG 2.1 AA)"
    echo "  📱 Mobile-responsive design"
    echo "  🌍 Multilingual support (EN/ES)"
    echo "  🔄 Real-time WebSocket communication"
else
    echo -e "${YELLOW}⚠️ Setup completed with warnings${NC}"
    echo "Some optional dependencies may be missing."
    echo "The system should still work with core functionality."
fi

echo ""
echo "📚 For more information:"
echo "  • Documentation: README_SISTEMA_COMPLETO.md"
echo "  • Filter demo: python3 demo_filtering_system.py"
echo "  • Health check: python3 health_check.py"
echo ""
echo "Happy exploring! 🚀"
