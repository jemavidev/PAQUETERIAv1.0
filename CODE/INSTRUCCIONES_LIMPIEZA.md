# 🗑️ Instrucciones de Limpieza de Datos de Prueba

## 📋 Resumen

Este documento explica cómo usar los scripts de limpieza para eliminar:
1. **Clientes de prueba** (4 clientes específicos)
2. **Todos los paquetes cancelados**

---

## 🔧 Requisitos Previos

### 1. Dependencias Python
```bash
pip install psycopg2-binary boto3 python-dotenv
```

### 2. Variables de Entorno
El archivo `.env` debe contener:
- Credenciales de RDS (PostgreSQL)
- Credenciales de S3 (AWS)

✅ Ya están configuradas en tu `.env`

---

## 📝 Scripts Disponibles

### 1. `verificar_limpieza.py` - Solo Consulta
**Propósito:** Ver qué se eliminará SIN eliminar nada

**Uso:**
```bash
cd CODE
python scripts/maintenance/verificar_limpieza.py
```

**Salida:**
- Lista de clientes a eliminar
- Cantidad de paquetes por estado
- Cantidad de archivos en S3
- Resumen total

### 2. `limpieza_datos_prueba.py` - Eliminación Real
**Propósito:** Eliminar los datos de forma segura

**Uso:**
```bash
cd CODE
python scripts/maintenance/limpieza_datos_prueba.py
```

**Proceso:**
1. Conecta a RDS y S3
2. Verifica registros a eliminar
3. Pide confirmación (debes escribir "SI")
4. Crea backup automático
5. Elimina archivos de S3
6. Elimina registros de BD
7. Genera reporte final

---

## 🚀 Proceso Recomendado

### Paso 1: Verificación Previa
```bash
cd CODE
python scripts/maintenance/verificar_limpieza.py
```

**Revisa la salida:**
- ¿Son los clientes correctos?
- ¿Cuántos paquetes se eliminarán?
- ¿Cuántos archivos en S3?

### Paso 2: Ejecutar Limpieza
```bash
cd CODE
python scripts/maintenance/limpieza_datos_prueba.py
```

**El script te mostrará:**
```
📊 VERIFICANDO REGISTROS A ELIMINAR

Clientes de prueba:
  - Clientes: 4
  - Paquetes: 15
  - Anuncios: 8
  - Eventos: 45
  - Archivos: 12

Paquetes cancelados:
  - Paquetes: 23
  - Eventos: 67
  - Historial: 89
  - Archivos: 5

⚠️  ADVERTENCIA: Esta operación NO se puede deshacer
Se creará un backup antes de eliminar

¿Deseas continuar? (escribe 'SI' para confirmar):
```

**Escribe:** `SI` (en mayúsculas)

### Paso 3: Verificar Resultados
El script mostrará:
```
✅ LIMPIEZA COMPLETADA EXITOSAMENTE

📊 RESUMEN DE ELIMINACIÓN:

Clientes de prueba:
  - eventos: 45
  - historial: 67
  - file_uploads: 12
  - archivos_s3: 12
  - packages: 15
  - customers: 4

Paquetes cancelados:
  - eventos: 67
  - historial: 89
  - file_uploads: 5
  - archivos_s3: 5
  - packages: 23

✅ Backup guardado en: CODE/backups/backup_limpieza_20251211_143022.json
```

---

## 🔒 Características de Seguridad

### 1. Backup Automático
- Se crea antes de eliminar
- Formato JSON con todos los datos
- Ubicación: `CODE/backups/backup_limpieza_YYYYMMDD_HHMMSS.json`

### 2. Transacciones
- Todo se ejecuta en una transacción
- Si algo falla → **ROLLBACK automático**
- No se elimina nada si hay error

### 3. Confirmación Requerida
- Debes escribir "SI" (mayúsculas)
- Cualquier otra respuesta cancela

### 4. Orden Correcto
- Elimina en orden de dependencias
- Evita errores de foreign key

### 5. Eliminación S3
- Elimina archivos de S3 primero
- Continúa aunque falle algún archivo
- Reporta errores sin detener el proceso

---

## 📊 Datos que se Eliminarán

### Clientes de Prueba
**Teléfonos:**
- `+573001234567`
- `+573002596319`
- `+573008103849`
- `+573008398365`

**Tablas afectadas:**
1. `customers` - Los clientes
2. `packages` - Todos sus paquetes (cualquier estado)
3. `package_announcements_new` - Sus anuncios
4. `package_events` - Eventos de sus paquetes
5. `package_history` - Historial de sus paquetes
6. `file_uploads` - Registros de archivos
7. `messages` - Mensajes relacionados
8. `notifications` - Notificaciones
9. `customer_preferences` - Preferencias
10. **S3** - Archivos físicos

### Paquetes Cancelados
**Criterio:** `status = 'CANCELADO'`

**Tablas afectadas:**
1. `packages` - Los paquetes cancelados
2. `package_events` - Sus eventos
3. `package_history` - Su historial
4. `file_uploads` - Registros de archivos
5. `messages` - Mensajes relacionados
6. `notifications` - Notificaciones
7. `package_announcements_new` - Desvincular (no eliminar)
8. **S3** - Archivos físicos

---

## ⚠️ Advertencias Importantes

### 1. Operación Irreversible
- Una vez ejecutado, NO se puede deshacer
- El backup es solo para referencia
- No hay función de "restaurar"

