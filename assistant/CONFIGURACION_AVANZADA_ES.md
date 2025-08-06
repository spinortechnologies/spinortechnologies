# Guía de Configuración Avanzada
# Advanced Configuration Guide

## Configuración de Rendimiento / Performance Configuration

### Modos de Rendimiento / Performance Modes

El sistema soporta tres modos de configuración:
The system supports three configuration modes:

#### 1. Modo Ligero (Lightweight)
```python
PERFORMANCE_MODE=lightweight
MAX_MEMORY_GB=2
ENABLE_GPU=false
DEFAULT_MODEL=microsoft/DialoGPT-small
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
MAX_CHUNKS=500
CHUNK_SIZE=512
```

**Características:**
- Uso mínimo de memoria RAM (< 2GB)
- Modelos más pequeños pero eficientes
- Respuestas más rápidas
- Ideal para laptops y sistemas con recursos limitados

#### 2. Modo Equilibrado (Balanced) - **RECOMENDADO**
```python
PERFORMANCE_MODE=balanced
MAX_MEMORY_GB=4
ENABLE_GPU=auto
DEFAULT_MODEL=microsoft/DialoGPT-medium
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
MAX_CHUNKS=1000
CHUNK_SIZE=1000
```

**Características:**
- Balance óptimo entre rendimiento y recursos
- Modelos de tamaño medio con buena precisión
- Auto-detección de GPU disponible
- Configuración recomendada para la mayoría de usuarios

#### 3. Modo Alto Rendimiento (High Performance)
```python
PERFORMANCE_MODE=performance
MAX_MEMORY_GB=8
ENABLE_GPU=true
DEFAULT_MODEL=microsoft/DialoGPT-large
EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2
MAX_CHUNKS=2000
CHUNK_SIZE=1500
```

**Características:**
- Máxima precisión y capacidad
- Requiere GPU dedicada (recomendado)
- Mayor uso de memoria y procesamiento
- Ideal para estaciones de trabajo y servidores

## Configuración de Idiomas / Language Configuration

### Soporte Multiidioma / Multilingual Support

```python
# Configuración principal de idioma
DEFAULT_LANGUAGE=es  # es, en, pt, fr, de, it
SUPPORT_MULTILINGUAL=true

# Modelos específicos por idioma
SPANISH_MODEL=PlanTL-GOB-ES/roberta-base-bne
ENGLISH_MODEL=microsoft/DialoGPT-medium
PORTUGUESE_MODEL=neuralmind/bert-base-portuguese-cased
FRENCH_MODEL=camembert-base
```

### Mercados Específicos / Specific Markets

```python
# Configuración para mercados hispanohablantes
PRIMARY_MARKETS=["ES", "MX", "AR", "CL", "CO", "PE"]
SECONDARY_MARKETS=["BR", "US", "EU"]

# Fuentes de datos específicas
SPANISH_DATA_SOURCES=[
    "cnmv.es",
    "bde.es", 
    "bmv.com.mx",
    "b3.com.br"
]
```

## Configuración de Base de Datos / Database Configuration

### Configuración de Vector Database

```python
# FAISS (Local - Recomendado para principiantes)
VECTOR_DB_TYPE=faiss
VECTOR_DB_PATH=./knowledge_base/vector_db
INDEX_TYPE=IndexFlatIP  # IndexFlatIP, IndexIVFFlat, IndexHNSWFlat

# ChromaDB (Avanzado)
VECTOR_DB_TYPE=chroma
CHROMA_PERSIST_DIRECTORY=./knowledge_base/chroma_db
CHROMA_COLLECTION_NAME=finance_papers

# Pinecone (Nube - Requiere API key)
VECTOR_DB_TYPE=pinecone
PINECONE_API_KEY=your_pinecone_key
PINECONE_ENVIRONMENT=us-west1-gcp
PINECONE_INDEX_NAME=finance-assistant
```

### Configuración de Actualización Automática

```python
# Frecuencia de actualización
UPDATE_FREQUENCY=daily  # daily, weekly, monthly
UPDATE_TIME=02:00  # Hora en formato HH:MM

# Filtros de calidad
MIN_CITATION_COUNT=5
MIN_PAPER_QUALITY_SCORE=0.7
PREFERRED_JOURNALS=[
    "Journal of Finance",
    "Review of Financial Studies", 
    "Journal of Financial Economics",
    "Quantitative Finance"
]

# Límites de recursos
MAX_PAPERS_PER_UPDATE=50
MAX_DOWNLOAD_SIZE_MB=100
PARALLEL_DOWNLOADS=3
```

