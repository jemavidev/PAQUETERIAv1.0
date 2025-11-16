#!/bin/bash
# Menú interactivo para la corrección de imágenes estáticas

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

clear

echo -e "${CYAN}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   CORRECCIÓN: IMÁGENES NO SE VISUALIZAN EN EL SERVIDOR       ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo ""
echo -e "${YELLOW}Problema:${NC} Las imágenes no se visualizan en el servidor"
echo -e "${GREEN}Solución:${NC} Corrección de configuración de volúmenes Docker"
echo ""

# Función para mostrar el menú
show_menu() {
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}MENÚ PRINCIPAL${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "  1) 📋 Ver resumen del problema"
    echo "  2) 🔍 Ejecutar diagnóstico (sin cambios)"
    echo "  3) 🧪 Probar corrección localmente"
    echo "  4) 🚀 Desplegar corrección al servidor"
    echo "  5) 📚 Ver documentación completa"
    echo "  6) ❓ Ayuda y troubleshooting"
    echo "  0) ❌ Salir"
    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
}

# Función para pausar
pause() {
    echo ""
    read -p "Presiona Enter para continuar..."
}

# Función para mostrar el resumen
show_summary() {
    clear
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}RESUMEN DEL PROBLEMA${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    cat RESUMEN_CORRECCION.txt
    pause
}

# Función para ejecutar diagnóstico
run_diagnostic() {
    clear
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}EJECUTANDO DIAGNÓSTICO${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    
    if [ ! -f "CODE/scripts/deployment/diagnose-static-files.sh" ]; then
        echo -e "${RED}❌ Error: No se encuentra diagnose-static-files.sh${NC}"
        pause
        return
    fi
    
    chmod +x CODE/scripts/deployment/diagnose-static-files.sh
    ./CODE/scripts/deployment/diagnose-static-files.sh
    pause
}

# Función para probar localmente
test_locally() {
    clear
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}PRUEBA LOCAL${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    
    if [ ! -f "CODE/scripts/deployment/redeploy-with-static-fix.sh" ]; then
        echo -e "${RED}❌ Error: No se encuentra redeploy-with-static-fix.sh${NC}"
        pause
        return
    fi
    
    echo -e "${YELLOW}⚠️  ADVERTENCIA:${NC} Esto detendrá y reconstruirá los contenedores locales"
    echo ""
    read -p "¿Deseas continuar? (s/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        chmod +x CODE/scripts/deployment/redeploy-with-static-fix.sh
        ./CODE/scripts/deployment/redeploy-with-static-fix.sh
    else
        echo "Operación cancelada"
    fi
    pause
}

# Función para desplegar al servidor
deploy_to_server() {
    clear
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}DESPLIEGUE AL SERVIDOR${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    
    if [ ! -f "CODE/scripts/deployment/deploy-static-fix-to-server.sh" ]; then
        echo -e "${RED}❌ Error: No se encuentra deploy-static-fix-to-server.sh${NC}"
        pause
        return
    fi
    
    echo -e "${YELLOW}⚠️  ADVERTENCIA:${NC} Esto desplegará los cambios al servidor de producción"
    echo ""
    echo "Asegúrate de tener:"
    echo "  ✓ Acceso SSH al servidor"
    echo "  ✓ La IP del servidor"
    echo "  ✓ Credenciales correctas"
    echo ""
    read -p "¿Deseas continuar? (s/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        chmod +x CODE/scripts/deployment/deploy-static-fix-to-server.sh
        ./CODE/scripts/deployment/deploy-static-fix-to-server.sh
    else
        echo "Operación cancelada"
    fi
    pause
}

