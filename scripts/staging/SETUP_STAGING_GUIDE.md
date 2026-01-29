# 🚀 GUÍA COMPLETA: Configurar Staging con Base de Datos Separada

## 📋 Resumen

Esta guía te ayudará a configurar el ambiente de staging para que use la base de datos `paqueteria_staging` en AWS RDS, completamente separada de producción.

## 🎯 Objetivo

```
Servidor Staging (puerto 8001)
    ↓
Base de Datos: paqueteria_staging (AWS RDS)
    ↓
Datos independientes de producción
```

## ✅ Cambios Realizados

### 1. **Archivo de Configuración Staging**
- ✅ Creado: `CODE/.env.staging`
- ✅ Configurado para usar `paqueteria_staging`
- ✅ Puerto 8001 para el servidor
- ✅ Redis en puerto 6380
- ✅ Prefijo S3: `staging/`

### 2. **Docker Compose Actualizado**
- ✅ Modificado: `docker-compose.staging.yml`
- ✅ Ahora usa `CODE/.env.staging` en lugar de `CODE/.env`

### 3. **Scripts de Gestión**
- ✅ `scripts/staging/01_verify_and_init_staging_db.py` - Verificar y preparar DB
- ✅ `scripts/staging/list_databases.py` - Listar todas las DBs
- ✅ Más scripts en desarrollo...

## 🚀 Pasos para Configurar Staging

### **Paso 1: Verificar Base de Datos**

```bash
python scripts/staging/01_verify_and_init_staging_db.py
```

Este script:
- ✅ Verifica que `paqueteria_staging` existe
- ✅ La crea si no existe
- ✅ Muestra el estado actual (tablas, registros, etc.)
- ✅ Te indica los próximos pasos

### **Paso 2: Inicializar Esquema**

Si la base de datos está vacía, tienes 2 opciones:

#### **Opción A: Usar Migraciones de Alembic** (Recomendado)

```bash
cd CODE
export DATABASE_URL="postgresql://jveyes:a?HC!2.*1#?[==:|289qAI=)#V4kDzl$@ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com:5432/paqueteria_staging"
alembic upgrade head
```

#### **Opción B: Copiar Esquema desde Producción**

```bash
python scripts/staging/02_copy_schema_from_prod.py
```

### **Paso 3: Sincronizar Datos (Opcional)**

Si quieres copiar datos de producción a staging:

```bash
python scripts/staging/03_sync_from_production.py
```

⚠️ **ADVERTENCIA**: Esto sobrescribirá los datos en staging.

### **Paso 4: Levantar Servidor Staging**

```bash
docker-compose -f docker-compose.staging.yml up -d
```

### **Paso 5: Verificar que Funciona**

```bash
# Verificar salud del servidor
curl http://localhost:8001/health

# Ver logs
docker-compose -f docker-compose.staging.yml logs -f app

# Verificar conexión a DB
docker-compose -f docker-compose.staging.yml exec app python -c "from src.app.database import check_db_connection; print('✅ DB OK' if check_db_connection() else '❌ DB Error')"
```

## 🔍 Verificar Configuración

### **Ver qué base de datos está usando:**

```bash
docker-compose -f docker-compose.staging.yml exec app env | grep DATABASE_URL
```

Debería mostrar:
```
DATABASE_URL=postgresql://...paqueteria_staging
```

### **Ver ambiente:**

```bash
docker-compose -f docker-compose.staging.yml exec app env | grep ENVIRONMENT
```

Debería mostrar:
```
ENVIRONMENT=staging
```

## 📊 Estructura de Bases de Datos

```
AWS RDS (ls-abe25e9bea57818f0ee32555c0e7b4a10e361535...)
├── paqueteria_v4 (Producción)
│   ├── Puerto: 80
│   ├── Datos: Reales
│   └── Acceso: Solo lectura desde staging
│
└── paqueteria_staging (Staging)
    ├── Puerto: 8001
    ├── Datos: Copia/Pruebas
    └── Acceso: Lectura/Escritura
```

## 🔄 Flujo de Sincronización

```
┌─────────────────┐
│  Producción     │
│  paqueteria_v4  │
│  (Solo lectura) │
└────────┬────────┘
         │
         │ Sincronización
         │ (Opcional)
         ↓
┌─────────────────┐
│  Staging        │
│paqueteria_staging│
│ (Lectura/Escrit)│
└─────────────────┘
```

## 🛠️ Comandos Útiles

### **Ver estado de contenedores:**
```bash
docker-compose -f docker-compose.staging.yml ps
```

### **Reiniciar staging:**
```bash
docker-compose -f docker-compose.staging.yml restart
```

### **Ver logs en tiempo real:**
```bash
docker-compose -f docker-compose.staging.yml logs -f
```

### **Detener staging:**
```bash
docker-compose -f docker-compose.staging.yml down
```

### **Reconstruir imagen:**
```bash
docker-compose -f docker-compose.staging.yml build --no-cache
docker-compose -f docker-compose.staging.yml up -d
```

## 🔒 Seguridad

- ✅ Staging usa SECRET_KEY diferente a producción
- ✅ Staging tiene su propia base de datos
- ✅ Staging usa prefijo S3 separado (`staging/`)
- ✅ Mensajes SMS tienen prefijo `[STAGING]`
- ✅ Producción es de solo lectura desde staging

## 🐛 Troubleshooting

### **Error: No se puede conectar a la base de datos**

1. Verificar credenciales en `CODE/.env.staging`
2. Verificar que `paqueteria_staging` existe:
   ```bash
   python scripts/staging/list_databases.py
   ```
3. Verificar conectividad de red al RDS

### **Error: Tablas no existen**

1. Ejecutar migraciones:
   ```bash
   cd CODE && alembic upgrade head
   ```
2. O copiar esquema desde producción

### **Error: Puerto 8001 ya en uso**

1. Verificar qué está usando el puerto:
   ```bash
   lsof -i :8001
   ```
2. Detener el proceso o cambiar el puerto en `docker-compose.staging.yml`

## 📞 Soporte

Si tienes problemas:
1. Revisar logs: `docker-compose -f docker-compose.staging.yml logs`
2. Verificar estado de DB: `python scripts/staging/01_verify_and_init_staging_db.py`
3. Consultar esta guía

## 🎉 ¡Listo!

Una vez completados estos pasos, tendrás:
- ✅ Servidor staging en puerto 8001
- ✅ Base de datos `paqueteria_staging` separada
- ✅ Datos independientes de producción
- ✅ Ambiente seguro para pruebas

---

**Última actualización**: 2026-01-29  
**Versión**: 1.0.0
