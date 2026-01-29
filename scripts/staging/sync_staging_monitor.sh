#!/bin/bash
# Monitor script para sincronización de staging
# Este script debe correr en el host (no en el contenedor)
# Se ejecuta como servicio o cron job

set -e

SIGNAL_FILE="/tmp/staging_sync_request"
RESULT_FILE="/tmp/staging_sync_result"
LOCK_FILE="/tmp/staging_sync.lock"

# Credenciales de base de datos
HOST="ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com"
USER="jveyes"
PASS='a?HC!2.*1#?[==:|289qAI=)#V4kDzl$'

# Detectar ruta de Docker
DOCKER_CMD=""
if command -v docker &> /dev/null; then
    DOCKER_CMD="docker"
elif command -v /usr/bin/docker &> /dev/null; then
    DOCKER_CMD="/usr/bin/docker"
elif [ -f /usr/local/bin/docker ]; then
    DOCKER_CMD="/usr/local/bin/docker"
else
    echo "❌ ERROR: Docker no encontrado"
    echo "Intentando usar el script simple_sync.sh como alternativa..."
    DOCKER_CMD=""
fi

echo "🔍 Monitor de sincronización iniciado..."
echo "📁 Esperando señal en: $SIGNAL_FILE"
if [ -n "$DOCKER_CMD" ]; then
    echo "🐳 Docker encontrado en: $DOCKER_CMD"
else
    echo "⚠️  Docker no encontrado, usando método alternativo"
fi

while true; do
    # Verificar si existe el archivo de señal
    if [ -f "$SIGNAL_FILE" ]; then
        echo ""
        echo "🔔 Señal de sincronización detectada!"
        
        # Verificar que no haya otra sincronización en curso
        if [ -f "$LOCK_FILE" ]; then
            echo "⚠️  Ya hay una sincronización en curso"
            sleep 5
            continue
        fi
        
        # Crear lock file
        touch "$LOCK_FILE"
        
        # Limpiar resultado anterior
        rm -f "$RESULT_FILE"
        
        echo "🔄 Iniciando sincronización..."
        
        # Método 1: Usar Docker si está disponible
        if [ -n "$DOCKER_CMD" ]; then
            echo "📦 Usando Docker para sincronización..."
            if $DOCKER_CMD run --rm \
                -e PGPASSWORD="$PASS" \
                postgres:17-alpine \
                sh -c "
                    echo '📦 Exportando producción...';
                    pg_dump -h '$HOST' -U '$USER' -d paqueteria_v4 -F c -f /tmp/backup.dump --no-owner --no-acl;
                    echo '✅ Exportado';
                    echo '';
                    echo '📥 Restaurando en staging...';
                    pg_restore -h '$HOST' -U '$USER' -d paqueteria_staging /tmp/backup.dump --clean --if-exists --no-owner --no-acl 2>&1 | grep -v '^WARNING' || true;
                    echo '✅ Restaurado';
                "; then
                
                echo "✅ Sincronización completada exitosamente"
                echo "success" > "$RESULT_FILE"
            else
                echo "❌ Error en la sincronización"
                echo "error: Falló la sincronización de base de datos" > "$RESULT_FILE"
            fi
        
        # Método 2: Usar simple_sync.sh si existe
        elif [ -f ~/simple_sync.sh ]; then
            echo "📦 Usando simple_sync.sh..."
            if bash ~/simple_sync.sh > /tmp/sync_output.log 2>&1; then
                echo "✅ Sincronización completada exitosamente"
                echo "success" > "$RESULT_FILE"
            else
                echo "❌ Error en la sincronización"
                cat /tmp/sync_output.log
                echo "error: Falló la sincronización. Ver /tmp/sync_output.log" > "$RESULT_FILE"
            fi
        
        # Método 3: Error - no hay forma de sincronizar
        else
            echo "❌ No se encontró método de sincronización"
            echo "error: Docker no disponible y simple_sync.sh no encontrado" > "$RESULT_FILE"
        fi
        
        # Limpiar archivos
        rm -f "$SIGNAL_FILE"
        rm -f "$LOCK_FILE"
        
        echo "🏁 Proceso completado"
        echo ""
    fi
    
    # Esperar 5 segundos antes de verificar de nuevo
    sleep 5
done
