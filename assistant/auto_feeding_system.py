"""
🔄 SPINOR Auto-Feeding System
Sistema de auto-alimentación inteligente desde ArXiv y ResearchGate
"""

import asyncio
import aiohttp
import xml.etree.ElementTree as ET
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
import re
from pathlib import Path

from intelligent_node_manager import IntelligentNodeManager

logger = logging.getLogger(__name__)

@dataclass
class PaperData:
    """Datos de un paper científico"""
    id: str
    title: str
    authors: List[str]
    abstract: str
    categories: List[str]
    published_date: datetime
    citations: int
    source: str
    url: str
    keywords: List[str]

class ArXivConnector:
    """Conector para ArXiv API"""
    
    def __init__(self):
        self.base_url = "http://export.arxiv.org/api/query"
        self.session = None
        
        # Categorías de finanzas cuantitativas y econofísica
        self.target_categories = [
            "q-fin",  # Quantitative Finance
            "physics.soc-ph",  # Physics and Society (econophysics)
            "stat.AP",  # Statistics Applications
            "cs.CE",  # Computational Engineering (financial computing)
            "math.PR",  # Probability (stochastic processes)
            "math.ST",  # Statistics Theory
        ]
        
        # Keywords específicos
        self.target_keywords = [
            "quantitative finance", "econophysics", "financial modeling",
            "risk management", "portfolio optimization", "option pricing",
            "market microstructure", "algorithmic trading", "financial markets",
            "stochastic processes", "volatility modeling", "derivatives pricing",
            "credit risk", "operational risk", "market risk",
            "high frequency trading", "market making", "liquidity",
            "behavioral finance", "market efficiency", "financial networks"
        ]

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def search_papers(self, max_results: int = 50, days_back: int = 7) -> List[PaperData]:
        """Buscar papers recientes en ArXiv"""
        papers = []
        
        try:
            for category in self.target_categories:
                category_papers = await self._search_by_category(category, max_results // len(self.target_categories), days_back)
                papers.extend(category_papers)
                
                # Delay para respetar rate limits
                await asyncio.sleep(1)
            
            # Buscar por keywords
            for keyword in self.target_keywords[:5]:  # Limitar keywords para no sobrecargar
                keyword_papers = await self._search_by_keyword(keyword, 10, days_back)
                papers.extend(keyword_papers)
                await asyncio.sleep(1)
            
            # Eliminar duplicados
            unique_papers = self._remove_duplicates(papers)
            
            logger.info(f"📚 ArXiv: {len(unique_papers)} papers únicos encontrados")
            return unique_papers
            
        except Exception as e:
            logger.error(f"❌ Error buscando en ArXiv: {e}")
            return []

    async def _search_by_category(self, category: str, max_results: int, days_back: int) -> List[PaperData]:
        """Buscar papers por categoría"""
        try:
            # Construir query
            start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y%m%d")
            query = f"cat:{category}"
            
            params = {
                "search_query": query,
                "start": 0,
                "max_results": max_results,
                "sortBy": "lastUpdatedDate",
                "sortOrder": "descending"
            }
            
            async with self.session.get(self.base_url, params=params) as response:
                if response.status == 200:
                    content = await response.text()
                    return self._parse_arxiv_response(content, "arxiv")
                else:
                    logger.warning(f"⚠️ ArXiv API error {response.status} para categoría {category}")
                    return []
                    
        except Exception as e:
            logger.error(f"❌ Error en búsqueda por categoría {category}: {e}")
            return []

    async def _search_by_keyword(self, keyword: str, max_results: int, days_back: int) -> List[PaperData]:
        """Buscar papers por keyword"""
        try:
            # Query en abstract y título
            query = f"abs:\"{keyword}\" OR ti:\"{keyword}\""
            
            params = {
                "search_query": query,
                "start": 0,
                "max_results": max_results,
                "sortBy": "lastUpdatedDate",
                "sortOrder": "descending"
            }
            
            async with self.session.get(self.base_url, params=params) as response:
                if response.status == 200:
                    content = await response.text()
                    return self._parse_arxiv_response(content, "arxiv")
                else:
                    logger.warning(f"⚠️ ArXiv API error {response.status} para keyword {keyword}")
                    return []
                    
        except Exception as e:
            logger.error(f"❌ Error en búsqueda por keyword {keyword}: {e}")
            return []

    def _parse_arxiv_response(self, xml_content: str, source: str) -> List[PaperData]:
        """Parsear respuesta XML de ArXiv"""
        papers = []
        
        try:
            # Definir namespace
            namespaces = {
                'atom': 'http://www.w3.org/2005/Atom',
                'arxiv': 'http://arxiv.org/schemas/atom'
            }
            
            root = ET.fromstring(xml_content)
            entries = root.findall('atom:entry', namespaces)
            
            for entry in entries:
                try:
                    # Extraer información básica
                    title_elem = entry.find('atom:title', namespaces)
                    title = title_elem.text.strip() if title_elem is not None else "Sin título"
                    
                    # Limpiar título (ArXiv incluye saltos de línea)
                    title = re.sub(r'\s+', ' ', title)
                    
                    # ID del paper
                    id_elem = entry.find('atom:id', namespaces)
                    paper_url = id_elem.text if id_elem is not None else ""
                    paper_id = paper_url.split('/')[-1] if paper_url else f"arxiv_{int(time.time())}"
                    
                    # Autores
                    authors = []
                    author_elems = entry.findall('atom:author', namespaces)
                    for author_elem in author_elems:
                        name_elem = author_elem.find('atom:name', namespaces)
                        if name_elem is not None:
                            authors.append(name_elem.text.strip())
                    
                    # Abstract
                    summary_elem = entry.find('atom:summary', namespaces)
                    abstract = summary_elem.text.strip() if summary_elem is not None else ""
                    abstract = re.sub(r'\s+', ' ', abstract)
                    
                    # Fecha de publicación
                    published_elem = entry.find('atom:published', namespaces)
                    published_date = datetime.now()
                    if published_elem is not None:
                        try:
                            published_date = datetime.fromisoformat(published_elem.text.replace('Z', '+00:00'))
                        except:
                            pass
                    
                    # Categorías
                    categories = []
                    category_elems = entry.findall('atom:category', namespaces)
                    for cat_elem in category_elems:
                        term = cat_elem.get('term')
                        if term:
                            categories.append(term)
                    
                    # Extraer keywords del abstract y título
                    keywords = self._extract_keywords(title + " " + abstract)
                    
                    # Crear objeto PaperData
                    paper = PaperData(
                        id=paper_id,
                        title=title,
                        authors=authors,
                        abstract=abstract,
                        categories=categories,
                        published_date=published_date,
                        citations=0,  # ArXiv no provee citaciones directamente
                        source=source,
                        url=paper_url,
                        keywords=keywords
                    )
                    
                    papers.append(paper)
                    
                except Exception as e:
                    logger.warning(f"⚠️ Error parseando entrada de ArXiv: {e}")
                    continue
            
            logger.info(f"✅ Parseados {len(papers)} papers de ArXiv")
            return papers
            
        except ET.ParseError as e:
            logger.error(f"❌ Error parseando XML de ArXiv: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Error inesperado parseando ArXiv: {e}")
            return []

    def _extract_keywords(self, text: str) -> List[str]:
        """Extraer keywords relevantes del texto"""
        text_lower = text.lower()
        found_keywords = []
        
        for keyword in self.target_keywords:
            if keyword.lower() in text_lower:
                found_keywords.append(keyword)
        
        # Keywords adicionales comunes en finanzas
        additional_keywords = [
            "volatility", "correlation", "regression", "optimization", "simulation",
            "neural network", "machine learning", "deep learning", "artificial intelligence",
            "blockchain", "cryptocurrency", "bitcoin", "ethereum", "defi",
            "esg", "sustainable finance", "green finance", "climate risk"
        ]
        
        for keyword in additional_keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
        
        return list(set(found_keywords))  # Eliminar duplicados

    def _remove_duplicates(self, papers: List[PaperData]) -> List[PaperData]:
        """Eliminar papers duplicados"""
        seen_ids = set()
        seen_titles = set()
        unique_papers = []
        
        for paper in papers:
            # Normalizar título para comparación
            normalized_title = re.sub(r'[^\w\s]', '', paper.title.lower()).strip()
            
            if paper.id not in seen_ids and normalized_title not in seen_titles:
                seen_ids.add(paper.id)
                seen_titles.add(normalized_title)
                unique_papers.append(paper)
        
        return unique_papers

class ResearchGateConnector:
    """Conector para ResearchGate (simulado debido a limitaciones de API)"""
    
    def __init__(self):
        # ResearchGate no tiene API pública, simularemos la funcionalidad
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def search_papers(self, max_results: int = 30, days_back: int = 7) -> List[PaperData]:
        """Simular búsqueda en ResearchGate"""
        # En una implementación real, aquí usarías web scraping o una API no oficial
        logger.info("🔍 ResearchGate: Simulando búsqueda de papers...")
        
        # Datos simulados de ejemplo
        simulated_papers = [
            PaperData(
                id="rg_001",
                title="High-Frequency Trading and Market Volatility: An Econophysics Approach",
                authors=["García, M.", "López, A.", "Chen, L."],
                abstract="This study analyzes the impact of high-frequency trading on market volatility using econophysics models and statistical mechanics principles.",
                categories=["econophysics", "market microstructure"],
                published_date=datetime.now() - timedelta(days=2),
                citations=15,
                source="researchgate",
                url="https://researchgate.net/publication/rg_001",
                keywords=["high frequency trading", "volatility", "econophysics"]
            ),
            PaperData(
                id="rg_002",
                title="Machine Learning Applications in Portfolio Risk Management",
                authors=["Smith, R.", "Johnson, K."],
                abstract="We present novel machine learning techniques for portfolio optimization and risk assessment in quantitative finance.",
                categories=["machine learning", "portfolio management"],
                published_date=datetime.now() - timedelta(days=4),
                citations=8,
                source="researchgate",
                url="https://researchgate.net/publication/rg_002",
                keywords=["machine learning", "portfolio optimization", "risk management"]
            )
        ]
        
        await asyncio.sleep(1)  # Simular delay de red
        logger.info(f"📚 ResearchGate: {len(simulated_papers)} papers simulados")
        return simulated_papers

class AutoFeedingSystem:
    """Sistema principal de auto-alimentación"""
    
    def __init__(self, node_manager: IntelligentNodeManager):
        self.node_manager = node_manager
        self.data_dir = Path("./data/auto_feeding")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuración
        self.feeding_interval_hours = 6  # Alimentar cada 6 horas
        self.max_papers_per_session = 100
        self.days_back = 7
        
        self.last_feeding = datetime.now() - timedelta(hours=12)  # Forzar primera alimentación
        
        # Estadísticas
        self.stats = {
            "total_papers_processed": 0,
            "papers_added": 0,
            "papers_rejected": 0,
            "last_feeding": None,
            "sources": {"arxiv": 0, "researchgate": 0},
            "categories_distribution": {},
        }
        
        self.load_stats()

    async def start_auto_feeding(self):
        """Iniciar el sistema de auto-alimentación"""
        logger.info("🚀 Iniciando sistema de auto-alimentación inteligente...")
        
        while True:
            try:
                # Verificar si es hora de alimentar
                hours_since_feeding = (datetime.now() - self.last_feeding).total_seconds() / 3600
                
                if hours_since_feeding >= self.feeding_interval_hours:
                    await self.feed_new_papers()
                    self.last_feeding = datetime.now()
                    self.save_stats()
                
                # Esperar 30 minutos antes del siguiente chequeo
                await asyncio.sleep(1800)
                
            except Exception as e:
                logger.error(f"❌ Error en auto-alimentación: {e}")
                await asyncio.sleep(3600)  # Esperar 1 hora en caso de error

    async def feed_new_papers(self):
        """Alimentar el sistema con nuevos papers"""
        logger.info("🍽️ Iniciando sesión de alimentación...")
        
        session_stats = {
            "papers_found": 0,
            "papers_added": 0,
            "papers_rejected": 0
        }
        
        try:
            # Buscar en ArXiv
            async with ArXivConnector() as arxiv:
                arxiv_papers = await arxiv.search_papers(
                    max_results=self.max_papers_per_session // 2,
                    days_back=self.days_back
                )
                session_stats["papers_found"] += len(arxiv_papers)
                
                # Procesar papers de ArXiv
                for paper in arxiv_papers:
                    if await self.process_paper(paper):
                        session_stats["papers_added"] += 1
                        self.stats["sources"]["arxiv"] += 1
                    else:
                        session_stats["papers_rejected"] += 1
            
            # Buscar en ResearchGate
            async with ResearchGateConnector() as rg:
                rg_papers = await rg.search_papers(
                    max_results=self.max_papers_per_session // 2,
                    days_back=self.days_back
                )
                session_stats["papers_found"] += len(rg_papers)
                
                # Procesar papers de ResearchGate
                for paper in rg_papers:
                    if await self.process_paper(paper):
                        session_stats["papers_added"] += 1
                        self.stats["sources"]["researchgate"] += 1
                    else:
                        session_stats["papers_rejected"] += 1
            
            # Actualizar estadísticas globales
            self.stats["total_papers_processed"] += session_stats["papers_found"]
            self.stats["papers_added"] += session_stats["papers_added"]
            self.stats["papers_rejected"] += session_stats["papers_rejected"]
            self.stats["last_feeding"] = datetime.now().isoformat()
            
            logger.info(f"✅ Sesión completada: {session_stats['papers_added']} papers agregados, {session_stats['papers_rejected']} rechazados")
            
        except Exception as e:
            logger.error(f"❌ Error en sesión de alimentación: {e}")

    async def process_paper(self, paper: PaperData) -> bool:
        """Procesar un paper individual"""
        try:
            # Verificar calidad del paper
            if not self.is_paper_relevant(paper):
                return False
            
            # Crear contenido para el nodo
            content = f"{paper.title}\n\nAbstract: {paper.abstract}"
            
            # Agregar al gestor de nodos
            node_id = self.node_manager.add_node(
                content=content,
                source=paper.source,
                paper_id=paper.id,
                title=paper.title,
                authors=paper.authors,
                citations=paper.citations,
                keywords=paper.keywords
            )
            
            # Actualizar estadísticas de categorías
            for category in paper.categories:
                self.stats["categories_distribution"][category] = \
                    self.stats["categories_distribution"].get(category, 0) + 1
            
            logger.debug(f"✅ Paper procesado: {paper.title[:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error procesando paper {paper.id}: {e}")
            return False

    def is_paper_relevant(self, paper: PaperData) -> bool:
        """Verificar si un paper es relevante para nuestro sistema"""
        
        # Verificar longitud mínima del abstract
        if len(paper.abstract) < 100:
            return False
        
        # Verificar que tenga palabras clave relevantes
        if not paper.keywords:
            return False
        
        # Verificar categorías relevantes
        relevant_categories = [
            "q-fin", "physics.soc-ph", "stat.AP", "cs.CE", "math.PR", "math.ST",
            "econophysics", "machine learning", "portfolio management"
        ]
        
        has_relevant_category = any(cat in paper.categories for cat in relevant_categories)
        
        # Verificar palabras clave en título o abstract
        finance_terms = [
            "finance", "financial", "market", "trading", "investment", "portfolio",
            "risk", "option", "derivative", "econom", "volatility", "price"
        ]
        
        text = (paper.title + " " + paper.abstract).lower()
        has_finance_terms = any(term in text for term in finance_terms)
        
        return has_relevant_category or has_finance_terms

    def get_feeding_stats(self) -> Dict:
        """Obtener estadísticas del sistema de alimentación"""
        return {
            **self.stats,
            "feeding_interval_hours": self.feeding_interval_hours,
            "max_papers_per_session": self.max_papers_per_session,
            "next_feeding_in_hours": self.feeding_interval_hours - 
                ((datetime.now() - self.last_feeding).total_seconds() / 3600)
        }

    def save_stats(self):
        """Guardar estadísticas"""
        try:
            with open(self.data_dir / "feeding_stats.json", "w", encoding="utf-8") as f:
                json.dump(self.stats, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"❌ Error guardando estadísticas: {e}")

    def load_stats(self):
        """Cargar estadísticas"""
        try:
            stats_file = self.data_dir / "feeding_stats.json"
            if stats_file.exists():
                with open(stats_file, "r", encoding="utf-8") as f:
                    saved_stats = json.load(f)
                    self.stats.update(saved_stats)
                    
                    if self.stats.get("last_feeding"):
                        self.last_feeding = datetime.fromisoformat(self.stats["last_feeding"])
        except Exception as e:
            logger.error(f"❌ Error cargando estadísticas: {e}")


async def create_auto_feeding_system():
    """Factory function para crear el sistema de auto-alimentación"""
    node_manager = IntelligentNodeManager()
    return AutoFeedingSystem(node_manager)


if __name__ == "__main__":
    # Prueba del sistema
    async def test_auto_feeding():
        system = await create_auto_feeding_system()
        
        # Ejecutar una sesión de alimentación
        await system.feed_new_papers()
        
        # Mostrar estadísticas
        stats = system.get_feeding_stats()
        print("\n📊 Estadísticas de Auto-alimentación:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # Mostrar estadísticas del gestor de nodos
        node_stats = system.node_manager.get_statistics()
        print("\n🧠 Estadísticas del Gestor de Nodos:")
        for key, value in node_stats.items():
            print(f"  {key}: {value}")
    
    asyncio.run(test_auto_feeding())
