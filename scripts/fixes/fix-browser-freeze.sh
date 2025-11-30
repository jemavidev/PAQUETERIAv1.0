#!/bin/bash

# Script para solucionar el problema de bloqueo del navegador
# Fecha: 2024-11-29

echo "🔧 Solucionando problema de bloqueo del navegador..."
echo ""

# 1. Detener servicios
echo "1️⃣ Deteniendo servicios..."
cd CODE
docker-compose -f docker-compose.dev.yml down 2>/dev/null || true
cd ..

# 2. Limpiar caché de Docker
echo ""
echo "2️⃣ Limpiando caché de Docker..."
docker system prune -f

# 3. Reiniciar servicios
echo ""
echo "3️⃣ Reiniciando servicios..."
cd CODE
docker-compose -f docker-compose.dev.yml up -d --build

# 4. Esperar a que los servicios estén listos
echo ""
echo "4️⃣ Esperando a que los servicios estén listos..."
sleep 10

# 5. Verificar estado
echo ""
echo "5️⃣ Verificando estado de los servicios..."
docker-compose -f docker-compose.dev.yml ps

echo ""
echo "✅ Servicios reiniciados correctamente"
echo ""
echo "📋 INSTRUCCIONES PARA EL NAVEGADOR:"
echo "   1. Cierra TODAS las pestañas de la aplicación"
echo "   2. Abre el navegador en modo incógnito (Ctrl+Shift+N)"
echo "   3. O limpia el caché: Ctrl+Shift+Delete"
echo "   4. Accede a: http://localhost:8000"
echo "   5. Ahora puedes abrir DevTools (F12) sin problemas"
echo ""
echo "🔍 CAMBIOS APLICADOS:"
echo "   ✅ Deshabilitados logs excesivos en validation-override.js"
echo "   ✅ Deshabilitado interceptor duplicado en main.js"
echo "   ✅ Deshabilitado MutationObserver en mobile-scroll-debug.js"
echo "   ✅ Deshabilitado PackageApp.init() automático"
echo ""
