#!/usr/bin/env python3
"""
Usage Examples for Enhanced Quantitative Finance Agent
Demonstrates advanced capabilities and best practices
"""

import os
import sys
import json
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

def create_mock_vector_store():
    """Create a mock vector store for demonstration."""
    from langchain.schema import Document
    
    class MockVectorStore:
        def __init__(self):
            # Simulate a knowledge base with financial documents
            self.documents = [
                Document(
                    page_content="The Black-Scholes model is a mathematical model for pricing European-style options...",
                    metadata={
                        "title": "Option Pricing Theory",
                        "authors": ["Fischer Black", "Myron Scholes"],
                        "source": "black_scholes_1973.pdf",
                        "type": "academic_paper"
                    }
                ),
                Document(
                    page_content="Value at Risk (VaR) is a statistical measure of the risk of loss for investments...",
                    metadata={
                        "title": "Risk Management in Finance",
                        "authors": ["Philippe Jorion"],
                        "source": "risk_management_2007.pdf",
                        "type": "textbook"
                    }
                ),
                Document(
                    page_content="Portfolio optimization seeks to maximize expected return for a given level of risk...",
                    metadata={
                        "title": "Modern Portfolio Theory",
                        "authors": ["Harry Markowitz"],
                        "source": "markowitz_1952.pdf",
                        "type": "academic_paper"
                    }
                )
            ]
        
        def as_retriever(self, **kwargs):
            return MockRetriever(self.documents)
    
    class MockRetriever:
        def __init__(self, documents):
            self.documents = documents
        
        def get_relevant_documents(self, query):
            # Simple keyword matching for demonstration
            query_lower = query.lower()
            relevant = []
            
            for doc in self.documents:
                if any(word in doc.page_content.lower() for word in query_lower.split()):
                    relevant.append(doc)
            
            return relevant[:5]  # Return top 5 matches
    
    return MockVectorStore()

def example_basic_usage():
    """Demonstrate basic agent usage."""
    print("=== Basic Usage Example ===")
    
    try:
        from quant_agent import EnhancedQuantFinanceAgent
        
        # Initialize agent with mock vector store
        vector_store = create_mock_vector_store()
        agent = EnhancedQuantFinanceAgent(vector_store)
        
        # Simple query
        query = "Explain the Black-Scholes option pricing model"
        print(f"Query: {query}")
        
        result = agent.query(query)
        
        print(f"Response: {result['result'][:200]}...")
        print(f"Sources: {len(result['source_documents'])} documents")
        print(f"Response Time: {result['metadata']['response_time']:.2f}s")
        
        return agent
        
    except Exception as e:
        print(f"Error in basic usage: {e}")
        return None

def example_advanced_configuration():
    """Demonstrate advanced configuration options."""
    print("\n=== Advanced Configuration Example ===")
    
    try:
        from quant_agent import EnhancedQuantFinanceAgent
        
        # Custom configuration for high-performance trading applications
        trading_config = {
            "model_name": "google/flan-t5-large",  # Faster model
            "temperature": 0.05,  # More deterministic responses
            "max_length": 256,    # Shorter responses for quick analysis
            "top_k": 3,           # Fewer sources for speed
            "enable_memory": True,
            "enable_preprocessing": True,
            "enable_postprocessing": True,
            "response_timeout": 15
        }
        
        vector_store = create_mock_vector_store()
        agent = EnhancedQuantFinanceAgent(vector_store, trading_config)
        
        print("Configuration applied:")
        for key, value in trading_config.items():
            print(f"  {key}: {value}")
        
        # Test with trading-specific query
        query = "What's the optimal portfolio allocation for a risk-averse investor?"
        result = agent.query(query)
        
        print(f"\nTrading Query Result:")
        print(f"Response: {result['result'][:150]}...")
        print(f"Financial Concepts: {result['metadata']['financial_concepts']}")
        
        return agent
        
    except Exception as e:
        print(f"Error in advanced configuration: {e}")
        return None

