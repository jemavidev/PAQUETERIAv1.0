#!/bin/bash

echo "=========================================="
echo "Verificación de Sintaxis - Sistema de Facturas V2"
echo "=========================================="
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

errors=0

# Función para verificar sintaxis
check_syntax() {
    file=$1
    if python3 -m py_compile "$file" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} $file"
    else
        echo -e "${RED}✗${NC} $file"
        python3 -m py_compile "$file" 2>&1 | head -5
        ((errors++))
    fi
}

echo "Verificando archivos Python..."
echo ""

# Verificar modelos
check_syntax "CODE/src/app/models/invoice_v2.py"

# Verificar servicios
check_syntax "CODE/src/app/services/pdf_parser_service.py"
check_syntax "CODE/src/app/services/invoice_v2_service.py"

# Verificar rutas
check_syntax "CODE/src/app/routes/invoices_v2_routes.py"
check_syntax "CODE/src/app/routes/invoices_v2_web_routes.py"

# Verificar main.py
check_syntax "CODE/src/main.py"

echo ""
echo "=========================================="
if [ $errors -eq 0 ]; then
    echo -e "${GREEN}✓ Todos los archivos tienen sintaxis correcta${NC}"
    echo ""
    echo "El problema del health check puede ser:"
    echo "1. La migración de base de datos no se aplicó"
    echo "2. Hay un error en tiempo de ejecución (no de sintaxis)"
    echo "3. El servidor tarda más de lo esperado en iniciar"
    echo ""
    echo "Soluciones:"
    echo "1. Aplicar migración: docker-compose exec app alembic upgrade head"
    echo "2. Ver logs: docker-compose logs app"
    echo "3. Aumentar timeout del health check en docker-compose"
else
    echo -e "${RED}✗ Se encontraron $errors errores de sintaxis${NC}"
fi
echo "=========================================="
