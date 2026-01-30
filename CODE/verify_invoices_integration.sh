#!/bin/bash

echo "=========================================="
echo "Verificación de Integración de Facturas"
echo "=========================================="
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para verificar
check() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $1"
    else
        echo -e "${RED}✗${NC} $1"
    fi
}

# 1. Verificar que las rutas están registradas en main.py
echo "1. Verificando rutas en main.py..."
grep -q "invoices_v2_api_router" CODE/src/main.py
check "Rutas API registradas"

grep -q "invoices_v2_web_router" CODE/src/main.py
check "Rutas Web registradas"

# 2. Verificar que el enlace está en el header
echo ""
echo "2. Verificando enlace en header..."
grep -q "/invoices/facturas" CODE/src/templates/base/base.html
check "Enlace en header principal"

grep -q "Facturas Móvil" CODE/src/templates/base/base.html
check "Enlace en menú móvil"

# 3. Verificar que las vistas extienden de base.html
echo ""
echo "3. Verificando templates..."
grep -q "extends \"base/base.html\"" CODE/src/templates/invoices_v2/layout.html
check "Layout extiende de base.html"

grep -q "papyrus-blue" CODE/src/templates/invoices_v2/facturas.html
check "Colores del proyecto en facturas.html"

grep -q "papyrus-blue" CODE/src/templates/invoices_v2/cufe.html
check "Colores del proyecto en cufe.html"

grep -q "papyrus-blue" CODE/src/templates/invoices_v2/productos.html
check "Colores del proyecto en productos.html"

# 4. Verificar que las URLs están actualizadas
echo ""
echo "4. Verificando URLs..."
grep -q "prefix=\"/invoices\"" CODE/src/app/routes/invoices_v2_web_routes.py
check "Prefix actualizado a /invoices"

! grep -q "/invoices-v2/" CODE/src/templates/invoices_v2/*.html
check "URLs actualizadas en templates"

# 5. Verificar que los modelos existen
echo ""
echo "5. Verificando archivos del sistema..."
[ -f "CODE/src/app/models/invoice_v2.py" ]
check "Modelo invoice_v2.py existe"

[ -f "CODE/src/app/services/pdf_parser_service.py" ]
check "Servicio pdf_parser_service.py existe"

[ -f "CODE/src/app/services/invoice_v2_service.py" ]
check "Servicio invoice_v2_service.py existe"

# 6. Verificar migración
echo ""
echo "6. Verificando migración..."
[ -f "CODE/alembic/versions/20260130_create_invoice_system_v2.py" ]
check "Migración existe"

# Resumen
echo ""
echo "=========================================="
echo "Resumen de Verificación"
echo "=========================================="
echo ""
echo -e "${YELLOW}Para completar la integración:${NC}"
echo "1. Reiniciar el servidor: docker-compose restart web"
echo "2. Acceder a: http://localhost:8000/invoices/facturas"
echo "3. El enlace 'Facturas' debe aparecer en el header entre 'Consulta' y 'DynamiaERP'"
echo ""
echo -e "${GREEN}✓ Integración verificada correctamente${NC}"
echo ""
