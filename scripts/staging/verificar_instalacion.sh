#!/bin/bash
# Script para verificar que la instalación fue exitosa

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║   🔍 VERIFICACIÓN DE INSTALACIÓN                             ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Verificar PostgreSQL client
echo "1️⃣  PostgreSQL client:"
if command -v pg_dump &> /dev/null; then
    echo "   ✅ Instalado: $(pg_dump --version | head -1)"
else
    echo "   ❌ NO instalado"
fi
echo ""

# Verificar script de sincronización
echo "2️⃣  Script de sincronización:"
if [ -f ~/sync_manual.sh ]; then
    echo "   ✅ Existe: ~/sync_manual.sh"
    if [ -x ~/sync_manual.sh ]; then
        echo "   ✅ Es ejecutable"
    else
        echo "   ⚠️  No es ejecutable (ejecutar: chmod +x ~/sync_manual.sh)"
    fi
else
    echo "   ❌ NO existe"
fi
echo ""

# Verificar código actualizado
echo "3️⃣  Código de la aplicación:"
if [ -f ~/paqueteria-staging/CODE/src/app/routes/sync_staging.py ]; then
    echo "   ✅ Archivo existe"
    # Verificar que tiene el código nuevo
    if grep -q "sync_manual.sh" ~/paqueteria-staging/CODE/src/app/routes/sync_staging.py; then
        echo "   ✅ Código actualizado (contiene referencia a sync_manual.sh)"
    else
        echo "   ⚠️  Código podría no estar actualizado"
    fi
else
    echo "   ❌ Archivo NO existe"
fi
echo ""

# Verificar contenedor
echo "4️⃣  Contenedor de staging:"
if docker ps | grep -q paqueteria_staging_app; then
    echo "   ✅ Contenedor corriendo"
    docker ps | grep paqueteria_staging_app | awk '{print "   ID: " $1 " | Status: " $7}'
else
    echo "   ❌ Contenedor NO está corriendo"
fi
echo ""

# Verificar conectividad a RDS
echo "5️⃣  Conectividad a RDS:"
if ping -c 1 ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com &> /dev/null; then
    echo "   ✅ Servidor RDS alcanzable"
else
    echo "   ⚠️  No se puede hacer ping al servidor RDS (puede ser normal si bloquea ICMP)"
fi
echo ""

# Probar conexión a base de datos
echo "6️⃣  Conexión a base de datos:"
export PGPASSWORD='a?HC!2.*1#?[==:|289qAI=)#V4kDzl$'
if psql -h ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com \
        -U jveyes -d paqueteria_v4 -c "SELECT 1;" &> /dev/null; then
    echo "   ✅ Conexión a paqueteria_v4 exitosa"
else
    echo "   ❌ No se puede conectar a paqueteria_v4"
fi

if psql -h ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com \
        -U jveyes -d paqueteria_staging -c "SELECT 1;" &> /dev/null; then
    echo "   ✅ Conexión a paqueteria_staging exitosa"
else
    echo "   ❌ No se puede conectar a paqueteria_staging"
fi
echo ""

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║   📝 RESUMEN                                                  ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Contar checks exitosos
checks_ok=0
checks_total=6

command -v pg_dump &> /dev/null && ((checks_ok++))
[ -f ~/sync_manual.sh ] && [ -x ~/sync_manual.sh ] && ((checks_ok++))
[ -f ~/paqueteria-staging/CODE/src/app/routes/sync_staging.py ] && ((checks_ok++))
docker ps | grep -q paqueteria_staging_app && ((checks_ok++))
psql -h ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com \
     -U jveyes -d paqueteria_v4 -c "SELECT 1;" &> /dev/null && ((checks_ok++))
psql -h ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com \
     -U jveyes -d paqueteria_staging -c "SELECT 1;" &> /dev/null && ((checks_ok++))

echo "Verificaciones exitosas: $checks_ok/$checks_total"
echo ""

if [ $checks_ok -eq $checks_total ]; then
    echo "✅ TODO ESTÁ LISTO"
    echo ""
    echo "Próximos pasos:"
    echo "  1. Probar sincronización manual: ~/sync_manual.sh"
    echo "  2. Probar desde navegador: Click en '🔄 Sincronizar'"
elif [ $checks_ok -ge 4 ]; then
    echo "⚠️  CASI LISTO (algunos checks fallaron pero puede funcionar)"
    echo ""
    echo "Intenta probar la sincronización manual: ~/sync_manual.sh"
else
    echo "❌ FALTAN COMPONENTES"
    echo ""
    echo "Ejecuta el instalador: ./instalar_sync_completo.sh"
fi
echo ""
