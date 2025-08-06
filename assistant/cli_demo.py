#!/usr/bin/env python3
"""
Simple CLI interface for the Quantitative Finance Assistant
Author: SPINOR Technologies
Date: August 6, 2025
Version: 2.0
"""

import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simple_agent import SimpleQuantFinanceAgent
from vector_db import load_vector_store
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def print_banner():
    """Print welcome banner"""
    print("=" * 80)
    print("🚀 ASISTENTE DE FINANZAS CUANTITATIVAS - SPINOR TECHNOLOGIES")
    print("🚀 QUANTITATIVE FINANCE ASSISTANT - SPINOR TECHNOLOGIES")
    print("=" * 80)
    print("📊 Versión 2.0 - Asistente con IA especializado en finanzas cuantitativas")
    print("📊 Version 2.0 - AI Assistant specialized in quantitative finance")
    print("=" * 80)
    print()


def print_help():
    """Print available commands"""
    print("📋 Comandos disponibles / Available commands:")
    print("  help    - Mostrar esta ayuda / Show this help")
    print("  exit    - Salir del programa / Exit the program")
    print("  status  - Estado del sistema / System status")
    print("  stats   - Estadísticas de uso / Usage statistics")
    print("  clear   - Limpiar memoria / Clear memory")
    print("  <pregunta> - Hacer una pregunta financiera / Ask a financial question")
    print()
    print("💡 Ejemplos de preguntas / Example questions:")
    print("  - ¿Cómo funciona el modelo Black-Scholes?")
    print("  - How does Black-Scholes model work?")
    print("  - Explica Value at Risk")
    print("  - Explain portfolio optimization")
    print("  - ¿Qué es el CAPM?")
    print("  - What are derivatives?")
    print()


def main():
    """Main CLI interface"""
    print_banner()
    
    try:
        # Initialize the system
        print("🔧 Inicializando sistema... / Initializing system...")
        
        # Load vector store
        print("📚 Cargando base de conocimientos... / Loading knowledge base...")
        vector_store = load_vector_store()
        
        # Initialize agent
        print("🤖 Inicializando agente IA... / Initializing AI agent...")
        agent = SimpleQuantFinanceAgent(vector_store)
        
        print("✅ Sistema listo! / System ready!")
        print()
        print_help()
        
        # Main interaction loop
        while True:
            try:
                # Get user input
                query = input("💬 Tu pregunta / Your question: ").strip()
                
                # Handle commands
                if query.lower() in ['exit', 'quit', 'salir']:
                    print("👋 ¡Hasta luego! / Goodbye!")
                    break
                    
                elif query.lower() == 'help':
                    print_help()
                    continue
                    
                elif query.lower() == 'status':
                    health = agent.health_check()
                    print(f"🔍 Estado del sistema / System status:")
                    print(f"   Salud general / Overall health: {'✅ Bueno' if health['overall_healthy'] else '❌ Problema'}")
                    for component, status in health['components'].items():
                        status_icon = "✅" if status else "❌"
                        print(f"   {component}: {status_icon}")
                    print()
                    continue
                    
                elif query.lower() == 'stats':
                    summary = agent.get_conversation_summary()
                    if 'message' in summary:
                        print(f"📊 {summary['message']}")
                    else:
                        print("📊 Estadísticas de uso / Usage statistics:")
                        print(f"   Consultas totales / Total queries: {summary['total_queries']}")
                        print(f"   Tiempo promedio / Average time: {summary['average_response_time']:.2f}s")
                        print(f"   Rendimiento / Performance: {summary['performance']}")
                        print(f"   Temas recientes / Recent topics: {', '.join(summary['recent_topics'][:5])}")
                    print()
                    continue
                    
                elif query.lower() == 'clear':
                    agent.clear_memory()
                    print("🧹 Memoria limpiada / Memory cleared")
                    print()
                    continue
                    
                elif not query:
                    continue
                
                # Process financial query
                print("🔄 Procesando consulta... / Processing query...")
                
                response = agent.query(query)
                
                print("\n" + "="*60)
                print("🤖 RESPUESTA / RESPONSE:")
                print("="*60)
                print(response['result'])
                
                # Show sources if available
                if response.get('source_documents'):
                    print("\n📚 FUENTES / SOURCES:")
                    for i, doc in enumerate(response['source_documents'][:3]):
                        title = doc.metadata.get('title', 'Documento desconocido')
                        print(f"   {i+1}. {title}")
                
                # Show metadata if available
                if response.get('metadata'):
                    meta = response['metadata']
                    if meta.get('financial_concepts'):
                        print(f"\n🏷️  CONCEPTOS DETECTADOS / DETECTED CONCEPTS: {', '.join(meta['financial_concepts'][:5])}")
                    
                    if meta.get('response_time'):
                        print(f"⏱️  TIEMPO DE RESPUESTA / RESPONSE TIME: {meta['response_time']:.2f}s")
                
                print("="*60)
                print()
                
            except KeyboardInterrupt:
                print("\n👋 ¡Hasta luego! / Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                logger.error(f"Error processing query: {e}")
                print()
    
    except Exception as e:
        print(f"❌ Error fatal al inicializar el sistema: {e}")
        logger.error(f"Fatal error initializing system: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
