#!/bin/bash

echo "=========================================="
echo "CREAR TABLA CUSTOMER_PREFERENCES"
echo "=========================================="
echo ""

# Verificar si docker compose está corriendo
if ! docker compose ps | grep -q "web.*Up"; then
    echo "⚠️  El servidor no está corriendo."
    echo "Por favor, inicia el servidor con: docker compose up -d"
    exit 1
fi

echo "✅ Servidor corriendo"
echo ""
echo "Creando tabla customer_preferences..."
echo ""

# Ejecutar el script Python para crear la tabla
docker compose exec web python /app/crear_tabla_customer_preferences.py

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ TABLA CREADA EXITOSAMENTE"
    echo "=========================================="
    echo ""
    echo "Próximos pasos:"
    echo "1. Reinicia el servidor: docker compose restart web"
    echo "2. Ve a: http://localhost:8000/customers/manage"
    echo "3. Haz clic en el botón morado (🔔) de cualquier cliente"
    echo ""
else
    echo ""
    echo "=========================================="
    echo "❌ ERROR AL CREAR LA TABLA"
    echo "=========================================="
    echo ""
    echo "Verifica los logs con: docker compose logs web"
    exit 1
fi
