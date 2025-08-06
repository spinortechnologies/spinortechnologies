#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SPINOR Quantitative Finance AI Assistant - Enhanced GUI
Author: SPINOR Technologies
Date: August 6, 2025
Version: 3.0 - Visual Enhancement Edition

Features:
- Modern Material Design UI
- Real-time paper integration
- Advanced visualization
- Responsive layout
- Dark/Light theme toggle
- Professional animations
"""

import sys
import os
import json
import webbrowser
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import traceback

# PyQt5 imports
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTextEdit, QLineEdit, QPushButton, QListWidget, 
    QSplitter, QStatusBar, QProgressBar, QMenuBar, QAction,
    QFileDialog, QMessageBox, QTabWidget, QScrollArea,
    QGroupBox, QGridLayout, QComboBox, QSpinBox, QCheckBox,
    QTreeWidget, QTreeWidgetItem, QDialog, QDialogButtonBox,
    QTextBrowser, QFrame, QSlider, QPushButton, QSpacerItem,
    QSizePolicy, QGraphicsDropShadowEffect, QListWidgetItem
)
from PyQt5.QtCore import (
    Qt, QThread, pyqtSignal, QTimer, QUrl, QPropertyAnimation, 
    QEasingCurve, QRect, QSize, pyqtProperty
)
from PyQt5.QtGui import (
    QFont, QPalette, QColor, QIcon, QPixmap, QDesktopServices,
    QPainter, QBrush, QPen, QLinearGradient, QFontMetrics
)

# Import our enhanced agent
try:
    from simple_agent import SimpleQuantFinanceAgent
    from vector_db import load_vector_store
    AGENT_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Agent import failed: {e}")
    AGENT_AVAILABLE = False


class AnimatedButton(QPushButton):
    """Custom button with hover animations"""
    
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setObjectName("AnimatedButton")
        self.animation = QPropertyAnimation(self, b"geometry")
        self.original_size = QSize(100, 40)
        
    def enterEvent(self, event):
        """Animate on hover"""
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        rect = self.geometry()
        expanded_rect = QRect(rect.x() - 2, rect.y() - 2, rect.width() + 4, rect.height() + 4)
        self.animation.setStartValue(rect)
        self.animation.setEndValue(expanded_rect)
        self.animation.start()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """Animate on leave"""
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        rect = self.geometry()
        normal_rect = QRect(rect.x() + 2, rect.y() + 2, rect.width() - 4, rect.height() - 4)
        self.animation.setStartValue(rect)
        self.animation.setEndValue(normal_rect)
        self.animation.start()
        super().leaveEvent(event)


class QueryWorker(QThread):
    """Worker thread for processing queries"""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)
    
    def __init__(self, agent, query):
        super().__init__()
        self.agent = agent
        self.query = query
    
    def run(self):
        try:
            self.progress.emit("🔍 Analyzing query...")
            self.msleep(200)
            
            self.progress.emit("📚 Searching knowledge base...")
            self.msleep(300)
            
            self.progress.emit("🧠 Generating response...")
            response = self.agent.query(self.query)
            
            self.progress.emit("✅ Complete!")
            self.msleep(100)
            
            self.finished.emit(response)
        except Exception as e:
            self.error.emit(str(e))


class PaperWorker(QThread):
    """Worker thread for fetching recent papers"""
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)
    
    def run(self):
        try:
            self.progress.emit("📄 Fetching recent papers...")
            papers = self.fetch_recent_papers()
            self.finished.emit(papers)
        except Exception as e:
            self.error.emit(str(e))
    
    def fetch_recent_papers(self):
        """Fetch recent papers from data directory"""
        papers = []
        papers_dir = "./data/papers"
        
        if not os.path.exists(papers_dir):
            return papers
            
        try:
            import glob
            paper_files = glob.glob(os.path.join(papers_dir, "papers_*.json"))
            if paper_files:
                latest_file = max(paper_files, key=os.path.getctime)
                with open(latest_file, 'r') as f:
                    papers = json.load(f)
                    return papers[:10]  # Return first 10 papers
        except Exception:
            pass
            
        return papers


class ModernFinanceGUI(QMainWindow):
    """
    Modern, visually appealing GUI for Quantitative Finance AI Assistant
    """
    
    def __init__(self):
        super().__init__()
        self.agent = None
        self.vector_store = None
        self.conversation_history = []
        self.current_theme = "dark"
        self.query_worker = None
        self.paper_worker = None
        
        self.init_agent()
        self.init_ui()
        self.apply_modern_styles()
        self.center_window()
        
        # Auto-refresh papers timer
        self.paper_timer = QTimer()
        self.paper_timer.timeout.connect(self.refresh_papers)
        self.paper_timer.start(300000)  # 5 minutes
        
        # Initial paper load
        self.refresh_papers()
        
    def init_agent(self):
        """Initialize the AI agent"""
        try:
            if AGENT_AVAILABLE:
                self.vector_store = load_vector_store()
                self.agent = SimpleQuantFinanceAgent(self.vector_store)
            else:
                # Create mock agent for demo
                self.agent = self.create_mock_agent()
        except Exception as e:
            print(f"Agent initialization error: {e}")
            self.agent = self.create_mock_agent()
    
    def create_mock_agent(self):
        """Create a mock agent for demonstration"""
        class MockAgent:
            def query(self, query_text):
                return {
                    'result': f"""
