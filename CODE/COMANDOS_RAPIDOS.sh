#!/bin/bash
# Comandos rápidos para migración de productos

echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                    COMANDOS RÁPIDOS - MIGRACIÓN DE PRODUCTOS                ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Activar entorno virtual
if [ ! -d ".venv" ]; then
    echo "❌ Error: No se encontró el entorno virtual .venv"
    echo "   Ejecuta este script desde el directorio CODE/"
    exit 1
fi

source .venv/bin/activate

echo "✅ Entorno virtual activado"
echo ""
echo "Comandos disponibles:"
echo ""
echo "1️⃣  Prueba rápida (3 facturas, DRY-RUN)"
echo "   → python3 quick_test_migration.py"
echo ""
echo "2️⃣  Prueba con 10 facturas (DRY-RUN)"
echo "   → python3 migrate_reprocess_products.py --dry-run 10"
echo ""
echo "3️⃣  Prueba con 50 facturas (DRY-RUN)"
echo "   → python3 migrate_reprocess_products.py --dry-run 50"
echo ""
echo "4️⃣  Migrar 10 facturas (PRODUCCIÓN)"
echo "   → python3 migrate_reprocess_products.py 10"
echo ""
echo "5️⃣  Migrar TODAS las facturas (PRODUCCIÓN)"
echo "   → python3 migrate_reprocess_products.py"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Preguntar qué quiere hacer
read -p "¿Qué comando quieres ejecutar? (1-5, o 'q' para salir): " opcion

case $opcion in
    1)
        echo ""
        echo "🚀 Ejecutando prueba rápida..."
        python3 quick_test_migration.py
        ;;
    2)
        echo ""
        echo "🚀 Ejecutando prueba con 10 facturas (DRY-RUN)..."
        python3 migrate_reprocess_products.py --dry-run 10
        ;;
    3)
        echo ""
        echo "🚀 Ejecutando prueba con 50 facturas (DRY-RUN)..."
        python3 migrate_reprocess_products.py --dry-run 50
        ;;
    4)
        echo ""
        echo "⚠️  ADVERTENCIA: Esto modificará la base de datos"
        read -p "¿Estás seguro? (s/n): " confirmar
        if [ "$confirmar" = "s" ] || [ "$confirmar" = "S" ]; then
            echo "🚀 Ejecutando migración de 10 facturas..."
            python3 migrate_reprocess_products.py 10
        else
            echo "❌ Cancelado"
        fi
        ;;
    5)
        echo ""
        echo "⚠️  ADVERTENCIA: Esto migrará TODAS las facturas"
        echo "   Asegúrate de haber hecho backup de la base de datos"
        read -p "¿Estás seguro? (s/n): " confirmar
        if [ "$confirmar" = "s" ] || [ "$confirmar" = "S" ]; then
            echo "🚀 Ejecutando migración completa..."
            python3 migrate_reprocess_products.py
        else
            echo "❌ Cancelado"
        fi
        ;;
    q|Q)
        echo "👋 Saliendo..."
        ;;
    *)
        echo "❌ Opción inválida"
        ;;
esac

echo ""
echo "✅ Listo!"
