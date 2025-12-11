# 🗑️ Plan de Limpieza de Base de Datos

## 📋 Resumen de Operaciones

### Objetivo 1: Eliminar Clientes de Prueba
Eliminar clientes con los siguientes teléfonos:
- `+573001234567`
- `+573002596319`
- `+573008103849`
- `+573008398365`

### Objetivo 2: Eliminar Todos los Paquetes Cancelados
Eliminar todos los paquetes con estado `CANCELADO`

---

## 🔍 Análisis de Dependencias

### Tablas Relacionadas con `customers`

1. **`packages`** - Paquetes del cliente
   - Relación: `customer_id` → `customers.id`
   - Cascade: `all, delete-orphan` ✅ (se eliminan automáticamente)

2. **`package_announcements_new`** - Anuncios del cliente
   - Relación: `customer_id` → `customers.id`
   - Cascade: `all, delete-orphan` ✅ (se eliminan automáticamente)

3. **`messages`** - Mensajes del cliente
   - Relación: `customer_id` → `customers.id`
   - Cascade: `all, delete-orphan` ✅ (se eliminan automáticamente)

4. **`notifications`** - Notificaciones del cliente
   - Relación: `customer_id` → `customers.id`
   - Cascade: `all, delete-orphan` ✅ (se eliminan automáticamente)

5. **`customer_preferences`** - Preferencias del cliente
   - Relación: `customer_id` → `customers.id`
   - Cascade: `CASCADE` (ondelete) ✅ (se eliminan automáticamente)

### Tablas Relacionadas con `packages`

1. **`package_announcements_new`** - Anuncios vinculados
   - Relación: `package_id` → `packages.id`
   - Cascade: NO definido ⚠️ (requiere eliminación manual)

2. **`package_history`** - Historial del paquete
   - Relación: `package_id` → `packages.id`
   - Cascade: NO definido ⚠️ (requiere eliminación manual)

3. **`package_event`** - Eventos del paquete
   - Relación: `package_id` → `packages.id`
   - Cascade: NO definido ⚠️ (requiere eliminación manual)

4. **`file_uploads`** - Archivos del paquete
   - Relación: `package_id` → `packages.id`
   - Cascade: NO definido ⚠️ (requiere eliminación manual)

5. **`messages`** - Mensajes del paquete
   - Relación: `package_id` → `packages.id`
   - Cascade: NO definido ⚠️ (requiere eliminación manual)

6. **`notifications`** - Notificaciones del paquete
   - Relación: `package_id` → `packages.id`
   - Cascade: NO definido ⚠️ (requiere eliminación manual)

---

## 📝 Plan de Ejecución

### Operación 1: Eliminar Clientes de Prueba

**Orden de eliminación (de más dependiente a menos):**

```sql
-- 1. Eliminar eventos de paquetes de estos clientes
DELETE FROM package_events 
WHERE customer_id IN (
    SELECT id FROM customers 
    WHERE phone IN ('+573001234567', '+573002596319', '+573008103849', '+573008398365')
);

-- 2. Eliminar historial de paquetes de estos clientes
DELETE FROM package_history 
WHERE package_id IN (
    SELECT id FROM packages 
    WHERE customer_id IN (
        SELECT id FROM customers 
        WHERE phone IN ('+573001234567', '+573002596319', '+573008103849', '+573008398365')
    )
);

-- 3. Eliminar archivos de paquetes de estos clientes
DELETE FROM file_uploads 
WHERE package_id IN (
    SELECT id FROM packages 
    WHERE customer_id IN (
        SELECT id FROM customers 
        WHERE phone IN ('+573001234567', '+573002596319', '+573008103849', '+573008398365')
    )
);

-- 4. Eliminar notificaciones de paquetes de estos clientes
DELETE FROM notifications 
WHERE package_id IN (
    SELECT id FROM packages 
    WHERE customer_id IN (
        SELECT id FROM customers 
        WHERE phone IN ('+573001234567', '+573002596319', '+573008103849', '+573008398365')
    )
);

-- 5. Eliminar mensajes de paquetes de estos clientes
DELETE FROM messages 
WHERE package_id IN (
    SELECT id FROM packages 
    WHERE customer_id IN (
        SELECT id FROM customers 
        WHERE phone IN ('+573001234567', '+573002596319', '+573008103849', '+573008398365')
    )
);

-- 6. Actualizar anuncios (desvincular de paquetes)
UPDATE package_announcements_new 
SET package_id = NULL 
WHERE package_id IN (
    SELECT id FROM packages 
    WHERE customer_id IN (
        SELECT id FROM customers 
        WHERE phone IN ('+573001234567', '+573002596319', '+573008103849', '+573008398365')
    )
);

-- 7. Eliminar paquetes de estos clientes
DELETE FROM packages 
WHERE customer_id IN (
    SELECT id FROM customers 
    WHERE phone IN ('+573001234567', '+573002596319', '+573008103849', '+573008398365')
);

-- 8. Eliminar clientes (esto eliminará automáticamente por cascade):
--    - package_announcements_new (customer_id)
--    - messages (customer_id)
--    - notifications (customer_id)
--    - customer_preferences
DELETE FROM customers 
WHERE phone IN ('+573001234567', '+573002596319', '+573008103849', '+573008398365');
```

### Operación 2: Eliminar Todos los Paquetes Cancelados

**Orden de eliminación:**

