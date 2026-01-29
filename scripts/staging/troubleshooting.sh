#!/bin/bash
# Script de troubleshooting para problemas comunes

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║   🔧 TROUBLESHOOTING - SOLUCIÓN DE PROBLEMAS                 ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

PS3="Selecciona el problema: "
options=(
    "El script sync_manual.sh no existe"
    "Error: pg_dump: command not found"
    "Error: connection refused"
    "Error: authentication failed"
    "El contenedor no está corriendo"
    "El botón no aparece en el navegador"
    "El botón no hace nada"
    "Ver logs de la aplicación"
    "Reinstalar todo desde cero"
    "Salir"
)

select opt in "${options[@]}"
do
    case $opt in
        "El script sync_manual.sh no existe")
            echo ""
            echo "📝 Solución:"
            echo "─────────────────────────────────────────────────────────────────"
            echo "Crear el script manualmente:"
            echo ""
            cat << 'EOF'
cat > ~/sync_manual.sh << 'SCRIPT'
#!/bin/bash
HOST="ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com"
USER="jveyes"
PASS='a?HC!2.*1#?[==:|289qAI=)#V4kDzl$'
export PGPASSWORD="$PASS"
echo "🔄 Sincronizando..."
pg_dump -h "$HOST" -U "$USER" -d paqueteria_v4 -F c -f /tmp/backup.dump --no-owner --no-acl
echo "✅ Exportado"
pg_restore -h "$HOST" -U "$USER" -d paqueteria_staging /tmp/backup.dump --clean --if-exists --no-owner --no-acl 2>&1 | grep -v "^WARNING" || true
echo "✅ Restaurado"
echo "✅ Completado"
rm -f /tmp/backup.dump
SCRIPT

chmod +x ~/sync_manual.sh
EOF
            echo ""
            echo "Luego probar: ~/sync_manual.sh"
            echo ""
            break
            ;;
        "Error: pg_dump: command not found")
            echo ""
            echo "📝 Solución:"
            echo "─────────────────────────────────────────────────────────────────"
            echo "Instalar PostgreSQL client:"
            echo ""
            echo "sudo dnf install -y postgresql"
            echo ""
            echo "Verificar:"
            echo "pg_dump --version"
            echo ""
            break
            ;;
        "Error: connection refused")
            echo ""
            echo "📝 Solución:"
            echo "─────────────────────────────────────────────────────────────────"
            echo "1. Verificar conectividad:"
            echo ""
            echo "ping ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com"
            echo ""
            echo "2. Verificar que el servidor RDS está corriendo en AWS Console"
            echo ""
            echo "3. Verificar security groups en AWS (debe permitir conexiones desde staging)"
            echo ""
            break
            ;;
        "Error: authentication failed")
            echo ""
            echo "📝 Solución:"
            echo "─────────────────────────────────────────────────────────────────"
            echo "Verificar credenciales en .env.staging:"
            echo ""
            echo "cat ~/paqueteria-staging/.env.staging | grep POSTGRES"
            echo ""
            echo "Probar conexión manualmente:"
            echo ""
            echo "export PGPASSWORD='a?HC!2.*1#?[==:|289qAI=)#V4kDzl\$'"
            echo "psql -h ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com \\"
            echo "     -U jveyes -d paqueteria_v4 -c 'SELECT version();'"
            echo ""
            break
            ;;
        "El contenedor no está corriendo")
            echo ""
            echo "📝 Solución:"
            echo "─────────────────────────────────────────────────────────────────"
            echo "1. Ver estado:"
            echo "docker ps -a | grep staging"
            echo ""
            echo "2. Ver logs:"
            echo "docker logs paqueteria_staging_app"
            echo ""
            echo "3. Reiniciar:"
            echo "cd ~/paqueteria-staging"
            echo "docker-compose -f docker-compose.staging.yml restart app"
            echo ""
            echo "4. Si no inicia, reconstruir:"
            echo "docker-compose -f docker-compose.staging.yml up -d --build app"
            echo ""
            break
            ;;
        "El botón no aparece en el navegador")
            echo ""
            echo "📝 Solución:"
            echo "─────────────────────────────────────────────────────────────────"
            echo "1. Verificar que estás en staging (no producción)"
            echo ""
            echo "2. Refrescar con Ctrl+Shift+R (limpiar caché)"
            echo ""
            echo "3. Abrir consola del navegador (F12) y buscar errores"
            echo ""
            echo "4. Verificar que el badge 'Staging' aparece en el header"
            echo ""
            break
            ;;
        "El botón no hace nada")
            echo ""
            echo "📝 Solución:"
            echo "─────────────────────────────────────────────────────────────────"
            echo "1. Ver logs de la aplicación:"
            echo "docker logs -f paqueteria_staging_app"
            echo ""
            echo "2. Verificar que el script existe:"
            echo "ls -la ~/sync_manual.sh"
            echo ""
            echo "3. Probar el script manualmente:"
            echo "~/sync_manual.sh"
            echo ""
            echo "4. Si el script funciona pero el botón no, reiniciar app:"
            echo "cd ~/paqueteria-staging"
            echo "docker-compose -f docker-compose.staging.yml restart app"
            echo ""
            break
            ;;
        "Ver logs de la aplicación")
            echo ""
            echo "📝 Comandos útiles:"
            echo "─────────────────────────────────────────────────────────────────"
            echo "Ver logs en tiempo real:"
            echo "docker logs -f paqueteria_staging_app"
            echo ""
            echo "Ver últimas 100 líneas:"
            echo "docker logs --tail 100 paqueteria_staging_app"
            echo ""
            echo "Buscar errores:"
            echo "docker logs paqueteria_staging_app 2>&1 | grep -i error"
            echo ""
            break
            ;;
        "Reinstalar todo desde cero")
            echo ""
            echo "📝 Reinstalación completa:"
            echo "─────────────────────────────────────────────────────────────────"
            echo "1. Limpiar archivos anteriores:"
            echo "rm -f ~/sync_manual.sh"
            echo ""
            echo "2. Ejecutar instalador:"
            echo "./instalar_sync_completo.sh"
            echo ""
            echo "3. Verificar instalación:"
            echo "./verificar_instalacion.sh"
            echo ""
            break
            ;;
        "Salir")
            echo ""
            echo "👋 ¡Hasta luego!"
            echo ""
            break
            ;;
        *) 
            echo "Opción inválida"
            ;;
    esac
done
