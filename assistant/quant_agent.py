"""
Quantitative Finance AI Agent - Enhanced Implementation
Author: SPINOR Technologies
Date: August 6, 2025
Version: 2.0
"""

import os
import time
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import numpy as np

# LangChain imports
from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from langchain.memory import ConversationSummaryBufferMemory
from langchain_community.llms import HuggingFaceHub
from langchain.prompts import PromptTemplate
from langchain.callbacks.manager import CallbackManagerForChainRun
from langchain.schema import Document

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedQuantFinanceAgent:
    """
    Advanced Quantitative Finance AI Agent with enhanced capabilities.
    
    Features:
    - Multi-model support with fallbacks
    - Conversation memory and context awareness
    - Specialized financial prompts and templates
    - Query preprocessing and result post-processing
    - Performance monitoring and caching
    - Error handling and graceful degradation
    """
    
    def __init__(self, vector_store, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the enhanced quantitative finance agent.
        
        Args:
            vector_store: Pre-loaded vector store for document retrieval
            config: Configuration dictionary with agent parameters
        """
        self.vector_store = vector_store
        self.config = self._setup_config(config)
        self.conversation_history = []
        self.query_count = 0
        self.total_response_time = 0.0
        
        # Initialize components
        self._setup_retriever()
        self._setup_llm()
        self._setup_memory()
        self._setup_chains()
        self._setup_prompts()
        
        logger.info("Enhanced QuantFinance Agent initialized successfully")
    
    def _setup_config(self, config: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Setup agent configuration with defaults optimized for Spanish markets."""
        default_config = {
            "model_name": "google/flan-t5-base",  # Modelo más equilibrado por defecto
            "temperature": 0.1,
            "max_length": 512,
            "top_k": 5,
            "enable_memory": True,
            "memory_max_tokens": 1000,
            "enable_caching": True,
            "enable_preprocessing": True,
            "enable_postprocessing": True,
            "response_timeout": 30,
            "fallback_models": ["google/flan-t5-small", "distilbert-base-uncased"],
            
            # Configuraciones específicas para eficiencia
            "lightweight_mode": True,
            "auto_optimize": True,
            "language_preference": "es",  # Preferencia de idioma
            "market_focus": ["european", "latam", "global"],  # Enfoque de mercados
            
            # Configuración de rendimiento adaptivo
            "performance_mode": "balanced",  # ultralight, balanced, performance
            "batch_processing": True,
            "memory_optimization": True,
            "response_caching": True,
            
            # Configuración de calidad de papers
            "paper_quality_threshold": 0.75,
            "max_papers_per_query": 10,
            "prefer_recent_papers": True,
            "multilingual_support": True
        }
        
        if config:
            default_config.update(config)
        
        # Optimización automática basada en recursos disponibles
        if default_config.get("auto_optimize", True):
            default_config = self._auto_optimize_config(default_config)
        
        return default_config
    
    def _auto_optimize_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Optimiza automáticamente la configuración basada en recursos disponibles."""
        try:
            import psutil
            
            # Obtener información del sistema
            available_memory = psutil.virtual_memory().available / (1024**3)  # GB
            cpu_count = psutil.cpu_count()
            
            # Ajustar configuración según recursos
            if available_memory < 4.0:
                # Modo ultraligero para sistemas con poca memoria
                config.update({
                    "model_name": "google/flan-t5-small",
                    "max_length": 256,
                    "top_k": 3,
                    "memory_max_tokens": 500,
                    "performance_mode": "ultralight"
                })
                logger.info("🚀 Modo ultraligero activado (memoria < 4GB)")
                
            elif available_memory < 8.0:
                # Modo balanceado
                config.update({
                    "model_name": "google/flan-t5-base",
                    "max_length": 512,
                    "top_k": 5,
                    "performance_mode": "balanced"
                })
                logger.info("⚖️ Modo balanceado activado (memoria 4-8GB)")
                
            else:
                # Modo de alto rendimiento
                config.update({
                    "model_name": "google/flan-t5-large", 
                    "max_length": 1024,
                    "top_k": 8,
                    "memory_max_tokens": 2000,
                    "performance_mode": "performance"
                })
                logger.info("🚀 Modo alto rendimiento activado (memoria > 8GB)")
            
            # Ajustar procesamiento según CPUs
            if cpu_count >= 8:
                config["batch_processing"] = True
                config["parallel_processing"] = True
            
            logger.info(f"💻 Sistema: {available_memory:.1f}GB RAM, {cpu_count} CPUs")
            
        except ImportError:
            logger.warning("psutil no disponible, usando configuración por defecto")
        except Exception as e:
            logger.warning(f"Error en optimización automática: {e}")
        
        return config
    
    def _setup_retriever(self):
        """Setup document retriever with enhanced search parameters."""
        search_kwargs = {
            "k": self.config["top_k"],
            "score_threshold": 0.7,
            "fetch_k": self.config["top_k"] * 2
        }
        
        self.retriever = self.vector_store.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs=search_kwargs
        )
        logger.info(f"Retriever configured with top_k={self.config['top_k']}")
    
    def _setup_llm(self):
        """Setup language model with fallback options."""
        try:
            # Check for API token
            api_token = os.getenv("HUGGINGFACE_API_TOKEN")
            if not api_token:
                logger.warning("HUGGINGFACE_API_TOKEN not found. Using default model.")
            
            model_kwargs = {
                "temperature": self.config["temperature"],
                "max_length": self.config["max_length"],
                "do_sample": True,
                "top_p": 0.9,
                "top_k": 50
            }
            
            self.llm = HuggingFaceHub(
                repo_id=self.config["model_name"],
                model_kwargs=model_kwargs,
                huggingfacehub_api_token=api_token
            )
            
            logger.info(f"LLM initialized: {self.config['model_name']}")
            
        except Exception as e:
            logger.error(f"Failed to initialize primary LLM: {e}")
            self._setup_fallback_llm()
    
    def _setup_fallback_llm(self):
        """Setup fallback LLM if primary fails."""
        for fallback_model in self.config["fallback_models"]:
            try:
                self.llm = HuggingFaceHub(
                    repo_id=fallback_model,
                    model_kwargs={"temperature": self.config["temperature"]}
                )
                logger.info(f"Fallback LLM initialized: {fallback_model}")
                break
            except Exception as e:
                logger.warning(f"Fallback model {fallback_model} failed: {e}")
                continue
        else:
            # Create mock LLM as last resort
            self.llm = self._create_mock_llm()
            logger.warning("Using mock LLM - all models failed to initialize")
    
    def _create_mock_llm(self):
        """Create a mock LLM for testing/fallback purposes."""
        class MockLLM:
            def __call__(self, prompt, **kwargs):
                return f"Mock response for query about quantitative finance. Original prompt length: {len(prompt)} characters."
            
            def invoke(self, prompt, **kwargs):
                return self(prompt, **kwargs)
        
        return MockLLM()
    
    def _setup_memory(self):
        """Setup conversation memory if enabled."""
        if self.config["enable_memory"]:
            try:
                self.memory = ConversationSummaryBufferMemory(
                    llm=self.llm,
                    max_token_limit=self.config["memory_max_tokens"],
                    return_messages=True,
                    memory_key="chat_history",
                    output_key="answer"
                )
                logger.info("Conversation memory enabled")
            except Exception as e:
                logger.warning(f"Failed to setup memory: {e}")
                self.memory = None
        else:
            self.memory = None
    
    def _setup_chains(self):
        """Setup QA chains with memory and custom prompts."""
        try:
            if self.memory:
                # Conversational chain with memory
                self.qa_chain = ConversationalRetrievalChain.from_llm(
                    llm=self.llm,
                    retriever=self.retriever,
                    memory=self.memory,
                    return_source_documents=True,
                    verbose=True
                )
            else:
                # Simple QA chain without memory
                self.qa_chain = RetrievalQA.from_chain_type(
                    llm=self.llm,
                    chain_type="stuff",
                    retriever=self.retriever,
                    return_source_documents=True,
                    verbose=True
                )
            
            logger.info("QA chains configured successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup QA chains: {e}")
            self.qa_chain = None
    
    def _setup_prompts(self):
        """Setup specialized prompts for quantitative finance with Spanish support."""
        # Prompt principal bilingüe
        self.finance_prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template="""
Eres un asistente experto en finanzas cuantitativas con conocimiento profundo en:
- Cálculo estocástico y matemáticas financieras
- Modelos de valoración de opciones (Black-Scholes, Heston, etc.)
- Gestión de riesgos y teoría de carteras
- Econofísica y microestructura de mercados
- Derivados financieros y productos estructurados
- Trading algorítmico y estrategias cuantitativas

You are an expert quantitative finance AI assistant with deep knowledge in:
- Stochastic calculus and mathematical finance
- Options pricing models (Black-Scholes, Heston, etc.)
- Risk management and portfolio theory
- Econophysics and market microstructure
- Financial derivatives and structured products
- Algorithmic trading and quantitative strategies

Contexto de literatura financiera:
Financial literature context:
{context}

Pregunta/Question: {question}

Por favor proporciona una respuesta técnicamente precisa basada en el contexto proporcionado. 
Incluye formulaciones matemáticas cuando sea relevante, cita modelos o papers específicos cuando aplique,
y explica conceptos complejos de manera clara. Si la pregunta involucra cálculos, muestra los pasos.

Please provide a comprehensive, technically accurate answer based on the provided context. 
Include mathematical formulations when relevant, cite specific models or papers when applicable,
and explain complex concepts clearly. If the question involves calculations, show the steps.

Respuesta/Answer:"""
        )
        
        # Prompts especializados con soporte multiidioma
        self.risk_prompt = self._create_risk_management_prompt()
        self.pricing_prompt = self._create_pricing_model_prompt()
        self.strategy_prompt = self._create_strategy_prompt()
        self.spanish_markets_prompt = self._create_spanish_markets_prompt()
    
    def _create_spanish_markets_prompt(self) -> PromptTemplate:
        """Create specialized prompt for Spanish and Latin American markets."""
        return PromptTemplate(
            input_variables=["context", "question"],
            template="""
Eres un especialista en mercados financieros hispanohablantes con experiencia en:
- Mercados de España: IBEX 35, MEFF, renta fija española
- Mercados latinoamericanos: México (BMV), Brasil (B3), Chile (BCS), Colombia (BVC)
- Regulación financiera iberoamericana: CNMV, CVM, CMF
- Instrumentos específicos: FIAMM, hedge funds latinos, bonos soberanos
- Riesgos específicos: riesgo país, volatilidad de commodities, riesgo cambiario

You are a specialist in Spanish-speaking financial markets with expertise in:
- Spanish markets: IBEX 35, MEFF, Spanish fixed income
- Latin American markets: Mexico (BMV), Brazil (B3), Chile (BCS), Colombia (BVC) 
- Ibero-American financial regulation: CNMV, CVM, CMF
- Specific instruments: FIAMM, Latin hedge funds, sovereign bonds
- Specific risks: country risk, commodity volatility, exchange rate risk

Contexto: {context}
Pregunta: {question}

Proporciona análisis específico para mercados hispanohablantes con consideraciones regulatorias y culturales locales.
Provide specific analysis for Spanish-speaking markets with local regulatory and cultural considerations.

Respuesta:"""
        )
    
    def _create_risk_management_prompt(self) -> PromptTemplate:
        """Create specialized prompt for risk management queries."""
        return PromptTemplate(
            input_variables=["context", "question"],
            template="""
You are a risk management expert. Focus on:
- Value at Risk (VaR) and Expected Shortfall (ES)
- Stress testing and scenario analysis
- Credit risk, market risk, and operational risk
- Risk metrics and model validation
- Regulatory frameworks (Basel III, Solvency II)

Context: {context}
Question: {question}

Provide a risk-focused analysis with quantitative measures where appropriate.
Answer:"""
        )
    
    def _create_pricing_model_prompt(self) -> PromptTemplate:
        """Create specialized prompt for pricing model queries."""
        return PromptTemplate(
            input_variables=["context", "question"],
            template="""
You are a derivatives pricing specialist. Focus on:
- Option pricing models (Black-Scholes, Binomial, Monte Carlo)
- Stochastic volatility models (Heston, SABR)
- Interest rate models (Vasicek, CIR, Hull-White)
- Credit derivatives and exotic products
- Model calibration and validation

Context: {context}
Question: {question}

Provide detailed pricing methodology with mathematical foundations.
Answer:"""
        )
    
    def _create_strategy_prompt(self) -> PromptTemplate:
        """Create specialized prompt for trading strategy queries."""
        return PromptTemplate(
            input_variables=["context", "question"],
            template="""
You are a quantitative strategy expert. Focus on:
- Algorithmic trading strategies
- Portfolio optimization and asset allocation
- Factor models and alpha generation
- Backtesting and performance attribution
- Market microstructure and execution

Context: {context}
Question: {question}

Provide strategic insights with implementation considerations.
Answer:"""
        )

    def _preprocess_query(self, question: str) -> str:
        """Preprocess query to improve retrieval and response quality."""
        if not self.config["enable_preprocessing"]:
            return question
        
        # Clean and normalize the question
        question = question.strip()
        
        # Add financial context keywords for better retrieval
        finance_keywords = {
            'option': ['Black-Scholes', 'volatility', 'strike price'],
            'risk': ['VaR', 'Value at Risk', 'Expected Shortfall'],
            'portfolio': ['Markowitz', 'optimization', 'efficient frontier'],
            'volatility': ['stochastic volatility', 'GARCH', 'volatility modeling'],
            'derivative': ['pricing', 'hedging', 'Greeks'],
            'credit': ['credit risk', 'default probability', 'credit derivatives']
        }
        
        question_lower = question.lower()
        for keyword, related_terms in finance_keywords.items():
            if keyword in question_lower:
                # Enhance question with context
                question = f"{question} (Related to: {', '.join(related_terms[:2])})"
                break
        
        return question
    
    def _postprocess_response(self, response: str, sources: List[Document]) -> Dict[str, Any]:
        """Postprocess response to improve quality and add metadata."""
        if not self.config["enable_postprocessing"]:
            return {
                "result": response,
                "source_documents": sources,
                "metadata": {}
            }
        
        # Extract key financial concepts mentioned
        financial_concepts = self._extract_financial_concepts(response)
        
        # Calculate response quality metrics
        quality_metrics = self._calculate_response_quality(response, sources)
        
        # Enhance source documents with relevance scores
        enhanced_sources = self._enhance_source_documents(sources)
        
        # Add citations if mathematical formulas are detected
        citations = self._extract_citations(response, enhanced_sources)
        
        return {
            "result": response,
            "source_documents": enhanced_sources,
            "metadata": {
                "financial_concepts": financial_concepts,
                "quality_metrics": quality_metrics,
                "citations": citations,
                "response_length": len(response),
                "source_count": len(sources),
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def _extract_financial_concepts(self, response: str) -> List[str]:
        """Extract financial concepts mentioned in the response."""
        concepts = [
            "Black-Scholes", "Monte Carlo", "VaR", "Expected Shortfall",
            "Markowitz", "CAPM", "volatility", "Greeks", "derivatives",
            "stochastic calculus", "Ito process", "Brownian motion",
            "risk management", "portfolio optimization", "arbitrage"
        ]
        
        found_concepts = []
        response_lower = response.lower()
        
        for concept in concepts:
            if concept.lower() in response_lower:
                found_concepts.append(concept)
        
        return found_concepts
    
    def _calculate_response_quality(self, response: str, sources: List[Document]) -> Dict[str, float]:
        """Calculate quality metrics for the response."""
        return {
            "length_score": min(len(response) / 500, 1.0),  # Normalized length score
            "source_utilization": len(sources) / max(self.config["top_k"], 1),
            "technical_depth": len(self._extract_financial_concepts(response)) / 10,
            "completeness": 1.0 if len(response) > 100 else len(response) / 100
        }
    
    def _enhance_source_documents(self, sources: List[Document]) -> List[Document]:
        """Enhance source documents with additional metadata."""
        enhanced = []
        
        for i, doc in enumerate(sources):
            # Add relevance ranking
            doc.metadata['relevance_rank'] = i + 1
            doc.metadata['relevance_score'] = max(0.9 - (i * 0.1), 0.1)
            
            # Extract document type
            source_url = doc.metadata.get('source', '')
            if 'arxiv' in source_url:
                doc.metadata['document_type'] = 'academic_paper'
            elif '.pdf' in source_url:
                doc.metadata['document_type'] = 'pdf_document'
            else:
                doc.metadata['document_type'] = 'web_content'
            
            enhanced.append(doc)
        
        return enhanced
    
    def _extract_citations(self, response: str, sources: List[Document]) -> List[Dict[str, str]]:
        """Extract potential citations from response and sources."""
        citations = []
        
        for source in sources[:3]:  # Top 3 most relevant sources
            title = source.metadata.get('title', 'Unknown')
            authors = source.metadata.get('authors', [])
            
            if title and title != 'Unknown':
                citations.append({
                    'title': title,
                    'authors': ', '.join(authors) if authors else 'Unknown',
                    'relevance': source.metadata.get('relevance_score', 0.5)
                })
        
        return citations
    
    def _select_prompt_template(self, question: str) -> PromptTemplate:
        """Select appropriate prompt template based on question content."""
        question_lower = question.lower()
        
        risk_keywords = ['risk', 'var', 'value at risk', 'expected shortfall', 'stress test']
        pricing_keywords = ['option', 'pricing', 'black-scholes', 'monte carlo', 'derivative']
        strategy_keywords = ['strategy', 'trading', 'portfolio', 'optimization', 'backtest']
        
        if any(keyword in question_lower for keyword in risk_keywords):
            return self.risk_prompt
        elif any(keyword in question_lower for keyword in pricing_keywords):
            return self.pricing_prompt
        elif any(keyword in question_lower for keyword in strategy_keywords):
            return self.strategy_prompt
        else:
            return self.finance_prompt_template

    def query(self, question: str, use_memory: bool = True) -> Dict[str, Any]:
        """
        Execute enhanced financial query with preprocessing and postprocessing.
        
        Args:
            question: The financial question to answer
            use_memory: Whether to use conversation memory
        
        Returns:
            Enhanced response with metadata and quality metrics
        """
        start_time = time.time()
        self.query_count += 1
        
        try:
            # Preprocess the query
            processed_question = self._preprocess_query(question)
            logger.info(f"Processing query {self.query_count}: {question[:50]}...")
            
            # Execute the query
            if self.qa_chain is None:
                # Fallback: direct retrieval + simple response
                docs = self.retriever.get_relevant_documents(processed_question)
                response = f"Retrieved {len(docs)} relevant documents for: {question}"
                result = {
                    "result": response,
                    "source_documents": docs
                }
            else:
                # Use the configured QA chain
                if self.memory and use_memory:
                    result = self.qa_chain({"question": processed_question})
                else:
                    result = self.qa_chain({"query": processed_question})
            
            # Postprocess the response
            enhanced_result = self._postprocess_response(
                result.get("result", result.get("answer", "")),
                result.get("source_documents", [])
            )
            
            # Update performance metrics
            response_time = time.time() - start_time
            self.total_response_time += response_time
            
            enhanced_result["metadata"]["response_time"] = response_time
            enhanced_result["metadata"]["avg_response_time"] = self.total_response_time / self.query_count
            
            # Store conversation history
            self.conversation_history.append({
                "question": question,
                "response": enhanced_result["result"],
                "timestamp": datetime.now(),
                "response_time": response_time
            })
            
            logger.info(f"Query completed in {response_time:.2f}s")
            return enhanced_result
            
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return self._create_error_response(question, str(e))
    
    def _create_error_response(self, question: str, error: str) -> Dict[str, Any]:
        """Create standardized error response."""
        return {
            "result": f"I apologize, but I encountered an error processing your question about: {question}. Error: {error}",
            "source_documents": [],
            "metadata": {
                "error": True,
                "error_message": error,
                "timestamp": datetime.now().isoformat(),
                "financial_concepts": [],
                "quality_metrics": {"error": True}
            }
        }
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get summary of conversation history and performance metrics."""
        if not self.conversation_history:
            return {"message": "No conversation history available"}
        
        total_queries = len(self.conversation_history)
        avg_response_time = self.total_response_time / total_queries if total_queries > 0 else 0
        
        recent_topics = []
        for conv in self.conversation_history[-5:]:  # Last 5 conversations
            concepts = self._extract_financial_concepts(conv["response"])
            recent_topics.extend(concepts)
        
        return {
            "total_queries": total_queries,
            "average_response_time": avg_response_time,
            "recent_topics": list(set(recent_topics)),
            "session_start": self.conversation_history[0]["timestamp"].isoformat(),
            "last_query": self.conversation_history[-1]["timestamp"].isoformat(),
            "performance": "optimal" if avg_response_time < 5 else "acceptable" if avg_response_time < 10 else "slow"
        }
    
    def clear_memory(self):
        """Clear conversation memory and history."""
        if self.memory:
            self.memory.clear()
        self.conversation_history.clear()
        logger.info("Memory and conversation history cleared")
    
    def update_config(self, new_config: Dict[str, Any]):
        """Update agent configuration dynamically."""
        self.config.update(new_config)
        
        # Reinitialize components if necessary
        if "top_k" in new_config:
            self._setup_retriever()
        
        if any(key in new_config for key in ["temperature", "max_length"]):
            self._setup_llm()
        
        logger.info(f"Configuration updated: {new_config}")
    
    def get_available_models(self) -> List[str]:
        """Get list of available models."""
        return [self.config["model_name"]] + self.config["fallback_models"]
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on agent components."""
        health_status = {
            "llm": False,
            "retriever": False,
            "memory": False,
            "qa_chain": False,
            "vector_store": False
        }
        
        try:
            # Test LLM
            test_response = self.llm("Test prompt")
            health_status["llm"] = bool(test_response)
        except:
            pass
        
        try:
            # Test retriever
            test_docs = self.retriever.get_relevant_documents("test query")
            health_status["retriever"] = isinstance(test_docs, list)
        except:
            pass
        
        health_status["memory"] = self.memory is not None
        health_status["qa_chain"] = self.qa_chain is not None
        health_status["vector_store"] = self.vector_store is not None
        
        overall_health = all(health_status.values())
        
        return {
            "overall_healthy": overall_health,
            "components": health_status,
            "timestamp": datetime.now().isoformat()
        }


# Backward compatibility alias
QuantFinanceAgent = EnhancedQuantFinanceAgent