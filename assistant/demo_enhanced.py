#!/usr/bin/env python3
"""
Enhanced Paper Integration Demo
Author: SPINOR Technologies
Date: August 6, 2025

Demonstration of the enhanced paper integration and multilingual capabilities.
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_papers import EnhancedPaperIntegrator
from enhanced_agent import EnhancedMultilingualAgent
from vector_db import load_vector_store

async def demo_enhanced_system():
    """Demonstrate the enhanced system capabilities."""
    
    print("🚀 SPINOR Enhanced AI System Demo")
    print("=" * 50)
    
    # Initialize paper integrator
    print("\n1. 📚 Initializing Enhanced Paper Integrator...")
    integrator = EnhancedPaperIntegrator()
    
    # Fetch and process papers
    print("\n2. 🔍 Fetching and processing recent papers...")
    result = await integrator.fetch_and_process_papers(days_back=2, max_papers=10)
    
    print(f"   ✅ Success: {result['success']}")
    print(f"   📄 Papers processed: {result['papers_processed']}")
    print(f"   🧠 Concepts extracted: {result.get('concepts_extracted', 0)}")
    print(f"   📁 File: {result.get('file_path', 'N/A')}")
    
    # Initialize multilingual agent
    print("\n3. 🤖 Initializing Enhanced Multilingual Agent...")
    try:
        vector_store = load_vector_store()
        agent = EnhancedMultilingualAgent(vector_store)
        print("   ✅ Agent initialized successfully")
    except Exception as e:
        print(f"   ❌ Agent initialization failed: {e}")
        return
    
    # Test multilingual capabilities
    print("\n4. 🌐 Testing Multilingual Capabilities...")
    
    # English queries
    english_queries = [
        "What is the Black-Scholes model?",
        "Explain Value at Risk",
        "How does portfolio optimization work?"
    ]
    
    # Spanish queries
    spanish_queries = [
        "¿Qué es el modelo Black-Scholes?",
        "Explica el Valor en Riesgo",
        "¿Cómo funciona la optimización de portafolios?"
    ]
    
    print("\n   🇺🇸 English Queries:")
    for i, query in enumerate(english_queries, 1):
        print(f"   {i}. Testing: '{query}'")
        response = agent.query(query)
        lang = response['metadata'].get('language', 'unknown')
        print(f"      📊 Detected language: {lang}")
        print(f"      🎯 Topic: {response['metadata'].get('topic', 'general')}")
        print(f"      ⏱️ Response time: {response['metadata'].get('response_time', 0):.2f}s")
        print(f"      📚 Papers integrated: {response['metadata'].get('papers_integrated', 0)}")
        print()
    
    print("   🇪🇸 Spanish Queries:")
    for i, query in enumerate(spanish_queries, 1):
        print(f"   {i}. Testing: '{query}'")
        response = agent.query(query)
        lang = response['metadata'].get('language', 'unknown')
        print(f"      📊 Detected language: {lang}")
        print(f"      🎯 Topic: {response['metadata'].get('topic', 'general')}")
        print(f"      ⏱️ Response time: {response['metadata'].get('response_time', 0):.2f}s")
        print(f"      📚 Papers integrated: {response['metadata'].get('papers_integrated', 0)}")
        print()
    
    # System health check
    print("5. 🔧 System Health Check...")
    health = agent.health_check()
    print(f"   Overall health: {'✅' if health['overall_healthy'] else '❌'}")
    print(f"   Vector store: {'✅' if health['vector_store'] else '❌'}")
    print(f"   Papers available: {'✅' if health['papers_available'] else '❌'}")
    print(f"   Papers count: {health.get('papers_count', 0)}")
    print(f"   Languages: {', '.join(health.get('languages_supported', []))}")
    print(f"   Query count: {health.get('query_count', 0)}")
    
    print("\n🎉 Demo completed successfully!")
    print("💡 The enhanced system includes:")
    print("   • Automatic language detection (Spanish/English)")
    print("   • Real-time paper integration from ArXiv")
    print("   • Enhanced knowledge extraction")
    print("   • Multilingual response generation")
    print("   • Dynamic concept learning")
    print("   • Web-based interface with real-time updates")

if __name__ == "__main__":
    asyncio.run(demo_enhanced_system())
