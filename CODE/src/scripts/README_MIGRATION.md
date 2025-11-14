# 📱 Guía de Migración - Números de Teléfono

## 🎯 Objetivo

Este script migra todos los números de teléfono en la base de datos al nuevo formato internacional estandarizado:

**Formato anterior:** `3001234567`, `300 123 4567`, `+57 300 1234567` (inconsistente)  
**Formato nuevo:** `+573001234567` (consistente)

---

## ⚠️ IMPORTANTE - ANTES DE EJECUTAR

### 1. **Backup de la Base de Datos** (OBLIGATORIO)

```bash
# PostgreSQL
pg_dump -U usuario -d nombre_bd > backup_antes_migracion_$(date +%Y%m%d_%H%M%S).sql

# MySQL
mysqldump -u usuario -p nombre_bd > backup_antes_migracion_$(date +%Y%m%d_%H%M%S).sql

# SQLite
cp tu_base_datos.db backup_antes_migracion_$(date +%Y%m%d_%H%M%S).db
```

### 2. **Verificar que el servidor NO esté en producción**

```bash
# Detener el servidor si está corriendo
# Ctrl+C o:
pkill -f uvicorn
```

---

## 🚀 Uso del Script de Migración

### **Paso 1: Modo DRY-RUN (Prueba sin cambios)**

**SIEMPRE ejecuta primero en modo dry-run** para ver qué cambios se harán:

```bash
cd CODE/src
python -m scripts.migrate_phone_numbers --dry-run
```

**Salida esperada:**
```
================================================================================
INICIANDO MIGRACIÓN DE NÚMEROS DE TELÉFONO
================================================================================
Modo: DRY-RUN (no se aplicarán cambios)

Total de clientes a procesar: 150

✅ Cliente 123... (Juan Pérez): 3001234567 → +573001234567
✅ Cliente 456... (María García): 300 123 4567 → +573001234567
ℹ️  Cliente 789... (Pedro López): +573009876543 - Ya normalizado

================================================================================
RESUMEN DE LA MIGRACIÓN
================================================================================
Total de clientes procesados:    150
Teléfonos normalizados:          120
Ya estaban normalizados:         25
Teléfonos inválidos:             3
Sin teléfono (omitidos):         2
Errores:                         0
================================================================================

⚠️  RECORDATORIO: Esto fue un DRY-RUN. Para aplicar los cambios, ejecuta sin --dry-run
```

### **Paso 2: Revisar el Log**

El script genera un log detallado:

```bash
# Ver el log más reciente
ls -lt phone_migration_*.log | head -1
cat phone_migration_20251114_143022.log
```

### **Paso 3: Aplicar Cambios (Producción)**

Si todo se ve bien en el dry-run:

```bash
python -m scripts.migrate_phone_numbers
```

**Se te pedirá confirmación:**
```
⚠️  ADVERTENCIA: Estás a punto de modificar la base de datos en MODO PRODUCCIÓN
⚠️  Se cambiarán PERMANENTEMENTE los números de teléfono

¿Estás seguro de que deseas continuar? (escribe 'SI' para confirmar): SI
```

---

## 🎛️ Opciones Avanzadas

### **Migrar un cliente específico**

```bash
# Dry-run de un cliente
python -m scripts.migrate_phone_numbers --dry-run --customer-id <UUID_DEL_CLIENTE>

# Aplicar cambio a un cliente
python -m scripts.migrate_phone_numbers --customer-id <UUID_DEL_CLIENTE>
```

### **Modo verbose (más detalles)**

```bash
python -m scripts.migrate_phone_numbers --dry-run --verbose
```

### **Ver ayuda**

```bash
python -m scripts.migrate_phone_numbers --help
```

---

## 📊 Casos de Uso

### **Caso 1: Teléfonos colombianos sin código**
```
Antes:  3001234567
Después: +573001234567
```

### **Caso 2: Teléfonos con formato amigable**
```
Antes:  300 123 4567
Después: +573001234567
```

### **Caso 3: Teléfonos con código pero mal formateados**
```
Antes:  +57 300 123 4567
Después: +573001234567
```

### **Caso 4: Teléfonos fijos colombianos**
```
Antes:  6012345678
Después: +576012345678
```

### **Caso 5: Teléfonos internacionales**
```
Antes:  +1 202 555 0123
Después: +12025550123
```

### **Caso 6: Teléfonos ya normalizados**
```
Antes:  +573001234567
Después: +573001234567 (sin cambios)
```

---

## 🔍 Solución de Problemas

### **Error: No se pudo normalizar un teléfono**

**Causa:** El teléfono es inválido o está muy mal formateado.

**Solución:**
1. Revisar el log para ver qué teléfono falló
2. Corregir manualmente en la BD o desde la interfaz
3. Volver a ejecutar la migración

### **Error: Teléfono duplicado después de normalizar**

**Causa:** Dos clientes tienen el mismo teléfono en diferentes formatos.

**Ejemplo:**
- Cliente A: `3001234567`
- Cliente B: `+573001234567`

**Solución:**
1. Identificar los duplicados
2. Fusionar los clientes o corregir el teléfono
3. Volver a ejecutar la migración

---

## 📝 Checklist Pre-Migración

- [ ] **Backup de la base de datos** ✅ OBLIGATORIO
- [ ] Servidor web detenido (o en mantenimiento)
- [ ] Ejecutado en modo `--dry-run` primero
- [ ] Revisado el log de dry-run
- [ ] No hay errores críticos
- [ ] Confirmado que los cambios son correctos
- [ ] Listo para aplicar cambios

---

## 🔄 Rollback (Deshacer Cambios)

Si algo sale mal, restaura el backup:

### **PostgreSQL**
```bash
psql -U usuario -d nombre_bd < backup_antes_migracion_FECHA.sql
```

### **MySQL**
```bash
mysql -u usuario -p nombre_bd < backup_antes_migracion_FECHA.sql
```

### **SQLite**
```bash
cp backup_antes_migracion_FECHA.db tu_base_datos.db
```

---

## ✅ Post-Migración

1. **Verificar datos en la interfaz:**
   - Gestión de Clientes
   - Crear/editar cliente

2. **Probar funcionalidades:**
   - Enlaces tel: y WhatsApp
   - Envío de SMS
   - Búsqueda de clientes

---

## 🎉 ¡Éxito!

✅ Teléfonos en formato internacional consistente  
✅ Validaciones funcionando  
✅ Enlaces funcionando correctamente  

**¡Base de datos estandarizada!** 🚀

