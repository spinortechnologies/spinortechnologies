# Asistente de IA para Finanzas Cuantitativas SPINOR

## 📖 Guía de Instalación y Configuración en Español

### 🚀 Descripción General

El Asistente de IA SPINOR es una herramienta avanzada que combina modelos de lenguaje natural con una base de conocimientos especializada en finanzas cuantitativas. Proporciona respuestas expertas sobre:

- **Cálculo Estocástico**: Procesos de Itô, ecuaciones diferenciales estocásticas
- **Valoración de Opciones**: Black-Scholes, Monte Carlo, modelos de volatilidad
- **Gestión de Riesgos**: VaR, Expected Shortfall, stress testing
- **Teoría de Carteras**: Optimización de Markowitz, modelos de factores
- **Econofísica**: Microestructura de mercados, modelos basados en agentes

### 🛠️ Requisitos del Sistema

```bash
# Sistema operativo
Ubuntu 20.04+ / macOS 10.15+ / Windows 10+

# Hardware mínimo
RAM: 8GB (recomendado 16GB)
CPU: 4 núcleos (recomendado 8+ núcleos)
Almacenamiento: 10GB libres
GPU: Opcional (acelera el procesamiento)

# Software
Python 3.8+
Git
Docker (opcional)
```

### 📦 Instalación Paso a Paso

#### Opción 1: Instalación Estándar

```bash
# 1. Clonar el repositorio
git clone https://github.com/spinortechnologies/spinortechnologies.git
cd spinortechnologies/assistant

# 2. Crear entorno virtual
python -m venv venv

# Activar entorno (Linux/Mac)
source venv/bin/activate

# Activar entorno (Windows)
venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
export HUGGINGFACE_API_TOKEN="tu_token_aqui"
export KNOWLEDGE_BASE="/ruta/a/tu/base/conocimientos"

# 5. Inicializar base de conocimientos
python build_kb.py --update --language es

# 6. Ejecutar el asistente
python gui.py
```

#### Opción 2: Instalación con Docker

```bash
# 1. Clonar repositorio
git clone https://github.com/spinortechnologies/spinortechnologies.git
cd spinortechnologies/assistant

# 2. Construir imagen Docker
docker build -t spinor-assistant .

# 3. Ejecutar contenedor
docker run -p 8080:8080 \
  -v $(pwd)/knowledge_base:/app/knowledge_base \
  -e HUGGINGFACE_API_TOKEN="tu_token" \
  spinor-assistant
```

### 🔧 Configuración Inicial

#### 1. Obtener Token de Hugging Face

```bash
# Visita: https://huggingface.co/settings/tokens
# Crea un token de lectura
# Añádelo a tu configuración:

echo 'export HUGGINGFACE_API_TOKEN="hf_tu_token_aqui"' >> ~/.bashrc
source ~/.bashrc
```

#### 2. Configurar Base de Conocimientos

```python
# config/assistant_config.py
ASSISTANT_CONFIG = {
    "knowledge_base": {
        "auto_update": True,
        "update_frequency": "daily",  # daily, weekly, monthly
        "sources": [
            "arxiv",
            "ssrn", 
            "quantlib",
            "risk_net",
            "custom_papers"
        ],
        "languages": ["en", "es"],
        "quality_threshold": 0.8
    },
    "model": {
        "primary": "google/flan-t5-xxl",
        "fallback": ["google/flan-t5-large", "google/flan-t5-base"],
        "temperature": 0.1,
        "max_length": 512
    },
    "performance": {
        "lightweight_mode": True,
        "gpu_acceleration": True,
        "cache_responses": True
    }
}
```

### 🔄 Sistema de Actualización Automática

#### Configuración del Actualizador de Papers

