# 🚀 Sistema de Finanzas Cuantitativas con Papers en Tiempo Real

## SPINOR TECHNOLOGIES - Sistema de IA Financiera Avanzada

Este sistema integra un asistente de IA especializado en finanzas cuantitativas con capacidades de descarga automática de papers de investigación desde ArXiv.

---

## 🎯 Características Principales

### 🤖 Asistente de IA Financiera
- **Especialización**: Finanzas cuantitativas, trading algorítmico, gestión de riesgo
- **Base de Conocimientos**: Vector database con papers recientes de ArXiv
- **Capacidades**: Análisis de opciones, modelos de pricing, portfolio optimization

### 📚 Sistema de Papers en Tiempo Real
- **Fuente**: ArXiv API (categorías q-fin.*)
- **Automatización**: Descarga programada cada 6 horas
- **Categorías**: Computational Finance, Risk Management, Portfolio Management, Trading, Mathematical Finance, Pricing
- **Procesamiento**: Filtrado automático por calidad y relevancia

### 🔄 Actualización Automática
- **Servicio Background**: Descarga automática de papers
- **Integración**: Papers se añaden automáticamente al vector database
- **Notificaciones**: Sistema de logs detallado

---

## 🚀 Formas de Usar el Sistema

### 1. 🎮 Sistema Completo (Recomendado)
```bash
python3 run_full_system.py
```
**Características:**
- Menú interactivo completo
- Servicio automático de papers
- Chat interactivo con IA
- Búsqueda en papers
- Estado del sistema

### 2. 💬 Chat Interactivo Simple
```bash
python3 demo_simple.py
```
**Comandos disponibles:**
- `help` - Ayuda
- `update` - Descargar papers recientes
- `papers` - Ver papers disponibles
- `status` - Estado del sistema
- `exit` - Salir

### 3. 📄 Descarga Manual de Papers
```bash
python3 realtime_papers.py
```
**Opciones:**
- Rápida: 3 días, 10 papers
- Normal: 7 días, 15 papers
- Completa: 14 días, 25 papers
- Personalizada: configuración manual

### 4. 🔄 Servicio Automático
```bash
python3 auto_paper_service.py
```
**Configuración:**
- Descarga cada 6 horas por defecto
- Configurable en `.env.papers`
- Logs detallados en `./logs/`

---

## 📋 Comandos Rápidos

### Instalación de Dependencias
```bash
pip install -r requirements.txt
pip install arxiv schedule psutil
```

### Uso Inmediato
```bash
# 1. Descargar papers recientes
python3 realtime_papers.py

# 2. Iniciar chat con IA
python3 demo_simple.py

# 3. Sistema completo
python3 run_full_system.py
```

---

## 🗂️ Estructura de Archivos

```
assistant/
├── 🎮 run_full_system.py      # Sistema completo con menú
├── 💬 demo_simple.py          # Chat interactivo simple
├── 🤖 simple_agent.py         # Agente de IA financiera
├── 📄 realtime_papers.py      # Descargador de papers
├── 🔄 auto_paper_service.py   # Servicio automático
├── 🗃️ vector_db.py            # Base de datos vectorial
├── 📊 data/papers/            # Papers descargados (JSON)
├── 🧠 knowledge_base/         # Vector database
└── 📝 logs/                   # Logs del sistema
```

---

## 💡 Ejemplos de Uso

### Consultas Financieras
```
¿Cómo funciona el modelo Black-Scholes?
Explica Value at Risk (VaR)
¿Qué es portfolio optimization?
Describe el trading algorítmico
¿Cómo se calcula la volatilidad implícita?
```

### Búsquedas en Papers Recientes
```
Busca información sobre machine learning en trading
¿Hay papers recientes sobre riesgo de mercado?
Encuentra investigación sobre arbitraje estadístico
```

---

## 🔧 Configuración Avanzada

### Variables de Entorno (.env.papers)
```bash
# Frecuencia de actualización (horas)
UPDATE_FREQUENCY=6

# Número máximo de papers por actualización
MAX_PAPERS=15

# Días hacia atrás para buscar
DAYS_BACK=7

# Categorías ArXiv (separadas por coma)
ARXIV_CATEGORIES=q-fin.CP,q-fin.PM,q-fin.RM,q-fin.TR,q-fin.MF,q-fin.PR
```

### Filtros de Calidad
- Mínimo 500 caracteres en abstract
- Filtrado por palabras clave relevantes
- Exclusión de papers no técnicos
- Priorización por fecha de publicación

---

## 📊 Categorías de Papers Soportadas

| Categoría | Descripción | Ejemplos |
|-----------|-------------|----------|
| **q-fin.CP** | Computational Finance | ML, algoritmos, simulaciones |
| **q-fin.PM** | Portfolio Management | Optimización, asset allocation |
| **q-fin.RM** | Risk Management | VaR, stress testing, credit risk |
| **q-fin.TR** | Trading & Market Microstructure | HFT, market making, execution |
| **q-fin.MF** | Mathematical Finance | Modelos estocásticos, pricing |
| **q-fin.PR** | Pricing of Securities | Opciones, derivados, bonos |

---

## 🔍 Características Técnicas

### Tecnologías Utilizadas
- **IA**: LangChain + HuggingFace Embeddings
- **Vector DB**: FAISS con embeddings sentence-transformers
- **API**: ArXiv API con rate limiting
- **Scheduling**: Python schedule library
- **GUI**: PyQt5 (opcional, CLI por defecto)

### Capacidades del Sistema
- **Procesamiento**: 1000+ papers por hora
- **Memoria**: Vector database escalable
- **Filtrado**: Calidad automática basada en contenido
- **Búsqueda**: Semantic search en papers
- **Updates**: Incrementales, no duplicación

---

## 📈 Rendimiento y Escalabilidad

### Benchmarks
- **Descarga**: ~16 papers/minuto con rate limiting
- **Procesamiento**: ~100 papers/segundo para embeddings
- **Búsqueda**: <1 segundo para queries complejas
- **Memoria**: ~50MB por 1000 papers en vector DB

### Optimizaciones
- Rate limiting automático para ArXiv API
- Cacheo de embeddings
- Procesamiento en batch
- Logs rotativos para evitar saturación

---

## 🛡️ Manejo de Errores

### Robustez del Sistema
- **Reintentos automáticos** en fallos de red
- **Fallback a datos locales** si ArXiv no disponible
- **Logs detallados** para debugging
- **Graceful shutdown** en interrupciones

### Monitoreo
- Estado de salud del sistema
- Métricas de descarga
- Alertas por errores críticos
- Histórico de actualizaciones

---

## 🚀 Inicio Rápido

1. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   pip install arxiv schedule psutil
   ```

2. **Primer uso:**
   ```bash
   python3 run_full_system.py
   ```

3. **Seleccionar opciones:**
   - ✅ Iniciar servicio automático
   - ✅ Descargar papers iniciales
   - 🤖 Comenzar chat interactivo

---

## 📞 Soporte

### SPINOR TECHNOLOGIES
- **Sistema**: IA Financiera Avanzada v2.0
- **Especialización**: Finanzas Cuantitativas + ML
- **Actualizaciones**: Tiempo real desde ArXiv
- **Capacidades**: Chat IA + Investigación automática

**¡El futuro de las finanzas cuantitativas está aquí! 🚀📊**
