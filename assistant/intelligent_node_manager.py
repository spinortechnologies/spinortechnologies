"""
🧠 SPINOR Intelligent Node Manager
Sistema de gestión inteligente de nodos de conocimiento con auto-limpieza
"""

import json
import time
import hashlib
import logging
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
import numpy as np

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class KnowledgeNode:
    """Nodo de conocimiento inteligente"""
    id: str
    content: str
    source: str  # 'arxiv', 'researchgate', 'manual'
    paper_id: str
    title: str
    authors: List[str]
    citations: int
    created_at: datetime
    last_accessed: datetime
    access_count: int
    relevance_score: float
    keywords: List[str]
    concepts: List[str]
    embedding_hash: str
    redundancy_group: Optional[str] = None
    
    def __post_init__(self):
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        if isinstance(self.last_accessed, str):
            self.last_accessed = datetime.fromisoformat(self.last_accessed)

    def update_access(self):
        """Actualizar estadísticas de acceso"""
        self.last_accessed = datetime.now()
        self.access_count += 1

    def calculate_importance_score(self) -> float:
        """Calcular puntuación de importancia basada en múltiples factores"""
        now = datetime.now()
        
        # Factor temporal (papers más recientes tienen mayor peso)
        days_old = (now - self.created_at).days
        temporal_factor = max(0.1, 1 / (1 + days_old / 365))  # Decae en 1 año
        
        # Factor de citaciones (normalizado)
        citation_factor = min(1.0, self.citations / 100)  # Normalizar a máximo 100 citaciones
        
        # Factor de acceso reciente
        days_since_access = (now - self.last_accessed).days
        access_factor = max(0.1, 1 / (1 + days_since_access / 30))  # Decae en 30 días
        
        # Factor de frecuencia de uso
        usage_factor = min(1.0, self.access_count / 50)  # Normalizar a máximo 50 accesos
        
        # Combinar factores
        importance = (
            temporal_factor * 0.3 +
            citation_factor * 0.4 +
            access_factor * 0.2 +
            usage_factor * 0.1
        ) * self.relevance_score
        
        return importance

    def is_redundant_with(self, other_node: 'KnowledgeNode', similarity_threshold: float = 0.85) -> bool:
        """Verificar si este nodo es redundante con otro"""
        # Comparar por hash de embedding (simplificado)
        if self.embedding_hash == other_node.embedding_hash:
            return True
        
        # Comparar conceptos clave
        self_concepts = set(self.concepts)
        other_concepts = set(other_node.concepts)
        
        if len(self_concepts) == 0 or len(other_concepts) == 0:
            return False
        
        similarity = len(self_concepts.intersection(other_concepts)) / len(self_concepts.union(other_concepts))
        return similarity > similarity_threshold

