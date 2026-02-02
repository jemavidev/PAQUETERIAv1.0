#!/bin/bash

# Script para probar la subida de facturas a S3 en staging
# Autor: Sistema de Deploy
# Fecha: 2026-02-02

set -e

echo "🧪 PRUEBA DE SUBIDA DE FACTURAS A S3 EN STAGING"
echo "================================================"
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Variables
STAGING_URL="https://staging.jemavi.co"
PDF_FILE="CUFE/FACTURAS/21bb002f269805b73ac22c5966cd9c91c3f13eacb76844986fd9b88c86f0305da41f432151997d3db36d96dfb0b10c13_20250719085817.pdf"

echo "📋 Configuración:"
echo "   URL: $STAGING_URL"
echo "   PDF: $PDF_FILE"
echo ""

# Verificar que el archivo existe
if [ ! -f "$PDF_FILE" ]; then
    echo -e "${RED}❌ Error: El archivo PDF no existe${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Archivo PDF encontrado${NC}"
echo ""

# Paso 1: Verificar que staging está activo
echo "🔍 Paso 1: Verificando que staging está activo..."
if curl -s -f "$STAGING_URL/health" > /dev/null; then
    echo -e "${GREEN}✅ Staging está activo${NC}"
else
    echo -e "${RED}❌ Staging no responde${NC}"
    exit 1
fi
echo ""

# Paso 2: Verificar estado de S3
echo "🔍 Paso 2: Verificando configuración de S3..."
ssh ubuntu@staging "docker exec paqueteria_staging_app python -c \"
from src.app.services.s3_service import S3Service
s3 = S3Service()
print('✅ S3 configurado:', s3.bucket_name)
\"" 2>&1 | grep -E "(✅|❌|Error)" || true
echo ""

# Paso 3: Contar facturas antes de subir
echo "🔍 Paso 3: Contando facturas antes de subir..."
BEFORE_COUNT=$(ssh ubuntu@staging "docker exec paqueteria_staging_app python -c \"
from src.app.database import SessionLocal
from src.app.models.invoice_v2 import InvoiceV2
db = SessionLocal()
count = db.query(InvoiceV2).count()
print(count)
db.close()
\"" 2>&1 | tail -1)

echo "   Facturas actuales: $BEFORE_COUNT"
echo ""

# Paso 4: Instrucciones para subir manualmente
echo "📝 Paso 4: Instrucciones para probar manualmente"
echo ""
echo -e "${YELLOW}Para probar la funcionalidad:${NC}"
echo ""
echo "1. Abre tu navegador en:"
echo "   $STAGING_URL/invoices"
echo ""
echo "2. Inicia sesión con tus credenciales"
echo ""
echo "3. Ve al tab 'Facturas'"
echo ""
echo "4. Click en 'Cargar Factura de Proveedor'"
echo ""
echo "5. Selecciona el archivo:"
echo "   $PDF_FILE"
echo ""
echo "6. Click en 'Subir'"
echo ""
echo "7. Verifica que:"
echo "   - La factura aparece en la lista"
echo "   - El botón de descarga está en VERDE"
echo "   - Al hacer click, descarga el PDF correctamente"
echo ""

# Paso 5: Comando para verificar después
echo "📊 Paso 5: Después de subir, ejecuta este comando para verificar:"
echo ""
echo -e "${YELLOW}./verify_s3_upload.sh${NC}"
echo ""

# Crear script de verificación
cat > verify_s3_upload.sh << 'EOF'
#!/bin/bash

echo "🔍 Verificando facturas con PDF en S3..."
echo ""

ssh ubuntu@staging "docker exec paqueteria_staging_app python -c \"
from src.app.database import SessionLocal
from src.app.models.invoice_v2 import InvoiceV2

db = SessionLocal()
total = db.query(InvoiceV2).count()
con_s3 = db.query(InvoiceV2).filter(InvoiceV2.archivo_proveedor_s3_key.isnot(None)).count()

print(f'📊 Estadísticas:')
print(f'   Total de facturas: {total}')
print(f'   Con PDF en S3: {con_s3}')
print(f'   Sin PDF en S3: {total - con_s3}')
print('')

if con_s3 > 0:
    print('✅ Últimas facturas con PDF en S3:')
    facturas = db.query(InvoiceV2).filter(
        InvoiceV2.archivo_proveedor_s3_key.isnot(None)
    ).order_by(InvoiceV2.created_at.desc()).limit(3).all()
    
    for f in facturas:
        print(f'   - CUFE: {f.cufe[:20]}...')
        print(f'     S3 Key: {f.archivo_proveedor_s3_key}')
        print(f'     Proveedor: {f.proveedor_nombre}')
        print(f'     Fecha: {f.created_at}')
        print('')

db.close()
\"" 2>&1 | grep -v "INFO sqlalchemy"
EOF

chmod +x verify_s3_upload.sh

echo -e "${GREEN}✅ Script de verificación creado: verify_s3_upload.sh${NC}"
echo ""

# Paso 6: Ver logs en tiempo real
echo "📋 Paso 6: Para ver los logs en tiempo real mientras subes:"
echo ""
echo -e "${YELLOW}ssh ubuntu@staging 'docker logs -f paqueteria_staging_app | grep -E \"(S3|invoice|upload|PDF)\"'${NC}"
echo ""

echo "================================================"
echo "✅ Preparación completada"
echo ""
echo "Ahora puedes:"
echo "1. Subir una factura manualmente desde el navegador"
echo "2. Ejecutar ./verify_s3_upload.sh para verificar"
echo ""
