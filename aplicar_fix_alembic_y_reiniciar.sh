#!/bin/bash
# Script para aplicar fix de Alembic y reiniciar servidor staging

set -e

echo "=================================================="
echo "FIX ALEMBIC MULTIPLE HEADS + REINICIO SERVIDOR"
echo "=================================================="
echo ""

# 1. Verificar que solo existe 1 head
echo "[1/4] Verificando heads de Alembic..."
python3 verificar_alembic_heads.py
if [ $? -ne 0 ]; then
    echo "❌ ERROR: Todavía existen múltiples heads"
    exit 1
fi
echo "✅ Verificación exitosa"
echo ""

# 2. Hacer commit de los cambios
echo "[2/4] Haciendo commit de los cambios..."
git add CODE/alembic/versions/20260211_092552_add_tipo_factura.py
git add verificar_alembic_heads.py
git add FIX_ALEMBIC_MULTIPLE_HEADS.md
git add aplicar_fix_alembic_y_reiniciar.sh

if git diff --cached --quiet; then
    echo "ℹ️  No hay cambios para commitear"
else
    git commit -m "fix: resolver múltiples heads en Alembic

- Eliminada migración de merge incorrecta (20260211_093000)
- Actualizada migración 20260211_092552 como único head
- Unifica todas las ramas: tipo_factura, supplier_invoices, customer_prefs, cufe_records, incremental_sync, products
- Agregado script de verificación de heads

Fixes: Multiple head revisions error en alembic upgrade head"
    echo "✅ Commit realizado"
fi
echo ""

# 3. Push a staging
echo "[3/4] Haciendo push a staging..."
git push origin staging
echo "✅ Push exitoso"
echo ""

# 4. Instrucciones para reiniciar servidor
echo "[4/4] Reinicio del servidor"
echo ""
echo "⚠️  IMPORTANTE: El servidor debe reiniciarse manualmente con permisos root"
echo ""
echo "Ejecuta en el servidor staging:"
echo "  sudo ./reiniciar_servidor_completo.sh"
echo ""
echo "O usa el script de deploy:"
echo "  ./deploy.sh staging"
echo ""
echo "=================================================="
echo "✅ FIX APLICADO - Listo para reiniciar servidor"
echo "=================================================="
