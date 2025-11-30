# 📱 Instrucciones para Limpiar Caché en Móvil

**Fecha:** 2025-11-28  
**Problema:** El footer móvil antiguo sigue apareciendo debido al caché del navegador

## ✅ Cambios Realizados en el Servidor

1. ✅ Agregados meta tags anti-caché en `base.html`
2. ✅ Actualizado versionado de todos los scripts JS
3. ✅ Actualizado versionado de archivos CSS
4. ✅ Agregado comentario de versión en `mobile-footer.html`

## 📱 Cómo Limpiar el Caché en tu Celular

### Para Chrome en Android:
1. Abre Chrome
2. Toca los **3 puntos** (⋮) en la esquina superior derecha
3. Ve a **Configuración**
4. Toca **Privacidad y seguridad**
5. Toca **Borrar datos de navegación**
6. Selecciona **Imágenes y archivos en caché**
7. Toca **Borrar datos**

### Para Safari en iPhone:
1. Ve a **Ajustes** del iPhone
2. Desplázate hacia abajo y toca **Safari**
3. Desplázate hacia abajo y toca **Borrar historial y datos de sitios web**
4. Confirma tocando **Borrar historial y datos**

### Método Rápido (Recarga Forzada):
1. Abre la página en tu navegador móvil
2. **Mantén presionado** el botón de recargar (🔄)
3. Selecciona **"Recarga forzada"** o **"Recargar sin caché"**

### Método Alternativo (Modo Incógnito):
1. Abre una **ventana de incógnito/privada** en tu navegador
2. Visita la página
3. Verifica que el footer nuevo aparezca correctamente

## 🔍 Cómo Verificar que Funciona

Después de limpiar el caché, deberías ver:

### ✅ Footer Móvil Correcto (Sticky en la parte inferior):
```
┌─────────────────────────────────┐
│ Desarrollado por JEMAVI | © 2025│
├─────────────────────────────────┤
│  📢      🔍      ❓      🔐     │
│ Anunciar Buscar Ayuda  Ingresar │
└─────────────────────────────────┘
```

### ❌ Footer Antiguo (NO debería aparecer):
- Footer simple sin iconos
- Footer no sticky
- Footer con diseño diferente

## 🚀 Despliegue en el Servidor

Si tienes acceso al servidor, ejecuta:

```bash
# Opción 1: Usando el script
./force-cache-clear.sh

# Opción 2: Manual con Docker
docker-compose down
docker-compose up -d --build

# Opción 3: Manual con systemd
sudo systemctl restart paquetex
```

## 🔧 Verificación Técnica

Para verificar que el servidor está sirviendo la versión correcta:

1. Abre las **Herramientas de Desarrollador** en el navegador
2. Ve a la pestaña **Network** (Red)
3. Recarga la página
4. Busca el archivo `base.html` o cualquier `.js`
5. Verifica que tenga los parámetros de versión actualizados:
   - `form-validation.js?v=2025-11-28`
   - `auth-redirect.js?v=2.0.1`
   - `mobile-scroll-debug.js?v=1.1`

## 📝 Notas Importantes

- El footer móvil **solo aparece en dispositivos móviles** (<768px)
- El footer móvil **solo aparece para usuarios NO autenticados**
- Si estás autenticado, verás una navegación diferente
- El footer es **sticky** (fijo en la parte inferior)
- El body tiene **padding-bottom: 92px** para compensar el footer

## 🆘 Si Aún No Funciona

1. Verifica que estés en un dispositivo móvil o con el navegador en modo responsive (<768px)
2. Verifica que NO estés autenticado (cierra sesión si es necesario)
3. Intenta con otro navegador móvil (Chrome, Safari, Firefox)
4. Verifica que el servidor se haya reiniciado correctamente
5. Revisa los logs del servidor para errores

## 📞 Contacto

Si después de seguir todos estos pasos el problema persiste, contacta al equipo de desarrollo.
