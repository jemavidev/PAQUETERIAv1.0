# 🗑️ Cómo Eliminar TODAS las Facturas

## ⚠️ ADVERTENCIA

Esta operación es **IRREVERSIBLE**. Eliminará:
- ✅ Todas las facturas de la base de datos
- ✅ Todos los productos asociados
- ✅ Todos los archivos PDF en S3 (solo con script Python)

## 📋 Opciones Disponibles

### Opción 1: Script Python (Recomendado)
**Elimina**: Base de datos + Archivos S3

```bash
cd CODE
python3 eliminar_todas_facturas.py
```

**Ventajas**:
- ✅ Elimina archivos de S3
- ✅ Muestra progreso detallado
- ✅ Doble confirmación
- ✅ Manejo de errores

**Desventajas**:
- ❌ Requiere dependencias Python instaladas

---

### Opción 2: Script Bash (Rápido)
**Elimina**: Solo base de datos (NO elimina S3)

```bash
cd CODE
./eliminar_todas_facturas.sh
```

**Ventajas**:
- ✅ Muy rápido
- ✅ No requiere Python
- ✅ Funciona con Docker

**Desventajas**:
- ❌ NO elimina archivos de S3

---

### Opción 3: SQL Directo (Manual)
**Elimina**: Solo base de datos (NO elimina S3)

```bash
# Conectar a la base de datos
docker-compose exec db psql -U paquetex_user -d paquetex_db

# Ejecutar SQL
DELETE FROM invoice_products_v2;
DELETE FROM invoices_v2;

# Verificar
SELECT COUNT(*) FROM invoices_v2;
```

**Ventajas**:
- ✅ Control total
- ✅ Muy rápido

**Desventajas**:
- ❌ NO elimina archivos de S3
- ❌ Sin confirmaciones de seguridad

---

## 🚀 Guía Paso a Paso

### Usando Script Python (Recomendado)

**Paso 1**: Ir a la carpeta CODE
```bash
cd CODE
```

**Paso 2**: Ejecutar el script
```bash
python3 eliminar_todas_facturas.py
```

**Paso 3**: Confirmar (primera vez)
```
¿Estás seguro de que quieres continuar? (escribe 'SI' en mayúsculas): SI
```

**Paso 4**: Confirmar (segunda vez)
```
¿REALMENTE quieres eliminar TODAS las facturas? (escribe 'ELIMINAR TODO'): ELIMINAR TODO
```

**Paso 5**: Esperar a que termine
```
🔄 Iniciando eliminación...

✅ Servicio S3 disponible

📊 Estadísticas:
  • Facturas a eliminar: 43
  • Productos a eliminar: 0

🗑️  Eliminando archivos de S3...
  [1/43] Procesando: e647d6cf12f9bc14...
    ✓ Eliminado: invoices/provider/e647d6cf12f9bc14....pdf
  [2/43] Procesando: 862a203aede5e068...
    ✓ Eliminado: invoices/provider/862a203aede5e068....pdf
  ...

🗑️  Eliminando productos...
  ✓ 0 productos eliminados

🗑️  Eliminando facturas...
  ✓ 43 facturas eliminadas

================================================================================
✅ ELIMINACIÓN COMPLETADA
================================================================================

📊 Resumen:
  • Facturas eliminadas: 43
  • Productos eliminados: 0
  • Archivos S3 eliminados: 43

✅ Base de datos limpia
```

---

### Usando Script Bash (Rápido)

**Paso 1**: Ir a la carpeta CODE
```bash
cd CODE
```

**Paso 2**: Ejecutar el script
```bash
./eliminar_todas_facturas.sh
```

**Paso 3**: Confirmar dos veces
```
¿Estás seguro de que quieres continuar? (escribe 'SI' en mayúsculas): SI
¿REALMENTE quieres eliminar TODAS las facturas? (escribe 'ELIMINAR TODO'): ELIMINAR TODO
```

**Paso 4**: Resultado
```
🔄 Iniciando eliminación...

ANTES DE ELIMINAR:
 total_facturas 
----------------
             43

DELETE 0
DELETE 43

DESPUÉS DE ELIMINAR:
 facturas_restantes 
--------------------
                  0

================================================================================
✅ ELIMINACIÓN COMPLETADA
================================================================================

⚠️  IMPORTANTE: Los archivos en S3 NO fueron eliminados
   Para eliminar archivos de S3, ejecuta:
   python3 eliminar_todas_facturas.py
```

---

## 🔍 Verificar que se Eliminaron

