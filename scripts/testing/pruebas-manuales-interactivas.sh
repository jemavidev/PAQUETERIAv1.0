#!/bin/bash

# 🧪 Guía Interactiva de Pruebas Manuales - Staging
# Fecha: 2024-11-29

set -e

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Función para esperar input del usuario
wait_for_user() {
    echo ""
    echo -e "${CYAN}Presiona ENTER cuando hayas completado este paso...${NC}"
    read -r
}

# Función para preguntar resultado
ask_result() {
    echo ""
    echo -e "${YELLOW}¿La prueba pasó correctamente? (s/n):${NC} "
    read -r response
    if [[ "$response" =~ ^[Ss]$ ]]; then
        echo -e "${GREEN}✅ PASS${NC}"
        return 0
    else
        echo -e "${RED}❌ FAIL${NC}"
        echo -e "${YELLOW}Describe el problema:${NC} "
        read -r problem
        echo "  Problema reportado: $problem"
        return 1
    fi
}

# Contadores
TOTAL=0
PASSED=0
FAILED=0
PROBLEMS=()

clear
echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  🧪 PRUEBAS MANUALES INTERACTIVAS - STAGING          ║${NC}"
echo -e "${BLUE}║  Fecha: 2024-11-29                                    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Esta guía te llevará paso a paso por las pruebas críticas."
echo "Sigue las instrucciones y reporta los resultados."
echo ""
wait_for_user

# ============================================
# PRUEBA 1: DevTools en Desktop
# ============================================
clear
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}PRUEBA 1/5: DevTools NO se Bloquea (Desktop)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo ""
echo "📋 Pasos a seguir:"
echo ""
echo "1. Abre staging en tu navegador:"
echo -e "   ${CYAN}https://staging.jemavi.co${NC}"
echo ""
echo "2. Inicia sesión si es necesario"
echo ""
echo "3. Ve a la página de paquetes:"
echo -e "   ${CYAN}https://staging.jemavi.co/packages${NC}"
echo ""
echo "4. Presiona F12 para abrir DevTools"
echo ""
echo "5. Ve a la pestaña 'Console'"
echo ""
echo "✅ Resultado esperado:"
echo "   - El navegador NO se bloquea"
echo "   - La consola muestra solo logs esenciales:"
echo "     • 🔧 Configuración PAQUETES EL CLUB v4.0 cargada"
echo "     • 🔐 AuthRedirectHandler v2.0 inicializado"
echo "     • Ruta protegida detectada: /packages"
echo ""
echo "❌ NO deberías ver:"
echo "   - Miles de logs por segundo"
echo "   - Logs de 'Detección de dispositivo'"
echo "   - Logs de 'Clasificando paquete'"
echo ""
wait_for_user

TOTAL=$((TOTAL + 1))
if ask_result; then
    PASSED=$((PASSED + 1))
else
    FAILED=$((FAILED + 1))
    PROBLEMS+=("PRUEBA 1: DevTools Desktop - $problem")
fi

# ============================================
# PRUEBA 2: DevTools en Modo Móvil
# ============================================
clear
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}PRUEBA 2/5: DevTools NO se Bloquea (Modo Móvil)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo ""
echo "📋 Pasos a seguir:"
echo ""
echo "1. Con DevTools abierto (F12)"
echo ""
echo "2. Presiona Ctrl+Shift+M para activar modo móvil"
echo "   (o haz clic en el ícono de dispositivo móvil)"
echo ""
echo "3. Selecciona un dispositivo del dropdown:"
echo "   - iPhone 12 Pro"
echo "   - Samsung Galaxy S20"
echo "   - iPad Air"
echo ""
echo "4. Cambia entre varios dispositivos"
echo ""
echo "5. Observa la consola"
echo ""
echo "✅ Resultado esperado:"
echo "   - El navegador NO se bloquea"
echo "   - NO hay logs excesivos"
echo "   - La página responde normalmente"
echo "   - Puedes cambiar de dispositivo sin problemas"
echo ""
echo "❌ NO debería pasar:"
echo "   - Navegador se congela"
echo "   - Miles de logs aparecen"
echo "   - La página deja de responder"
echo ""
wait_for_user

