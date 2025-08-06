#!/usr/bin/env python3
"""
Test script for SimpleQuantFinanceAgent initialization
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_agent():
    print("🧪 Testing SimpleQuantFinanceAgent initialization...")
    
    try:
        # Import required modules
        from vector_db import load_vector_store
        from simple_agent import SimpleQuantFinanceAgent
        
        print("✅ Modules imported successfully")
        
        # Initialize vector store
        print("🗃️ Loading vector store...")
        vector_store = load_vector_store()
        print("✅ Vector store loaded")
        
        # Initialize agent
        print("🤖 Initializing agent...")
        agent = SimpleQuantFinanceAgent(vector_store)
        print("✅ Agent initialized successfully")
        
        # Test a simple query
        print("\n🎯 Testing query: 'Explica Value at Risk (VaR)'")
        response = agent.query("Explica Value at Risk (VaR)")
        
        print("\n📝 Response:")
        print("="*50)
        print(response)
        print("="*50)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_agent()
    if success:
        print("\n✅ Test completed successfully!")
    else:
        print("\n❌ Test failed!")
        sys.exit(1)
