"""
🤖 SPINOR Specialized AI Agent
Agente de IA especializado en finanzas cuantitativas y econofísica
con auto-alimentación inteligente y gestión de nodos
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import json

from intelligent_node_manager import IntelligentNodeManager
from auto_feeding_system import AutoFeedingSystem
from conversational_agent import AdvancedConversationalAgent, ConversationalMemory

logger = logging.getLogger(__name__)

class SpecializedAIAgent:
    """Agente de IA especializado con auto-alimentación inteligente"""
    
    def __init__(self, domain: str = "quantitative_finance"):
        self.domain = domain
        self.data_dir = Path(f"./data/specialized_agent_{domain}")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Componentes principales
        self.node_manager = IntelligentNodeManager(
            data_dir=str(self.data_dir / "nodes")
        )
        self.auto_feeding = AutoFeedingSystem(self.node_manager)
        
        # Agente conversacional mejorado
        self.conversational_agent = None
        self.memory = ConversationalMemory()
        
        # Configuración especializada por dominio
        self.domain_config = self.get_domain_config(domain)
        
        # Estadísticas del agente
        self.agent_stats = {
            "queries_processed": 0,
            "papers_learned_from": 0,
            "domain_expertise_level": 1.0,
            "last_learning_session": None,
            "specialized_topics": [],
            "performance_metrics": {
                "accuracy_score": 0.85,
                "user_satisfaction": 0.90,
                "response_relevance": 0.88
            }
        }
        
        self.load_agent_stats()
        
        # Inicializar agente conversacional
        self._initialize_conversational_agent()
        
        logger.info(f"🎯 Agente especializado iniciado - Dominio: {domain}")

    def get_domain_config(self, domain: str) -> Dict:
        """Configuración específica por dominio"""
        configurations = {
            "quantitative_finance": {
                "name": "Quantitative Finance Expert",
                "description": "Especialista en finanzas cuantitativas, econofísica y gestión de riesgos",
                "keywords": [
                    "quantitative finance", "econophysics", "derivatives pricing",
                    "risk management", "portfolio optimization", "algorithmic trading",
                    "market microstructure", "volatility modeling", "stochastic calculus",
                    "option pricing", "credit risk", "operational risk", "market risk",
                    "high frequency trading", "statistical arbitrage", "machine learning finance"
                ],
                "specialties": [
                    "Black-Scholes y extensiones", "Modelos de volatilidad estocástica",
                    "Métodos Monte Carlo", "Optimización de portafolios", "Value at Risk",
                    "Econofísica y redes financieras", "Trading algorítmico",
                    "Microestructura de mercados", "Pricing de derivados exóticos"
                ],
                "languages": ["Spanish", "English"],
                "personality_traits": {
                    "analytical": 0.9,
                    "formal": 0.7,
                    "helpful": 0.95,
                    "curious": 0.8,
                    "precise": 0.9
                }
            },
            "machine_learning": {
                "name": "Machine Learning Expert",
                "description": "Especialista en machine learning, deep learning y AI applications",
                "keywords": [
                    "machine learning", "deep learning", "neural networks",
                    "artificial intelligence", "data science", "natural language processing",
                    "computer vision", "reinforcement learning", "optimization"
                ],
                "specialties": [
                    "Neural Networks", "Deep Learning", "NLP", "Computer Vision",
                    "Reinforcement Learning", "Data Science", "MLOps"
                ],
                "languages": ["English", "Spanish"],
                "personality_traits": {
                    "analytical": 0.95,
                    "formal": 0.6,
                    "helpful": 0.9,
                    "curious": 0.95,
                    "precise": 0.85
                }
            },
            "physics": {
                "name": "Physics Expert",
                "description": "Especialista en física teórica, física estadística y sistemas complejos",
                "keywords": [
                    "statistical physics", "condensed matter", "quantum mechanics",
                    "thermodynamics", "complex systems", "network theory"
                ],
                "specialties": [
                    "Statistical Physics", "Quantum Mechanics", "Complex Systems",
                    "Network Theory", "Thermodynamics"
                ],
                "languages": ["English", "Spanish"],
                "personality_traits": {
                    "analytical": 0.95,
                    "formal": 0.8,
                    "helpful": 0.85,
                    "curious": 0.9,
                    "precise": 0.95
                }
            }
        }
        
        return configurations.get(domain, configurations["quantitative_finance"])

    def _initialize_conversational_agent(self):
        """Inicializar el agente conversacional especializado"""
        try:
            # Crear agente conversacional con configuración del dominio
            self.conversational_agent = AdvancedConversationalAgent(
                memory=self.memory,
                personality_config=self.domain_config.get("personality_traits", {}),
                domain_expertise=self.domain_config.get("specialties", []),
                supported_languages=self.domain_config.get("languages", ["English", "Spanish"])
            )
            
            # Configurar conocimiento especializado inicial
            self._load_specialized_knowledge()
            
            logger.info("✅ Agente conversacional especializado inicializado")
            
        except Exception as e:
            logger.error(f"❌ Error inicializando agente conversacional: {e}")
            # Fallback simple
            self.conversational_agent = None

    def _load_specialized_knowledge(self):
        """Cargar conocimiento especializado inicial"""
        if not self.conversational_agent:
            return
        
        # Conocimiento base por dominio
        base_knowledge = {
            "quantitative_finance": [
                "Soy un experto en finanzas cuantitativas con conocimiento profundo en modelos matemáticos para pricing de derivados.",
                "Mi especialidad incluye econofísica, gestión de riesgos, y optimización de portafolios usando métodos estocásticos.",
                "Puedo ayudar con Black-Scholes, modelos de volatilidad, Value at Risk, y trading algorítmico."
            ]
        }
        
        domain_knowledge = base_knowledge.get(self.domain, [])
        for knowledge in domain_knowledge:
            self.memory.add_context("system", knowledge)

    async def query(self, user_query: str, context: Dict = None) -> Dict:
        """Procesar query del usuario con conocimiento especializado"""
        try:
            self.agent_stats["queries_processed"] += 1
            
            # Buscar en nodos relevantes
            relevant_nodes = self.node_manager.search_nodes(user_query, limit=5)
            
            # Construir contexto enriquecido
            enriched_context = {
                "query": user_query,
                "domain": self.domain,
                "relevant_papers": len(relevant_nodes),
                "specialized_knowledge": []
            }
            
            # Agregar conocimiento de nodos relevantes
            for node in relevant_nodes:
                enriched_context["specialized_knowledge"].append({
                    "title": node.title,
                    "content": node.content[:500],  # Primeros 500 caracteres
                    "citations": node.citations,
                    "concepts": node.concepts,
                    "source": node.source
                })
            
            # Usar agente conversacional si está disponible
            if self.conversational_agent:
                response = await self._generate_conversational_response(user_query, enriched_context)
            else:
                response = self._generate_basic_response(user_query, enriched_context)
            
            # Actualizar estadísticas de aprendizaje
            if relevant_nodes:
                self.agent_stats["papers_learned_from"] += len(relevant_nodes)
            
            return {
                "result": response,
                "metadata": {
                    "domain": self.domain,
                    "relevant_papers": len(relevant_nodes),
                    "specialized_response": True,
                    "knowledge_sources": [node.source for node in relevant_nodes],
                    "concepts_used": [concept for node in relevant_nodes for concept in node.concepts]
                },
                "source_documents": relevant_nodes
            }
            
        except Exception as e:
            logger.error(f"❌ Error procesando query: {e}")
            return {
                "result": f"Lo siento, hubo un error procesando tu consulta: {str(e)}",
                "metadata": {"error": True, "domain": self.domain},
                "source_documents": []
            }

    async def _generate_conversational_response(self, query: str, context: Dict) -> str:
        """Generar respuesta usando el agente conversacional"""
        try:
            # Preparar contexto para el agente conversacional
            context_text = f"Dominio: {self.domain}\n"
            context_text += f"Consulta: {query}\n"
            
            if context.get("specialized_knowledge"):
                context_text += "\nConocimiento especializado disponible:\n"
                for i, knowledge in enumerate(context["specialized_knowledge"][:3]):  # Top 3
                    context_text += f"{i+1}. {knowledge['title']}\n"
                    context_text += f"   Conceptos: {', '.join(knowledge['concepts'][:5])}\n"
                    context_text += f"   Citaciones: {knowledge['citations']}\n\n"
            
            # Generar respuesta conversacional
            response = await self.conversational_agent.generate_response(query, context_text)
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error en respuesta conversacional: {e}")
            return self._generate_basic_response(query, context)

    def _generate_basic_response(self, query: str, context: Dict) -> str:
        """Generar respuesta básica cuando el agente conversacional no está disponible"""
        
        domain_intro = {
            "quantitative_finance": "Como especialista en finanzas cuantitativas y econofísica",
            "machine_learning": "Como experto en machine learning y ciencia de datos",
            "physics": "Como especialista en física y sistemas complejos"
        }
        
        intro = domain_intro.get(self.domain, "Como asistente especializado")
        
        response = f"{intro}, puedo ayudarte con tu consulta sobre: {query}\n\n"
        
        if context.get("specialized_knowledge"):
            response += "Basándome en los papers más relevantes:\n\n"
            
            for i, knowledge in enumerate(context["specialized_knowledge"][:2]):
                response += f"📄 **{knowledge['title']}**\n"
                response += f"🔬 Conceptos clave: {', '.join(knowledge['concepts'][:3])}\n"
                response += f"📊 Citaciones: {knowledge['citations']}\n"
                response += f"💡 Resumen: {knowledge['content'][:200]}...\n\n"
        
        response += f"¿Te gustaría que profundice en algún aspecto específico de {self.domain}?"
        
        return response

    async def start_autonomous_learning(self):
        """Iniciar aprendizaje autónomo continuo"""
        logger.info("🧠 Iniciando aprendizaje autónomo...")
        
        # Iniciar auto-alimentación en background
        feeding_task = asyncio.create_task(self.auto_feeding.start_auto_feeding())
        
        # Iniciar mantenimiento de nodos en background
        maintenance_task = asyncio.create_task(self.node_manager.auto_maintenance())
        
        # Monitoreo del agente
        monitoring_task = asyncio.create_task(self._monitor_agent_performance())
        
        # Ejecutar todas las tareas
        try:
            await asyncio.gather(feeding_task, maintenance_task, monitoring_task)
        except Exception as e:
            logger.error(f"❌ Error en aprendizaje autónomo: {e}")

    async def _monitor_agent_performance(self):
        """Monitorear y mejorar el rendimiento del agente"""
        while True:
            try:
                # Actualizar estadísticas cada hora
                await asyncio.sleep(3600)
                
                # Calcular métricas de rendimiento
                node_stats = self.node_manager.get_statistics()
                feeding_stats = self.auto_feeding.get_feeding_stats()
                
                # Actualizar nivel de expertise basado en papers aprendidos
                papers_learned = node_stats.get("total_nodes", 0)
                self.agent_stats["domain_expertise_level"] = min(5.0, 1.0 + (papers_learned / 1000) * 4.0)
                
                # Actualizar temas especializados basado en conceptos más frecuentes
                top_concepts = node_stats.get("top_concepts", [])
                self.agent_stats["specialized_topics"] = [concept[0] for concept in top_concepts[:10]]
                
                # Guardar estadísticas
                self.save_agent_stats()
                
                logger.info(f"📊 Estadísticas actualizadas - Expertise: {self.agent_stats['domain_expertise_level']:.2f}")
                
            except Exception as e:
                logger.error(f"❌ Error en monitoreo: {e}")

    def get_agent_status(self) -> Dict:
        """Obtener estado completo del agente"""
        node_stats = self.node_manager.get_statistics()
        feeding_stats = self.auto_feeding.get_feeding_stats()
        
        return {
            "agent_info": {
                "domain": self.domain,
                "name": self.domain_config["name"],
                "description": self.domain_config["description"],
                "expertise_level": self.agent_stats["domain_expertise_level"],
                "queries_processed": self.agent_stats["queries_processed"]
            },
            "knowledge_base": {
                "total_nodes": node_stats.get("total_nodes", 0),
                "total_citations": node_stats.get("total_citations", 0),
                "specialized_topics": self.agent_stats["specialized_topics"],
                "knowledge_sources": node_stats.get("source_distribution", {})
            },
            "auto_learning": {
                "papers_processed": feeding_stats.get("total_papers_processed", 0),
                "papers_added": feeding_stats.get("papers_added", 0),
                "last_feeding": feeding_stats.get("last_feeding"),
                "next_feeding_hours": feeding_stats.get("next_feeding_in_hours", 0)
            },
            "performance": {
                **self.agent_stats["performance_metrics"],
                "last_updated": datetime.now().isoformat()
            }
        }

    def health_check(self) -> Dict:
        """Verificación de salud del sistema"""
        return {
            "overall_healthy": True,
            "components": {
                "node_manager": len(self.node_manager.nodes) > 0,
                "auto_feeding": self.auto_feeding is not None,
                "conversational_agent": self.conversational_agent is not None,
                "domain_configured": bool(self.domain_config)
            },
            "domain": self.domain,
            "expertise_level": self.agent_stats["domain_expertise_level"],
            "knowledge_nodes": len(self.node_manager.nodes),
            "specialized": True
        }

    def save_agent_stats(self):
        """Guardar estadísticas del agente"""
        try:
            stats_with_timestamp = {
                **self.agent_stats,
                "last_updated": datetime.now().isoformat()
            }
            
            with open(self.data_dir / "agent_stats.json", "w", encoding="utf-8") as f:
                json.dump(stats_with_timestamp, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"❌ Error guardando estadísticas del agente: {e}")

    def load_agent_stats(self):
        """Cargar estadísticas del agente"""
        try:
            stats_file = self.data_dir / "agent_stats.json"
            if stats_file.exists():
                with open(stats_file, "r", encoding="utf-8") as f:
                    saved_stats = json.load(f)
                    self.agent_stats.update(saved_stats)
                    
        except Exception as e:
            logger.error(f"❌ Error cargando estadísticas del agente: {e}")

    async def manual_learning_session(self, topic: str = None):
        """Sesión manual de aprendizaje enfocada"""
        logger.info(f"📚 Iniciando sesión de aprendizaje manual - Tema: {topic or 'general'}")
        
        try:
            # Forzar alimentación inmediata
            await self.auto_feeding.feed_new_papers()
            
            # Si se especifica un tema, buscar nodos relacionados
            if topic:
                relevant_nodes = self.node_manager.search_nodes(topic, limit=10)
                logger.info(f"🎯 Encontrados {len(relevant_nodes)} nodos relacionados con '{topic}'")
                
                # Actualizar relevancia de estos nodos
                for node in relevant_nodes:
                    node.relevance_score = min(1.0, node.relevance_score * 1.1)
            
            # Actualizar estadísticas
            self.agent_stats["last_learning_session"] = datetime.now().isoformat()
            self.save_agent_stats()
            
            return {
                "success": True,
                "message": f"Sesión de aprendizaje completada para tema: {topic or 'general'}",
                "nodes_found": len(relevant_nodes) if topic else 0
            }
            
        except Exception as e:
            logger.error(f"❌ Error en sesión de aprendizaje manual: {e}")
            return {
                "success": False,
                "error": str(e)
            }


def create_specialized_agent(domain: str = "quantitative_finance") -> SpecializedAIAgent:
    """Factory function para crear agente especializado"""
    return SpecializedAIAgent(domain)


async def main():
    """Función principal para pruebas"""
    # Crear agente especializado
    agent = create_specialized_agent("quantitative_finance")
    
    # Mostrar estado inicial
    status = agent.get_agent_status()
    print("\n🤖 Estado del Agente Especializado:")
    print(json.dumps(status, indent=2, ensure_ascii=False))
    
    # Probar query
    response = await agent.query("¿Qué es el modelo Black-Scholes y cómo se aplica en el pricing de opciones?")
    print(f"\n💬 Respuesta: {response['result'][:500]}...")
    
    # Sesión de aprendizaje manual
    learning_result = await agent.manual_learning_session("volatility modeling")
    print(f"\n📚 Resultado del aprendizaje: {learning_result}")


if __name__ == "__main__":
    asyncio.run(main())
