# TAREAS - Sistema de Facturas de Proveedores

## Flujo del Sistema

```
1. Subir PDF del proveedor → 2. Extraer CUFE/fecha/proveedor → 3. Abrir DIAN con CUFE
→ 4. Resolver captcha y descargar PDF DIAN → 5. Subir PDF DIAN al sistema → 6. Factura procesada
```

---

## ✅ COMPLETADO

### Backend - Modelo (`invoice.py`)
- [x] Modelo `SupplierInvoice` con todos los campos necesarios
- [x] Enum `SupplierInvoiceStatus` (pending, no_cufe, cufe_extracted, dian_downloaded, processed, error, duplicate)
- [x] Propiedades `cufe_short` y `dian_url`
- [x] Relación con `Invoice` procesada

### Backend - Servicio (`supplier_invoice_service.py`)
- [x] Extracción de CUFE del nombre de archivo
- [x] Extracción de CUFE del contenido PDF (usando pdfplumber)
- [x] Validación de CUFE (96 caracteres hex)
- [x] Detección de duplicados (por hash y por CUFE)
- [x] Extracción de info básica (NIT, fecha, número factura, proveedor)
- [x] CRUD completo (get_all, get_by_id, delete)
- [x] Estadísticas por estado
- [x] Actualización de estado y CUFE manual
- [x] Corregido para usar `pdfplumber` (no PyMuPDF)

### Backend - Rutas (`invoices.py`)
- [x] GET `/supplier-invoices` - Vista principal
- [x] POST `/api/supplier-invoices/upload` - Subir PDF
- [x] POST `/api/supplier-invoices/{id}/cufe` - Actualizar CUFE manual
- [x] GET `/api/supplier-invoices/pending-cufes` - Lista CUFEs para DIAN
- [x] POST `/api/supplier-invoices/{id}/mark-downloaded` - Marcar descargado
- [x] POST `/api/supplier-invoices/{id}/mark-processed` - Marcar procesado
- [x] DELETE `/api/supplier-invoices/{id}` - Eliminar

### Frontend - Template (`supplier_invoices.html`)
- [x] Vista de tabla con todas las facturas
- [x] Cards de estadísticas por estado (Total, Sin CUFE, CUFE Extraído, DIAN Descargado, Procesadas, Errores)
- [x] Filtro por estado
- [x] Paginación
- [x] Modal de upload (drag & drop, múltiples archivos)
- [x] Modal de CUFE manual
- [x] Modal de procesamiento DIAN (lista de CUFEs pendientes con links)
- [x] Modal de importación de PDF DIAN
- [x] Acciones por fila según estado
- [x] Función eliminar
- [x] Integración con sistema existente de facturas (`/invoices/api/extract` y `/invoices/api/save`)

### Dashboard
- [x] Botón "Facturas Proveedores" agregado al dashboard principal

### Migración
- [x] Archivo de migración creado (`add_supplier_invoices_table.py`)
- [x] Corregido `down_revision = 'enhance_invoice_system'`

---

## ❌ PENDIENTE (Mejoras futuras, no bloqueantes)

### Almacenamiento
- [ ] Guardar PDF original en S3 (actualmente solo se procesa temporalmente)
- [ ] Guardar PDF de DIAN en S3
- [ ] Endpoint para descargar PDF original

### UX
- [ ] Búsqueda por nombre de archivo o proveedor
- [ ] Ordenamiento de columnas
- [ ] Selección múltiple para acciones en lote
- [ ] Exportar lista a Excel/CSV

### Automatización
- [ ] Automatizar descarga de DIAN (requiere resolver captcha - difícil)

---

## 📋 PARA DEPLOY

1. ✅ Migración corregida con `down_revision`
2. ✅ Servicio usa `pdfplumber` (ya instalado)
3. Ejecutar migración: `alembic upgrade head`
4. Commit de todos los archivos
5. Deploy a staging
6. Probar flujo completo

---

## ARCHIVOS INVOLUCRADOS

**Modificados:**
- `CODE/src/app/models/invoice.py` - Modelo SupplierInvoice
- `CODE/src/app/routes/invoices.py` - Endpoints API
- `CODE/src/templates/invoices/dashboard.html` - Botón de acceso

**Nuevos:**
- `CODE/alembic/versions/add_supplier_invoices_table.py` - Migración
- `CODE/src/app/services/supplier_invoice_service.py` - Servicio
- `CODE/src/templates/invoices/supplier_invoices.html` - Vista
