#!/bin/bash

# =====================================================
# SCRIPT RÁPIDO PARA APLICAR MEJORAS DE PAGINACIÓN
# =====================================================

echo "🚀 APLICANDO MEJORAS DE PAGINACIÓN"
echo "===================================="
echo ""

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. Aplicar índices de base de datos
echo -e "${BLUE}📊 Paso 1: Aplicando índices de base de datos...${NC}"
python apply_pagination_indexes.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Índices aplicados correctamente${NC}"
else
    echo -e "${RED}❌ Error aplicando índices${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}📈 Paso 2: Verificando índices...${NC}"

# Verificar que los índices existen
python -c "
from app.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text('''
        SELECT COUNT(*) as count
        FROM pg_indexes
        WHERE tablename = 'invoices_v2'
        AND indexname LIKE 'idx_%'
    '''))
    count = result.fetchone()[0]
    print(f'   Índices encontrados: {count}')
    
    if count >= 8:
        print('   ✅ Todos los índices principales están creados')
    else:
        print('   ⚠️  Faltan algunos índices')
"

echo ""
echo -e "${BLUE}🔄 Paso 3: Reiniciando servidor...${NC}"
echo -e "${YELLOW}   Nota: Debes reiniciar manualmente el servidor para que los cambios tengan efecto completo${NC}"
echo ""
echo -e "${GREEN}Comandos para reiniciar:${NC}"
echo "   Docker: docker-compose restart"
echo "   Uvicorn: Ctrl+C y luego: uvicorn src.main:app --reload"

echo ""
echo "===================================="
echo -e "${GREEN}✅ MEJORAS APLICADAS EXITOSAMENTE${NC}"
echo "===================================="
echo ""
echo "📋 Próximos pasos:"
echo "   1. Reinicia el servidor"
echo "   2. Abre /invoices/facturas en el navegador"
echo "   3. Prueba la paginación (debería ser mucho más rápida)"
echo "   4. Prueba el salto directo a página"
echo "   5. Recarga la página (debería mantener el estado)"
echo ""
echo "📚 Documentación completa en: MEJORAS_PAGINACION_IMPLEMENTADAS.md"
echo ""
