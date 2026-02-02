#!/bin/bash

# Script para verificar el estado completo de staging
# Autor: Sistema de Deploy
# Fecha: 2026-02-02

set -e

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "🔍 VERIFICACIÓN COMPLETA DE STAGING"
echo "===================================="
echo ""

# 1. Verificar conectividad
echo -e "${BLUE}1. Verificando conectividad...${NC}"
if curl -s -f https://staging.jemavi.co/health > /dev/null; then
    echo -e "${GREEN}   ✅ Staging está activo${NC}"
else
    echo -e "${RED}   ❌ Staging no responde${NC}"
    exit 1
fi
echo ""

# 2. Verificar servicios Docker
echo -e "${BLUE}2. Verificando servicios Docker...${NC}"
ssh ubuntu@staging "cd /home/ubuntu/paqueteria-staging && docker compose -f docker-compose.staging.yml ps" | grep -E "(NAME|app|redis)" || true
echo ""

# 3. Verificar commit actual
echo -e "${BLUE}3. Verificando commit desplegado...${NC}"
CURRENT_COMMIT=$(ssh ubuntu@staging "cd /home/ubuntu/paqueteria-staging && git log --oneline -1")
echo "   $CURRENT_COMMIT"
echo ""

# 4. Verificar configuración S3
echo -e "${BLUE}4. Verificando configuración S3...${NC}"
ssh ubuntu@staging "docker exec paqueteria_staging_app python -c \"
from src.app.services.s3_service import S3Service
import os

try:
    s3 = S3Service()
    print('   ✅ Bucket:', s3.bucket_name)
    print('   ✅ Región:', s3.region)
    print('   ✅ Prefix:', os.getenv('S3_PREFIX', 'N/A'))
except Exception as e:
    print('   ❌ Error:', str(e))
\"" 2>&1 | grep -E "(✅|❌|Bucket|Región|Prefix)" || true
echo ""

# 5. Verificar facturas en base de datos
echo -e "${BLUE}5. Verificando facturas en base de datos...${NC}"
ssh ubuntu@staging "docker exec paqueteria_staging_app python -c \"
from src.app.database import SessionLocal
from src.app.models.invoice_v2 import InvoiceV2

db = SessionLocal()
total = db.query(InvoiceV2).count()
con_s3 = db.query(InvoiceV2).filter(InvoiceV2.archivo_proveedor_s3_key.isnot(None)).count()

print(f'   📊 Total de facturas: {total}')
print(f'   📦 Con PDF en S3: {con_s3}')
print(f'   📄 Sin PDF en S3: {total - con_s3}')

if con_s3 > 0:
    print('')
    print('   ✅ Últimas facturas con PDF en S3:')
    facturas = db.query(InvoiceV2).filter(
        InvoiceV2.archivo_proveedor_s3_key.isnot(None)
    ).order_by(InvoiceV2.created_at.desc()).limit(3).all()
    
    for f in facturas:
        proveedor = f.proveedor_nombre if f.proveedor_nombre else 'Sin nombre'
        print(f'      - {proveedor} | {f.cufe[:20]}...')

db.close()
\"" 2>&1 | grep -v "INFO sqlalchemy" | grep -v "Configuración" | grep -v "Ambiente" | grep -v "Base de datos" | grep -v "JWT Secret" || true
echo ""

# 6. Verificar logs recientes
echo -e "${BLUE}6. Últimos logs (últimas 5 líneas)...${NC}"
ssh ubuntu@staging "docker logs --tail 5 paqueteria_staging_app 2>&1" | grep -v "INFO sqlalchemy" | tail -5 || true
echo ""

# 7. Resumen
echo "===================================="
echo -e "${GREEN}✅ Verificación completada${NC}"
echo ""
echo "📝 Próximos pasos:"
echo "   1. Accede a: https://staging.jemavi.co/invoices"
echo "   2. Sube una factura nueva"
echo "   3. Verifica el botón de descarga en verde"
echo ""
echo "📚 Documentación completa:"
echo "   - RESUMEN_DEPLOY_S3_COMPLETADO.md"
echo "   - DEPLOY_EN_PROGRESO.md"
echo ""
