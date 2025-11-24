#!/bin/bash

echo "🔧 Creando tabla customer_preferences..."

# Ejecutar SQL en el contenedor de base de datos
docker-compose exec -T db psql -U postgres -d paquetex_db < crear_tabla_customer_preferences.sql

if [ $? -eq 0 ]; then
    echo "✅ Tabla creada exitosamente"
else
    echo "❌ Error al crear la tabla"
    echo ""
    echo "Intenta manualmente:"
    echo "docker-compose exec db psql -U postgres -d paquetex_db"
    echo "Luego copia y pega el contenido de crear_tabla_customer_preferences.sql"
fi
