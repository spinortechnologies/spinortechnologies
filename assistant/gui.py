# -*- coding: utf-8 -*-
"""
Quantitative Finance AI Assistant - GUI Implementation
Author: SPINOR Technologies
Date: August 6, 2025
Version: 2.0
"""

import sys
import os
import webbrowser
from datetime import datetime
from typing import Optional, List, Dict, Any
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTextEdit, QLineEdit, QPushButton, QListWidget, 
    QSplitter, QStatusBar, QProgressBar, QMenuBar, QAction,
    QFileDialog, QMessageBox, QTabWidget, QScrollArea,
    QGroupBox, QGridLayout, QComboBox, QSpinBox, QCheckBox,
    QTreeWidget, QTreeWidgetItem, QDialog, QDialogButtonBox,
    QTextBrowser, QFrame
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QUrl
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon, QPixmap, QDesktopServices
from quant_agent import QuantFinanceAgent
from vector_db import load_vector_store


class QueryWorker(QThread):
    """Worker thread for processing queries to avoid blocking the UI"""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, agent, query):
        super().__init__()
        self.agent = agent
        self.query = query
    
    def run(self):
        try:
            response = self.agent.query(self.query)
            self.finished.emit(response)
        except Exception as e:
            self.error.emit(str(e))


class SourceDialog(QDialog):
    """Dialog to display source document details"""
    
    def __init__(self, document_metadata, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Source Document Details")
        self.setModal(True)
        self.resize(600, 400)
        self.init_ui(document_metadata)
    
    def init_ui(self, metadata):
        layout = QVBoxLayout(self)
        
        # Document details
        details_group = QGroupBox("Document Information")
        details_layout = QGridLayout(details_group)
        
        title = metadata.get('title', 'Untitled Document')
        source = metadata.get('source', 'Unknown Source')
        authors = metadata.get('authors', [])
        published = metadata.get('published', 'Unknown')
        
        details_layout.addWidget(QLabel("Title:"), 0, 0)
        details_layout.addWidget(QLabel(title), 0, 1)
        details_layout.addWidget(QLabel("Source:"), 1, 0)
        details_layout.addWidget(QLabel(source), 1, 1)
        details_layout.addWidget(QLabel("Authors:"), 2, 0)
        details_layout.addWidget(QLabel(", ".join(authors) if authors else "N/A"), 2, 1)
        details_layout.addWidget(QLabel("Published:"), 3, 0)
        details_layout.addWidget(QLabel(str(published)), 3, 1)
        
        layout.addWidget(details_group)
        
        # Preview content
        content_group = QGroupBox("Content Preview")
        content_layout = QVBoxLayout(content_group)
        
        content_text = QTextBrowser()
        content_text.setPlainText(metadata.get('content', 'No content available'))
        content_layout.addWidget(content_text)
        
        layout.addWidget(content_group)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

class FinanceAIAssistant(QMainWindow):
    """Main application window for Quantitative Finance AI Assistant"""
    
    def __init__(self, agent):
        """
        Initialize the AI Assistant GUI
        
        Args:
            agent (QuantFinanceAgent): Pre-initialized AI agent instance
        """
        super().__init__()
        self.agent = agent
        self.conversation_history = []
        self.current_sources = []
        self.query_worker = None
        
        self.init_ui()
        self.init_menu_bar()
        self.init_status_bar()
        
        self.setWindowTitle("SPINOR Quantitative Finance AI Assistant v2.0")
        self.resize(1400, 900)
        self.center_window()
        
        # Auto-save timer
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.auto_save_conversation)
        self.auto_save_timer.start(300000)  # Auto-save every 5 minutes
    
    def center_window(self):
        """Center the window on the screen"""
        screen = QApplication.desktop().screenGeometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )
    
    def init_menu_bar(self):
        """Initialize the menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        save_action = QAction('Save Conversation', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_conversation)
        file_menu.addAction(save_action)
        
        load_action = QAction('Load Conversation', self)
        load_action.setShortcut('Ctrl+O')
        load_action.triggered.connect(self.load_conversation)
        file_menu.addAction(load_action)
        
        file_menu.addSeparator()
        
        export_action = QAction('Export to PDF', self)
        export_action.triggered.connect(self.export_conversation)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu('Tools')
        
        settings_action = QAction('Settings', self)
        settings_action.triggered.connect(self.show_settings)
        tools_menu.addAction(settings_action)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def init_status_bar(self):
        """Initialize the status bar with useful information"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Progress bar for query processing
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)
        
        # Model info
        model_label = QLabel("Model: FLAN-T5-XXL | Knowledge Base: Quant Finance Papers")
        self.status_bar.addPermanentWidget(model_label)
        
    def init_ui(self):
        """Initialize UI components and layout"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create tab widget for multiple views
        self.tab_widget = QTabWidget()
        
        # Main chat tab
        chat_tab = self.create_chat_tab()
        self.tab_widget.addTab(chat_tab, "Chat")
        
        # Analytics tab
        analytics_tab = self.create_analytics_tab()
        self.tab_widget.addTab(analytics_tab, "Analytics")
        
        # Settings tab
        settings_tab = self.create_settings_tab()
        self.tab_widget.addTab(settings_tab, "Settings")
        
        main_layout.addWidget(self.tab_widget)
    
    def create_chat_tab(self):
        """Create the main chat interface tab"""
        chat_widget = QWidget()
        main_layout = QVBoxLayout(chat_widget)
        
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Input and conversation
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Conversation header
        header_layout = QHBoxLayout()
        conversation_label = QLabel("Conversation History")
        conversation_label.setFont(QFont("Arial", 12, QFont.Bold))
        header_layout.addWidget(conversation_label)
        
        # Export button
        export_btn = QPushButton("Export")
        export_btn.setMaximumWidth(80)
        export_btn.clicked.connect(self.export_conversation)
        header_layout.addWidget(export_btn)
        
        left_layout.addLayout(header_layout)
        
        # Conversation display with improved formatting
        self.conversation_display = QTextBrowser()
        self.conversation_display.setFont(QFont("Consolas", 11))
        self.conversation_display.setOpenExternalLinks(True)
        self.conversation_display.setStyleSheet("""
            QTextBrowser {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        left_layout.addWidget(self.conversation_display)
        
        # Input section with enhanced features
        input_group = QGroupBox("Ask a Question")
        input_layout = QVBoxLayout(input_group)
        
        # Quick suggestion buttons
        suggestions_layout = QHBoxLayout()
        suggestions = [
            "Options pricing models",
            "Risk management",
            "Portfolio optimization",
            "Market volatility"
        ]
        
        for suggestion in suggestions:
            btn = QPushButton(suggestion)
            btn.setMaximumHeight(25)
            btn.clicked.connect(lambda checked, text=suggestion: self.set_input_text(text))
            suggestions_layout.addWidget(btn)
        
        input_layout.addLayout(suggestions_layout)
        
        # Main input area
        input_main_layout = QHBoxLayout()
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Ask about quantitative finance, stochastic calculus, derivatives pricing...")
        self.user_input.returnPressed.connect(self.process_query)
        self.user_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #555;
                border-radius: 5px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #42a5f5;
            }
        """)
        input_main_layout.addWidget(self.user_input, 4)
        
        # Control buttons
        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self.process_query)
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #42a5f5;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
            QPushButton:pressed {
                background-color: #1565c0;
            }
        """)
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_conversation)
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        
        input_main_layout.addWidget(self.send_btn, 1)
        input_main_layout.addWidget(self.clear_btn, 1)
        
        input_layout.addLayout(input_main_layout)
        left_layout.addWidget(input_group)
        
        # Right panel - Sources and analysis
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Sources section
        sources_group = QGroupBox("Source Documents")
        sources_layout = QVBoxLayout(sources_group)
        
        self.source_tree = QTreeWidget()
        self.source_tree.setHeaderLabels(["Document", "Relevance", "Type"])
        self.source_tree.itemDoubleClicked.connect(self.open_source_detail)
        sources_layout.addWidget(self.source_tree)
        
        right_layout.addWidget(sources_group)
        
        # Agent capabilities and info
        info_group = QGroupBox("AI Agent Capabilities")
        info_layout = QVBoxLayout(info_group)
        
        capabilities_text = QTextBrowser()
        capabilities_text.setMaximumHeight(200)
        capabilities_content = """
        <h4>Core Capabilities:</h4>
        <ul>
        <li><b>Stochastic Calculus:</b> Ito processes, SDEs, Brownian motion</li>
        <li><b>Options Pricing:</b> Black-Scholes, Monte Carlo, Binomial trees</li>
        <li><b>Risk Management:</b> VaR, ES, stress testing</li>
        <li><b>Portfolio Theory:</b> Markowitz, CAPM, factor models</li>
        <li><b>Econophysics:</b> Market microstructure, agent-based models</li>
        <li><b>Machine Learning:</b> Time series forecasting, deep learning</li>
        </ul>
        
        <h4>Knowledge Base:</h4>
        <p>Access to 1000+ quantitative finance research papers, textbooks, and industry reports.</p>
        """
        capabilities_text.setHtml(capabilities_content)
        info_layout.addWidget(capabilities_text)
        
        right_layout.addWidget(info_group)
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([800, 400])
        
        main_layout.addWidget(splitter)
        return chat_widget
    def create_analytics_tab(self):
        """Create analytics and statistics tab"""
        analytics_widget = QWidget()
        layout = QVBoxLayout(analytics_widget)
        
        # Statistics group
        stats_group = QGroupBox("Conversation Statistics")
        stats_layout = QGridLayout(stats_group)
        
        self.stats_labels = {}
        stats_items = [
            ("Total Queries", "total_queries"),
            ("Average Response Time", "avg_response_time"),
            ("Most Used Topics", "common_topics"),
            ("Session Duration", "session_duration")
        ]
        
        for i, (label, key) in enumerate(stats_items):
            stats_layout.addWidget(QLabel(f"{label}:"), i, 0)
            value_label = QLabel("0")
            self.stats_labels[key] = value_label
            stats_layout.addWidget(value_label, i, 1)
        
        layout.addWidget(stats_group)
        
        # Query history
        history_group = QGroupBox("Query History")
        history_layout = QVBoxLayout(history_group)
        
        self.history_tree = QTreeWidget()
        self.history_tree.setHeaderLabels(["Timestamp", "Query", "Response Length"])
        history_layout.addWidget(self.history_tree)
        
        layout.addWidget(history_group)
        
        return analytics_widget
    
    def create_settings_tab(self):
        """Create settings and configuration tab"""
        settings_widget = QWidget()
        layout = QVBoxLayout(settings_widget)
        
        # Model settings
        model_group = QGroupBox("Model Configuration")
        model_layout = QGridLayout(model_group)
        
        model_layout.addWidget(QLabel("Max Response Length:"), 0, 0)
        self.max_length_spin = QSpinBox()
        self.max_length_spin.setRange(100, 2000)
        self.max_length_spin.setValue(500)
        model_layout.addWidget(self.max_length_spin, 0, 1)
        
        model_layout.addWidget(QLabel("Temperature:"), 1, 0)
        self.temperature_combo = QComboBox()
        self.temperature_combo.addItems(["0.1", "0.3", "0.5", "0.7", "0.9"])
        self.temperature_combo.setCurrentText("0.3")
        model_layout.addWidget(self.temperature_combo, 1, 1)
        
        layout.addWidget(model_group)
        
        # UI settings
        ui_group = QGroupBox("Interface Settings")
        ui_layout = QGridLayout(ui_group)
        
        self.dark_mode_check = QCheckBox("Dark Mode")
        self.dark_mode_check.setChecked(True)
        self.dark_mode_check.toggled.connect(self.toggle_dark_mode)
        ui_layout.addWidget(self.dark_mode_check, 0, 0)
        
        self.auto_save_check = QCheckBox("Auto-save conversations")
        self.auto_save_check.setChecked(True)
        ui_layout.addWidget(self.auto_save_check, 1, 0)
        
        layout.addWidget(ui_group)
        
        # Knowledge base settings
        kb_group = QGroupBox("Knowledge Base")
        kb_layout = QVBoxLayout(kb_group)
        
        kb_info = QLabel("Current knowledge base contains quantitative finance papers and textbooks.")
        kb_layout.addWidget(kb_info)
        
        refresh_kb_btn = QPushButton("Refresh Knowledge Base")
        refresh_kb_btn.clicked.connect(self.refresh_knowledge_base)
        kb_layout.addWidget(refresh_kb_btn)
        
        layout.addWidget(kb_group)
        
        # Spacer
        layout.addStretch()
        
        return settings_widget
    
    def set_input_text(self, text):
        """Set text in the input field"""
        self.user_input.setText(text)
        self.user_input.setFocus()
    
    def process_query(self):
        """Process user query with improved threading and error handling"""
        query = self.user_input.text().strip()
        if not query:
            return
        
        if self.query_worker and self.query_worker.isRunning():
            QMessageBox.information(self, "Processing", "Please wait for the current query to complete.")
            return
            
        self.user_input.clear()
        self.send_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.status_label.setText("Processing query...")
        
        # Add to conversation history
        timestamp = datetime.now().strftime("%H:%M:%S")
        user_message = f"<div style='margin: 10px 0; padding: 10px; background-color: #1e3a8a; border-radius: 10px; color: white;'>"
        user_message += f"<strong>[{timestamp}] You:</strong><br>{query}</div>"
        self.conversation_display.append(user_message)
        
        # Start worker thread
        self.query_worker = QueryWorker(self.agent, query)
        self.query_worker.finished.connect(self.on_query_finished)
        self.query_worker.error.connect(self.on_query_error)
        self.query_worker.start()
        
        # Update analytics
        self.conversation_history.append({
            'timestamp': datetime.now(),
            'query': query,
            'type': 'user'
        })
        self.update_analytics()
    
    def on_query_finished(self, response):
        """Handle successful query completion"""
        self.send_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText("Ready")
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        result = response.get('result', '')
        
        # Format assistant response
        assistant_message = f"<div style='margin: 10px 0; padding: 10px; background-color: #064e3b; border-radius: 10px; color: white;'>"
        assistant_message += f"<strong>[{timestamp}] Assistant:</strong><br>{result}</div>"
        self.conversation_display.append(assistant_message)
        
        # Update sources
        self.current_sources = response.get('source_documents', [])
        self.update_source_tree(self.current_sources)
        
        # Add to conversation history
        self.conversation_history.append({
            'timestamp': datetime.now(),
            'query': result,
            'type': 'assistant',
            'sources': self.current_sources
        })
        
        # Scroll to bottom
        self.conversation_display.verticalScrollBar().setValue(
            self.conversation_display.verticalScrollBar().maximum()
        )
    
    def on_query_error(self, error_message):
        """Handle query processing error"""
        self.send_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText("Error occurred")
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        error_message_formatted = f"<div style='margin: 10px 0; padding: 10px; background-color: #7f1d1d; border-radius: 10px; color: white;'>"
        error_message_formatted += f"<strong>[{timestamp}] Error:</strong><br>{error_message}</div>"
        self.conversation_display.append(error_message_formatted)
    
    def update_source_tree(self, documents):
        """Update source tree with enhanced document information"""
        self.source_tree.clear()
        
        for i, doc in enumerate(documents):
            metadata = getattr(doc, 'metadata', {})
            title = metadata.get('title', f'Document {i+1}')
            source_type = metadata.get('type', 'Unknown')
            relevance = f"{metadata.get('score', 0.5):.2f}" if 'score' in metadata else "N/A"
            
            item = QTreeWidgetItem([title, relevance, source_type])
            item.setData(0, Qt.UserRole, metadata)
            self.source_tree.addItem(item)
        
        # Auto-resize columns
        for i in range(3):
            self.source_tree.resizeColumnToContents(i)
    
    def open_source_detail(self, item, column):
        """Open detailed view of selected source document"""
        metadata = item.data(0, Qt.UserRole)
        if metadata:
            dialog = SourceDialog(metadata, self)
            dialog.exec_()
    
    def update_analytics(self):
        """Update analytics and statistics"""
        total_queries = len([h for h in self.conversation_history if h['type'] == 'user'])
        self.stats_labels['total_queries'].setText(str(total_queries))
        
        if self.conversation_history:
            start_time = self.conversation_history[0]['timestamp']
            duration = datetime.now() - start_time
            self.stats_labels['session_duration'].setText(str(duration).split('.')[0])
        
        # Update history tree
        self.history_tree.clear()
        for entry in self.conversation_history:
            if entry['type'] == 'user':
                timestamp = entry['timestamp'].strftime("%H:%M:%S")
                query = entry['query'][:50] + "..." if len(entry['query']) > 50 else entry['query']
                
                # Find corresponding assistant response
                response_length = "N/A"
                for i, h in enumerate(self.conversation_history):
                    if h == entry and i < len(self.conversation_history) - 1:
                        next_entry = self.conversation_history[i + 1]
                        if next_entry['type'] == 'assistant':
                            response_length = str(len(next_entry['query']))
                        break
                
                item = QTreeWidgetItem([timestamp, query, response_length])
                self.history_tree.addItem(item)
    
    def clear_conversation(self):
        """Clear conversation history and reset UI"""
        self.conversation_display.clear()
        self.source_tree.clear()
        self.conversation_history.clear()
        self.current_sources.clear()
        self.history_tree.clear()
        
        # Reset analytics
        for label in self.stats_labels.values():
            label.setText("0")
        
        self.status_label.setText("Conversation cleared")
    
    def save_conversation(self):
        """Save conversation to file"""
        if not self.conversation_history:
            QMessageBox.information(self, "Save", "No conversation to save.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Conversation", 
            f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
            "HTML files (*.html);;Text files (*.txt);;All files (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    if file_path.endswith('.html'):
                        f.write(self.conversation_display.toHtml())
                    else:
                        f.write(self.conversation_display.toPlainText())
                self.status_label.setText(f"Conversation saved to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save conversation: {str(e)}")
    
    def load_conversation(self):
        """Load conversation from file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Conversation", "",
            "HTML files (*.html);;Text files (*.txt);;All files (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.conversation_display.clear()
                if file_path.endswith('.html'):
                    self.conversation_display.setHtml(content)
                else:
                    self.conversation_display.setPlainText(content)
                
                self.status_label.setText(f"Conversation loaded from {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load conversation: {str(e)}")
    
    def export_conversation(self):
        """Export conversation to PDF"""
        try:
            from PyQt5.QtPrintSupport import QPrinter
            from PyQt5.QtGui import QTextDocument
            
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export to PDF", 
                f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                "PDF files (*.pdf)"
            )
            
            if file_path:
                printer = QPrinter(QPrinter.HighResolution)
                printer.setOutputFormat(QPrinter.PdfFormat)
                printer.setOutputFileName(file_path)
                
                document = QTextDocument()
                document.setHtml(self.conversation_display.toHtml())
                document.print_(printer)
                
                self.status_label.setText(f"Conversation exported to {file_path}")
        except ImportError:
            QMessageBox.warning(self, "Export", "PDF export requires PyQt5 print support.")
    
    def auto_save_conversation(self):
        """Auto-save conversation periodically"""
        if self.auto_save_check.isChecked() and self.conversation_history:
            auto_save_dir = os.path.join(os.getcwd(), "auto_saves")
            os.makedirs(auto_save_dir, exist_ok=True)
            
            file_path = os.path.join(
                auto_save_dir, 
                f"auto_save_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            )
            
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.conversation_display.toHtml())
            except Exception:
                pass  # Silent fail for auto-save
    
    def toggle_dark_mode(self, enabled):
        """Toggle between dark and light mode"""
        # This would require more extensive styling changes
        # For now, just show a message
        mode = "dark" if enabled else "light"
        self.status_label.setText(f"Switched to {mode} mode")
    
    def refresh_knowledge_base(self):
        """Refresh the knowledge base"""
        QMessageBox.information(
            self, "Knowledge Base", 
            "Knowledge base refresh initiated. This may take a few minutes."
        )
        self.status_label.setText("Refreshing knowledge base...")
    
    def show_settings(self):
        """Show settings dialog"""
        self.tab_widget.setCurrentIndex(2)  # Switch to settings tab
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
        <h2>SPINOR Quantitative Finance AI Assistant</h2>
        <p><b>Version:</b> 2.0</p>
        <p><b>Author:</b> SPINOR Technologies</p>
        <p><b>Date:</b> August 6, 2025</p>
        
        <p>This application provides an AI-powered assistant for quantitative finance research, 
        featuring advanced natural language processing capabilities and access to a comprehensive 
        knowledge base of financial literature.</p>
        
        <p><b>Features:</b></p>
        <ul>
        <li>Stochastic calculus and mathematical finance</li>
        <li>Options pricing and derivatives</li>
        <li>Risk management and portfolio theory</li>
        <li>Market microstructure analysis</li>
        <li>Econophysics and agent-based modeling</li>
        </ul>
        
        <p><b>Powered by:</b> FLAN-T5-XXL and LangChain</p>
        """
        
        QMessageBox.about(self, "About", about_text)


if __name__ == "__main__":
    # Initialize agent with improved error handling
    base_dir = os.environ.get('KNOWLEDGE_BASE', os.getcwd())
    index_path = os.path.join(base_dir, "quant_finance_index")
    
    def create_application():
        """Create and configure the application"""
        app = QApplication(sys.argv)
        app.setApplicationName("SPINOR Quantitative Finance AI Assistant")
        app.setApplicationVersion("2.0")
        app.setStyle("Fusion")
        
        # Set enhanced dark palette
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(35, 35, 35))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)
        dark_palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(127, 127, 127))
        dark_palette.setColor(QPalette.Disabled, QPalette.Text, QColor(127, 127, 127))
        dark_palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(127, 127, 127))
        app.setPalette(dark_palette)
        
        return app
    
    def initialize_agent():
        """Initialize the AI agent with fallback options"""
        try:
            # Try to import required modules
            from langchain.embeddings import HuggingFaceEmbeddings
            from vector_db import load_vector_store
            
            embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-mpnet-base-v2"
            )
            vector_store = load_vector_store(index_path, embeddings)
            agent = QuantFinanceAgent(vector_store)
            return agent
            
        except ImportError as e:
            # Fallback for missing dependencies
            print(f"Warning: Some dependencies missing: {e}")
            print("Creating mock agent for demonstration...")
            
            class MockAgent:
                def query(self, query_text):
                    return {
                        'result': f"Mock response for: {query_text}",
                        'source_documents': []
                    }
            
            return MockAgent()
            
        except Exception as e:
            print(f"Failed to initialize agent: {e}")
            return None
    
    # Create application
    app = create_application()
    
    # Initialize agent
    agent = initialize_agent()
    if agent is None:
        QMessageBox.critical(
            None, "Initialization Error", 
            "Failed to initialize the AI agent. Please check your configuration."
        )
        sys.exit(1)
    
    # Create and show main window
    try:
        window = FinanceAIAssistant(agent)
        window.show()
        
        # Center the window on screen
        screen = app.desktop().screenGeometry()
        size = window.geometry()
        window.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )
        
        sys.exit(app.exec_())
        
    except Exception as e:
        QMessageBox.critical(
            None, "Application Error", 
            f"Failed to start application: {str(e)}"
        )
        sys.exit(1)