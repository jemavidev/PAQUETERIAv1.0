# ✅ Checklist de Despliegue - Integración Fase 1

**Fecha:** 15 de Enero, 2026

---

## 📋 PRE-DESPLIEGUE

### 1. Verificar archivos modificados
- [ ] `CODE/src/app/services/s3_storage_service.py` - Métodos actualizados
- [ ] `CODE/src/app/routes/invoices.py` - Endpoint PDF mejorado
- [ ] `CODE/src/app/models/invoice.py` - Modelos actualizados
- [ ] `CODE/alembic/versions/integrate_invoices_products.py` - Migración creada

### 2. Verificar que no hay errores de sintaxis
```bash
cd CODE
python -m py_compile src/app/services/s3_storage_service.py
python -m py_compile src/app/routes/invoices.py
python -m py_compile src/app/models/invoice.py
python -m py_compile alembic/versions/integrate_invoices_products.py
```

---

## 🚀 DESPLIEGUE

### 3. Backup de base de datos (IMPORTANTE)
```bash
# PostgreSQL
pg_dump -U usuario -d nombre_bd > backup_antes_integracion_$(date +%Y%m%d_%H%M%S).sql

# O desde Docker
docker exec -t postgres_container pg_dump -U usuario nombre_bd > backup_antes_integracion_$(date +%Y%m%d_%H%M%S).sql
```
- [ ] Backup creado exitosamente

### 4. Ejecutar migración
```bash
cd CODE
alembic upgrade head
```
- [ ] Migración ejecutada sin errores
- [ ] Mensaje: "✅ Migración completada: Integración de facturas con productos"

### 5. Verificar migración
```bash
python test_integracion_fase1.py
```
- [ ] Todas las pruebas pasan
- [ ] Mensaje: "✅ TODAS LAS PRUEBAS COMPLETADAS"

### 6. Reiniciar servidor
```bash
# Docker
docker-compose restart web

# O uvicorn
# Ctrl+C y luego:
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```
- [ ] Servidor reiniciado sin errores
- [ ] No hay errores en los logs

---

## 🧪 PRUEBAS POST-DESPLIEGUE

### 7. Probar acceso a PDFs de supplier_invoices

**URL:** `https://staging.jemavi.co/invoices/supplier-invoices`

- [ ] La página carga correctamente
- [ ] Se muestran las facturas de proveedores
- [ ] Hacer clic en ícono PDF de una factura
- [ ] El PDF se abre correctamente en el navegador
- [ ] Probar con al menos 3 facturas diferentes

### 8. Verificar que facturas existentes no se rompieron

**URL:** `https://staging.jemavi.co/invoices`

- [ ] Dashboard de facturas carga correctamente
- [ ] Se muestran las facturas procesadas
- [ ] Los totales se calculan correctamente
- [ ] No hay errores en consola del navegador

### 9. Verificar que se pueden subir nuevas facturas

**URL:** `https://staging.jemavi.co/invoices/supplier-invoices`

- [ ] Hacer clic en "Subir Factura"
- [ ] Seleccionar un PDF de prueba
- [ ] La factura se sube correctamente
- [ ] Se extrae el CUFE (si existe)
- [ ] El PDF es accesible después de subir

### 10. Verificar logs del servidor

```bash
# Docker
docker logs -f container_name

# O revisar archivo de logs
tail -f logs/app.log
```

- [ ] No hay errores relacionados con la migración
- [ ] No hay errores de foreign keys
- [ ] Los logs de S3 muestran las rutas correctas

---

## 🔍 VERIFICACIÓN DE BASE DE DATOS

### 11. Verificar columnas nuevas en `invoices`

```sql
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'invoices'
AND column_name IN ('buyer_nit', 'buyer_razon_social', 'buyer_direccion', 'is_papyrus_buyer', 'supplier_invoice_id');
```

- [ ] 5 columnas encontradas
- [ ] Todas son nullable

### 12. Verificar columnas nuevas en `invoice_items`

```sql
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'invoice_items'
AND column_name IN ('product_id', 'matched_with_catalog', 'match_confidence', 'match_method');
```

- [ ] 4 columnas encontradas
- [ ] Todas son nullable

### 13. Verificar foreign keys

```sql
SELECT
    tc.constraint_name,
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
AND (
    (tc.table_name = 'invoices' AND kcu.column_name = 'supplier_invoice_id')
    OR
    (tc.table_name = 'invoice_items' AND kcu.column_name = 'product_id')
);
```

- [ ] FK `invoices.supplier_invoice_id` → `supplier_invoices.id` existe
- [ ] FK `invoice_items.product_id` → `products.id` existe

---

## 📊 PRUEBAS DE INTEGRACIÓN

### 14. Probar flujo completo (si hay datos)

Si tienes una factura de proveedor con CUFE que ya fue procesada:

- [ ] Ir a `/invoices/supplier-invoices`
- [ ] Buscar una factura con estado "PROCESSED"
- [ ] Verificar que tiene un `processed_invoice_id`
- [ ] Hacer clic en el número de factura procesada
- [ ] Verificar que se abre la factura en `/invoices`
- [ ] Verificar que la factura tiene el campo `supplier_invoice_id` poblado

### 15. Verificar que productos existen en catálogo

```sql
SELECT COUNT(*) FROM products WHERE activo = true;
```

- [ ] Hay productos en el catálogo
- [ ] Si no hay productos, sincronizar desde DynamiaERP

---

## ⚠️ ROLLBACK (Si algo sale mal)

### En caso de error crítico:

```bash
# 1. Revertir migración
cd CODE
alembic downgrade -1

# 2. Restaurar backup
psql -U usuario -d nombre_bd < backup_antes_integracion_YYYYMMDD_HHMMSS.sql

# 3. Reiniciar servidor
docker-compose restart web
```

---

## ✅ CONFIRMACIÓN FINAL

### Todos los checks deben estar marcados:

- [ ] Backup creado
- [ ] Migración ejecutada
- [ ] Pruebas automatizadas pasan
- [ ] Servidor reiniciado
- [ ] PDFs accesibles
- [ ] Facturas existentes funcionan
- [ ] Se pueden subir nuevas facturas
- [ ] No hay errores en logs
- [ ] Columnas nuevas en BD
- [ ] Foreign keys creadas
- [ ] Flujo completo funciona (si aplica)

---

## 📝 NOTAS

**Fecha de despliegue:** _______________

**Ejecutado por:** _______________

**Problemas encontrados:**
- 
- 
- 

**Soluciones aplicadas:**
- 
- 
- 

**Tiempo total:** _______________

---

## 🎯 PRÓXIMOS PASOS

Una vez completado este checklist:

1. [ ] Documentar cualquier problema encontrado
2. [ ] Notificar al equipo que la Fase 1 está completa
3. [ ] Planificar Fase 2: Extracción de datos del comprador
4. [ ] Planificar Fase 3: Matching manual de productos
5. [ ] Planificar Fase 4: Vista de trazabilidad completa

---

**Estado:** ⏳ PENDIENTE DE EJECUCIÓN
