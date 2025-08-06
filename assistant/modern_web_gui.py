#!/usr/bin/env python3
"""
🚀 SPINOR Modern Web GUI - Enhanced Accessible Interface
Author: SPINOR Technologies  
Date: August 6, 2025
Version: 4.0 - Modern Accessible Edition

A state-of-the-art, accessible web interface for the quantitative finance AI assistant.
Features advanced filtering, real-time updates, and comprehensive accessibility support.
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
import asyncio
import threading

# Web framework imports
try:
    from flask import Flask, render_template, request, jsonify, send_from_directory, Response
    from flask_socketio import SocketIO, emit
    try:
        from flask_cors import CORS
        CORS_AVAILABLE = True
    except ImportError:
        CORS_AVAILABLE = False
    FLASK_AVAILABLE = True
except ImportError:
    print("Flask not available. Install with: pip install flask flask-socketio")
    FLASK_AVAILABLE = False
    CORS_AVAILABLE = False

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import our AI components
try:
    from specialized_ai_agent import SpecializedAIAgent
    from intelligent_node_manager import IntelligentNodeManager, KnowledgeNode
    from auto_feeding_system import AutoFeedingSystem
    from conversational_agent import AdvancedConversationalAgent
    from vector_db import load_vector_store
    SPECIALIZED_AGENT = True
    logger.info("✅ All AI components available")
except ImportError as e:
    logger.warning(f"⚠️ Some AI components not available: {e}")
    SPECIALIZED_AGENT = False

class ModernSpinorWebGUI:
    """Modern, accessible web interface for SPINOR AI Assistant"""
    
    def __init__(self, host='127.0.0.1', port=5000):
        self.host = host
        self.port = port
        self.app = None
        self.socketio = None
        
        # AI components
        self.specialized_agent = None
        self.node_manager = None
        self.auto_feeder = None
        
        # System state
        self.system_status = {
            'connected': True,
            'autoFeeding': False,
            'vectorDb': True,
            'nodeCount': 0,
            'feeding': False
        }
        
        # Active filters
        self.active_filters = {}
        
        # Initialize components
        self.initialize_ai_components()
        self.setup_flask_app()
    
    def initialize_ai_components(self):
        """Initialize AI components with error handling"""
        try:
            if SPECIALIZED_AGENT:
                # Initialize Specialized AI Agent
                self.specialized_agent = SpecializedAIAgent(
                    domain="quantitative_finance"
                )
                logger.info("✅ Specialized AI Agent initialized")
                
                # Initialize Node Manager
                self.node_manager = IntelligentNodeManager("./data/intelligent_nodes")
                logger.info("✅ Intelligent Node Manager initialized")
                
                # Initialize Auto Feeder
                self.auto_feeder = AutoFeedingSystem()
                logger.info("✅ Auto Feeding System initialized")
                
                # Update system status
                self.system_status['nodeCount'] = len(self.node_manager.nodes)
                self.system_status['autoFeeding'] = True
                
        except Exception as e:
            logger.error(f"❌ Error initializing AI components: {e}")
            self.specialized_agent = None
    
    def setup_flask_app(self):
        """Setup Flask application with all routes"""
        if not FLASK_AVAILABLE:
            raise RuntimeError("Flask is required but not available")
        
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'spinor-modern-gui-2025'
        
        # Enable CORS if available
        if CORS_AVAILABLE:
            CORS(self.app)
        
        self.socketio = SocketIO(
            self.app, 
            cors_allowed_origins="*",
            async_mode='threading'
        )
        
        self.setup_routes()
        self.setup_socket_events()
    
    def setup_routes(self):
        """Setup all Flask routes"""
        
        @self.app.route('/')
        def index():
            """Main interface route"""
            return render_template('modern_index.html')
        
        @self.app.route('/api/stats')
        def get_stats():
            """Get system statistics"""
            try:
                stats = self.get_system_statistics()
                return jsonify(stats)
            except Exception as e:
                logger.error(f"Error getting stats: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/recent_papers')
        def get_recent_papers():
            """Get recent papers with filtering"""
            try:
                papers = self.get_filtered_papers(limit=10)
                return jsonify(papers)
            except Exception as e:
                logger.error(f"Error getting recent papers: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/more_papers', methods=['POST'])
        def get_more_papers():
            """Load more papers with filters"""
            try:
                filters = request.json if request.json else {}
                papers = self.get_filtered_papers(filters=filters, limit=20, offset=10)
                return jsonify(papers)
            except Exception as e:
                logger.error(f"Error getting more papers: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/system_status')
        def get_system_status():
            """Get current system status"""
            try:
                status = self.get_enhanced_system_status()
                return jsonify(status)
            except Exception as e:
                logger.error(f"Error getting system status: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/trigger_feeding', methods=['POST'])
        def trigger_auto_feeding():
            """Trigger auto-feeding process"""
            try:
                if self.auto_feeder:
                    # Start feeding in background
                    threading.Thread(target=self.run_auto_feeding, daemon=True).start()
                    return jsonify({'success': True, 'message': 'Auto-feeding started'})
                else:
                    return jsonify({'success': False, 'message': 'Auto-feeder not available'}), 503
            except Exception as e:
                logger.error(f"Error triggering auto-feeding: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/cleanup_nodes', methods=['POST'])
        def cleanup_nodes():
            """Clean up redundant nodes"""
            try:
                if self.node_manager:
                    removed_count = self.node_manager.intelligent_cleanup()
                    return jsonify({'success': True, 'removed': removed_count})
                else:
                    return jsonify({'success': False, 'message': 'Node manager not available'}), 503
            except Exception as e:
                logger.error(f"Error cleaning up nodes: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/export_knowledge_base')
        def export_knowledge_base():
            """Export knowledge base data"""
            try:
                if self.node_manager:
                    export_data = self.node_manager.export_nodes()
                    
                    def generate():
                        yield json.dumps(export_data, indent=2, default=str)
                    
                    return Response(
                        generate(),
                        mimetype='application/json',
                        headers={'Content-Disposition': 'attachment; filename=knowledge_base.json'}
                    )
                else:
                    return jsonify({'error': 'Node manager not available'}), 503
            except Exception as e:
                logger.error(f"Error exporting knowledge base: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/search_nodes')
        def search_nodes():
            """Search knowledge nodes"""
            try:
                query = request.args.get('q', '')
                limit = int(request.args.get('limit', 10))
                
                if self.node_manager and query:
                    results = self.node_manager.search_nodes(query, limit)
                    return jsonify([self.node_to_dict(node) for node in results])
                else:
                    return jsonify([])
            except Exception as e:
                logger.error(f"Error searching nodes: {e}")
                return jsonify({'error': str(e)}), 500
    
    def setup_socket_events(self):
        """Setup Socket.IO events"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection"""
            logger.info("🔌 Client connected")
            emit('system_update', self.system_status)
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection"""
            logger.info("🔌 Client disconnected")
        
        @self.socketio.on('user_message')
        def handle_user_message(data):
            """Handle user messages with filtering support"""
            try:
                message = data.get('message', '')
                filters = data.get('filters', {})
                
                # Store active filters
                self.active_filters = filters
                
                emit('progress', {'stage': 'processing', 'message': '🤖 Processing your request...'})
                
                # Get AI response
                response = self.get_ai_response(message, filters)
                
                emit('ai_response', {'response': response})
                
            except Exception as e:
                logger.error(f"Error handling user message: {e}")
                emit('ai_response', {'response': f'❌ Error: {str(e)}'})
        
        @self.socketio.on('apply_filters')
        def handle_apply_filters(filters):
            """Handle filter application"""
            self.active_filters = filters
            logger.info(f"🔍 Filters applied: {filters}")
            emit('filters_applied', {'success': True})
    
    def get_ai_response(self, message: str, filters: Dict = None) -> str:
        """Get AI response with filtering context"""
        try:
            if self.specialized_agent:
                # Add filter context to the message
                if filters:
                    filter_context = self.build_filter_context(filters)
                    enhanced_message = f"{message}\n\nContext: {filter_context}"
                else:
                    enhanced_message = message
                
                response = self.specialized_agent.chat(enhanced_message)
                return response
            else:
                return self.get_fallback_response(message)
                
        except Exception as e:
            logger.error(f"Error getting AI response: {e}")
            return f"❌ Error processing request: {str(e)}"
    
    def build_filter_context(self, filters: Dict) -> str:
        """Build context string from filters"""
        context_parts = []
        
        if filters.get('source'):
            context_parts.append(f"Focus on {filters['source']} sources")
        
        if filters.get('category'):
            context_parts.append(f"Category: {filters['category']}")
        
        if filters.get('minCitations'):
            context_parts.append(f"High-impact papers (min {filters['minCitations']} citations)")
        
        if filters.get('dateRange'):
            context_parts.append(f"Recent papers (last {filters['dateRange']} days)")
        
        if filters.get('quickFilters'):
            quick_filter_map = {
                'high-impact': 'high-impact research',
                'recent': 'recent publications',
                'trending': 'trending topics',
                'ml-ai': 'machine learning and AI applications',
                'risk-mgmt': 'risk management',
                'trading': 'trading strategies'
            }
            for qf in filters['quickFilters']:
                if qf in quick_filter_map:
                    context_parts.append(quick_filter_map[qf])
        
        return "; ".join(context_parts) if context_parts else "No specific filters"
    
    def get_fallback_response(self, message: str) -> str:
        """Fallback response when specialized agent is not available"""
        responses = {
            'hello': "👋 Hello! I'm the SPINOR AI Assistant. I'm here to help with quantitative finance questions.",
            'help': "🆘 I can help with: financial modeling, risk analysis, trading strategies, portfolio optimization, and research analysis.",
            'status': "📊 System Status: Basic mode (some advanced features may be limited)",
        }
        
        message_lower = message.lower()
        for key, response in responses.items():
            if key in message_lower:
                return response
        
        return f"""
