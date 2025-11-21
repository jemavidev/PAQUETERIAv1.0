# 🔧 Solución: Sincronización de Templates en Producción

## 📋 Problema Identificado

Las vistas de términos y condiciones (`/terms` y `/privacy`) no se están sincronizando en el servidor de producción.

## 🔍 Diagnóstico

### Archivos Verificados

✅ **Templates existen en el código:**
- `CODE/src/templates/general/terms.html` ✅
- `CODE/src/templates/general/privacy.html` ✅

✅ **Rutas configuradas en `public.py`:**
```python
@router.get("/terms")
async def terms_page(request: Request):
    context = get_auth_context_from_request(request)
    return templates.TemplateResponse("general/terms.html", context)

@router.get("/privacy")
async def privacy_page(request: Request):
    context = get_auth_context_from_request(request)
    return templates.TemplateResponse("general/privacy.html", context)
```

✅ **Volumen configurado en `docker-compose.prod.yml`:**
```yaml
volumes:
  - ./CODE/src:/app/src
```

## 🎯 Causas Posibles

1. **Contenedor no reiniciado** después de crear los archivos
2. **Archivos no subidos al servidor** de producción
3. **Permisos incorrectos** en los archivos
4. **Caché de templates** no actualizado

## 🛠️ Soluciones

### Solución 1: Verificación Rápida (Local)

Ejecuta el script de verificación:

```bash
./verificar-templates.sh
```

Este script verifica:
- ✅ Archivos en el host
- ✅ Archivos en el contenedor
- ✅ Rutas configuradas
- ✅ PDFs disponibles
- ✅ Endpoints funcionando

### Solución 2: Sincronización Automática (Local)

Ejecuta el script de sincronización:

```bash
./sincronizar-templates.sh
```

Este script:
1. Verifica archivos en el host
2. Verifica que el contenedor esté corriendo
3. Reinicia el contenedor para forzar sincronización
4. Verifica que los archivos estén sincronizados
5. Prueba los endpoints
6. Muestra los logs

### Solución 3: Sincronización Manual en Servidor de Producción

Si estás en el servidor de producción, sigue estos pasos:

#### Paso 1: Verificar archivos en el servidor

```bash
# Conectarse al servidor
ssh usuario@servidor-produccion

# Ir al directorio del proyecto
cd /ruta/al/proyecto

# Verificar que los archivos existen
ls -lh CODE/src/templates/general/terms.html
ls -lh CODE/src/templates/general/privacy.html
```

#### Paso 2: Si los archivos NO existen, subirlos

```bash
# Desde tu máquina local, subir los archivos
scp CODE/src/templates/general/terms.html usuario@servidor:/ruta/al/proyecto/CODE/src/templates/general/
scp CODE/src/templates/general/privacy.html usuario@servidor:/ruta/al/proyecto/CODE/src/templates/general/

# O usar rsync para sincronizar todo el directorio
rsync -avz CODE/src/templates/general/ usuario@servidor:/ruta/al/proyecto/CODE/src/templates/general/
```

#### Paso 3: Verificar permisos

```bash
# En el servidor
chmod 644 CODE/src/templates/general/terms.html
chmod 644 CODE/src/templates/general/privacy.html
```

#### Paso 4: Reiniciar el contenedor

```bash
# En el servidor
docker compose -f docker-compose.prod.yml restart app

# O reiniciar todo el stack
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d
```

#### Paso 5: Verificar sincronización

```bash
# Verificar que los archivos están en el contenedor
docker exec paqueteria_v1_prod_app ls -lh /app/src/templates/general/terms.html
docker exec paqueteria_v1_prod_app ls -lh /app/src/templates/general/privacy.html

# Probar los endpoints
curl -I http://localhost:8000/terms
curl -I http://localhost:8000/privacy
```

### Solución 4: Reconstruir el Contenedor (Si nada funciona)

```bash
# En el servidor de producción
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml build --no-cache app
docker compose -f docker-compose.prod.yml up -d
```

## 📊 Checklist de Verificación

Usa este checklist para verificar que todo está funcionando:

