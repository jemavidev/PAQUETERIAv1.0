#!/bin/bash
# Diagnóstico completo del sistema de carga de facturas

echo "╔════════════════════════════════════════════════════════╗"
echo "║     DIAGNÓSTICO COMPLETO - STAGING                     ║"
echo "╚════════════════════════════════════════════════════════╝"

echo -e "\n1️⃣ Estado del servidor..."
ssh -o ConnectTimeout=10 staging 'docker ps --format "table {{.Names}}\t{{.Status}}" 2>&1' | head -10

echo -e "\n2️⃣ Verificando archivos actualizados..."
echo "   base.html (window.alert comentado):"
ssh -o ConnectTimeout=10 staging 'grep -c "window.alert = function" /home/ubuntu/paqueteria-staging/CODE/src/templates/base/base.html 2>&1'
echo "   Debería ser 0 (comentado)"

echo -e "\n   _tab_facturas.html (URL correcta):"
ssh -o ConnectTimeout=10 staging 'grep -c "/invoices/api/supplier-invoices/upload" /home/ubuntu/paqueteria-staging/CODE/src/templates/invoices/_tab_facturas.html 2>&1'
echo "   Debería ser 1 o más"

echo -e "\n3️⃣ Últimos uploads exitosos..."
ssh -o ConnectTimeout=10 staging 'docker logs --tail 100 paqueteria_staging_app 2>&1 | grep "supplier-invoices/upload" | tail -5'

echo -e "\n4️⃣ Archivos en S3..."
ssh -o ConnectTimeout=10 staging 'docker logs --tail 100 paqueteria_staging_app 2>&1 | grep "PDF de proveedor guardado" | tail -5'

echo -e "\n5️⃣ Errores recientes..."
ssh -o ConnectTimeout=10 staging 'docker logs --tail 50 paqueteria_staging_app 2>&1 | grep -i "error\|exception\|failed" | tail -10'

echo -e "\n6️⃣ Health check..."
HEALTH=$(ssh -o ConnectTimeout=10 staging 'curl -s https://staging.jemavi.co/health 2>&1')
if echo "$HEALTH" | grep -q "healthy"; then
    echo "   ✅ Servidor funcionando"
else
    echo "   ❌ Problema con el servidor"
fi

echo -e "\n╔════════════════════════════════════════════════════════╗"
echo "║     DIAGNÓSTICO COMPLETADO                             ║"
echo "╚════════════════════════════════════════════════════════╝"

echo -e "\n📝 INSTRUCCIONES PARA PROBAR:"
echo "   1. Abre modo incógnito"
echo "   2. Ve a: https://staging.jemavi.co/invoices"
echo "   3. Inicia sesión"
echo "   4. Tab 'Facturas' > 'Subir Facturas'"
echo "   5. Selecciona un PDF"
echo "   6. Deberías ver un alert NATIVO del navegador"
echo "   7. Sin errores de Alpine.js"
echo ""