def example_specialized_queries():
    """Demonstrate specialized query types."""
    print("\n=== Specialized Queries Example ===")
    
    try:
        from quant_agent import EnhancedQuantFinanceAgent
        
        vector_store = create_mock_vector_store()
        agent = EnhancedQuantFinanceAgent(vector_store)
        
        specialized_queries = [
            {
                "category": "Risk Management",
                "query": "Calculate 95% VaR for a $1M portfolio with 20% volatility",
                "expected_concepts": ["VaR", "risk management", "volatility"]
            },
            {
                "category": "Options Pricing",
                "query": "Price a European call option with S=100, K=105, T=0.25, r=0.05, σ=0.2",
                "expected_concepts": ["Black-Scholes", "option pricing", "Greeks"]
            },
            {
                "category": "Portfolio Theory",
                "query": "Optimize a 3-asset portfolio using mean-variance optimization",
                "expected_concepts": ["Markowitz", "portfolio optimization", "efficient frontier"]
            }
        ]
        
        for query_info in specialized_queries:
            print(f"\n{query_info['category']} Query:")
            print(f"Question: {query_info['query']}")
            
            result = agent.query(query_info['query'])
            
            # Check if expected concepts are detected
            detected_concepts = result['metadata']['financial_concepts']
            expected_concepts = query_info['expected_concepts']
            
            matching_concepts = set(detected_concepts) & set(expected_concepts)
            
            print(f"Response: {result['result'][:100]}...")
            print(f"Expected concepts: {expected_concepts}")
            print(f"Detected concepts: {detected_concepts}")
            print(f"Matching concepts: {list(matching_concepts)}")
            print(f"Quality score: {result['metadata']['quality_metrics']}")
        
    except Exception as e:
        print(f"Error in specialized queries: {e}")

def example_conversation_memory():
    """Demonstrate conversation memory capabilities."""
    print("\n=== Conversation Memory Example ===")
    
    try:
        from quant_agent import EnhancedQuantFinanceAgent
        
        # Enable memory for conversational context
        memory_config = {
            "enable_memory": True,
            "memory_max_tokens": 1000
        }
        
        vector_store = create_mock_vector_store()
        agent = EnhancedQuantFinanceAgent(vector_store, memory_config)
        
        # Multi-turn conversation
        conversation = [
            "What is the Black-Scholes model?",
            "How do you calculate the Greeks for this model?",
            "Can you give me a practical example of delta hedging?",
            "What are the limitations of this approach?"
        ]
        
        print("Multi-turn conversation:")
        for i, query in enumerate(conversation, 1):
            print(f"\nTurn {i}: {query}")
            result = agent.query(query, use_memory=True)
            print(f"Response: {result['result'][:120]}...")
        
        # Show conversation summary
        summary = agent.get_conversation_summary()
        print(f"\nConversation Summary:")
        print(f"Total queries: {summary['total_queries']}")
        print(f"Recent topics: {summary['recent_topics']}")
        print(f"Performance: {summary['performance']}")
        
    except Exception as e:
        print(f"Error in conversation memory: {e}")

def example_performance_monitoring():
    """Demonstrate performance monitoring and analytics."""
    print("\n=== Performance Monitoring Example ===")
    
    try:
        from quant_agent import EnhancedQuantFinanceAgent
        
        vector_store = create_mock_vector_store()
        agent = EnhancedQuantFinanceAgent(vector_store)
        
        # Run several queries to generate performance data
        test_queries = [
            "Explain portfolio diversification",
            "What is credit risk?",
            "How does correlation affect portfolio risk?",
            "Describe the efficient market hypothesis"
        ]
        
        print("Running performance benchmark...")
        for query in test_queries:
            result = agent.query(query)
            print(f"  ✓ Processed: {query[:30]}... ({result['metadata']['response_time']:.2f}s)")
        
        # Health check
        health = agent.health_check()
        print(f"\nHealth Check:")
        for component, status in health['components'].items():
            print(f"  {component}: {'✓' if status else '✗'}")
        
        # Performance summary
        summary = agent.get_conversation_summary()
        print(f"\nPerformance Summary:")
        print(f"  Average response time: {summary['average_response_time']:.2f}s")
        print(f"  Total queries processed: {summary['total_queries']}")
        print(f"  Overall performance: {summary['performance']}")
        
    except Exception as e:
        print(f"Error in performance monitoring: {e}")

