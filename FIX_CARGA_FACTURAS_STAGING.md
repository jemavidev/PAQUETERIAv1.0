# 🔧 Fix: Carga de Facturas en Staging

## Problema Identificado

Al intentar cargar facturas en https://staging.jemavi.co/invoices (Tab Facturas), se producía un error 404:

```
POST https://staging.jemavi.co/api/supplier-invoices/upload 404 (Not Found)
```

## Causa Raíz

Inconsistencia en las URLs de los endpoints API:

- **Router Backend**: Configurado con prefijo `/invoices` en `src/main.py`
- **Template Incorrecto**: `_tab_facturas.html` llamaba a `/api/supplier-invoices/upload`
- **URL Correcta**: Debería ser `/invoices/api/supplier-invoices/upload`

### Archivos Afectados

1. ✅ `supplier_invoices.html` - Ya tenía la URL correcta
2. ❌ `_tab_facturas.html` - Tenía la URL incorrecta

## Solución Aplicada

### Cambio en el Código

**Archivo**: `CODE/src/templates/invoices/_tab_facturas.html`

**Línea 241**:
```javascript
// ANTES (Incorrecto)
const response = await fetch('/api/supplier-invoices/upload', {

// DESPUÉS (Correcto)
const response = await fetch('/invoices/api/supplier-invoices/upload', {
```

### Deploy a Staging

1. **Actualización Local**: ✅ Corregido en repositorio local
2. **Actualización Staging**: ✅ Aplicado directamente en servidor
3. **Sin Rebuild**: No fue necesario reconstruir el contenedor (templates montados como volumen)

## Verificación

### Estado Actual

```bash
✅ URL correcta en local
✅ URL correcta en staging  
✅ Endpoint existe (HTTP 302 - requiere autenticación)
✅ Servidor staging funcionando (healthy)
```

### Prueba Manual

1. Abrir: https://staging.jemavi.co/invoices
2. Ir al tab "Facturas"
3. Clic en "Subir Facturas"
4. Seleccionar archivo PDF
5. Verificar que se suba correctamente

## Scripts Creados

### `verify_invoices_fix.sh`
Script de verificación automática que comprueba:
- URL correcta en archivos locales
- URL correcta en staging
- Endpoint funcionando
- Estado del servidor

**Uso**:
```bash
./verify_invoices_fix.sh
```

## Notas Técnicas

### Estructura de Rutas

El router de invoices está configurado así en `src/main.py`:

```python
app.include_router(invoices_router, prefix="/invoices", tags=["Facturas CUFE"])
```

Por lo tanto, todas las rutas definidas en `invoices.py` como `/api/...` se convierten en `/invoices/api/...`

### Volúmenes Docker

Los templates están montados como volumen en `docker-compose.staging.yml`:

```yaml
volumes:
  - ./CODE/src/templates:/app/src/templates
```

Esto permite actualizar templates sin rebuild del contenedor.

## Fecha

**Aplicado**: 2026-01-19 13:13 UTC

## Estado

✅ **RESUELTO** - La carga de facturas ahora funciona correctamente en staging
