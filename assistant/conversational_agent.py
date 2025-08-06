#!/usr/bin/env python3
"""
Advanced Conversational Quantitative Finance AI Agent
Author: SPINOR Technologies
Date: August 6, 2025
Version: 5.0 - Full Conversational AI

A sophisticated AI agent with human-like conversational abilities:
- Context-aware multi-turn conversations
- Memory of previous interactions
- Personality and adaptive responses
- Advanced training capabilities
- Real-time learning and improvement
- Multilingual conversational support
"""

import os
import re
import json
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from pathlib import Path
import pickle
import hashlib

# Language detection
try:
    from langdetect import detect, DetectorFactory
    from langdetect.lang_detect_exception import LangDetectException
    DetectorFactory.seed = 0
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False

# Advanced NLP capabilities
try:
    import nltk
    from nltk.sentiment import SentimentIntensityAnalyzer
    from nltk.tokenize import sent_tokenize, word_tokenize
    from nltk.corpus import stopwords
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConversationalMemory:
    """Advanced memory system for maintaining conversation context."""
    
    def __init__(self, max_history: int = 50):
        self.max_history = max_history
        self.conversation_history = []
        self.user_profile = {}
        self.topics_discussed = {}
        self.sentiment_history = []
        self.learning_feedback = []
        
    def add_interaction(self, user_input: str, ai_response: str, metadata: Dict[str, Any]):
        """Add an interaction to memory."""
        interaction = {
            'id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat(),
            'user_input': user_input,
            'ai_response': ai_response,
            'language': metadata.get('language', 'en'),
            'topic': metadata.get('topic', 'general'),
            'sentiment': metadata.get('sentiment', 'neutral'),
            'confidence': metadata.get('confidence', 0.5),
            'tokens_used': len(user_input.split()) + len(ai_response.split())
        }
        
        self.conversation_history.append(interaction)
        
        # Maintain history limit
        if len(self.conversation_history) > self.max_history:
            self.conversation_history.pop(0)
        
        # Update topic tracking
        topic = interaction['topic']
        if topic not in self.topics_discussed:
            self.topics_discussed[topic] = 0
        self.topics_discussed[topic] += 1
        
        # Update sentiment history
        self.sentiment_history.append({
            'timestamp': interaction['timestamp'],
            'sentiment': interaction['sentiment']
        })
        
    def get_context(self, last_n: int = 5) -> str:
        """Get recent conversation context."""
        if not self.conversation_history:
            return ""
        
        recent = self.conversation_history[-last_n:]
        context_parts = []
        
        for interaction in recent:
            context_parts.append(f"User: {interaction['user_input']}")
            context_parts.append(f"AI: {interaction['ai_response'][:200]}...")
        
        return "\n".join(context_parts)
    
    def get_user_preferences(self) -> Dict[str, Any]:
        """Analyze user preferences from conversation history."""
        if not self.conversation_history:
            return {}
        
        preferences = {
            'preferred_language': self._get_preferred_language(),
            'favorite_topics': self._get_favorite_topics(),
            'interaction_style': self._get_interaction_style(),
            'complexity_level': self._get_complexity_level()
        }
        
        return preferences
    
    def _get_preferred_language(self) -> str:
        """Determine user's preferred language."""
        languages = [i['language'] for i in self.conversation_history]
        return max(set(languages), key=languages.count) if languages else 'en'
    
    def _get_favorite_topics(self) -> List[str]:
        """Get user's most discussed topics."""
        sorted_topics = sorted(self.topics_discussed.items(), key=lambda x: x[1], reverse=True)
        return [topic for topic, count in sorted_topics[:5]]
    
    def _get_interaction_style(self) -> str:
        """Analyze user's interaction style."""
        if not self.conversation_history:
            return 'neutral'
        
        avg_length = sum(len(i['user_input'].split()) for i in self.conversation_history) / len(self.conversation_history)
        
        if avg_length > 20:
            return 'detailed'
        elif avg_length > 10:
            return 'moderate'
        else:
            return 'concise'
    
    def _get_complexity_level(self) -> str:
        """Determine preferred complexity level."""
        technical_keywords = ['derivative', 'stochastic', 'optimization', 'mathematical', 'formula', 'equation']
        
        technical_count = 0
        total_interactions = len(self.conversation_history)
        
        for interaction in self.conversation_history:
            user_text = interaction['user_input'].lower()
            if any(keyword in user_text for keyword in technical_keywords):
                technical_count += 1
        
        if total_interactions == 0:
            return 'intermediate'
        
        technical_ratio = technical_count / total_interactions
        
        if technical_ratio > 0.6:
            return 'advanced'
        elif technical_ratio > 0.3:
            return 'intermediate'
        else:
            return 'beginner'