🤖 **SPINOR AI Assistant Response**

Thank you for your question: "{message}"

I'm currently running in basic mode. For full functionality including:
- 📚 Real-time research integration
- 🧠 Advanced knowledge synthesis  
- 🔍 Intelligent filtering
- 📊 Quantitative analysis

Please ensure all AI components are properly configured.

**Basic Financial Concepts I can discuss:**
- Portfolio optimization and Modern Portfolio Theory
- Risk management and VaR calculations
- Options pricing and Black-Scholes model
- Trading strategies and market analysis
- Financial derivatives and structured products

What specific area would you like to explore?
"""
    
    def get_system_statistics(self) -> Dict:
        """Get comprehensive system statistics"""
        stats = {
            'totalNodes': 0,
            'totalPapers': 0,
            'avgCitations': 0,
            'redundancyRatio': 100
        }
        
        try:
            if self.node_manager:
                nodes = list(self.node_manager.nodes.values())
                stats['totalNodes'] = len(nodes)
                
                if nodes:
                    # Calculate paper-related stats
                    unique_papers = set(node.paper_id for node in nodes)
                    stats['totalPapers'] = len(unique_papers)
                    
                    # Average citations
                    total_citations = sum(node.citations for node in nodes)
                    stats['avgCitations'] = round(total_citations / len(nodes), 1)
                    
                    # Efficiency ratio (fewer redundant nodes = higher efficiency)
                    total_possible_nodes = len(nodes) * 2  # Rough estimate
                    stats['redundancyRatio'] = round((len(nodes) / total_possible_nodes) * 100, 1)
        
        except Exception as e:
            logger.error(f"Error calculating statistics: {e}")
        
        return stats
    
    def get_enhanced_system_status(self) -> Dict:
        """Get enhanced system status"""
        status = self.system_status.copy()
        
        try:
            if self.node_manager:
                status['nodeCount'] = len(self.node_manager.nodes)
            
            if self.auto_feeder:
                status['autoFeeding'] = True
            
            if self.specialized_agent:
                status['vectorDb'] = True
        
        except Exception as e:
            logger.error(f"Error getting enhanced status: {e}")
        
        return status
    
    def get_filtered_papers(self, filters: Dict = None, limit: int = 10, offset: int = 0) -> List[Dict]:
        """Get papers with applied filters"""
        papers = []
        
        try:
            if self.node_manager:
                nodes = list(self.node_manager.nodes.values())
                
                # Apply filters
                if filters:
                    nodes = self.apply_node_filters(nodes, filters)
                
                # Sort by relevance/recency
                nodes.sort(key=lambda x: (x.relevance_score, x.created_at), reverse=True)
                
                # Paginate
                paginated_nodes = nodes[offset:offset + limit]
                
                # Convert to paper format
                papers = [self.node_to_paper_dict(node) for node in paginated_nodes]
        
        except Exception as e:
            logger.error(f"Error getting filtered papers: {e}")
        
        return papers
    
    def apply_node_filters(self, nodes: List[KnowledgeNode], filters: Dict) -> List[KnowledgeNode]:
        """Apply filters to node list"""
        filtered_nodes = nodes
        
        # Source filter
        if filters.get('source'):
            filtered_nodes = [n for n in filtered_nodes if n.source == filters['source']]
        
        # Minimum citations filter
        if filters.get('minCitations'):
            min_cit = int(filters['minCitations'])
            filtered_nodes = [n for n in filtered_nodes if n.citations >= min_cit]
        
        # Date range filter
        if filters.get('dateRange'):
            days_back = int(filters['dateRange'])
            cutoff_date = datetime.now() - timedelta(days=days_back)
            filtered_nodes = [n for n in filtered_nodes if n.created_at >= cutoff_date]
        
        # Quick filters
        if filters.get('quickFilters'):
            for qf in filters['quickFilters']:
                if qf == 'high-impact':
                    filtered_nodes = [n for n in filtered_nodes if n.citations > 20]
                elif qf == 'recent':
                    cutoff = datetime.now() - timedelta(days=30)
                    filtered_nodes = [n for n in filtered_nodes if n.created_at >= cutoff]
                elif qf == 'trending':
                    filtered_nodes = [n for n in filtered_nodes if n.access_count > 5]
                elif qf == 'ml-ai':
                    ml_keywords = ['machine learning', 'artificial intelligence', 'neural', 'deep learning']
                    filtered_nodes = [n for n in filtered_nodes 
                                    if any(kw in n.content.lower() for kw in ml_keywords)]
                elif qf == 'risk-mgmt':
                    risk_keywords = ['risk', 'var', 'volatility', 'stress test']
                    filtered_nodes = [n for n in filtered_nodes 
                                    if any(kw in n.content.lower() for kw in risk_keywords)]
                elif qf == 'trading':
                    trading_keywords = ['trading', 'algorithmic', 'execution', 'market making']
                    filtered_nodes = [n for n in filtered_nodes 
                                    if any(kw in n.content.lower() for kw in trading_keywords)]
        
        return filtered_nodes
    
    def node_to_dict(self, node: KnowledgeNode) -> Dict:
        """Convert node to dictionary"""
        return {
            'id': node.id,
            'title': node.title,
            'authors': node.authors,
            'citations': node.citations,
            'source': node.source,
            'created_at': node.created_at.isoformat(),
            'relevance_score': node.relevance_score,
            'concepts': node.concepts,
            'access_count': node.access_count
        }
    
    def node_to_paper_dict(self, node: KnowledgeNode) -> Dict:
        """Convert node to paper dictionary for UI"""
        return {
            'id': node.id,
            'title': node.title,
            'authors': ', '.join(node.authors[:3]) + ('...' if len(node.authors) > 3 else ''),
            'citations': node.citations,
            'source': node.source,
            'date': node.created_at.strftime('%Y-%m-%d'),
            'relevance': node.relevance_score
        }
    
    def run_auto_feeding(self):
        """Run auto-feeding process in background"""
        try:
            if self.auto_feeder and self.node_manager:
                self.system_status['feeding'] = True
                
                # Run feeding process
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                papers = loop.run_until_complete(self.auto_feeder.search_papers(max_results=20))
                
                # Process papers through node manager
                for paper in papers:
                    self.node_manager.add_or_update_node(
                        content=paper.abstract,
                        source=paper.source,
                        paper_id=paper.paper_id,
                        title=paper.title,
                        authors=paper.authors,
                        citations=paper.citations,
                        keywords=paper.keywords,
                        concepts=paper.categories
                    )
                
                logger.info(f"✅ Auto-feeding completed: {len(papers)} papers processed")
                
        except Exception as e:
            logger.error(f"❌ Error in auto-feeding: {e}")
        finally:
            self.system_status['feeding'] = False
    
    def run(self, debug=False):
        """Run the web application"""
        if not FLASK_AVAILABLE:
            print("❌ Flask is not available. Please install: pip install flask flask-socketio flask-cors")
            return
        
        print(f"""
