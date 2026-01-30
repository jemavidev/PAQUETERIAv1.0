# 🗄️ Opciones para Limpiar Base de Datos - Sistema de Facturas

**Situación Actual:** El código de invoices fue eliminado, pero las tablas en la base de datos siguen existiendo.

---

## 📊 Tablas Existentes en la Base de Datos

Según tu captura, estas tablas están en la BD:

1. **`supplier_invoices`** - Facturas de proveedores subidas
2. **`invoices`** - Facturas procesadas
3. **`invoice_items`** - Items/productos de facturas
4. **`invoice_irregularities`** - Irregularidades detectadas
5. **`invoice_rejected_files`** - Archivos rechazados
6. **`cufe_records`** - Registros de CUFE

---

## 🎯 Opciones Disponibles

### **Opción 1: NO HACER NADA (Mantener Tablas)**

**✅ Ventajas:**
- Conservas todos los datos existentes
- Puedes acceder a los datos si los necesitas
- Fácil de integrar con nuevo código

**❌ Desventajas:**
- Ocupan espacio en la BD
- Pueden causar confusión
- Migraciones de Alembic pueden fallar si intentas recrearlas

**📝 Cuándo usar:**
- Tienes datos importantes en producción
- Quieres reutilizar la estructura existente
- No estás seguro de qué hacer

---

### **Opción 2: VACIAR TABLAS (TRUNCATE)**

**Qué hace:** Elimina todos los datos pero mantiene la estructura de las tablas.

**✅ Ventajas:**
- Mantiene la estructura (columnas, índices, foreign keys)
- Rápido de ejecutar
- Fácil de revertir (solo necesitas los datos)

**❌ Desventajas:**
- Pierdes todos los datos (irreversible sin backup)
- Las tablas siguen ocupando espacio (mínimo)

**📝 Cuándo usar:**
- Quieres empezar con datos limpios
- Vas a reutilizar la misma estructura
- No tienes datos importantes

**🔧 Cómo ejecutar:**

```bash
# Opción A: Script Python interactivo
python cleanup_invoices_database.py
# Selecciona opción 3 o 5

# Opción B: SQL directo
psql -U usuario -d paquetex
```

```sql
TRUNCATE TABLE invoice_rejected_files CASCADE;
TRUNCATE TABLE invoice_irregularities CASCADE;
TRUNCATE TABLE invoice_items CASCADE;
TRUNCATE TABLE invoices CASCADE;
TRUNCATE TABLE supplier_invoices CASCADE;
TRUNCATE TABLE cufe_records CASCADE;
```

---

### **Opción 3: ELIMINAR TABLAS (DROP)**

**Qué hace:** Elimina completamente las tablas (estructura y datos).

**✅ Ventajas:**
- Limpieza total
- Libera espacio en la BD
- Puedes recrear desde cero con nuevas migraciones

**❌ Desventajas:**
- Pierdes estructura y datos (irreversible sin backup completo)
- Debes eliminar también las migraciones de Alembic
- Más trabajo para recrear

**📝 Cuándo usar:**
- Vas a cambiar completamente la estructura
- No necesitas los datos ni la estructura actual
- Quieres empezar 100% desde cero

**🔧 Cómo ejecutar:**

```bash
# Opción A: Script Python interactivo
python cleanup_invoices_database.py
# Selecciona opción 4 o 6

# Opción B: SQL directo
psql -U usuario -d paquetex
```

```sql
DROP TABLE IF EXISTS invoice_rejected_files CASCADE;
DROP TABLE IF EXISTS invoice_irregularities CASCADE;
DROP TABLE IF EXISTS invoice_items CASCADE;
DROP TABLE IF EXISTS invoices CASCADE;
DROP TABLE IF EXISTS supplier_invoices CASCADE;
DROP TABLE IF EXISTS cufe_records CASCADE;
```

**⚠️ IMPORTANTE:** Si haces DROP, también debes eliminar las migraciones:

```bash
rm CODE/alembic/versions/add_supplier_invoices_table.py
rm CODE/alembic/versions/integrate_invoices_products.py
rm CODE/alembic/versions/add_cufe_dian_status_fields.py
rm CODE/alembic/versions/20260119_170057_add_extraction_quality.py
```

---

### **Opción 4: BACKUP + ELIMINAR (Recomendado si tienes datos)**

**Qué hace:** Hace backup de los datos antes de eliminar.

**✅ Ventajas:**
- Seguridad total
- Puedes restaurar si es necesario
- Limpieza completa

