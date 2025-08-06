#!/usr/bin/env python3
"""
SPINOR Quantitative Finance AI Assistant - Web GUI
Author: SPINOR Technologies
Date: August 6, 2025
Version: 3.0 - Web Edition

A modern, responsive web interface for the quantitative finance AI assistant.
Works without PyQt5 dependencies and provides a beautiful, professional UI.
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

# Web framework imports
try:
    from flask import Flask, render_template, request, jsonify, send_from_directory
    from flask_socketio import SocketIO, emit
    FLASK_AVAILABLE = True
except ImportError:
    print("Flask not available. Install with: pip install flask flask-socketio")
    FLASK_AVAILABLE = False

# Our enhanced multilingual AI agent
try:
    from enhanced_agent import EnhancedMultilingualAgent
    from vector_db import load_vector_store
    from enhanced_papers import EnhancedPaperIntegrator
    AGENT_AVAILABLE = True
except ImportError as e:
    print(f"Enhanced agent not available, falling back to simple agent: {e}")
    try:
        from simple_agent import SimpleQuantFinanceAgent as EnhancedMultilingualAgent
        from vector_db import load_vector_store
        AGENT_AVAILABLE = True
    except ImportError as e:
        print(f"Agent not available: {e}")
        AGENT_AVAILABLE = False

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebFinanceGUI:
    """Web-based GUI for the Finance AI Assistant"""
    
    def __init__(self):
        self.app = Flask(__name__, template_folder='templates', static_folder='static')
        self.app.secret_key = 'spinor_quantfinance_2025'
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        self.agent = None
        self.vector_store = None
        self.conversation_history = []
        self.paper_integrator = None
        
        self.init_agent()
        self.setup_routes()
        self.setup_socketio()
        self.create_templates()
        
    def init_agent(self):
        """Initialize the enhanced multilingual AI agent"""
        try:
            if AGENT_AVAILABLE:
                self.vector_store = load_vector_store()
                self.agent = EnhancedMultilingualAgent(self.vector_store)
                self.paper_integrator = EnhancedPaperIntegrator()
                logger.info("🚀 Enhanced Multilingual AI Agent initialized successfully")
            else:
                self.agent = self.create_mock_agent()
                logger.info("Using mock agent (dependencies not available)")
        except Exception as e:
            logger.error(f"Agent initialization failed: {e}")
            self.agent = self.create_mock_agent()
    
    def create_mock_agent(self):
        """Create a mock agent for demonstration"""
        class MockAgent:
            def query(self, query_text):
                # Detect language for mock response
                detected_lang = 'es' if any(word in query_text.lower() for word in [
                    'qué', 'que', 'cómo', 'como', 'cuál', 'cual', 'finanzas', 'riesgo', 'modelo'
                ]) else 'en'
                
                if detected_lang == 'es':
                    response_text = f"""
**Consulta:** {query_text}

**Respuesta del Asistente SPINOR AI:**

Esta es una demostración de la interfaz web del Asistente de Finanzas Cuantitativas SPINOR con soporte multilingüe.

### Capacidades de Análisis Financiero:

🔹 **Finanzas Matemáticas**
- Cálculo estocástico y procesos de Ito
- Marco de Black-Scholes-Merton
- Valoración neutral al riesgo

🔹 **Opciones y Derivados**
- Opciones europeas y americanas
- Valoración de derivados exóticos
- Cálculo de las griegas y cobertura

🔹 **Gestión de Riesgos**
- Modelos de Valor en Riesgo (VaR)
- Expected Shortfall (ES)
- Marcos de pruebas de estrés

🔹 **Teoría de Portafolios**
- Optimización media-varianza
- Modelo de Valoración de Activos (CAPM)
- Modelos de factores y atribución de rendimiento

🔹 **Trading Cuantitativo**
- Estrategias de generación de alfa
- Análisis de microestructura de mercado
- Ejecución algorítmica

### Integración en Tiempo Real:
- Monitoreo de papers de ArXiv
- Feeds de datos de mercado
- Actualizaciones de investigación

*Para desbloquear toda la funcionalidad, asegúrese de que todas las dependencias estén configuradas correctamente.*
                    """
                else:
                    response_text = f"""
**Query:** {query_text}

**SPINOR AI Response:**

This is a demonstration of the SPINOR Quantitative Finance AI Assistant web interface with multilingual support.

### Financial Analysis Capabilities:

🔹 **Mathematical Finance**
- Stochastic calculus and Ito processes
- Black-Scholes-Merton framework
- Risk-neutral valuation

