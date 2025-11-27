#!/bin/bash

# ========================================
# VERIFICACIÓN RÁPIDA: Fix de Loop de Redirección
# ========================================

BASE_URL="http://localhost:8000"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${CYAN}${BOLD}"
echo "========================================"
echo "  VERIFICACIÓN DEL FIX"
echo "  Loop de Redirección en Login"
echo "========================================"
echo -e "${NC}"

# Verificar que el servidor esté corriendo
echo -e "${BLUE}[1/3]${NC} Verificando servidor..."
if curl -s "$BASE_URL/health" | grep -q "healthy"; then
    echo -e "${GREEN}✓${NC} Servidor funcionando"
else
    echo -e "${RED}✗${NC} Servidor no responde"
    echo ""
    echo "Por favor, inicia el servidor primero:"
    echo "  cd CODE"
    echo "  docker-compose up -d"
    exit 1
fi

# Verificar que no haya ruta duplicada
echo -e "${BLUE}[2/3]${NC} Verificando código..."
duplicate_count=$(grep -c '@router.get("/auth/login")' src/app/routes/public.py 2>/dev/null || echo "0")

if [ "$duplicate_count" -eq "1" ]; then
    echo -e "${GREEN}✓${NC} Solo una definición de /auth/login (correcto)"
elif [ "$duplicate_count" -gt "1" ]; then
    echo -e "${RED}✗${NC} Hay $duplicate_count definiciones de /auth/login (debe ser 1)"
    echo ""
    echo "Acción requerida:"
    echo "  1. Abre: CODE/src/app/routes/public.py"
    echo "  2. Busca: @router.get(\"/auth/login\")"
    echo "  3. Elimina la definición duplicada (debe quedar solo la que tiene el fix)"
    echo "  4. Reinicia el servidor"
    exit 1
else
    echo -e "${YELLOW}!${NC} No se pudo verificar el archivo (puede estar en otra ubicación)"
fi

# Verificar comportamiento con token expirado
echo -e "${BLUE}[3/3]${NC} Verificando comportamiento con token expirado..."

COOKIE_FILE="/tmp/verify_cookies.txt"
cat > "$COOKIE_FILE" << EOF
# Netscape HTTP Cookie File
localhost	FALSE	/	FALSE	0	access_token	expired_token_test
localhost	FALSE	/	FALSE	0	user_id	999
EOF

response=$(curl -s -b "$COOKIE_FILE" "$BASE_URL/auth/login")

if echo "$response" | grep -qi "sesión ha expirado\|session.*expired"; then
    echo -e "${GREEN}✓${NC} Mensaje de sesión expirada funciona"
    FIX_WORKING=true
else
    echo -e "${RED}✗${NC} Mensaje de sesión expirada NO se muestra"
    FIX_WORKING=false
fi

rm -f "$COOKIE_FILE"

# Resultado final
echo ""
echo -e "${CYAN}${BOLD}========================================"
echo "  RESULTADO"
echo "========================================${NC}"
echo ""

if [ "$FIX_WORKING" = true ]; then
    echo -e "${GREEN}${BOLD}✓ EL FIX ESTÁ FUNCIONANDO${NC}"
    echo ""
    echo "Puedes proceder a probar manualmente:"
    echo ""
    echo "1. Abre tu navegador en modo incógnito"
    echo "2. Ve a: $BASE_URL/admin"
    echo "3. Inicia sesión con tus credenciales"
    echo "4. Verifica que NO entres en loop de redirección"
    echo ""
    echo "Credenciales sugeridas:"
    echo "  Usuario: jesus"
    echo "  Contraseña: jesusSeaboard12"
    echo ""
else
    echo -e "${RED}${BOLD}✗ EL FIX NO ESTÁ FUNCIONANDO${NC}"
    echo ""
    echo "Posibles causas:"
    echo ""
    echo "1. El servidor no se reinició después de los cambios"
    echo "   Solución:"
    echo "     cd CODE"
    echo "     docker-compose restart app"
    echo ""
    echo "2. Hay una ruta duplicada en public.py"
    echo "   Solución:"
    echo "     Revisa: CODE/src/app/routes/public.py"
    echo "     Busca: @router.get(\"/auth/login\")"
    echo "     Debe haber solo UNA definición"
    echo ""
    echo "3. Los cambios no se guardaron correctamente"
    echo "   Solución:"
    echo "     Verifica que los archivos modificados estén guardados"
    echo "     Reinicia el servidor"
    echo ""
    echo "Para más ayuda, revisa:"
    echo "  DOCS/fixes/INSTRUCCIONES_TEST_FIX.md"
    echo ""
fi

echo -e "${CYAN}========================================${NC}"
