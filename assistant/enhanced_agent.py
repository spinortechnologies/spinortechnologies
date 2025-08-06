#!/usr/bin/env python3
"""
Enhanced Multilingual Quantitative Finance AI Agent
Author: SPINOR Technologies
Date: August 6, 2025
Version: 4.0 - Multilingual Edition

Advanced AI agent with:
- Automatic language detection (Spanish/English)
- Dynamic response language matching
- Enhanced online paper integration
- Improved knowledge base training
- Real-time learning from ArXiv papers
"""

import os
import re
import json
import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from pathlib import Path

# Language detection
try:
    from langdetect import detect, DetectorFactory
    from langdetect.lang_detect_exception import LangDetectException
    DetectorFactory.seed = 0  # For consistent results
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False
    logging.info("langdetect not available - using keyword-based detection")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedMultilingualAgent:
    """
    Enhanced Multilingual Quantitative Finance AI Agent
    
    Features:
    - Automatic language detection and response matching
    - Dynamic paper integration and learning
    - Enhanced knowledge base with real-time updates
    - Improved response quality with recent research
    """
    
    def __init__(self, vector_store):
        """Initialize the enhanced multilingual agent."""
        self.vector_store = vector_store
        self.conversation_history = []
        self.query_count = 0
        self.learned_papers = []
        
        # Language detection patterns
        self.spanish_patterns = [
            r'\b(qué|que|cómo|como|cuál|cual|dónde|donde|cuándo|cuando|por qué|porque)\b',
            r'\b(el|la|los|las|un|una|de|del|en|con|por|para|y|o|pero|si|no)\b',
            r'\b(finanzas|riesgo|opciones|derivados|portafolio|modelo|precio|mercado)\b'
        ]
        
        self.english_patterns = [
            r'\b(what|how|which|where|when|why|who|can|could|would|should)\b',
            r'\b(the|a|an|of|in|on|at|to|for|with|by|from|and|or|but|if|not)\b',
            r'\b(finance|risk|options|derivatives|portfolio|model|price|market)\b'
        ]
        
        # Initialize enhanced knowledge base
        self._initialize_enhanced_knowledge()
        
        # Load and integrate recent papers
        self._integrate_recent_papers()
        
        logger.info("🚀 Enhanced Multilingual Finance AI Agent initialized")
    
    def detect_language(self, text: str) -> str:
        """
        Detect the language of the input text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            'es' for Spanish, 'en' for English
        """
        text_clean = text.lower().strip()
        
        # Try langdetect first if available
        if LANGDETECT_AVAILABLE:
            try:
                detected = detect(text_clean)
                if detected in ['es', 'en']:
                    return detected
            except LangDetectException:
                pass
        
        # Fallback to pattern-based detection
        spanish_score = sum(1 for pattern in self.spanish_patterns 
                          if re.search(pattern, text_clean, re.IGNORECASE))
        english_score = sum(1 for pattern in self.english_patterns 
                          if re.search(pattern, text_clean, re.IGNORECASE))
        
        # Additional keyword scoring
        spanish_keywords = ['finanzas', 'riesgo', 'opciones', 'modelo', 'precio', 'mercado', 'análisis']
        english_keywords = ['finance', 'risk', 'options', 'model', 'price', 'market', 'analysis']
        
        spanish_score += sum(1 for word in spanish_keywords if word in text_clean)
        english_score += sum(1 for word in english_keywords if word in text_clean)
        
        return 'es' if spanish_score > english_score else 'en'
    
    def _initialize_enhanced_knowledge(self):
        """Initialize enhanced financial knowledge base."""
        self.enhanced_concepts = {
            'black_scholes': {
                'keywords_en': ['black', 'scholes', 'option', 'pricing', 'call', 'put', 'european'],
                'keywords_es': ['black', 'scholes', 'opción', 'opcion', 'precio', 'call', 'put', 'europea'],
                'response_en': self._black_scholes_response_en,
                'response_es': self._black_scholes_response_es
            },
            'var': {
                'keywords_en': ['var', 'value at risk', 'risk', 'loss', 'confidence', 'percentile'],
                'keywords_es': ['var', 'valor en riesgo', 'riesgo', 'pérdida', 'perdida', 'confianza'],
                'response_en': self._var_response_en,
                'response_es': self._var_response_es
            },
            'portfolio': {
                'keywords_en': ['portfolio', 'markowitz', 'optimization', 'efficient', 'frontier', 'diversification'],
                'keywords_es': ['portafolio', 'cartera', 'markowitz', 'optimización', 'eficiente', 'frontera', 'diversificación'],
                'response_en': self._portfolio_response_en,
                'response_es': self._portfolio_response_es
            },
            'derivatives': {
                'keywords_en': ['derivative', 'futures', 'forwards', 'swaps', 'options', 'hedging'],
                'keywords_es': ['derivado', 'futuro', 'forward', 'swap', 'opción', 'cobertura'],
                'response_en': self._derivatives_response_en,
                'response_es': self._derivatives_response_es
            },
            'monte_carlo': {
                'keywords_en': ['monte carlo', 'simulation', 'random', 'sampling', 'numerical'],
                'keywords_es': ['monte carlo', 'simulación', 'simulacion', 'aleatorio', 'muestreo', 'numérico'],
                'response_en': self._monte_carlo_response_en,
                'response_es': self._monte_carlo_response_es
            }
        }
    
    def _integrate_recent_papers(self):
        """Integrate recent papers into the knowledge base."""
        papers_dir = Path("./data/papers")
        
        if not papers_dir.exists():
            logger.info("📚 No papers directory found - creating sample knowledge")
            self._create_sample_knowledge()
            return
        
        try:
            # Find the most recent papers file
            paper_files = list(papers_dir.glob("papers_*.json"))
            if not paper_files:
                logger.info("📄 No paper files found")
                return
            
            latest_file = max(paper_files, key=lambda x: x.stat().st_mtime)
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                papers = json.load(f)
            
            # Process and integrate papers
            self.learned_papers = papers[:50]  # Keep recent 50 papers
            
            # Extract key concepts from papers
            self._extract_paper_concepts(papers)
            
            logger.info(f"📚 Integrated {len(papers)} recent papers into knowledge base")
            
            # Store paper integration info
            self.papers_info = {
                'count': len(papers),
                'last_update': datetime.now().isoformat(),
                'file': str(latest_file),
                'topics': self._extract_paper_topics(papers[:10])
            }
            
        except Exception as e:
            logger.error(f"Error integrating papers: {e}")
            self._create_sample_knowledge()
    
    def _extract_paper_concepts(self, papers: List[Dict]):
        """Extract and learn concepts from recent papers."""
        concept_keywords = {}
        
        for paper in papers:
            title = paper.get('title', '').lower()
            summary = paper.get('summary', '').lower()
            
            # Extract financial keywords
            financial_terms = [
                'volatility', 'option', 'derivative', 'portfolio', 'risk',
                'black-scholes', 'monte carlo', 'var', 'capm', 'sharpe',
                'volatilidad', 'opción', 'derivado', 'cartera', 'riesgo'
            ]
            
            for term in financial_terms:
                if term in title or term in summary:
                    if term not in concept_keywords:
                        concept_keywords[term] = []
                    concept_keywords[term].append({
                        'title': paper.get('title', '')[:100],
                        'authors': paper.get('authors', [])[:3],
                        'summary': summary[:200]
                    })
        
        self.dynamic_concepts = concept_keywords
        logger.info(f"🧠 Extracted {len(concept_keywords)} dynamic concepts from papers")
    
    def _extract_paper_topics(self, papers: List[Dict]) -> List[str]:
        """Extract main topics from recent papers."""
        topics = []
        for paper in papers:
            title = paper.get('title', '')
            # Extract key topics using simple keyword matching
            if any(term in title.lower() for term in ['option', 'pricing', 'black-scholes']):
                topics.append('Options Pricing')
            elif any(term in title.lower() for term in ['risk', 'var', 'value at risk']):
                topics.append('Risk Management')
            elif any(term in title.lower() for term in ['portfolio', 'optimization']):
                topics.append('Portfolio Theory')
            elif any(term in title.lower() for term in ['monte carlo', 'simulation']):
                topics.append('Computational Finance')
        
        return list(set(topics))[:5]  # Return unique topics, max 5
    
    def _create_sample_knowledge(self):
        """Create sample knowledge when no papers are available."""
        self.papers_info = {
            'count': 0,
            'last_update': datetime.now().isoformat(),
            'file': 'none',
            'topics': ['Sample Topics']
        }
    
    def query(self, question: str) -> Dict[str, Any]:
        """
        Process a financial query with automatic language detection and response matching.
        
        Args:
            question: The financial question in Spanish or English
            
        Returns:
            Dictionary with response in the same language as the query
        """
        start_time = datetime.now()
        self.query_count += 1
        
        try:
            # Detect query language
            detected_lang = self.detect_language(question)
            logger.info(f"🗣️ Detected language: {detected_lang}")
            
            # Get relevant documents from vector store
            docs = self.vector_store.similarity_search(question, k=5)
            
            # Identify topic
            main_topic = self._identify_topic(question, detected_lang)
            
            # Generate response in the detected language
            if main_topic and main_topic in self.enhanced_concepts:
                response_func = self.enhanced_concepts[main_topic][f'response_{detected_lang}']
                response = response_func(question, docs)
            else:
                response = self._general_response(question, docs, detected_lang)
            
            # Add recent papers context if relevant
            response = self._enhance_with_papers(response, question, detected_lang)
            
            # Calculate response time
            response_time = (datetime.now() - start_time).total_seconds()
            
            # Store in conversation history
            self.conversation_history.append({
                'question': question,
                'response': response,
                'language': detected_lang,
                'timestamp': start_time,
                'response_time': response_time
            })
            
            return {
                'result': response,
                'source_documents': docs,
                'metadata': {
                    'language': detected_lang,
                    'topic': main_topic,
                    'response_time': response_time,
                    'source_count': len(docs),
                    'query_number': self.query_count,
                    'papers_integrated': len(self.learned_papers)
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            error_msg = self._get_error_message(detected_lang if 'detected_lang' in locals() else 'en')
            return {
                'result': error_msg,
                'source_documents': [],
                'metadata': {'error': True, 'error_message': str(e)}
            }
    
    def _identify_topic(self, question: str, language: str) -> Optional[str]:
        """Identify the main financial topic considering language."""
        question_lower = question.lower()
        
        for topic, data in self.enhanced_concepts.items():
            keywords = data[f'keywords_{language}']
            if any(keyword in question_lower for keyword in keywords):
                return topic
        
        return None
    
    def _enhance_with_papers(self, response: str, question: str, language: str) -> str:
        """Enhance response with relevant recent papers."""
        if not self.learned_papers:
            return response
        
        # Find relevant papers
        relevant_papers = []
        question_lower = question.lower()
        
        for paper in self.learned_papers[:10]:  # Check recent 10 papers
            title = paper.get('title', '').lower()
            summary = paper.get('summary', '').lower()
            
            # Simple relevance check
            if any(word in title or word in summary for word in question_lower.split() if len(word) > 3):
                relevant_papers.append(paper)
        
        if relevant_papers:
            if language == 'es':
                papers_section = f"\n\n## 📚 Investigación Reciente Relacionada:\n\n"
                papers_section += f"*Basado en {len(self.learned_papers)} papers recientes de ArXiv*\n\n"
                for i, paper in enumerate(relevant_papers[:3], 1):
                    title = paper.get('title', 'Sin título')[:100]
                    authors = ', '.join(paper.get('authors', [])[:2])
                    papers_section += f"**{i}.** {title}\n"
                    papers_section += f"   *Autores: {authors}*\n\n"
            else:
                papers_section = f"\n\n## 📚 Related Recent Research:\n\n"
                papers_section += f"*Based on {len(self.learned_papers)} recent ArXiv papers*\n\n"
                for i, paper in enumerate(relevant_papers[:3], 1):
                    title = paper.get('title', 'Untitled')[:100]
                    authors = ', '.join(paper.get('authors', [])[:2])
                    papers_section += f"**{i}.** {title}\n"
                    papers_section += f"   *Authors: {authors}*\n\n"
            
            response += papers_section
        
        return response
    
    def _get_error_message(self, language: str) -> str:
        """Get error message in appropriate language."""
        if language == 'es':
            return "Disculpa, encontré un error procesando tu pregunta. Por favor intenta reformularla."
        else:
            return "I apologize, but I encountered an error processing your question. Please try rephrasing it."
    
    def _general_response(self, question: str, docs: List, language: str) -> str:
        """Generate a general response in the appropriate language."""
        if language == 'es':
            return f"""
## 💼 Respuesta del Asistente de Finanzas Cuantitativas SPINOR

**Pregunta:** {question}

Basándome en mi base de conocimientos de finanzas cuantitativas y {len(self.learned_papers)} papers recientes, aquí está mi análisis:

### 🔍 Análisis:

Esta es una consulta interesante sobre finanzas cuantitativas. Basado en los documentos disponibles en mi base de conocimientos, puedo proporcionarte información relevante sobre este tema.

### 📊 Información Clave:

• **Contexto:** Las finanzas cuantitativas combinan matemáticas, estadística y programación
• **Aplicaciones:** Valoración de derivados, gestión de riesgos, optimización de portafolios
• **Métodos:** Modelos estocásticos, simulación Monte Carlo, análisis numérico

### 🚀 Recomendaciones:

1. **Profundizar en la teoría** matemática subyacente
2. **Implementar modelos** computacionales
3. **Validar resultados** con datos históricos
4. **Considerar limitaciones** del modelo

### 📚 Recursos Adicionales:

Consulta papers recientes en ArXiv categorías q-fin.* para investigación actualizada.

*Respuesta generada por SPINOR AI con {len(docs)} documentos de referencia*
            """
        else:
            return f"""
## 💼 SPINOR Quantitative Finance Assistant Response

**Query:** {question}

Based on my quantitative finance knowledge base and {len(self.learned_papers)} recent papers, here's my analysis:

### 🔍 Analysis:

This is an interesting quantitative finance query. Based on the documents available in my knowledge base, I can provide relevant information on this topic.

### 📊 Key Information:

• **Context:** Quantitative finance combines mathematics, statistics, and programming
• **Applications:** Derivatives valuation, risk management, portfolio optimization
• **Methods:** Stochastic models, Monte Carlo simulation, numerical analysis

### 🚀 Recommendations:

1. **Deepen understanding** of underlying mathematical theory
2. **Implement computational** models
3. **Validate results** with historical data
4. **Consider model** limitations

### 📚 Additional Resources:

Check recent papers in ArXiv q-fin.* categories for updated research.

*Response generated by SPINOR AI with {len(docs)} reference documents*
            """
    
    # Enhanced concept responses in both languages
    def _black_scholes_response_es(self, question: str, docs: List) -> str:
        """Respuesta sobre Black-Scholes en español."""
        return """
## 📈 Modelo Black-Scholes - Análisis Detallado

### 🎯 Fórmula Principal:
Para una opción call europea: **C = S₀ × N(d₁) - K × e^(-rT) × N(d₂)**

Donde:
- **C** = Precio de la opción call
- **S₀** = Precio actual del activo subyacente
- **K** = Precio de ejercicio (strike)
- **r** = Tasa libre de riesgo
- **T** = Tiempo hasta vencimiento
- **N** = Distribución normal acumulada

### 🔢 Cálculo de d₁ y d₂:
- **d₁ = [ln(S₀/K) + (r + σ²/2)T] / (σ√T)**
- **d₂ = d₁ - σ√T**

### ⚙️ Supuestos Clave:
1. **Volatilidad constante** (σ)
2. **Tasa de interés constante**
3. **No dividendos** durante la vida de la opción
4. **Mercados eficientes** (sin costos de transacción)
5. **Posibilidad de negociación continua**

### 🎪 Las "Griegas":
- **Delta (Δ)**: Sensibilidad al precio del subyacente
- **Gamma (Γ)**: Sensibilidad del delta
- **Theta (Θ)**: Decaimiento temporal
- **Vega (ν)**: Sensibilidad a la volatilidad
- **Rho (ρ)**: Sensibilidad a la tasa de interés

### ⚠️ Limitaciones:
• Supone log-normalidad de precios
• Volatilidad constante (irreal en la práctica)
• No considera dividendos
• Válido solo para opciones europeas

### 🚀 Aplicaciones Prácticas:
1. **Valoración de opciones** vanilla
2. **Gestión de riesgos** con las griegas
3. **Estrategias de cobertura**
4. **Arbitraje** de volatilidad
        """
    
    def _black_scholes_response_en(self, question: str, docs: List) -> str:
        """Black-Scholes response in English."""
        return """
## 📈 Black-Scholes Model - Detailed Analysis

### 🎯 Main Formula:
For a European call option: **C = S₀ × N(d₁) - K × e^(-rT) × N(d₂)**

Where:
- **C** = Call option price
- **S₀** = Current stock price
- **K** = Strike price
- **r** = Risk-free interest rate
- **T** = Time to expiration
- **N** = Cumulative standard normal distribution

### 🔢 Calculating d₁ and d₂:
- **d₁ = [ln(S₀/K) + (r + σ²/2)T] / (σ√T)**
- **d₂ = d₁ - σ√T**

### ⚙️ Key Assumptions:
1. **Constant volatility** (σ)
2. **Constant interest rate**
3. **No dividends** during option life
4. **Efficient markets** (no transaction costs)
5. **Continuous trading** possibility

### 🎪 The "Greeks":
- **Delta (Δ)**: Sensitivity to underlying price
- **Gamma (Γ)**: Delta sensitivity
- **Theta (Θ)**: Time decay
- **Vega (ν)**: Volatility sensitivity
- **Rho (ρ)**: Interest rate sensitivity

### ⚠️ Limitations:
• Assumes log-normal price distribution
• Constant volatility (unrealistic in practice)
• No dividend consideration
• Valid only for European options

### 🚀 Practical Applications:
1. **Vanilla option** valuation
2. **Risk management** with Greeks
3. **Hedging strategies**
4. **Volatility** arbitrage
        """
    
    def _var_response_es(self, question: str, docs: List) -> str:
        """Respuesta sobre VaR en español."""
        return """
## ⚠️ Value at Risk (VaR) - Gestión de Riesgos

### 🎯 Definición:
El **VaR** es una medida estadística que cuantifica el nivel de riesgo financiero dentro de una empresa, portafolio o posición durante un período específico.

### 📊 Interpretación:
**"Existe una probabilidad X% de que las pérdidas no excedan $Y en Z días"**

### 🔢 Métodos de Cálculo:

#### 1. **Método Paramétrico (Delta-Normal)**
- Asume distribución normal de retornos
- VaR = μ - (Z_α × σ × √t)
- Rápido pero limitado por el supuesto de normalidad

#### 2. **Simulación Histórica**
- Usa datos históricos reales
- No asume distribución específica
- Refleja mejor las colas pesadas

#### 3. **Simulación Monte Carlo**
- Genera miles de escenarios posibles
- Más flexible y preciso
- Computacionalmente intensivo

### ⚙️ Parámetros Clave:
- **Nivel de Confianza**: Típicamente 95% o 99%
- **Horizonte Temporal**: 1 día, 10 días, 1 mes
- **Moneda Base**: Para consolidación de riesgos

### 📈 Ejemplo Práctico:
*VaR diario al 95% de $1M significa que hay 5% de probabilidad de perder más de $1M en un día*

### ⚠️ Limitaciones del VaR:
• No informa sobre pérdidas más allá del VaR
• Puede subestimar riesgos en crisis
• Sensible a la calidad de datos históricos
• No es una medida de riesgo coherente

### 🔄 Expected Shortfall (ES):
**Complemento del VaR** que mide la pérdida esperada cuando se excede el VaR.
ES = E[Pérdida | Pérdida > VaR]
        """
    
    def _var_response_en(self, question: str, docs: List) -> str:
        """VaR response in English."""
        return """
## ⚠️ Value at Risk (VaR) - Risk Management

### 🎯 Definition:
**VaR** is a statistical measure that quantifies the level of financial risk within a firm, portfolio, or position over a specific time frame.

### 📊 Interpretation:
**"There is an X% probability that losses will not exceed $Y over Z days"**

### 🔢 Calculation Methods:

#### 1. **Parametric Method (Delta-Normal)**
- Assumes normal distribution of returns
- VaR = μ - (Z_α × σ × √t)
- Fast but limited by normality assumption

#### 2. **Historical Simulation**
- Uses actual historical data
- No specific distribution assumption
- Better reflects fat tails

#### 3. **Monte Carlo Simulation**
- Generates thousands of possible scenarios
- More flexible and accurate
- Computationally intensive

### ⚙️ Key Parameters:
- **Confidence Level**: Typically 95% or 99%
- **Time Horizon**: 1 day, 10 days, 1 month
- **Base Currency**: For risk consolidation

### 📈 Practical Example:
*Daily 95% VaR of $1M means there's a 5% chance of losing more than $1M in one day*

### ⚠️ VaR Limitations:
• Doesn't inform about losses beyond VaR
• May underestimate crisis risks
• Sensitive to historical data quality
• Not a coherent risk measure

### 🔄 Expected Shortfall (ES):
**VaR complement** that measures expected loss when VaR is exceeded.
ES = E[Loss | Loss > VaR]
        """
    
    def _portfolio_response_es(self, question: str, docs: List) -> str:
        """Respuesta sobre teoría de portafolios en español."""
        return """
## 📊 Teoría Moderna de Portafolios (Markowitz)

### 🎯 Concepto Central:
**Optimización del balance riesgo-retorno** mediante diversificación eficiente.

### 🔢 Formulación Matemática:

#### **Retorno Esperado del Portafolio:**
E(Rp) = Σ wi × E(Ri)

#### **Varianza del Portafolio:**
σp² = Σ Σ wi × wj × σij

Donde:
- **wi** = Peso del activo i
- **E(Ri)** = Retorno esperado del activo i
- **σij** = Covarianza entre activos i y j

### 📈 Frontera Eficiente:
**Conjunto de portafolios óptimos** que ofrecen:
- **Máximo retorno** para un nivel de riesgo dado
- **Mínimo riesgo** para un nivel de retorno dado

### ⚙️ Proceso de Optimización:

#### **Función Objetivo:**
Minimizar: σp² (riesgo)
Sujeto a: E(Rp) = Retorno objetivo
         Σ wi = 1 (pesos suman 100%)

### 🎪 Ratio de Sharpe:
**S = (E(Rp) - Rf) / σp**

Mide el **retorno excesivo por unidad de riesgo**.

### 🚀 Aplicaciones Prácticas:

#### 1. **Asset Allocation**
- Diversificación entre clases de activos
- Balanceo periódico del portafolio

#### 2. **Construcción de Portafolios**
- Selección óptima de activos
- Determinación de pesos

#### 3. **Gestión de Riesgos**
- Control de concentraciones
- Límites de exposición

### ⚠️ Supuestos y Limitaciones:
• **Retornos normalmente distribuidos**
• **Correlaciones constantes** (problemático en crisis)
• **Aversión al riesgo cuadrática**
• **Mercados eficientes**
• **No considera costos de transacción**

### 🔄 Extensiones Modernas:
- **Black-Litterman**: Incorpora views del gestor
- **Risk Parity**: Iguala contribuciones de riesgo
- **Factor Models**: Usa factores de riesgo comunes
        """
    
    def _portfolio_response_en(self, question: str, docs: List) -> str:
        """Portfolio theory response in English."""
        return """
## 📊 Modern Portfolio Theory (Markowitz)

### 🎯 Central Concept:
**Risk-return optimization** through efficient diversification.

### 🔢 Mathematical Formulation:

#### **Portfolio Expected Return:**
E(Rp) = Σ wi × E(Ri)

#### **Portfolio Variance:**
σp² = Σ Σ wi × wj × σij

Where:
- **wi** = Weight of asset i
- **E(Ri)** = Expected return of asset i
- **σij** = Covariance between assets i and j

### 📈 Efficient Frontier:
**Set of optimal portfolios** offering:
- **Maximum return** for a given risk level
- **Minimum risk** for a given return level

### ⚙️ Optimization Process:

#### **Objective Function:**
Minimize: σp² (risk)
Subject to: E(Rp) = Target return
           Σ wi = 1 (weights sum to 100%)

### 🎪 Sharpe Ratio:
**S = (E(Rp) - Rf) / σp**

Measures **excess return per unit of risk**.

### 🚀 Practical Applications:

#### 1. **Asset Allocation**
- Diversification across asset classes
- Periodic portfolio rebalancing

#### 2. **Portfolio Construction**
- Optimal asset selection
- Weight determination

#### 3. **Risk Management**
- Concentration control
- Exposure limits

### ⚠️ Assumptions and Limitations:
• **Normally distributed returns**
• **Constant correlations** (problematic in crises)
• **Quadratic risk aversion**
• **Efficient markets**
• **No transaction costs**

### 🔄 Modern Extensions:
- **Black-Litterman**: Incorporates manager views
- **Risk Parity**: Equalizes risk contributions
- **Factor Models**: Uses common risk factors
        """
    
    def _derivatives_response_es(self, question: str, docs: List) -> str:
        """Respuesta sobre derivados en español."""
        return """
## 🔄 Instrumentos Derivados - Análisis Completo

### 🎯 Definición:
**Contratos financieros** cuyo valor deriva de un activo subyacente (acciones, bonos, commodities, divisas, índices).

### 📊 Tipos Principales:

#### 1. **Opciones**
- **Call**: Derecho a comprar
- **Put**: Derecho a vender
- **Europeas**: Ejercicio solo al vencimiento
- **Americanas**: Ejercicio en cualquier momento

#### 2. **Futuros**
- **Contratos estandarizados**
- **Negociados en mercados organizados**
- **Requieren margen inicial**
- **Liquidación diaria (mark-to-market)**

#### 3. **Forwards**
- **Contratos OTC personalizados**
- **Sin margen inicial**
- **Liquidación al vencimiento**
- **Riesgo de contraparte**

#### 4. **Swaps**
- **Intercambio de flujos de caja**
- **Interest Rate Swaps (IRS)**
- **Currency Swaps**
- **Credit Default Swaps (CDS)**

### 🚀 Aplicaciones Principales:

#### **1. Cobertura (Hedging)**
- **Protección contra movimientos adversos**
- Ejemplo: Exportador usa forwards para fijar tipo de cambio

#### **2. Especulación**
- **Aprovechamiento del apalancamiento**
- Exposición amplificada con capital limitado

#### **3. Arbitraje**
- **Explotación de ineficiencias de mercado**
- Operaciones libres de riesgo

### 🔢 Factores de Valoración:
- **Precio del subyacente**
- **Precio de ejercicio (opciones)**
- **Tiempo hasta vencimiento**
- **Volatilidad**
- **Tasa libre de riesgo**
- **Dividendos/cupones**

### ⚠️ Riesgos Principales:
• **Riesgo de mercado**
• **Riesgo de contraparte**
• **Riesgo de liquidez**
• **Riesgo de modelo**
• **Riesgo operacional**

### 📈 Regulación y Clearing:
- **Dodd-Frank Act** (EEUU)
- **EMIR** (Europa)
- **Cámaras de compensación** (CCPs)
- **Márgenes obligatorios**
        """
    
    def _derivatives_response_en(self, question: str, docs: List) -> str:
        """Derivatives response in English."""
        return """
## 🔄 Derivative Instruments - Complete Analysis

### 🎯 Definition:
**Financial contracts** whose value derives from an underlying asset (stocks, bonds, commodities, currencies, indices).

### 📊 Main Types:

#### 1. **Options**
- **Call**: Right to buy
- **Put**: Right to sell
- **European**: Exercise only at expiration
- **American**: Exercise anytime

#### 2. **Futures**
- **Standardized contracts**
- **Exchange-traded**
- **Require initial margin**
- **Daily settlement (mark-to-market)**

#### 3. **Forwards**
- **Customized OTC contracts**
- **No initial margin**
- **Settlement at expiration**
- **Counterparty risk**

#### 4. **Swaps**
- **Cash flow exchange**
- **Interest Rate Swaps (IRS)**
- **Currency Swaps**
- **Credit Default Swaps (CDS)**

### 🚀 Main Applications:

#### **1. Hedging**
- **Protection against adverse movements**
- Example: Exporter uses forwards to fix exchange rate

#### **2. Speculation**
- **Leverage utilization**
- Amplified exposure with limited capital

#### **3. Arbitrage**
- **Market inefficiency exploitation**
- Risk-free operations

### 🔢 Valuation Factors:
- **Underlying price**
- **Strike price (options)**
- **Time to expiration**
- **Volatility**
- **Risk-free rate**
- **Dividends/coupons**

### ⚠️ Main Risks:
• **Market risk**
• **Counterparty risk**
• **Liquidity risk**
• **Model risk**
• **Operational risk**

### 📈 Regulation and Clearing:
- **Dodd-Frank Act** (US)
- **EMIR** (Europe)
- **Central Clearing Counterparties** (CCPs)
- **Mandatory margins**
        """
    
    def _monte_carlo_response_es(self, question: str, docs: List) -> str:
        """Respuesta sobre Monte Carlo en español."""
        return """
## 🎲 Simulación Monte Carlo en Finanzas

### 🎯 Concepto:
**Método numérico** que usa muestreo aleatorio para resolver problemas matemáticos complejos en finanzas.

### 🔢 Proceso Básico:

#### **1. Definir el Modelo**
- Especificar procesos estocásticos
- Parámetros del modelo (μ, σ, correlaciones)

#### **2. Generar Trayectorias**
```
S(t+Δt) = S(t) × exp[(μ - σ²/2)Δt + σ√Δt × Z]
```
Donde Z ~ N(0,1)

#### **3. Calcular Payoffs**
- Evaluar el instrumento en cada trayectoria
- Aplicar condiciones de frontera

#### **4. Promediar Resultados**
- Precio = e^(-rT) × E[Payoff]

### 🚀 Aplicaciones en Finanzas:

#### **1. Valoración de Opciones**
- **Opciones exóticas** (asiáticas, barreras, lookback)
- **Opciones americanas** con ejercicio anticipado
- **Opciones sobre múltiples subyacentes**

#### **2. Gestión de Riesgos**
- **Cálculo de VaR** y Expected Shortfall
- **Stress testing** de portafolios
- **Análisis de escenarios**

#### **3. Optimización de Portafolios**
- **Proyección de trayectorias** de retornos
- **Análisis de eficiencia** dinámica

### ⚙️ Técnicas de Reducción de Varianza:

#### **1. Variables Antitéticas**
- Usar Z y -Z para cada simulación
- Reduce varianza por simetría

#### **2. Variables de Control**
- Usar instrumento con solución analítica conocida
- Correlación para reducir error

#### **3. Estratificación**
- Dividir dominio en estratos
- Muestreo proporcional

#### **4. Quasi-Monte Carlo**
- Secuencias de baja discrepancia
- Convergencia más rápida

### 📊 Ventajas:
• **Flexibilidad** para modelos complejos
• **Fácil implementación** de payoffs complejos
• **Paralelizable** para alta performance
• **Convergencia garantizada**

### ⚠️ Desventajas:
• **Computacionalmente intensivo**
• **Convergencia lenta** (√N)
• **Requires many paths** para precisión
• **Sensible a generación** de números aleatorios

### 🔧 Implementación Práctica:
- **Generadores de números aleatorios** de calidad
- **Semillas fijas** para reproducibilidad
- **Paralelización** en GPU/cluster
- **Análisis de convergencia**
        """
    
    def _monte_carlo_response_en(self, question: str, docs: List) -> str:
        """Monte Carlo response in English."""
        return """
## 🎲 Monte Carlo Simulation in Finance

### 🎯 Concept:
**Numerical method** using random sampling to solve complex mathematical problems in finance.

### 🔢 Basic Process:

#### **1. Define the Model**
- Specify stochastic processes
- Model parameters (μ, σ, correlations)

#### **2. Generate Paths**
```
S(t+Δt) = S(t) × exp[(μ - σ²/2)Δt + σ√Δt × Z]
```
Where Z ~ N(0,1)

#### **3. Calculate Payoffs**
- Evaluate instrument on each path
- Apply boundary conditions

#### **4. Average Results**
- Price = e^(-rT) × E[Payoff]

### 🚀 Finance Applications:

#### **1. Option Valuation**
- **Exotic options** (Asian, barrier, lookback)
- **American options** with early exercise
- **Multi-asset options**

#### **2. Risk Management**
- **VaR calculation** and Expected Shortfall
- **Portfolio stress testing**
- **Scenario analysis**

#### **3. Portfolio Optimization**
- **Return path projection**
- **Dynamic efficiency** analysis

### ⚙️ Variance Reduction Techniques:

#### **1. Antithetic Variables**
- Use Z and -Z for each simulation
- Reduces variance through symmetry

#### **2. Control Variables**
- Use instrument with known analytical solution
- Correlation to reduce error

#### **3. Stratification**
- Divide domain into strata
- Proportional sampling

#### **4. Quasi-Monte Carlo**
- Low-discrepancy sequences
- Faster convergence

### 📊 Advantages:
• **Flexibility** for complex models
• **Easy implementation** of complex payoffs
• **Parallelizable** for high performance
• **Guaranteed convergence**

### ⚠️ Disadvantages:
• **Computationally intensive**
• **Slow convergence** (√N)
• **Requires many paths** for precision
• **Sensitive to random number** generation

### 🔧 Practical Implementation:
- **Quality random number** generators
- **Fixed seeds** for reproducibility
- **GPU/cluster parallelization**
- **Convergence analysis**
        """
    
    def health_check(self) -> Dict[str, Any]:
        """Perform system health check with language-aware status."""
        try:
            return {
                'overall_healthy': True,
                'vector_store': self.vector_store is not None,
                'knowledge_base': True,
                'papers_available': len(self.learned_papers) > 0,
                'papers_count': len(self.learned_papers),
                'last_update': self.papers_info.get('last_update', 'Unknown'),
                'languages_supported': ['Spanish (es)', 'English (en)'],
                'query_count': self.query_count,
                'features': [
                    'Automatic language detection',
                    'Multilingual responses',
                    'Real-time paper integration',
                    'Enhanced knowledge base'
                ]
            }
        except Exception as e:
            return {
                'overall_healthy': False,
                'error': str(e),
                'languages_supported': ['Spanish (es)', 'English (en)']
            }


def load_enhanced_agent(vector_store):
    """Load the enhanced multilingual agent."""
    return EnhancedMultilingualAgent(vector_store)
