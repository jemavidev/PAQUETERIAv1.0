#!/bin/bash
# Script para iniciar el servidor en desarrollo local

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                    INICIANDO SERVIDOR DE DESARROLLO                          ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Obtener directorio actual
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Configurar PYTHONPATH
export PYTHONPATH="$SCRIPT_DIR:$SCRIPT_DIR/src"

echo -e "${BLUE}📁 Directorio:${NC} $SCRIPT_DIR"
echo -e "${BLUE}🐍 PYTHONPATH:${NC} $PYTHONPATH"
echo ""

# Crear directorio uploads si no existe
mkdir -p "$SCRIPT_DIR/uploads"
mkdir -p "$SCRIPT_DIR/logs"

echo -e "${GREEN}✅ Directorios creados${NC}"
echo ""

# Activar entorno virtual si existe
if [ -d "$SCRIPT_DIR/.venv" ]; then
    source "$SCRIPT_DIR/.venv/bin/activate"
    echo -e "${GREEN}✅ Entorno virtual activado${NC}"
else
    echo -e "${BLUE}ℹ️  No se encontró entorno virtual (.venv)${NC}"
fi

echo ""
echo -e "${BLUE}🚀 Iniciando servidor en http://localhost:8000${NC}"
echo ""

# Iniciar servidor
cd "$SCRIPT_DIR"
python3 -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