**❌ Desventajas:**
- Toma más tiempo
- Genera archivos de backup

**🔧 Cómo ejecutar:**

```bash
# Script Python (hace backup automático)
python cleanup_invoices_database.py
# Selecciona opción 5 (backup + truncate) o 6 (backup + drop)
```

**O manualmente:**

```sql
-- 1. Crear tablas de backup
CREATE TABLE supplier_invoices_backup AS SELECT * FROM supplier_invoices;
CREATE TABLE invoices_backup AS SELECT * FROM invoices;
CREATE TABLE invoice_items_backup AS SELECT * FROM invoice_items;
CREATE TABLE invoice_irregularities_backup AS SELECT * FROM invoice_irregularities;
CREATE TABLE invoice_rejected_files_backup AS SELECT * FROM invoice_rejected_files;
CREATE TABLE cufe_records_backup AS SELECT * FROM cufe_records;

-- 2. Verificar backup
SELECT COUNT(*) FROM supplier_invoices_backup;

-- 3. Eliminar tablas originales
DROP TABLE IF EXISTS invoice_rejected_files CASCADE;
DROP TABLE IF EXISTS invoice_irregularities CASCADE;
DROP TABLE IF EXISTS invoice_items CASCADE;
DROP TABLE IF EXISTS invoices CASCADE;
DROP TABLE IF EXISTS supplier_invoices CASCADE;
DROP TABLE IF EXISTS cufe_records CASCADE;
```

---

## 🚀 Recomendación Según tu Caso

### **Si NO tienes datos importantes en producción:**
→ **Opción 3: ELIMINAR TABLAS (DROP)**
- Limpieza total
- Empiezas desde cero
- Más limpio para desarrollo

### **Si tienes datos en producción:**
→ **Opción 4: BACKUP + ELIMINAR**
- Seguridad primero
- Puedes restaurar si es necesario

### **Si vas a reutilizar la estructura:**
→ **Opción 1: NO HACER NADA**
- Mantén las tablas
- Crea nuevo código que las use

### **Si solo quieres limpiar datos de prueba:**
→ **Opción 2: VACIAR TABLAS (TRUNCATE)**
- Rápido y simple
- Mantiene estructura

---

## 📋 Checklist de Limpieza Completa

Si decides hacer limpieza total (DROP):

- [ ] **1. Backup de datos** (si es necesario)
  ```bash
  python cleanup_invoices_database.py  # Opción 2
  ```

- [ ] **2. Eliminar tablas de BD**
  ```bash
  python cleanup_invoices_database.py  # Opción 4 o 6
  ```

- [ ] **3. Eliminar migraciones de Alembic**
  ```bash
  rm CODE/alembic/versions/add_supplier_invoices_table.py
  rm CODE/alembic/versions/integrate_invoices_products.py
  rm CODE/alembic/versions/add_cufe_dian_status_fields.py
  rm CODE/alembic/versions/20260119_170057_add_extraction_quality.py
  ```

- [ ] **4. Eliminar modelos (opcional)**
  ```bash
  # Si no vas a reutilizar los modelos
  rm CODE/src/app/models/invoice.py
  # O comentar las clases que no necesites
  ```

- [ ] **5. Verificar que todo funciona**
  ```bash
  docker-compose restart
  curl http://localhost:8000/health
  ```

---

## 🔄 Cómo Restaurar (Si hiciste backup)

```sql
-- Restaurar desde tablas de backup
INSERT INTO supplier_invoices SELECT * FROM supplier_invoices_backup;
INSERT INTO invoices SELECT * FROM invoices_backup;
INSERT INTO invoice_items SELECT * FROM invoice_items_backup;
INSERT INTO invoice_irregularities SELECT * FROM invoice_irregularities_backup;
INSERT INTO invoice_rejected_files SELECT * FROM invoice_rejected_files_backup;
INSERT INTO cufe_records SELECT * FROM cufe_records_backup;
```

---

## 📞 ¿Qué Opción Eliges?

**Dime:**
1. ¿Tienes datos importantes en las tablas?
2. ¿Vas a reutilizar la estructura existente?
3. ¿Prefieres empezar 100% desde cero?

**Y yo ejecuto la opción que prefieras.** 🎯

---

## 📄 Archivos Creados

- **`cleanup_invoices_database.py`** - Script Python interactivo
- **`cleanup_invoices_tables.sql`** - Script SQL manual
- **`DATABASE_CLEANUP_OPTIONS.md`** - Este documento