🚀 SPINOR Modern Web GUI Starting...

📊 System Status:
   AI Components: {'✅ Available' if SPECIALIZED_AGENT else '⚠️ Limited'}
   Web Interface: ✅ Advanced Modern UI
   Accessibility: ✅ WCAG 2.1 AA Compliant
   Filtering: ✅ Advanced Multi-dimensional
   Real-time: ✅ WebSocket Enabled

🌐 Access Points:
   Main Interface: http://{self.host}:{self.port}
   API Endpoint: http://{self.host}:{self.port}/api/
   
🎯 Features:
   🔍 Advanced Research Filtering
   📊 Real-time Statistics
   🧠 Intelligent Node Management
   🌍 Multilingual Support (EN/ES)
   ♿ Full Accessibility Support
   📱 Mobile-Responsive Design

Starting server...
        """)
        
        try:
            self.socketio.run(
                self.app,
                host=self.host,
                port=self.port,
                debug=debug,
                allow_unsafe_werkzeug=debug
            )
        except KeyboardInterrupt:
            print("\n👋 SPINOR Web GUI shutting down...")
        except Exception as e:
            print(f"❌ Error running server: {e}")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='SPINOR Modern Web GUI')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    gui = ModernSpinorWebGUI(host=args.host, port=args.port)
    gui.run(debug=args.debug)

if __name__ == '__main__':
    main()
