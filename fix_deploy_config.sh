#!/bin/bash
# ════════════════════════════════════════════════════════════════════════════
# Script para corregir configuración de deploy antes de ejecutar deploy.sh
# ════════════════════════════════════════════════════════════════════════════

set -e

echo "════════════════════════════════════════════════════════════════════════════"
echo "  Corrección de Configuración de Deploy para Facturas V2"
echo "════════════════════════════════════════════════════════════════════════════"
echo ""

CONFIG_FILE=".deploy/config/staging.conf"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Error: Archivo $CONFIG_FILE no encontrado"
    exit 1
fi

echo "📝 Creando backup de configuración actual..."
cp "$CONFIG_FILE" "${CONFIG_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
echo "✅ Backup creado"
echo ""

echo "🔧 Aplicando correcciones..."
echo ""

# 1. Habilitar migraciones
echo "  [1/3] Habilitando migraciones..."
sed -i 's/^MIGRATIONS_ENABLED=false/MIGRATIONS_ENABLED=true/' "$CONFIG_FILE"
sed -i 's/^MIGRATIONS_AUTO=false/MIGRATIONS_AUTO=true/' "$CONFIG_FILE"
echo "  ✅ Migraciones habilitadas"

# 2. Corregir comando de migraciones (heads → head)
echo "  [2/3] Corrigiendo comando de migraciones..."
sed -i 's/upgrade heads/upgrade head/g' "$CONFIG_FILE"
echo "  ✅ Comando corregido"

# 3. Habilitar backup (opcional pero recomendado)
echo "  [3/3] Habilitando backup automático..."
sed -i 's/^BACKUP_ENABLED=false/BACKUP_ENABLED=true/' "$CONFIG_FILE"
sed -i 's/^BACKUP_AUTO_BEFORE_DEPLOY=false/BACKUP_AUTO_BEFORE_DEPLOY=true/' "$CONFIG_FILE"
echo "  ✅ Backup habilitado"

echo ""
echo "════════════════════════════════════════════════════════════════════════════"
echo "  ✅ Configuración corregida exitosamente"
echo "════════════════════════════════════════════════════════════════════════════"
echo ""

echo "📊 Cambios aplicados:"
echo ""
echo "  ✅ MIGRATIONS_ENABLED=true"
echo "  ✅ MIGRATIONS_AUTO=true"
echo "  ✅ Comando de migraciones corregido (head)"
echo "  ✅ BACKUP_ENABLED=true"
echo "  ✅ BACKUP_AUTO_BEFORE_DEPLOY=true"
echo ""

echo "════════════════════════════════════════════════════════════════════════════"
echo "  📋 Verificación de Cambios"
echo "════════════════════════════════════════════════════════════════════════════"
echo ""

echo "Configuración actual de migraciones:"
grep -E "^MIGRATIONS_ENABLED|^MIGRATIONS_AUTO|^MIGRATIONS_COMMAND" "$CONFIG_FILE"
echo ""

echo "Configuración actual de backup:"
grep -E "^BACKUP_ENABLED|^BACKUP_AUTO_BEFORE_DEPLOY" "$CONFIG_FILE"
echo ""

echo "════════════════════════════════════════════════════════════════════════════"
echo "  ⚠️  IMPORTANTE: Verificar Base de Datos"
echo "════════════════════════════════════════════════════════════════════════════"
echo ""
echo "Antes de ejecutar deploy.sh, verifica que:"
echo ""
echo "  1. Staging tiene una base de datos SEPARADA de producción"
echo "  2. El archivo .env.staging existe y está actualizado"
echo "  3. Tienes acceso SSH al servidor staging"
echo ""
echo "Para verificar la BD:"
echo "  ssh ubuntu@staging 'cat /home/ubuntu/paqueteria-staging/.env.staging | grep DATABASE_URL'"
echo ""

echo "════════════════════════════════════════════════════════════════════════════"
echo "  🚀 Próximos Pasos"
echo "════════════════════════════════════════════════════════════════════════════"
echo ""
echo "1. Verificar que staging tiene BD separada (comando arriba)"
echo "2. Ejecutar deploy:"
echo "   ./deploy.sh --env staging --deploy"
echo ""
echo "O en modo interactivo:"
echo "   ./deploy.sh"
echo "   Seleccionar: [E] Cambiar Entorno → staging"
echo "   Seleccionar: [1] Deploy Completo"
echo ""

echo "════════════════════════════════════════════════════════════════════════════"
echo "  💾 Backup de Configuración"
echo "════════════════════════════════════════════════════════════════════════════"
echo ""
echo "Si necesitas revertir los cambios:"
echo "  cp ${CONFIG_FILE}.backup.* $CONFIG_FILE"
echo ""
echo "Backups disponibles:"
ls -lh "${CONFIG_FILE}.backup."* 2>/dev/null || echo "  (ninguno anterior)"
echo ""

echo "✅ Listo para deploy"
