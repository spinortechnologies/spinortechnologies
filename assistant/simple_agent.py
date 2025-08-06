"""
Simple Quantitative Finance AI Agent - Demo Version
Author: SPINOR Technologies
Date: August 6, 2025
Version: 2.0
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleQuantFinanceAgent:
    """
    Simplified Quantitative Finance AI Agent for demonstration.
    
    This version works without external API tokens and provides
    intelligent responses based on the knowledge base.
    """
    
    def __init__(self, vector_store):
        """Initialize the simple agent."""
        self.vector_store = vector_store
        self.conversation_history = []
        self.query_count = 0
        
        # Financial concepts mapping for intelligent responses
        self.financial_concepts = {
            'black-scholes': {
                'keywords': ['black', 'scholes', 'option', 'pricing', 'call', 'put'],
                'response_template': self._black_scholes_response
            },
            'var': {
                'keywords': ['var', 'value at risk', 'risk', 'loss', 'confidence'],
                'response_template': self._var_response
            },
            'portfolio': {
                'keywords': ['portfolio', 'markowitz', 'optimization', 'efficient', 'frontier'],
                'response_template': self._portfolio_response
            },
            'capm': {
                'keywords': ['capm', 'capital asset', 'beta', 'alpha', 'market'],
                'response_template': self._capm_response
            },
            'algorithmic': {
                'keywords': ['algorithmic', 'trading', 'strategy', 'algo', 'automated'],
                'response_template': self._algo_trading_response
            }
        }
        
        logger.info("Simple QuantFinance Agent initialized successfully")
    
    def query(self, question: str) -> Dict[str, Any]:
        """
        Process a financial query and return an intelligent response.
        
        Args:
            question: The financial question to answer
            
        Returns:
            Dictionary with response and metadata
        """
        start_time = datetime.now()
        self.query_count += 1
        
        try:
            # Get relevant documents from vector store
            docs = self.vector_store.similarity_search(question, k=3)
            
            # Determine the main topic
            main_topic = self._identify_topic(question)
            
            # Generate response based on topic and documents
            if main_topic and main_topic in self.financial_concepts:
                response = self.financial_concepts[main_topic]['response_template'](question, docs)
            else:
                response = self._general_financial_response(question, docs)
            
            # Calculate response time
            response_time = (datetime.now() - start_time).total_seconds()
            
            # Store in conversation history
            self.conversation_history.append({
                'question': question,
                'response': response,
                'timestamp': start_time,
                'response_time': response_time
            })
            
            return {
                'result': response,
                'source_documents': docs,
                'metadata': {
                    'topic': main_topic,
                    'response_time': response_time,
                    'source_count': len(docs),
                    'query_number': self.query_count
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                'result': f"I apologize, but I encountered an error processing your question. Error: {str(e)}",
                'source_documents': [],
                'metadata': {'error': True, 'error_message': str(e)}
            }
    
    def _identify_topic(self, question: str) -> Optional[str]:
        """Identify the main financial topic of the question."""
        question_lower = question.lower()
        
        for topic, data in self.financial_concepts.items():
            if any(keyword in question_lower for keyword in data['keywords']):
                return topic
        
        return None
    
    def _black_scholes_response(self, question: str, docs: List) -> str:
        """Generate response for Black-Scholes related questions."""
        base_info = """
The Black-Scholes model is a fundamental mathematical model in quantitative finance for pricing European options. 

**Key Formula:**
For a European call option: C = S₀ × N(d₁) - K × e^(-rT) × N(d₂)

Where:
- C = Call option price
- S₀ = Current stock price
- K = Strike price  
- r = Risk-free interest rate
- T = Time to expiration
- N = Cumulative standard normal distribution

**Key Assumptions:**
1. Constant volatility
2. Constant risk-free rate
3. Log-normal distribution of stock prices
4. No dividends during option life
5. European exercise (only at expiration)

**Applications:**
- Option pricing and valuation
- Risk management and hedging strategies
- Portfolio optimization
- Derivatives trading

The model was developed by Fischer Black, Myron Scholes, and Robert Merton, with Scholes and Merton winning the Nobel Prize in Economics in 1997.
"""
        
        # Add context from retrieved documents
        if docs:
            doc_context = "\n\n**Additional Context from Knowledge Base:**\n"
            for i, doc in enumerate(docs[:2]):
                doc_context += f"\n{i+1}. {doc.page_content[:200]}...\n"
            base_info += doc_context
        
        return base_info
    
    def _var_response(self, question: str, docs: List) -> str:
        """Generate response for Value at Risk related questions."""
        base_info = """
