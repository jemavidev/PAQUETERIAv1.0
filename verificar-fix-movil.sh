#!/bin/bash

echo "🔍 Verificando cambios aplicados para fix de DevTools móvil..."
echo ""

# Verificar validation-override.js
echo "1️⃣ Verificando validation-override.js..."
if grep -q "DEBUG_VALIDATION = false" CODE/src/static/js/validation-override.js; then
    echo "   ✅ DEBUG_VALIDATION = false"
else
    echo "   ❌ DEBUG_VALIDATION no encontrado"
fi

# Verificar mobile-scroll-debug.js
echo ""
echo "2️⃣ Verificando mobile-scroll-debug.js..."
if grep -q "ENABLE_MONITOR = false" CODE/src/static/js/mobile-scroll-debug.js; then
    echo "   ✅ ENABLE_MONITOR = false"
else
    echo "   ❌ ENABLE_MONITOR no encontrado"
fi

# Verificar main.js
echo ""
echo "3️⃣ Verificando main.js..."
if grep -q "DESHABILITADO" CODE/src/static/js/main.js; then
    echo "   ✅ Interceptor deshabilitado"
else
    echo "   ❌ Interceptor no deshabilitado"
fi

# Verificar packages.html
echo ""
echo "4️⃣ Verificando packages.html..."
if grep -q "ENABLE_VERBOSE_LOGS = false" CODE/src/templates/packages/packages.html; then
    echo "   ✅ ENABLE_VERBOSE_LOGS = false"
else
    echo "   ❌ ENABLE_VERBOSE_LOGS no encontrado"
fi

if grep -q "CACHE_DURATION = 5000" CODE/src/templates/packages/packages.html; then
    echo "   ✅ isMobileDevice() con caché"
else
    echo "   ❌ Caché no encontrado"
fi

echo ""
echo "✅ Verificación completada"
echo ""
echo "📋 PRÓXIMOS PASOS:"
echo "   1. Recarga la página: Ctrl+Shift+R"
echo "   2. Abre DevTools: F12"
echo "   3. Activa modo móvil: Ctrl+Shift+M"
echo "   4. Selecciona un dispositivo (iPhone, Android)"
echo "   5. La página NO debería bloquearse"
echo ""
