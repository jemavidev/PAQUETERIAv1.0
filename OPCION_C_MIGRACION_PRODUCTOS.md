# ✅ OPCIÓN C: Script de Migración de Productos - COMPLETADO

## 🎯 Objetivo
Crear un script que reprocese todas las facturas existentes que tienen archivo DIAN para extraer productos con el parser mejorado.

---

## 📋 Scripts Creados

### 1. `migrate_reprocess_products.py` - Script Principal

**Funcionalidades:**
- ✅ Busca facturas con archivo DIAN en S3
- ✅ Descarga archivos PDF de S3
- ✅ Parsea con el parser mejorado
- ✅ Extrae productos con todos los datos
- ✅ Actualiza base de datos (elimina antiguos, inserta nuevos)
- ✅ Genera estadísticas detalladas
- ✅ Modo DRY-RUN para pruebas sin modificar DB
- ✅ Soporte para límite de facturas
- ✅ Logging detallado con progreso

**Uso:**
```bash
# Modo DRY-RUN (prueba sin cambios)
python3 migrate_reprocess_products.py --dry-run

# Modo DRY-RUN con límite de 10 facturas
python3 migrate_reprocess_products.py --dry-run 10

# Migración real de 10 facturas
python3 migrate_reprocess_products.py 10

# Migración de TODAS las facturas (requiere confirmación)
python3 migrate_reprocess_products.py
```

### 2. `quick_test_migration.py` - Prueba Rápida

**Funcionalidades:**
- ✅ Prueba rápida con 3 facturas
- ✅ Siempre en modo DRY-RUN
- ✅ Muestra ejemplo de resultados
- ✅ Útil para validar que todo funciona

**Uso:**
```bash
python3 quick_test_migration.py
```

---

## 🔧 Características Técnicas

### Clase `ProductMigration`

#### Métodos principales:

1. **`get_facturas_con_dian(limit)`**
   - Obtiene facturas que tienen `archivo_dian_s3_key`
   - Soporta límite opcional
   - Retorna lista de objetos `InvoiceV2`

2. **`process_factura(factura)`**
   - Descarga archivo PDF de S3
   - Parsea con `PDFParserService.parse_dian_document()`
   - Extrae productos
   - Analiza calidad (completos vs parciales)
   - Actualiza DB (si no es dry-run)
   - Retorna True/False según éxito

3. **`run(limit)`**
   - Ejecuta migración completa
   - Procesa todas las facturas
   - Genera estadísticas
   - Imprime resumen final

4. **`print_summary()`**
   - Muestra resumen detallado
   - Estadísticas de éxito/error
   - Productos extraídos
   - Porcentaje de completitud

### Estadísticas Recopiladas

```python
stats = {
    'total_facturas': 0,        # Total a procesar
    'procesadas': 0,            # Procesadas exitosamente
    'con_productos': 0,         # Con productos extraídos
    'sin_productos': 0,         # Sin productos
    'errores': 0,               # Errores de procesamiento
    'productos_totales': 0,     # Total productos extraídos
    'productos_completos': 0,   # Con todos los datos
    'productos_parciales': 0,   # Con datos incompletos
}
```

---

## 🚀 Proceso de Migración

### Flujo del Script:

```
1. Buscar facturas con archivo DIAN
   ↓
2. Para cada factura:
   ├─ Descargar PDF de S3
   ├─ Parsear con parser mejorado
   ├─ Extraer productos
   ├─ Analizar calidad de datos
   └─ Actualizar DB (si no es dry-run)
   ↓
3. Generar resumen con estadísticas
```

### Actualización de Base de Datos:

```sql
-- 1. Eliminar productos anteriores
DELETE FROM invoice_products_v2 WHERE cufe = ?

-- 2. Insertar productos nuevos
INSERT INTO invoice_products_v2 (
    cufe, linea_numero, codigo_producto, descripcion,
    cantidad, unidad_medida, precio_unitario,
    iva_porcentaje, total_item, fecha_compra, datos_raw
) VALUES (...)
```

---

## 📊 Ejemplo de Salida

