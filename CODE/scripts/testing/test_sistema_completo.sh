#!/bin/bash
# Script de pruebas automatizadas para el sistema de preferencias

echo "=========================================="
echo "PRUEBAS AUTOMATIZADAS - Sistema Completo"
echo "=========================================="

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para imprimir resultados
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
    fi
}

# PRUEBA 1: Verificar que el backend está corriendo
echo ""
echo "PRUEBA 1: Backend está corriendo"
docker ps | grep paquetes-backend-1 > /dev/null
print_result $? "Backend container está activo"

# PRUEBA 2: Verificar que la BD está corriendo
echo ""
echo "PRUEBA 2: Base de datos está corriendo"
docker ps | grep paquetes-db-1 > /dev/null
print_result $? "Database container está activo"

# PRUEBA 3: Verificar tabla customer_preferences existe
echo ""
echo "PRUEBA 3: Tabla customer_preferences existe"
docker exec paquetes-db-1 psql -U postgres -d paquetes_db -c "\d customer_preferences" > /dev/null 2>&1
print_result $? "Tabla customer_preferences existe"

# PRUEBA 4: Verificar que hay clientes con preferencias
echo ""
echo "PRUEBA 4: Clientes tienen preferencias configuradas"
COUNT=$(docker exec paquetes-db-1 psql -U postgres -d paquetes_db -t -c "SELECT COUNT(*) FROM customer_preferences;")
if [ $COUNT -gt 0 ]; then
    print_result 0 "Hay $COUNT clientes con preferencias"
else
    print_result 1 "No hay clientes con preferencias"
fi

# PRUEBA 5: Verificar cliente de prueba
echo ""
echo "PRUEBA 5: Cliente de prueba existe"
docker exec paquetes-db-1 psql -U postgres -d paquetes_db -t -c "
SELECT 
    c.full_name,
    c.phone,
    CASE WHEN cp.id IS NOT NULL THEN 'CON PREFERENCIAS' ELSE 'SIN PREFERENCIAS' END as estado
FROM customers c
LEFT JOIN customer_preferences cp ON c.id = cp.customer_id
WHERE c.phone = '573002596319';
"

# PRUEBA 6: Verificar notificaciones bloqueadas
echo ""
echo "PRUEBA 6: Sistema de bloqueo funciona"
BLOCKED=$(docker exec paquetes-db-1 psql -U postgres -d paquetes_db -t -c "SELECT COUNT(*) FROM notifications WHERE status = 'blocked';")
if [ $BLOCKED -gt 0 ]; then
    print_result 0 "Hay $BLOCKED notificaciones bloqueadas (sistema funciona)"
    echo "Últimas 3 notificaciones bloqueadas:"
    docker exec paquetes-db-1 psql -U postgres -d paquetes_db -c "
    SELECT 
        notification_type,
        event_type,
        error_message,
        created_at
    FROM notifications
    WHERE status = 'blocked'
    ORDER BY created_at DESC
    LIMIT 3;
    "
else
    echo -e "${YELLOW}⚠️  No hay notificaciones bloqueadas (puede ser normal si no se ha probado)${NC}"
fi

# PRUEBA 7: Verificar logs recientes
echo ""
echo "PRUEBA 7: Logs del sistema (últimas 20 líneas con 'preferencias')"
docker logs --tail 100 paquetes-backend-1 2>&1 | grep -i "preferencias" | tail -20

# PRUEBA 8: Verificar endpoints públicos
echo ""
echo "PRUEBA 8: Endpoints públicos responden"

# /announce
curl -s -o /dev/null -w "%{http_code}" https://staging.jemavi.co/announce > /tmp/announce_status
ANNOUNCE_STATUS=$(cat /tmp/announce_status)
if [ "$ANNOUNCE_STATUS" = "200" ]; then
    print_result 0 "/announce responde 200"
else
    print_result 1 "/announce responde $ANNOUNCE_STATUS"
fi

# /customer/verify
curl -s -o /dev/null -w "%{http_code}" https://staging.jemavi.co/customer/verify > /tmp/verify_status
VERIFY_STATUS=$(cat /tmp/verify_status)
if [ "$VERIFY_STATUS" = "200" ]; then
    print_result 0 "/customer/verify responde 200"
else
    print_result 1 "/customer/verify responde $VERIFY_STATUS"
fi

# PRUEBA 9: Verificar archivos modificados
echo ""
echo "PRUEBA 9: Archivos modificados están presentes"
FILES=(
    "src/main.py"
    "src/app/services/sms_service.py"
    "src/app/services/email_service.py"
    "src/templates/announce/announce.html"
    "src/templates/customer_portal/dashboard.html"
    "src/templates/customers/manage.html"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        print_result 0 "$file existe"
    else
        print_result 1 "$file NO existe"
    fi
done

# RESUMEN
echo ""
echo "=========================================="
echo "RESUMEN DE PRUEBAS"
echo "=========================================="
echo "✅ = Prueba pasada"
echo "❌ = Prueba fallida"
echo "⚠️  = Advertencia"
echo ""
echo "Revisa los resultados arriba para ver el estado del sistema."
echo ""
echo "Para pruebas manuales, consulta: CODE/PRUEBAS_PRE_PRODUCCION.md"
echo "=========================================="
