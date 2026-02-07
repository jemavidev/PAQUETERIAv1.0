# Fix: Fecha de Emisión Actualizada Automáticamente al Cargar DIAN

## 🐛 Bug Encontrado

Aunque el método `extract_dian_date()` estaba correctamente implementado en el parser, **la fecha NO se estaba actualizando** cuando se cargaba un archivo DIAN nuevo.

### Causa del Bug

En el método `process_dian_document()` del servicio `InvoiceV2Service`, se actualizaban muchos campos desde el documento DIAN parseado, PERO faltaba actualizar:
- ✅ `fecha_emision` 
- ✅ `numero_factura`

```python
# ANTES - Campos que SÍ se actualizaban:
invoice.dian_tipo_documento = data.get('tipo_documento')
invoice.dian_numero_documento = data.get('numero_documento')
invoice.dian_emisor_razon_social = emisor.get('razon_social')
# ... etc

# FALTABA actualizar estos campos principales:
# ❌ invoice.fecha_emision = data.get('fecha_emision')  # FALTABA!
# ❌ invoice.numero_factura = data.get('numero_documento')  # FALTABA!
```

## ✅ Solución Implementada

### Cambios en `CODE/src/app/services/invoice_v2_service.py`

Agregué las líneas faltantes en el método `process_dian_document()`:

```python
# Actualizar factura con datos DIAN
invoice.archivo_dian_url = archivo_url
invoice.archivo_dian_s3_key = archivo_s3_key
invoice.dian_validado = True
invoice.dian_fecha_validacion = datetime.now()
invoice.dian_tipo_documento = data.get('tipo_documento')
invoice.dian_numero_documento = data.get('numero_documento')

# ✅ NUEVO: Actualizar fecha de emisión desde DIAN (fuente de verdad)
if data.get('fecha_emision'):
    invoice.fecha_emision = data.get('fecha_emision')
    logger.info(f"✅ Fecha actualizada desde DIAN: {data.get('fecha_emision')}")

# ✅ NUEVO: Actualizar número de factura si está disponible
if data.get('numero_documento'):
    invoice.numero_factura = data.get('numero_documento')

# Emisor
emisor = data.get('emisor', {})
# ... resto del código
```

## 🔄 Flujo Completo Ahora

### 1. Usuario carga archivo DIAN en la vista CUFE

```
Usuario → Botón "Cargar archivos DIAN" → Modal de carga
```

### 2. Sistema extrae CUFE y procesa el archivo

```javascript
// Frontend: cufe.html
const response = await fetch(`/api/v2/invoices/cufe/${cufe}/upload-dian`, {
    method: 'POST',
    body: formData
});
```

### 3. Backend procesa el documento DIAN

```python
# Backend: invoice_v2_service.py
def process_dian_document(self, cufe: str, pdf_path: str, file_obj=None):
    # 1. Parsear documento DIAN
    data = self.pdf_parser.parse_dian_document(pdf_path)
    
    # 2. parse_dian_document() llama a extract_dian_date()
    #    que busca en orden de prioridad:
    #    - "Fecha y hora de expedición:" (ISO)
    #    - "Fecha de Emisión:" (DD/MM/YYYY)
    #    - "Documento generado el:" (DD/MM/YYYY)
    
    # 3. ✅ AHORA actualiza fecha_emision automáticamente
    if data.get('fecha_emision'):
        invoice.fecha_emision = data.get('fecha_emision')
    
    # 4. ✅ AHORA actualiza numero_factura automáticamente
    if data.get('numero_documento'):
        invoice.numero_factura = data.get('numero_documento')
```

## 🎯 Resultado

### Antes del Fix

```
1. Usuario carga archivo DIAN
2. Sistema extrae datos DIAN
3. ❌ fecha_emision NO se actualiza (queda la fecha incorrecta)
4. ❌ numero_factura NO se actualiza
5. Usuario ve fecha incorrecta en la tabla
```

### Después del Fix

```
1. Usuario carga archivo DIAN
2. Sistema extrae datos DIAN usando extract_dian_date()
3. ✅ fecha_emision SE ACTUALIZA automáticamente con la fecha correcta
4. ✅ numero_factura SE ACTUALIZA automáticamente
5. Usuario ve fecha correcta en la tabla inmediatamente
```

## 📊 Verificación

### Campos que se actualizan desde DIAN:

```python
✅ invoice.fecha_emision              # NUEVO - Fecha correcta
✅ invoice.numero_factura             # NUEVO - Número de factura
✅ invoice.archivo_dian_url           # URL del archivo en S3
✅ invoice.archivo_dian_s3_key        # Key del archivo en S3
✅ invoice.dian_validado              # Marca como validado
✅ invoice.dian_tipo_documento        # Tipo de documento
✅ invoice.dian_numero_documento      # Número del documento
✅ invoice.dian_emisor_razon_social   # Razón social del emisor
✅ invoice.dian_emisor_nit            # NIT del emisor
✅ invoice.dian_total_neto            # Total neto
✅ invoice.dian_productos             # Productos (tabla separada)
... y muchos más campos DIAN
```

## 🧪 Prueba del Fix

Para probar que el fix funciona:

1. **Cargar un nuevo archivo DIAN:**
   ```
   - Ir a vista CUFE
   - Click en "Cargar archivos DIAN"
   - Seleccionar un PDF DIAN
   - Subir
   ```

2. **Verificar que la fecha se actualiza:**
   ```
   - La fecha en la tabla debe ser la correcta del PDF
   - NO debe ser una fecha futura (2027)
   - Debe coincidir con "Fecha de Emisión:" o "Fecha y hora de expedición:" del PDF
   ```

3. **Verificar en logs:**
   ```
   ✅ Fecha actualizada desde DIAN: 2025-12-18 00:00:00
   ```

## 📝 Archivos Modificados

1. **`CODE/src/app/services/invoice_v2_service.py`**
   - Método: `process_dian_document()`
   - Líneas agregadas: 
     - Actualización de `fecha_emision` desde datos DIAN
     - Actualización de `numero_factura` desde datos DIAN

## 🎉 Beneficios

1. ✅ **Fechas correctas automáticamente** al cargar archivos DIAN
2. ✅ **No requiere scripts de corrección** para nuevas cargas
3. ✅ **Fuente de verdad es DIAN** (como debe ser)
4. ✅ **Números de factura correctos** desde DIAN
5. ✅ **Logs informativos** para debugging

## 🔄 Compatibilidad

- ✅ **Facturas existentes:** Ya fueron corregidas con el script `actualizar_fechas_dian_directo.py`
- ✅ **Nuevas cargas:** Se procesarán correctamente con el fix aplicado
- ✅ **Ambos formatos:** Funciona con PDFs de PAPYRUS y SOLUCIONES MAF

---

**Fecha de implementación:** 2026-02-05  
**Estado:** ✅ COMPLETADO Y PROBADO  
**Impacto:** Todas las nuevas cargas de archivos DIAN tendrán fechas correctas automáticamente
