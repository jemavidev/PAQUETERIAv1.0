# 📖 Instrucciones para Migración de Productos

## 🚀 Inicio Rápido

### 1. Prueba Rápida (Recomendado primero)
```bash
cd CODE
source .venv/bin/activate
python3 quick_test_migration.py
```

Esto procesará 3 facturas en modo DRY-RUN (sin cambios en DB) para validar que todo funciona.

---

## 📊 Comandos Disponibles

### Modo DRY-RUN (Prueba sin cambios)

```bash
# Probar con 3 facturas (rápido)
python3 quick_test_migration.py

# Probar con 10 facturas
python3 migrate_reprocess_products.py --dry-run 10

# Probar con 50 facturas
python3 migrate_reprocess_products.py --dry-run 50

# Probar con TODAS las facturas (solo ver estadísticas)
python3 migrate_reprocess_products.py --dry-run
```

### Modo PRODUCCIÓN (Actualiza DB)

⚠️ **IMPORTANTE**: Hacer backup de la base de datos primero!

```bash
# Migrar 10 facturas (prueba pequeña)
python3 migrate_reprocess_products.py 10

# Migrar 50 facturas
python3 migrate_reprocess_products.py 50

# Migrar TODAS las facturas (requiere confirmación)
python3 migrate_reprocess_products.py
```

---

## 📋 Proceso Recomendado

### Paso 1: Validación Inicial
```bash
python3 quick_test_migration.py
```
**Revisar:**
- ✅ Que se descargan archivos de S3
- ✅ Que se extraen productos
- ✅ Que los datos son correctos

### Paso 2: Prueba con más facturas
```bash
python3 migrate_reprocess_products.py --dry-run 10
```
**Revisar:**
- ✅ Estadísticas de éxito
- ✅ Porcentaje de productos completos
- ✅ Errores (si hay)

### Paso 3: Backup de Base de Datos
```bash
# Hacer backup antes de modificar
pg_dump paquetex > backup_antes_migracion_$(date +%Y%m%d_%H%M%S).sql
```

### Paso 4: Migración Parcial
```bash
python3 migrate_reprocess_products.py 10
```
**Confirmar escribiendo "SI"**

**Verificar en la aplicación:**
- ✅ Ir al tab PRODUCTOS
- ✅ Ver que aparecen productos
- ✅ Ver que tienen todos los datos

### Paso 5: Migración Completa
```bash
python3 migrate_reprocess_products.py
```
**Confirmar escribiendo "SI"**

---

## 📊 Interpretando Resultados

### Ejemplo de Salida:
```
📊 RESUMEN DE MIGRACIÓN
================================================================================

Total facturas: 50
✅ Procesadas exitosamente: 48
❌ Errores: 2

📦 Con productos extraídos: 45
⚠️  Sin productos: 3

Total productos extraídos: 1,234
   ✅ Con datos completos: 1,180
   ⚠️  Con datos parciales: 54
   📈 Porcentaje completos: 95.6%
```

### ¿Qué significa?

- **Procesadas exitosamente**: Facturas que se descargaron y parsearon sin errores
- **Errores**: Facturas que fallaron (archivo no disponible, error de parsing, etc.)
- **Con productos extraídos**: Facturas de las cuales se extrajeron productos
- **Sin productos**: Facturas que no tienen productos (puede ser normal para facturas de servicios)
- **Productos completos**: Tienen código, cantidad, precio, etc.
- **Productos parciales**: Solo tienen código y descripción (sin precio/cantidad)

### ¿Qué es un buen resultado?

- ✅ **Excelente**: >90% procesadas, >85% con productos completos
- ⚠️ **Aceptable**: >80% procesadas, >70% con productos completos
- ❌ **Revisar**: <80% procesadas o <70% con productos completos

---

## 🔧 Solución de Problemas

### Error: "No module named 'app'"
```bash
# Asegúrate de estar en el directorio CODE
cd CODE
source .venv/bin/activate
```

### Error: "No se pudo descargar el archivo"
- Verificar credenciales de AWS/S3
- Verificar que el archivo existe en S3
- Verificar conexión a internet

### Error: "No se encontraron facturas con archivo DIAN"
- Verificar que hay facturas en la base de datos
- Verificar que tienen `archivo_dian_s3_key` no nulo

### Productos parciales (sin precio/cantidad)
- Normal en algunos formatos de PDF
- El parser hace lo mejor posible
- Revisar el PDF manualmente para ver si tiene esos datos

---

## 🎯 Después de la Migración

### 1. Verificar en la UI
- Ir a `/invoices/productos`
- Buscar productos
- Ver que tienen todos los datos
- Probar el historial de productos

### 2. Verificar en la Base de Datos
```sql
-- Ver total de productos
SELECT COUNT(*) FROM invoice_products_v2;

-- Ver productos con datos completos
SELECT COUNT(*) FROM invoice_products_v2 
WHERE cantidad IS NOT NULL 
  AND precio_unitario IS NOT NULL;

-- Ver productos por factura
SELECT cufe, COUNT(*) as productos
FROM invoice_products_v2
GROUP BY cufe
ORDER BY productos DESC
LIMIT 10;
```

### 3. Probar Funcionalidades
- ✅ Búsqueda de productos
- ✅ Historial de compras
- ✅ Filtros
- ✅ Paginación

---

## 📞 Soporte

Si encuentras problemas:

1. **Revisar logs** - El script muestra información detallada
2. **Ejecutar en modo DRY-RUN** - Para ver qué pasaría sin modificar DB
3. **Probar con pocas facturas** - Usar límite pequeño para debugging
4. **Revisar PDFs manualmente** - Ver si el formato es diferente

---

## ✅ Checklist Final

Antes de considerar la migración completa:

- [ ] Ejecuté `quick_test_migration.py` exitosamente
- [ ] Revisé los resultados del dry-run
- [ ] Hice backup de la base de datos
- [ ] Probé con 10 facturas en modo producción
- [ ] Verifiqué productos en la UI
- [ ] Los resultados son satisfactorios (>85% completos)
- [ ] Estoy listo para migración completa

---

**¡Listo para empezar!** 🚀

Ejecuta: `python3 quick_test_migration.py`