## Configuración de APIs / API Configuration

### APIs Financieras Gratuitas / Free Financial APIs

```python
# Alpha Vantage (12,500 llamadas gratis/día)
ALPHA_VANTAGE_KEY=your_free_key_here
ALPHA_VANTAGE_ENDPOINT=https://www.alphavantage.co/query

# Yahoo Finance (Gratis, sin límite oficial)
YAHOO_FINANCE_ENABLED=true

# FRED (Federal Reserve Economic Data - Gratis)
FRED_API_KEY=your_fred_key_here
```

### APIs Premium (Opcional)

```python
# Bloomberg API (Requiere suscripción)
BLOOMBERG_API_KEY=your_bloomberg_key
BLOOMBERG_ENDPOINT=https://api.bloomberg.com

# Refinitiv (Requiere suscripción) 
REFINITIV_API_KEY=your_refinitiv_key
```

## Configuración de Seguridad / Security Configuration

### Configuración de Logs y Monitoreo

```python
# Configuración de logs
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
LOG_FILE=./logs/quant_assistant.log
LOG_ROTATION=daily
MAX_LOG_SIZE_MB=100

# Monitoreo de rendimiento
ENABLE_PERFORMANCE_MONITORING=true
PERFORMANCE_LOG_FILE=./logs/performance.log
MEMORY_MONITORING_INTERVAL=300  # segundos
```

### Configuración de Privacidad

```python
# Configuración de datos
ANONYMIZE_QUERIES=true
STORE_CONVERSATION_HISTORY=false
DATA_RETENTION_DAYS=30

# Configuración de red
PROXY_ENABLED=false
PROXY_HOST=your_proxy_host
PROXY_PORT=8080
```

## Configuración de GPU / GPU Configuration

### Configuración Automática (Recomendado)

```python
ENABLE_GPU=auto  # auto, true, false
GPU_MEMORY_FRACTION=0.7  # Usar 70% de la memoria GPU
```

### Configuración Manual

```python
# Para NVIDIA GPUs
CUDA_DEVICE=0  # Número de GPU a usar
CUDA_MEMORY_LIMIT=6144  # MB de memoria GPU

# Para Apple Silicon (M1/M2)
MPS_ENABLED=true  # Metal Performance Shaders
```

## Personalización de Prompts / Prompt Customization

### Prompts Personalizados para Mercados Específicos

```python
# Archivo: config/custom_prompts.yaml
spanish_markets:
  template: |
    Eres un especialista en mercados financieros de España y Latinoamérica.
    Contexto específico: Regulación CNMV, mercados BMV, B3, BCS.
    
    Pregunta: {question}
    Contexto: {context}
    
    Proporciona análisis específico para el mercado hispanohablante.

risk_management:
  template: |
    Análisis de riesgo cuantitativo considerando:
    - VaR y CVaR
    - Stress testing
    - Modelos de correlación
    - Regulación Basel III/IV
```

## Solución de Problemas Comunes / Common Troubleshooting

### Problemas de Memoria

```bash
# Si el sistema se queda sin memoria
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
# O en Windows:
set PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
```

### Problemas de Conexión

```python
# Configurar timeouts más largos
REQUEST_TIMEOUT=30
DOWNLOAD_TIMEOUT=120
MAX_RETRIES=3
```

### Problemas de Modelos

```bash
# Limpiar cache de modelos
rm -rf ~/.cache/huggingface/transformers
# Reinstalar dependencias
pip install --force-reinstall transformers
```

## Configuración para Desarrollo / Development Configuration

### Modo Desarrollo

```python
DEBUG_MODE=true
ENABLE_HOT_RELOAD=true
MOCK_API_CALLS=true
USE_SAMPLE_DATA=true
```

### Testing

```python
# Configuración de tests
TEST_DB_PATH=./test_db
USE_TEST_MODELS=true
MOCK_EXTERNAL_APIS=true
```

## Configuración de Deployment / Deployment Configuration

### Docker Configuration

```dockerfile
# Variables de entorno para Docker
ENV PERFORMANCE_MODE=balanced
ENV MAX_MEMORY_GB=4
ENV ENABLE_GPU=false
ENV DEFAULT_LANGUAGE=es
```

### Configuración de Producción

```python
# Para servidores de producción
PRODUCTION_MODE=true
ENABLE_CACHING=true
CACHE_TTL=3600
MAX_CONCURRENT_USERS=10
RATE_LIMITING=true
```
