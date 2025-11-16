#!/bin/bash
# Script con soluciones alternativas para archivos estáticos

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║     SOLUCIONES ALTERNATIVAS PARA ARCHIVOS ESTÁTICOS          ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo "Este script ofrece 3 soluciones alternativas:"
echo ""
echo "1. Copiar archivos estáticos dentro de la imagen Docker"
echo "2. Servir archivos estáticos directamente con Nginx"
echo "3. Crear un volumen específico para archivos estáticos"
echo ""

read -p "Selecciona una opción (1-3): " OPTION

case $OPTION in
    1)
        echo ""
        echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
        echo -e "${YELLOW}SOLUCIÓN 1: Copiar archivos en la imagen Docker${NC}"
        echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
        echo ""
        
        echo "Esta solución copia los archivos estáticos dentro de la imagen Docker"
        echo "durante el build, en lugar de montarlos como volumen."
        echo ""
        
        read -p "¿Deseas aplicar esta solución? (s/N): " -n 1 -r
        echo
        
        if [[ $REPLY =~ ^[Ss]$ ]]; then
            echo ""
            echo "Modificando Dockerfile..."
            
            # Backup del Dockerfile
            cp CODE/Dockerfile CODE/Dockerfile.backup-$(date +%Y%m%d-%H%M%S)
            
            # Verificar si ya existe la línea COPY
            if grep -q "COPY src/static" CODE/Dockerfile; then
                echo -e "${YELLOW}⚠️  La línea COPY ya existe en el Dockerfile${NC}"
            else
                # Agregar la línea COPY después de copiar src/
                sed -i '/COPY src\/ \/app\/src\//a COPY src/static/ /app/src/static/' CODE/Dockerfile
                echo -e "${GREEN}✅ Dockerfile modificado${NC}"
            fi
            
            echo ""
            echo "Ahora necesitas reconstruir la imagen:"
            echo ""
            echo "  docker compose -f docker-compose.lightsail.yml build --no-cache app"
            echo "  docker compose -f docker-compose.lightsail.yml up -d"
            echo ""
        fi
        ;;
        
    2)
        echo ""
        echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
        echo -e "${YELLOW}SOLUCIÓN 2: Servir archivos directamente con Nginx${NC}"
        echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
        echo ""
        
        echo "Esta solución configura Nginx para servir los archivos estáticos"
        echo "directamente desde el host, sin pasar por FastAPI."
        echo ""
        
        read -p "¿Deseas aplicar esta solución? (s/N): " -n 1 -r
        echo
        
        if [[ $REPLY =~ ^[Ss]$ ]]; then
            echo ""
            echo "Creando configuración de Nginx..."
            
            # Backup de la configuración
            cp CODE/nginx/nginx.lightsail.conf CODE/nginx/nginx.lightsail.conf.backup-$(date +%Y%m%d-%H%M%S)
            
            # Crear nueva configuración
            cat > CODE/nginx/nginx.lightsail.conf.new << 'EOF'
# Agregar esta sección ANTES de la configuración de proxy

        # Servir archivos estáticos directamente desde el host
        location /static/ {
            alias /ruta/al/proyecto/CODE/src/static/;
            expires 7d;
            add_header Cache-Control "public, immutable";
            access_log off;
        }
EOF
            
            echo -e "${GREEN}✅ Configuración creada en nginx.lightsail.conf.new${NC}"
            echo ""
            echo "IMPORTANTE: Debes editar manualmente el archivo y:"
            echo "1. Reemplazar '/ruta/al/proyecto' con la ruta real"
            echo "2. Mover esta sección ANTES del bloque 'location /static/' existente"
            echo "3. Reiniciar Nginx: sudo systemctl restart nginx"
            echo ""
        fi
        ;;
        
    3)
        echo ""
        echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
        echo -e "${YELLOW}SOLUCIÓN 3: Volumen específico para estáticos${NC}"
        echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
        echo ""
        
        echo "Esta solución crea un volumen Docker específico para archivos estáticos"
        echo "y los copia al iniciar el contenedor."
        echo ""
        
        read -p "¿Deseas aplicar esta solución? (s/N): " -n 1 -r
        echo
        
        if [[ $REPLY =~ ^[Ss]$ ]]; then
            echo ""
            echo "Modificando docker-compose.lightsail.yml..."
            
            # Backup
            cp docker-compose.lightsail.yml docker-compose.lightsail.yml.backup-$(date +%Y%m%d-%H%M%S)
            
            echo ""
            echo "Agrega estas líneas a docker-compose.lightsail.yml:"
            echo ""
            echo -e "${CYAN}En la sección 'volumes' del servicio 'app':${NC}"
            echo "  - static_data:/app/src/static"
            echo ""
            echo -e "${CYAN}En la sección 'volumes' global (al final):${NC}"
            echo "  static_data:"
            echo "    driver: local"
            echo ""
            echo -e "${CYAN}En el 'command' del servicio 'app', agrega al inicio:${NC}"
            echo "  cp -r /app/src/static/* /app/src/static/ 2>/dev/null || true &&"
            echo ""
            
            read -p "¿Deseas que el script haga estos cambios automáticamente? (s/N): " -n 1 -r
            echo
            
            if [[ $REPLY =~ ^[Ss]$ ]]; then
                # Aquí iría la lógica para modificar el archivo
                echo -e "${YELLOW}⚠️  Modificación automática no implementada${NC}"
                echo "Por favor, realiza los cambios manualmente"
            fi
        fi
        ;;
        
    *)
        echo -e "${RED}Opción inválida${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Proceso completado${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
