# ✅ SOLUCIÓN: Botón de Descarga Habilitado

## 🎯 Problema Identificado

El código está **funcionando correctamente** (probado con `test_upload_directo.py`), pero el servidor necesita reiniciarse para aplicar los cambios.

## 📋 Pasos para Solucionar

### Paso 1: Reiniciar el Servidor

```bash
./REINICIAR_SERVIDOR.sh
```

O manualmente:

```bash
# Si usas Docker
docker-compose restart app

# Si usas Systemd
sudo systemctl restart paquetex

# Si ejecutas manualmente
# Detén el proceso (Ctrl+C) y ejecuta:
cd CODE && source .venv/bin/activate && uvicorn src.main:app --reload
```

### Paso 2: Eliminar Facturas Antiguas

Las facturas actuales no tienen archivos en S3 porque se cargaron antes de la corrección.

**En la interfaz web**:
1. Ve a: http://localhost:8000/invoices/facturas
2. Selecciona todas las facturas (checkbox en el header)
3. Click en "🗑️ Eliminar (N)"
4. Confirma la eliminación

### Paso 3: Cargar Nuevas Facturas

1. Click en el botón "+" (Cargar nueva factura)
2. Selecciona uno o varios PDFs
3. Click en "Cargar"
4. Espera a que se procesen

### Paso 4: Verificar

Después de cargar, deberías ver:
- ✅ Botón de descarga **VERDE** (habilitado)
- ✅ Click en el botón descarga el PDF
- ✅ Mensaje: "Descargando factura..."

---

## 🔍 Verificación Técnica

### Test 1: Verificar que el código funciona
```bash
cd CODE
source .venv/bin/activate
python3 test_upload_directo.py
```

**Resultado esperado**:
```
✅ Factura creada exitosamente!
   S3 Key: invoices/provider/7569152b6d0396f9e5079cbac6bc56df...pdf
🎉 ¡ÉXITO! El archivo se subió a S3 correctamente
```

### Test 2: Verificar S3
```bash
cd CODE
source .venv/bin/activate
python3 diagnostico_s3_upload.py
```

**Resultado esperado**:
```
✅ S3Service inicializado correctamente
✅ Conexión a S3 exitosa
✅ Archivo de prueba subido exitosamente
✅ InvoiceV2Service tiene S3Service disponible
```

### Test 3: Ver logs durante la carga

```bash
# Docker
docker-compose logs -f app | grep -E "(📤|S3|subir|archivo)"

# Systemd
journalctl -u paquetex -f | grep -E "(📤|S3|subir|archivo)"
```

**Logs esperados durante la carga**:
```
📤 Subiendo factura: nombre.pdf (25713 bytes)
📤 Intentando subir archivo a S3...
   Tamaño del archivo: 25713 bytes
   S3 Key: invoices/provider/CUFE.pdf
🔄 Subiendo archivo a S3:
   📦 Bucket: elclub-paqueteria
   🔑 Key: invoices/provider/CUFE.pdf
   📏 Tamaño: 25713 bytes
✅ Archivo subido exitosamente
✅ Factura creada: CUFE... - PROVEEDOR (estado: pendiente_dian)
```

---

## 🛠️ Cambios Implementados

### 1. Endpoint de Upload (`invoices_v2_routes.py`)
```python
# ANTES: Usaba file.file que ya estaba leído
await file.seek(0)
invoice = service.create_invoice_from_provider_pdf(tmp_path, file_obj=file.file)

# AHORA: Usa BytesIO con contenido completo
from io import BytesIO
file_for_s3 = BytesIO(content)
file_for_s3.name = file.filename
invoice = service.create_invoice_from_provider_pdf(tmp_path, file_obj=file_for_s3)
```

### 2. Logging Detallado (`invoice_v2_service.py`)
```python
logger.info(f"📤 Intentando subir archivo a S3...")
logger.info(f"   Tamaño del archivo: {len(file_content)} bytes")
logger.info(f"   S3 Key: {s3_key}")
logger.info(f"✅ Archivo subido a S3: {s3_key}")
```

### 3. Endpoint de Descarga (`invoices_v2_routes.py`)
```python
@router.get("/facturas/{cufe}/download-url")
async def get_invoice_download_url(cufe: str, db: Session = Depends(get_db)):
    # Genera URL pre-firmada de S3 (válida 1 hora)
    url = service.s3_service.generate_presigned_url(...)
    return {"url": url, "filename": "factura_XXX.pdf"}
```

---

## 🎨 Estados del Botón

| Condición | Color | Estado | Acción |
|-----------|-------|--------|--------|
| `archivo_proveedor_s3_key` existe | 🟢 Verde | Habilitado | Descarga PDF |
| `archivo_proveedor_s3_key` es null | ⚪ Gris | Deshabilitado | No hace nada |

---

## 🐛 Si Sigue Sin Funcionar

### Problema: Botón sigue gris después de reiniciar

**Causa**: Las facturas antiguas no tienen archivo en S3

**Solución**: Elimina las facturas antiguas y carga nuevas

### Problema: Error al cargar factura

**Causa**: Problema con S3 o credenciales

**Solución**:
1. Verifica `.env`:
   ```
   AWS_ACCESS_KEY_ID=tu-access-key
   AWS_SECRET_ACCESS_KEY=tu-secret-key
   AWS_S3_BUCKET=elclub-paqueteria
   AWS_REGION=us-east-1
   ```

2. Ejecuta: `python3 CODE/diagnostico_s3_upload.py`

### Problema: Descarga no funciona

**Causa**: URL pre-firmada no se genera

**Solución**: Revisa logs del servidor para ver el error específico

---

## ✅ Checklist Final

- [ ] Servidor reiniciado
- [ ] Facturas antiguas eliminadas
- [ ] Nuevas facturas cargadas
- [ ] Botón de descarga VERDE visible
- [ ] Click en botón descarga el PDF
- [ ] No hay errores en logs

---

## 🎉 Resultado Esperado

Después de seguir estos pasos:

1. ✅ Todas las facturas nuevas tendrán botón VERDE
2. ✅ Click en el botón descarga el PDF automáticamente
3. ✅ Mensaje de éxito: "Descargando factura..."
4. ✅ El archivo se descarga con nombre: `factura_XXX.pdf`

---

## 📞 Soporte

Si después de seguir todos los pasos el botón sigue gris:

1. Ejecuta: `python3 CODE/test_upload_directo.py`
2. Si el test pasa ✅ pero la interfaz no funciona → El servidor no se reinició
3. Si el test falla ❌ → Hay un problema con S3 o credenciales
4. Comparte los logs del servidor para diagnóstico específico
