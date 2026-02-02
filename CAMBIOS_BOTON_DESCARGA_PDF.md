# ✅ CAMBIOS REALIZADOS: Botón de Descarga PDF

## 🎯 Problema Reportado

El usuario indicó que no veía el botón para descargar el archivo PDF de las facturas subidas.

## 🔍 Diagnóstico

El botón de descarga SÍ estaba implementado en el código (línea 309), pero:
- Solo aparecía si `invoice.archivo_proveedor_url` tenía un valor
- Si las facturas no tenían este campo poblado, el botón no se mostraba

## ✅ Solución Implementada

### 1. Botón Siempre Visible

**Antes:**
```javascript
${invoice.archivo_proveedor_url ? `
<button onclick="downloadInvoice(...)">...</button>
` : ''}
```

**Después:**
```javascript
<button onclick="downloadInvoice('${invoice.archivo_proveedor_url || ''}', ...)" 
        class="${invoice.archivo_proveedor_url ? 'text-green-600 hover:text-green-800' : 'text-gray-300 cursor-not-allowed'}" 
        title="${invoice.archivo_proveedor_url ? 'Descargar factura PDF' : 'No hay archivo PDF disponible'}"
        ${!invoice.archivo_proveedor_url ? 'disabled' : ''}>
    <svg>...</svg>
</button>
```

**Comportamiento:**
- ✅ **CON archivo PDF**: Botón verde, clickeable, descarga el archivo
- ⚠️ **SIN archivo PDF**: Botón gris, deshabilitado, tooltip explicativo

### 2. Función de Descarga Mejorada

**Antes:**
```javascript
function downloadInvoice(url, filename) {
    const link = document.createElement('a');
    link.href = url;
    link.download = `factura_${filename}.pdf`;
    link.target = '_blank';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    showToast('Descargando factura...', 'info');
}
```

**Después:**
```javascript
function downloadInvoice(url, filename) {
    if (!url || url.trim() === '') {
        showToast('No hay archivo PDF disponible para esta factura', 'warning');
        return;
    }
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `factura_${filename}.pdf`;
    link.target = '_blank';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    showToast('Descargando factura...', 'info');
}
```

**Mejoras:**
- Valida que la URL exista antes de intentar descargar
- Muestra mensaje de advertencia si no hay archivo
- Previene errores en el navegador

## 📊 Vista en la Tabla

```
┌────────────────────────────────────────────────────────────────────┐
│ CUFE          │ Proveedor │ ... │ Estado │ Acciones              │
├────────────────────────────────────────────────────────────────────┤
│ 8cf8ec5366... │ ABC S.A.S │ ... │ ✓      │ [🟢⬇️] [✏️] [🗑️]      │  ← CON PDF
│ b95d05e6ff... │ XYZ Ltda  │ ... │ ⚠️     │ [⚪⬇️] [✏️] [🗑️]      │  ← SIN PDF
└────────────────────────────────────────────────────────────────────┘

Leyenda:
🟢 = Verde (clickeable, descarga el PDF)
⚪ = Gris (deshabilitado, no hay PDF)
```

## 🔧 Archivos Modificados

### `CODE/src/templates/invoices_v2/facturas.html`

**Líneas modificadas:**
- **Línea ~307-327**: Botón de descarga siempre visible con estados condicionales
- **Línea ~341-352**: Función `downloadInvoice()` con validación

## 📝 Notas Técnicas

### ¿Por qué algunas facturas no tienen archivo PDF?

Hay varias razones posibles:

1. **Facturas antiguas**: Creadas antes de implementar la subida a S3
2. **Servicio S3 no configurado**: Si las variables de entorno de AWS no están configuradas
3. **Error al subir**: Problemas de red o permisos en S3

### ¿Cómo se guarda el archivo PDF?

Cuando se sube una factura (endpoint `/api/v2/invoices/facturas/upload`):

1. El archivo se recibe como `UploadFile`
2. Se extrae el CUFE y otros datos del PDF
3. Se sube a S3 con la ruta: `invoices/provider/{cufe}.pdf`
4. La URL de S3 se guarda en `archivo_proveedor_url`
5. La key de S3 se guarda en `archivo_proveedor_s3_key`

**Código relevante** (`CODE/src/app/services/invoice_v2_service.py`, línea 58-67):
```python
# Subir archivo a S3 (opcional)
archivo_url = None
archivo_s3_key = None
if file_obj and self.s3_service:
    try:
        s3_key = f"invoices/provider/{data['cufe']}.pdf"
        archivo_url = self.s3_service.upload_file(file_obj, s3_key)
        archivo_s3_key = s3_key
    except Exception as e:
        logger.warning(f"No se pudo subir archivo a S3: {e}")
```

### Verificar configuración de S3

Para que los archivos se suban correctamente, verifica estas variables de entorno:

```bash
AWS_ACCESS_KEY_ID=tu_access_key
AWS_SECRET_ACCESS_KEY=tu_secret_key
AWS_REGION=us-east-1
AWS_S3_BUCKET=tu-bucket-name
```

## 🧪 Cómo Probar

### 1. Verificar el botón en el navegador

1. Ve a: `http://localhost:8000/invoices`
2. Deberías ver el botón de descarga (⬇️) en TODAS las filas
3. Pasa el mouse sobre el botón:
   - **Verde**: "Descargar factura PDF"
   - **Gris**: "No hay archivo PDF disponible"

### 2. Probar la descarga

**Con archivo PDF:**
1. Click en el botón verde
2. Debería descargar el archivo
3. Aparece toast: "Descargando factura..."

**Sin archivo PDF:**
1. Click en el botón gris (deshabilitado, no hace nada)
2. Si intentas hacer click, aparece toast: "No hay archivo PDF disponible para esta factura"

### 3. Verificar en la base de datos

Ejecuta este query para ver qué facturas tienen archivo:

```sql
SELECT 
    cufe,
    proveedor_nombre,
    numero_factura,
    CASE 
        WHEN archivo_proveedor_url IS NOT NULL AND archivo_proveedor_url != '' 
        THEN '✅ SÍ' 
        ELSE '❌ NO' 
    END as tiene_pdf,
    archivo_proveedor_url
FROM invoices_v2
ORDER BY created_at DESC
LIMIT 10;
```

## 🚀 Próximos Pasos (Opcional)

Si quieres que TODAS las facturas tengan el PDF disponible:

### Opción 1: Re-subir facturas antiguas
Sube nuevamente las facturas que no tienen PDF usando el modal de carga.

### Opción 2: Migrar PDFs existentes
Si tienes los PDFs en una carpeta local, puedes crear un script para subirlos a S3 y actualizar la base de datos.

### Opción 3: Aceptar el estado actual
El botón gris indica claramente que no hay PDF disponible, lo cual es información útil para el usuario.

## ✅ Resumen

- ✅ Botón de descarga ahora SIEMPRE visible
- ✅ Verde si hay PDF, gris si no hay
- ✅ Tooltip explicativo en ambos casos
- ✅ Validación en la función JavaScript
- ✅ Mensajes de error claros para el usuario

**El usuario ahora puede ver claramente qué facturas tienen PDF disponible para descargar.**
