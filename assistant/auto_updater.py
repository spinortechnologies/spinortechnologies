#!/usr/bin/env python3
"""
Sistema de Actualización Automática de Papers
Actualiza la base de conocimientos con nuevos papers de finanzas cuantitativas
"""

import os
import schedule
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import arxiv
import requests
import json
from dataclasses import dataclass
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_updater.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class PaperMetadata:
    """Metadatos de un paper académico."""
    title: str
    authors: List[str]
    abstract: str
    url: str
    published: datetime
    source: str
    categories: List[str]
    quality_score: float = 0.0
    language: str = "en"


class LightweightModelManager:
    """Gestor de modelos optimizado para eficiencia."""
    
    def __init__(self):
        self.model_configs = {
            "ultralight": {
                "model": "google/flan-t5-small",
                "max_tokens": 256,
                "batch_size": 32,
                "memory_usage": "low"
            },
            "balanced": {
                "model": "google/flan-t5-base", 
                "max_tokens": 512,
                "batch_size": 16,
                "memory_usage": "medium"
            },
            "performance": {
                "model": "google/flan-t5-large",
                "max_tokens": 1024,
                "batch_size": 8,
                "memory_usage": "high"
            }
        }
        
    def select_optimal_model(self, query_complexity: str, available_memory: float) -> Dict:
        """Selecciona el modelo óptimo basado en recursos disponibles."""
        
        if available_memory < 4.0:  # GB
            return self.model_configs["ultralight"]
        elif available_memory < 8.0:
            return self.model_configs["balanced"] 
        else:
            return self.model_configs["performance"]
    
    def get_model_efficiency_score(self, model_name: str) -> float:
        """Calcula puntuación de eficiencia del modelo."""
        efficiency_scores = {
            "google/flan-t5-small": 0.95,
            "google/flan-t5-base": 0.80,
            "google/flan-t5-large": 0.65,
            "google/flan-t5-xl": 0.45,
            "google/flan-t5-xxl": 0.30
        }
        return efficiency_scores.get(model_name, 0.5)


