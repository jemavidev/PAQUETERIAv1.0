# 🔧 Fix: Error de Alpine.js en Alertas de Carga de Facturas

## Problema Identificado

Al cargar facturas en https://staging.jemavi.co/invoices (Tab Facturas), aunque el archivo se subía correctamente, aparecían múltiples errores de Alpine.js en la consola:

```
Alpine Expression Error: Invalid or unexpected token
Expression: "errorAlert({title: 'Atención',message: '✅ Archivos subidos exitosamenteTotal: 1Subidos: 1Fallidos: 0',...
```

### Síntomas

- ✅ El archivo SÍ se subía correctamente al servidor
- ❌ Errores masivos de Alpine.js en consola
- ❌ La notificación de éxito no se mostraba correctamente
- ❌ Múltiples errores: `type is not defined`, `message is not defined`, `title is not defined`

## Causa Raíz

El sistema de alertas personalizado en `base.html` no escapaba correctamente los saltos de línea (`\n`) en los mensajes antes de insertarlos en el atributo `x-data` de Alpine.js.

### Flujo del Problema

1. `uploadFiles()` en `_tab_facturas.html` llama a `alert()` con un mensaje que contiene `\n`
2. `window.alert` está sobrescrito en `base.html` para usar el sistema de alertas personalizado
3. `showAlert()` inserta el mensaje directamente en el HTML sin escapar
4. Los saltos de línea rompen la sintaxis de JavaScript en el atributo `x-data`
5. Alpine.js no puede parsear la expresión y genera múltiples errores

### Código Problemático

**Antes** (línea ~1318 en base.html):
```javascript
const alertHtml = `
    <div id="${alertId}" 
         x-data="errorAlert({
             title: '${title}',           // ❌ Sin escapar
             message: '${message}',       // ❌ Sin escapar - contiene \n
             type: '${type}',
             ...
         })"
```

Cuando `message` contenía:
```
✅ Archivos subidos exitosamente\n\nTotal: 1\nSubidos: 1\nFallidos: 0
```

Se generaba HTML inválido:
```javascript
message: '✅ Archivos subidos exitosamente
Total: 1
Subidos: 1
Fallidos: 0'  // ❌ Sintaxis rota
```

## Solución Aplicada

### 1. Escapar Mensajes en showAlert()

**Archivo**: `CODE/src/templates/base/base.html`

**Cambio**:
```javascript
// Escapar comillas y saltos de línea en el mensaje
const escapedTitle = title.replace(/'/g, "\\'").replace(/\n/g, ' ');
const escapedMessage = message.replace(/'/g, "\\'").replace(/\n/g, ' ');

const alertHtml = `
    <div id="${alertId}" 
         x-data="errorAlert({
             title: '${escapedTitle}',      // ✅ Escapado
             message: '${escapedMessage}',  // ✅ Escapado
             type: '${type}',
             ...
         })"
```

### 2. Usar window.alert Explícitamente

**Archivo**: `CODE/src/templates/invoices/_tab_facturas.html`

**Cambio**:
```javascript
// Antes
alert(`✅ Archivos subidos exitosamente...`);

// Después
window.alert(`✅ Archivos subidos exitosamente...`);
```

Esto asegura que se use el alert sobrescrito y no alguna versión local.

## Archivos Modificados

1. ✅ `CODE/src/templates/base/base.html` - Escapar mensajes en showAlert()
2. ✅ `CODE/src/templates/invoices/_tab_facturas.html` - Usar window.alert explícitamente

## Deploy a Staging

```bash
# Actualizar base.html
scp CODE/src/templates/base/base.html staging:/home/ubuntu/paqueteria-staging/CODE/src/templates/base/base.html

# Actualizar _tab_facturas.html
scp CODE/src/templates/invoices/_tab_facturas.html staging:/home/ubuntu/paqueteria-staging/CODE/src/templates/invoices/_tab_facturas.html
```

**Nota**: No fue necesario reiniciar el contenedor porque los templates están montados como volumen.

## Verificación

### Antes del Fix
```
❌ Alpine Expression Error: Invalid or unexpected token
❌ Alpine Expression Error: alertTypeClass is not defined
❌ Alpine Expression Error: show is not defined
❌ Alpine Expression Error: type is not defined
❌ Alpine Expression Error: title is not defined
❌ Alpine Expression Error: message is not defined
... (múltiples errores)
```

### Después del Fix
```
✅ Sin errores de Alpine.js
✅ Notificación se muestra correctamente
✅ Mensaje escapado: "✅ Archivos subidos exitosamente Total: 1 Subidos: 1 Fallidos: 0"
✅ Archivo se sube correctamente
```

## Prueba Manual

1. Abrir: https://staging.jemavi.co/invoices
2. Ir al tab "Facturas"
3. Clic en "Subir Facturas"
4. Seleccionar un archivo PDF
5. Verificar que:
   - ✅ El archivo se sube correctamente
   - ✅ Aparece notificación de éxito
   - ✅ No hay errores en consola
   - ✅ El tab se recarga mostrando la nueva factura

## Notas Técnicas

### Escapado de Caracteres

La función ahora escapa:
- **Comillas simples** (`'` → `\'`) - Para evitar romper la sintaxis de JavaScript
- **Saltos de línea** (`\n` → ` `) - Para evitar romper la sintaxis de JavaScript

### Alternativas Consideradas

1. **Usar JSON.stringify()**: Más robusto pero genera comillas dobles que requieren más procesamiento
2. **Usar <br> en lugar de \n**: Requeriría cambiar x-text a x-html (riesgo de XSS)
3. **Usar alert nativo sin override**: Perdería la consistencia visual

La solución actual es la más simple y mantiene la funcionalidad existente.

## Fecha

**Aplicado**: 2026-01-19 13:30 UTC

## Estado

✅ **RESUELTO** - La carga de facturas funciona correctamente sin errores de Alpine.js