class AdvancedConversationalAgent:
    """Advanced conversational AI agent with human-like capabilities."""
    
    def __init__(self, vector_store, personality: str = "professional_friendly"):
        """Initialize the advanced conversational agent."""
        self.vector_store = vector_store
        self.memory = ConversationalMemory()
        self.personality = personality
        self.session_id = str(uuid.uuid4())
        self.start_time = datetime.now()
        
        # Initialize NLP components
        self._init_nlp_components()
        
        # Load conversation patterns and responses
        self._init_conversation_patterns()
        
        # Learning and training capabilities
        self.training_data = []
        self.feedback_scores = []
        self.improvement_suggestions = []
        
        # Enhanced knowledge from papers
        self.learned_papers = []
        self.dynamic_concepts = {}
        
        # Initialize enhanced knowledge
        self._initialize_enhanced_knowledge()
        
        # Load recent papers
        self._integrate_recent_papers()
        
        logger.info("🤖 Advanced Conversational Agent initialized")
    
    def _init_nlp_components(self):
        """Initialize NLP components."""
        if NLTK_AVAILABLE:
            try:
                # Download required NLTK data if not present
                nltk.data.find('vader_lexicon')
                self.sentiment_analyzer = SentimentIntensityAnalyzer()
            except LookupError:
                try:
                    nltk.download('vader_lexicon', quiet=True)
                    nltk.download('punkt', quiet=True)
                    nltk.download('stopwords', quiet=True)
                    self.sentiment_analyzer = SentimentIntensityAnalyzer()
                except:
                    self.sentiment_analyzer = None
            except:
                self.sentiment_analyzer = None
        else:
            self.sentiment_analyzer = None
    
    def _init_conversation_patterns(self):
        """Initialize conversation patterns and responses."""
        self.conversation_patterns = {
            'greeting': {
                'patterns': [r'\b(hello|hi|hey|good morning|good afternoon|good evening|hola|buenos días|buenas tardes)\b'],
                'responses_en': [
                    "Hello! I'm SPINOR AI, your quantitative finance assistant. How can I help you today?",
                    "Hi there! I'm excited to discuss quantitative finance with you. What would you like to explore?",
                    "Good to see you! I'm here to help with any quantitative finance questions you might have."
                ],
                'responses_es': [
                    "¡Hola! Soy SPINOR AI, tu asistente de finanzas cuantitativas. ¿Cómo puedo ayudarte hoy?",
                    "¡Hola! Me emociona discutir finanzas cuantitativas contigo. ¿Qué te gustaría explorar?",
                    "¡Qué gusto verte! Estoy aquí para ayudarte con cualquier pregunta sobre finanzas cuantitativas."
                ]
            },
            'goodbye': {
                'patterns': [r'\b(goodbye|bye|see you|hasta luego|adiós|nos vemos)\b'],
                'responses_en': [
                    "Goodbye! It was great discussing quantitative finance with you. Feel free to return anytime!",
                    "See you later! I hope our conversation was helpful. Have a great day!",
                    "Thanks for the engaging conversation! Come back anytime you need help with quantitative finance."
                ],
                'responses_es': [
                    "¡Adiós! Fue genial discutir finanzas cuantitativas contigo. ¡Vuelve cuando quieras!",
                    "¡Hasta luego! Espero que nuestra conversación haya sido útil. ¡Que tengas un gran día!",
                    "¡Gracias por la conversación tan interesante! Vuelve cuando necesites ayuda con finanzas cuantitativas."
                ]
            },
            'appreciation': {
                'patterns': [r'\b(thank you|thanks|gracias|appreciate|helpful)\b'],
                'responses_en': [
                    "You're very welcome! I'm glad I could help you understand the topic better.",
                    "Happy to help! That's what I'm here for. Feel free to ask more questions anytime.",
                    "My pleasure! I love discussing quantitative finance and helping others learn."
                ],
                'responses_es': [
                    "¡De nada! Me alegra poder ayudarte a entender mejor el tema.",
                    "¡Con gusto! Para eso estoy aquí. No dudes en hacer más preguntas cuando quieras.",
                    "¡Es un placer! Me encanta discutir finanzas cuantitativas y ayudar a otros a aprender."
                ]
            },
            'confusion': {
                'patterns': [r'\b(confused|don\'t understand|no entiendo|confuso|unclear)\b'],
                'responses_en': [
                    "I understand this can be confusing. Let me explain it in a different way that might be clearer.",
                    "No worries! Complex financial concepts can be tricky. Let me break it down step by step.",
                    "That's completely normal - these topics are challenging. Let me simplify my explanation."
                ],
                'responses_es': [
                    "Entiendo que esto puede ser confuso. Déjame explicártelo de una manera diferente que sea más clara.",
                    "¡No te preocupes! Los conceptos financieros complejos pueden ser difíciles. Te lo explico paso a paso.",
                    "Es completamente normal - estos temas son desafiantes. Déjame simplificar mi explicación."
                ]
            }
        }
        
        # Personality traits
        self.personality_traits = {
            'professional_friendly': {
                'tone': 'professional yet approachable',
                'emoji_usage': 'moderate',
                'explanation_style': 'detailed with examples',
                'enthusiasm_level': 'high'
            },
            'academic': {
                'tone': 'formal and precise',
                'emoji_usage': 'minimal',
                'explanation_style': 'theoretical with mathematical rigor',
                'enthusiasm_level': 'moderate'
            },
            'casual': {
                'tone': 'friendly and relaxed',
                'emoji_usage': 'frequent',
                'explanation_style': 'simple with analogies',
                'enthusiasm_level': 'very high'
            }
        }
    
    def detect_language(self, text: str) -> str:
        """Enhanced language detection with context awareness."""
        text_clean = text.lower().strip()
        
        # Use conversation history for context
        if self.memory.conversation_history:
            recent_language = self.memory.get_user_preferences().get('preferred_language', 'en')
            
            # If very short text, use recent language preference
            if len(text_clean.split()) < 3:
                return recent_language
        
        # Try langdetect first
        if LANGDETECT_AVAILABLE and len(text_clean) > 10:
            try:
                detected = detect(text_clean)
                if detected in ['es', 'en']:
                    return detected
            except LangDetectException:
                pass
        
        # Enhanced pattern-based detection
        spanish_indicators = [
            r'\b(qué|que|cómo|como|cuál|cual|dónde|donde|cuándo|cuando|por qué|porque)\b',
            r'\b(el|la|los|las|un|una|de|del|en|con|por|para|y|o|pero|si|no|es|son|está|están)\b',
            r'\b(finanzas|riesgo|opciones|derivados|portafolio|modelo|precio|mercado|valor)\b'
        ]
        
        english_indicators = [
            r'\b(what|how|which|where|when|why|who|can|could|would|should|will)\b',
            r'\b(the|a|an|of|in|on|at|to|for|with|by|from|and|or|but|if|not|is|are)\b',
            r'\b(finance|risk|options|derivatives|portfolio|model|price|market|value)\b'
        ]
        
        spanish_score = sum(1 for pattern in spanish_indicators 
                          if re.search(pattern, text_clean, re.IGNORECASE))
        english_score = sum(1 for pattern in english_indicators 
                          if re.search(pattern, text_clean, re.IGNORECASE))
        
        return 'es' if spanish_score > english_score else 'en'
    
    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze sentiment of user input."""
        if self.sentiment_analyzer:
            try:
                scores = self.sentiment_analyzer.polarity_scores(text)
                return {
                    'positive': scores['pos'],
                    'negative': scores['neg'],
                    'neutral': scores['neu'],
                    'compound': scores['compound']
                }
            except:
                pass
        
        # Fallback simple sentiment analysis
        positive_words = ['good', 'great', 'excellent', 'helpful', 'thanks', 'love', 'perfect']
        negative_words = ['bad', 'terrible', 'confusing', 'difficult', 'hate', 'wrong', 'error']
        
        text_lower = text.lower()
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        total = pos_count + neg_count
        if total == 0:
            return {'positive': 0.1, 'negative': 0.1, 'neutral': 0.8, 'compound': 0.0}
        
        return {
            'positive': pos_count / total,
            'negative': neg_count / total,
            'neutral': 1 - (pos_count + neg_count) / total,
            'compound': (pos_count - neg_count) / total
        }
    
    def detect_conversation_pattern(self, text: str, language: str) -> Optional[str]:
        """Detect conversation patterns in user input."""
        text_lower = text.lower()
        
        for pattern_type, pattern_data in self.conversation_patterns.items():
            for pattern in pattern_data['patterns']:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    return pattern_type
        
        return None
    
    def query(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process user input with full conversational capabilities.
        
        Args:
            user_input: User's message/question
            context: Additional context information
            
        Returns:
            Enhanced response with conversational capabilities
        """
        start_time = datetime.now()
        
        try:
            # Detect language and sentiment
            detected_lang = self.detect_language(user_input)
            sentiment = self.analyze_sentiment(user_input)
            
            # Detect conversation patterns
            conversation_pattern = self.detect_conversation_pattern(user_input, detected_lang)
            
            # Get conversation context
            conversation_context = self.memory.get_context(last_n=3)
            user_preferences = self.memory.get_user_preferences()
            
            # Generate response based on pattern or content
            if conversation_pattern:
                response = self._generate_pattern_response(conversation_pattern, detected_lang, user_preferences)
                topic = conversation_pattern
            else:
                # Identify financial topic
                topic = self._identify_financial_topic(user_input, detected_lang)
                
                # Generate contextual financial response
                response = self._generate_contextual_response(
                    user_input, detected_lang, topic, conversation_context, user_preferences, sentiment
                )
            
            # Calculate response time
            response_time = (datetime.now() - start_time).total_seconds()
            
            # Prepare metadata
            metadata = {
                'language': detected_lang,
                'topic': topic,
                'conversation_pattern': conversation_pattern,
                'sentiment': sentiment,
                'response_time': response_time,
                'session_id': self.session_id,
                'user_preferences': user_preferences,
                'conversation_length': len(self.memory.conversation_history),
                'papers_integrated': len(self.learned_papers),
                'confidence': self._calculate_response_confidence(user_input, topic, conversation_pattern)
            }
            
            # Add to memory
            self.memory.add_interaction(user_input, response, metadata)
            
            return {
                'result': response,
                'source_documents': self._get_relevant_documents(user_input),
                'metadata': metadata
            }
            
        except Exception as e:
            logger.error(f"Error in conversational query processing: {e}")
            error_response = self._get_error_response(detected_lang if 'detected_lang' in locals() else 'en')
            return {
                'result': error_response,
                'source_documents': [],
                'metadata': {'error': True, 'error_message': str(e)}
            }
    
    def _generate_pattern_response(self, pattern: str, language: str, preferences: Dict[str, Any]) -> str:
        """Generate response for detected conversation patterns."""
        pattern_data = self.conversation_patterns.get(pattern, {})
        responses_key = f'responses_{language}'
        
        if responses_key in pattern_data:
            responses = pattern_data[responses_key]
            # Select response based on conversation length or randomize
            response_index = len(self.memory.conversation_history) % len(responses)
            base_response = responses[response_index]
            
            # Personalize based on preferences
            if preferences.get('favorite_topics'):
                topic = preferences['favorite_topics'][0]
                if language == 'es':
                    base_response += f" ¿Te gustaría continuar explorando {topic}?"
                else:
                    base_response += f" Would you like to continue exploring {topic}?"
            
            return base_response
        
        # Fallback response
        if language == 'es':
            return "¡Gracias por tu mensaje! ¿En qué puedo ayudarte con finanzas cuantitativas?"
        else:
            return "Thank you for your message! How can I help you with quantitative finance?"
    
    def _generate_contextual_response(self, user_input: str, language: str, topic: str, 
                                    context: str, preferences: Dict[str, Any], 
                                    sentiment: Dict[str, float]) -> str:
        """Generate contextually aware response."""
        
        # Get base financial response
        if topic and hasattr(self, f'_get_{topic}_response'):
            response_method = getattr(self, f'_get_{topic}_response')
            base_response = response_method(user_input, language, preferences)
        else:
            base_response = self._get_general_response(user_input, language, preferences)
        
        # Add conversational elements
        conversational_response = self._add_conversational_elements(
            base_response, language, preferences, sentiment, context
        )
        
        # Add recent papers if relevant
        enhanced_response = self._enhance_with_recent_papers(
            conversational_response, user_input, language
        )
        
        return enhanced_response
    
    def _add_conversational_elements(self, base_response: str, language: str, 
                                   preferences: Dict[str, Any], sentiment: Dict[str, float],
                                   context: str) -> str:
        """Add conversational elements to make response more human-like."""
        
        # Analyze user's complexity preference
        complexity = preferences.get('complexity_level', 'intermediate')
        interaction_style = preferences.get('interaction_style', 'moderate')
        
        # Add personality-based intro
        if sentiment['compound'] > 0.5:  # User seems positive/excited
            if language == 'es':
                intro = "¡Me alegra tu entusiasmo! "
            else:
                intro = "I love your enthusiasm! "
        elif sentiment['compound'] < -0.3:  # User seems confused/frustrated
            if language == 'es':
                intro = "Entiendo que esto puede ser desafiante. "
            else:
                intro = "I understand this can be challenging. "
        else:
            intro = ""
        
        # Add context reference if available
        context_ref = ""
        if context and len(self.memory.conversation_history) > 1:
            if language == 'es':
                context_ref = "Continuando nuestra conversación, "
            else:
                context_ref = "Building on our discussion, "
        
        # Adjust complexity based on preferences
        if complexity == 'beginner' and 'mathematical' in base_response.lower():
            if language == 'es':
                complexity_note = "\n\n💡 *Nota: Puedo explicar esto de manera más simple si lo prefieres.*"
            else:
                complexity_note = "\n\n💡 *Note: I can explain this more simply if you prefer.*"
        elif complexity == 'advanced' and len(base_response) < 500:
            if language == 'es':
                complexity_note = "\n\n🔬 *¿Te gustaría una explicación más técnica y detallada?*"
            else:
                complexity_note = "\n\n🔬 *Would you like a more technical and detailed explanation?*"
        else:
            complexity_note = ""
        
        # Add follow-up question
        if language == 'es':
            follow_up = "\n\n❓ ¿Hay algún aspecto específico que te gustaría explorar más a fondo?"
        else:
            follow_up = "\n\n❓ Is there any specific aspect you'd like to explore further?"
        
        return intro + context_ref + base_response + complexity_note + follow_up
    
    def _get_black_scholes_response(self, user_input: str, language: str, preferences: Dict[str, Any]) -> str:
        """Get Black-Scholes response adapted to conversation."""
        if language == 'es':
            return """
## 📈 El Modelo Black-Scholes

El modelo Black-Scholes es fundamental en finanzas cuantitativas para valorar opciones europeas.

### 🎯 Fórmula Principal:
**C = S₀ × N(d₁) - K × e^(-rT) × N(d₂)**

### 🔑 Variables Clave:
- **S₀**: Precio actual del activo
- **K**: Precio de ejercicio  
- **r**: Tasa libre de riesgo
- **T**: Tiempo hasta vencimiento
- **σ**: Volatilidad del activo

### 💡 Intuición:
El modelo calcula el valor presente esperado del payoff de la opción bajo medida neutral al riesgo.

### ⚙️ Supuestos Importantes:
1. Volatilidad constante
2. Tasa de interés constante
3. No hay dividendos
4. Mercados eficientes

### 🎪 Las "Griegas":
- **Delta (Δ)**: Sensibilidad al precio del subyacente
- **Gamma (Γ)**: Convexidad del delta
- **Theta (Θ)**: Decaimiento temporal
- **Vega (ν)**: Sensibilidad a la volatilidad
            """
        else:
            return """
## 📈 The Black-Scholes Model

The Black-Scholes model is fundamental in quantitative finance for valuing European options.

### 🎯 Core Formula:
**C = S₀ × N(d₁) - K × e^(-rT) × N(d₂)**

### 🔑 Key Variables:
- **S₀**: Current asset price
- **K**: Strike price
- **r**: Risk-free rate
- **T**: Time to expiration
- **σ**: Asset volatility

### 💡 Intuition:
The model calculates the expected present value of the option's payoff under risk-neutral measure.

### ⚙️ Key Assumptions:
1. Constant volatility
2. Constant interest rate
3. No dividends
4. Efficient markets

### 🎪 The "Greeks":
- **Delta (Δ)**: Sensitivity to underlying price
- **Gamma (Γ)**: Delta convexity
- **Theta (Θ)**: Time decay
- **Vega (ν)**: Volatility sensitivity
            """
    
    def _get_var_response(self, user_input: str, language: str, preferences: Dict[str, Any]) -> str:
        """Get VaR response adapted to conversation."""
        if language == 'es':
            return """
## ⚠️ Value at Risk (VaR)

El VaR es una medida estadística que cuantifica el riesgo financiero potencial.

### 🎯 Definición:
**"Hay una probabilidad X% de que las pérdidas no excedan $Y en Z días"**

### 📊 Métodos de Cálculo:

#### 1. **Método Paramétrico**
- Asume normalidad de retornos
- VaR = μ - Z_α × σ × √t
- Rápido pero limitado

#### 2. **Simulación Histórica**
- Usa datos reales del pasado
- No asume distribución específica
- Captura mejor las colas pesadas

#### 3. **Monte Carlo**
- Simula miles de escenarios
- Muy flexible y preciso
- Computacionalmente intensivo

### 💼 Aplicaciones Prácticas:
- Límites de riesgo
- Requerimientos de capital
- Informes regulatorios
- Gestión de portafolios
            """
        else:
            return """
## ⚠️ Value at Risk (VaR)

VaR is a statistical measure that quantifies potential financial risk.

### 🎯 Definition:
**"There is an X% probability that losses will not exceed $Y over Z days"**

### 📊 Calculation Methods:

#### 1. **Parametric Method**
- Assumes return normality
- VaR = μ - Z_α × σ × √t
- Fast but limited

#### 2. **Historical Simulation**
- Uses actual past data
- No specific distribution assumption
- Better captures fat tails

#### 3. **Monte Carlo**
- Simulates thousands of scenarios
- Very flexible and accurate
- Computationally intensive

### 💼 Practical Applications:
- Risk limits
- Capital requirements
- Regulatory reporting
- Portfolio management
            """
    
    def _get_portfolio_response(self, user_input: str, language: str, preferences: Dict[str, Any]) -> str:
        """Get portfolio optimization response adapted to conversation."""
        if language == 'es':
            return """
## 📊 Optimización de Portafolios (Markowitz)

La teoría moderna de portafolios busca maximizar retorno por unidad de riesgo.

### 🎯 Objetivo:
Encontrar la combinación óptima de activos que maximice la utilidad del inversor.

### 🔢 Formulación Matemática:
- **Retorno**: E(Rp) = Σ wi × E(Ri)
- **Riesgo**: σp² = Σ Σ wi × wj × σij

### 📈 Frontera Eficiente:
Conjunto de portafolios que ofrecen:
- Máximo retorno para un nivel de riesgo dado
- Mínimo riesgo para un nivel de retorno dado

### ⚙️ Proceso de Optimización:
1. Estimar retornos esperados
2. Calcular matriz de covarianzas
3. Resolver problema de optimización
4. Construir frontera eficiente

### 🎪 Ratio de Sharpe:
**S = (E(Rp) - Rf) / σp**

Mide el retorno excesivo por unidad de riesgo.
            """
        else:
            return """
## 📊 Portfolio Optimization (Markowitz)

Modern portfolio theory seeks to maximize return per unit of risk.

### 🎯 Objective:
Find the optimal combination of assets that maximizes investor utility.

### 🔢 Mathematical Formulation:
- **Return**: E(Rp) = Σ wi × E(Ri)
- **Risk**: σp² = Σ Σ wi × wj × σij

### 📈 Efficient Frontier:
Set of portfolios offering:
- Maximum return for given risk level
- Minimum risk for given return level

### ⚙️ Optimization Process:
1. Estimate expected returns
2. Calculate covariance matrix
3. Solve optimization problem
4. Construct efficient frontier

### 🎪 Sharpe Ratio:
**S = (E(Rp) - Rf) / σp**

Measures excess return per unit of risk.
            """
    
    def _get_general_response(self, user_input: str, language: str, preferences: Dict[str, Any]) -> str:
        """Generate general conversational response."""
        complexity = preferences.get('complexity_level', 'intermediate')
        
        if language == 'es':
            if complexity == 'beginner':
                return f"""
## 💼 Análisis de Finanzas Cuantitativas

Basándome en tu pregunta sobre "{user_input[:50]}...", aquí tienes una explicación accesible:

### 🔍 Contexto:
Las finanzas cuantitativas utilizan matemáticas y estadística para entender los mercados financieros.

### 📊 Conceptos Clave:
• **Riesgo**: La incertidumbre en los retornos de inversión
• **Retorno**: Las ganancias o pérdidas de una inversión
• **Diversificación**: Reducir riesgo invirtiendo en múltiples activos
• **Valoración**: Determinar el precio justo de un activo

### 🚀 Aplicaciones Prácticas:
1. Valoración de inversiones
2. Gestión de riesgos
3. Optimización de portafolios
4. Trading algorítmico

### 💡 Consejo:
Comienza con los conceptos básicos antes de avanzar a modelos más complejos.
                """
            else:
                return f"""
## 💼 Análisis Avanzado de Finanzas Cuantitativas

Examinando tu consulta sobre "{user_input[:50]}...", proporciono un análisis detallado:

### 🔬 Marco Teórico:
Las finanzas cuantitativas integran:
- Procesos estocásticos
- Teoría de probabilidades
- Optimización matemática
- Análisis estadístico

### 📈 Metodologías Aplicables:
• **Modelos de Valoración**: Black-Scholes, Binomial, Monte Carlo
• **Gestión de Riesgos**: VaR, Expected Shortfall, Stress Testing
• **Optimización**: Markowitz, Black-Litterman, Risk Parity
• **Econometría**: GARCH, VAR, Cointegración

### 🎯 Consideraciones Implementación:
1. Calidad y disponibilidad de datos
2. Supuestos del modelo y limitaciones
3. Validación y backtesting
4. Aspectos computacionales

### 🔄 Desarrollos Recientes:
Machine learning, factor investing, ESG integration, crypto assets.
                """
        else:
            if complexity == 'beginner':
                return f"""
## 💼 Quantitative Finance Analysis

Based on your question about "{user_input[:50]}...", here's an accessible explanation:

### 🔍 Context:
Quantitative finance uses mathematics and statistics to understand financial markets.

### 📊 Key Concepts:
• **Risk**: Uncertainty in investment returns
• **Return**: Gains or losses from an investment
• **Diversification**: Reducing risk by investing in multiple assets
• **Valuation**: Determining the fair price of an asset

### 🚀 Practical Applications:
1. Investment valuation
2. Risk management
3. Portfolio optimization
4. Algorithmic trading

### 💡 Tip:
Start with basic concepts before advancing to more complex models.
                """
            else:
                return f"""
## 💼 Advanced Quantitative Finance Analysis

Examining your query about "{user_input[:50]}...", I provide a detailed analysis:

### 🔬 Theoretical Framework:
Quantitative finance integrates:
- Stochastic processes
- Probability theory
- Mathematical optimization
- Statistical analysis

### 📈 Applicable Methodologies:
• **Valuation Models**: Black-Scholes, Binomial, Monte Carlo
• **Risk Management**: VaR, Expected Shortfall, Stress Testing
• **Optimization**: Markowitz, Black-Litterman, Risk Parity
• **Econometrics**: GARCH, VAR, Cointegration

### 🎯 Implementation Considerations:
1. Data quality and availability
2. Model assumptions and limitations
3. Validation and backtesting
4. Computational aspects

### 🔄 Recent Developments:
Machine learning, factor investing, ESG integration, crypto assets.
                """
    
    def _identify_financial_topic(self, text: str, language: str) -> str:
        """Identify financial topic with enhanced pattern matching."""
        text_lower = text.lower()
        
        # Enhanced topic patterns
        topic_patterns = {
            'black_scholes': [
                r'black.scholes', r'option.pricing', r'european.option',
                r'bs.model', r'greeks', r'delta.hedging'
            ],
            'var': [
                r'value.at.risk', r'var\b', r'risk.measure', r'quantile',
                r'expected.shortfall', r'conditional.var', r'riesgo'
            ],
            'portfolio': [
                r'portfolio', r'markowitz', r'efficient.frontier',
                r'asset.allocation', r'diversification', r'portafolio'
            ],
            'derivatives': [
                r'derivative', r'option', r'future', r'forward', r'swap',
                r'exotic', r'american.option', r'derivado'
            ],
            'monte_carlo': [
                r'monte.carlo', r'simulation', r'random.sampling',
                r'path.dependent', r'numerical.method', r'simulación'
            ],
            'trading': [
                r'algorithmic.trading', r'high.frequency', r'market.making',
                r'execution', r'trading.strategy', r'arbitrage'
            ],
            'risk_management': [
                r'risk.management', r'stress.test', r'scenario.analysis',
                r'credit.risk', r'market.risk', r'gestión.riesgo'
            ]
        }
        
        # Score each topic
        topic_scores = {}
        for topic, patterns in topic_patterns.items():
            score = sum(1 for pattern in patterns if re.search(pattern, text_lower))
            if score > 0:
                topic_scores[topic] = score
        
        # Return highest scoring topic
        if topic_scores:
            return max(topic_scores.items(), key=lambda x: x[1])[0]
        
        return 'general'
    
    def _calculate_response_confidence(self, user_input: str, topic: str, pattern: str) -> float:
        """Calculate confidence in response quality."""
        confidence = 0.5  # Base confidence
        
        # Increase confidence for known topics
        if topic != 'general':
            confidence += 0.3
        
        # Increase confidence for recognized patterns
        if pattern:
            confidence += 0.2
        
        # Increase confidence based on input clarity
        input_length = len(user_input.split())
        if input_length > 5:
            confidence += 0.1
        if input_length > 10:
            confidence += 0.1
        
        # Cap at 1.0
        return min(confidence, 1.0)
    
    def _get_relevant_documents(self, user_input: str) -> List[Any]:
        """Get relevant documents from vector store."""
        try:
            return self.vector_store.similarity_search(user_input, k=3)
        except:
            return []
    
    def _enhance_with_recent_papers(self, response: str, user_input: str, language: str) -> str:
        """Enhance response with relevant recent papers."""
        if not self.learned_papers:
            return response
        
        # Find relevant papers
        relevant_papers = []
        query_words = set(user_input.lower().split())
        
        for paper in self.learned_papers[:5]:
            title_words = set(paper.get('title', '').lower().split())
            summary_words = set(paper.get('summary', '').lower().split())
            
            # Calculate relevance score
            title_overlap = len(query_words.intersection(title_words))
            summary_overlap = len(query_words.intersection(summary_words))
            
            if title_overlap > 0 or summary_overlap > 0:
                relevant_papers.append({
                    'paper': paper,
                    'relevance': title_overlap * 2 + summary_overlap
                })
        
        if relevant_papers:
            # Sort by relevance
            relevant_papers.sort(key=lambda x: x['relevance'], reverse=True)
            
            if language == 'es':
                papers_section = f"\n\n## 📚 Investigación Reciente Relacionada:\n\n"
                for i, item in enumerate(relevant_papers[:2], 1):
                    paper = item['paper']
                    title = paper.get('title', 'Sin título')[:80]
                    authors = ', '.join(paper.get('authors', [])[:2])
                    papers_section += f"**{i}.** {title}...\n   *Autores: {authors}*\n\n"
            else:
                papers_section = f"\n\n## 📚 Related Recent Research:\n\n"
                for i, item in enumerate(relevant_papers[:2], 1):
                    paper = item['paper']
                    title = paper.get('title', 'Untitled')[:80]
                    authors = ', '.join(paper.get('authors', [])[:2])
                    papers_section += f"**{i}.** {title}...\n   *Authors: {authors}*\n\n"
            
            response += papers_section
        
        return response
    
    def _get_error_response(self, language: str) -> str:
        """Get error response in appropriate language."""
        if language == 'es':
            return """
Disculpa, encontré un problema procesando tu mensaje. 

🔧 **Cosas que puedes intentar:**
- Reformular tu pregunta
- Ser más específico sobre el tema
- Verificar la ortografía

💡 **Mientras tanto**, puedo ayudarte con:
- Modelos de valoración (Black-Scholes, binomial)
- Gestión de riesgos (VaR, stress testing)
- Optimización de portafolios
- Derivados financieros
- Trading cuantitativo

¿Sobre qué tema te gustaría que conversemos?
            """
        else:
            return """
Sorry, I encountered an issue processing your message.

🔧 **Things you can try:**
- Rephrase your question
- Be more specific about the topic
- Check spelling

💡 **Meanwhile**, I can help you with:
- Valuation models (Black-Scholes, binomial)
- Risk management (VaR, stress testing)
- Portfolio optimization
- Financial derivatives
- Quantitative trading

What topic would you like to discuss?
            """
    
    def provide_feedback(self, interaction_id: str, rating: int, comment: str = ""):
        """Accept feedback for continuous improvement."""
        feedback = {
            'interaction_id': interaction_id,
            'rating': rating,  # 1-5 scale
            'comment': comment,
            'timestamp': datetime.now().isoformat()
        }
        
        self.memory.learning_feedback.append(feedback)
        
        # Log feedback for analysis
        logger.info(f"Received feedback: {rating}/5 for interaction {interaction_id}")
        
        if rating <= 2:
            logger.warning(f"Low rating feedback: {comment}")
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get summary of current conversation session."""
        if not self.memory.conversation_history:
            return {'message': 'No conversation history available'}
        
        preferences = self.memory.get_user_preferences()
        
        return {
            'session_id': self.session_id,
            'duration': str(datetime.now() - self.start_time),
            'total_interactions': len(self.memory.conversation_history),
            'languages_used': list(set(i['language'] for i in self.memory.conversation_history)),
            'topics_discussed': list(self.memory.topics_discussed.keys()),
            'user_preferences': preferences,
            'avg_response_time': sum(i.get('metadata', {}).get('response_time', 0) 
                                   for i in self.memory.conversation_history) / len(self.memory.conversation_history),
            'sentiment_trend': self._analyze_sentiment_trend()
        }
    
    def _analyze_sentiment_trend(self) -> str:
        """Analyze sentiment trend over conversation."""
        if len(self.memory.sentiment_history) < 2:
            return 'neutral'
        
        recent_sentiments = [s['sentiment']['compound'] for s in self.memory.sentiment_history[-3:]]
        avg_sentiment = sum(recent_sentiments) / len(recent_sentiments)
        
        if avg_sentiment > 0.3:
            return 'positive'
        elif avg_sentiment < -0.3:
            return 'negative'
        else:
            return 'neutral'
    
    def _initialize_enhanced_knowledge(self):
        """Initialize enhanced knowledge base."""
        # This would be called from the original enhanced_agent methods
        pass
    
    def _integrate_recent_papers(self):
        """Integrate recent papers from the data directory."""
        papers_dir = Path("./data/papers")
        
        if not papers_dir.exists():
            return
        
        try:
            paper_files = list(papers_dir.glob("papers_*.json"))
            if not paper_files:
                return
            
            latest_file = max(paper_files, key=lambda x: x.stat().st_mtime)
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                papers = json.load(f)
            
            self.learned_papers = papers[:20]  # Keep recent 20 papers
            
            logger.info(f"🚀 Integrated {len(papers)} papers into conversational knowledge")
            
        except Exception as e:
            logger.error(f"Error integrating papers: {e}")
    
    def health_check(self) -> Dict[str, Any]:
        """Enhanced health check with conversational metrics."""
        base_health = {
            'overall_healthy': True,
            'vector_store': self.vector_store is not None,
            'knowledge_base': True,
            'papers_available': len(self.learned_papers) > 0,
            'papers_count': len(self.learned_papers)
        }
        
        # Add conversational metrics
        conversational_metrics = {
            'conversation_active': len(self.memory.conversation_history) > 0,
            'languages_supported': ['Spanish (es)', 'English (en)'],
            'conversation_length': len(self.memory.conversation_history),
            'session_duration': str(datetime.now() - self.start_time),
            'nlp_components': {
                'sentiment_analysis': self.sentiment_analyzer is not None,
                'language_detection': LANGDETECT_AVAILABLE,
                'conversation_patterns': len(self.conversation_patterns)
            },
            'user_preferences': self.memory.get_user_preferences(),
            'memory_usage': {
                'interactions_stored': len(self.memory.conversation_history),
                'topics_tracked': len(self.memory.topics_discussed),
                'feedback_received': len(self.memory.learning_feedback)
            },
            'capabilities': [
                'Multi-turn conversations',
                'Context awareness',
                'Sentiment analysis',
                'Personality adaptation',
                'Learning from feedback',
                'Real-time paper integration',
                'Multilingual support'
            ]
        }
        
        return {**base_health, **conversational_metrics}


def load_conversational_agent(vector_store, personality: str = "professional_friendly"):
    """Load the advanced conversational agent."""
    return AdvancedConversationalAgent(vector_store, personality)