# Función para mostrar documentación
show_documentation() {
    clear
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}DOCUMENTACIÓN${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "Documentos disponibles:"
    echo ""
    echo "  1) DOCS/documentacion/CORRECCION_IMAGENES_ESTATICAS.md (Guía rápida)"
    echo "  2) DOCS/SOLUCION_IMAGENES_ESTATICAS.md (Documentación completa)"
    echo "  3) RESUMEN_CORRECCION.txt (Resumen ejecutivo)"
    echo "  0) Volver al menú principal"
    echo ""
    read -p "Selecciona un documento (0-3): " doc_choice
    
    case $doc_choice in
        1)
            clear
            cat DOCS/documentacion/CORRECCION_IMAGENES_ESTATICAS.md | less
            ;;
        2)
            clear
            cat DOCS/SOLUCION_IMAGENES_ESTATICAS.md | less
            ;;
        3)
            clear
            cat RESUMEN_CORRECCION.txt | less
            ;;
        0)
            return
            ;;
        *)
            echo -e "${RED}Opción inválida${NC}"
            ;;
    esac
    pause
}

# Función para mostrar ayuda
show_help() {
    clear
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}AYUDA Y TROUBLESHOOTING${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${YELLOW}Problema: Las imágenes aún no se ven después de aplicar la corrección${NC}"
    echo ""
    echo "Soluciones:"
    echo "  1. Limpiar caché del navegador (Ctrl+Shift+R)"
    echo "  2. Verificar logs: docker logs paqueteria_app --tail 100"
    echo "  3. Verificar estructura: docker exec paqueteria_app ls -lh /app/src/static/"
    echo ""
    echo -e "${YELLOW}Problema: Error de conexión SSH al servidor${NC}"
    echo ""
    echo "Soluciones:"
    echo "  1. Verificar la IP del servidor"
    echo "  2. Verificar credenciales SSH"
    echo "  3. Verificar que el puerto SSH esté abierto (default: 22)"
    echo "  4. Probar conexión: ssh usuario@servidor"
    echo ""
    echo -e "${YELLOW}Problema: Contenedores no inician después del cambio${NC}"
    echo ""
    echo "Soluciones:"
    echo "  1. Ver logs: docker compose -f docker-compose.lightsail.yml logs"
    echo "  2. Verificar sintaxis: docker compose -f docker-compose.lightsail.yml config"
    echo "  3. Reconstruir: docker compose -f docker-compose.lightsail.yml build --no-cache"
    echo ""
    echo -e "${YELLOW}Comandos útiles:${NC}"
    echo ""
    echo "  Ver estado:        docker compose -f docker-compose.lightsail.yml ps"
    echo "  Ver logs:          docker logs -f paqueteria_app"
    echo "  Reiniciar:         docker compose -f docker-compose.lightsail.yml restart app"
    echo "  Detener todo:      docker compose -f docker-compose.lightsail.yml down"
    echo ""
    echo -e "${YELLOW}Verificación:${NC}"
    echo ""
    echo "  Health check:      curl http://localhost:8000/health"
    echo "  Favicon:           curl -I http://localhost:8000/static/images/favicon.png"
    echo "  Logo:              curl -I http://localhost:8000/static/images/logo.png"
    echo ""
    pause
}

# Bucle principal
while true; do
    clear
    echo -e "${CYAN}"
    cat << "EOF"
╔═══════════════════════════════════════════════════════════════╗
║   CORRECCIÓN: IMÁGENES NO SE VISUALIZAN EN EL SERVIDOR       ║
╚═══════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
    
    show_menu
    read -p "Selecciona una opción (0-6): " choice
    
    case $choice in
        1)
            show_summary
            ;;
        2)
            run_diagnostic
            ;;
        3)
            test_locally
            ;;
        4)
            deploy_to_server
            ;;
        5)
            show_documentation
            ;;
        6)
            show_help
            ;;
        0)
            clear
            echo -e "${GREEN}¡Hasta luego!${NC}"
            echo ""
            exit 0
            ;;
        *)
            echo -e "${RED}Opción inválida. Por favor, selecciona una opción válida.${NC}"
            sleep 2
            ;;
    esac
done