🔹 **Options & Derivatives**
- European and American options
- Exotic derivatives pricing
- Greeks calculation and hedging

🔹 **Risk Management**
- Value at Risk (VaR) models
- Expected Shortfall (ES)
- Stress testing frameworks

🔹 **Portfolio Theory**
- Mean-variance optimization
- Capital Asset Pricing Model (CAPM)
- Factor models and performance attribution

🔹 **Quantitative Trading**
- Alpha generation strategies
- Market microstructure analysis
- Algorithmic execution

### Real-time Integration:
- ArXiv paper monitoring
- Market data feeds
- Research updates

*To unlock full functionality, ensure all dependencies are properly configured.*
                    """
                
                return {
                    'result': response_text,
                    'source_documents': [],
                    'metadata': {
                        'response_time': 0.8,
                        'confidence': 0.95,
                        'language': detected_lang,
                        'topics': ['demo', 'quantitative finance'],
                        'papers_integrated': 0
                    }
                }
            
            def health_check(self):
                return {
                    'overall_healthy': True,
                    'vector_store': AGENT_AVAILABLE,
                    'knowledge_base': True,
                    'papers_available': self.check_papers(),
                    'languages_supported': ['Spanish (es)', 'English (en)'],
                    'features': [
                        'Multilingual support',
                        'Real-time paper integration',
                        'Enhanced knowledge base'
                    ]
                }
            
            def check_papers(self):
                """Check if papers are available"""
                papers_dir = Path("./data/papers")
                return papers_dir.exists() and any(papers_dir.glob("papers_*.json"))
        
        return MockAgent()
    
    def setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def index():
            return render_template('index.html')
        
        @self.app.route('/api/query', methods=['POST'])
        def api_query():
            try:
                data = request.get_json()
                query = data.get('query', '').strip()
                
                if not query:
                    return jsonify({'error': 'Empty query'}), 400
                
                # Process query
                response = self.agent.query(query)
                
                # Add to history
                self.conversation_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'query': query,
                    'response': response.get('result', ''),
                    'language': response.get('metadata', {}).get('language', 'en'),
                    'metadata': response.get('metadata', {})
                })
                
                return jsonify({
                    'success': True,
                    'response': response.get('result', ''),
                    'metadata': response.get('metadata', {}),
                    'sources': len(response.get('source_documents', []))
                })
                
            except Exception as e:
                logger.error(f"Query processing error: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/health')
        def api_health():
            try:
                health = self.agent.health_check()
                return jsonify(health)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/papers')
        def api_papers():
            try:
                papers = self.get_recent_papers()
                return jsonify({'papers': papers})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/conversation')
        def api_conversation():
            return jsonify({'history': self.conversation_history})
        
        @self.app.route('/api/clear', methods=['POST'])
        def api_clear():
            self.conversation_history.clear()
            return jsonify({'success': True})
        
        @self.app.route('/api/update_papers', methods=['POST'])
        def api_update_papers():
            """Fetch and integrate new papers from ArXiv"""
            try:
                if self.paper_integrator:
                    # Run paper update asynchronously
                    import asyncio
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    result = loop.run_until_complete(
                        self.paper_integrator.fetch_and_process_papers(days_back=3, max_papers=30)
                    )
                    loop.close()
                    
                    return jsonify({
                        'success': result['success'],
                        'papers_processed': result['papers_processed'],
                        'concepts_extracted': result.get('concepts_extracted', 0),
                        'message': 'Papers updated successfully'
                    })
                else:
                    return jsonify({
                        'success': False,
                        'message': 'Paper integrator not available'
                    })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                })
        
        @self.app.route('/api/language_stats')
        def api_language_stats():
            """Get language usage statistics"""
            try:
                languages = {}
                for conv in self.conversation_history:
                    lang = conv.get('language', 'en')
                    languages[lang] = languages.get(lang, 0) + 1
                
                return jsonify({
                    'language_distribution': languages,
                    'total_conversations': len(self.conversation_history),
                    'supported_languages': ['en', 'es']
                })
            except Exception as e:
                return jsonify({'error': str(e)})
    
    def setup_socketio(self):
        """Setup SocketIO events"""
        
        @self.socketio.on('connect')
        def handle_connect():
            emit('status', {'message': 'Connected to SPINOR AI Assistant'})
        
        @self.socketio.on('query')
        def handle_query(data):
            try:
                query = data.get('query', '').strip()
                if not query:
                    emit('error', {'message': 'Empty query'})
                    return
                
                # Emit progress updates
                emit('progress', {'stage': 'analyzing', 'message': '🔍 Analyzing query...'})
                
                emit('progress', {'stage': 'searching', 'message': '📚 Searching knowledge base...'})
                
                emit('progress', {'stage': 'generating', 'message': '🧠 Generating response...'})
                
                # Process query
                response = self.agent.query(query)
                
                # Add to history
                self.conversation_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'query': query,
                    'response': response.get('result', ''),
                    'language': response.get('metadata', {}).get('language', 'en'),
                    'metadata': response.get('metadata', {})
                })
                
                emit('response', {
                    'query': query,
                    'response': response.get('result', ''),
                    'metadata': response.get('metadata', {}),
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                emit('error', {'message': str(e)})
    
    def get_recent_papers(self):
        """Get recent papers from data directory"""
        papers = []
        papers_dir = Path("./data/papers")
        
        if not papers_dir.exists():
            return papers
        
        try:
            import glob
            paper_files = glob.glob(str(papers_dir / "papers_*.json"))
            if paper_files:
                latest_file = max(paper_files, key=os.path.getctime)
                with open(latest_file, 'r') as f:
                    papers_data = json.load(f)
                    return papers_data[:10]  # Return first 10
        except Exception as e:
            logger.error(f"Error loading papers: {e}")
        
        return papers
    
    def create_templates(self):
        """Create HTML templates"""
        templates_dir = Path("templates")
        templates_dir.mkdir(exist_ok=True)
        
        # Create main template
        index_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 SPINOR Quantitative Finance AI Assistant</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/marked/4.0.2/marked.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        .header {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .header p {
            font-size: 1.2em;
            color: #666;
            font-style: italic;
        }
        
        .main-content {
            display: grid;
            grid-template-columns: 1fr 350px;
            gap: 30px;
            flex: 1;
        }
        
        .chat-panel {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 30px;
            display: flex;
            flex-direction: column;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
        }
        
        .chat-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #eee;
        }
        
        .chat-header h2 {
            font-size: 1.5em;
            color: #333;
        }
        
        .clear-btn {
            background: linear-gradient(135deg, #ff6b6b, #ee5a52);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 25px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        
        .clear-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(255, 107, 107, 0.4);
        }
        
        .conversation {
            flex: 1;
            overflow-y: auto;
            margin-bottom: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 15px;
            min-height: 400px;
            max-height: 500px;
        }
        
        .message {
            margin: 15px 0;
            padding: 15px;
            border-radius: 15px;
            max-width: 80%;
            animation: fadeIn 0.5s ease;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .user-message {
            background: linear-gradient(135deg, #4facfe, #00f2fe);
            color: white;
            margin-left: auto;
            border-bottom-right-radius: 5px;
        }
        
        .ai-message {
            background: linear-gradient(135deg, #43e97b, #38f9d7);
            color: white;
            border-bottom-left-radius: 5px;
        }
        
        .error-message {
            background: linear-gradient(135deg, #ff6b6b, #ee5a52);
            color: white;
            text-align: center;
        }
        
        .message-header {
            font-weight: bold;
            font-size: 0.9em;
            opacity: 0.8;
            margin-bottom: 8px;
        }
        
        .message-content {
            line-height: 1.6;
            white-space: pre-wrap;
        }
        
        .input-section {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        
        .suggestions {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        .suggestion-btn {
            background: #e3f2fd;
            border: 2px solid #2196f3;
            color: #1976d2;
            padding: 8px 15px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 0.9em;
            transition: all 0.3s ease;
        }
        
        .suggestion-btn:hover {
            background: #2196f3;
            color: white;
            transform: translateY(-2px);
        }
        
        .input-row {
            display: flex;
            gap: 15px;
        }
        
        .query-input {
            flex: 1;
            padding: 15px 20px;
            border: 2px solid #ddd;
            border-radius: 25px;
            font-size: 16px;
            outline: none;
            transition: all 0.3s ease;
        }
        
        .query-input:focus {
            border-color: #667eea;
            box-shadow: 0 0 10px rgba(102, 126, 234, 0.3);
        }
        
        .send-btn {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 25px;
            cursor: pointer;
            font-weight: bold;
            font-size: 16px;
            transition: all 0.3s ease;
        }
        
        .send-btn:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .send-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        
        .progress {
            background: #e3f2fd;
            padding: 10px 15px;
            border-radius: 10px;
            color: #1976d2;
            text-align: center;
            font-weight: bold;
            display: none;
        }
        
        .progress.show {
            display: block;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
        
        .sidebar {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        
        .panel {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
        }
        
        .panel h3 {
            margin-bottom: 15px;
            color: #333;
            font-size: 1.2em;
        }
        
        .status-item {
            display: flex;
            justify-content: space-between;
            margin: 8px 0;
            padding: 8px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        
        .status-label {
            font-weight: bold;
        }
        
        .papers-list {
            max-height: 300px;
            overflow-y: auto;
        }
        
        .paper-item {
            padding: 10px;
            margin: 5px 0;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            font-size: 0.9em;
        }
        
        .paper-title {
            font-weight: bold;
            margin-bottom: 5px;
            color: #333;
        }
        
        .paper-authors {
            color: #666;
            font-size: 0.8em;
        }
        
        .capabilities-list {
            list-style: none;
        }
        
        .capabilities-list li {
            padding: 8px 0;
            border-bottom: 1px solid #eee;
            color: #555;
        }
        
        .capabilities-list li:before {
            content: "🎯 ";
            margin-right: 5px;
        }
        
        .refresh-btn {
            background: linear-gradient(135deg, #4CAF50, #45a049);
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 20px;
            cursor: pointer;
            font-weight: bold;
            width: 100%;
            margin-top: 10px;
            transition: all 0.3s ease;
        }
        
        .refresh-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(76, 175, 80, 0.4);
        }
        
        @media (max-width: 768px) {
            .main-content {
                grid-template-columns: 1fr;
            }
            
            .header h1 {
                font-size: 2em;
            }
            
            .suggestions {
                flex-direction: column;
            }
            
            .input-row {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 SPINOR AI Assistant</h1>
            <p>Advanced Quantitative Finance Intelligence</p>
        </div>
        
        <div class="main-content">
            <div class="chat-panel">
                <div class="chat-header">
                    <h2>💬 Conversation</h2>
                    <button class="clear-btn" onclick="clearConversation()">🗑️ Clear</button>
                </div>
                
                <div class="conversation" id="conversation">
                    <div class="message ai-message">
                        <div class="message-header">[System] 🤖 SPINOR AI</div>
                        <div class="message-content">Welcome to the SPINOR Quantitative Finance AI Assistant! 

I'm here to help you with:
• Mathematical finance and stochastic calculus
• Options pricing and derivatives
• Risk management and portfolio theory
• Quantitative trading strategies
• Market analysis and research

Ask me anything about quantitative finance!</div>
                    </div>
                </div>
                
                <div class="progress" id="progress"></div>
                
                <div class="input-section">
                    <div class="suggestions">
                        <button class="suggestion-btn" onclick="setQuery('Black-Scholes Model')">📊 Black-Scholes</button>
                        <button class="suggestion-btn" onclick="setQuery('Value at Risk')">⚠️ VaR</button>
                        <button class="suggestion-btn" onclick="setQuery('Portfolio Optimization')">📈 Portfolio</button>
                        <button class="suggestion-btn" onclick="setQuery('¿Qué es el modelo Black-Scholes?')">🇪🇸 Black-Scholes</button>
                        <button class="suggestion-btn" onclick="setQuery('Gestión de riesgos financieros')">🇪🇸 Riesgos</button>
                        <button class="suggestion-btn" onclick="setQuery('Optimización de portafolios')">🇪🇸 Portafolios</button>
                    </div>
                    
                    <div class="input-row">
                        <input type="text" class="query-input" id="queryInput" 
                               placeholder="Ask in English or Spanish / Pregunta en inglés o español..."
                               onkeypress="handleKeyPress(event)">
                        <button class="send-btn" id="sendBtn" onclick="sendQuery()">🚀 Send</button>
                    </div>
                </div>
            </div>
            
            <div class="sidebar">
                <div class="panel">
                    <h3>🔧 System Status</h3>
                    <div class="status-item">
                        <span class="status-label">AI Agent:</span>
                        <span id="aiStatus">✅ Ready</span>
                    </div>
                    <div class="status-item">
                        <span class="status-label">Knowledge Base:</span>
                        <span id="kbStatus">✅ Loaded</span>
                    </div>
                    <div class="status-item">
                        <span class="status-label">Papers:</span>
                        <span id="papersStatus">🔄 Loading...</span>
                    </div>
                    <div class="status-item">
                        <span class="status-label">Languages:</span>
                        <span id="langStatus">🌐 ES/EN</span>
                    </div>
                    <button class="refresh-btn" onclick="updatePapers()" style="margin-top: 10px;">
                        🔄 Update Papers
                    </button>
                </div>
                
                <div class="panel">
                    <h3>📚 Recent Papers</h3>
                    <div class="papers-list" id="papersList">
                        <div class="paper-item">Loading recent papers...</div>
                    </div>
                    <button class="refresh-btn" onclick="refreshPapers()">🔄 Refresh Papers</button>
                </div>
                
                <div class="panel">
                    <h3>🧠 Enhanced AI Capabilities</h3>
                    <ul class="capabilities-list">
                        <li>🌐 Multilingual Support (ES/EN)</li>
                        <li>📊 Stochastic Calculus & SDEs</li>
                        <li>📈 Options Pricing Models</li>
                        <li>⚠️ Risk Management (VaR, ES)</li>
                        <li>💼 Portfolio Optimization</li>
                        <li>🔄 Market Microstructure</li>
                        <li>🤖 Quantitative Trading</li>
                        <li>📚 Real-time Paper Learning</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        const socket = io();
        let isProcessing = false;
        
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            refreshStatus();
            refreshPapers();
        });
        
        // Socket events
        socket.on('connect', function() {
            console.log('Connected to SPINOR AI Assistant');
        });
        
        socket.on('progress', function(data) {
            const progress = document.getElementById('progress');
            progress.textContent = data.message;
            progress.classList.add('show');
        });
        
        socket.on('response', function(data) {
            addMessage('ai', data.response, data.timestamp, data.metadata?.language);
            hideProgress();
        });
        
        socket.on('error', function(data) {
            addMessage('error', 'Error: ' + data.message);
            hideProgress();
        });
        
        function setQuery(text) {
            document.getElementById('queryInput').value = text;
            document.getElementById('queryInput').focus();
        }
        
        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendQuery();
            }
        }
        
        function sendQuery() {
            if (isProcessing) return;
            
            const input = document.getElementById('queryInput');
            const query = input.value.trim();
            
            if (!query) return;
            
            isProcessing = true;
            input.value = '';
            
            const sendBtn = document.getElementById('sendBtn');
            sendBtn.disabled = true;
            sendBtn.textContent = '⏳ Processing...';
            
            addMessage('user', query);
            socket.emit('query', {query: query});
        }
        
        function addMessage(sender, content, timestamp = null) {
            const conversation = document.getElementById('conversation');
            const messageDiv = document.createElement('div');
            
            const now = timestamp || new Date().toLocaleTimeString();
            let senderLabel, className;
            
            if (sender === 'user') {
                senderLabel = 'You';
                className = 'user-message';
            } else if (sender === 'ai') {
                senderLabel = '🤖 SPINOR AI';
                className = 'ai-message';
            } else {
                senderLabel = '⚠️ System';
                className = 'error-message';
            }
            
            messageDiv.className = `message ${className}`;
            messageDiv.innerHTML = `
                <div class="message-header">[${now}] ${senderLabel}</div>
                <div class="message-content">${content}</div>
            `;
            
            conversation.appendChild(messageDiv);
            conversation.scrollTop = conversation.scrollHeight;
        }
        
        function hideProgress() {
            const progress = document.getElementById('progress');
            progress.classList.remove('show');
            
            const sendBtn = document.getElementById('sendBtn');
            sendBtn.disabled = false;
            sendBtn.textContent = '🚀 Send';
            
            isProcessing = false;
        }
        
        function clearConversation() {
            const conversation = document.getElementById('conversation');
            conversation.innerHTML = `
                <div class="message ai-message">
                    <div class="message-header">[System] 🤖 SPINOR AI</div>
                    <div class="message-content">Conversation cleared! How can I help you today?</div>
                </div>
            `;
            
            fetch('/api/clear', {method: 'POST'});
        }
        
        function refreshStatus() {
            fetch('/api/health')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('aiStatus').textContent = 
                        data.overall_healthy ? '✅ Healthy' : '❌ Issues';
                    document.getElementById('kbStatus').textContent = 
                        data.vector_store ? '✅ Loaded' : '❌ Error';
                })
                .catch(error => {
                    console.error('Status check failed:', error);
                });
        }
        
        function refreshPapers() {
            document.getElementById('papersStatus').textContent = '🔄 Loading...';
            
            fetch('/api/papers')
                .then(response => response.json())
                .then(data => {
                    const papersList = document.getElementById('papersList');
                    const papersStatus = document.getElementById('papersStatus');
                    
                    if (data.papers && data.papers.length > 0) {
                        papersStatus.textContent = `📚 ${data.papers.length} papers`;
                        papersList.innerHTML = data.papers.map(paper => `
                            <div class="paper-item">
                                <div class="paper-title">${paper.title || 'Untitled'}</div>
                                <div class="paper-authors">👥 ${
                                    Array.isArray(paper.authors) 
                                        ? paper.authors.slice(0, 2).join(', ') + 
                                          (paper.authors.length > 2 ? ` et al. (${paper.authors.length})` : '')
                                        : 'Unknown'
                                }</div>
                            </div>
                        `).join('');
                    } else {
                        papersStatus.textContent = '📄 No papers';
                        papersList.innerHTML = '<div class="paper-item">No recent papers available</div>';
                    }
                })
                .catch(error => {
                    console.error('Papers refresh failed:', error);
                    document.getElementById('papersStatus').textContent = '❌ Error';
                    document.getElementById('papersList').innerHTML = 
                        '<div class="paper-item">Error loading papers</div>';
                });
        }
        
        // Auto-refresh every 5 minutes
        setInterval(refreshPapers, 300000);
        
        // New functions for enhanced features
        function updatePapers() {
            const updateBtn = event.target;
            updateBtn.disabled = true;
            updateBtn.textContent = '🔄 Updating...';
            
            fetch('/api/update_papers', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert(`✅ Papers updated successfully!\\n📄 Processed: ${data.papers_processed}\\n🧠 Concepts: ${data.concepts_extracted}`);
                        refreshPapers();
                    } else {
                        alert(`❌ Update failed: ${data.message || data.error}`);
                    }
                })
                .catch(error => {
                    console.error('Paper update failed:', error);
                    alert('❌ Paper update failed');
                })
                .finally(() => {
                    updateBtn.disabled = false;
                    updateBtn.textContent = '🔄 Update Papers';
                });
        }
        
        function getLanguageStats() {
            fetch('/api/language_stats')
                .then(response => response.json())
                .then(data => {
                    console.log('Language statistics:', data);
                    // You can display this in the UI if needed
                })
                .catch(error => {
                    console.error('Language stats failed:', error);
                });
        }
        
        // Enhanced message display with language indicator
        function addMessage(sender, content, timestamp = null, language = null) {
            const conversation = document.getElementById('conversation');
            const messageDiv = document.createElement('div');
            
            const now = timestamp || new Date().toLocaleTimeString();
            let senderLabel, className;
            
            if (sender === 'user') {
                senderLabel = 'You';
                className = 'user-message';
            } else if (sender === 'ai') {
                senderLabel = '🤖 SPINOR AI';
                className = 'ai-message';
            } else {
                senderLabel = '⚠️ System';
                className = 'error-message';
            }
            
            // Add language indicator
            const langIndicator = language ? ` (${language.toUpperCase()})` : '';
            
            messageDiv.className = `message ${className}`;
            messageDiv.innerHTML = `
                <div class="message-header">[${now}] ${senderLabel}${langIndicator}</div>
                <div class="message-content">${content}</div>
            `;
            
            conversation.appendChild(messageDiv);
            conversation.scrollTop = conversation.scrollHeight;
        }
    </script>
</body>
</html>'''
        
        with open(templates_dir / "index.html", "w", encoding="utf-8") as f:
            f.write(index_html)
    
    def run(self, host='localhost', port=5000, debug=False):
        """Run the web application"""
        logger.info(f"Starting SPINOR Finance AI Assistant Web GUI on http://{host}:{port}")
        self.socketio.run(self.app, host=host, port=port, debug=debug)


def main():
    """Main application entry point"""
    if not FLASK_AVAILABLE:
        print("Flask is required for the web GUI. Install with:")
        print("pip install flask flask-socketio")
        sys.exit(1)
    
    try:
        # Create and run the web GUI
        gui = WebFinanceGUI()
        
        print("\n" + "="*60)
        print("🚀 SPINOR Quantitative Finance AI Assistant - Web GUI")
        print("="*60)
        print("📊 Version: 3.0 - Web Edition")
        print("🌐 Starting web server...")
        print("💡 Access the interface at: http://localhost:5000")
        print("⚡ Real-time updates via WebSocket")
        print("🎨 Modern, responsive design")
        print("="*60)
        
        # Run the application
        gui.run(host='0.0.0.0', port=5000, debug=False)
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down SPINOR AI Assistant...")
    except Exception as e:
        print(f"❌ Error starting web GUI: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
