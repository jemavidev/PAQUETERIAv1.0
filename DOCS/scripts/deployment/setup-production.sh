#!/bin/bash
# Script de configuración completa de producción
# PAQUETERÍA v1.0
# 
# Este script configura todo lo necesario para producción:
# - Nginx con proxy reverso
# - Servicio systemd para auto-start
# - SSL con Let's Encrypt
# - Scripts de verificación

set -euo pipefail

DOMAIN="${1:-paquetex.papyrus.com.co}"
EMAIL="${2:-admin@papyrus.com.co}"
PROJECT_DIR="${3:-$(pwd)}"

info() { echo -e "\033[0;34m[INFO]\033[0m $1"; }
success() { echo -e "\033[0;32m[SUCCESS]\033[0m $1"; }
error() { echo -e "\033[0;31m[ERROR]\033[0m $1"; }
warning() { echo -e "\033[0;33m[WARNING]\033[0m $1"; }

# Verificar que se ejecuta como root
if [ "$EUID" -ne 0 ]; then 
    error "Por favor ejecuta como root (usa sudo)"
    exit 1
fi

info "🚀 Configuración de Producción - PAQUETERÍA v1.0"
info "Dominio: $DOMAIN"
info "Email: $EMAIL"
info "Directorio: $PROJECT_DIR"
echo ""

# ========================================
# 1. CONFIGURAR NGINX
# ========================================
info "📋 Paso 1: Configurando Nginx..."

# Crear configuración de Nginx
if [ -f "$PROJECT_DIR/DOCS/scripts/deployment/nginx-production.conf" ]; then
    info "Copiando configuración Nginx desde proyecto..."
    cp "$PROJECT_DIR/DOCS/scripts/deployment/nginx-production.conf" "/etc/nginx/sites-available/$DOMAIN"
else
    error "No se encontró nginx-production.conf en $PROJECT_DIR/DOCS/scripts/deployment/"
    error "Por favor, crea la configuración manualmente."
    exit 1
fi

# Crear directorio para certbot
mkdir -p /var/www/certbot
chown www-data:www-data /var/www/certbot

# Habilitar sitio
ln -sf "/etc/nginx/sites-available/$DOMAIN" "/etc/nginx/sites-enabled/$DOMAIN"

# Verificar configuración
if nginx -t; then
    success "Configuración Nginx válida"
else
    error "Error en configuración Nginx"
    exit 1
fi

# Recargar Nginx
systemctl reload nginx
success "Nginx configurado"

# Habilitar para auto-start
systemctl enable nginx
success "Nginx habilitado para auto-start"

echo ""

# ========================================
# 2. CONFIGURAR SERVICIO SYSTEMD
# ========================================
info "📋 Paso 2: Configurando servicio systemd..."

# Detectar archivo compose
if [ -f "$PROJECT_DIR/docker-compose.prod.yml" ]; then
    COMPOSE_FILE="docker-compose.prod.yml"
elif [ -f "$PROJECT_DIR/docker-compose.yml" ]; then
    COMPOSE_FILE="docker-compose.yml"
else
    COMPOSE_FILE="docker-compose.prod.yml"
fi

if [ -f "$PROJECT_DIR/DOCS/scripts/deployment/paqueteria.service" ]; then
    info "Copiando servicio systemd desde proyecto..."
    cp "$PROJECT_DIR/DOCS/scripts/deployment/paqueteria.service" /etc/systemd/system/paqueteria.service
    
    # Actualizar WorkingDirectory y archivo compose
    sed -i "s|WorkingDirectory=.*|WorkingDirectory=$PROJECT_DIR|g" /etc/systemd/system/paqueteria.service
    sed -i "s|ExecStart=.*docker compose -f docker-compose.yml|ExecStart=/usr/bin/docker compose -f $COMPOSE_FILE|g" /etc/systemd/system/paqueteria.service
    sed -i "s|ExecStop=.*docker compose -f docker-compose.yml|ExecStop=/usr/bin/docker compose -f $COMPOSE_FILE|g" /etc/systemd/system/paqueteria.service
    sed -i "s|ExecReload=.*docker compose -f docker-compose.yml|ExecReload=/usr/bin/docker compose -f $COMPOSE_FILE|g" /etc/systemd/system/paqueteria.service
    
    systemctl daemon-reload
    systemctl enable paqueteria.service
    success "Servicio systemd configurado y habilitado"
else
    error "No se encontró paqueteria.service en $PROJECT_DIR/DOCS/scripts/deployment/"
    warning "Creando servicio systemd básico..."
    cat > /etc/systemd/system/paqueteria.service << EOF
[Unit]
Description=PAQUETERÍA v1.0 - Docker Compose Application
Requires=docker.service
After=docker.service network-online.target
Wants=network-online.target

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$PROJECT_DIR
ExecStart=/usr/bin/docker compose -f $COMPOSE_FILE up -d
ExecStop=/usr/bin/docker compose -f $COMPOSE_FILE down
ExecReload=/usr/bin/docker compose -f $COMPOSE_FILE restart
TimeoutStartSec=0
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
    systemctl daemon-reload
    systemctl enable paqueteria.service
    success "Servicio systemd creado y habilitado"
fi

echo ""

# ========================================
# 3. CONFIGURAR SSL (OPCIONAL)
# ========================================
info "📋 Paso 3: Configuración SSL (opcional)..."

