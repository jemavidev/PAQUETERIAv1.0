# 🧹 Scripts de Limpieza de Base de Datos

## 📋 Descripción

Este directorio contiene scripts para limpiar las tablas de la base de datos de PAQUETES EL CLUB v4.0. Los scripts eliminan todos los datos de las siguientes tablas:

- `packages`
- `package_history`
- `package_announcements_new`
- `messages`
- `file_uploads`
- `customers`

## ⚠️ Advertencia Importante

**ESTOS SCRIPTS ELIMINAN TODOS LOS DATOS DE LAS TABLAS ESPECIFICADAS.**

- ✅ **Solo usar en desarrollo**
- ❌ **NUNCA usar en producción**
- 🔒 **La acción NO SE PUEDE DESHACER**

## 🚀 Scripts Disponibles

### 1. Script Bash (Recomendado)
```bash
# Desde la raíz del proyecto
./cleanup-db.sh

# O directamente
./SCRIPTS/database/cleanup_database.sh
```

**Ventajas:**
- ✅ No requiere dependencias Python adicionales
- ✅ Usa psql directamente
- ✅ Más rápido y confiable
- ✅ Manejo de errores robusto

### 2. Script Python con Variables de Entorno
```bash
# Desde la raíz del proyecto
python SCRIPTS/database/cleanup_database_env.py
```

**Ventajas:**
- ✅ Usa psycopg2 directamente
- ✅ Carga variables de entorno automáticamente
- ✅ Logging detallado
- ✅ Manejo de transacciones

### 3. Script Python con SQLAlchemy
```bash
# Desde la raíz del proyecto
python SCRIPTS/database/cleanup_database_simple.py
```

**Ventajas:**
- ✅ Usa SQLAlchemy
- ✅ Integración con el proyecto
- ✅ Logging detallado

### 4. 🆕 Limpieza Completa (DB + AWS S3)
```bash
# Desde la raíz del proyecto
./cleanup-complete.sh

# O directamente
python SCRIPTS/database/cleanup_database_with_s3.py
```

**Ventajas:**
- ✅ Limpieza completa del sistema
- ✅ Elimina archivos de AWS S3
- ✅ Limpia base de datos
- ✅ Verificación completa
- ✅ Resumen detallado

### 5. 🆕 Limpieza Selectiva
```bash
# Desde la raíz del proyecto
python SCRIPTS/database/cleanup_selective.py
```

**Ventajas:**
- ✅ Limpieza por tablas específicas
- ✅ Limpieza por fechas
- ✅ Limpieza por usuario
- ✅ Solo archivos S3
- ✅ Solo base de datos
- ✅ Archivos huérfanos
- ✅ Interfaz interactiva

## 📊 Funcionalidades

### ✅ Características Comunes
- **Confirmación de seguridad**: Requiere escribir 'SI' para confirmar
- **Conteo de registros**: Muestra cuántos registros se van a eliminar
- **Orden correcto**: Elimina en orden que respeta foreign keys
- **Logging detallado**: Registra todas las operaciones
- **Verificación**: Confirma que la limpieza fue exitosa
- **Reset de secuencias**: Reinicia contadores auto-incremento

### 🔄 Orden de Eliminación
1. `file_uploads` (depende de packages)
2. `messages` (depende de packages y customers)
3. `package_history` (depende de packages)
4. `package_announcements_new` (depende de packages y customers)
5. `packages` (tabla principal)
6. `customers` (tabla principal)

## 🛠️ Requisitos

### Para Script Bash
- PostgreSQL instalado
- `psql` en el PATH
- Variables de entorno configuradas en `.env`

### Para Scripts Python
- Python 3.8+
- `psycopg2-binary` (para script con variables de entorno)
- SQLAlchemy (para script con SQLAlchemy)
- Variables de entorno configuradas

## 📝 Variables de Entorno Requeridas

Asegúrate de tener estas variables en `.env`:

```bash
# Base de datos
DB_HOST=localhost
DB_PORT=5432
DB_NAME=paqueteria
DB_USER=postgres
DB_PASSWORD=tu_password

# AWS S3 (para limpieza completa)
AWS_ACCESS_KEY_ID=tu_access_key
AWS_SECRET_ACCESS_KEY=tu_secret_key
AWS_S3_BUCKET=paquetes-el-club
AWS_REGION=us-east-1
```

## 📋 Uso Rápido

### Paso 0: Configuración Inicial (Solo la primera vez)
```bash
# 1. Instalar dependencias
./SCRIPTS/database/install_s3_dependencies.sh

# 2. Configurar AWS S3
./SCRIPTS/database/configure_aws_s3.sh

# 3. Probar configuración
./test-s3-cleanup.sh
```

### Opción 1: Script de Conveniencia (Solo DB)
```bash
# Desde la raíz del proyecto
./cleanup-db.sh
```

### Opción 2: Limpieza Completa (DB + S3) 🆕
```bash
# Desde la raíz del proyecto
./cleanup-complete.sh
```

