#!/usr/bin/env python3
"""
Test script for Enhanced Quantitative Finance Agent
"""

import sys
import os
import time
from typing import Dict, Any

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_agent_initialization():
    """Test agent initialization with different configurations."""
    print("Testing Agent Initialization...")
    
    try:
        from quant_agent import EnhancedQuantFinanceAgent
        
        # Create mock vector store
        class MockVectorStore:
            def as_retriever(self, **kwargs):
                return MockRetriever()
        
        class MockRetriever:
            def get_relevant_documents(self, query):
                from langchain.schema import Document
                return [
                    Document(
                        page_content=f"Mock document content for query: {query}",
                        metadata={
                            "title": "Mock Financial Paper",
                            "authors": ["Dr. Mock", "Prof. Test"],
                            "source": "mock_arxiv.pdf"
                        }
                    )
                ]
        
        # Test default configuration
        mock_store = MockVectorStore()
        agent = EnhancedQuantFinanceAgent(mock_store)
        print("✓ Default configuration initialization successful")
        
        # Test custom configuration
        custom_config = {
            "temperature": 0.3,
            "max_length": 1024,
            "top_k": 10,
            "enable_memory": False
        }
        agent_custom = EnhancedQuantFinanceAgent(mock_store, custom_config)
        print("✓ Custom configuration initialization successful")
        
        return True, agent
        
    except Exception as e:
        print(f"✗ Initialization failed: {e}")
        return False, None

def test_query_processing(agent):
    """Test query processing with various financial topics."""
    print("\nTesting Query Processing...")
    
    test_queries = [
        "Explain the Black-Scholes option pricing model",
        "What is Value at Risk (VaR) and how is it calculated?",
        "Describe portfolio optimization using Markowitz theory",
        "How does stochastic volatility affect option pricing?",
        "Explain the concept of Greeks in options trading"
    ]
    
    results = []
    
    for i, query in enumerate(test_queries, 1):
        try:
            print(f"  Testing query {i}: {query[:50]}...")
            start_time = time.time()
            
            result = agent.query(query)
            response_time = time.time() - start_time
            
            # Validate response structure
            assert "result" in result
            assert "source_documents" in result
            assert "metadata" in result
            
            print(f"    ✓ Response received in {response_time:.2f}s")
            print(f"    ✓ Response length: {len(result['result'])} chars")
            print(f"    ✓ Sources found: {len(result['source_documents'])}")
            
            if result["metadata"]:
                concepts = result["metadata"].get("financial_concepts", [])
                if concepts:
                    print(f"    ✓ Financial concepts detected: {', '.join(concepts[:3])}")
            
            results.append(result)
            
        except Exception as e:
            print(f"    ✗ Query failed: {e}")
            return False, []
    
    print("✓ All queries processed successfully")
    return True, results

def test_specialized_prompts(agent):
    """Test specialized prompt selection."""
    print("\nTesting Specialized Prompts...")
    
    prompt_tests = [
        ("Calculate VaR for a portfolio", "risk"),
        ("Price a European call option", "pricing"), 
        ("Design a momentum trading strategy", "strategy"),
        ("Explain stochastic calculus", "general")
    ]
    
    for query, expected_type in prompt_tests:
        try:
            selected_prompt = agent._select_prompt_template(query)
            print(f"  ✓ Query: '{query[:30]}...' -> {type(selected_prompt).__name__}")
        except Exception as e:
            print(f"  ✗ Prompt selection failed for '{query}': {e}")
            return False
    
    return True

def test_preprocessing_postprocessing(agent):
    """Test query preprocessing and response postprocessing."""
    print("\nTesting Preprocessing and Postprocessing...")
    
    try:
        # Test preprocessing
        raw_query = "option pricing"
        processed_query = agent._preprocess_query(raw_query)
        print(f"  ✓ Preprocessing: '{raw_query}' -> '{processed_query[:50]}...'")
        
        # Test postprocessing
        from langchain.schema import Document
        mock_response = "The Black-Scholes model is a mathematical model for pricing options..."
        mock_sources = [
            Document(
                page_content="Black-Scholes content",
                metadata={"title": "Options Pricing Theory", "authors": ["Black", "Scholes"]}
            )
        ]
        
        enhanced_result = agent._postprocess_response(mock_response, mock_sources)
        
        assert "metadata" in enhanced_result
        assert "financial_concepts" in enhanced_result["metadata"]
        assert "quality_metrics" in enhanced_result["metadata"]
        
        print("  ✓ Postprocessing adds metadata successfully")
        print(f"  ✓ Concepts detected: {enhanced_result['metadata']['financial_concepts']}")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Preprocessing/Postprocessing failed: {e}")
        return False