class IntelligentPaperFilter:
    """Filtro inteligente que balancea calidad y eficiencia."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.quality_threshold = config.get("quality_threshold", 0.75)
        self.max_papers_per_update = config.get("max_papers_per_update", 100)
        
        # Palabras clave por categoría con pesos
        self.keyword_weights = {
            "core_finance": {
                "keywords": ["quantitative finance", "mathematical finance", "financial mathematics"],
                "weight": 1.0
            },
            "derivatives": {
                "keywords": ["option pricing", "black-scholes", "derivatives", "volatility modeling"],
                "weight": 0.9
            },
            "risk_management": {
                "keywords": ["risk management", "var", "expected shortfall", "stress testing"],
                "weight": 0.9
            },
            "portfolio": {
                "keywords": ["portfolio optimization", "markowitz", "asset allocation"],
                "weight": 0.8
            },
            "algorithmic": {
                "keywords": ["algorithmic trading", "high frequency", "market making"],
                "weight": 0.7
            },
            "econophysics": {
                "keywords": ["econophysics", "agent-based", "complex systems"],
                "weight": 0.6
            }
        }
    
    def filter_and_rank_papers(self, papers: List[Dict]) -> List[PaperMetadata]:
        """Filtra y rankea papers por calidad y relevancia."""
        scored_papers = []
        
        for paper_data in papers:
            paper = PaperMetadata(**paper_data)
            
            # Calcular puntuación compuesta
            quality_score = self._calculate_quality_score(paper)
            relevance_score = self._calculate_relevance_score(paper)
            recency_score = self._calculate_recency_score(paper)
            
            # Puntuación final ponderada
            final_score = (
                quality_score * 0.4 +
                relevance_score * 0.4 +
                recency_score * 0.2
            )
            
            paper.quality_score = final_score
            
            if final_score >= self.quality_threshold:
                scored_papers.append(paper)
        
        # Ordenar por puntuación y limitar cantidad
        scored_papers.sort(key=lambda x: x.quality_score, reverse=True)
        return scored_papers[:self.max_papers_per_update]
    
    def _calculate_quality_score(self, paper: PaperMetadata) -> float:
        """Calcula puntuación de calidad."""
        score = 0.0
        
        # 1. Calidad del título
        title_score = self._evaluate_title_quality(paper.title)
        score += title_score * 0.3
        
        # 2. Calidad del abstract
        abstract_score = self._evaluate_abstract_quality(paper.abstract)
        score += abstract_score * 0.4
        
        # 3. Calidad de autores (simplificado)
        author_score = self._evaluate_author_quality(paper.authors)
        score += author_score * 0.3
        
        return min(score, 1.0)
    
    def _calculate_relevance_score(self, paper: PaperMetadata) -> float:
        """Calcula relevancia para finanzas cuantitativas."""
        text = f"{paper.title} {paper.abstract}".lower()
        relevance_score = 0.0
        
        for category, info in self.keyword_weights.items():
            category_score = 0.0
            for keyword in info["keywords"]:
                if keyword.lower() in text:
                    category_score += 1
            
            # Normalizar y aplicar peso
            if info["keywords"]:
                category_score = (category_score / len(info["keywords"])) * info["weight"]
                relevance_score += category_score
        
        # Normalizar puntuación final
        max_possible_score = sum(cat["weight"] for cat in self.keyword_weights.values())
        return min(relevance_score / max_possible_score, 1.0)
    
    def _calculate_recency_score(self, paper: PaperMetadata) -> float:
        """Calcula puntuación por recencia."""
        if not paper.published:
            return 0.5
        
        days_old = (datetime.now() - paper.published.replace(tzinfo=None)).days
        
        if days_old <= 7:
            return 1.0
        elif days_old <= 30:
            return 0.8
        elif days_old <= 90:
            return 0.6
        elif days_old <= 180:
            return 0.4
        else:
            return 0.2
    
    def _evaluate_title_quality(self, title: str) -> float:
        """Evalúa calidad del título."""
        if not title:
            return 0.0
        
        # Longitud óptima del título
        length_score = 1.0
        if len(title) < 20:
            length_score = 0.5
        elif len(title) > 150:
            length_score = 0.7
        
        # Presencia de términos técnicos
        technical_terms = [
            "model", "analysis", "approach", "method", "framework",
            "evidence", "empirical", "theoretical", "estimation"
        ]
        
        technical_score = sum(1 for term in technical_terms if term in title.lower())
        technical_score = min(technical_score / 3, 1.0)
        
        return (length_score * 0.6) + (technical_score * 0.4)
    
    def _evaluate_abstract_quality(self, abstract: str) -> float:
        """Evalúa calidad del abstract."""
        if not abstract:
            return 0.0
        
        # Longitud óptima
        length = len(abstract)
        if 150 <= length <= 1500:
            length_score = 1.0
        elif length < 150:
            length_score = length / 150
        else:
            length_score = max(0.5, 1500 / length)
        
        # Estructura del abstract
        structure_indicators = [
            "we propose", "we show", "we find", "results show",
            "conclusion", "methodology", "data", "empirical"
        ]
        
        structure_score = sum(1 for indicator in structure_indicators 
                            if indicator in abstract.lower())
        structure_score = min(structure_score / 4, 1.0)
        
        return (length_score * 0.6) + (structure_score * 0.4)
    
    def _evaluate_author_quality(self, authors: List[str]) -> float:
        """Evalúa calidad de autores (simplificado)."""
        if not authors:
            return 0.3
        
        num_authors = len(authors)
        
        # Número óptimo de autores para papers de finanzas
        if 1 <= num_authors <= 3:
            return 1.0
        elif num_authors <= 5:
            return 0.8
        else:
            return 0.6


class AutoPaperUpdater:
    """Sistema principal de actualización automática."""
    
    def __init__(self, config_path: str = "config/updater_config.json"):
        self.config = self._load_config(config_path)
        self.filter = IntelligentPaperFilter(self.config.get("filter", {}))
        self.model_manager = LightweightModelManager()
        self.knowledge_base_path = Path(self.config.get("knowledge_base_path", "./knowledge_base"))
        self.knowledge_base_path.mkdir(exist_ok=True)
        
    def _load_config(self, config_path: str) -> Dict:
        """Carga configuración desde archivo JSON."""
        default_config = {
            "update_frequency": "daily",
            "max_papers_per_update": 50,
            "quality_threshold": 0.75,
            "sources": ["arxiv", "ssrn"],
            "categories": ["q-fin.*", "math.PR", "stat.ML"],
            "languages": ["en", "es"],
            "lightweight_mode": True,
            "auto_optimize": True
        }
        
        try:
            with open(config_path, 'r') as f:
                user_config = json.load(f)
            default_config.update(user_config)
        except FileNotFoundError:
            logger.warning(f"Archivo de configuración no encontrado: {config_path}")
            logger.info("Usando configuración por defecto")
        
        return default_config
    
    def setup_scheduler(self):
        """Configura el programador de actualizaciones."""
        frequency = self.config["update_frequency"]
        
        if frequency == "hourly":
            schedule.every().hour.do(self.run_update)
        elif frequency == "daily":
            schedule.every().day.at("02:00").do(self.run_update)
        elif frequency == "weekly":
            schedule.every().monday.at("02:00").do(self.run_update)
        elif frequency == "monthly":
            schedule.every().month.do(self.run_update)
        
        logger.info(f"📅 Actualizaciones programadas: {frequency}")
    
    def run_update(self):
        """Ejecuta actualización completa de la base de conocimientos."""
        logger.info("🔄 Iniciando actualización automática de papers")
        start_time = datetime.now()
        
        try:
            # 1. Recopilar papers recientes
            raw_papers = self._fetch_recent_papers()
            logger.info(f"📚 Recopilados {len(raw_papers)} papers en bruto")
            
            # 2. Filtrar y rankear por calidad
            quality_papers = self.filter.filter_and_rank_papers(raw_papers)
            logger.info(f"⭐ {len(quality_papers)} papers aprobaron filtros de calidad")
            
            # 3. Procesar y guardar papers
            processed_count = self._process_papers(quality_papers)
            
            # 4. Actualizar índices vectoriales
            self._update_vector_indices()
            
            # 5. Optimizar modelo si está habilitado
            if self.config.get("auto_optimize", False):
                self._optimize_model_selection()
            
            duration = datetime.now() - start_time
            logger.info(f"✅ Actualización completada en {duration}")
            logger.info(f"📊 {processed_count} papers añadidos a la base de conocimientos")
            
            # Guardar estadísticas
            self._save_update_stats({
                "timestamp": start_time.isoformat(),
                "papers_processed": processed_count,
                "duration_seconds": duration.total_seconds(),
                "quality_threshold": self.config["quality_threshold"]
            })
            
        except Exception as e:
            logger.error(f"❌ Error en actualización automática: {e}")
    
    def _fetch_recent_papers(self) -> List[Dict]:
        """Recopila papers recientes de múltiples fuentes."""
        all_papers = []
        
        if "arxiv" in self.config["sources"]:
            arxiv_papers = self._fetch_arxiv_papers()
            all_papers.extend(arxiv_papers)
            logger.info(f"📄 ArXiv: {len(arxiv_papers)} papers")
        
        if "ssrn" in self.config["sources"]:
            ssrn_papers = self._fetch_ssrn_papers()
            all_papers.extend(ssrn_papers)
            logger.info(f"📄 SSRN: {len(ssrn_papers)} papers")
        
        return all_papers
    
    def _fetch_arxiv_papers(self) -> List[Dict]:
        """Obtiene papers recientes de ArXiv."""
        papers = []
        client = arxiv.Client()
        
        # Consultas especializadas en finanzas cuantitativas
        search_queries = [
            "cat:q-fin.PR",  # Pricing of Securities
            "cat:q-fin.RM",  # Risk Management  
            "cat:q-fin.PM",  # Portfolio Management
            "cat:q-fin.TR",  # Trading and Market Microstructure
            "cat:q-fin.MF",  # Mathematical Finance
            "cat:q-fin.CP",  # Computational Finance
        ]
        
        for query in search_queries:
            try:
                search = arxiv.Search(
                    query=query,
                    max_results=20,
                    sort_by=arxiv.SortCriterion.SubmittedDate
                )
                
                for result in client.results(search):
                    # Solo papers de los últimos 30 días
                    days_old = (datetime.now() - result.published.replace(tzinfo=None)).days
                    if days_old <= 30:
                        papers.append({
                            "title": result.title,
                            "authors": [author.name for author in result.authors],
                            "abstract": result.summary,
                            "url": result.pdf_url,
                            "published": result.published,
                            "source": "arxiv",
                            "categories": result.categories
                        })
                
                time.sleep(1)  # Respetar límites de API
                
            except Exception as e:
                logger.warning(f"Error fetching from ArXiv query {query}: {e}")
        
        return papers
    
    def _fetch_ssrn_papers(self) -> List[Dict]:
        """Obtiene papers de SSRN (implementación simplificada)."""
        # En una implementación real, usarías la API de SSRN
        # Por ahora, retornamos lista vacía
        logger.info("SSRN fetching no implementado aún")
        return []
    
    def _process_papers(self, papers: List[PaperMetadata]) -> int:
        """Procesa y guarda papers en la base de conocimientos."""
        processed_count = 0
        
        for paper in papers:
            try:
                # Extraer texto completo si es posible
                full_text = self._extract_paper_text(paper.url)
                
                # Crear entrada en la base de datos
                paper_data = {
                    "id": self._generate_paper_id(paper),
                    "title": paper.title,
                    "authors": paper.authors,
                    "abstract": paper.abstract,
                    "full_text": full_text,
                    "url": paper.url,
                    "published": paper.published.isoformat(),
                    "source": paper.source,
                    "categories": paper.categories,
                    "quality_score": paper.quality_score,
                    "added_date": datetime.now().isoformat()
                }
                
                # Guardar en archivo JSON
                paper_file = self.knowledge_base_path / f"{paper_data['id']}.json"
                with open(paper_file, 'w', encoding='utf-8') as f:
                    json.dump(paper_data, f, indent=2, ensure_ascii=False)
                
                processed_count += 1
                
            except Exception as e:
                logger.warning(f"Error procesando paper {paper.title}: {e}")
        
        return processed_count
    
    def _extract_paper_text(self, url: str) -> str:
        """Extrae texto completo del paper."""
        try:
            from data_loader import extract_text_from_pdf
            return extract_text_from_pdf(url)
        except Exception as e:
            logger.warning(f"No se pudo extraer texto de {url}: {e}")
            return ""
    
    def _generate_paper_id(self, paper: PaperMetadata) -> str:
        """Genera ID único para el paper."""
        import hashlib
        text = f"{paper.title}{paper.authors[0] if paper.authors else ''}{paper.published}"
        return hashlib.md5(text.encode()).hexdigest()[:12]
    
    def _update_vector_indices(self):
        """Actualiza índices vectoriales para búsqueda."""
        try:
            from vector_db import rebuild_vector_store
            rebuild_vector_store(str(self.knowledge_base_path))
            logger.info("🔍 Índices vectoriales actualizados")
        except Exception as e:
            logger.warning(f"Error actualizando índices: {e}")
    
    def _optimize_model_selection(self):
        """Optimiza selección de modelo basado en uso actual."""
        import psutil
        
        # Obtener uso actual de memoria
        memory_usage = psutil.virtual_memory().percent
        available_memory = psutil.virtual_memory().available / (1024**3)  # GB
        
        # Seleccionar modelo óptimo
        optimal_config = self.model_manager.select_optimal_model(
            "medium", available_memory
        )
        
        logger.info(f"🎯 Modelo optimizado seleccionado: {optimal_config['model']}")
        logger.info(f"💾 Memoria disponible: {available_memory:.1f}GB")
    
    def _save_update_stats(self, stats: Dict):
        """Guarda estadísticas de actualización."""
        stats_file = self.knowledge_base_path / "update_stats.jsonl"
        
        with open(stats_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(stats) + "\n")
    
    def start_continuous_updates(self):
        """Inicia el sistema de actualizaciones continuas."""
        self.setup_scheduler()
        
        logger.info("🚀 Sistema de actualización automática iniciado")
        logger.info(f"📋 Configuración: {self.config}")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Revisar cada minuto
        except KeyboardInterrupt:
            logger.info("🛑 Sistema de actualización detenido por el usuario")


def main():
    """Función principal para ejecutar el actualizador."""
    updater = AutoPaperUpdater()
    
    # Opción 1: Ejecutar actualización inmediata
    if "--now" in sys.argv:
        updater.run_update()
    
    # Opción 2: Iniciar modo continuo
    else:
        updater.start_continuous_updates()


if __name__ == "__main__":
    import sys
    main()