### Opción 3: Limpieza Selectiva 🆕
```bash
# Desde la raíz del proyecto
python SCRIPTS/database/cleanup_selective.py
```

### Opción 4: Script Bash Directo
```bash
# Desde la raíz del proyecto
./SCRIPTS/database/cleanup_database.sh
```

### Opción 5: Script Python
```bash
# Desde la raíz del proyecto
python SCRIPTS/database/cleanup_database_env.py
```

## 🆕 Nuevas Funcionalidades

### Limpieza Completa (DB + S3)
- **Elimina archivos de AWS S3** basándose en las claves almacenadas en la base de datos
- **Limpia todas las tablas** de la base de datos
- **Verificación completa** tanto de DB como de S3
- **Resumen detallado** de elementos eliminados

### Limpieza Selectiva
- **8 opciones diferentes** de limpieza
- **Interfaz interactiva** fácil de usar
- **Limpieza por fechas** - elimina registros de un rango específico
- **Limpieza por usuario** - elimina solo datos de un usuario específico
- **Limpieza de archivos huérfanos** - elimina archivos S3 sin referencia en DB
- **Limpieza de registros sin S3** - elimina registros de file_uploads sin archivos

### Requisitos Adicionales para S3
- **boto3** instalado: `pip install boto3`
- **Variables AWS** configuradas en `.env`:
  - `AWS_ACCESS_KEY_ID`
  - `AWS_SECRET_ACCESS_KEY`
  - `AWS_S3_BUCKET`
  - `AWS_REGION` (opcional, default: us-east-1)

### Configuración Automática de AWS S3
```bash
# Configurar variables AWS de forma interactiva
./SCRIPTS/database/configure_aws_s3.sh
```

**Ventajas:**
- ✅ Configuración interactiva y segura
- ✅ Validación de credenciales
- ✅ Backup automático del archivo original
- ✅ Guía paso a paso

## 📊 Ejemplo de Salida

```
🚀 PAQUETES EL CLUB v4.0 - Script de Limpieza de Base de Datos
============================================================

📊 Estado actual de la base de datos:
📊 packages: 150 registros
📊 package_history: 300 registros
📊 package_announcements_new: 75 registros
📊 messages: 25 registros
📊 file_uploads: 10 registros
📊 customers: 50 registros

Total de registros a eliminar: 610

============================================================
⚠️  ADVERTENCIA: LIMPIEZA DE BASE DE DATOS  ⚠️
============================================================
Este script eliminará TODOS los datos de las siguientes tablas:
• packages
• package_history
• package_announcements_new
• messages
• file_uploads
• customers

Esta acción NO SE PUEDE DESHACER.
============================================================

¿Estás seguro de que quieres continuar? (escribe 'SI' para confirmar): SI

🧹 Iniciando limpieza...
🗑️ file_uploads: 10 registros eliminados
🗑️ messages: 25 registros eliminados
🗑️ package_history: 300 registros eliminados
🗑️ package_announcements_new: 75 registros eliminados
🗑️ packages: 150 registros eliminados
🗑️ customers: 50 registros eliminados
🎉 Limpieza completada. Total de registros eliminados: 610

🔄 Reseteando secuencias...
🔄 Secuencia packages_id_seq reseteada
🔄 Secuencia messages_id_seq reseteada
🔄 Secuencia file_uploads_id_seq reseteada
✅ Secuencias reseteadas correctamente

🔍 Verificando limpieza...
✅ packages está vacía
✅ package_history está vacía
✅ package_announcements_new está vacía
✅ messages está vacía
✅ file_uploads está vacía
✅ customers está vacía
🎉 Verificación exitosa: Todas las tablas están vacías

✅ Limpieza completada exitosamente
📝 Revisa los logs para más detalles
```

## 🐛 Solución de Problemas

### Error de Conexión
```
❌ Error: No se puede conectar a la base de datos
```
**Solución**: Verifica las variables de entorno en `CODE/LOCAL/env.local`

### Error de Permisos
```
❌ Error: permission denied
```
**Solución**: Ejecuta `chmod +x cleanup-db.sh`

### Error de Dependencias
```
❌ Error: psycopg2 no está instalado
```
**Solución**: Instala con `pip install psycopg2-binary`

## 📁 Archivos de Log

Los logs se guardan en:
- `logs/database_cleanup.log` - Log detallado de operaciones

## 🔒 Seguridad

- ✅ Requiere confirmación explícita
- ✅ Solo funciona en desarrollo
- ✅ Logging de todas las operaciones
- ✅ Verificación post-limpieza
- ✅ Manejo de errores robusto

## 📞 Soporte

Si tienes problemas con los scripts:

1. Verifica que estés en la raíz del proyecto
2. Confirma que las variables de entorno estén configuradas
3. Revisa el archivo de log para detalles del error
4. Asegúrate de que PostgreSQL esté ejecutándose

---

**PAQUETES EL CLUB v4.0** - Scripts de Limpieza de Base de Datos
**Versión**: 1.0.0
**Fecha**: 2025-01-24