Value at Risk (VaR) is a statistical measure used to quantify the potential loss in a portfolio over a specific time period at a given confidence level.

**Definition:**
VaR answers the question: "What is the maximum loss we can expect with X% confidence over Y time period?"

**Example:**
A 1-day 95% VaR of $1 million means: "We are 95% confident that our portfolio will not lose more than $1 million in one day."

**Three Main Calculation Methods:**

1. **Historical Simulation Method:**
   - Uses historical price data
   - No distributional assumptions
   - Simple but limited by historical data

2. **Parametric Method (Variance-Covariance):**
   - Assumes normal distribution of returns
   - Uses portfolio volatility and correlation
   - Fast but relies on normality assumption

3. **Monte Carlo Simulation:**
   - Uses random sampling
   - Can handle complex portfolios
   - Computationally intensive but flexible

**Limitations:**
- Doesn't capture tail risk beyond confidence level
- Assumes normal market conditions
- Historical data may not predict future risks

**Complementary Measures:**
- Expected Shortfall (ES): Average loss beyond VaR threshold
- Stress Testing: Scenario-based risk assessment
- Maximum Drawdown: Largest peak-to-trough loss
"""
        
        if docs:
            doc_context = "\n\n**Additional Context:**\n"
            for doc in docs[:1]:
                doc_context += f"\n{doc.page_content[:300]}...\n"
            base_info += doc_context
        
        return base_info
    
    def _portfolio_response(self, question: str, docs: List) -> str:
        """Generate response for portfolio theory related questions."""
        base_info = """
Modern Portfolio Theory (MPT), developed by Harry Markowitz, provides a mathematical framework for constructing optimal investment portfolios.

**Core Principle:**
Maximize expected return for a given level of risk, or minimize risk for a given expected return.

**Key Concepts:**

1. **Efficient Frontier:**
   - Set of optimal portfolios
   - Best risk-return combinations
   - Curved line in risk-return space

2. **Diversification:**
   - Reduces portfolio risk without sacrificing expected return
   - "Don't put all eggs in one basket"
   - Correlation matters more than individual asset risk

3. **Risk Measures:**
   - Standard deviation as risk measure
   - Covariance and correlation between assets
   - Systematic vs. unsystematic risk

**Key Formulas:**

**Portfolio Expected Return:**
E(Rp) = Σ wi × E(Ri)

**Portfolio Variance:**
σp² = Σ Σ wi × wj × σij

Where:
- wi = weight of asset i
- E(Ri) = expected return of asset i
- σij = covariance between assets i and j

**Capital Asset Pricing Model (CAPM):**
E(R) = Rf + β × (E(Rm) - Rf)

**Sharpe Ratio:**
Sharpe = (Rp - Rf) / σp

**Applications:**
- Asset allocation decisions
- Risk budgeting
- Performance measurement
- Fund management strategies
"""
        
        if docs:
            doc_context = "\n\n**Context from Knowledge Base:**\n"
            for doc in docs[:1]:
                doc_context += f"{doc.page_content[:250]}...\n"
            base_info += doc_context
        
        return base_info
    
    def _capm_response(self, question: str, docs: List) -> str:
        """Generate response for CAPM related questions."""
        return """
The Capital Asset Pricing Model (CAPM) is a financial model that describes the relationship between systematic risk and expected return for assets.

**CAPM Formula:**
E(R) = Rf + β × (E(Rm) - Rf)

Where:
- E(R) = Expected return of the asset
- Rf = Risk-free rate
- β (Beta) = Systematic risk measure
- E(Rm) = Expected market return
- (E(Rm) - Rf) = Market risk premium

**Beta Interpretation:**
- β = 1: Asset moves with the market
- β > 1: Asset is more volatile than market
- β < 1: Asset is less volatile than market
- β < 0: Asset moves opposite to market

**Alpha:**
α = Actual Return - CAPM Expected Return

Positive alpha indicates outperformance relative to risk taken.

**Applications:**
- Security valuation
- Portfolio performance evaluation
- Cost of equity calculation
- Investment decision making