TOTAL=$((TOTAL + 1))
if ask_result; then
    PASSED=$((PASSED + 1))
else
    FAILED=$((FAILED + 1))
    PROBLEMS+=("PRUEBA 2: DevTools Móvil - $problem")
fi

# ============================================
# PRUEBA 3: Mensaje de WhatsApp con Link
# ============================================
clear
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}PRUEBA 3/5: Mensaje de WhatsApp con Link de Búsqueda${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo ""
echo "📋 Pasos a seguir:"
echo ""
echo "1. En la página /packages, busca un paquete"
echo "   (cualquier paquete con tracking number)"
echo ""
echo "2. Localiza el botón verde de WhatsApp en la columna 'Acciones'"
echo ""
echo "3. Haz clic en el botón de WhatsApp"
echo ""
echo "4. Se abrirá WhatsApp Web o la app"
echo ""
echo "5. Verifica el mensaje pre-llenado"
echo ""
echo "✅ Resultado esperado:"
echo "   El mensaje debe tener este formato:"
echo ""
echo -e "   ${CYAN}Hola [NOMBRE DEL CLIENTE], te contacto por tu paquete.${NC}"
echo -e "   ${CYAN}Puedes consultar el estado aquí:${NC}"
echo -e "   ${CYAN}https://staging.jemavi.co/search?auto_search=[TRACKING]${NC}"
echo ""
echo "   Ejemplo real:"
echo -e "   ${GREEN}Hola DINA MARCELA, te contacto por tu paquete.${NC}"
echo -e "   ${GREEN}Puedes consultar el estado aquí:${NC}"
echo -e "   ${GREEN}https://staging.jemavi.co/search?auto_search=8ZWG${NC}"
echo ""
echo "❌ NO debería ser:"
echo "   - Solo: 'Hola [NOMBRE], te contacto por tu paquete' (sin link)"
echo "   - Link roto o mal formado"
echo ""
wait_for_user

TOTAL=$((TOTAL + 1))
if ask_result; then
    PASSED=$((PASSED + 1))
else
    FAILED=$((FAILED + 1))
    PROBLEMS+=("PRUEBA 3: WhatsApp Link - $problem")
fi

# ============================================
# PRUEBA 4: Link de Búsqueda Funciona
# ============================================
clear
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}PRUEBA 4/5: Link de Búsqueda Funciona (auto_search)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo ""
echo "📋 Pasos a seguir:"
echo ""
echo "1. Copia el link del mensaje de WhatsApp"
echo "   (el que dice: https://staging.jemavi.co/search?auto_search=...)"
echo ""
echo "2. Abre una nueva pestaña en el navegador"
echo ""
echo "3. Pega el link y presiona ENTER"
echo ""
echo "4. Observa qué sucede"
echo ""
echo "✅ Resultado esperado:"
echo "   - Se abre la página /search"
echo "   - La búsqueda se ejecuta AUTOMÁTICAMENTE"
echo "   - Se muestra el resultado del paquete"
echo "   - El tracking number aparece en el campo de búsqueda"
echo "   - Se muestra la información del paquete (estado, cliente, etc.)"
echo ""
echo "❌ NO debería pasar:"
echo "   - La búsqueda NO se ejecuta automáticamente"
echo "   - Muestra 'Paquete no encontrado'"
echo "   - Error 404 o página en blanco"
echo ""
wait_for_user

TOTAL=$((TOTAL + 1))
if ask_result; then
    PASSED=$((PASSED + 1))
else
    FAILED=$((FAILED + 1))
    PROBLEMS+=("PRUEBA 4: Auto Search - $problem")
fi

