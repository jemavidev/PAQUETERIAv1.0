# Instrucciones para Reprocesar Archivos DIAN desde S3

## Objetivo
Reprocesar todos los archivos DIAN almacenados en S3 para actualizar los totales con el patrón de extracción mejorado que ahora busca:
- "Total factura (=)"
- "Total documento"

## Proceso Recomendado (2 Pasos)

### Paso 1: Análisis (Sin modificar datos) ✅ RECOMENDADO PRIMERO

Este script analiza las diferencias sin modificar nada en la base de datos:

```bash
cd CODE
python analizar_totales_actuales.py
```

**Qué hace:**
- ✅ Descarga todos los archivos DIAN desde S3
- ✅ Extrae los totales con el nuevo patrón
- ✅ Compara con los totales actuales en la BD
- ✅ Genera un reporte de diferencias
- ✅ NO modifica la base de datos

**Salida esperada:**
```
================================================================================
🔍 ANÁLISIS DE TOTALES - ARCHIVOS DIAN EN S3
================================================================================

📊 Total de facturas con archivo DIAN en S3: 45

────────────────────────────────────────────────────────────────────────────────
Analizando facturas...
────────────────────────────────────────────────────────────────────────────────

[1/45] 8a73ab009b4eb093... ✅ OK: $1,469,134
[2/45] 7fc31ab6fa261796... ⚠️ DIFERENCIA: $0 → $460,815
[3/45] 8cf8ec5366fa9eac... ✅ OK: $234,567
...

================================================================================
📊 RESUMEN DEL ANÁLISIS
================================================================================
   Total analizadas:        45
   ✅ Sin cambios:          38
   ⚠️ Con diferencias:      7
   ❌ Errores:              0
================================================================================

⚠️ FACTURAS CON DIFERENCIAS EN EL TOTAL:
────────────────────────────────────────────────────────────────────────────────
CUFE               Número          Actual          Nuevo     Diferencia
────────────────────────────────────────────────────────────────────────────────
7fc31ab6fa261796   FE-12345        $        0   $ 460,815    $ 460,815
...
────────────────────────────────────────────────────────────────────────────────

📄 Reporte detallado guardado en: reporte_diferencias_totales_20260204_153045.txt
```

### Paso 2: Reprocesamiento (Modifica datos) ⚠️ CUIDADO

Una vez revisado el análisis, ejecuta el reprocesamiento:

```bash
cd CODE
python reprocesar_archivos_dian_s3.py
```

**Qué hace:**
- 📥 Descarga todos los archivos DIAN desde S3
- 🔄 Reprocesa cada archivo con el nuevo patrón
- 💾 Actualiza la base de datos con los nuevos valores
- ✅ Muestra progreso en tiempo real

**Confirmación requerida:**
```
⚠️ ADVERTENCIA: Este proceso reprocesará 45 facturas
   Esto actualizará todos los datos extraídos del archivo DIAN

¿Deseas continuar? (si/no): 
```

**Salida esperada:**
```
================================================================================
🔄 REPROCESAMIENTO DE ARCHIVOS DIAN DESDE S3
================================================================================

📊 Total de facturas con archivo DIAN en S3: 45

────────────────────────────────────────────────────────────────────────────────
🚀 Iniciando reprocesamiento...
────────────────────────────────────────────────────────────────────────────────

[1/45] Procesando: 8a73ab009b4eb093...
   S3 Key: invoices/dian/8a73ab009b4eb0933087c42f46d48309...pdf
   📥 Descargando desde S3...
   🔍 Reprocesando archivo DIAN...
   ✅ Reprocesado exitosamente
      Total actualizado: $1,469,134.00

[2/45] Procesando: 7fc31ab6fa261796...
   S3 Key: invoices/dian/7fc31ab6fa2617965c9e21ea4072a282...pdf
   📥 Descargando desde S3...
   🔍 Reprocesando archivo DIAN...
   ✅ Reprocesado exitosamente
      Total actualizado: $460,815.00

...

================================================================================
📊 RESUMEN DEL REPROCESAMIENTO
================================================================================
   Total procesadas:  45
   ✅ Exitosas:       45
   ❌ Fallidas:       0
================================================================================

✅ Reprocesamiento completado
   Fecha: 2026-02-04 15:35:12
```

## Scripts Creados

### 1. `analizar_totales_actuales.py` (Análisis sin modificar)
- **Propósito:** Análisis previo seguro
- **Modifica BD:** ❌ NO
- **Genera reporte:** ✅ SÍ
- **Uso:** Siempre ejecutar primero

### 2. `reprocesar_archivos_dian_s3.py` (Reprocesamiento real)
- **Propósito:** Actualizar datos en BD
- **Modifica BD:** ✅ SÍ
- **Requiere confirmación:** ✅ SÍ
- **Uso:** Después de revisar el análisis