```python
# auto_updater.py - Sistema de actualización automática
import schedule
import time
from datetime import datetime, timedelta
from typing import List, Dict
import arxiv
import requests
from bs4 import BeautifulSoup

class PaperAutoUpdater:
    """Sistema de actualización automática de papers financieros."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.quality_filter = PaperQualityFilter()
        self.last_update = None
        
    def setup_automatic_updates(self):
        """Configura actualizaciones automáticas según la frecuencia."""
        frequency = self.config["knowledge_base"]["update_frequency"]
        
        if frequency == "daily":
            schedule.every().day.at("02:00").do(self.update_knowledge_base)
        elif frequency == "weekly":
            schedule.every().monday.at("02:00").do(self.update_knowledge_base)
        elif frequency == "monthly":
            schedule.every().month.do(self.update_knowledge_base)
            
        print(f"✅ Actualizaciones automáticas configuradas: {frequency}")
    
    def update_knowledge_base(self):
        """Actualiza la base de conocimientos con nuevos papers."""
        print(f"🔄 Iniciando actualización automática - {datetime.now()}")
        
        try:
            # 1. Buscar nuevos papers
            new_papers = self.fetch_recent_papers()
            print(f"📄 Encontrados {len(new_papers)} papers potenciales")
            
            # 2. Filtrar por calidad
            quality_papers = self.quality_filter.filter_papers(new_papers)
            print(f"⭐ {len(quality_papers)} papers aprobaron el filtro de calidad")
            
            # 3. Procesar y añadir a la base de datos
            added_count = self.process_and_add_papers(quality_papers)
            print(f"✅ {added_count} papers añadidos exitosamente")
            
            # 4. Actualizar índices vectoriales
            self.update_vector_indices()
            print("🔍 Índices vectoriales actualizados")
            
            self.last_update = datetime.now()
            
        except Exception as e:
            print(f"❌ Error en actualización automática: {e}")
    
    def fetch_recent_papers(self) -> List[Dict]:
        """Obtiene papers recientes de múltiples fuentes."""
        all_papers = []
        
        # ArXiv - Finanzas Cuantitativas
        arxiv_papers = self.fetch_arxiv_papers()
        all_papers.extend(arxiv_papers)
        
        # SSRN - Finanzas
        ssrn_papers = self.fetch_ssrn_papers()
        all_papers.extend(ssrn_papers)
        
        # Papers personalizados
        custom_papers = self.fetch_custom_sources()
        all_papers.extend(custom_papers)
        
        return all_papers
    
    def fetch_arxiv_papers(self) -> List[Dict]:
        """Obtiene papers recientes de ArXiv."""
        search_queries = [
            "quantitative finance",
            "mathematical finance", 
            "stochastic calculus",
            "option pricing",
            "risk management",
            "portfolio optimization",
            "algorithmic trading"
        ]
        
        papers = []
        client = arxiv.Client()
        
        for query in search_queries:
            search = arxiv.Search(
                query=f"cat:q-fin.* AND ({query})",
                max_results=50,
                sort_by=arxiv.SortCriterion.SubmittedDate
            )
            
            for result in client.results(search):
                # Solo papers de los últimos 30 días
                if (datetime.now() - result.published.replace(tzinfo=None)).days <= 30:
                    papers.append({
                        "title": result.title,
                        "authors": [author.name for author in result.authors],
                        "abstract": result.summary,
                        "url": result.pdf_url,
                        "published": result.published,
                        "source": "arxiv",
                        "categories": [cat for cat in result.categories]
                    })
        
        return papers

class PaperQualityFilter:
    """Filtro inteligente de calidad de papers."""
    
    def __init__(self):
        self.quality_indicators = {
            "citation_keywords": [
                "Black-Scholes", "Monte Carlo", "Stochastic", "Volatility",
                "Risk Management", "Portfolio", "Derivatives", "Quantitative"
            ],
            "quality_journals": [
                "Journal of Finance", "Review of Financial Studies",
                "Journal of Financial Economics", "Mathematical Finance",
                "Quantitative Finance", "Journal of Risk"
            ],
            "author_metrics": {
                "min_papers": 3,
                "h_index_threshold": 10
            }
        }
    
    def filter_papers(self, papers: List[Dict]) -> List[Dict]:
        """Filtra papers por calidad y relevancia."""
        quality_papers = []
        
        for paper in papers:
            score = self.calculate_quality_score(paper)
            
            if score >= 0.7:  # Umbral de calidad
                paper["quality_score"] = score
                quality_papers.append(paper)
        
        # Ordenar por puntuación de calidad
        return sorted(quality_papers, key=lambda x: x["quality_score"], reverse=True)
    
    def calculate_quality_score(self, paper: Dict) -> float:
        """Calcula puntuación de calidad del paper."""
        score = 0.0
        
        # 1. Relevancia de palabras clave (40%)
        keyword_score = self.calculate_keyword_relevance(paper)
        score += keyword_score * 0.4
        
        # 2. Calidad de autores (30%) 
        author_score = self.calculate_author_quality(paper)
        score += author_score * 0.3
        
        # 3. Novedad del contenido (20%)
        novelty_score = self.calculate_novelty_score(paper)
        score += novelty_score * 0.2
        
        # 4. Claridad del abstract (10%)
        clarity_score = self.calculate_clarity_score(paper)
        score += clarity_score * 0.1
        
        return min(score, 1.0)
    
    def calculate_keyword_relevance(self, paper: Dict) -> float:
        """Calcula relevancia basada en palabras clave."""
        text = f"{paper['title']} {paper['abstract']}".lower()
        
        matches = 0
        for keyword in self.quality_indicators["citation_keywords"]:
            if keyword.lower() in text:
                matches += 1
        
        return min(matches / len(self.quality_indicators["citation_keywords"]), 1.0)
    
    def calculate_author_quality(self, paper: Dict) -> float:
        """Estima calidad de autores (simplificado)."""
        # En implementación real, consultar bases de datos académicas
        authors = paper.get("authors", [])
        
        if len(authors) == 0:
            return 0.2
        elif len(authors) <= 2:
            return 0.8  # Papers con pocos autores suelen ser más focalizados
        elif len(authors) <= 4:
            return 0.9
        else:
            return 0.6  # Muchos autores puede indicar menor profundidad
    
    def calculate_novelty_score(self, paper: Dict) -> float:
        """Calcula novedad del contenido."""
        # Buscar términos que indican novedad/innovación
        novelty_terms = [
            "novel", "new", "innovative", "breakthrough", "advance",
            "improved", "enhanced", "state-of-the-art"
        ]
        
        text = f"{paper['title']} {paper['abstract']}".lower()
        
        novelty_count = sum(1 for term in novelty_terms if term in text)
        return min(novelty_count / 3, 1.0)
    
    def calculate_clarity_score(self, paper: Dict) -> float:
        """Evalúa claridad del abstract."""
        abstract = paper.get("abstract", "")
        
        if len(abstract) < 100:
            return 0.3  # Abstract muy corto
        elif len(abstract) > 2000:
            return 0.6  # Abstract muy largo
        
        # Evaluar estructura y claridad
        sentences = abstract.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
        
        if 15 <= avg_sentence_length <= 25:
            return 1.0  # Longitud óptima de oraciones
        else:
            return 0.7
```
