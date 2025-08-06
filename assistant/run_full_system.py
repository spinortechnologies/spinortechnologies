#!/usr/bin/env python3
"""
Sistema Completo de Finanzas Cuantitativas con Papers en Tiempo Real
Complete Quantitative Finance System with Real-Time Papers
SPINOR TECHNOLOGIES - 2025
"""

import os
import sys
import time
import subprocess
import threading
import signal
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FullSystemManager:
    def __init__(self):
        self.auto_service_process = None
        self.running = True
        self.vector_store = None
        self.agent = None
        
    def _initialize_ai_system(self):
        """Initialize the AI system with vector store and agent"""
        if self.agent is None:
            try:
                print("🧠 Inicializando sistema de IA...")
                from vector_db import load_vector_store
                from simple_agent import SimpleQuantFinanceAgent
                
                # Load vector store
                self.vector_store = load_vector_store()
                
                # Initialize agent
                self.agent = SimpleQuantFinanceAgent(self.vector_store)
                print("✅ Sistema de IA inicializado")
                return True
            except Exception as e:
                print(f"❌ Error inicializando sistema de IA: {e}")
                return False
        return True
        
    def print_banner(self):
        print("="*80)
        print("🚀 SISTEMA COMPLETO - FINANZAS CUANTITATIVAS CON PAPERS EN TIEMPO REAL")
        print("🚀 FULL SYSTEM - QUANTITATIVE FINANCE WITH REAL-TIME PAPERS")
        print("="*80)
        print("📊 SPINOR TECHNOLOGIES - Sistema de IA Financiera Avanzada")
        print("📊 SPINOR TECHNOLOGIES - Advanced Financial AI System")
        print("="*80)
        
    def start_auto_service(self):
        """Inicia el servicio automático de papers en background"""
        try:
            print("🔄 Iniciando servicio automático de papers...")
            
            # Check if the service script exists
            service_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "auto_paper_service.py")
            if not os.path.exists(service_path):
                print("❌ Error: auto_paper_service.py no encontrado")
                return False
                
            self.auto_service_process = subprocess.Popen(
                [sys.executable, "auto_paper_service.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
            
            # Wait a moment to check if the process started successfully
            time.sleep(2)
            if self.auto_service_process.poll() is not None:
                print("❌ Error: El servicio automático no pudo iniciarse")
                return False
                
            print("✅ Servicio automático iniciado (PID:", self.auto_service_process.pid, ")")
            return True
        except FileNotFoundError:
            print("❌ Error: Python o auto_paper_service.py no encontrado")
            return False
        except Exception as e:
            print(f"❌ Error iniciando servicio automático: {e}")
            logger.error(f"Auto service start error: {e}", exc_info=True)
            return False
            
    def stop_auto_service(self):
        """Detiene el servicio automático"""
        if self.auto_service_process:
            try:
                self.auto_service_process.terminate()
                self.auto_service_process.wait(timeout=5)
                print("✅ Servicio automático detenido")
            except Exception as e:
                print(f"⚠️ Error deteniendo servicio: {e}")
                try:
                    self.auto_service_process.kill()
                except:
                    pass
                    
    def run_initial_paper_update(self):
        """Ejecuta una actualización inicial de papers"""
        print("📚 Ejecutando actualización inicial de papers...")
        try:
            # Create directories if they don't exist
            os.makedirs("./data/papers", exist_ok=True)
            os.makedirs("./logs", exist_ok=True)
            
            result = subprocess.run(
                [sys.executable, "realtime_papers.py"],
                input="1\n",  # Opción rápida
                text=True,
                capture_output=True,
                timeout=300,  # 5 minutos timeout
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
            
            if result.returncode == 0:
                print("✅ Actualización inicial completada")
                
                # Try to parse output to show summary
                output_lines = result.stdout.split('\n')
                for line in output_lines:
                    if "Total de papers:" in line or "papers descargados:" in line:
                        print(f"📊 {line.strip()}")
                        
            else:
                print("⚠️ Actualización inicial con warnings")
                if result.stderr:
                    logger.warning(f"Paper update warnings: {result.stderr[:200]}...")
                    
        except subprocess.TimeoutExpired:
            print("⏰ Timeout en actualización inicial - continuando...")
            logger.warning("Paper update timeout after 5 minutes")
        except FileNotFoundError:
            print("❌ Error: No se encontró realtime_papers.py")
            logger.error("realtime_papers.py not found")
        except Exception as e:
            print(f"❌ Error en actualización inicial: {e}")
            logger.error(f"Initial paper update error: {e}", exc_info=True)
            
    def show_menu(self):
        """Muestra el menú principal"""
        print("\n" + "="*50)
        print("📋 MENÚ PRINCIPAL / MAIN MENU")
        print("="*50)
        print("1. 🤖 Iniciar Chat Interactivo / Start Interactive Chat")
        print("2. 📄 Descargar Papers Recientes / Download Recent Papers")
        print("3. 📊 Ver Estado del Sistema / View System Status")
        print("4. ⚙️ Configurar Servicio Automático / Configure Auto Service")
        print("5. 🔍 Buscar en Papers / Search Papers")
        print("6. 📈 Ejemplo de Consulta Financiera / Financial Query Example")
        print("7. 🧠 Inicializar Sistema IA / Initialize AI System")
        print("8. 📚 Ver Papers Recientes / View Recent Papers")
        print("0. 🚪 Salir / Exit")
        print("-"*50)
        
    def view_recent_papers(self):
        """Muestra los papers recientes descargados"""
        print("\n📚 PAPERS RECIENTES / RECENT PAPERS")
        print("="*40)
        
        papers_dir = Path("./data/papers")
        if not papers_dir.exists():
            print("❌ No hay directorio de papers")
            return
            
        paper_files = list(papers_dir.glob("papers_*.json"))
        if not paper_files:
            print("❌ No hay papers descargados")
            print("💡 Usa la opción 2 para descargar papers")
            return
            
        # Get the latest file
        latest_file = max(paper_files, key=lambda p: p.stat().st_mtime)
        
        try:
            import json
            with open(latest_file, 'r') as f:
                papers = json.load(f)
                
            print(f"📄 Archivo: {latest_file.name}")
            print(f"📊 Total de papers: {len(papers)}")
            
            # Show first 10 papers
            print("\n🔥 Últimos papers descargados:")
            for i, paper in enumerate(papers[:10], 1):
                title = paper.get('title', 'Sin título')
                authors = paper.get('authors', ['Desconocido'])
                category = paper.get('category', 'N/A')
                
                # Truncate title if too long
                if len(title) > 60:
                    title = title[:57] + "..."
                    
                # Handle authors list
                if isinstance(authors, list):
                    author_str = authors[0] if authors else "Desconocido"
                    if len(authors) > 1:
                        author_str += f" et al. ({len(authors)} autores)"
                else:
                    author_str = str(authors)
                    
                print(f"   {i:2d}. {title}")
                print(f"       👥 {author_str}")
                print(f"       🏷️ {category}")
                print()
                
            if len(papers) > 10:
                print(f"... y {len(papers) - 10} papers más")
                
        except Exception as e:
            print(f"❌ Error leyendo papers: {e}")
            logger.error(f"Error reading papers: {e}", exc_info=True)
        
    def run_interactive_chat(self):
        """Ejecuta el chat interactivo"""
        print("🤖 Iniciando chat interactivo...")
        try:
            subprocess.run([sys.executable, "demo_simple.py"])
        except KeyboardInterrupt:
            print("\n💬 Chat finalizado")
        except Exception as e:
            print(f"❌ Error en chat: {e}")
            
    def download_papers(self):
        """Ejecuta descarga manual de papers"""
        print("📄 Iniciando descarga de papers...")
        try:
            subprocess.run([sys.executable, "realtime_papers.py"])
        except KeyboardInterrupt:
            print("\n📄 Descarga cancelada")
        except Exception as e:
            print(f"❌ Error descargando papers: {e}")
            
    def show_system_status(self):
        """Muestra el estado del sistema"""
        print("\n📊 ESTADO DEL SISTEMA / SYSTEM STATUS")
        print("="*50)
        
        # Check papers
        papers_dir = Path("./data/papers")
        if papers_dir.exists():
            paper_files = list(papers_dir.glob("papers_*.json"))
            print(f"📚 Papers descargados: {len(paper_files)} archivos")
            if paper_files:
                latest = max(paper_files, key=lambda p: p.stat().st_mtime)
                mod_time = latest.stat().st_mtime
                hours_ago = (time.time() - mod_time) / 3600
                print(f"🕒 Últimos papers: hace {hours_ago:.1f} horas")
                
                # Show paper count info
                try:
                    import json
                    with open(latest, 'r') as f:
                        papers_data = json.load(f)
                    print(f"📄 Papers en último archivo: {len(papers_data)}")
                except Exception as e:
                    logger.warning(f"Error reading paper file: {e}")
        else:
            print("📚 Papers descargados: 0 archivos")
            
        # Check auto service
        if self.auto_service_process and self.auto_service_process.poll() is None:
            print("🔄 Servicio automático: ✅ Activo")
        else:
            print("🔄 Servicio automático: ❌ Inactivo")
            
        # Check vector database
        vector_db_path = Path("./knowledge_base/vector_db")
        if vector_db_path.exists():
            print("🗃️ Base de datos vectorial: ✅ Disponible")
        else:
            print("🗃️ Base de datos vectorial: ⚠️ No encontrada")
            
        # Check AI system
        if self.agent is not None:
            print("🤖 Sistema de IA: ✅ Inicializado")
            try:
                health = self.agent.health_check()
                if health.get('overall_healthy', False):
                    print("💚 Estado de IA: ✅ Saludable")
                else:
                    print("💛 Estado de IA: ⚠️ Con advertencias")
            except Exception as e:
                print("💛 Estado de IA: ⚠️ Error en verificación")
                logger.warning(f"Health check error: {e}")
        else:
            print("🤖 Sistema de IA: ❌ No inicializado")
            
        print("="*50)
        
    def configure_auto_service(self):
        """Configura el servicio automático"""
        print("\n⚙️ CONFIGURACIÓN SERVICIO AUTOMÁTICO")
        print("="*40)
        print("1. Iniciar servicio automático")
        print("2. Detener servicio automático")
        print("3. Reiniciar servicio automático")
        print("0. Volver al menú principal")
        
        choice = input("\n🔢 Selecciona opción: ").strip()
        
        if choice == "1":
            if self.auto_service_process and self.auto_service_process.poll() is None:
                print("ℹ️ El servicio ya está activo")
            else:
                self.start_auto_service()
        elif choice == "2":
            self.stop_auto_service()
        elif choice == "3":
            self.stop_auto_service()
            time.sleep(2)
            self.start_auto_service()
        elif choice == "0":
            return
        else:
            print("❌ Opción inválida")
            
    def search_papers(self):
        """Busca en los papers descargados"""
        print("\n🔍 BÚSQUEDA EN PAPERS")
        print("="*30)
        
        # Initialize AI system if needed
        if not self._initialize_ai_system():
            print("❌ No se pudo inicializar el sistema de IA")
            return
        
        try:
            query = input("💭 ¿Qué quieres buscar?: ").strip()
            if query:
                print(f"\n🔎 Buscando: '{query}'...")
                response = self.agent.query(f"Busca información sobre: {query}")
                print("\n📝 Resultado:")
                print("-" * 40)
                print(response)
                print("-" * 40)
            else:
                print("❌ Consulta vacía")
                
        except Exception as e:
            print(f"❌ Error en búsqueda: {e}")
            logger.error(f"Search error: {e}", exc_info=True)
            
    def financial_query_example(self):
        """Muestra un ejemplo de consulta financiera"""
        print("\n📈 EJEMPLO DE CONSULTA FINANCIERA")
        print("="*40)
        
        # Initialize AI system if needed
        if not self._initialize_ai_system():
            print("❌ No se pudo inicializar el sistema de IA")
            return
        
        examples = [
            "¿Cómo funciona el modelo Black-Scholes?",
            "Explica Value at Risk (VaR)",
            "¿Qué es portfolio optimization?",
            "Describe el trading algorítmico",
            "¿Cómo se calcula la volatilidad implícita?"
        ]
        
        print("💡 Consultas de ejemplo:")
        for i, example in enumerate(examples, 1):
            print(f"   {i}. {example}")
            
        try:
            choice = int(input("\n🔢 Selecciona ejemplo (1-5): ")) - 1
            if 0 <= choice < len(examples):
                selected_query = examples[choice]
                print(f"\n🤖 Ejecutando: '{selected_query}'")
                
                response = self.agent.query(selected_query)
                
                print("\n📝 Respuesta:")
                print("="*50)
                print(response)
                print("="*50)
            else:
                print("❌ Opción inválida")
        except ValueError:
            print("❌ Entrada inválida")
        except Exception as e:
            print(f"❌ Error: {e}")
            logger.error(f"Financial query error: {e}", exc_info=True)
            
    def signal_handler(self, signum, frame):
        """Manejador de señales para shutdown limpio"""
        print("\n🛑 Deteniendo sistema...")
        self.running = False
        self.stop_auto_service()
        sys.exit(0)
        
    def run(self):
        """Ejecuta el sistema completo"""
        # Configurar manejador de señales
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        self.print_banner()
        
        # Preguntar si quiere iniciar el servicio automático
        print("\n🔄 ¿Quieres iniciar el servicio automático de papers?")
        print("   (Descargará papers nuevos cada 6 horas)")
        auto_start = input("📝 (s/n): ").strip().lower()
        
        if auto_start in ['s', 'y', 'yes', 'sí', 'si']:
            self.start_auto_service()
            
        # Preguntar si quiere hacer una actualización inicial
        print("\n📚 ¿Quieres descargar papers recientes ahora?")
        initial_update = input("📝 (s/n): ").strip().lower()
        
        if initial_update in ['s', 'y', 'yes', 'sí', 'si']:
            self.run_initial_paper_update()
            
        # Menú principal
        while self.running:
            try:
                self.show_menu()
                choice = input("🔢 Selecciona opción: ").strip()
                
                if choice == "0":
                    print("👋 ¡Hasta luego!")
                    break
                elif choice == "1":
                    self.run_interactive_chat()
                elif choice == "2":
                    self.download_papers()
                elif choice == "3":
                    self.show_system_status()
                elif choice == "4":
                    self.configure_auto_service()
                elif choice == "5":
                    self.search_papers()
                elif choice == "6":
                    self.financial_query_example()
                elif choice == "7":
                    self._initialize_ai_system()
                elif choice == "8":
                    self.view_recent_papers()
                else:
                    print("❌ Opción inválida. Intenta de nuevo.")
                    
            except KeyboardInterrupt:
                print("\n🛑 Interrupción detectada...")
                break
            except Exception as e:
                print(f"❌ Error inesperado: {e}")
                
        # Cleanup
        self.stop_auto_service()
        print("🔧 Sistema detenido correctamente")

if __name__ == "__main__":
    manager = FullSystemManager()
    manager.run()
