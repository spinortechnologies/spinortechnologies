# SPINOR Quantitative Finance AI Assistant v2.0

An advanced AI-powered assistant for quantitative finance research, featuring an improved PyQt5 GUI with comprehensive functionality for financial analysis and research.

## 🚀 New Features (v2.0)

### Enhanced User Interface
- **Tabbed Interface**: Organized chat, analytics, and settings tabs
- **Threaded Processing**: Non-blocking query processing with progress indicators
- **Rich Formatting**: Improved message styling with timestamps and color coding
- **Quick Suggestions**: Pre-defined query buttons for common topics
- **Source Tree View**: Hierarchical display of source documents with relevance scores

### Advanced Functionality
- **Conversation Management**: Save, load, and export conversations (HTML/PDF)
- **Auto-save**: Automatic conversation backup every 5 minutes
- **Analytics Dashboard**: Query statistics and session metrics
- **Source Document Viewer**: Detailed view of reference materials
- **Dark Mode**: Professional dark theme with enhanced readability

### Improved Error Handling
- **Graceful Degradation**: Mock agent fallback for missing dependencies
- **Robust Initialization**: Better error handling and user feedback
- **Progress Indicators**: Real-time status updates during processing

## 📋 System Requirements

- Python 3.8+
- PyQt5 5.15+
- 8GB RAM minimum (16GB recommended)
- Modern multi-core CPU
- Internet connection for model downloads

## 🛠️ Installation

### Option 1: Standard Installation

```bash
# Clone the repository
git clone https://github.com/spinortechnologies/spinortechnologies.git
cd spinortechnologies/assistant

# Install dependencies
pip install -r requirements.txt

# Run the application
python gui.py
```

### Option 2: Docker Installation

```bash
# Build and run with Docker
chmod +x build_docker.sh
./build_docker.sh

# Or use docker-compose
docker-compose up --build
```

## 📚 Dependencies

```txt
PyQt5==5.15.9           # GUI framework
langchain==0.1.16       # LLM orchestration
arxiv==2.1.0            # Academic paper access
pdfplumber==0.10.2      # PDF text extraction
faiss-cpu==1.7.4        # Vector similarity search
sentence-transformers==2.5.1  # Text embeddings
transformers==4.40.1    # Hugging Face models
torch==2.2.1            # PyTorch backend
numpy==1.26.4           # Numerical computing
scipy==1.13.0           # Scientific computing
```

## 🧠 Enhanced AI Agent (v2.0)

The core AI agent has been completely redesigned with enterprise-grade features:

### 🔥 Major Enhancements

#### **Multi-Model Architecture**
- **Primary Model**: google/flan-t5-xxl with fallback support
- **Fallback Models**: Automatic degradation to flan-t5-large, flan-t5-base
- **Mock Agent**: Graceful fallback for development/testing

#### **Advanced Query Processing**
- **Preprocessing**: Query enhancement with financial context keywords
- **Specialized Prompts**: Risk management, pricing models, trading strategies
- **Postprocessing**: Response quality metrics and financial concept extraction
- **Conversation Memory**: Multi-turn conversations with context awareness

#### **Performance Optimization**
- **Caching**: Intelligent response caching for repeated queries
- **Monitoring**: Real-time performance metrics and analytics
- **Health Checks**: Component status monitoring and diagnostics
- **Dynamic Configuration**: Runtime parameter updates

#### **Production Features**
- **Error Handling**: Comprehensive exception handling and recovery
- **Logging**: Structured logging with multiple levels
- **Timeout Management**: Configurable response timeouts
- **Source Enhancement**: Advanced document metadata and relevance scoring

### 🎯 Specialized Capabilities

#### **Risk Management**
```python
# VaR calculation and stress testing
agent.query("Calculate 95% VaR for a portfolio with historical simulation")
```

#### **Options Pricing**
```python
# Advanced pricing models
agent.query("Price a barrier option using Monte Carlo with 100k simulations")
```

#### **Portfolio Optimization**
```python
# Modern portfolio theory applications
agent.query("Optimize a 5-asset portfolio using Black-Litterman model")
```

### 📊 Usage Examples

#### Basic Configuration
```python
from quant_agent import EnhancedQuantFinanceAgent

# Default configuration
agent = EnhancedQuantFinanceAgent(vector_store)

# Custom configuration
config = {
    "temperature": 0.1,
    "max_length": 1024,
    "top_k": 10,
    "enable_memory": True,
    "enable_preprocessing": True
}
agent = EnhancedQuantFinanceAgent(vector_store, config)
```

#### Advanced Query Processing
```python
# Enhanced query with metadata
result = agent.query("Explain the Heston stochastic volatility model")

print(f"Response: {result['result']}")
print(f"Financial concepts: {result['metadata']['financial_concepts']}")
print(f"Quality metrics: {result['metadata']['quality_metrics']}")
print(f"Source count: {len(result['source_documents'])}")
```