### En el Host (Servidor)
- [ ] `terms.html` existe en `CODE/src/templates/general/`
- [ ] `privacy.html` existe en `CODE/src/templates/general/`
- [ ] Permisos correctos (644)
- [ ] Rutas configuradas en `public.py`

### En el Contenedor
- [ ] Contenedor está corriendo
- [ ] `terms.html` existe en `/app/src/templates/general/`
- [ ] `privacy.html` existe en `/app/src/templates/general/`
- [ ] Volumen montado correctamente

### Endpoints
- [ ] `/terms` responde con 200
- [ ] `/privacy` responde con 200
- [ ] `/help` muestra enlaces a términos y privacidad
- [ ] PDFs descargables funcionan

## 🚀 Comandos Útiles

### Ver logs del contenedor
```bash
docker logs -f paqueteria_v1_prod_app
```

### Ver logs de errores
```bash
docker logs paqueteria_v1_prod_app 2>&1 | grep -i error
```

### Entrar al contenedor
```bash
docker exec -it paqueteria_v1_prod_app bash
```

### Ver archivos dentro del contenedor
```bash
docker exec paqueteria_v1_prod_app find /app/src/templates/general -name "*.html"
```

### Probar endpoints desde el servidor
```bash
curl -v http://localhost:8000/terms
curl -v http://localhost:8000/privacy
```

## 🔄 Proceso de Despliegue Recomendado

Para evitar este problema en el futuro:

1. **Desarrollo Local:**
   ```bash
   # Crear/modificar templates
   # Probar localmente
   docker compose -f docker-compose.dev.yml up -d
   ```

2. **Commit y Push:**
   ```bash
   git add CODE/src/templates/general/
   git commit -m "feat: agregar templates de términos y privacidad"
   git push origin main
   ```

3. **Despliegue en Producción:**
   ```bash
   # En el servidor
   git pull origin main
   docker compose -f docker-compose.prod.yml restart app
   ```

4. **Verificación:**
   ```bash
   ./verificar-templates.sh
   ```

## 📝 Notas Importantes

### Sobre los Volúmenes

El `docker-compose.prod.yml` tiene configurado:
```yaml
volumes:
  - ./CODE/src:/app/src
```

Esto significa que:
- ✅ Los cambios en `CODE/src/` se reflejan inmediatamente en el contenedor
- ✅ No necesitas reconstruir la imagen para cambios en templates
- ⚠️ Pero SÍ necesitas reiniciar el contenedor si hay cambios en rutas Python

### Sobre el Caché de Templates

FastAPI/Jinja2 puede cachear templates. Para forzar recarga:
1. Reiniciar el contenedor
2. O configurar `auto_reload=True` en desarrollo

### Sobre los PDFs

Los PDFs deben estar en:
```
CODE/static/pdf/
├── TERMINOS_Y_CONDICIONES.pdf
└── POLITICAS_PRIVACIDAD.pdf
```

Y son accesibles en:
- `/static/pdf/TERMINOS_Y_CONDICIONES.pdf`
- `/static/pdf/POLITICAS_PRIVACIDAD.pdf`

## 🆘 Si Nada Funciona

Si después de todos estos pasos los templates no se sincronizan:

1. **Verificar logs completos:**
   ```bash
   docker logs paqueteria_v1_prod_app > logs.txt
   ```

2. **Verificar configuración de Docker:**
   ```bash
   docker inspect paqueteria_v1_prod_app | grep -A 20 "Mounts"
   ```

3. **Verificar espacio en disco:**
   ```bash
   df -h
   ```

4. **Contactar al equipo de DevOps** con:
   - Logs del contenedor
   - Salida de `docker inspect`
   - Salida de los scripts de verificación

## ✅ Resultado Esperado

Después de aplicar las soluciones, deberías poder:

1. Acceder a `https://tu-dominio.com/terms` ✅
2. Acceder a `https://tu-dominio.com/privacy` ✅
3. Ver los enlaces en `/help` ✅
4. Descargar los PDFs ✅

---

**Fecha de Creación:** 2025-01-XX  
**Versión:** 1.0  
**Estado:** ✅ Documentado  
**Autor:** Sistema Kiro
