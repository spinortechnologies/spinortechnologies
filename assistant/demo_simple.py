#!/usr/bin/env python3
"""
Interfaz Interactiva Simple del Asistente de Finanzas Cuantitativas
Simple Interactive Interface for the Quantitative Finance Assistant
Author: SPINOR Technologies
Date: August 6, 2025
Version: 2.0
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    print("=" * 80)
    print("🚀 ASISTENTE DE FINANZAS CUANTITATIVAS - SPINOR TECHNOLOGIES")
    print("🚀 QUANTITATIVE FINANCE ASSISTANT - SPINOR TECHNOLOGIES") 
    print("=" * 80)
    print("📊 Versión 2.0 - Asistente con IA especializado en finanzas cuantitativas")
    print("📊 Version 2.0 - AI Assistant specialized in quantitative finance")
    print("=" * 80)
    print()
    
    try:
        print("🔧 Inicializando sistema... / Initializing system...")
        
        from vector_db import load_vector_store
        print("📚 Cargando base de conocimientos... / Loading knowledge base...")
        vector_store = load_vector_store()
        
        from simple_agent import SimpleQuantFinanceAgent
        print("🤖 Inicializando agente IA... / Initializing AI agent...")
        agent = SimpleQuantFinanceAgent(vector_store)
        
        print("✅ Sistema listo! / System ready!")
        print()
        print("💡 Ejemplos de preguntas / Example questions:")
        print("  - ¿Cómo funciona el modelo Black-Scholes?")
        print("  - How does Black-Scholes model work?")
        print("  - Explica Value at Risk")
        print("  - What is portfolio optimization?")
        print("  - ¿Qué es el trading algorítmico?")
        print()
        print("📋 Comandos: 'help' (ayuda), 'exit' (salir), 'status' (estado), 'update' (papers), 'papers' (ver papers)")
        print("📋 Commands: 'help' (help), 'exit' (exit), 'status' (status), 'update' (papers), 'papers' (view papers)")
        print("📋 'update' (descargar papers recientes), 'papers' (ver papers)")
        print()
        
        while True:
            try:
                query = input("💬 Tu pregunta / Your question: ").strip()
                
                if query.lower() in ['exit', 'quit', 'salir']:
                    print("👋 ¡Hasta luego! / Goodbye!")
                    break
                    
                elif query.lower() == 'help':
                    print("\n📋 Ayuda / Help:")
                    print("  - Haz preguntas sobre finanzas cuantitativas")
                    print("  - Ask questions about quantitative finance")
                    print("  - Temas: opciones, riesgo, carteras, trading")
                    print("  - Topics: options, risk, portfolios, trading")
                    print("  - Usa 'update' para descargar papers recientes")
                    print("  - Use 'papers' to see available research papers")
                    print("  - Escribe 'exit' para salir / Type 'exit' to quit")
                    print()
                    continue
                    
                elif query.lower() == 'status':
                    health = agent.health_check()
                    summary = agent.get_conversation_summary()
                    print(f"\n🔍 Estado del sistema / System status:")
                    print(f"   Salud: {'✅ Excelente' if health['overall_healthy'] else '❌ Problema'}")
                    if 'total_queries' in summary:
                        print(f"   Consultas: {summary['total_queries']}")
                        print(f"   Rendimiento: {summary['performance']}")
                    print()
                    continue
                    
                elif query.lower() == 'update':
                    print("🔄 Descargando papers recientes de ArXiv...")
                    try:
                        from realtime_papers import RealTimePaperFetcher
                        fetcher = RealTimePaperFetcher()
                        papers = fetcher.fetch_latest_papers(days_back=3, max_papers=10)
                        if papers:
                            fetcher.save_papers(papers)
                            fetcher.update_vector_database(papers)
                            print(f"✅ {len(papers)} papers descargados y agregados a la base de datos")
                        else:
                            print("ℹ️ No se encontraron papers nuevos")
                    except Exception as e:
                        print(f"❌ Error descargando papers: {e}")
                    print()
                    continue
                    
                elif query.lower() == 'papers':
                    print("📚 Verificando papers recientes...")
                    try:
                        import glob
                        import json
                        papers_dir = "./data/papers"
                        if os.path.exists(papers_dir):
                            recent_papers = glob.glob(os.path.join(papers_dir, "papers_*.json"))
                            if recent_papers:
                                latest_file = max(recent_papers, key=os.path.getctime)
                                with open(latest_file, 'r') as f:
                                    papers = json.load(f)
                                print(f"📄 Papers disponibles: {len(papers)}")
                                print("🔥 Últimos 3 papers:")
                                for i, paper in enumerate(papers[:3]):
                                    print(f"   {i+1}. {paper['title'][:60]}...")
                            else:
                                print("ℹ️ No hay papers descargados. Usa 'update' para descargar.")
                        else:
                            print("ℹ️ No hay papers descargados. Usa 'update' para descargar.")
                    except Exception as e:
                        print(f"❌ Error: {e}")
                    print()
                    continue
                    
                elif not query:
                    continue
                
                print("🔄 Procesando... / Processing...")
                response = agent.query(query)
                
                print("\n" + "="*60)
                print("🤖 RESPUESTA / RESPONSE:")
                print("="*60)
                print(response['result'])
                
                if response.get('source_documents'):
                    print(f"\n📚 Basado en {len(response['source_documents'])} documentos de la base de conocimientos")
                    print(f"📚 Based on {len(response['source_documents'])} documents from knowledge base")
                
                meta = response.get('metadata', {})
                if meta.get('response_time'):
                    print(f"⏱️  Tiempo: {meta['response_time']:.2f}s")
                
                print("="*60)
                print()
                
            except KeyboardInterrupt:
                print("\n👋 ¡Hasta luego! / Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                print()
    
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        print("Verifica que todas las dependencias estén instaladas:")
        print("pip install langchain langchain-community transformers sentence-transformers faiss-cpu pandas numpy")

if __name__ == "__main__":
    main()