# ============================================
# PRUEBA 5: WhatsApp desde Modales
# ============================================
clear
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}PRUEBA 5/5: WhatsApp desde Modales (Recepción/Entrega)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo ""
echo "📋 Pasos a seguir:"
echo ""
echo "PARTE A - Modal de Recepción:"
echo "1. En /packages, haz clic en 'Recibir' en un paquete"
echo "2. Se abre el modal de recepción"
echo "3. Busca el teléfono del cliente (debería ser un link)"
echo "4. Haz clic en el link del teléfono"
echo "5. Verifica el mensaje de WhatsApp"
echo ""
echo "PARTE B - Modal de Entrega:"
echo "1. En /packages, haz clic en 'Entregar' en un paquete"
echo "2. Se abre el modal de entrega"
echo "3. Busca el teléfono del cliente"
echo "4. Haz clic en el link del teléfono"
echo "5. Verifica el mensaje de WhatsApp"
echo ""
echo "✅ Resultado esperado (ambos casos):"
echo "   - El mensaje incluye el link de búsqueda"
echo "   - El formato es el mismo que en la tabla"
echo "   - El link funciona correctamente"
echo ""
wait_for_user

TOTAL=$((TOTAL + 1))
if ask_result; then
    PASSED=$((PASSED + 1))
else
    FAILED=$((FAILED + 1))
    PROBLEMS+=("PRUEBA 5: WhatsApp Modales - $problem")
fi

# ============================================
# RESUMEN FINAL
# ============================================
clear
echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  📊 RESUMEN DE PRUEBAS MANUALES                       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Total de pruebas: $TOTAL"
echo -e "${GREEN}Pasadas: $PASSED${NC}"
echo -e "${RED}Fallidas: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  ✅ ¡TODAS LAS PRUEBAS PASARON!                       ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "🎉 Los últimos commits de staging están funcionando correctamente."
    echo ""
    echo "📋 Resumen de lo verificado:"
    echo "  ✅ DevTools NO se bloquea (desktop y móvil)"
    echo "  ✅ Mensajes de WhatsApp incluyen link de búsqueda"
    echo "  ✅ Link de búsqueda funciona con auto_search"
    echo "  ✅ WhatsApp funciona desde modales"
    echo ""
    echo "🚀 Próximos pasos sugeridos:"
    echo "  1. Merge staging → main (si todo está OK)"
    echo "  2. Deploy a producción"
    echo "  3. Monitorear logs en producción"
    echo ""
else
    echo -e "${RED}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  ❌ ALGUNAS PRUEBAS FALLARON                          ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "🔍 Problemas encontrados:"
    echo ""
    for i in "${!PROBLEMS[@]}"; do
        echo "  $((i+1)). ${PROBLEMS[$i]}"
    done
    echo ""
    echo "🛠️  Acciones recomendadas:"
    echo "  1. Revisa los problemas reportados arriba"
    echo "  2. Verifica los archivos modificados"
    echo "  3. Revisa la consola del navegador por errores"
    echo "  4. Consulta la documentación:"
    echo "     - FIX_BROWSER_FREEZE_2024-11-29.md"
    echo "     - SOLUCION_DEVTOOLS_MOVIL.md"
    echo "     - WHATSAPP_LINK_ACTUALIZADO.md"
    echo ""
fi

# Guardar reporte
REPORT_FILE="reporte-pruebas-manuales-$(date +%Y%m%d-%H%M%S).txt"
{
    echo "REPORTE DE PRUEBAS MANUALES - STAGING"
    echo "======================================"
    echo "Fecha: $(date)"
    echo "Rama: staging"
    echo ""
    echo "RESULTADOS:"
    echo "Total: $TOTAL"
    echo "Pasadas: $PASSED"
    echo "Fallidas: $FAILED"
    echo ""
    if [ $FAILED -gt 0 ]; then
        echo "PROBLEMAS ENCONTRADOS:"
        for problem in "${PROBLEMS[@]}"; do
            echo "  - $problem"
        done
    fi
} > "$REPORT_FILE"

echo ""
echo "📄 Reporte guardado en: $REPORT_FILE"
echo ""

if [ $FAILED -eq 0 ]; then
    exit 0
else
    exit 1
fi
