#!/bin/bash
# ════════════════════════════════════════════════════════════════════════════
# Script de Limpieza para Deploy a Staging
# ════════════════════════════════════════════════════════════════════════════
# Elimina archivos innecesarios preservando lo crítico
# ════════════════════════════════════════════════════════════════════════════

# No salir en error si un archivo no existe
set +e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  🧹 LIMPIEZA DE PROYECTO PARA STAGING${NC}"
echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
echo ""

# Función para eliminar con confirmación
delete_item() {
    local item="$1"
    if [ -e "$item" ]; then
        echo -e "${YELLOW}  ✗ Eliminando:${NC} $item"
        rm -rf "$item"
    fi
}

# Contador
deleted_count=0

echo -e "${GREEN}📋 PRESERVANDO:${NC}"
echo "  ✓ DYNAMIA API/"
echo "  ✓ README.md"
echo "  ✓ CUFE/"
echo "  ✓ Scripts de testing y debug"
echo "  ✓ Archivos de BD local"
echo "  ✓ Archivos de configuración de desarrollo"
echo "  ✓ Claves SSH"
echo "  ✓ Archivos de entorno sensibles"
echo "  ✓ Todo lo necesario para staging"
echo ""

read -p "¿Continuar con la limpieza? [y/N]: " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}Operación cancelada${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}🗑️  ELIMINANDO ARCHIVOS INNECESARIOS...${NC}"
echo ""

# ════════════════════════════════════════════════════════════════════════════
# 1. DOCUMENTACIÓN (excepto README.md raíz)
# ════════════════════════════════════════════════════════════════════════════
echo -e "${CYAN}[1/6] Documentación...${NC}"

# Eliminar subcarpetas de DOCS pero preservar algunos archivos críticos si existen
if [ -d "DOCS" ]; then
    # Eliminar todo DOCS
    delete_item "DOCS"
    ((deleted_count++))
fi

# Eliminar documentación dentro de CODE (preservando CODE/docs si tiene info de API)
# Solo eliminar archivos .md específicos que son documentación de cambios
if [ -d "CODE" ]; then
    delete_item "CODE/ANUNCIO_RAPIDO_README.md"
    delete_item "CODE/CAMBIOS_CLIENTE_NUEVO.md"
    delete_item "CODE/CAMBIOS_PAPYRUS.md"
    delete_item "CODE/CAMBIOS_PERMISOS_PRODUCTOS.md"
    delete_item "CODE/DESPLEGAR_A_STAGING.md"
    delete_item "CODE/ESTRUCTURA_PROYECTO.md"
    delete_item "CODE/IMPLEMENTACION_COMPLETADA.txt"
    delete_item "CODE/IMPLEMENTACION_S3.md"
    delete_item "CODE/INICIO_RAPIDO.md"
    delete_item "CODE/INICIO_RAPIDO_ANUNCIO.md"
    delete_item "CODE/INSTRUCCIONES_LIMPIEZA.md"
    delete_item "CODE/INSTRUCCIONES_PRODUCTOS.md"
    delete_item "CODE/PLAN_LIMPIEZA_BD.md"
    delete_item "CODE/README_S3.md"
    delete_item "CODE/REPORTE_VERIFICACION_FINAL.md"
    delete_item "CODE/RESUMEN_DEPLOY_PRODUCTOS.md"
    delete_item "CODE/RESUMEN_FIX_IVA.md"
    delete_item "CODE/RESUMEN_IMPLEMENTACION.md"
    delete_item "CODE/RESUMEN_IMPLEMENTACION_S3.md"
    delete_item "CODE/RESUMEN_LIMPIEZA.md"
    delete_item "CODE/CUFES_EJEMPLO.txt"
    ((deleted_count+=18))
fi

delete_item "PLAN_LIMPIEZA_PROYECTO.md"
((deleted_count++))

# ════════════════════════════════════════════════════════════════════════════
# 2. ARCHIVOS ARCHIVADOS
# ════════════════════════════════════════════════════════════════════════════
echo -e "${CYAN}[2/6] Archivos archivados...${NC}"

delete_item "ARCHIVE"
((deleted_count++))

# ════════════════════════════════════════════════════════════════════════════
# 3. SCRIPTS DE LIMPIEZA Y MANTENIMIENTO MANUAL
# ════════════════════════════════════════════════════════════════════════════
echo -e "${CYAN}[3/6] Scripts de limpieza y mantenimiento...${NC}"

