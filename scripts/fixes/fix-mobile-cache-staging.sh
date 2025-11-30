#!/bin/bash
# Script para forzar actualización del footer en móvil - staging
# Fecha: 2025-11-28

set -e

echo "🔄 =========================================="
echo "   FIX CACHÉ MÓVIL - STAGING"
echo "   =========================================="
echo ""

echo "📋 Conectando a servidor staging..."
ssh staging << 'ENDSSH'
cd paqueteria-staging

echo ""
echo "📋 Paso 1: Verificando commit actual..."
git log -1 --oneline

echo ""
echo "📋 Paso 2: Deteniendo contenedores..."
docker compose -f docker-compose.staging.yml down

echo ""
echo "📋 Paso 3: Limpiando volúmenes y caché de Docker..."
docker system prune -f
docker volume prune -f

echo ""
echo "📋 Paso 4: Reconstruyendo COMPLETAMENTE (sin caché)..."
docker compose -f docker-compose.staging.yml build --no-cache --pull

echo ""
echo "📋 Paso 5: Iniciando contenedores..."
docker compose -f docker-compose.staging.yml up -d

echo ""
echo "📋 Paso 6: Esperando que los servicios estén listos..."
sleep 15

echo ""
echo "📋 Paso 7: Reiniciando nginx para forzar headers..."
docker compose -f docker-compose.staging.yml restart nginx

echo ""
echo "📋 Paso 8: Verificando estado..."
docker compose -f docker-compose.staging.yml ps

echo ""
echo "📋 Paso 9: Verificando logs de nginx..."
docker compose -f docker-compose.staging.yml logs --tail=20 nginx

echo ""
echo "✅ =========================================="
echo "   ACTUALIZACIÓN COMPLETADA"
echo "   =========================================="
ENDSSH

echo ""
echo "🎉 ¡Servidor actualizado!"
echo ""
echo "📱 AHORA EN TU CELULAR:"
echo "   =========================================="
echo ""
echo "   1️⃣  CIERRA COMPLETAMENTE el navegador"
echo "       (no solo la pestaña, cierra la app)"
echo ""
echo "   2️⃣  Borra el caché:"
echo "       • Chrome: Ajustes → Privacidad → Borrar caché"
echo "       • Safari: Ajustes → Safari → Borrar historial"
echo ""
echo "   3️⃣  Abre el navegador de nuevo"
echo ""
echo "   4️⃣  Visita: https://staging.jemavi.co/announce"
echo ""
echo "   5️⃣  Deberías ver el footer con 4 iconos:"
echo "       📢 Anunciar | 🔍 Buscar | ❓ Ayuda | 🔐 Ingresar"
echo ""
echo "   =========================================="
echo ""
echo "💡 Si aún no funciona, prueba en MODO INCÓGNITO"
echo ""

