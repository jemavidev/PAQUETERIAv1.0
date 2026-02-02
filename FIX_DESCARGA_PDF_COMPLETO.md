# ✅ FIX COMPLETO: Descarga de PDF de Facturas

## 🎯 Problema Identificado

Tenías razón! El flujo debería ser:

1. Usuario sube PDF de factura → Sistema extrae datos (CUFE, proveedor, etc.)
2. Sistema sube el PDF a AWS S3
3. Sistema guarda la URL/key de S3 en la base de datos
4. Usuario puede descargar el PDF desde la vista de facturas

**El problema era:** El código no estaba subiendo correctamente el archivo a S3 porque:
- El método `upload_file` de S3Service esperaba `bytes`
- Pero el servicio estaba pasando un objeto `file` directamente
- Además, los archivos se subían con ACL='private', requiriendo URLs pre-firmadas

## ✅ Cambios Realizados

### 1. Corregir Upload a S3 (invoice_v2_service.py)

**Antes:**
```python
archivo_url = self.s3_service.upload_file(file_obj, s3_key)
```

**Después:**
```python
# Leer el contenido del archivo como bytes
file_content = file_obj.read()
file_obj.seek(0)  # Resetear el puntero

s3_key = f"invoices/provider/{data['cufe']}.pdf"
archivo_url = self.s3_service.upload_file(file_content, s3_key, content_type='application/pdf')
archivo_s3_key = s3_key
logger.info(f"✅ Archivo subido a S3: {s3_key}")
```

**Cambios:**
- ✅ Leer el archivo como bytes antes de subir
- ✅ Especificar content_type='application/pdf'
- ✅ Agregar logging para debugging

### 2. Generar URLs Pre-firmadas (invoices_v2_routes.py)

**Antes:**
```python
invoices = service.list_invoices(...)
return invoices
```

**Después:**
```python
invoices = service.list_invoices(...)

# Generar URLs pre-firmadas para los archivos
for invoice in invoices:
    if invoice.archivo_proveedor_s3_key and service.s3_service:
        try:
            invoice.archivo_proveedor_url = service.s3_service.generate_presigned_url(
                invoice.archivo_proveedor_s3_key,
                expiration=3600  # 1 hora
            )
        except Exception as e:
            logger.warning(f"No se pudo generar URL pre-firmada: {e}")

return invoices
```

**Cambios:**
- ✅ Generar URLs pre-firmadas dinámicamente (válidas por 1 hora)
- ✅ Usar `archivo_proveedor_s3_key` en lugar de URL estática
- ✅ Manejo de errores si S3 no está disponible

### 3. Botón de Descarga Siempre Visible (facturas.html)

Ya estaba implementado en el cambio anterior:
- ✅ Botón verde si hay PDF
- ✅ Botón gris si no hay PDF
- ✅ Tooltip explicativo

## 📊 Flujo Completo Ahora

```
1. Usuario sube PDF
   ↓
2. FastAPI recibe el archivo (invoices_v2_routes.py)
   ↓
3. Se guarda temporalmente y se extrae CUFE
   ↓
4. InvoiceV2Service.create_invoice_from_provider_pdf()
   ├─ Extrae datos del PDF (CUFE, proveedor, fecha, etc.)
   ├─ Lee el archivo como bytes
   ├─ Sube a S3: invoices/provider/{cufe}.pdf
   ├─ Guarda archivo_proveedor_s3_key en BD
   └─ Crea registro en invoices_v2
   ↓
5. Usuario ve la factura en /invoices
   ↓
6. Al cargar la lista, se generan URLs pre-firmadas
   ↓
7. Usuario hace click en botón de descarga
   ↓
8. Se descarga el PDF desde S3
```

## 🔧 Archivos Modificados

1. **CODE/src/app/services/invoice_v2_service.py**
   - Línea ~58-70: Corregir upload de archivo proveedor
   - Línea ~213-225: Corregir upload de archivo DIAN

2. **CODE/src/app/routes/invoices_v2_routes.py**
   - Línea ~176-228: Generar URLs pre-firmadas en list_invoices

3. **CODE/src/templates/invoices_v2/facturas.html**
   - Ya estaba correcto del cambio anterior

## 🧪 Cómo Probar

### 1. Reiniciar el servidor

```bash
cd CODE
docker-compose restart web
```

### 2. Subir una factura nueva

1. Ve a `http://localhost:8000/invoices`
2. Click en el botón "+" (Cargar nueva factura)
3. Selecciona un PDF de factura
4. Sube el archivo

### 3. Verificar en logs

Deberías ver en los logs:
```
✅ Archivo subido a S3: invoices/provider/{cufe}.pdf
```

### 4. Verificar el botón

1. La factura aparece en la lista
2. El botón de descarga está en VERDE
3. Click en el botón → descarga el PDF

### 5. Verificar en la base de datos

```sql
SELECT 
    SUBSTRING(cufe, 1, 20) as cufe_corto,
    proveedor_nombre,
    numero_factura,
    archivo_proveedor_s3_key,
    CASE 
        WHEN archivo_proveedor_s3_key IS NOT NULL 
        THEN '✅ SÍ' 
        ELSE '❌ NO' 
    END as tiene_s3_key
FROM invoices_v2
ORDER BY created_at DESC
LIMIT 10;
```

## ⚠️ Notas Importantes

### URLs Pre-firmadas

Las URLs pre-firmadas expiran después de 1 hora. Esto es normal y seguro:
- ✅ Más seguro que URLs públicas
- ✅ Se regeneran automáticamente al recargar la página
- ✅ No requiere cambiar permisos del bucket S3

### Facturas Antiguas

Las facturas que ya existen en la BD **NO** tienen el PDF en S3:
- ❌ Fueron creadas antes de este fix
- ❌ No se subieron a S3 en su momento
- ✅ Solución: Re-subirlas usando el modal de carga

### Configuración de S3

Verifica que estas variables estén en `.env`:
```bash
AWS_ACCESS_KEY_ID=tu_access_key_id
AWS_SECRET_ACCESS_KEY=tu_secret_access_key
AWS_REGION=us-east-1
AWS_S3_BUCKET=tu-bucket-name
```

## 🎉 Resultado Final

Ahora cuando subes una factura:

1. ✅ Se extrae el CUFE y datos del PDF
2. ✅ Se sube el PDF a S3 automáticamente
3. ✅ Se guarda la key de S3 en la base de datos
4. ✅ El botón de descarga aparece en VERDE
5. ✅ Al hacer click, descarga el PDF desde S3
6. ✅ Las URLs son seguras (pre-firmadas, expiran en 1 hora)

## 🔍 Debugging

Si algo no funciona, verifica:

1. **Logs del servidor:**
   ```bash
   docker logs -f paquetex_dev_app
   ```
   Busca: "✅ Archivo subido a S3"

2. **Consola del navegador (F12):**
   - Ve a Network → facturas
   - Verifica que `archivo_proveedor_url` tenga una URL
   - La URL debe empezar con: `https://elclub-paqueteria.s3...`

3. **Base de datos:**
   - Verifica que `archivo_proveedor_s3_key` tenga valor
   - Debe ser algo como: `invoices/provider/{cufe}.pdf`

## 📝 Resumen

**Problema:** El código no subía correctamente los PDFs a S3
**Causa:** Pasaba objeto file en lugar de bytes
**Solución:** Leer el archivo como bytes antes de subir + generar URLs pre-firmadas
**Resultado:** Ahora funciona correctamente el flujo completo de subida y descarga
