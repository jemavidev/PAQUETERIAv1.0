# 🔄 Plan de Refactorización Completa - Sistema de Facturas

**Fecha:** 2026-01-30  
**Objetivo:** Eliminar todo el código existente del sistema de facturas para implementar nuevas funcionalidades desde cero.

---

## 📦 Backup Realizado

✅ Archivos respaldados en `BACKUP_INVOICES_OLD/`:
- `invoices_routes_backup.py` (92KB)
- `invoices_mockup_backup.py` (9KB)
- `templates_invoices_backup/` (todos los templates HTML)

---

## 🗑️ Archivos a ELIMINAR

### 1. **Rutas (Routes)**
- [ ] `CODE/src/app/routes/invoices.py` (92KB - 2100+ líneas)
- [ ] `CODE/src/app/routes/invoices_mockup.py` (9KB)

### 2. **Servicios (Services)**
- [ ] `CODE/src/app/services/invoice_service.py`
- [ ] `CODE/src/app/services/supplier_invoice_service.py`
- [ ] `CODE/src/app/services/pdf_extractor_service.py`
- [ ] `CODE/src/app/services/enhanced_pdf_extractor.py` (si existe)

### 3. **Templates HTML**
- [ ] `CODE/src/templates/invoices/dashboard.html`
- [ ] `CODE/src/templates/invoices/_tab_facturas.html`
- [ ] `CODE/src/templates/invoices/_tab_cufe.html`
- [ ] `CODE/src/templates/invoices/_tab_productos.html`
- [ ] `CODE/src/templates/invoices/supplier_invoices.html`
- [ ] `CODE/src/templates/invoices/list.html`
- [ ] `CODE/src/templates/invoices/detail.html`
- [ ] `CODE/src/templates/invoices/upload.html`
- [ ] `CODE/src/templates/invoices/products.html`
- [ ] `CODE/src/templates/invoices/cufe_import.html`
- [ ] `CODE/src/templates/invoices/irregularities.html`
- [ ] `CODE/src/templates/invoices/rejected.html`

### 4. **Modelos (Opcional - Mantener estructura de BD)**
⚠️ **NO ELIMINAR** (a menos que quieras recrear las tablas):
- `CODE/src/app/models/invoice.py` - Contiene `SupplierInvoice`, `Invoice`, etc.

### 5. **Migraciones de Base de Datos**
⚠️ **DECISIÓN REQUERIDA:**
- ¿Mantener las tablas existentes? → NO eliminar migraciones
- ¿Recrear todo desde cero? → Eliminar migraciones y tablas

**Migraciones relacionadas:**
- `add_supplier_invoices_table.py`
- `integrate_invoices_products.py`
- `add_cufe_dian_status_fields.py`
- `20260119_170057_add_extraction_quality.py`

---

## 🔧 Archivos a MODIFICAR

### 1. **Main.py** - Eliminar registro de router
```python
# ELIMINAR esta línea:
app.include_router(invoices_router, prefix="/invoices", tags=["Facturas CUFE"])
```

### 2. **Base Template** - Eliminar enlace del menú
```html
<!-- ELIMINAR del menú de navegación -->
<a href="/invoices">Facturas CUFE</a>
```

---

## 📋 Pasos de Ejecución

### Paso 1: Backup Completo ✅
- [x] Copiar archivos críticos a `BACKUP_INVOICES_OLD/`

### Paso 2: Eliminar Código Python
```bash
# Eliminar rutas
rm CODE/src/app/routes/invoices.py
rm CODE/src/app/routes/invoices_mockup.py

# Eliminar servicios
rm CODE/src/app/services/invoice_service.py
rm CODE/src/app/services/supplier_invoice_service.py
rm CODE/src/app/services/pdf_extractor_service.py
rm CODE/src/app/services/enhanced_pdf_extractor.py
```

### Paso 3: Eliminar Templates
```bash
# Eliminar todos los templates de invoices
rm -rf CODE/src/templates/invoices/
```

### Paso 4: Limpiar Imports en main.py
```python
# Eliminar imports relacionados
from app.routes.invoices import router as invoices_router
```

### Paso 5: (Opcional) Eliminar Tablas de BD
```sql
-- Solo si quieres recrear desde cero
DROP TABLE IF EXISTS supplier_invoices CASCADE;
DROP TABLE IF EXISTS invoices CASCADE;
DROP TABLE IF EXISTS invoice_items CASCADE;
DROP TABLE IF EXISTS cufe_records CASCADE;
```

---

## ✨ Estructura Nueva (Después de Limpieza)

```
CODE/src/app/routes/
  └── (sin invoices.py)

CODE/src/app/services/
  └── (sin invoice_service.py, supplier_invoice_service.py, etc.)

CODE/src/templates/
  └── (sin carpeta invoices/)
```

---

## 🚀 Próximos Pasos

1. **Definir nuevas funcionalidades** - ¿Qué quieres implementar?
2. **Crear nueva estructura** - Desde cero con mejores prácticas
3. **Implementar paso a paso** - Con testing desde el inicio

---

## ⚠️ ADVERTENCIAS

- ✅ Backup realizado - Puedes recuperar todo si es necesario
- ⚠️ La ruta `/invoices` dejará de funcionar
- ⚠️ Si hay datos en producción, considera migración
- ⚠️ Actualiza documentación y tests

---

## 🔄 Rollback (Si necesitas volver atrás)

```bash
# Restaurar desde backup
cp BACKUP_INVOICES_OLD/invoices_routes_backup.py CODE/src/app/routes/invoices.py
cp -r BACKUP_INVOICES_OLD/templates_invoices_backup/* CODE/src/templates/invoices/
# ... restaurar servicios
```