```
╔══════════════════════════════════════════════════════════════════════════════╗
║              MIGRACIÓN DE PRODUCTOS - PARSER MEJORADO V2                     ║
╚══════════════════════════════════════════════════════════════════════════════╝

🚀 MIGRACIÓN DE PRODUCTOS - PARSER MEJORADO
================================================================================
Modo: DRY-RUN (sin cambios en DB)
Límite: 3
================================================================================

🔍 Buscando facturas con archivo DIAN...
✅ Encontradas 3 facturas para procesar

────────────────────────────────────────────────────────────────────────────────
Factura 1/3
================================================================================
📄 Procesando factura: 8cf8ec5366fa9eaccea38cdffdfa0a76...
   Proveedor: MARCOS MARTINEZ PARRA
   Número: FE15778
   Fecha: 2025-11-11
   Productos actuales en DB: 0
📥 Descargando archivo de S3...
✅ Archivo descargado (25,728 bytes)
🔍 Parseando documento con parser mejorado...
📦 Productos extraídos: 41
   ✅ Con datos completos: 41
   ⚠️  Con datos parciales: 0

   Muestra de productos:
   1. 787138 - BANDERIN METALIZADO BIENVENIDO PF-4-DO (NEON PARTY)
      Cant: 3.0 | Precio: $3,100.00 | Total: $9,300.00
   2. 780177 - BANDERIN FELIZ CUMPLEAÑOS PASTEL/ NEON Y NEGRO
      Cant: 3.0 | Precio: $3,500.00 | Total: $10,500.00
   3. 780177 - BANDERIN FELIZ CUMPLEAÑOS PASTEL/ NEON Y NEGRO
      Cant: 10.0 | Precio: $2,900.00 | Total: $29,000.00
   ... y 38 más

🔍 DRY-RUN: No se actualizó la base de datos

================================================================================
📊 RESUMEN DE MIGRACIÓN
================================================================================

Total facturas: 3
✅ Procesadas exitosamente: 3
❌ Errores: 0

📦 Con productos extraídos: 3
⚠️  Sin productos: 0

Total productos extraídos: 123
   ✅ Con datos completos: 118
   ⚠️  Con datos parciales: 5
   📈 Porcentaje completos: 95.9%

================================================================================
🔍 DRY-RUN: No se realizaron cambios en la base de datos
================================================================================
```

---

## ⚠️ Consideraciones Importantes

### Seguridad:
1. **Modo DRY-RUN por defecto** - Siempre probar primero
2. **Confirmación requerida** - Para modo producción pide escribir "SI"
3. **Backup recomendado** - Hacer backup de DB antes de migración completa

### Performance:
1. **Descarga de S3** - Puede ser lento con muchas facturas
2. **Procesamiento** - ~2-5 segundos por factura
3. **Pausa cada 10 facturas** - Para monitorear progreso

### Datos:
1. **Elimina productos anteriores** - Los reemplaza completamente
2. **Preserva CUFE** - No modifica la factura, solo productos
3. **Datos raw guardados** - En campo `datos_raw` para debugging

---

## 🧪 Plan de Pruebas

### Fase 1: Prueba Rápida (3 facturas)
```bash
python3 quick_test_migration.py
```
**Objetivo**: Validar que el script funciona

### Fase 2: Prueba Pequeña (10 facturas)
```bash
python3 migrate_reprocess_products.py --dry-run 10
```
**Objetivo**: Ver estadísticas reales

### Fase 3: Prueba Mediana (50 facturas)
```bash
python3 migrate_reprocess_products.py --dry-run 50
```
**Objetivo**: Validar performance y calidad

### Fase 4: Migración Real Parcial (10 facturas)
```bash
python3 migrate_reprocess_products.py 10
```
**Objetivo**: Probar actualización de DB

### Fase 5: Migración Completa
```bash
# Hacer backup de DB primero!
python3 migrate_reprocess_products.py
```
**Objetivo**: Migrar todas las facturas

---

## 📝 Checklist de Ejecución

Antes de ejecutar la migración completa:

- [ ] Probar con `quick_test_migration.py`
- [ ] Revisar resultados del dry-run
- [ ] Verificar que productos se extraen correctamente
- [ ] Hacer backup de la base de datos
- [ ] Ejecutar migración parcial (10 facturas)
- [ ] Verificar productos en DB
- [ ] Verificar en UI que se ven correctamente
- [ ] Ejecutar migración completa
- [ ] Validar resultados finales

---

## 🔄 Rollback (si es necesario)

Si algo sale mal:

1. **Restaurar backup de DB**
   ```bash
   # Restaurar desde backup
   pg_restore -d paquetex backup.sql
   ```

2. **Reprocesar facturas específicas**
   ```bash
   # Modificar script para procesar solo CUFEs específicos
   ```

---

## 📈 Mejoras Futuras

1. **Procesamiento paralelo** - Usar multiprocessing para más velocidad
2. **Reintentos automáticos** - Para errores de red
3. **Checkpoint/Resume** - Guardar progreso y continuar si se interrumpe
4. **Notificaciones** - Email/Slack cuando termine
5. **Validación post-migración** - Script para verificar integridad

---

## 🎯 Estado Actual

**OPCIÓN C: COMPLETADA** ✅

- [x] Script principal de migración
- [x] Script de prueba rápida
- [x] Modo DRY-RUN
- [x] Estadísticas detalladas
- [x] Logging completo
- [x] Confirmación de seguridad
- [x] Documentación completa
- [ ] Ejecutar pruebas (pendiente por usuario)
- [ ] Ejecutar migración real (pendiente por usuario)

---

**Fecha**: 2026-02-07
**Estado**: Scripts listos para ejecutar
**Siguiente paso**: Ejecutar `quick_test_migration.py` para validar
