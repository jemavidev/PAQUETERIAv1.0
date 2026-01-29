#!/bin/bash
# Script de instalación completa para sincronización staging

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║   🚀 INSTALACIÓN SINCRONIZACIÓN STAGING                      ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Verificar que estamos en el servidor correcto
if [ ! -d ~/paqueteria-staging ]; then
    echo "❌ ERROR: No se encuentra el directorio ~/paqueteria-staging"
    echo "   ¿Estás en el servidor staging?"
    exit 1
fi

echo "📋 Paso 1/5: Verificar PostgreSQL client"
echo "─────────────────────────────────────────────────────────────────"

if command -v pg_dump &> /dev/null; then
    echo "✅ PostgreSQL client ya está instalado"
    pg_dump --version
else
    echo "⚠️  PostgreSQL client no encontrado, instalando..."
    sudo dnf install -y postgresql
    
    if [ $? -eq 0 ]; then
        echo "✅ PostgreSQL client instalado"
    else
        echo "❌ Error instalando PostgreSQL client"
        exit 1
    fi
fi
echo ""

echo "📋 Paso 2/5: Crear script de sincronización"
echo "─────────────────────────────────────────────────────────────────"

cat > ~/sync_manual.sh << 'EOF'
#!/bin/bash
# Script manual de sincronización producción → staging

HOST="ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com"
USER="jveyes"
PASS='a?HC!2.*1#?[==:|289qAI=)#V4kDzl$'

export PGPASSWORD="$PASS"

echo "🔄 Sincronizando producción → staging..."
echo ""

# Exportar producción
echo "📦 Exportando producción..."
pg_dump -h "$HOST" -U "$USER" -d paqueteria_v4 -F c -f /tmp/backup.dump --no-owner --no-acl

if [ $? -eq 0 ]; then
    echo "✅ Exportado"
else
    echo "❌ Error en exportación"
    exit 1
fi

echo ""

# Restaurar en staging
echo "📥 Restaurando en staging..."
pg_restore -h "$HOST" -U "$USER" -d paqueteria_staging /tmp/backup.dump --clean --if-exists --no-owner --no-acl 2>&1 | grep -v "^WARNING" || true

if [ $? -le 1 ]; then
    echo "✅ Restaurado"
else
    echo "❌ Error en restauración"
    exit 1
fi

echo ""
echo "✅ Sincronización completada"
rm -f /tmp/backup.dump
EOF

chmod +x ~/sync_manual.sh
echo "✅ Script creado en ~/sync_manual.sh"
echo ""

echo "📋 Paso 3/5: Probar script de sincronización"
echo "─────────────────────────────────────────────────────────────────"
echo "⚠️  Esto puede tardar 1-3 minutos..."
echo ""

if ~/sync_manual.sh; then
    echo ""
    echo "✅ Script de sincronización funciona correctamente"
else
    echo ""
    echo "❌ Error en el script de sincronización"
    echo "   Por favor revisa los logs arriba"
    exit 1
fi
echo ""

echo "📋 Paso 4/5: Actualizar código de la aplicación"
echo "─────────────────────────────────────────────────────────────────"

# Verificar que el archivo actualizado existe
if [ ! -f ~/CODE/src/app/routes/sync_staging.py ]; then
    echo "⚠️  Archivo sync_staging.py no encontrado en ~/CODE/"
    echo "   Necesitas subirlo primero con:"
    echo "   scp CODE/src/app/routes/sync_staging.py staging:~/CODE/src/app/routes/"
    echo ""
    read -p "¿Ya subiste el archivo? (s/n): " respuesta
    if [ "$respuesta" != "s" ]; then
        echo "Por favor sube el archivo y ejecuta este script de nuevo"
        exit 1
    fi
fi

# Copiar archivo actualizado
cp ~/CODE/src/app/routes/sync_staging.py ~/paqueteria-staging/CODE/src/app/routes/sync_staging.py
echo "✅ Código actualizado"
echo ""

echo "📋 Paso 5/5: Reiniciar aplicación"
echo "─────────────────────────────────────────────────────────────────"

cd ~/paqueteria-staging

# Detectar comando docker compose
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
elif docker compose version &> /dev/null 2>&1; then
    DOCKER_COMPOSE="docker compose"
else
    echo "❌ No se encontró docker-compose"
    exit 1
fi

echo "Reiniciando aplicación..."
$DOCKER_COMPOSE -f docker-compose.staging.yml restart app

if [ $? -eq 0 ]; then
    echo "✅ Aplicación reiniciada"
else
    echo "❌ Error reiniciando aplicación"
    exit 1
fi

echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║   ✅ INSTALACIÓN COMPLETADA                                  ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "📝 Próximos pasos:"
echo "   1. Abrir staging en el navegador"
echo "   2. Click en '🔄 Sincronizar'"
echo "   3. Confirmar y esperar"
echo ""
echo "🔍 Para ver logs:"
echo "   docker logs -f paqueteria_staging_app"
echo ""
echo "🔧 Para sincronizar manualmente:"
echo "   ~/sync_manual.sh"
echo ""
