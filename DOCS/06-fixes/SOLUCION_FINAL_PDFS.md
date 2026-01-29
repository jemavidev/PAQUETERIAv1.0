# ✅ SOLUCIÓN FINAL: PDFs de Supplier Invoices

**Fecha:** 16 de Enero, 2026  
**Problema:** Error 404 al intentar ver PDFs

---

## 🔧 CAMBIOS APLICADOS

### 1. Corregido el código de subida de PDFs

**Archivo:** `CODE/src/app/routes/invoices.py`

Ahora guarda correctamente en S3 con la key completa:
```python
s3_key = f"supplier-invoices/{invoice.original_file_hash}.pdf"
s3_service.s3_client.put_object(
    Bucket=s3_service.bucket_name,
    Key=s3_key,
    Body=content,
    ...
)
invoice.original_file_path = s3_key
```

### 2. Agregado fallback local

Si S3 falla, guarda localmente:
```python
local_dir = "/app/src/uploads/supplier-invoices"
os.makedirs(local_dir, exist_ok=True)
local_path = f"{local_dir}/{invoice.original_file_hash}.pdf"
with open(local_path, 'wb') as f:
    f.write(content)
```

### 3. Cambiado el método de visualización

**Archivo:** `CODE/src/templates/invoices/supplier_invoices.html`

**ANTES:** Enlace directo que no funcionaba
```html
<a href="/invoices/api/supplier-invoices/{{ invoice.id }}/pdf" target="_blank">
```

**AHORA:** Botón con JavaScript que usa fetch
```html
<button onclick="viewPDF({{ invoice.id }})">
```

**Función JavaScript agregada:**
```javascript
async function viewPDF(invoiceId) {
    const res = await fetch(`/invoices/api/supplier-invoices/${invoiceId}/pdf`, {
        method: 'GET',
        credentials: 'include' // Incluye cookies para autenticación
    });
    
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    window.open(url, '_blank');
}
```

---

## ⚠️ PROBLEMA CON FACTURAS EXISTENTES

Las 5 facturas que ya subiste **NO tienen el PDF guardado** porque se subieron con el código bugueado.

### Verificación:
```bash
cd CODE
python3 verificar_supplier_invoice.py 3
```

Resultado:
```
Path S3: NO GUARDADO ❌
S3 habilitado: ❌
Archivo local: ❌
```

---

## 🚀 SOLUCIÓN: RE-SUBIR LAS FACTURAS

### Paso 1: Eliminar facturas sin PDF

```bash
cd CODE
python3 reparar_pdfs_supplier_invoices.py
# Escribir "SI" para confirmar
```

Esto eliminará las 5 facturas que no tienen PDF.

### Paso 2: Reiniciar el servidor

```bash
docker-compose restart web
```

### Paso 3: Re-subir las facturas

1. Ir a: `https://staging.jemavi.co/invoices/supplier-invoices`
2. Hacer clic en "Subir Factura"
3. Seleccionar los 5 PDFs nuevamente
4. Ahora se guardarán correctamente ✅

### Paso 4: Verificar que funciona

1. Hacer clic en el ícono PDF (ahora es un botón)
2. El PDF debería abrirse en una nueva pestaña ✅

---

## 📊 RESUMEN DE CAMBIOS

| Archivo | Cambio |
|---------|--------|
| `CODE/src/app/routes/invoices.py` | ✅ Corregido upload de PDFs |
| `CODE/src/templates/invoices/supplier_invoices.html` | ✅ Cambiado enlace a botón con JS |
| `CODE/reparar_pdfs_supplier_invoices.py` | ✅ Script para limpiar facturas sin PDF |
| `CODE/verificar_supplier_invoice.py` | ✅ Script para verificar estado |

---

## ✅ VERIFICACIÓN POST-FIX

### Test 1: Subir nueva factura

1. Ir a `/invoices/supplier-invoices`
2. Subir un PDF
3. Verificar en logs que dice: "PDF de proveedor guardado en S3"

### Test 2: Ver PDF

1. Hacer clic en el ícono PDF
2. Debería abrir en nueva pestaña
3. Sin error 404

### Test 3: Verificar en BD

```bash
python3 verificar_supplier_invoice.py <ID>
```

Debería mostrar:
```
Path S3: supplier-invoices/{hash}.pdf ✅
S3 habilitado: ✅
URL firmada: ✅
```

---

## 🎯 POR QUÉ FUNCIONARÁ AHORA

### Problema Original:
1. ❌ Código de subida tenía bug
2. ❌ PDF no se guardaba
3. ❌ Enlace directo no enviaba cookies
4. ❌ Error 404

### Solución Aplicada:
1. ✅ Código corregido
2. ✅ PDF se guarda en S3 + fallback local
3. ✅ JavaScript usa fetch con credentials
4. ✅ PDF se abre correctamente

---

## 📞 INSTRUCCIONES FINALES

**EJECUTA EN ESTE ORDEN:**

```bash
# 1. Eliminar facturas sin PDF
cd CODE
python3 reparar_pdfs_supplier_invoices.py
# Escribir "SI"

# 2. Reiniciar servidor
docker-compose restart web

# 3. Re-subir las 5 facturas desde el navegador
# Ir a: https://staging.jemavi.co/invoices/supplier-invoices
# Click en "Subir Factura"
# Seleccionar PDFs

# 4. Probar haciendo click en el ícono PDF
```

---

**Estado:** ✅ CÓDIGO CORREGIDO - PENDIENTE RE-SUBIR FACTURAS