### 2. Archivos S3
- Se eliminan permanentemente
- No hay papelera de reciclaje en S3
- Asegúrate de que no los necesitas

### 3. Tiempo de Ejecución
- Depende de la cantidad de datos
- Puede tomar varios minutos
- No interrumpas el proceso

### 4. Conexión a RDS
- Requiere acceso a internet
- Usa las credenciales del `.env`
- Verifica que el RDS esté accesible

---

## 🐛 Solución de Problemas

### Error: "No se puede conectar a RDS"
**Solución:**
1. Verifica que el `.env` tenga las credenciales correctas
2. Verifica que tu IP tenga acceso al RDS
3. Verifica que el RDS esté activo

### Error: "No se puede conectar a S3"
**Solución:**
1. Verifica las credenciales AWS en `.env`
2. Verifica que el bucket exista
3. Verifica permisos de la cuenta AWS

### Error: "Foreign key constraint"
**Solución:**
- El script ya maneja el orden correcto
- Si ocurre, el rollback automático protege los datos
- Revisa los logs para más detalles

### Script se detiene
**Solución:**
1. Revisa el mensaje de error
2. El rollback automático protegió los datos
3. Nada se eliminó si hubo error
4. Puedes ejecutar de nuevo

---

## 📁 Estructura de Archivos

```
CODE/
├── scripts/
│   └── maintenance/
│       ├── verificar_limpieza.py      # Solo consulta
│       └── limpieza_datos_prueba.py   # Eliminación real
├── backups/                            # Backups automáticos
│   └── backup_limpieza_*.json
├── .env                                # Credenciales
└── INSTRUCCIONES_LIMPIEZA.md          # Este archivo
```

---

## 🎯 Checklist Pre-Ejecución

Antes de ejecutar la limpieza, verifica:

- [ ] He ejecutado `verificar_limpieza.py`
- [ ] He revisado los datos a eliminar
- [ ] Estoy seguro de que son datos de prueba
- [ ] Tengo acceso a RDS
- [ ] Tengo acceso a S3
- [ ] He leído las advertencias
- [ ] Entiendo que es irreversible
- [ ] Estoy listo para escribir "SI"

---

## 📞 Soporte

Si tienes dudas o problemas:
1. Revisa los logs del script
2. Verifica el backup creado
3. Contacta al equipo de desarrollo

---

## ✅ Ejemplo de Ejecución Exitosa

```bash
$ cd CODE
$ python scripts/maintenance/limpieza_datos_prueba.py

============================================================
SCRIPT DE LIMPIEZA DE DATOS DE PRUEBA
============================================================

✅ Conectado a RDS: ls-abe25e9bea57818f0ee32555c0e7b4a10e361535...
✅ Conectado a S3: elclub-paqueteria

📊 VERIFICANDO REGISTROS A ELIMINAR

Clientes de prueba:
  - Clientes: 4
  - Paquetes: 15
  - Anuncios: 8
  - Eventos: 45
  - Archivos: 12

Paquetes cancelados:
  - Paquetes: 23
  - Eventos: 67
  - Historial: 89
  - Archivos: 5

⚠️  ADVERTENCIA: Esta operación NO se puede deshacer
Se creará un backup antes de eliminar

¿Deseas continuar? (escribe 'SI' para confirmar): SI

📦 Creando backup...
✅ Backup creado: CODE/backups/backup_limpieza_20251211_143022.json

🚀 INICIANDO ELIMINACIÓN

============================================================
ELIMINANDO CLIENTES DE PRUEBA
============================================================

🗑️  Eliminando 12 archivos de S3...
   Eliminados: 10/12
   Eliminados: 12/12
1/8 Eliminando eventos de paquetes...
2/8 Eliminando historial de paquetes...
3/8 Eliminando registros de archivos...
4/8 Eliminando notificaciones de paquetes...
5/8 Eliminando mensajes de paquetes...
6/8 Desvinculando anuncios de paquetes...
7/8 Eliminando paquetes...
8/8 Eliminando clientes...

============================================================
ELIMINANDO PAQUETES CANCELADOS
============================================================

🗑️  Eliminando 5 archivos de S3...
   Eliminados: 5/5
1/7 Eliminando eventos...
2/7 Eliminando historial...
3/7 Eliminando registros de archivos...
4/7 Eliminando notificaciones...
5/7 Eliminando mensajes...
6/7 Desvinculando anuncios...
7/7 Eliminando paquetes cancelados...

============================================================
✅ LIMPIEZA COMPLETADA EXITOSAMENTE
============================================================

📊 RESUMEN DE ELIMINACIÓN:

Clientes de prueba:
  - archivos_s3: 12
  - eventos: 45
  - historial: 67
  - file_uploads: 12
  - notifications_packages: 23
  - messages_packages: 8
  - announcements_updated: 8
  - packages: 15
  - customers: 4

Paquetes cancelados:
  - archivos_s3: 5
  - eventos: 67
  - historial: 89
  - file_uploads: 5
  - notifications: 12
  - messages: 3
  - announcements_updated: 15
  - packages: 23

✅ Backup guardado en: CODE/backups/backup_limpieza_20251211_143022.json

Conexión cerrada
```

---

**Fecha:** 11 de Diciembre, 2025
**Versión:** 1.0.0
**Estado:** ✅ Listo para usar
