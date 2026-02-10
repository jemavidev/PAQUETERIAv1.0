#!/bin/bash
# Script simple para cargar PDFs usando curl
# Requiere tener una sesión activa en el navegador

PDF_DIR="/home/stk/Documents/GIT/PAQUETEX v1.0/CUFE/CUFE-XML"
API_URL="http://localhost:8000/api/v2/invoices/facturas/upload"

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "============================================================"
echo "CARGA MASIVA DE PDFs - TAB FACTURAS (CURL)"
echo "============================================================"

# Verificar directorio
if [ ! -d "$PDF_DIR" ]; then
    echo -e "${RED}❌ Error: Directorio no existe: $PDF_DIR${NC}"
    exit 1
fi

# Contar PDFs
PDF_COUNT=$(ls "$PDF_DIR"/*.pdf 2>/dev/null | wc -l)
echo -e "📄 Encontrados ${GREEN}$PDF_COUNT${NC} archivos PDF"

if [ $PDF_COUNT -eq 0 ]; then
    echo -e "${RED}❌ No se encontraron archivos PDF${NC}"
    exit 1
fi

# Confirmar
echo ""
echo -e "${YELLOW}⚠️  Se cargarán $PDF_COUNT archivos PDF${NC}"
read -p "¿Deseas continuar? (s/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo -e "${RED}❌ Operación cancelada${NC}"
    exit 0
fi

echo ""
echo "============================================================"

# Contadores
EXITOSOS=0
FALLIDOS=0
TOTAL=0

# Procesar cada PDF
for pdf_file in "$PDF_DIR"/*.pdf; do
    TOTAL=$((TOTAL + 1))
    filename=$(basename "$pdf_file")
    
    echo ""
    echo "[$TOTAL/$PDF_COUNT] Procesando: $filename"
    
    # Hacer upload con curl
    response=$(curl -s -w "\n%{http_code}" -X POST "$API_URL" \
        -F "file=@$pdf_file" \
        --max-time 30 \
        2>&1)
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" = "200" ]; then
        # Extraer CUFE y proveedor del JSON
        cufe=$(echo "$body" | grep -o '"cufe":"[^"]*"' | cut -d'"' -f4 | cut -c1-20)
        proveedor=$(echo "$body" | grep -o '"proveedor_nombre":"[^"]*"' | cut -d'"' -f4)
        
        echo -e "   ${GREEN}✅ Cargado exitosamente${NC}"
        [ ! -z "$cufe" ] && echo "   📋 CUFE: ${cufe}..."
        [ ! -z "$proveedor" ] && echo "   🏢 Proveedor: $proveedor"
        EXITOSOS=$((EXITOSOS + 1))
    else
        error=$(echo "$body" | grep -o '"detail":"[^"]*"' | cut -d'"' -f4)
        echo -e "   ${RED}❌ Error (HTTP $http_code)${NC}"
        [ ! -z "$error" ] && echo "   💬 $error"
        FALLIDOS=$((FALLIDOS + 1))
    fi
    
    # Pausa pequeña
    sleep 0.5
done

# Resumen
echo ""
echo "============================================================"
echo ""
echo "📊 RESUMEN DE CARGA"
echo "   Total archivos: $TOTAL"
echo -e "   ${GREEN}✅ Exitosos: $EXITOSOS${NC}"
echo -e "   ${RED}❌ Fallidos: $FALLIDOS${NC}"

if [ $TOTAL -gt 0 ]; then
    TASA=$((EXITOSOS * 100 / TOTAL))
    echo "   📈 Tasa de éxito: ${TASA}%"
fi

echo ""
echo "✅ Proceso completado"