### 3. `test_total_extraction.py` (Prueba individual)
- **Propósito:** Probar un PDF específico
- **Modifica BD:** ❌ NO
- **Uso:** Para debugging de PDFs problemáticos

## Requisitos

### Variables de Entorno
Asegúrate de tener configuradas las variables de S3:
```bash
AWS_ACCESS_KEY_ID=tu_access_key
AWS_SECRET_ACCESS_KEY=tu_secret_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=tu_bucket
```

### Dependencias
```bash
pip install boto3 sqlalchemy psycopg2-binary PyPDF2
```

## Casos de Uso

### Caso 1: Primera vez (Análisis completo)
```bash
# 1. Analizar sin modificar
python CODE/analizar_totales_actuales.py

# 2. Revisar el reporte generado
cat reporte_diferencias_totales_*.txt

# 3. Si todo está bien, reprocesar
python CODE/reprocesar_archivos_dian_s3.py
```

### Caso 2: Probar un PDF específico
```bash
# Descargar el PDF problemático o usar uno local
python CODE/test_total_extraction.py CUFE/FACTURAS/factura.pdf
```

### Caso 3: Reprocesar solo facturas con total en $0
Modificar el script `reprocesar_archivos_dian_s3.py` línea 30:
```python
# Antes:
facturas = db.query(InvoiceV2).filter(
    InvoiceV2.archivo_dian_s3_key.isnot(None)
).all()

# Después (solo facturas con total en 0):
facturas = db.query(InvoiceV2).filter(
    InvoiceV2.archivo_dian_s3_key.isnot(None),
    InvoiceV2.dian_total_neto == 0
).all()
```

## Tiempo Estimado

- **Análisis:** ~2-3 segundos por factura
- **Reprocesamiento:** ~3-4 segundos por factura

Para 45 facturas:
- Análisis: ~2-3 minutos
- Reprocesamiento: ~3-4 minutos

## Seguridad

### Backup Recomendado
Antes de reprocesar, hacer backup de la tabla:
```sql
-- Backup de la tabla invoices_v2
CREATE TABLE invoices_v2_backup_20260204 AS 
SELECT * FROM invoices_v2;
```

### Rollback
Si algo sale mal:
```sql
-- Restaurar desde backup
DELETE FROM invoices_v2;
INSERT INTO invoices_v2 SELECT * FROM invoices_v2_backup_20260204;
```

## Verificación Post-Reprocesamiento

### 1. Verificar totales actualizados
```sql
SELECT 
    cufe,
    numero_factura,
    dian_emisor_razon_social,
    dian_total_neto,
    updated_at
FROM invoices_v2
WHERE archivo_dian_s3_key IS NOT NULL
ORDER BY updated_at DESC
LIMIT 10;
```

### 2. Verificar facturas con total en $0
```sql
SELECT COUNT(*) 
FROM invoices_v2 
WHERE archivo_dian_s3_key IS NOT NULL 
AND (dian_total_neto = 0 OR dian_total_neto IS NULL);
```

Debería ser 0 o muy pocas.

### 3. Comparar con backup
```sql
SELECT 
    a.cufe,
    a.numero_factura,
    b.dian_total_neto as total_anterior,
    a.dian_total_neto as total_nuevo,
    (a.dian_total_neto - b.dian_total_neto) as diferencia
FROM invoices_v2 a
JOIN invoices_v2_backup_20260204 b ON a.cufe = b.cufe
WHERE a.dian_total_neto != b.dian_total_neto
ORDER BY diferencia DESC;
```

## Troubleshooting

### Error: "No se pudo descargar desde S3"
- Verificar credenciales AWS
- Verificar que el bucket existe
- Verificar permisos de lectura

### Error: "No se pudo extraer texto del PDF"
- El PDF puede estar corrupto
- Verificar que el archivo existe en S3
- Intentar descargar manualmente y probar con `test_total_extraction.py`

### Total sigue en $0 después de reprocesar
- Ejecutar `test_total_extraction.py` con ese PDF específico
- Revisar la sección de totales del PDF
- El formato puede ser diferente, ajustar el regex

## Logs

Los scripts generan logs en consola. Para guardar:
```bash
python CODE/analizar_totales_actuales.py 2>&1 | tee analisis.log
python CODE/reprocesar_archivos_dian_s3.py 2>&1 | tee reprocesamiento.log
```

## Contacto

Si encuentras problemas:
1. Ejecuta `test_total_extraction.py` con el PDF problemático
2. Comparte la salida completa
3. Comparte el CUFE de la factura
4. Se ajustará el patrón regex según sea necesario
