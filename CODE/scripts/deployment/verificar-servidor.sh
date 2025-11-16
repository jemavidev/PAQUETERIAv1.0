#!/bin/bash
# Script simple de verificación del servidor
# Ejecutar en el servidor: bash verificar-servidor.sh

echo "========================================="
echo "🔍 VERIFICACIÓN DEL SERVIDOR"
echo "========================================="
echo ""

# Ir a la raíz del proyecto
cd ~/paqueteria 2>/dev/null || cd /home/ubuntu/paqueteria 2>/dev/null || {
    echo "❌ No se encontró el directorio del proyecto"
    exit 1
}

echo "✓ Directorio del proyecto: $(pwd)"
echo ""

# 1. Verificar Git
echo "1. Verificando Git..."
if [ -d .git ]; then
    echo "  ✓ Repositorio Git encontrado"
    
    # Cambios sin commitear
    if git diff-index --quiet HEAD -- 2>/dev/null; then
        echo "  ✓ No hay cambios sin commitear"
    else
        echo "  ⚠ Hay cambios sin commitear:"
        git status --short 2>/dev/null | head -5 | sed 's/^/    /'
    fi
    
    # Estado de sincronización
    CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "main")
    echo "  ✓ Rama actual: $CURRENT_BRANCH"
else
    echo "  ✗ No se encontró repositorio Git"
fi
echo ""

# 2. Verificar Docker
echo "2. Verificando Docker..."
if command -v docker &> /dev/null; then
    echo "  ✓ Docker instalado"
    
    # Volúmenes
    echo "  Volúmenes Docker:"
    docker volume ls 2>/dev/null | grep -E "redis|upload|log|celery|prometheus|grafana" | while read line; do
        echo "    ✓ $line"
    done
    
    # Contenedores
    echo "  Contenedores:"
    if docker ps 2>/dev/null | grep -q "paqueteria"; then
        docker ps --format "  ✓ {{.Names}} - {{.Status}}" 2>/dev/null | grep paqueteria
    else
        echo "    ⚠ No hay contenedores en ejecución"
    fi
else
    echo "  ✗ Docker no está instalado"
fi
echo ""

# 3. Verificar archivos críticos
echo "3. Verificando archivos críticos..."
CRITICAL_FILES=(
    "CODE/.env"
    "docker-compose.prod.yml"
    "CODE/Dockerfile"
    "CODE/requirements.txt"
)

for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file existe"
    else
        echo "  ✗ $file NO existe"
    fi
done
echo ""

# 4. Verificar scripts
echo "4. Verificando scripts de deployment..."
if [ -d "CODE/scripts/deployment" ]; then
    echo "  ✓ Directorio de scripts existe"
    ls -1 CODE/scripts/deployment/*.sh 2>/dev/null | while read script; do
        if [ -x "$script" ]; then
            echo "  ✓ $(basename $script) (ejecutable)"
        else
            echo "  ⚠ $(basename $script) (NO ejecutable)"
        fi
    done
else
    echo "  ✗ Directorio de scripts NO existe"
fi
echo ""

# 5. Resumen de volúmenes persistentes
echo "5. Resumen de persistencia:"
echo "  Los siguientes datos son PERSISTENTES:"
echo "    ✓ Código fuente (en Git o montaje local)"
echo "    ✓ Volúmenes Docker (redis_data, uploads_data, logs_data, etc.)"
echo "    ✓ Archivos de configuración (.env, docker-compose.yml)"
echo ""
echo "========================================="
echo "✅ Verificación completada"
echo "========================================="

