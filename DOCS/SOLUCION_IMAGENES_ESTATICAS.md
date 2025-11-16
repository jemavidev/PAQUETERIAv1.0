# Solución: Imágenes no se visualizan en el servidor

## 🔍 Problema Identificado

Las imágenes y archivos estáticos no se visualizaban correctamente en el servidor de producción, aunque funcionaban perfectamente en localhost.

### Causa Raíz

El problema estaba en la configuración de volúmenes de Docker. Había una inconsistencia entre:

1. **La aplicación FastAPI** (`CODE/src/main.py`) que monta los archivos estáticos desde:
   ```python
   app.mount("/static", StaticFiles(directory="/app/src/static"), name="static")
   ```

2. **Los volúmenes de Docker** que estaban montando los archivos en una ubicación diferente:
   ```yaml
   # ❌ INCORRECTO - Montaba en /app/static en lugar de /app/src/static
   - ./CODE/src/static:/app/static:ro
   ```

Esto causaba que FastAPI buscara los archivos en `/app/src/static/` pero los volúmenes los montaban en `/app/static/`, resultando en errores 404.

## ✅ Solución Aplicada

### 1. Corrección de Docker Compose

Se eliminó el montaje redundante de archivos estáticos en ambos archivos:

**`docker-compose.prod.yml`:**
```yaml
volumes:
  - ./CODE/src:/app/src              # ✅ Monta todo el código fuente
  - uploads_data:/app/uploads
  - logs_data:/app/logs
  # ❌ ELIMINADO: - ./CODE/src/static:/app/static
```

**`docker-compose.lightsail.yml`:**
```yaml
volumes:
  - ./CODE/src:/app/src:ro           # ✅ Monta todo el código fuente (read-only)
  - uploads_data:/app/uploads
  - logs_data:/app/logs
  # ❌ ELIMINADO: - ./CODE/src/static:/app/static:ro
```

### 2. Mejora en Nginx

Se habilitaron logs temporales para debug en `CODE/nginx/nginx.lightsail.conf`:

```nginx
location /static/ {
    proxy_pass http://fastapi_backend;
    
    # Logs habilitados para debug
    access_log /var/log/nginx/static_access.log main;
    error_log /var/log/nginx/static_error.log warn;
    
    # Cache agresivo
    expires 7d;
    add_header Cache-Control "public, immutable";
}
```

## 🚀 Cómo Aplicar la Solución

### Opción 1: Script Automático (Recomendado)

Ejecuta el script de redespliegue que aplica todos los cambios:

```bash
./redeploy-with-static-fix.sh
```

Este script:
- ✅ Verifica que los archivos estáticos existan
- ✅ Detiene los contenedores actuales
- ✅ Reconstruye la imagen con la nueva configuración
- ✅ Inicia los contenedores
- ✅ Verifica que los archivos sean accesibles
- ✅ Muestra logs y estado final

### Opción 2: Manual

Si prefieres hacerlo manualmente:

```bash
# 1. Detener contenedores
docker compose -f docker-compose.lightsail.yml down

# 2. Reconstruir imagen
docker compose -f docker-compose.lightsail.yml build --no-cache app

# 3. Iniciar contenedores
docker compose -f docker-compose.lightsail.yml up -d

# 4. Verificar logs
docker logs paqueteria_app --tail 50

# 5. Probar acceso
curl -I http://localhost:8000/static/images/favicon.png
```

## 🔧 Scripts de Diagnóstico

### Script de Diagnóstico

Para verificar el estado actual sin hacer cambios:

```bash
./diagnose-static-files.sh
```

Este script muestra:
- Estructura de directorios en el contenedor
- Montajes de volúmenes activos
- Accesibilidad de archivos estáticos
- Logs recientes

### Script de Corrección Rápida

Para aplicar solo la corrección sin redesplegar todo:

```bash
./fix-static-files.sh
```

## 📋 Verificación Post-Despliegue

Después de aplicar la solución, verifica que todo funcione:

### 1. Verificar Archivos Estáticos

```bash
# Favicon
curl -I http://localhost:8000/static/images/favicon.png
# Debe retornar: HTTP/1.1 200 OK

# Logo
curl -I http://localhost:8000/static/images/logo.png
# Debe retornar: HTTP/1.1 200 OK

# CSS
curl -I http://localhost:8000/static/css/main.css
# Debe retornar: HTTP/1.1 200 OK
```

