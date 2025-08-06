#!/usr/bin/env python3
"""
Sistema Simplificado de Descarga de Papers en Tiempo Real
Simplified Real-time Paper Download System
Author: SPINOR Technologies
Date: August 6, 2025
"""

import os
import sys
import arxiv
import json
from datetime import datetime, timedelta
from typing import List, Dict
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Agregar el directorio actual al path para imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class RealTimePaperFetcher:
    """Descargador de papers en tiempo real desde ArXiv."""
    
    def __init__(self):
        self.categories = [
            "q-fin.PR",  # Pricing of Securities
            "q-fin.RM",  # Risk Management
            "q-fin.PM",  # Portfolio Management
            "q-fin.TR",  # Trading and Market Microstructure
            "q-fin.MF",  # Mathematical Finance
            "q-fin.CP",  # Computational Finance
        ]
        
        self.keywords = [
            "quantitative finance", "option pricing", "risk management",
            "portfolio optimization", "algorithmic trading", "derivatives",
            "black-scholes", "value at risk", "monte carlo", "stochastic"
        ]
        
        # Crear directorio para papers
        self.data_dir = "./data/papers"
        os.makedirs(self.data_dir, exist_ok=True)
        
        logger.info("🚀 Real-time Paper Fetcher initialized")
    
    def fetch_latest_papers(self, days_back: int = 7, max_papers: int = 20) -> List[Dict]:
        """
        Descarga los papers más recientes de finanzas cuantitativas.
        
        Args:
            days_back: Días hacia atrás para buscar papers
            max_papers: Número máximo de papers por categoría
            
        Returns:
            Lista de papers con metadatos
        """
        logger.info(f"📚 Buscando papers de los últimos {days_back} días...")
        
        all_papers = []
        client = arxiv.Client()
        
        for category in self.categories:
            try:
                logger.info(f"🔍 Buscando en categoría: {category}")
                
                # Crear consulta con fecha reciente
                query = f"cat:{category}"
                
                search = arxiv.Search(
                    query=query,
                    max_results=max_papers,
                    sort_by=arxiv.SortCriterion.SubmittedDate,
                    sort_order=arxiv.SortOrder.Descending
                )
                
                papers_found = 0
                for result in client.results(search):
                    # Filtrar por fecha
                    if self._is_recent_paper(result.published, days_back):
                        paper_data = self._extract_paper_data(result)
                        if self._is_relevant_paper(paper_data):
                            all_papers.append(paper_data)
                            papers_found += 1
                            
                            if papers_found >= max_papers:
                                break
                
                logger.info(f"✅ {category}: {papers_found} papers relevantes encontrados")
                
            except Exception as e:
                logger.error(f"❌ Error buscando en {category}: {e}")
                continue
        
        logger.info(f"🎉 Total de papers descargados: {len(all_papers)}")
        return all_papers
    
    def _is_recent_paper(self, published_date: datetime, days_back: int) -> bool:
        """Verifica si el paper es reciente."""
        cutoff_date = datetime.now().replace(tzinfo=published_date.tzinfo) - timedelta(days=days_back)
        return published_date >= cutoff_date
    
    def _extract_paper_data(self, result) -> Dict:
        """Extrae datos relevantes del paper."""
        return {
            "title": result.title,
            "authors": [author.name for author in result.authors],
            "abstract": result.summary,
            "url": result.entry_id,
            "pdf_url": result.pdf_url,
            "published": result.published.isoformat(),
            "updated": result.updated.isoformat() if result.updated else None,
            "categories": result.categories,
            "source": "arxiv",
            "fetched_at": datetime.now().isoformat()
        }
    
    def _is_relevant_paper(self, paper_data: Dict) -> bool:
        """Verifica si el paper es relevante para finanzas cuantitativas."""
        text_to_check = (paper_data["title"] + " " + paper_data["abstract"]).lower()
        
        # Verificar palabras clave
        for keyword in self.keywords:
            if keyword in text_to_check:
                return True
        
        # Verificar que esté en categorías de finanzas
        finance_categories = [cat for cat in paper_data["categories"] if cat.startswith("q-fin")]
        return len(finance_categories) > 0
    
    def save_papers(self, papers: List[Dict], filename: str = None) -> str:
        """Guarda los papers en formato JSON."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"papers_{timestamp}.json"
        
        filepath = os.path.join(self.data_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(papers, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Papers guardados en: {filepath}")
        return filepath
    
    def update_vector_database(self, papers: List[Dict]):
        """Actualiza la base de datos vectorial con nuevos papers."""
        try:
            from vector_db import load_vector_store, create_vector_store
            from langchain.schema import Document
            
            logger.info("🔄 Actualizando base de datos vectorial...")
            
            # Convertir papers a documentos
            documents = []
            for paper in papers:
                doc_content = f"""
                Título: {paper['title']}
                
                Autores: {', '.join(paper['authors'])}
                
                Resumen: {paper['abstract']}
                
                Categorías: {', '.join(paper['categories'])}
                
                Publicado: {paper['published']}
                """
                
                doc = Document(
                    page_content=doc_content,
                    metadata={
                        "title": paper["title"],
                        "authors": paper["authors"],
                        "source": paper["url"],
                        "category": "Recent Research",
                        "published": paper["published"],
                        "type": "arxiv_paper"
                    }
                )
                documents.append(doc)
            
            # Cargar vector store existente
            try:
                vector_store = load_vector_store()
                logger.info("📚 Vector store existente cargado")
            except:
                vector_store = create_vector_store()
                logger.info("📚 Nuevo vector store creado")
            
            # Agregar nuevos documentos
            if hasattr(vector_store, 'add_documents'):
                vector_store.add_documents(documents)
                logger.info(f"✅ {len(documents)} papers agregados al vector store")
            else:
                logger.warning("⚠️ No se pudo actualizar el vector store")
            
        except Exception as e:
            logger.error(f"❌ Error actualizando vector database: {e}")
    
    def fetch_and_update(self, days_back: int = 7, max_papers: int = 15):
        """Proceso completo: descargar papers y actualizar base de datos."""
        logger.info("🚀 Iniciando descarga y actualización de papers...")
        
        try:
            # 1. Descargar papers
            papers = self.fetch_latest_papers(days_back, max_papers)
            
            if not papers:
                logger.info("ℹ️ No se encontraron papers nuevos")
                return
            
            # 2. Guardar papers
            filepath = self.save_papers(papers)
            
            # 3. Actualizar vector database
            self.update_vector_database(papers)
            
            # 4. Mostrar resumen
            self.show_summary(papers)
            
            logger.info("🎉 Actualización completa exitosa!")
            
        except Exception as e:
            logger.error(f"❌ Error en actualización: {e}")
    
    def show_summary(self, papers: List[Dict]):
        """Muestra resumen de papers descargados."""
        print("\n" + "="*80)
        print("📊 RESUMEN DE PAPERS DESCARGADOS / DOWNLOADED PAPERS SUMMARY")
        print("="*80)
        
        categories_count = {}
        for paper in papers:
            for cat in paper["categories"]:
                if cat.startswith("q-fin"):
                    categories_count[cat] = categories_count.get(cat, 0) + 1
        
        print(f"📄 Total de papers: {len(papers)}")
        print(f"📂 Categorías encontradas:")
        for cat, count in categories_count.items():
            cat_name = {
                "q-fin.PR": "Pricing of Securities",
                "q-fin.RM": "Risk Management", 
                "q-fin.PM": "Portfolio Management",
                "q-fin.TR": "Trading & Market Microstructure",
                "q-fin.MF": "Mathematical Finance",
                "q-fin.CP": "Computational Finance"
            }.get(cat, cat)
            print(f"   • {cat_name}: {count} papers")
        
        print(f"\n📚 Últimos 5 papers descargados:")
        for i, paper in enumerate(papers[:5]):
            print(f"{i+1}. {paper['title'][:60]}...")
            print(f"   👥 {', '.join(paper['authors'][:2])}{'...' if len(paper['authors']) > 2 else ''}")
            print()
        
        print("="*80)


def main():
    """Función principal para ejecutar la descarga de papers."""
    print("🚀 DESCARGA DE PAPERS EN TIEMPO REAL - SPINOR TECHNOLOGIES")
    print("🚀 REAL-TIME PAPER DOWNLOAD - SPINOR TECHNOLOGIES")
    print("="*80)
    
    try:
        fetcher = RealTimePaperFetcher()
        
        # Opciones de descarga
        print("\n📋 Opciones de descarga / Download options:")
        print("1. Rápida: Últimos 3 días, 10 papers máximo")
        print("2. Normal: Últimos 7 días, 15 papers máximo")
        print("3. Completa: Últimos 14 días, 25 papers máximo")
        print("4. Personalizada")
        
        choice = input("\n🔢 Selecciona opción (1-4) / Select option (1-4): ").strip()
        
        if choice == "1":
            fetcher.fetch_and_update(days_back=3, max_papers=10)
        elif choice == "2":
            fetcher.fetch_and_update(days_back=7, max_papers=15)
        elif choice == "3":
            fetcher.fetch_and_update(days_back=14, max_papers=25)
        elif choice == "4":
            days = int(input("📅 Días hacia atrás / Days back: "))
            max_papers = int(input("📄 Máximo papers por categoría / Max papers per category: "))
            fetcher.fetch_and_update(days_back=days, max_papers=max_papers)
        else:
            print("🔄 Usando configuración por defecto...")
            fetcher.fetch_and_update()
        
    except KeyboardInterrupt:
        print("\n👋 Proceso cancelado por el usuario")
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.error(f"Fatal error: {e}")


if __name__ == "__main__":
    main()
