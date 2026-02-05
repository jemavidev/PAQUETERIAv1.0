# Fix: Descarga de PDF DIAN desde Tab CUFE

## Problema
El botón de descarga de PDF DIAN en el tab CUFE no funcionaba correctamente. No descargaba el archivo asociado al CUFE.

## Solución Implementada

### 1. Modificación del Endpoint de Descarga
**Archivo:** `CODE/src/app/routes/invoices_v2_routes.py`

Se modificó el endpoint `/facturas/{cufe}/download-url` para aceptar un parámetro `file_type` que permite especificar qué tipo de archivo descargar:

- `file_type=proveedor`: Descarga el archivo PDF del proveedor
- `file_type=dian`: Descarga el archivo PDF oficial de la DIAN

**Cambios:**
```python
@router.get("/facturas/{cufe}/download-url")
async def get_invoice_download_url(
    cufe: str, 
    file_type: str = "proveedor",  # "proveedor" o "dian"
    db: Session = Depends(get_db)
):
    # Determinar qué archivo descargar según file_type
    if file_type == "dian":
        s3_key = invoice.archivo_dian_s3_key
        file_prefix = "factura_dian"
    else:
        s3_key = invoice.archivo_proveedor_s3_key
        file_prefix = "factura_proveedor"
    
    # Generar URL pre-firmada de S3
    url = service.s3_service.generate_presigned_url(s3_key, expiration=3600)
    return {"download_url": url, "filename": f"{file_prefix}_{invoice.numero_factura}.pdf"}
```

### 2. Actualización de la Función JavaScript
**Archivo:** `CODE/src/templates/invoices_v2/cufe.html`

Se actualizó la función `downloadInvoicePDF()` para usar el parámetro `file_type=dian`:

```javascript
async function downloadInvoicePDF(cufe) {
    try {
        // Solicitar URL de descarga del archivo DIAN
        const response = await fetch(`/api/v2/invoices/facturas/${cufe}/download-url?file_type=dian`);
        
        if (!response.ok) {
            const error = await response.json();
            showToast(error.detail || 'No hay archivo PDF DIAN disponible', 'warning');
            return;
        }
        
        const data = await response.json();
        
        if (data.download_url) {
            window.open(data.download_url, '_blank');
            showToast('Descargando archivo DIAN...', 'success');
        }
    } catch (error) {
        console.error('Error descargando archivo DIAN:', error);
        showToast('Error al descargar el archivo DIAN', 'error');
    }
}
```

### 3. Corrección de Visibilidad del Botón "Ver en Portal DIAN"
**Archivo:** `CODE/src/templates/invoices_v2/cufe.html`

Se corrigió la lógica para que el botón "Ver en portal DIAN" solo se muestre cuando el estado sea "Pendiente" (no validado):

```javascript
${!dianValidado ? `
    <a href="https://catalogo-vpfe.dian.gov.co/document/searchqr?documentkey=${invoice.cufe}" 
       target="_blank" 
       class="text-purple-600 hover:text-purple-800 transition-colors" 
       title="Ver en portal DIAN">
        <!-- SVG icon -->
    </a>
` : ''}
```

## Lógica de Visibilidad de Botones

En el tab CUFE, los botones se muestran según el estado:

### Estado: Pendiente (no validado)
- ✅ **Cargar archivo DIAN** (nube naranja) - Permite subir el PDF oficial
- ✅ **Ver detalles** (ojo verde) - Siempre visible
- ✅ **Ver en portal DIAN** (enlace morado) - Abre el portal de la DIAN
- ❌ **Descargar PDF DIAN** - No visible (no hay archivo)

### Estado: Validado
- ❌ **Cargar archivo DIAN** - No visible (ya está validado)
- ✅ **Ver detalles** (ojo verde) - Siempre visible
- ❌ **Ver en portal DIAN** - No visible (ya está validado)
- ✅ **Descargar PDF DIAN** (documento rojo) - Descarga el archivo oficial

## Campos del Modelo

El modelo `InvoiceV2` tiene los siguientes campos para archivos:

```python
# Archivos del proveedor
archivo_proveedor_url = Column(Text, nullable=True)
archivo_proveedor_s3_key = Column(String(500), nullable=True)

# Archivos oficiales de la DIAN
archivo_dian_url = Column(Text, nullable=True)
archivo_dian_s3_key = Column(String(500), nullable=True)
```

## Pruebas

Se creó un script de prueba: `CODE/test_download_dian_pdf.py`

**Uso:**
```bash
python CODE/test_download_dian_pdf.py <CUFE>
```

Este script verifica:
1. Que el endpoint genere correctamente la URL de descarga
2. Que la URL sea accesible
3. Que funcione tanto para archivos DIAN como de proveedor

## Flujo de Descarga

1. Usuario hace clic en el botón de descarga PDF DIAN (icono rojo)
2. JavaScript llama a `/api/v2/invoices/facturas/{cufe}/download-url?file_type=dian`
3. Backend verifica que existe `archivo_dian_s3_key`
4. Backend genera URL pre-firmada de S3 (válida por 1 hora)
5. Frontend abre la URL en nueva pestaña para descargar el archivo

## Notas Técnicas

- Las URLs pre-firmadas de S3 expiran en 1 hora (3600 segundos)
- El archivo se descarga directamente desde S3, no pasa por el servidor
- Si no existe el archivo, se muestra un mensaje de error apropiado
- El botón solo es visible si `hasArchivoDIAN` es verdadero
