# 🔧 Solución: Facturas Duplicadas en la Tabla

## 🐛 Problema Identificado

En la interfaz de facturas se están mostrando múltiples filas duplicadas con el mismo CUFE (ejemplo: "b6613bfc1d5c5624..." aparece muchas veces).

### Causas:

1. **Bug en `refreshSingleInvoice()`**: La función usaba `forEach` y reemplazaba TODAS las filas que coincidían con el criterio, creando duplicados
2. **Datos duplicados en BD**: Posiblemente hay registros duplicados en la tabla `invoices_v2`

## ✅ Soluciones Implementadas

### 1. Fix en el Frontend (COMPLETADO)

**Archivo**: `CODE/src/templates/invoices_v2/facturas.html`

**Cambios**:
- ✅ Cambiado `forEach` por `for...of` con `break` para reemplazar solo UNA fila
- ✅ Cambiado a recargar toda la tabla después de asociar CUFE (más seguro)

```javascript
// ANTES (causaba duplicados)
rows.forEach(row => {
    // ... reemplazaba TODAS las filas que coincidían
});

// DESPUÉS (solo reemplaza una)
for (let row of rows) {
    // ... reemplaza solo la primera
    break; // IMPORTANTE
}

// MEJOR AÚN: Recargar toda la tabla
await loadInvoices();
```

### 2. Limpiar Duplicados en Base de Datos

**Opción A: Script SQL Manual**

Archivo: `CODE/fix_duplicate_invoices.sql`

```sql
-- Ver duplicados
SELECT cufe, COUNT(*) as count
FROM invoices_v2
GROUP BY cufe
HAVING COUNT(*) > 1;

-- Eliminar duplicados (mantiene el más reciente)
DELETE FROM invoices_v2
WHERE id NOT IN (
    SELECT MAX(id)
    FROM invoices_v2
    GROUP BY cufe
);
```

**Opción B: Script Bash Interactivo** (RECOMENDADO)

Archivo: `CODE/fix_duplicate_invoices_simple.sh`

```bash
# Ejecutar desde la carpeta CODE
./fix_duplicate_invoices_simple.sh
```

Este script:
1. Muestra los duplicados encontrados
2. Pregunta si deseas eliminarlos
3. Elimina duplicados manteniendo el registro más reciente
4. Verifica el resultado

## 📋 Pasos para Resolver

### Paso 1: Verificar si hay duplicados

```bash
cd CODE
./fix_duplicate_invoices_simple.sh
```

### Paso 2: Si hay duplicados, el script preguntará si deseas eliminarlos

Responde `s` para eliminar o `n` para cancelar.

### Paso 3: Recargar la página

Después de limpiar los duplicados, recarga la página de facturas (F5) y los duplicados deberían desaparecer.

## 🔍 Verificación Manual

Si prefieres verificar manualmente en la base de datos:

```bash
# Conectar a la base de datos
docker-compose exec db psql -U paquetex_user -d paquetex_db

# Ver duplicados
SELECT cufe, COUNT(*) as count
FROM invoices_v2
GROUP BY cufe
HAVING COUNT(*) > 1
ORDER BY count DESC;

# Ver total de facturas
SELECT COUNT(*) FROM invoices_v2;
```

## 🎯 Resultado Esperado

Después de aplicar las soluciones:

- ✅ No más filas duplicadas en la interfaz
- ✅ Cada CUFE aparece solo UNA vez en la base de datos
- ✅ La asociación de CUFE recarga toda la tabla (más seguro)
- ✅ No se crean nuevos duplicados

## 🚨 Prevención Futura

El código ya fue corregido para prevenir duplicados futuros:

1. ✅ La función `refreshSingleInvoice()` usa `break` para reemplazar solo una fila
2. ✅ La asociación de CUFE recarga toda la tabla en lugar de actualizar una fila
3. ✅ Se puede agregar un índice UNIQUE en la columna `cufe` para prevenir duplicados en BD

### Agregar Índice UNIQUE (Opcional)

```sql
-- Esto previene duplicados a nivel de base de datos
ALTER TABLE invoices_v2 ADD CONSTRAINT invoices_v2_cufe_unique UNIQUE (cufe);
```

## 📝 Notas

- Los cambios en el frontend ya están aplicados
- Solo falta limpiar los duplicados existentes en la base de datos
- El script es seguro: mantiene el registro más reciente de cada CUFE
- Se recomienda hacer un backup antes de ejecutar el script de limpieza
