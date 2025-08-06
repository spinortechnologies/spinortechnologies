#!/usr/bin/env python3
"""
Test script for the improved GUI
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test if all required modules can be imported"""
    try:
        # Test PyQt5 imports
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QFont
        print("✓ PyQt5 imports successful")
        
        # Test custom module imports
        from quant_agent import QuantFinanceAgent
        print("✓ QuantFinanceAgent import successful")
        
        from vector_db import load_vector_store
        print("✓ vector_db import successful")
        
        # Test GUI import
        from gui import FinanceAIAssistant, QueryWorker, SourceDialog
        print("✓ GUI components import successful")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_mock_gui():
    """Test GUI with mock agent"""
    try:
        from PyQt5.QtWidgets import QApplication
        from gui import FinanceAIAssistant
        
        # Create mock agent
        class MockAgent:
            def query(self, query_text):
                return {
                    'result': f"Mock response for: {query_text}",
                    'source_documents': []
                }
        
        # Test GUI creation
        app = QApplication(sys.argv)
        agent = MockAgent()
        window = FinanceAIAssistant(agent)
        
        # Test basic functionality
        window.set_input_text("Test query")
        window.clear_conversation()
        
        print("✓ GUI creation and basic functionality test passed")
        
        # Clean up
        app.quit()
        return True
        
    except Exception as e:
        print(f"✗ GUI test error: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing improved GUI components...")
    print("=" * 50)
    
    # Test imports
    imports_ok = test_imports()
    
    if imports_ok:
        # Test GUI functionality
        gui_ok = test_mock_gui()
        
        if gui_ok:
            print("\n" + "=" * 50)
            print("✓ All tests passed! GUI improvements are working.")
        else:
            print("\n" + "=" * 50)
            print("✗ GUI functionality tests failed.")
    else:
        print("\n" + "=" * 50)
        print("✗ Import tests failed. Check dependencies.")
        print("Run: pip install -r requirements.txt")

if __name__ == "__main__":
    main()