class IntelligentNodeManager:
    """Gestor inteligente de nodos de conocimiento"""
    
    def __init__(self, data_dir: str = "./data/intelligent_nodes"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.nodes: Dict[str, KnowledgeNode] = {}
        self.redundancy_groups: Dict[str, List[str]] = defaultdict(list)
        self.citation_cache: Dict[str, int] = {}
        
        # Configuración
        self.max_nodes = 5000  # Máximo número de nodos
        self.cleanup_interval_hours = 24  # Limpieza cada 24 horas
        self.min_citations_threshold = 5  # Mínimo de citaciones para mantener
        self.min_access_days = 30  # Días mínimos sin acceso antes de considerar eliminación
        self.redundancy_threshold = 0.85  # Umbral de similaridad para redundancia
        
        self.last_cleanup = datetime.now()
        
        # Cargar nodos existentes
        self.load_nodes()
        
        logger.info(f"🧠 Intelligent Node Manager iniciado con {len(self.nodes)} nodos")

    def generate_node_id(self, content: str, source: str) -> str:
        """Generar ID único para un nodo"""
        unique_string = f"{content[:100]}{source}{datetime.now().isoformat()}"
        return hashlib.md5(unique_string.encode()).hexdigest()[:16]

    def generate_embedding_hash(self, content: str) -> str:
        """Generar hash simplificado del embedding del contenido"""
        # En una implementación real, aquí usarías embeddings reales
        return hashlib.sha256(content.encode()).hexdigest()[:32]

    def extract_concepts(self, content: str, title: str) -> List[str]:
        """Extraer conceptos clave del contenido"""
        # Conceptos específicos de finanzas cuantitativas y econofísica
        quant_concepts = [
            'black-scholes', 'monte carlo', 'var', 'volatility', 'option pricing',
            'portfolio optimization', 'risk management', 'stochastic calculus',
            'econophysics', 'market microstructure', 'algorithmic trading',
            'derivatives', 'copulas', 'garch', 'jump diffusion', 'fractional brownian',
            'statistical arbitrage', 'high frequency trading', 'market making',
            'liquidity', 'bid-ask spread', 'order book', 'price discovery'
        ]
        
        content_lower = (content + " " + title).lower()
        found_concepts = []
        
        for concept in quant_concepts:
            if concept in content_lower:
                found_concepts.append(concept)
        
        return found_concepts

    def add_node(self, content: str, source: str, paper_id: str, title: str, 
                 authors: List[str], citations: int = 0, keywords: List[str] = None) -> str:
        """Agregar un nuevo nodo de conocimiento"""
        
        # Generar ID y datos del nodo
        node_id = self.generate_node_id(content, source)
        embedding_hash = self.generate_embedding_hash(content)
        concepts = self.extract_concepts(content, title)
        
        if keywords is None:
            keywords = []
        
        # Crear nodo
        node = KnowledgeNode(
            id=node_id,
            content=content,
            source=source,
            paper_id=paper_id,
            title=title,
            authors=authors,
            citations=citations,
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            access_count=1,
            relevance_score=1.0,  # Se ajustará dinámicamente
            keywords=keywords,
            concepts=concepts,
            embedding_hash=embedding_hash
        )
        
        # Verificar redundancia antes de agregar
        redundant_node = self.find_redundant_node(node)
        if redundant_node:
            logger.info(f"📋 Nodo redundante detectado, actualizando existente: {redundant_node.id}")
            self.merge_nodes(redundant_node, node)
            return redundant_node.id
        
        # Agregar nodo
        self.nodes[node_id] = node
        
        # Verificar si necesitamos limpieza
        if len(self.nodes) > self.max_nodes:
            asyncio.create_task(self.intelligent_cleanup())
        
        logger.info(f"✅ Nuevo nodo agregado: {node_id[:8]}... ({source})")
        return node_id

    def find_redundant_node(self, new_node: KnowledgeNode) -> Optional[KnowledgeNode]:
        """Encontrar nodo redundante existente"""
        for existing_node in self.nodes.values():
            if new_node.is_redundant_with(existing_node, self.redundancy_threshold):
                return existing_node
        return None

    def merge_nodes(self, existing_node: KnowledgeNode, new_node: KnowledgeNode):
        """Fusionar información de nodos redundantes"""
        # Actualizar citaciones (tomar el máximo)
        existing_node.citations = max(existing_node.citations, new_node.citations)
        
        # Fusionar conceptos y keywords
        existing_node.concepts = list(set(existing_node.concepts + new_node.concepts))
        existing_node.keywords = list(set(existing_node.keywords + new_node.keywords))
        
        # Actualizar acceso
        existing_node.update_access()
        
        # Mejorar relevancia si el nuevo nodo tiene más citaciones
        if new_node.citations > existing_node.citations * 0.8:
            existing_node.relevance_score = min(1.0, existing_node.relevance_score * 1.1)

    async def intelligent_cleanup(self):
        """Limpieza inteligente de nodos"""
        logger.info("🧹 Iniciando limpieza inteligente de nodos...")
        
        nodes_before = len(self.nodes)
        
        # Calcular puntuaciones de importancia
        node_scores = []
        for node in self.nodes.values():
            score = node.calculate_importance_score()
            node_scores.append((node.id, score))
        
        # Ordenar por puntuación (menor primero para eliminar)
        node_scores.sort(key=lambda x: x[1])
        
        # Identificar nodos para eliminación
        nodes_to_remove = []
        target_removal = len(self.nodes) - int(self.max_nodes * 0.8)  # Reducir al 80% del máximo
        
        for node_id, score in node_scores[:target_removal]:
            node = self.nodes[node_id]
            
            # Criterios de eliminación
            days_without_access = (datetime.now() - node.last_accessed).days
            
            should_remove = (
                (node.citations < self.min_citations_threshold and days_without_access > self.min_access_days) or
                (score < 0.1) or  # Puntuación muy baja
                (days_without_access > 90 and node.access_count < 3)  # Sin uso y poco acceso
            )
            
            if should_remove:
                nodes_to_remove.append(node_id)
        
        # Eliminar nodos seleccionados
        for node_id in nodes_to_remove:
            del self.nodes[node_id]
            logger.info(f"🗑️ Nodo eliminado: {node_id[:8]}...")
        
        nodes_after = len(self.nodes)
        removed_count = nodes_before - nodes_after
        
        logger.info(f"✅ Limpieza completada: {removed_count} nodos eliminados, {nodes_after} nodos restantes")
        
        # Guardar cambios
        await self.save_nodes()

    async def update_citations(self):
        """Actualizar citaciones de papers desde fuentes externas"""
        logger.info("📊 Actualizando citaciones de papers...")
        
        updated_count = 0
        for node in self.nodes.values():
            if node.source in ['arxiv', 'researchgate']:
                # Simular actualización de citaciones (aquí irían llamadas a APIs reales)
                new_citations = await self.fetch_citations(node.paper_id, node.source)
                if new_citations > node.citations:
                    node.citations = new_citations
                    updated_count += 1
        
        logger.info(f"✅ Citaciones actualizadas para {updated_count} papers")

    async def fetch_citations(self, paper_id: str, source: str) -> int:
        """Obtener número de citaciones de un paper (simulado)"""
        # En implementación real, aquí irían llamadas a APIs de ArXiv/ResearchGate
        await asyncio.sleep(0.1)  # Simular delay de API
        
        # Simular crecimiento gradual de citaciones
        if paper_id in self.citation_cache:
            base_citations = self.citation_cache[paper_id]
            growth = np.random.poisson(0.5)  # Crecimiento promedio
            return base_citations + growth
        else:
            initial_citations = np.random.poisson(10)  # Citaciones iniciales
            self.citation_cache[paper_id] = initial_citations
            return initial_citations

    def get_top_nodes(self, limit: int = 10) -> List[KnowledgeNode]:
        """Obtener los nodos más importantes"""
        node_scores = []
        for node in self.nodes.values():
            score = node.calculate_importance_score()
            node_scores.append((node, score))
        
        node_scores.sort(key=lambda x: x[1], reverse=True)
        return [node for node, score in node_scores[:limit]]

    def search_nodes(self, query: str, limit: int = 5) -> List[KnowledgeNode]:
        """Buscar nodos por contenido y conceptos"""
        query_lower = query.lower()
        matching_nodes = []
        
        for node in self.nodes.values():
            # Actualizar estadísticas de acceso
            score = 0
            
            # Buscar en título
            if query_lower in node.title.lower():
                score += 10
            
            # Buscar en conceptos
            for concept in node.concepts:
                if query_lower in concept:
                    score += 5
            
            # Buscar en contenido
            if query_lower in node.content.lower():
                score += 1
            
            if score > 0:
                node.update_access()  # Marcar como accedido
                matching_nodes.append((node, score))
        
        # Ordenar por relevancia
        matching_nodes.sort(key=lambda x: x[1], reverse=True)
        return [node for node, score in matching_nodes[:limit]]

    def get_statistics(self) -> Dict:
        """Obtener estadísticas del sistema de nodos"""
        if not self.nodes:
            return {"total_nodes": 0}
        
        total_citations = sum(node.citations for node in self.nodes.values())
        avg_citations = total_citations / len(self.nodes)
        
        source_distribution = defaultdict(int)
        concept_frequency = defaultdict(int)
        
        for node in self.nodes.values():
            source_distribution[node.source] += 1
            for concept in node.concepts:
                concept_frequency[concept] += 1
        
        top_concepts = sorted(concept_frequency.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "total_nodes": len(self.nodes),
            "total_citations": total_citations,
            "average_citations": round(avg_citations, 2),
            "source_distribution": dict(source_distribution),
            "top_concepts": top_concepts,
            "last_cleanup": self.last_cleanup.isoformat(),
            "storage_efficiency": f"{len(self.nodes)}/{self.max_nodes} ({(len(self.nodes)/self.max_nodes)*100:.1f}%)"
        }

    def save_nodes(self):
        """Guardar nodos a disco"""
        try:
            nodes_data = {}
            for node_id, node in self.nodes.items():
                nodes_data[node_id] = {
                    **asdict(node),
                    'created_at': node.created_at.isoformat(),
                    'last_accessed': node.last_accessed.isoformat()
                }
            
            with open(self.data_dir / "nodes.json", "w", encoding="utf-8") as f:
                json.dump(nodes_data, f, indent=2, ensure_ascii=False)
            
            # Guardar estadísticas
            stats = self.get_statistics()
            with open(self.data_dir / "stats.json", "w", encoding="utf-8") as f:
                json.dump(stats, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 {len(self.nodes)} nodos guardados exitosamente")
            
        except Exception as e:
            logger.error(f"❌ Error guardando nodos: {e}")

    def load_nodes(self):
        """Cargar nodos desde disco"""
        try:
            nodes_file = self.data_dir / "nodes.json"
            if nodes_file.exists():
                with open(nodes_file, "r", encoding="utf-8") as f:
                    nodes_data = json.load(f)
                
                for node_id, node_data in nodes_data.items():
                    node = KnowledgeNode(**node_data)
                    self.nodes[node_id] = node
                
                logger.info(f"📂 {len(self.nodes)} nodos cargados desde disco")
            
        except Exception as e:
            logger.error(f"❌ Error cargando nodos: {e}")

    async def auto_maintenance(self):
        """Mantenimiento automático del sistema"""
        while True:
            try:
                # Verificar si es hora de mantenimiento
                hours_since_cleanup = (datetime.now() - self.last_cleanup).total_seconds() / 3600
                
                if hours_since_cleanup >= self.cleanup_interval_hours:
                    await self.update_citations()
                    await self.intelligent_cleanup()
                    self.last_cleanup = datetime.now()
                
                # Esperar 1 hora antes del siguiente chequeo
                await asyncio.sleep(3600)
                
            except Exception as e:
                logger.error(f"❌ Error en mantenimiento automático: {e}")
                await asyncio.sleep(3600)


def create_intelligent_manager():
    """Factory function para crear el gestor inteligente"""
    return IntelligentNodeManager()


if __name__ == "__main__":
    # Prueba del sistema
    async def test_system():
        manager = IntelligentNodeManager()
        
        # Agregar algunos nodos de prueba
        node1 = manager.add_node(
            content="Black-Scholes model for option pricing using stochastic calculus and risk-neutral valuation.",
            source="arxiv",
            paper_id="1234.5678",
            title="Advanced Black-Scholes Extensions",
            authors=["Smith, J.", "Doe, A."],
            citations=45,
            keywords=["options", "pricing", "stochastic"]
        )
        
        node2 = manager.add_node(
            content="Monte Carlo simulation for portfolio risk assessment and value-at-risk calculations.",
            source="researchgate",
            paper_id="rg-567890",
            title="Monte Carlo Methods in Finance",
            authors=["Johnson, K."],
            citations=23,
            keywords=["monte carlo", "risk", "portfolio"]
        )
        
        # Mostrar estadísticas
        stats = manager.get_statistics()
        print("\n📊 Estadísticas del Sistema:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # Buscar nodos
        results = manager.search_nodes("black-scholes")
        print(f"\n🔍 Resultados de búsqueda para 'black-scholes': {len(results)} nodos")
        
        # Guardar nodos
        manager.save_nodes()
        
    asyncio.run(test_system())
