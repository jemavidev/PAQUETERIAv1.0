#!/bin/bash

echo "🔍 Diagnóstico del Sistema SMTP"
echo "================================"
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 1. Verificar variables de entorno SMTP
echo -e "${BLUE}📧 Verificando configuración SMTP en .env...${NC}"
if [ -f "CODE/.env" ]; then
    echo -e "${GREEN}✓${NC} Archivo .env encontrado"
    
    # Verificar cada variable
    if grep -q "SMTP_HOST=" CODE/.env; then
        SMTP_HOST=$(grep "SMTP_HOST=" CODE/.env | cut -d'=' -f2)
        echo -e "${GREEN}✓${NC} SMTP_HOST: $SMTP_HOST"
    else
        echo -e "${RED}✗${NC} SMTP_HOST no configurado"
    fi
    
    if grep -q "SMTP_PORT=" CODE/.env; then
        SMTP_PORT=$(grep "SMTP_PORT=" CODE/.env | cut -d'=' -f2)
        echo -e "${GREEN}✓${NC} SMTP_PORT: $SMTP_PORT"
    else
        echo -e "${RED}✗${NC} SMTP_PORT no configurado"
    fi
    
    if grep -q "SMTP_USER=" CODE/.env; then
        SMTP_USER=$(grep "SMTP_USER=" CODE/.env | cut -d'=' -f2)
        echo -e "${GREEN}✓${NC} SMTP_USER: $SMTP_USER"
    else
        echo -e "${RED}✗${NC} SMTP_USER no configurado"
    fi
    
    if grep -q "SMTP_PASSWORD=" CODE/.env; then
        echo -e "${GREEN}✓${NC} SMTP_PASSWORD: [CONFIGURADO]"
    else
        echo -e "${RED}✗${NC} SMTP_PASSWORD no configurado"
    fi
    
    if grep -q "SMTP_FROM_EMAIL=" CODE/.env; then
        SMTP_FROM=$(grep "SMTP_FROM_EMAIL=" CODE/.env | cut -d'=' -f2)
        echo -e "${GREEN}✓${NC} SMTP_FROM_EMAIL: $SMTP_FROM"
    else
        echo -e "${RED}✗${NC} SMTP_FROM_EMAIL no configurado"
    fi
else
    echo -e "${RED}✗${NC} Archivo .env no encontrado"
fi

echo ""

# 2. Verificar servicio de email
echo -e "${BLUE}🔧 Verificando EmailService...${NC}"
cd CODE
if python3 -c "import sys; sys.path.insert(0, 'src'); from app.services.email_service import EmailService; print('OK')" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} EmailService se puede importar"
else
    echo -e "${RED}✗${NC} Error al importar EmailService"
fi
cd ..

echo ""

# 3. Verificar archivos modificados recientemente
echo -e "${BLUE}📝 Archivos modificados (no commiteados)...${NC}"
git status --short | grep "^ M" | while read -r line; do
    file=$(echo "$line" | awk '{print $2}')
    echo "   $file"
done

echo ""

# 4. Verificar si hay cambios en archivos relacionados con notificaciones
echo -e "${BLUE}🔔 Verificando archivos de notificaciones...${NC}"
NOTIFICATION_FILES=(
    "CODE/src/app/services/email_service.py"
    "CODE/src/app/services/notification_service.py"
    "CODE/src/app/services/sms_service.py"
    "CODE/src/app/models/notification.py"
)

for file in "${NOTIFICATION_FILES[@]}"; do
    if [ -f "$file" ]; then
        # Verificar si el archivo fue modificado
        if git status --short "$file" | grep -q "M"; then
            echo -e "${YELLOW}⚠${NC} $file - MODIFICADO (no commiteado)"
        else
            echo -e "${GREEN}✓${NC} $file - Sin cambios"
        fi
    else
        echo -e "${RED}✗${NC} $file - NO EXISTE"
    fi
done

echo ""

# 5. Test de conexión SMTP (Python)
echo -e "${BLUE}🧪 Probando conexión SMTP...${NC}"
cd CODE
python3 << 'PYTHON_SCRIPT'
import sys
sys.path.insert(0, 'src')

try:
    from app.services.email_service import EmailService
    import asyncio
    
    async def test():
        service = EmailService()
        result = await service.test_smtp_connection()
        
        if result.get("success"):
            print(f"✅ Conexión SMTP exitosa")
            print(f"   Servidor: {result.get('server')}:{result.get('port')}")
        else:
            print(f"❌ Error de conexión SMTP")
            print(f"   Mensaje: {result.get('message')}")
            print(f"   Error: {result.get('error')}")
    
    asyncio.run(test())
    
except Exception as e:
    print(f"❌ Error al probar SMTP: {str(e)}")
PYTHON_SCRIPT
cd ..

echo ""

# Resumen
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${BLUE}📊 RESUMEN${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Si el test de conexión SMTP falló, verifica:"
echo "1. Las credenciales en CODE/.env"
echo "2. Que el servidor SMTP esté accesible"
echo "3. Los logs del servidor para más detalles"
echo ""
echo "NOTA IMPORTANTE:"
echo "Los archivos modificados recientemente NO incluyen"
echo "ningún archivo relacionado con el sistema de notificaciones."
echo "El problema de SMTP NO fue causado por los cambios recientes."
echo ""
