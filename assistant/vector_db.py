import os
import logging
from typing import List, Dict, Any, Optional
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_sample_documents() -> List[Document]:
    """Create sample documents for demonstration purposes."""
    sample_docs = [
        Document(
            page_content="""
            The Black-Scholes model is a mathematical model for the dynamics of a financial market 
            containing derivative investment instruments. It estimates the price of European-style options 
            using the Black-Scholes-Merton formula. The key assumptions include constant volatility, 
            constant risk-free rate, and log-normal distribution of stock prices.
            
            The Black-Scholes formula for a European call option is:
            C = S₀ * N(d₁) - K * e^(-rT) * N(d₂)
            
            Where:
            - C = Call option price
            - S₀ = Current stock price  
            - K = Strike price
            - r = Risk-free rate
            - T = Time to expiration
            - N = Cumulative standard normal distribution
            """,
            metadata={
                "title": "Black-Scholes Option Pricing Model",
                "authors": ["Fischer Black", "Myron Scholes"],
                "source": "sample_financial_theory.pdf",
                "category": "Options Pricing"
            }
        ),
        
        Document(
            page_content="""
            Value at Risk (VaR) is a statistical measure used to assess the level of financial risk 
            within a firm, portfolio, or position over a specific time frame. VaR estimates how much 
            a set of investments might lose, given normal market conditions, in a set time period 
            such as a day.
            
            There are three main approaches to calculating VaR:
            1. Historical Simulation Method - Uses historical returns to simulate potential losses
            2. Parametric Method (Variance-Covariance) - Assumes normal distribution of returns
            3. Monte Carlo Simulation - Uses random sampling to model potential outcomes
            
            VaR is typically expressed as a percentage or dollar amount. For example, a 1-day 95% VaR 
            of $1 million means there is a 95% confidence that losses will not exceed $1 million in one day.
            Expected Shortfall (ES) is often used alongside VaR to measure tail risk.
            """,
            metadata={
                "title": "Value at Risk (VaR) in Financial Risk Management",
                "authors": ["Philippe Jorion"],
                "source": "risk_management_handbook.pdf",
                "category": "Risk Management"
            }
        ),
        
        Document(
            page_content="""
            Modern Portfolio Theory (MPT) is a mathematical framework for assembling a portfolio of assets 
            such that the expected return is maximized for a given level of risk. It is a formalization 
            and extension of diversification in investing.
            
            Key concepts include:
            - Efficient Frontier: The set of optimal portfolios offering the highest expected return for each level of risk
            - Capital Asset Pricing Model (CAPM): E(R) = Rf + β(E(Rm) - Rf)
            - Sharpe Ratio: (Portfolio Return - Risk-free Rate) / Portfolio Standard Deviation
            - Beta: Measure of systematic risk relative to the market
            - Alpha: Excess return above what CAPM predicts
            
            The theory assumes investors are rational, markets are efficient, and investors can borrow 
            and lend at the risk-free rate. Harry Markowitz won the Nobel Prize for this work.
            """,
            metadata={
                "title": "Modern Portfolio Theory and Investment Analysis",
                "authors": ["Harry Markowitz"],
                "source": "portfolio_theory.pdf",
                "category": "Portfolio Management"
            }
        ),
        
        Document(
            page_content="""
            Algorithmic trading refers to the use of computer algorithms to automatically make trading 
            decisions, submit orders, and manage those orders after submission. These algorithms are 
            based on predefined criteria such as timing, price, quantity, or any mathematical model.
            
            Common algorithmic trading strategies include:
            1. Trend Following Strategies - Moving averages, momentum indicators
            2. Arbitrage Opportunities - Price differences between markets
            3. Index Fund Rebalancing - Automatic portfolio adjustments
            4. Mathematical Model-based Strategies - Statistical arbitrage
            5. Trading Range (Mean Reversion) - Buy low, sell high strategies
            6. Volume Weighted Average Price (VWAP) - Execute large orders efficiently
            7. Time Weighted Average Price (TWAP) - Spread orders over time
            8. Implementation Shortfall - Minimize market impact
            
            High-frequency trading (HFT) is a subset characterized by extremely high speeds and turnover rates.
            """,
            metadata={
                "title": "Algorithmic Trading Strategies",
                "authors": ["Ernest Chan"],
                "source": "algorithmic_trading.pdf",
                "category": "Trading Strategies"
            }
        )
    ]
    
    return sample_docs


def create_vector_store(documents=None):
    """Create and return a vector store from a list of documents."""
    # Use HuggingFace embeddings that work offline
    try:
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
    except Exception as e:
        logger.warning(f"Failed to load HuggingFace embeddings: {e}")
        # Fallback to simpler embeddings
        from langchain_community.embeddings import HuggingFaceEmbeddings
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Create documents if not provided
    if documents is None:
        logger.info("No documents provided, creating sample financial documents")
        documents = create_sample_documents()
    
    # Convert documents if they're in dict format
    docs = []
    for doc in documents:
        if isinstance(doc, dict):
            text = doc.get("text", doc.get("page_content", ""))
            metadata = doc.get("metadata", {})
            docs.append(Document(page_content=text, metadata=metadata))
        elif isinstance(doc, Document):
            docs.append(doc)
    
    # Split documents into chunks for better retrieval
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    
    split_docs = text_splitter.split_documents(docs)
    logger.info(f"Split {len(docs)} documents into {len(split_docs)} chunks")
    
    # Create vector store
    vector_store = FAISS.from_documents(split_docs, embeddings)
    logger.info("Vector store created successfully")
    
    return vector_store


def load_vector_store(index_path="./knowledge_base/vector_db"):
    """Load an existing vector store from disk or create a new one."""
    try:
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
    except Exception as e:
        logger.warning(f"Failed to load HuggingFace embeddings: {e}")
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Check if vector store already exists
    if os.path.exists(index_path) and os.path.exists(f"{index_path}.pkl"):
        try:
            logger.info(f"Loading existing vector store from {index_path}")
            vector_store = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
            logger.info(f"Loaded vector store with {vector_store.index.ntotal} documents")
            return vector_store
        except Exception as e:
            logger.warning(f"Failed to load existing vector store: {e}")
    
    # Create new vector store if loading fails or doesn't exist
    logger.info("Creating new vector store with sample documents")
    vector_store = create_vector_store()
    
    # Try to save the new vector store
    try:
        os.makedirs(os.path.dirname(index_path), exist_ok=True)
        vector_store.save_local(index_path)
        logger.info(f"Vector store saved to {index_path}")
    except Exception as e:
        logger.warning(f"Failed to save vector store: {e}")
    
    return vector_store