def example_error_handling():
    """Demonstrate error handling and fallback mechanisms."""
    print("\n=== Error Handling Example ===")
    
    try:
        from quant_agent import EnhancedQuantFinanceAgent
        
        vector_store = create_mock_vector_store()
        agent = EnhancedQuantFinanceAgent(vector_store)
        
        # Test various error conditions
        error_tests = [
            ("Empty query", ""),
            ("Very long query", "x" * 10000),
            ("Non-financial query", "What's the weather like today?"),
            ("Special characters", "∑∫∂∆∇∞±≈≠√∝∈∪∩⊂⊃∀∃∄∅"),
        ]
        
        print("Testing error handling:")
        for test_name, query in error_tests:
            try:
                result = agent.query(query)
                error_status = result['metadata'].get('error', False)
                print(f"  {test_name}: {'✓ Handled gracefully' if not error_status else '⚠ Error detected but handled'}")
            except Exception as e:
                print(f"  {test_name}: ✗ Unhandled error: {e}")
        
        # Test configuration updates
        print("\nTesting dynamic configuration:")
        try:
            agent.update_config({"temperature": 0.7, "top_k": 10})
            print("  ✓ Configuration updated successfully")
        except Exception as e:
            print(f"  ✗ Configuration update failed: {e}")
        
    except Exception as e:
        print(f"Error in error handling demo: {e}")

def example_integration_patterns():
    """Demonstrate integration patterns for different use cases."""
    print("\n=== Integration Patterns Example ===")
    
    try:
        from quant_agent import EnhancedQuantFinanceAgent
        
        vector_store = create_mock_vector_store()
        
        # Pattern 1: Research Assistant
        print("1. Research Assistant Pattern:")
        research_config = {
            "temperature": 0.1,
            "max_length": 1024,
            "top_k": 10,
            "enable_memory": True
        }
        research_agent = EnhancedQuantFinanceAgent(vector_store, research_config)
        
        # Pattern 2: Trading Bot
        print("2. Trading Bot Pattern:")
        trading_config = {
            "temperature": 0.05,
            "max_length": 256,
            "top_k": 3,
            "enable_memory": False,
            "response_timeout": 5
        }
        trading_agent = EnhancedQuantFinanceAgent(vector_store, trading_config)
        
        # Pattern 3: Educational Assistant
        print("3. Educational Assistant Pattern:")
        education_config = {
            "temperature": 0.3,
            "max_length": 800,
            "top_k": 7,
            "enable_memory": True,
            "enable_preprocessing": True
        }
        education_agent = EnhancedQuantFinanceAgent(vector_store, education_config)
        
        print("All integration patterns initialized successfully!")
        
        # Example usage for each pattern
        test_query = "Explain volatility clustering in financial markets"
        
        for name, agent in [("Research", research_agent), ("Trading", trading_agent), ("Education", education_agent)]:
            result = agent.query(test_query)
            print(f"  {name} Agent Response Length: {len(result['result'])} chars")
        
    except Exception as e:
        print(f"Error in integration patterns: {e}")

def save_results_to_file(results):
    """Save example results to a JSON file."""
    try:
        output_file = "agent_examples_output.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\n📄 Results saved to {output_file}")
    except Exception as e:
        print(f"Error saving results: {e}")

def main():
    """Run all usage examples."""
    print("Enhanced Quantitative Finance Agent - Usage Examples")
    print("=" * 70)
    
    results = {}
    
    try:
        # Run all examples
        examples = [
            ("Basic Usage", example_basic_usage),
            ("Advanced Configuration", example_advanced_configuration),
            ("Specialized Queries", example_specialized_queries),
            ("Conversation Memory", example_conversation_memory),
            ("Performance Monitoring", example_performance_monitoring),
            ("Error Handling", example_error_handling),
            ("Integration Patterns", example_integration_patterns)
        ]
        
        for example_name, example_func in examples:
            print(f"\n{'='*20} {example_name} {'='*20}")
            try:
                result = example_func()
                results[example_name] = "Success"
                print(f"✅ {example_name} completed successfully")
            except Exception as e:
                results[example_name] = f"Error: {str(e)}"
                print(f"❌ {example_name} failed: {e}")
        
        # Summary
        print("\n" + "="*70)
        print("EXAMPLES SUMMARY")
        successful = sum(1 for v in results.values() if v == "Success")
        total = len(results)
        print(f"Completed: {successful}/{total} examples")
        
        if successful == total:
            print("🎉 All examples completed successfully!")
            print("\nThe Enhanced Quantitative Finance Agent is ready for:")
            print("  • Research and academic applications")
            print("  • Trading and risk management systems") 
            print("  • Educational and training platforms")
            print("  • Financial advisory services")
        else:
            print("⚠️ Some examples encountered issues")
            for name, status in results.items():
                if status != "Success":
                    print(f"  - {name}: {status}")
        
        # Save results
        save_results_to_file(results)
        
    except Exception as e:
        print(f"Error running examples: {e}")

if __name__ == "__main__":
    main()
