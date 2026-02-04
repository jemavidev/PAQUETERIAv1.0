#!/bin/bash
# Script de prueba rápida para el botón de descarga

echo "=========================================="
echo "🧪 TEST: Botón de Descarga de Facturas"
echo "=========================================="
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Verificar que el servidor esté corriendo
echo "1️⃣ Verificando servidor..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Servidor corriendo${NC}"
else
    echo -e "${RED}❌ Servidor no está corriendo${NC}"
    echo "💡 Inicia el servidor con: docker-compose up -d"
    exit 1
fi

# 2. Verificar endpoint de facturas
echo ""
echo "2️⃣ Verificando endpoint de facturas..."
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v2/invoices/facturas?limit=1)
if [ "$RESPONSE" = "200" ]; then
    echo -e "${GREEN}✅ Endpoint de facturas funciona${NC}"
else
    echo -e "${RED}❌ Endpoint de facturas no responde (HTTP $RESPONSE)${NC}"
    exit 1
fi

# 3. Obtener una factura con archivo
echo ""
echo "3️⃣ Buscando factura con archivo PDF..."
FACTURAS=$(curl -s http://localhost:8000/api/v2/invoices/facturas?limit=10)

# Extraer CUFE de una factura que tenga archivo_proveedor_s3_key
CUFE=$(echo "$FACTURAS" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    items = data.get('items', [])
    for item in items:
        if item.get('archivo_proveedor_s3_key'):
            print(item['cufe'])
            break
except:
    pass
")

if [ -z "$CUFE" ]; then
    echo -e "${YELLOW}⚠️ No se encontraron facturas con archivo PDF${NC}"
    echo "💡 Carga una factura con PDF para probar la descarga"
    exit 0
fi

echo -e "${GREEN}✅ Factura encontrada: ${CUFE:0:20}...${NC}"

# 4. Probar endpoint de descarga
echo ""
echo "4️⃣ Probando endpoint de descarga..."
DOWNLOAD_RESPONSE=$(curl -s http://localhost:8000/api/v2/invoices/facturas/$CUFE/download-url)

# Verificar que la respuesta contenga una URL
if echo "$DOWNLOAD_RESPONSE" | grep -q "https://"; then
    echo -e "${GREEN}✅ Endpoint de descarga funciona${NC}"
    
    # Extraer y mostrar la URL
    URL=$(echo "$DOWNLOAD_RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('url', '')[:100] + '...')
except:
    pass
")
    echo "   URL generada: $URL"
    
    FILENAME=$(echo "$DOWNLOAD_RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('filename', ''))
except:
    pass
")
    echo "   Nombre archivo: $FILENAME"
else
    echo -e "${RED}❌ Error en endpoint de descarga${NC}"
    echo "   Respuesta: $DOWNLOAD_RESPONSE"
    exit 1
fi

# 5. Resumen
echo ""
echo "=========================================="
echo -e "${GREEN}✅ TODOS LOS TESTS PASARON${NC}"
echo "=========================================="
echo ""
echo "🎯 El botón de descarga está funcionando correctamente"
echo ""
echo "📝 Para probar en el navegador:"
echo "   1. Abre: http://localhost:8000/invoices/facturas"
echo "   2. Busca el botón verde de descarga (icono ⬇️)"
echo "   3. Haz clic para descargar el PDF"
echo ""
echo "🔍 Para ver logs en tiempo real:"
echo "   docker-compose logs -f app | grep -E '(download|URL)'"
echo ""
