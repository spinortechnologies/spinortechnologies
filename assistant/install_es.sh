# Script de Instalación Automática para Linux/Mac
# Automatic Installation Script for Linux/Mac

#!/bin/bash

echo "🚀 Iniciando instalación del Asistente de Finanzas Cuantitativas..."
echo "🚀 Starting Quantitative Finance Assistant installation..."

# Verificar Python
echo "📋 Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no está instalado. Por favor instálalo primero."
    echo "❌ Python3 is not installed. Please install it first."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python $PYTHON_VERSION detectado"

# Crear entorno virtual
echo "🔧 Creando entorno virtual..."
python3 -m venv quant_assistant_env
source quant_assistant_env/bin/activate

echo "✅ Entorno virtual creado y activado"

# Actualizar pip
echo "⬆️ Actualizando pip..."
pip install --upgrade pip

# Instalar dependencias base
echo "📦 Instalando dependencias principales..."
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements_es.txt

# Descargar modelos de spaCy para español
echo "🌐 Descargando modelos de lenguaje..."
python -m spacy download es_core_news_sm
python -m spacy download en_core_web_sm

# Crear directorios necesarios
echo "📁 Creando estructura de directorios..."
mkdir -p knowledge_base
mkdir -p data
mkdir -p models
mkdir -p logs
mkdir -p config

# Configurar NLTK
echo "📚 Configurando NLTK..."
python -c "
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
"

# Verificar instalación
echo "🧪 Verificando instalación..."
python validate_installation.sh

# Configurar variables de entorno
echo "⚙️ Configurando variables de entorno..."
cat > .env << EOL
# Configuración del Asistente de Finanzas Cuantitativas
# Quantitative Finance Assistant Configuration

# Modelos de IA / AI Models
DEFAULT_MODEL=microsoft/DialoGPT-medium
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
SPANISH_MODEL=PlanTL-GOB-ES/roberta-base-bne

# Base de datos vectorial / Vector database
VECTOR_DB_PATH=./knowledge_base/vector_db
MAX_CHUNKS=1000
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# API Keys (opcional / optional)
HUGGINGFACE_API_KEY=your_huggingface_key_here
ALPHA_VANTAGE_KEY=your_alpha_vantage_key_here

# Configuración de actualización automática / Auto-update configuration
AUTO_UPDATE_ENABLED=true
UPDATE_FREQUENCY=daily
MAX_PAPERS_PER_UPDATE=50

# Configuración de idioma / Language configuration
DEFAULT_LANGUAGE=es
SUPPORT_MULTILINGUAL=true

# Configuración de rendimiento / Performance configuration
PERFORMANCE_MODE=balanced
MAX_MEMORY_GB=4
ENABLE_GPU=false
EOL

echo "✅ Archivo de configuración .env creado"

# Crear script de inicio
echo "🚀 Creando script de inicio..."
cat > start_assistant.sh << 'EOL'
#!/bin/bash
cd "$(dirname "$0")"
source quant_assistant_env/bin/activate
echo "🚀 Iniciando Asistente de Finanzas Cuantitativas..."
python gui.py
EOL

chmod +x start_assistant.sh

# Crear script de actualización
echo "🔄 Creando script de actualización..."
cat > update_knowledge.sh << 'EOL'
#!/bin/bash
cd "$(dirname "$0")"
source quant_assistant_env/bin/activate
echo "📚 Actualizando base de conocimientos..."
python auto_updater.py
EOL

chmod +x update_knowledge.sh

echo ""
echo "🎉 ¡Instalación completada exitosamente!"
echo "🎉 Installation completed successfully!"
echo ""
echo "📋 Próximos pasos / Next steps:"
echo "   1. Activar entorno: source quant_assistant_env/bin/activate"
echo "   1. Activate environment: source quant_assistant_env/bin/activate"
echo ""
echo "   2. Iniciar aplicación: ./start_assistant.sh"
echo "   2. Start application: ./start_assistant.sh"
echo ""
echo "   3. Actualizar conocimientos: ./update_knowledge.sh"
echo "   3. Update knowledge: ./update_knowledge.sh"
echo ""
echo "📖 Ver INSTALACION_ES.md para más detalles"
echo "📖 See INSTALACION_ES.md for more details"