```sql
-- 1. Eliminar eventos de paquetes cancelados
DELETE FROM package_events 
WHERE package_id IN (
    SELECT id FROM packages WHERE status = 'CANCELADO'
);

-- 2. Eliminar historial de paquetes cancelados
DELETE FROM package_history 
WHERE package_id IN (
    SELECT id FROM packages WHERE status = 'CANCELADO'
);

-- 3. Eliminar archivos de paquetes cancelados
DELETE FROM file_uploads 
WHERE package_id IN (
    SELECT id FROM packages WHERE status = 'CANCELADO'
);

-- 4. Eliminar notificaciones de paquetes cancelados
DELETE FROM notifications 
WHERE package_id IN (
    SELECT id FROM packages WHERE status = 'CANCELADO'
);

-- 5. Eliminar mensajes de paquetes cancelados
DELETE FROM messages 
WHERE package_id IN (
    SELECT id FROM packages WHERE status = 'CANCELADO'
);

-- 6. Actualizar anuncios (desvincular de paquetes cancelados)
UPDATE package_announcements_new 
SET package_id = NULL 
WHERE package_id IN (
    SELECT id FROM packages WHERE status = 'CANCELADO'
);

-- 7. Eliminar paquetes cancelados
DELETE FROM packages WHERE status = 'CANCELADO';
```

---

## 🔢 Estimación de Registros a Eliminar

### Consultas de Verificación (ejecutar ANTES de eliminar):

```sql
-- Contar clientes a eliminar
SELECT COUNT(*) as total_clientes
FROM customers 
WHERE phone IN ('+573001234567', '+573002596319', '+573008103849', '+573008398365');

-- Contar paquetes de estos clientes
SELECT COUNT(*) as total_paquetes_clientes
FROM packages 
WHERE customer_id IN (
    SELECT id FROM customers 
    WHERE phone IN ('+573001234567', '+573002596319', '+573008103849', '+573008398365')
);

-- Contar anuncios de estos clientes
SELECT COUNT(*) as total_anuncios_clientes
FROM package_announcements_new 
WHERE customer_id IN (
    SELECT id FROM customers 
    WHERE phone IN ('+573001234567', '+573002596319', '+573008103849', '+573008398365')
);

-- Contar paquetes cancelados
SELECT COUNT(*) as total_paquetes_cancelados
FROM packages 
WHERE status = 'CANCELADO';

-- Contar eventos de paquetes cancelados
SELECT COUNT(*) as total_eventos_cancelados
FROM package_events 
WHERE package_id IN (
    SELECT id FROM packages WHERE status = 'CANCELADO'
);

-- Contar historial de paquetes cancelados
SELECT COUNT(*) as total_historial_cancelados
FROM package_history 
WHERE package_id IN (
    SELECT id FROM packages WHERE status = 'CANCELADO'
);
```

---

## ⚠️ Advertencias y Consideraciones

### 1. Backup Obligatorio
**ANTES de ejecutar cualquier eliminación:**
```bash
# PostgreSQL
pg_dump -U usuario -d nombre_bd > backup_antes_limpieza_$(date +%Y%m%d_%H%M%S).sql

# O desde el contenedor Docker
docker exec -t postgres_container pg_dump -U usuario nombre_bd > backup_antes_limpieza_$(date +%Y%m%d_%H%M%S).sql
```

### 2. Archivos en S3
Los archivos en S3 (fotos de paquetes) NO se eliminarán automáticamente. Necesitarás:
- Listar los archivos de los paquetes a eliminar
- Eliminarlos manualmente de S3 o dejarlos (ocupan poco espacio)

### 3. Transacciones
Todas las operaciones deben ejecutarse dentro de una transacción:
```sql
BEGIN;
-- Ejecutar todas las operaciones aquí
-- Si algo falla: ROLLBACK;
-- Si todo está bien: COMMIT;
```

### 4. Orden de Ejecución
**MUY IMPORTANTE:** Ejecutar en el orden especificado para evitar errores de foreign key.

---

## 🚀 Script Python Automatizado

Puedo crear un script Python que:
1. ✅ Hace backup automático
2. ✅ Ejecuta las consultas de verificación
3. ✅ Muestra cuántos registros se eliminarán
4. ✅ Pide confirmación
5. ✅ Ejecuta las eliminaciones en orden correcto
6. ✅ Usa transacciones (rollback automático si hay error)
7. ✅ Genera reporte de lo eliminado

---

## 📊 Resumen de Tablas Afectadas

| Tabla | Operación 1 (Clientes) | Operación 2 (Cancelados) |
|-------|------------------------|--------------------------|
| `customers` | ✅ Eliminar | ❌ No afectado |
| `packages` | ✅ Eliminar | ✅ Eliminar |
| `package_announcements_new` | ✅ Desvincular/Eliminar | ✅ Desvincular |
| `package_events` | ✅ Eliminar | ✅ Eliminar |
| `package_history` | ✅ Eliminar | ✅ Eliminar |
| `file_uploads` | ✅ Eliminar | ✅ Eliminar |
| `messages` | ✅ Eliminar | ✅ Eliminar |
| `notifications` | ✅ Eliminar | ✅ Eliminar |
| `customer_preferences` | ✅ Eliminar (cascade) | ❌ No afectado |

---

## ✅ Recomendación Final

**Opción 1: Script SQL Manual**
- Ejecutar los SQL en orden
- Más control manual
- Requiere más atención

**Opción 2: Script Python Automatizado** ⭐ RECOMENDADO
- Más seguro (transacciones automáticas)
- Backup automático
- Confirmación antes de eliminar
- Reporte detallado
- Rollback automático si hay error

---

## 🎯 Próximo Paso

**¿Qué prefieres?**

1. **SQL Manual**: Te proporciono los scripts SQL completos para ejecutar manualmente
2. **Script Python**: Creo un script automatizado que hace todo de forma segura

**Ambas opciones incluyen:**
- ✅ Backup automático
- ✅ Verificación previa
- ✅ Confirmación requerida
- ✅ Transacciones seguras
- ✅ Reporte de resultados

---

**Fecha**: 11 de Diciembre, 2025
**Estado**: ⏳ Esperando autorización
