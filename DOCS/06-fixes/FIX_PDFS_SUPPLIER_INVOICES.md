# 🔧 Fix: PDFs de Supplier Invoices No Accesibles

**Fecha:** 16 de Enero, 2026  
**Problema:** Error 404 al intentar ver PDFs de supplier_invoices

---

## 🐛 PROBLEMA IDENTIFICADO

### Síntomas:
- Al hacer clic en el ícono PDF de una supplier_invoice
- Se abre la URL: `/invoices/api/supplier-invoices/{id}/pdf`
- Aparece error 404: "Página no encontrada"

### Causa Raíz:
El código de subida tenía un bug que impedía guardar el PDF correctamente:

```python
# CÓDIGO ANTERIOR (INCORRECTO):
s3_service.upload_pdf(content, f"supplier-invoices/{invoice.original_file_hash}", metadata)
```

El problema era que:
1. El método `upload_pdf` espera solo el hash
2. Pero le estábamos pasando `supplier-invoices/{hash}`
3. El método agrega automáticamente el prefijo `invoices/`
4. Resultado: intentaba guardar en `invoices/supplier-invoices/{hash}.pdf` ❌

---

## ✅ SOLUCIÓN APLICADA

### 1. Código Corregido

```python
# CÓDIGO NUEVO (CORRECTO):
s3_key = f"supplier-invoices/{invoice.original_file_hash}.pdf"

s3_service.s3_client.put_object(
    Bucket=s3_service.bucket_name,
    Key=s3_key,  # Key completa y correcta
    Body=content,
    ContentType='application/pdf',
    Metadata=metadata,
    ServerSideEncryption='AES256',
)

invoice.original_file_path = s3_key
db.commit()
```

### 2. Fallback Local Agregado

Si S3 falla, ahora guarda localmente:

```python
except Exception as e:
    logger.error(f"Error guardando PDF en S3: {e}")
    # Fallback: guardar localmente
    local_dir = "/app/src/uploads/supplier-invoices"
    os.makedirs(local_dir, exist_ok=True)
    local_path = f"{local_dir}/{invoice.original_file_hash}.pdf"
    with open(local_path, 'wb') as f:
        f.write(content)
    logger.info(f"PDF guardado localmente: {local_path}")
```

---

## 📊 FACTURAS AFECTADAS

Las 5 facturas que subiste tienen este problema:

| ID | Archivo | Estado | PDF Guardado |
|----|---------|--------|--------------|
| 1 | Factura.pdf | no_cufe | ❌ NO |
| 2 | Factura.pdf | no_cufe | ❌ NO |
| 3 | Factura.pdf | no_cufe | ❌ NO |
| 4 | Factura.pdf | no_cufe | ❌ NO |
| 5 | Factura.pdf | no_cufe | ❌ NO |

---

## 🚀 PASOS PARA RESOLVER

### Opción A: Eliminar y Re-subir (RECOMENDADO)

**Más fácil y rápido:**

1. Ejecutar script de reparación:
```bash
cd CODE
python3 reparar_pdfs_supplier_invoices.py
# Escribir "SI" para confirmar eliminación
```

2. Re-subir las 5 facturas:
   - Ir a `/invoices/supplier-invoices`
   - Hacer clic en "Subir Factura"
   - Seleccionar los PDFs nuevamente
   - Ahora se guardarán correctamente ✅

### Opción B: Mantener Sin PDF

**Si no tienes los PDFs originales:**

1. Ejecutar script:
```bash
cd CODE
python3 reparar_pdfs_supplier_invoices.py
# Escribir "NO" para cancelar
```

2. Las facturas se mantienen pero sin PDF accesible
3. Puedes agregar el CUFE manualmente si lo conoces

---

## ✅ VERIFICACIÓN POST-FIX

### 1. Reiniciar Servidor

```bash
# Docker
docker-compose restart web

# O uvicorn
# Ctrl+C y luego:
cd CODE
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Subir Nueva Factura de Prueba

1. Ir a: `https://staging.jemavi.co/invoices/supplier-invoices`
2. Hacer clic en "Subir Factura"
3. Seleccionar un PDF
4. Verificar que se sube correctamente
5. Hacer clic en el ícono PDF
6. Verificar que el PDF se abre ✅

### 3. Verificar en Base de Datos

```bash
cd CODE
python3 verificar_supplier_invoice.py <ID>
```

Deberías ver:
```
Path S3: supplier-invoices/{hash}.pdf  ✅
S3 habilitado: ✅
URL firmada: ✅
```

---

## 📋 ARCHIVOS MODIFICADOS

1. ✅ `CODE/src/app/routes/invoices.py`
   - Endpoint `/api/supplier-invoices/upload` corregido
   - Agregado fallback local

2. ✅ `CODE/reparar_pdfs_supplier_invoices.py` (NUEVO)
   - Script para identificar y eliminar facturas afectadas

3. ✅ `CODE/verificar_supplier_invoice.py` (NUEVO)
   - Script para verificar estado de una factura

---

## 🎯 RESULTADO ESPERADO

### Antes del Fix:
```
Subir PDF → ❌ No se guarda → ❌ Error 404 al ver
```

### Después del Fix:
```
Subir PDF → ✅ Se guarda en S3 → ✅ PDF accesible
```

---

## ⚠️ IMPORTANTE

### Para Facturas Nuevas:
- ✅ El bug está corregido
- ✅ Se guardarán correctamente en S3
- ✅ Tendrán fallback local si S3 falla

### Para Facturas Existentes (las 5):
- ❌ No tienen PDF guardado
- ⚠️ Necesitas eliminarlas y re-subirlas
- O mantenerlas sin PDF

---

## 📞 PRÓXIMOS PASOS

1. **Reiniciar servidor** (obligatorio)
2. **Ejecutar script de reparación** (opcional)
3. **Re-subir las 5 facturas** (recomendado)
4. **Probar con nueva factura** (verificación)

---

**Estado:** ✅ FIX APLICADO - PENDIENTE REINICIO DE SERVIDOR
