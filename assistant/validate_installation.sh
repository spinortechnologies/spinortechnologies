#!/bin/bash
# Validate Docker installation
docker run --rm -v $(pwd)/knowledge_base:/app/knowledge_base quant-ai \
    python -c "from vector_db import load_vector_store; print('Vector store loaded successfully!')"

# Test GUI launch
docker run --rm -v $(pwd)/knowledge_base:/app/knowledge_base \
    -e DISPLAY=host.docker.internal:0 quant-ai \
    python -c "from PyQt5 import QtWidgets; app = QtWidgets.QApplication([]); print('GUI dependencies verified')"