#### Performance Monitoring
```python
# Conversation analytics
summary = agent.get_conversation_summary()
print(f"Total queries: {summary['total_queries']}")
print(f"Average response time: {summary['average_response_time']}")
print(f"Recent topics: {summary['recent_topics']}")

# Health check
health = agent.health_check()
print(f"System healthy: {health['overall_healthy']}")
```

### 🔧 Configuration Options

```python
default_config = {
    "model_name": "google/flan-t5-xxl",
    "temperature": 0.1,
    "max_length": 512,
    "top_k": 5,
    "enable_memory": True,
    "memory_max_tokens": 1000,
    "enable_caching": True,
    "enable_preprocessing": True,
    "enable_postprocessing": True,
    "response_timeout": 30,
    "fallback_models": ["google/flan-t5-large", "google/flan-t5-base"]
}
```

## 🖥️ User Interface Guide

### Main Chat Tab
- **Conversation Area**: Formatted chat history with timestamps
- **Input Section**: Text input with quick suggestion buttons
- **Source Panel**: Document references with relevance scores
- **Capabilities Info**: Overview of AI assistant features

### Analytics Tab
- **Session Statistics**: Query count, response times, duration
- **Query History**: Chronological view of all interactions
- **Usage Patterns**: Most common topics and trends

### Settings Tab
- **Model Configuration**: Response length, temperature settings
- **Interface Options**: Dark mode, auto-save preferences
- **Knowledge Base**: Refresh and update options

## 🔧 Configuration

### Environment Variables
```bash
export KNOWLEDGE_BASE=/path/to/knowledge/base
export HUGGINGFACE_API_TOKEN=your_token_here
export MODEL_CACHE_DIR=/path/to/model/cache
```

### Model Settings
- **Default Model**: google/flan-t5-xxl
- **Embedding Model**: sentence-transformers/all-mpnet-base-v2
- **Vector Store**: FAISS with cosine similarity
- **Response Length**: 500 tokens (configurable)

## 📊 Performance Optimization

### Memory Usage
- **Minimum**: 8GB RAM for basic operation
- **Recommended**: 16GB RAM for optimal performance
- **GPU Support**: CUDA-compatible GPU for faster inference

### Response Times
- **Average Query**: 3-5 seconds
- **Complex Analysis**: 10-15 seconds
- **Document Retrieval**: 1-2 seconds

## 🔍 Usage Examples

### Basic Queries
```
"Explain the Black-Scholes model for option pricing"
"What is Value at Risk and how is it calculated?"
"Compare different portfolio optimization techniques"
```

### Advanced Analysis
```
"Derive the stochastic differential equation for geometric Brownian motion"
"Implement a Monte Carlo simulation for Asian options"
"Analyze market microstructure effects on volatility clustering"
```

### Research Assistance
```
"Find recent papers on deep learning in quantitative finance"
"Summarize advances in stochastic volatility models"
"Compare factor models for equity risk assessment"
```

## 🧪 Testing

Run the test suite to verify installation:

```bash
python test_gui.py
```

Expected output:
```
✓ PyQt5 imports successful
✓ QuantFinanceAgent import successful
✓ vector_db import successful
✓ GUI components import successful
✓ All tests passed! GUI improvements are working.
```

## 🚨 Troubleshooting

### Common Issues

1. **PyQt5 Import Error**
   ```bash
   pip install PyQt5==5.15.9
   # On Ubuntu/Debian:
   sudo apt-get install python3-pyqt5
   ```

2. **Model Download Timeout**
   ```bash
   export TRANSFORMERS_CACHE=/path/to/cache
   export HF_HOME=/path/to/huggingface/cache
   ```

3. **Memory Issues**
   - Reduce max_response_length in settings
   - Use CPU-only inference: `pip install torch --index-url https://download.pytorch.org/whl/cpu`

4. **GUI Display Issues**
   ```bash
   # For remote servers:
   export DISPLAY=:0
   xhost +local:docker  # For Docker containers
   ```

## 📈 Performance Monitoring

The application includes built-in analytics:
- Query processing times
- Memory usage tracking
- Model inference statistics
- User interaction patterns

## 🔒 Security Considerations

- API keys stored in environment variables
- Local knowledge base with no external data transmission
- Conversation auto-save uses local file system
- No user data sent to external services (except Hugging Face models)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Implement improvements
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙋‍♂️ Support

For technical support or feature requests:
- Create an issue on GitHub
- Contact: support@spinortechnologies.com
- Documentation: [Wiki](https://github.com/spinortechnologies/spinortechnologies/wiki)

## 📝 Changelog

### v2.0 (August 6, 2025)
- Complete GUI redesign with tabbed interface
- Threaded query processing
- Enhanced error handling and fallback options
- Conversation management features
- Analytics dashboard
- Improved source document handling
- Auto-save functionality
- Dark mode theme
- Comprehensive testing framework

### v1.0
- Initial release with basic GUI
- ArXiv integration
- PDF text extraction
- Basic vector store functionality

---

**SPINOR Technologies** - Advancing Quantitative Finance through AI Innovation
