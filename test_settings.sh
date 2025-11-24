#!/bin/bash
# Script para probar la ruta /settings

echo "🧪 Probando ruta /settings..."
echo ""

# 1. Primero hacer login para obtener cookies
echo "1️⃣ Haciendo login..."
LOGIN_RESPONSE=$(curl -s -c cookies.txt -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"jesus","password":"tu_password_aqui"}')

echo "Respuesta del login:"
echo "$LOGIN_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$LOGIN_RESPONSE"
echo ""

# 2. Verificar si hay cookies
if [ -f cookies.txt ]; then
    echo "2️⃣ Cookies guardadas:"
    cat cookies.txt | grep -v "^#"
    echo ""
fi

# 3. Intentar acceder a /settings con las cookies
echo "3️⃣ Accediendo a /settings con autenticación..."
SETTINGS_RESPONSE=$(curl -s -b cookies.txt -L http://localhost:8000/settings)

# Verificar si la respuesta contiene HTML válido
if echo "$SETTINGS_RESPONSE" | grep -q "Configuración"; then
    echo "✅ Página /settings cargada correctamente"
    echo "Título encontrado: $(echo "$SETTINGS_RESPONSE" | grep -o '<title>[^<]*</title>' | sed 's/<[^>]*>//g')"
else
    echo "❌ Error al cargar /settings"
    echo "Primeras líneas de la respuesta:"
    echo "$SETTINGS_RESPONSE" | head -20
fi

# Limpiar
rm -f cookies.txt

echo ""
echo "✅ Prueba completada"