**Assumptions:**
1. Investors are rational and risk-averse
2. Perfect information available to all
3. No transaction costs
4. Investors can borrow/lend at risk-free rate
5. Single-period investment horizon
"""
    
    def _algo_trading_response(self, question: str, docs: List) -> str:
        """Generate response for algorithmic trading questions."""
        return """
Algorithmic Trading involves using computer programs to execute trading strategies automatically based on predefined criteria.

**Key Components:**

1. **Strategy Development:**
   - Mathematical models
   - Statistical analysis
   - Backtesting procedures
   - Risk management rules

2. **Common Strategies:**

   **Trend Following:**
   - Moving averages
   - Momentum indicators
   - Breakout strategies

   **Mean Reversion:**
   - Statistical arbitrage
   - Pairs trading
   - Reversal patterns

   **Arbitrage:**
   - Price differences across markets
   - Currency arbitrage
   - Index arbitrage

   **Market Making:**
   - Bid-ask spread capture
   - Liquidity provision
   - High-frequency trading

3. **Execution Algorithms:**
   - VWAP (Volume Weighted Average Price)
   - TWAP (Time Weighted Average Price)
   - Implementation Shortfall
   - Participation Rate algorithms

**Advantages:**
- Removes emotional bias
- Faster execution
- Consistent strategy application
- Can process large amounts of data
- 24/7 market monitoring

**Risks:**
- Model risk and overfitting
- Technology failures
- Market impact
- Regulatory compliance
- Flash crashes

**Technologies:**
- Python, R, C++ for development
- APIs for market data and execution
- Cloud computing for scalability
- Machine learning for pattern recognition
"""
    
    def _general_financial_response(self, question: str, docs: List) -> str:
        """Generate general financial response using retrieved documents."""
        if not docs:
            return """
I'd be happy to help with your quantitative finance question! However, I need more specific information 
to provide a detailed answer. 

Some topics I can help with include:
- Option pricing models (Black-Scholes, Binomial)
- Risk management (VaR, Expected Shortfall)
- Portfolio theory (Markowitz, CAPM)
- Derivatives and structured products
- Algorithmic trading strategies
- Financial econometrics and modeling

Could you please rephrase your question with more specific financial terms or concepts?
"""
        
        # Use the most relevant document to generate response
        main_doc = docs[0]
        title = main_doc.metadata.get('title', 'Financial Concept')
        category = main_doc.metadata.get('category', 'Finance')
        
        response = f"""
Based on your question about {category.lower()}, here's what I can tell you about **{title}**:

{main_doc.page_content}

**Key Takeaways:**
"""
        
        # Extract key points from the document
        content_lines = main_doc.page_content.split('\n')
        bullet_points = [line.strip() for line in content_lines if line.strip().startswith('-') or line.strip().startswith('1.') or line.strip().startswith('2.') or line.strip().startswith('3.')]
        
        if bullet_points:
            for point in bullet_points[:3]:
                response += f"\n• {point.lstrip('- 123.')}"
        else:
            # Extract first few sentences as key points
            sentences = main_doc.page_content.split('. ')
            for sentence in sentences[:2]:
                if len(sentence.strip()) > 20:
                    response += f"\n• {sentence.strip()}."
        
        if len(docs) > 1:
            response += f"\n\n*This response is based on {len(docs)} relevant documents from our financial knowledge base.*"
        
        return response
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get conversation statistics."""
        if not self.conversation_history:
            return {"message": "No conversation history available"}
        
        total_queries = len(self.conversation_history)
        avg_response_time = sum(conv['response_time'] for conv in self.conversation_history) / total_queries
        
        return {
            "total_queries": total_queries,
            "average_response_time": avg_response_time,
            "last_query_time": self.conversation_history[-1]['timestamp'].isoformat(),
            "performance": "excellent" if avg_response_time < 1 else "good" if avg_response_time < 3 else "acceptable"
        }
    
    def clear_memory(self):
        """Clear conversation history."""
        self.conversation_history.clear()
        logger.info("Conversation history cleared")
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        return {
            "overall_healthy": True,
            "components": {
                "vector_store": self.vector_store is not None,
                "conversation_history": True,
                "financial_concepts": len(self.financial_concepts) > 0
            },
            "timestamp": datetime.now().isoformat()
        }


# For backward compatibility
QuantFinanceAgent = SimpleQuantFinanceAgent
EnhancedQuantFinanceAgent = SimpleQuantFinanceAgent