def test_performance_monitoring(agent):
    """Test performance monitoring and analytics."""
    print("\nTesting Performance Monitoring...")
    
    try:
        # Run a few queries to generate data
        for i in range(3):
            agent.query(f"Test query {i+1} about portfolio optimization")
        
        # Test conversation summary
        summary = agent.get_conversation_summary()
        
        assert "total_queries" in summary
        assert "average_response_time" in summary
        assert summary["total_queries"] >= 3
        
        print(f"  ✓ Total queries tracked: {summary['total_queries']}")
        print(f"  ✓ Average response time: {summary['average_response_time']:.2f}s")
        print(f"  ✓ Performance rating: {summary['performance']}")
        
        # Test health check
        health = agent.health_check()
        print(f"  ✓ Health check completed: {health['overall_healthy']}")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Performance monitoring failed: {e}")
        return False

def test_configuration_management(agent):
    """Test dynamic configuration updates."""
    print("\nTesting Configuration Management...")
    
    try:
        # Test configuration update
        original_temp = agent.config["temperature"]
        agent.update_config({"temperature": 0.5, "top_k": 8})
        
        assert agent.config["temperature"] == 0.5
        assert agent.config["top_k"] == 8
        
        print("  ✓ Configuration updated successfully")
        
        # Test available models
        models = agent.get_available_models()
        print(f"  ✓ Available models: {len(models)} found")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Configuration management failed: {e}")
        return False

def test_error_handling(agent):
    """Test error handling and fallback mechanisms."""
    print("\nTesting Error Handling...")
    
    try:
        # Test with invalid input
        result = agent.query("")
        assert "error" in result["metadata"] or len(result["result"]) > 0
        print("  ✓ Empty query handled gracefully")
        
        # Test memory operations
        agent.clear_memory()
        print("  ✓ Memory cleared successfully")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error handling test failed: {e}")
        return False

def performance_benchmark(agent):
    """Run performance benchmark."""
    print("\nRunning Performance Benchmark...")
    
    benchmark_queries = [
        "Explain the Heston stochastic volatility model",
        "Calculate portfolio VaR using Monte Carlo simulation",
        "Describe the Greeks in options trading",
        "What is the Capital Asset Pricing Model (CAPM)?",
        "How does credit risk affect bond pricing?"
    ]
    
    total_time = 0
    successful_queries = 0
    
    for query in benchmark_queries:
        try:
            start_time = time.time()
            result = agent.query(query)
            response_time = time.time() - start_time
            
            total_time += response_time
            successful_queries += 1
            
        except Exception as e:
            print(f"  ✗ Benchmark query failed: {e}")
    
    if successful_queries > 0:
        avg_time = total_time / successful_queries
        print(f"  ✓ Benchmark completed: {successful_queries}/{len(benchmark_queries)} queries successful")
        print(f"  ✓ Average response time: {avg_time:.2f}s")
        
        # Performance rating
        if avg_time < 3:
            rating = "Excellent"
        elif avg_time < 5:
            rating = "Good"
        elif avg_time < 10:
            rating = "Acceptable"
        else:
            rating = "Needs Improvement"
        
        print(f"  ✓ Performance rating: {rating}")
        return True
    
    return False

def main():
    """Run comprehensive test suite."""
    print("Enhanced Quantitative Finance Agent - Test Suite")
    print("=" * 60)
    
    # Initialize tests
    init_success, agent = test_agent_initialization()
    if not init_success:
        print("✗ Failed to initialize agent. Stopping tests.")
        return
    
    # Run test suite
    tests = [
        ("Query Processing", lambda: test_query_processing(agent)),
        ("Specialized Prompts", lambda: test_specialized_prompts(agent)),
        ("Preprocessing/Postprocessing", lambda: test_preprocessing_postprocessing(agent)),
        ("Performance Monitoring", lambda: test_performance_monitoring(agent)),
        ("Configuration Management", lambda: test_configuration_management(agent)),
        ("Error Handling", lambda: test_error_handling(agent)),
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            if success:
                passed_tests += 1
                print(f"✓ {test_name} - PASSED")
            else:
                print(f"✗ {test_name} - FAILED")
        except Exception as e:
            print(f"✗ {test_name} - ERROR: {e}")
    
    # Run performance benchmark
    print("\n" + "=" * 60)
    benchmark_success = performance_benchmark(agent)
    
    # Final summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print(f"Passed: {passed_tests}/{total_tests} tests")
    print(f"Benchmark: {'PASSED' if benchmark_success else 'FAILED'}")
    
    if passed_tests == total_tests and benchmark_success:
        print("✅ ALL TESTS PASSED - Agent is ready for production!")
    else:
        print("⚠️  Some tests failed - Review the output above")

if __name__ == "__main__":
    main()