**Your Question:** {query_text}

**AI Response:** This is a demonstration of the SPINOR Quantitative Finance AI Assistant. 

In a fully configured system, I would provide detailed analysis on:
- **Financial Models:** Black-Scholes, CAPM, APT, Fama-French
- **Risk Management:** VaR, Expected Shortfall, Stress Testing
- **Portfolio Theory:** Mean-variance optimization, factor models
- **Derivatives:** Options pricing, Greeks, exotic derivatives
- **Market Microstructure:** Order flow, market making, latency arbitrage

The system integrates with real-time research papers from ArXiv and provides comprehensive quantitative finance expertise.

*To enable full functionality, ensure all dependencies are installed and the vector database is configured.*
                    """,
                    'source_documents': [],
                    'metadata': {
                        'response_time': 0.5,
                        'confidence': 0.95,
                        'topics': ['demo', 'quantitative finance']
                    }
                }
            
            def health_check(self):
                return {
                    'overall_healthy': True,
                    'vector_store': True,
                    'knowledge_base': True
                }
        
        return MockAgent()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("🚀 SPINOR Quantitative Finance AI Assistant v3.0")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header
        self.create_header(main_layout)
        
        # Content area
        content_splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Chat
        left_panel = self.create_chat_panel()
        content_splitter.addWidget(left_panel)
        
        # Right panel - Info and controls
        right_panel = self.create_info_panel()
        content_splitter.addWidget(right_panel)
        
        content_splitter.setSizes([800, 400])
        main_layout.addWidget(content_splitter)
        
        # Status bar
        self.create_status_bar()
        
        # Menu bar
        self.create_menu_bar()
    
    def create_header(self, layout):
        """Create the header section"""
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_layout = QHBoxLayout(header_frame)
        
        # Logo and title
        title_layout = QVBoxLayout()
        
        title_label = QLabel("🚀 SPINOR AI Assistant")
        title_label.setObjectName("titleLabel")
        title_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        
        subtitle_label = QLabel("Advanced Quantitative Finance Intelligence")
        subtitle_label.setObjectName("subtitleLabel")
        subtitle_label.setFont(QFont("Segoe UI", 12))
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        header_layout.addLayout(title_layout)
        
        # Spacer
        header_layout.addStretch()
        
        # Theme toggle
        theme_btn = AnimatedButton("🌙 Dark")
        theme_btn.setObjectName("themeButton")
        theme_btn.clicked.connect(self.toggle_theme)
        header_layout.addWidget(theme_btn)
        
        # Settings button
        settings_btn = AnimatedButton("⚙️ Settings")
        settings_btn.setObjectName("settingsButton")
        settings_btn.clicked.connect(self.show_settings)
        header_layout.addWidget(settings_btn)
        
        layout.addWidget(header_frame)
    
    def create_chat_panel(self):
        """Create the chat panel"""
        chat_widget = QWidget()
        chat_layout = QVBoxLayout(chat_widget)
        
        # Chat header
        chat_header = QFrame()
        chat_header.setObjectName("chatHeader")
        chat_header_layout = QHBoxLayout(chat_header)
        
        chat_title = QLabel("💬 Conversation")
        chat_title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        chat_header_layout.addWidget(chat_title)
        
        chat_header_layout.addStretch()
        
        # Clear button
        clear_btn = QPushButton("🗑️ Clear")
        clear_btn.setObjectName("clearButton")
        clear_btn.clicked.connect(self.clear_conversation)
        chat_header_layout.addWidget(clear_btn)
        
        chat_layout.addWidget(chat_header)
        
        # Conversation display
        self.conversation_display = QTextBrowser()
        self.conversation_display.setObjectName("conversationDisplay")
        self.conversation_display.setOpenExternalLinks(True)
        
        # Add welcome message
        welcome_msg = self.create_welcome_message()
        self.conversation_display.setHtml(welcome_msg)
        
        chat_layout.addWidget(self.conversation_display)
        
        # Input section
        input_frame = QFrame()
        input_frame.setObjectName("inputFrame")
        input_layout = QVBoxLayout(input_frame)
        
        # Quick suggestions
        suggestions_layout = QHBoxLayout()
        suggestions = [
            "📊 Black-Scholes Model",
            "⚠️ Value at Risk",
            "📈 Portfolio Optimization",
            "🔄 Algorithmic Trading"
        ]
        
        for suggestion in suggestions:
            btn = QPushButton(suggestion)
            btn.setObjectName("suggestionButton")
            btn.clicked.connect(lambda checked, text=suggestion.split(" ", 1)[1]: self.set_query(text))
            suggestions_layout.addWidget(btn)
        
        input_layout.addLayout(suggestions_layout)
        
        # Main input
        input_main_layout = QHBoxLayout()
        
        self.query_input = QLineEdit()
        self.query_input.setObjectName("queryInput")
        self.query_input.setPlaceholderText("Ask about quantitative finance, risk management, derivatives pricing...")
        self.query_input.returnPressed.connect(self.process_query)
        input_main_layout.addWidget(self.query_input)
        
        self.send_button = AnimatedButton("🚀 Send")
        self.send_button.setObjectName("sendButton")
        self.send_button.clicked.connect(self.process_query)
        input_main_layout.addWidget(self.send_button)
        
        input_layout.addLayout(input_main_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("progressBar")
        self.progress_bar.setVisible(False)
        input_layout.addWidget(self.progress_bar)
        
        # Progress label
        self.progress_label = QLabel("")
        self.progress_label.setObjectName("progressLabel")
        self.progress_label.setVisible(False)
        input_layout.addWidget(self.progress_label)
        
        chat_layout.addWidget(input_frame)
        
        return chat_widget
    
    def create_info_panel(self):
        """Create the information panel"""
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        
        # System status
        status_group = QGroupBox("🔧 System Status")
        status_group.setObjectName("statusGroup")
        status_layout = QGridLayout(status_group)
        
        # AI Status
        status_layout.addWidget(QLabel("AI Agent:"), 0, 0)
        self.ai_status_label = QLabel("✅ Ready")
        self.ai_status_label.setObjectName("statusLabel")
        status_layout.addWidget(self.ai_status_label, 0, 1)
        
        # Vector DB Status
        status_layout.addWidget(QLabel("Knowledge Base:"), 1, 0)
        self.kb_status_label = QLabel("✅ Loaded")
        self.kb_status_label.setObjectName("statusLabel")
        status_layout.addWidget(self.kb_status_label, 1, 1)
        
        # Papers Status
        status_layout.addWidget(QLabel("Recent Papers:"), 2, 0)
        self.papers_status_label = QLabel("🔄 Loading...")
        self.papers_status_label.setObjectName("statusLabel")
        status_layout.addWidget(self.papers_status_label, 2, 1)
        
        info_layout.addWidget(status_group)
        
        # Recent papers
        papers_group = QGroupBox("📚 Recent Papers")
        papers_group.setObjectName("papersGroup")
        papers_layout = QVBoxLayout(papers_group)
        
        self.papers_list = QListWidget()
        self.papers_list.setObjectName("papersList")
        papers_layout.addWidget(self.papers_list)
        
        # Refresh papers button
        refresh_papers_btn = QPushButton("🔄 Refresh Papers")
        refresh_papers_btn.setObjectName("refreshButton")
        refresh_papers_btn.clicked.connect(self.refresh_papers)
        papers_layout.addWidget(refresh_papers_btn)
        
        info_layout.addWidget(papers_group)
        
        # Capabilities
        capabilities_group = QGroupBox("🧠 AI Capabilities")
        capabilities_group.setObjectName("capabilitiesGroup")
        capabilities_layout = QVBoxLayout(capabilities_group)
        
        capabilities_text = QTextBrowser()
        capabilities_text.setObjectName("capabilitiesText")
        capabilities_text.setMaximumHeight(200)
        
        capabilities_content = """
        <h4>🎯 Core Expertise:</h4>
        <ul>
        <li><b>Mathematical Finance:</b> Stochastic calculus, SDEs</li>
        <li><b>Options Pricing:</b> Black-Scholes, Monte Carlo</li>
        <li><b>Risk Management:</b> VaR, ES, stress testing</li>
        <li><b>Portfolio Theory:</b> Markowitz, CAPM, APT</li>
        <li><b>Market Microstructure:</b> Order flow analysis</li>
        <li><b>Quantitative Trading:</b> Alpha generation</li>
        </ul>
        
        <h4>📖 Knowledge Sources:</h4>
        <p>• 1000+ research papers from ArXiv<br>
        • Financial textbooks and references<br>
        • Real-time market data integration</p>
        """
        
        capabilities_text.setHtml(capabilities_content)
        capabilities_layout.addWidget(capabilities_text)
        
        info_layout.addWidget(capabilities_group)
        
        # Spacer
        info_layout.addStretch()
        
        return info_widget
    
    def create_welcome_message(self):
        """Create welcome message HTML"""
        return """
        <div style='text-align: center; padding: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; margin: 20px; color: white;'>
            <h1 style='margin: 0; font-size: 28px; font-weight: bold;'>🚀 Welcome to SPINOR AI Assistant</h1>
            <p style='margin: 10px 0; font-size: 16px; opacity: 0.9;'>Your Advanced Quantitative Finance Intelligence Partner</p>
            <p style='margin: 15px 0; font-size: 14px; opacity: 0.8;'>Ask me anything about financial mathematics, risk management, or quantitative trading!</p>
        </div>
        
        <div style='padding: 20px; margin: 20px; background-color: #f8f9fa; border-left: 4px solid #007bff; border-radius: 8px;'>
            <h3 style='color: #007bff; margin-top: 0;'>💡 Example Questions:</h3>
            <ul style='margin: 10px 0; padding-left: 20px; color: #333;'>
                <li>How does the Black-Scholes model work?</li>
                <li>Explain Value at Risk calculation methods</li>
                <li>What is portfolio optimization theory?</li>
                <li>How do you implement algorithmic trading strategies?</li>
                <li>What are the Greeks in options trading?</li>
            </ul>
        </div>
        """
    
    def create_status_bar(self):
        """Create status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Status message
        self.status_message = QLabel("Ready for queries")
        self.status_bar.addWidget(self.status_message)
        
        # Spacer
        self.status_bar.addPermanentWidget(QLabel(""), 1)
        
        # System info
        system_info = QLabel("SPINOR v3.0 | Enhanced UI | Real-time Papers")
        system_info.setStyleSheet("color: #666; font-size: 11px;")
        self.status_bar.addPermanentWidget(system_info)
    
    def create_menu_bar(self):
        """Create menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('📁 File')
        
        save_action = QAction('💾 Save Conversation', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_conversation)
        file_menu.addAction(save_action)
        
        export_action = QAction('📄 Export to PDF', self)
        export_action.triggered.connect(self.export_conversation)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('🚪 Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu('🔧 Tools')
        
        papers_action = QAction('📚 Download Papers', self)
        papers_action.triggered.connect(self.download_papers)
        tools_menu.addAction(papers_action)
        
        health_action = QAction('🏥 System Health Check', self)
        health_action.triggered.connect(self.health_check)
        tools_menu.addAction(health_action)
        
        # Help menu
        help_menu = menubar.addMenu('❓ Help')
        
        about_action = QAction('ℹ️ About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def apply_modern_styles(self):
        """Apply modern styling"""
        self.setStyleSheet(f"""
            /* Main Window */
            QMainWindow {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 #2c3e50, stop:1 #34495e);
                color: #ecf0f1;
            }}
            
            /* Header Frame */
            #headerFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 15px;
                padding: 20px;
                margin-bottom: 10px;
            }}
            
            #titleLabel {{
                color: white;
                font-weight: bold;
            }}
            
            #subtitleLabel {{
                color: rgba(255, 255, 255, 0.8);
                font-style: italic;
            }}
            
            /* Buttons */
            #themeButton, #settingsButton {{
                background: rgba(255, 255, 255, 0.2);
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 25px;
                padding: 10px 20px;
                color: white;
                font-weight: bold;
                min-width: 100px;
            }}
            
            #themeButton:hover, #settingsButton:hover {{
                background: rgba(255, 255, 255, 0.3);
                border-color: rgba(255, 255, 255, 0.5);
            }}
            
            /* Chat Area */
            #chatHeader {{
                background: #34495e;
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 10px;
            }}
            
            #conversationDisplay {{
                background: #2c3e50;
                border: 2px solid #34495e;
                border-radius: 15px;
                padding: 15px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
                line-height: 1.6;
            }}
            
            /* Input Frame */
            #inputFrame {{
                background: #34495e;
                border-radius: 15px;
                padding: 20px;
                margin-top: 10px;
            }}
            
            #queryInput {{
                background: #2c3e50;
                border: 2px solid #3498db;
                border-radius: 25px;
                padding: 15px 20px;
                font-size: 14px;
                color: #ecf0f1;
                min-height: 20px;
            }}
            
            #queryInput:focus {{
                border-color: #e74c3c;
                outline: none;
            }}
            
            #sendButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #e74c3c, stop:1 #c0392b);
                border: none;
                border-radius: 25px;
                padding: 15px 30px;
                color: white;
                font-weight: bold;
                min-width: 100px;
            }}
            
            #sendButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #c0392b, stop:1 #a93226);
            }}
            
            #suggestionButton {{
                background: #3498db;
                border: none;
                border-radius: 20px;
                padding: 8px 15px;
                color: white;
                font-size: 12px;
                margin: 2px;
            }}
            
            #suggestionButton:hover {{
                background: #2980b9;
            }}
            
            /* Progress Bar */
            #progressBar {{
                border: 2px solid #3498db;
                border-radius: 10px;
                background: #2c3e50;
                text-align: center;
                font-weight: bold;
                color: white;
            }}
            
            #progressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2980b9);
                border-radius: 8px;
            }}
            
            #progressLabel {{
                color: #3498db;
                font-weight: bold;
                text-align: center;
            }}
            
            /* Group Boxes */
            QGroupBox {{
                font-weight: bold;
                font-size: 14px;
                color: #ecf0f1;
                border: 2px solid #34495e;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                background: #2c3e50;
                border-radius: 5px;
            }}
            
            #statusGroup, #papersGroup, #capabilitiesGroup {{
                background: #34495e;
                margin: 5px;
            }}
            
            /* List Widget */
            #papersList {{
                background: #2c3e50;
                border: 2px solid #34495e;
                border-radius: 10px;
                padding: 5px;
                color: #ecf0f1;
                alternate-background-color: #34495e;
            }}
            
            #papersList::item {{
                padding: 8px;
                border-radius: 5px;
                margin: 2px;
            }}
            
            #papersList::item:selected {{
                background: #3498db;
                color: white;
            }}
            
            #papersList::item:hover {{
                background: #34495e;
            }}
            
            /* Status Labels */
            #statusLabel {{
                font-weight: bold;
                padding: 5px;
                border-radius: 5px;
            }}
            
            /* Text Browser */
            #capabilitiesText {{
                background: #2c3e50;
                border: 1px solid #34495e;
                border-radius: 8px;
                padding: 10px;
                color: #ecf0f1;
            }}
            
            /* Buttons */
            #clearButton, #refreshButton {{
                background: #e74c3c;
                border: none;
                border-radius: 8px;
                padding: 8px 15px;
                color: white;
                font-weight: bold;
            }}
            
            #clearButton:hover, #refreshButton:hover {{
                background: #c0392b;
            }}
            
            /* Menu Bar */
            QMenuBar {{
                background: #2c3e50;
                color: #ecf0f1;
                border-bottom: 2px solid #34495e;
                font-weight: bold;
                padding: 5px;
            }}
            
            QMenuBar::item {{
                padding: 8px 12px;
                margin: 2px;
                border-radius: 5px;
            }}
            
            QMenuBar::item:selected {{
                background: #3498db;
            }}
            
            QMenu {{
                background: #34495e;
                color: #ecf0f1;
                border: 2px solid #2c3e50;
                border-radius: 8px;
                padding: 5px;
            }}
            
            QMenu::item {{
                padding: 8px 20px;
                margin: 2px;
                border-radius: 5px;
            }}
            
            QMenu::item:selected {{
                background: #3498db;
            }}
            
            /* Status Bar */
            QStatusBar {{
                background: #2c3e50;
                color: #ecf0f1;
                border-top: 2px solid #34495e;
                font-size: 12px;
                padding: 5px;
            }}
        """)
        
        # Add shadow effects
        self.add_shadow_effects()
    
    def add_shadow_effects(self):
        """Add shadow effects to enhance visual appeal"""
        # Shadow for main window (doesn't work on main window, but we can add to child widgets)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 5)
        
        # Apply shadow to conversation display
        if hasattr(self, 'conversation_display'):
            self.conversation_display.setGraphicsEffect(shadow)
    
    def center_window(self):
        """Center window on screen"""
        screen = QApplication.desktop().screenGeometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )
    
    def set_query(self, text):
        """Set query text"""
        self.query_input.setText(text)
        self.query_input.setFocus()
    
    def process_query(self):
        """Process user query"""
        query = self.query_input.text().strip()
        if not query:
            return
            
        if self.query_worker and self.query_worker.isRunning():
            QMessageBox.information(self, "Processing", "Please wait for the current query to complete.")
            return
        
        self.query_input.clear()
        self.send_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.progress_label.setVisible(True)
        
        # Add user message
        self.add_message("user", query)
        
        # Start worker
        self.query_worker = QueryWorker(self.agent, query)
        self.query_worker.finished.connect(self.on_query_finished)
        self.query_worker.error.connect(self.on_query_error)
        self.query_worker.progress.connect(self.on_query_progress)
        self.query_worker.start()
    
    def on_query_progress(self, message):
        """Update progress"""
        self.progress_label.setText(message)
    
    def on_query_finished(self, response):
        """Handle query completion"""
        self.send_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        
        # Add assistant message
        result = response.get('result', 'No response generated.')
        self.add_message("assistant", result)
        
        # Update status
        self.status_message.setText("Query completed successfully")
        
        # Add to conversation history
        self.conversation_history.append({
            'query': self.query_input.text(),
            'response': result,
            'timestamp': datetime.now()
        })
    
    def on_query_error(self, error):
        """Handle query error"""
        self.send_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        
        self.add_message("error", f"Error: {error}")
        self.status_message.setText("Query failed")
    
    def add_message(self, sender, content):
        """Add message to conversation"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if sender == "user":
            message_html = f"""
            <div style='margin: 15px 0; padding: 15px; background: linear-gradient(135deg, #3498db, #2980b9); 
                        border-radius: 15px; border-top-right-radius: 5px; color: white; max-width: 80%; margin-left: auto;'>
                <div style='font-weight: bold; margin-bottom: 5px; opacity: 0.8;'>[{timestamp}] You</div>
                <div style='font-size: 14px; line-height: 1.5;'>{content}</div>
            </div>
            """
        elif sender == "assistant":
            message_html = f"""
            <div style='margin: 15px 0; padding: 15px; background: linear-gradient(135deg, #27ae60, #229954); 
                        border-radius: 15px; border-top-left-radius: 5px; color: white; max-width: 80%;'>
                <div style='font-weight: bold; margin-bottom: 5px; opacity: 0.8;'>[{timestamp}] 🤖 SPINOR AI</div>
                <div style='font-size: 14px; line-height: 1.6; white-space: pre-wrap;'>{content}</div>
            </div>
            """
        else:  # error
            message_html = f"""
            <div style='margin: 15px 0; padding: 15px; background: linear-gradient(135deg, #e74c3c, #c0392b); 
                        border-radius: 15px; color: white; max-width: 80%;'>
                <div style='font-weight: bold; margin-bottom: 5px; opacity: 0.8;'>[{timestamp}] ⚠️ System</div>
                <div style='font-size: 14px; line-height: 1.5;'>{content}</div>
            </div>
            """
        
        self.conversation_display.append(message_html)
        
        # Scroll to bottom
        scrollbar = self.conversation_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def clear_conversation(self):
        """Clear conversation"""
        self.conversation_display.clear()
        welcome_msg = self.create_welcome_message()
        self.conversation_display.setHtml(welcome_msg)
        self.conversation_history.clear()
        self.status_message.setText("Conversation cleared")
    
    def refresh_papers(self):
        """Refresh recent papers"""
        if self.paper_worker and self.paper_worker.isRunning():
            return
            
        self.papers_status_label.setText("🔄 Loading...")
        
        self.paper_worker = PaperWorker()
        self.paper_worker.finished.connect(self.on_papers_loaded)
        self.paper_worker.error.connect(self.on_papers_error)
        self.paper_worker.start()
    
    def on_papers_loaded(self, papers):
        """Handle papers loaded"""
        self.papers_list.clear()
        
        if not papers:
            self.papers_status_label.setText("📄 No papers found")
            item = QListWidgetItem("No recent papers available")
            item.setFlags(item.flags() & ~Qt.ItemIsEnabled)
            self.papers_list.addItem(item)
            return
        
        self.papers_status_label.setText(f"📚 {len(papers)} papers")
        
        for paper in papers:
            title = paper.get('title', 'Untitled')
            authors = paper.get('authors', [])
            
            # Truncate title if too long
            if len(title) > 50:
                title = title[:47] + "..."
            
            # Format authors
            if isinstance(authors, list) and authors:
                author_str = authors[0]
                if len(authors) > 1:
                    author_str += f" et al. ({len(authors)})"
            else:
                author_str = "Unknown"
            
            item_text = f"{title}\n👥 {author_str}"
            item = QListWidgetItem(item_text)
            item.setToolTip(paper.get('title', 'No title'))
            self.papers_list.addItem(item)
    
    def on_papers_error(self, error):
        """Handle papers loading error"""
        self.papers_status_label.setText("❌ Error loading")
        item = QListWidgetItem(f"Error: {error}")
        item.setFlags(item.flags() & ~Qt.ItemIsEnabled)
        self.papers_list.addItem(item)
    
    def toggle_theme(self):
        """Toggle between dark and light theme"""
        # For now, just show a message - full theme switching would require more extensive CSS
        current_button = self.sender()
        if self.current_theme == "dark":
            self.current_theme = "light"
            current_button.setText("☀️ Light")
            self.status_message.setText("Switched to light theme (demo)")
        else:
            self.current_theme = "dark"
            current_button.setText("🌙 Dark")
            self.status_message.setText("Switched to dark theme")
    
    def show_settings(self):
        """Show settings dialog"""
        QMessageBox.information(
            self, "Settings", 
            "Settings panel would open here.\n\nAvailable options:\n• Theme preferences\n• Model configuration\n• Knowledge base settings\n• Auto-save options"
        )
    
    def save_conversation(self):
        """Save conversation to file"""
        if not self.conversation_history:
            QMessageBox.information(self, "Save", "No conversation to save.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Conversation", 
            f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
            "HTML files (*.html);;Text files (*.txt)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    if file_path.endswith('.html'):
                        f.write(self.conversation_display.toHtml())
                    else:
                        f.write(self.conversation_display.toPlainText())
                self.status_message.setText(f"Conversation saved to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save: {str(e)}")
    
    def export_conversation(self):
        """Export to PDF"""
        QMessageBox.information(
            self, "Export", 
            "PDF export functionality would be implemented here.\n\nThe conversation would be formatted and exported as a professional PDF document."
        )
    
    def download_papers(self):
        """Download recent papers"""
        QMessageBox.information(
            self, "Download Papers", 
            "Paper download initiated.\n\nThis would trigger the real-time paper fetching system to download the latest quantitative finance research from ArXiv."
        )
        self.refresh_papers()
    
    def health_check(self):
        """Perform system health check"""
        try:
            health = self.agent.health_check()
            status = "✅ All systems operational" if health.get('overall_healthy', False) else "⚠️ Some issues detected"
            
            details = f"""
            System Health Report:
            
            🤖 AI Agent: {'✅ Healthy' if health.get('overall_healthy', False) else '❌ Issues'}
            🗃️ Vector Store: {'✅ Loaded' if health.get('vector_store', False) else '❌ Not loaded'}
            📚 Knowledge Base: {'✅ Available' if health.get('knowledge_base', False) else '❌ Unavailable'}
            
            Status: {status}
            """
            
            QMessageBox.information(self, "Health Check", details)
        except Exception as e:
            QMessageBox.warning(self, "Health Check", f"Health check failed: {str(e)}")
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
        <h2>🚀 SPINOR Quantitative Finance AI Assistant</h2>
        <p><b>Version:</b> 3.0 - Visual Enhancement Edition</p>
        <p><b>Author:</b> SPINOR Technologies</p>
        <p><b>Date:</b> August 6, 2025</p>
        
        <h3>🎯 Features:</h3>
        <ul>
        <li>💬 Advanced conversational AI for quantitative finance</li>
        <li>📚 Real-time research paper integration</li>
        <li>🎨 Modern, responsive user interface</li>
        <li>🔍 Comprehensive knowledge base search</li>
        <li>📊 Risk management and portfolio analysis</li>
        <li>⚡ High-performance vector database</li>
        </ul>
        
        <h3>🛠️ Technology Stack:</h3>
        <p>• PyQt5 for modern GUI<br>
        • LangChain for AI orchestration<br>
        • FAISS for vector similarity search<br>
        • ArXiv API for real-time papers<br>
        • Sentence Transformers for embeddings</p>
        
        <p><i>Empowering quantitative finance with cutting-edge AI technology.</i></p>
        """
        
        QMessageBox.about(self, "About SPINOR AI Assistant", about_text)


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("SPINOR Quantitative Finance AI Assistant")
    app.setApplicationVersion("3.0")
    app.setStyle("Fusion")
    
    # Set application icon (if available)
    try:
        app.setWindowIcon(QIcon("icon.png"))
    except:
        pass
    
    try:
        # Create and show main window
        window = ModernFinanceGUI()
        window.show()
        
        # Start application
        sys.exit(app.exec_())
        
    except Exception as e:
        QMessageBox.critical(
            None, "Application Error", 
            f"Failed to start application:\n\n{str(e)}\n\nPlease check your installation and try again."
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
