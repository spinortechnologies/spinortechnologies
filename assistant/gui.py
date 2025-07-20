# -*- coding: utf-8 -*-
"""
Quantitative Finance AI Assistant - GUI Implementation
Author: [Your Name]
Date: [Date]
"""

import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QTextEdit, QLineEdit, QPushButton, QListWidget, 
                             QSplitter, QStatusBar)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor
from quant_agent import QuantFinanceAgent
from vector_db import load_vector_store

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
        self.init_ui()
        self.setWindowTitle("Quantitative Finance AI Assistant")
        self.resize(1200, 800)
        
    def init_ui(self):
        """Initialize UI components and layout"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Input and conversation
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        self.conversation_display = QTextEdit()
        self.conversation_display.setReadOnly(True)
        self.conversation_display.setFont(QFont("Consolas", 11))
        left_layout.addWidget(QLabel("Conversation:"))
        left_layout.addWidget(self.conversation_display)
        
        input_layout = QHBoxLayout()
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Ask about quantitative finance...")
        self.user_input.returnPressed.connect(self.process_query)
        input_layout.addWidget(self.user_input, 4)
        
        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self.process_query)
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_conversation)
        input_layout.addWidget(self.send_btn, 1)
        input_layout.addWidget(self.clear_btn, 1)
        
        left_layout.addLayout(input_layout)
        
        # Right panel - Sources and info
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        right_layout.addWidget(QLabel("Source Documents:"))
        self.source_list = QListWidget()
        self.source_list.itemDoubleClicked.connect(self.open_source)
        right_layout.addWidget(self.source_list)
        
        info_box = QWidget()
        info_layout = QVBoxLayout(info_box)
        info_layout.addWidget(QLabel("Agent Capabilities:"))
        
        capabilities = [
            "- Stochastic calculus models",
            "- Volatility forecasting",
            "- Options pricing",
            "- Market microstructure analysis",
            "- Econophysics simulations"
        ]
        
        for cap in capabilities:
            info_layout.addWidget(QLabel(cap))
        
        right_layout.addWidget(info_box)
        
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([700, 300])
        
        main_layout.addWidget(splitter)
        
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready | Model: FLAN-T5-XXL | Knowledge Base: Quant Finance Papers")
    
    def process_query(self):
        """Process user query and display response"""
        query = self.user_input.text().strip()
        if not query:
            return
            
        self.user_input.clear()
        self.display_message(f"You: {query}", "user")
        
        try:
            response = self.agent.query(query)
            self.display_message(f"Assistant: {response.get('result', '')}", "assistant")
            self.update_source_list(response.get('source_documents', []))
        except Exception as e:
            self.display_message(f"Error: {str(e)}", "error")
    
    def display_message(self, message, sender):
        """Display message in conversation window with styling"""
        if sender == "user":
            self.conversation_display.append(f'<p style="color:#2c3e50; font-weight:bold;">{message}</p>')
        elif sender == "assistant":
            self.conversation_display.append(f'<p style="color:#2980b9;">{message}</p>')
        else:  # error
            self.conversation_display.append(f'<p style="color:#e74c3c;">{message}</p>')
    
    def update_source_list(self, documents):
        """Update source list with relevant documents"""
        self.source_list.clear()
        for doc in documents:
            title = doc.metadata.get('title', 'Untitled Document')
            source = doc.metadata.get('source', 'Unknown Source')
            item_text = f"{title} [{source}]"
            self.source_list.addItem(item_text)
    
    def open_source(self, item):
        """Open selected source document (placeholder for actual implementation)"""
        self.status_bar.showMessage(f"Opening source: {item.text()}...", 3000)
    
    def clear_conversation(self):
        """Clear conversation history"""
        self.conversation_display.clear()
        self.source_list.clear()
        self.status_bar.showMessage("Conversation cleared", 2000)

if __name__ == "__main__":
    # Initialize agent (assuming vector store exists)
    base_dir = os.environ.get('KNOWLEDGE_BASE', os.getcwd())
    index_path = os.path.join(base_dir, "quant_finance_index")
    
    try:
        # Import required modules
        from langchain.embeddings import HuggingFaceEmbeddings
        from vector_db import load_vector_store
        
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
        vector_store = load_vector_store(index_path, embeddings)
        agent = QuantFinanceAgent(vector_store)
    except Exception as e:
        print(f"Failed to initialize agent: {e}")
        sys.exit(1)

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Set dark palette
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
    app.setPalette(dark_palette)

    window = FinanceAIAssistant(agent)
    window.show()
    sys.exit(app.exec_())