if [ -d "CODE" ]; then
    # Scripts de limpieza
    delete_item "CODE/limpiar_facturas.py"
    delete_item "CODE/limpiar_facturas_completo.py"
    delete_item "CODE/limpiar_facturas_docker.sh"
    delete_item "CODE/limpiar_facturas_simple.py"
    delete_item "CODE/limpiar_facturas_sql.sh"
    delete_item "CODE/limpiar_todo_facturas.py"
    
    # Scripts de eliminación
    delete_item "CODE/eliminar_facturas_problematicas.py"
    delete_item "CODE/eliminar_facturas_sin_pdf.py"
    
    # Scripts de corrección
    delete_item "CODE/corregir_fechas_futuras.py"
    delete_item "CODE/fix_fechas.py"
    
    # Scripts de reparación
    delete_item "CODE/reparar_pdfs_supplier_invoices.py"
    delete_item "CODE/recalcular_calidad_facturas.py"
    
    # Scripts de migración manual
    delete_item "CODE/migrar_pdfs_a_s3.py"
    delete_item "CODE/sync_products_initial.py"
    delete_item "CODE/apply_migration_manual.py"
    
    # Scripts de permisos
    delete_item "CODE/dar_permisos_admin.py"
    delete_item "CODE/src/cambiar_password_jveyes.py"
    delete_item "CODE/src/cambiar_password_simple.py"
    
    # Otros scripts de mantenimiento
    delete_item "CODE/add_extraction_quality_column.sql"
    
    ((deleted_count+=19))
fi

# ════════════════════════════════════════════════════════════════════════════
# 4. BACKUPS
# ════════════════════════════════════════════════════════════════════════════
echo -e "${CYAN}[4/6] Backups locales...${NC}"

delete_item "CODE/backups"
((deleted_count++))

# ════════════════════════════════════════════════════════════════════════════
# 5. ARCHIVOS TEMPORALES Y LOGS
# ════════════════════════════════════════════════════════════════════════════
echo -e "${CYAN}[5/6] Archivos temporales...${NC}"

delete_item "CODE/src/main.py.backup"
((deleted_count++))

# ════════════════════════════════════════════════════════════════════════════
# 6. SCRIPTS DE TESTING EN RAÍZ (solo algunos específicos)
# ════════════════════════════════════════════════════════════════════════════
echo -e "${CYAN}[6/6] Scripts de testing en raíz...${NC}"

if [ -d "scripts" ]; then
    delete_item "scripts/create_test_message.py"
    delete_item "scripts/create_simple_message.py"
    delete_item "scripts/delete_all_messages.py"
    delete_item "scripts/delete_all_messages.sh"
    delete_item "scripts/delete_all_messages.sql"
    delete_item "scripts/delete_messages_direct.py"
    delete_item "scripts/test_auth_messages.html"
    delete_item "scripts/README_DELETE_MESSAGES.md"
    ((deleted_count+=8))
fi

# ════════════════════════════════════════════════════════════════════════════
# RESUMEN
# ════════════════════════════════════════════════════════════════════════════
echo ""
echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ LIMPIEZA COMPLETADA${NC}"
echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}📊 Estadísticas:${NC}"
echo -e "  • Items eliminados: ${YELLOW}~${deleted_count}${NC} archivos/carpetas"
echo ""
echo -e "${GREEN}✓ PRESERVADO:${NC}"
echo "  • DYNAMIA API/ (documentación de API)"
echo "  • README.md (raíz)"
echo "  • CUFE/ (facturas de ejemplo)"
echo "  • CODE/test_*.py (scripts de testing)"
echo "  • CODE/check_*.py (scripts de verificación)"
echo "  • CODE/debug_*.py (scripts de debug)"
echo "  • CODE/verificar_*.py (scripts de verificación)"
echo "  • CODE/src/paquetex.db (BD local)"
echo "  • CODE/*.sql (scripts SQL)"
echo "  • docker-compose.dev.yml"
echo "  • .vscode/"
echo "  • CODE/LOCAL/"
echo "  • .ssh_keys/ (claves SSH)"
echo "  • .env* (archivos de entorno)"
echo "  • .deploy/ (sistema de deploy)"
echo "  • CODE/src/ (código fuente)"
echo "  • CODE/alembic/ (migraciones)"
echo "  • CODE/requirements.txt"
echo "  • CODE/Dockerfile"
echo "  • Y todo lo necesario para staging"
echo ""
echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}🚀 Proyecto listo para deploy a staging${NC}"
echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}Siguiente paso:${NC}"
echo -e "  ./deploy.sh --env staging --deploy"
echo ""