read -p "¿Configurar SSL con Let's Encrypt ahora? (s/n): " configure_ssl

if [ "$configure_ssl" = "s" ] || [ "$configure_ssl" = "S" ]; then
    # Verificar que certbot está instalado
    if ! command -v certbot &> /dev/null; then
        warning "Certbot no está instalado. Instalando..."
        apt update
        apt install -y certbot python3-certbot-nginx
    fi
    
    # Verificar que la app está respondiendo
    if curl -s http://127.0.0.1:8000/health > /dev/null; then
        info "Configurando certificado SSL..."
        certbot --nginx -d "$DOMAIN" \
            --non-interactive \
            --agree-tos \
            --email "$EMAIL" \
            --redirect
        
        if [ $? -eq 0 ]; then
            success "SSL configurado exitosamente"
            
            # Verificar renovación automática
            if systemctl is-enabled certbot.timer > /dev/null 2>&1; then
                success "Renovación automática: HABILITADA"
            else
                warning "Habilitando renovación automática..."
                systemctl enable certbot.timer
                systemctl start certbot.timer
                success "Renovación automática habilitada"
            fi
        else
            error "Error configurando SSL"
            warning "Puedes configurar SSL manualmente después con:"
            warning "  sudo certbot --nginx -d $DOMAIN"
        fi
    else
        warning "La aplicación no está respondiendo en 127.0.0.1:8000"
        warning "Asegúrate de que los contenedores estén corriendo antes de configurar SSL"
        warning "Puedes configurar SSL después con:"
        warning "  sudo certbot --nginx -d $DOMAIN"
    fi
else
    info "SSL se configurará después"
    info "Usa: sudo certbot --nginx -d $DOMAIN"
fi

echo ""

# ========================================
# 4. INSTALAR SCRIPTS DE VERIFICACIÓN
# ========================================
info "📋 Paso 4: Instalando scripts de verificación..."

# Script de verificación de servicios
cat > /usr/local/bin/verify-paqueteria.sh << VERIFY_EOF
#!/bin/bash
# Script de verificación de servicios post-reinicio
# PAQUETERÍA v1.0

PROJECT_DIR="${PROJECT_DIR:-/opt/paqueteria/Paqueteria-v1.0}"
COMPOSE_FILE="docker-compose.prod.yml"

if [ -f "\$PROJECT_DIR/docker-compose.prod.yml" ]; then
    COMPOSE_FILE="docker-compose.prod.yml"
elif [ -f "\$PROJECT_DIR/docker-compose.yml" ]; then
    COMPOSE_FILE="docker-compose.yml"
fi

echo "🔍 Verificando servicios PAQUETERÍA v1.0..."
echo "=========================================="

# Verificar Docker
if systemctl is-active --quiet docker; then
    echo "✅ Docker: ACTIVO"
else
    echo "❌ Docker: INACTIVO"
    exit 1
fi

# Verificar Docker Compose
if systemctl is-active --quiet paqueteria.service; then
    echo "✅ Paqueteria Service: ACTIVO"
else
    echo "⚠️ Paqueteria Service: INACTIVO (intentando iniciar...)"
    sudo systemctl start paqueteria.service
    sleep 5
    if systemctl is-active --quiet paqueteria.service; then
        echo "✅ Paqueteria Service: INICIADO"
    else
        echo "❌ Paqueteria Service: ERROR al iniciar"
    fi
fi

# Verificar Nginx
if systemctl is-active --quiet nginx; then
    echo "✅ Nginx: ACTIVO"
else
    echo "⚠️ Nginx: INACTIVO (intentando iniciar...)"
    sudo systemctl start nginx
    sleep 2
    if systemctl is-active --quiet nginx; then
        echo "✅ Nginx: INICIADO"
    else
        echo "❌ Nginx: ERROR al iniciar"
    fi
fi

# Verificar contenedores
echo ""
echo "📦 Estado de contenedores:"
cd "\$PROJECT_DIR" && docker compose -f "\$COMPOSE_FILE" ps

# Verificar health check
echo ""
echo "🏥 Health Check:"
curl -s http://127.0.0.1:8000/health | head -1 || echo "❌ Health check falló"

echo ""
echo "✅ Verificación completada"
VERIFY_EOF

chmod +x /usr/local/bin/verify-paqueteria.sh
success "Script de verificación instalado"

echo ""

# ========================================
# RESUMEN
# ========================================
success "✅ Configuración de producción completada"
echo ""
info "Resumen de cambios:"
echo "  ✅ Nginx configurado en /etc/nginx/sites-available/$DOMAIN"
echo "  ✅ Servicio systemd en /etc/systemd/system/paqueteria.service"
echo "  ✅ Scripts de verificación instalados"
if [ "$configure_ssl" = "s" ] || [ "$configure_ssl" = "S" ]; then
    echo "  ✅ SSL configurado"
fi
echo ""
info "Próximos pasos:"
echo "  1. Verificar servicios: sudo /usr/local/bin/verify-paqueteria.sh"
echo "  2. Reiniciar servidor para probar auto-start: sudo reboot"
echo "  3. Ver logs: sudo journalctl -u paqueteria.service -f"
echo ""
success "🎉 ¡Listo para producción!"

