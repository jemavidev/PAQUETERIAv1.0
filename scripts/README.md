# 🔧 Scripts del Proyecto

## 📁 Estructura

### 🗄️ [database/](./database/) - Scripts de Base de Datos
Scripts para gestión de base de datos, migraciones y sincronización.

### 🚀 [deployment/](./deployment/) - Scripts de Despliegue
Scripts para desplegar en diferentes entornos.

### 🔄 [staging/](./staging/) - Scripts de Staging
Scripts específicos para el entorno de staging, sincronización y verificación.

### 🛠️ [maintenance/](./maintenance/) - Scripts de Mantenimiento
Scripts para limpieza, corrección y mantenimiento del sistema.

---

## 🎯 Scripts Principales

### Base de Datos
- `database/create_staging_db.py` - Crear base de datos de staging
- `database/sync_databases.py` - Sincronizar bases de datos

### Despliegue
- `../deploy.sh` - Script principal de despliegue (en raíz)
- `deployment/ejecutar_migracion_staging.sh` - Ejecutar migraciones en staging

### Staging
- `staging/sync_staging_SIMPLE.py` - Sincronización simple de staging
- `staging/diagnostico_sync.sh` - Diagnóstico de sincronización
- `staging/verificar_instalacion.sh` - Verificar instalación

### Mantenimiento
- `maintenance/limpiar_facturas.py` - Limpiar facturas
- `maintenance/corregir_fechas_futuras.py` - Corregir fechas

---

## 📝 Uso

Todos los scripts deben ejecutarse desde la raíz del proyecto:

```bash
# Ejemplo
python scripts/database/create_staging_db.py
bash scripts/staging/diagnostico_sync.sh
```

---

**Nota**: Algunos scripts requieren variables de entorno configuradas en `.env`
