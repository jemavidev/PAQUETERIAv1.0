#!/bin/bash
# Script para reiniciar el servidor y cargar los fixes

echo "============================================================"
echo "REINICIANDO SERVIDOR PARA CARGAR FIXES"
echo "============================================================"

# Verificar si hay docker-compose
if [ -f "docker-compose.yml" ] || [ -f "docker-compose.staging.yml" ]; then
    echo ""
    echo "🐳 Detectado Docker Compose"
    echo ""
    
    # Determinar qué archivo usar
    if [ -f "docker-compose.staging.yml" ]; then
        COMPOSE_FILE="docker-compose.staging.yml"
    else
        COMPOSE_FILE="docker-compose.yml"
    fi
    
    echo "📄 Usando: $COMPOSE_FILE"
    echo ""
    
    # Reiniciar contenedor web
    echo "🔄 Reiniciando contenedor web..."
    docker-compose -f $COMPOSE_FILE restart web
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Servidor reiniciado correctamente"
        echo ""
        echo "⏳ Esperando 5 segundos para que el servidor inicie..."
        sleep 5
        
        # Verificar que el servidor responde
        echo ""
        echo "🔍 Verificando servidor..."
        response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/ 2>/dev/null)
        
        if [ "$response" = "200" ] || [ "$response" = "307" ] || [ "$response" = "302" ]; then
            echo "✅ Servidor respondiendo correctamente (HTTP $response)"
            echo ""
            echo "============================================================"
            echo "✅ LISTO PARA CARGAR ARCHIVOS XML"
            echo "============================================================"
            echo ""
            echo "Ahora puedes:"
            echo "1. Ir a: http://localhost:8000/invoices/cufe"
            echo "2. Refrescar el navegador (Ctrl + Shift + R)"
            echo "3. Cargar los archivos XML"
            echo ""
        else
            echo "⚠️  Servidor no responde aún (HTTP $response)"
            echo "   Espera unos segundos más e intenta cargar los XMLs"
        fi
    else
        echo ""
        echo "❌ Error al reiniciar el servidor"
        echo "   Intenta manualmente: docker-compose -f $COMPOSE_FILE restart web"
    fi
    
else
    echo ""
    echo "⚠️  No se encontró docker-compose.yml"
    echo ""
    echo "Si el servidor está corriendo localmente:"
    echo "1. Detén el servidor (Ctrl+C en la terminal donde corre)"
    echo "2. Inicia de nuevo: cd CODE && ./start_server.sh"
    echo ""
fi
