#!/bin/bash
# Script para reiniciar el servidor en staging

echo "🔄 Reiniciando servidor en staging..."
echo ""

# Verificar rutas antes de reiniciar
echo "1️⃣ Verificando configuración de rutas..."
docker-compose exec web python debug_routes.py

echo ""
echo "2️⃣ Reiniciando contenedor web..."
docker-compose restart web

echo ""
echo "3️⃣ Esperando que el servidor esté listo..."
sleep 5

echo ""
echo "4️⃣ Verificando que el servidor esté corriendo..."
docker-compose ps web

echo ""
echo "5️⃣ Verificando logs recientes..."
docker-compose logs --tail=20 web

echo ""
echo "✅ Servidor reiniciado"
echo ""
echo "🧪 Prueba ahora:"
echo "   https://staging.jemavi.co/customer-portal"
echo ""
echo "📋 Ver logs en tiempo real:"
echo "   docker-compose logs -f web"