### Opción 1: Desde la interfaz web
1. Ir a http://localhost/invoices/facturas
2. Debería mostrar "No hay facturas"

### Opción 2: Desde la base de datos
```bash
docker-compose exec db psql -U paquetex_user -d paquetex_db -c "SELECT COUNT(*) FROM invoices_v2;"
```

Debería mostrar: `0`

### Opción 3: Verificar S3
```bash
# Listar archivos en S3 (si tienes AWS CLI configurado)
aws s3 ls s3://tu-bucket/invoices/provider/
```

---

## ⚠️ Problemas Comunes

### Error: "No module named 'sqlalchemy'"
**Solución**: Instalar dependencias
```bash
cd CODE
pip install -r requirements.txt
```

### Error: "Permission denied"
**Solución**: Dar permisos al script
```bash
chmod +x eliminar_todas_facturas.sh
```

### Error: "S3Service no disponible"
**Solución**: El script continuará pero NO eliminará archivos de S3. Puedes:
1. Configurar AWS credentials
2. O eliminar archivos de S3 manualmente desde la consola de AWS

### Error: "Connection refused"
**Solución**: Asegúrate de que Docker esté corriendo
```bash
docker-compose up -d
```

---

## 🛡️ Seguridad

### Confirmaciones Requeridas

El script Python requiere **2 confirmaciones**:
1. Primera: Escribir `SI` (en mayúsculas)
2. Segunda: Escribir `ELIMINAR TODO` (exacto)

Esto previene eliminaciones accidentales.

### Cancelar la Operación

Puedes cancelar en cualquier momento:
- Presiona `Ctrl+C`
- O escribe cualquier cosa diferente a las confirmaciones

---

## 📊 Qué se Elimina

| Elemento | Script Python | Script Bash | SQL Directo |
|----------|---------------|-------------|-------------|
| Facturas (BD) | ✅ | ✅ | ✅ |
| Productos (BD) | ✅ | ✅ | ✅ |
| Archivos S3 | ✅ | ❌ | ❌ |

---

## 💡 Casos de Uso

### Caso 1: Empezar de Cero
**Situación**: Quieres limpiar todo y empezar de nuevo.

**Solución**:
```bash
cd CODE
python3 eliminar_todas_facturas.py
```

### Caso 2: Limpiar Base de Datos Rápido
**Situación**: Solo quieres limpiar la BD (no te importa S3).

**Solución**:
```bash
cd CODE
./eliminar_todas_facturas.sh
```

### Caso 3: Limpiar Solo Facturas de Prueba
**Situación**: Quieres eliminar solo algunas facturas.

**Solución**: Usa SQL directo con WHERE
```sql
DELETE FROM invoice_products_v2 WHERE cufe IN (SELECT cufe FROM invoices_v2 WHERE estado = 'sin_cufe');
DELETE FROM invoices_v2 WHERE estado = 'sin_cufe';
```

---

## 🔄 Después de Eliminar

### Verificar que todo está limpio:
```bash
# Verificar BD
docker-compose exec db psql -U paquetex_user -d paquetex_db -c "SELECT COUNT(*) FROM invoices_v2;"

# Verificar interfaz
# Ir a http://localhost/invoices/facturas
# Debería mostrar "No hay facturas"
```

### Empezar a cargar facturas nuevas:
1. Ir a http://localhost/invoices/facturas
2. Click en el botón "+" (Cargar nueva factura)
3. Seleccionar PDFs
4. Cargar

---

## 📝 Archivos Creados

1. `CODE/eliminar_todas_facturas.py` - Script Python completo
2. `CODE/eliminar_todas_facturas.sh` - Script Bash rápido
3. `CODE/eliminar_todas_facturas.sql` - SQL directo (manual)

---

## 🎯 Resumen Rápido

**Para eliminar TODO (BD + S3)**:
```bash
cd CODE
python3 eliminar_todas_facturas.py
```

**Para eliminar solo BD (rápido)**:
```bash
cd CODE
./eliminar_todas_facturas.sh
```

**Para eliminar manualmente**:
```bash
docker-compose exec db psql -U paquetex_user -d paquetex_db
DELETE FROM invoice_products_v2;
DELETE FROM invoices_v2;
```

---

## ⚠️ RECORDATORIO FINAL

Esta operación es **IRREVERSIBLE**. Asegúrate de:
- ✅ Tener un backup si necesitas los datos
- ✅ Estar seguro de que quieres eliminar TODO
- ✅ Haber leído esta guía completamente

**¿Listo para eliminar?** Ejecuta el script que prefieras. 🗑️
