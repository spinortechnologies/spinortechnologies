# Script de Instalación para Windows
# Windows Installation Script

@echo off
chcp 65001 >nul

echo 🚀 Iniciando instalación del Asistente de Finanzas Cuantitativas...
echo 🚀 Starting Quantitative Finance Assistant installation...

REM Verificar Python
echo 📋 Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no está instalado. Por favor instálalo desde python.org
    echo ❌ Python is not installed. Please install it from python.org
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% detectado

REM Crear entorno virtual
echo 🔧 Creando entorno virtual...
python -m venv quant_assistant_env
call quant_assistant_env\Scripts\activate.bat

echo ✅ Entorno virtual creado y activado

REM Actualizar pip
echo ⬆️ Actualizando pip...
python -m pip install --upgrade pip

REM Instalar dependencias base
echo 📦 Instalando dependencias principales...
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements_es.txt

REM Descargar modelos de spaCy
echo 🌐 Descargando modelos de lenguaje...
python -m spacy download es_core_news_sm
python -m spacy download en_core_web_sm

REM Crear directorios necesarios
echo 📁 Creando estructura de directorios...
if not exist knowledge_base mkdir knowledge_base
if not exist data mkdir data
if not exist models mkdir models
if not exist logs mkdir logs
if not exist config mkdir config

REM Configurar NLTK
echo 📚 Configurando NLTK...
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"

REM Verificar instalación
echo 🧪 Verificando instalación...
python validate_installation.sh

REM Configurar variables de entorno
echo ⚙️ Configurando variables de entorno...
(
echo # Configuración del Asistente de Finanzas Cuantitativas
echo # Quantitative Finance Assistant Configuration
echo.
echo # Modelos de IA / AI Models
echo DEFAULT_MODEL=microsoft/DialoGPT-medium
echo EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
echo SPANISH_MODEL=PlanTL-GOB-ES/roberta-base-bne
echo.
echo # Base de datos vectorial / Vector database
echo VECTOR_DB_PATH=./knowledge_base/vector_db
echo MAX_CHUNKS=1000
echo CHUNK_SIZE=1000
echo CHUNK_OVERLAP=200
echo.
echo # API Keys ^(opcional / optional^)
echo HUGGINGFACE_API_KEY=your_huggingface_key_here
echo ALPHA_VANTAGE_KEY=your_alpha_vantage_key_here
echo.
echo # Configuración de actualización automática / Auto-update configuration
echo AUTO_UPDATE_ENABLED=true
echo UPDATE_FREQUENCY=daily
echo MAX_PAPERS_PER_UPDATE=50
echo.
echo # Configuración de idioma / Language configuration
echo DEFAULT_LANGUAGE=es
echo SUPPORT_MULTILINGUAL=true
echo.
echo # Configuración de rendimiento / Performance configuration
echo PERFORMANCE_MODE=balanced
echo MAX_MEMORY_GB=4
echo ENABLE_GPU=false
) > .env

echo ✅ Archivo de configuración .env creado

REM Crear script de inicio
echo 🚀 Creando script de inicio...
(
echo @echo off
echo cd /d "%%~dp0"
echo call quant_assistant_env\Scripts\activate.bat
echo echo 🚀 Iniciando Asistente de Finanzas Cuantitativas...
echo python gui.py
echo pause
) > start_assistant.bat

REM Crear script de actualización
echo 🔄 Creando script de actualización...
(
echo @echo off
echo cd /d "%%~dp0"
echo call quant_assistant_env\Scripts\activate.bat
echo echo 📚 Actualizando base de conocimientos...
echo python auto_updater.py
echo pause
) > update_knowledge.bat

echo.
echo 🎉 ¡Instalación completada exitosamente!
echo 🎉 Installation completed successfully!
echo.
echo 📋 Próximos pasos / Next steps:
echo    1. Ejecutar: start_assistant.bat
echo    1. Run: start_assistant.bat
echo.
echo    2. Para actualizar conocimientos: update_knowledge.bat
echo    2. To update knowledge: update_knowledge.bat
echo.
echo 📖 Ver INSTALACION_ES.md para más detalles
echo 📖 See INSTALACION_ES.md for more details
echo.
pause
