#!/bin/bash
# Script para reiniciar el servidor completamente

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                    REINICIANDO SERVIDOR COMPLETO                             ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""

# 1. Detener procesos existentes
echo -e "${YELLOW}🛑 Deteniendo procesos existentes...${NC}"
sudo pkill -f "uvicorn" 2>/dev/null
sudo pkill -f "python.*main" 2>/dev/null
sleep 2

# Verificar que se detuvieron
RUNNING=$(ps aux | grep -E "uvicorn|python.*main" | grep -v grep | wc -l)
if [ $RUNNING -eq 0 ]; then
    echo -e "${GREEN}✅ Procesos detenidos correctamente${NC}"
else
    echo -e "${RED}⚠️  Algunos procesos aún están corriendo${NC}"
    ps aux | grep -E "uvicorn|python.*main" | grep -v grep
fi

echo ""

# 2. Limpiar archivos temporales
echo -e "${YELLOW}🧹 Limpiando archivos temporales...${NC}"
find CODE -name "*.pyc" -delete 2>/dev/null
find CODE -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
echo -e "${GREEN}✅ Archivos temporales eliminados${NC}"

echo ""

# 3. Iniciar servidor
echo -e "${BLUE}🚀 Iniciando servidor...${NC}"
echo ""

cd CODE
./start_server.sh