### 2. Verificar en el Navegador

1. Abre la aplicación en el navegador
2. Presiona F12 para abrir las herramientas de desarrollo
3. Ve a la pestaña "Network" o "Red"
4. Recarga la página (Ctrl+R o Cmd+R)
5. Verifica que todos los archivos estáticos se carguen con código 200

### 3. Verificar Estructura en el Contenedor

```bash
# Obtener el nombre del contenedor
CONTAINER=$(docker ps --filter "name=paqueteria_app" --format "{{.Names}}" | head -n 1)

# Verificar estructura
docker exec $CONTAINER ls -lh /app/src/static/images/
```

## 🐛 Troubleshooting

### Problema: Archivos aún no se ven

**Solución 1: Limpiar caché del navegador**
```
Ctrl+Shift+R (Windows/Linux)
Cmd+Shift+R (Mac)
```

**Solución 2: Verificar permisos**
```bash
# En el host
ls -lh CODE/src/static/images/

# Deben ser legibles (r--) para todos
```

**Solución 3: Verificar logs de Nginx**
```bash
# Si usas Nginx en el host
sudo tail -f /var/log/nginx/static_error.log
```

### Problema: Error 404 en archivos estáticos

**Verificar que el volumen esté montado correctamente:**
```bash
docker inspect paqueteria_app --format='{{range .Mounts}}{{.Source}} -> {{.Destination}}{{println}}{{end}}'
```

Debe mostrar:
```
.../CODE/src -> /app/src
```

### Problema: Error 500 al acceder a estáticos

**Verificar logs de la aplicación:**
```bash
docker logs paqueteria_app --tail 100
```

Busca errores relacionados con `StaticFiles` o permisos.

## 📊 Comparación Antes/Después

### ❌ Antes (Incorrecto)

```yaml
volumes:
  - ./CODE/src:/app/src
  - ./CODE/src/static:/app/static:ro  # ❌ Montaje redundante e incorrecto
```

**Resultado:** FastAPI busca en `/app/src/static/` pero los archivos están en `/app/static/`

### ✅ Después (Correcto)

```yaml
volumes:
  - ./CODE/src:/app/src:ro  # ✅ Un solo montaje que incluye todo
```

**Resultado:** FastAPI encuentra los archivos en `/app/src/static/` correctamente

## 🎯 Mejores Prácticas

1. **Mantén la estructura simple:** Un solo montaje del código fuente es suficiente
2. **Usa read-only en producción:** Agrega `:ro` para seguridad
3. **Verifica siempre después de cambios:** Usa los scripts de diagnóstico
4. **Documenta los cambios:** Mantén este documento actualizado

## 📝 Notas Adicionales

- Los archivos estáticos se sirven a través de FastAPI usando `StaticFiles`
- Nginx hace proxy de las peticiones `/static/` a FastAPI
- El cache de Nginx está configurado para 7 días en archivos estáticos
- Los uploads se manejan en un volumen separado (`/app/uploads`)

## 🔗 Archivos Relacionados

- `docker-compose.prod.yml` - Configuración de producción
- `docker-compose.lightsail.yml` - Configuración para AWS Lightsail
- `CODE/src/main.py` - Configuración de FastAPI
- `CODE/nginx/nginx.lightsail.conf` - Configuración de Nginx
- `redeploy-with-static-fix.sh` - Script de redespliegue
- `diagnose-static-files.sh` - Script de diagnóstico

## ✅ Checklist de Verificación

Después de aplicar la solución, verifica:

- [ ] Los contenedores están corriendo (`docker ps`)
- [ ] El health check responde 200 (`curl http://localhost:8000/health`)
- [ ] El favicon es accesible (`curl -I http://localhost:8000/static/images/favicon.png`)
- [ ] El logo es accesible (`curl -I http://localhost:8000/static/images/logo.png`)
- [ ] Los CSS son accesibles (`curl -I http://localhost:8000/static/css/main.css`)
- [ ] Las imágenes se ven en el navegador
- [ ] No hay errores 404 en la consola del navegador
- [ ] Los logs no muestran errores relacionados con archivos estáticos

---

**Fecha de creación:** 2025-01-24  
**Última actualización:** 2025-01-24  
**Estado:** ✅ Solucionado
