# 🎯 Instrucciones: Crear Base de Datos Staging

## ⚠️ IMPORTANTE

El servidor AWS RDS no es accesible desde tu máquina local (por seguridad).
Necesitas ejecutar los comandos desde un servidor que tenga acceso a RDS.

---

## 📍 OPCIONES PARA EJECUTAR

### Opción 1: Desde el Servidor de Producción (Recomendada)

```bash
# 1. Conectar al servidor de producción
ssh usuario@servidor-produccion

# 2. Navegar al directorio del proyecto
cd /ruta/al/proyecto

# 3. Ejecutar el script
./scripts/database/create_staging_database_docker.sh
```

### Opción 2: Desde el Servidor de Staging

```bash
# 1. Conectar al servidor de staging
ssh usuario@servidor-staging

# 2. Navegar al directorio del proyecto
cd /ruta/al/proyecto

# 3. Ejecutar el script
./scripts/database/create_staging_database_docker.sh
```

### Opción 3: Manualmente con Docker (Desde cualquier servidor con acceso a RDS)

```bash
# Crear la base de datos
docker run --rm \
  -e PGPASSWORD='a?HC!2.*1#?[==:|289qAI=)#V4kDzl$' \
  postgres:15-alpine \
  psql \
    -h ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com \
    -U jveyes \
    -d postgres \
    -c "CREATE DATABASE paqueteria_staging OWNER jveyes;"

# Verificar creación
docker run --rm \
  -e PGPASSWORD='a?HC!2.*1#?[==:|289qAI=)#V4kDzl$' \
  postgres:15-alpine \
  psql \
    -h ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com \
    -U jveyes \
    -d postgres \
    -c "SELECT datname, pg_size_pretty(pg_database_size(datname)) as size FROM pg_database WHERE datname IN ('paqueteria_v4', 'paqueteria_staging') ORDER BY datname;"
```

### Opción 4: Desde AWS Console (Más fácil)

1. Ir a AWS RDS Console
2. Seleccionar tu instancia RDS
3. Click en "Query Editor" o conectar con pgAdmin
4. Ejecutar:
```sql
CREATE DATABASE paqueteria_staging OWNER jveyes;
```

---

## 🔍 VERIFICAR QUE SE CREÓ

Desde cualquier servidor con acceso a RDS:

```bash
docker run --rm \
  -e PGPASSWORD='a?HC!2.*1#?[==:|289qAI=)#V4kDzl$' \
  postgres:15-alpine \
  psql \
    -h ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com \
    -U jveyes \
    -d postgres \
    -c "\l"
```

Deberías ver:
```
     Name          |  Owner   | Encoding |   Size    
-------------------+----------+----------+-----------
 paqueteria_v4     | jveyes   | UTF8     | 150 MB
 paqueteria_staging| jveyes   | UTF8     | 8192 kB
```

---

## 📋 DESPUÉS DE CREAR LA BASE DE DATOS

### 1. Sincronizar Datos (Desde servidor con acceso a RDS)

```bash
./scripts/database/sync_prod_to_staging_initial.sh
```

O manualmente:

```bash
# Exportar producción
docker run --rm \
  -e PGPASSWORD='a?HC!2.*1#?[==:|289qAI=)#V4kDzl$' \
  -v $(pwd):/backup \
  postgres:15-alpine \
  pg_dump \
    -h ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com \
    -U jveyes \
    -d paqueteria_v4 \
    --no-owner \
    --no-acl \
    -F c \
    -f /backup/prod_backup.dump

# Importar a staging
docker run --rm \
  -e PGPASSWORD='a?HC!2.*1#?[==:|289qAI=)#V4kDzl$' \
  -v $(pwd):/backup \
  postgres:15-alpine \
  pg_restore \
    -h ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com \
    -U jveyes \
    -d paqueteria_staging \
    --clean \
    --if-exists \
    --no-owner \
    --no-acl \
    /backup/prod_backup.dump
```

### 2. Aplicar Migraciones de Staging

```bash
cd CODE
DATABASE_URL="postgresql://jveyes:a?HC!2.*1#?[==:|289qAI=)#V4kDzl$@ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com:5432/paqueteria_staging" \
  alembic upgrade head
```

### 3. Iniciar Staging

```bash
docker-compose -f docker-compose.staging.yml up -d
```

### 4. Verificar

```bash
# Ver logs
docker-compose -f docker-compose.staging.yml logs -f app

# Probar endpoint
curl http://localhost:8001/health
```

---

## 🚨 SI NO TIENES ACCESO A RDS

Si no puedes acceder a RDS desde ningún servidor, necesitas:

1. **Configurar Security Group en AWS:**
   - Ir a AWS RDS Console
   - Seleccionar tu instancia
   - Ir a "Security groups"
   - Agregar regla de entrada:
     - Type: PostgreSQL
     - Port: 5432
     - Source: Tu IP o 0.0.0.0/0 (menos seguro)

2. **O usar AWS Systems Manager Session Manager:**
   ```bash
   aws ssm start-session --target instance-id
   ```

3. **O usar un bastion host:**
   - Crear EC2 pequeño con acceso a RDS
   - Conectar por SSH
   - Ejecutar comandos desde ahí

---

## 📊 RESUMEN DE ARCHIVOS PREPARADOS

Todos estos archivos están listos en tu repositorio:

```
✅ .env.production              - Backup de producción
✅ .env.staging                 - Config staging (paqueteria_staging)
✅ docker-compose.staging.yml   - Actualizado para usar .env.staging
✅ scripts/database/create_staging_database_docker.sh
✅ scripts/database/sync_prod_to_staging_initial.sh
✅ scripts/database/sync_prod_to_staging_daily.sh
```

Solo necesitas ejecutarlos desde un servidor con acceso a RDS.

---

## 🎯 ALTERNATIVA: Crear DB Staging Localmente

Si quieres probar localmente sin AWS RDS:

```bash
# 1. Iniciar PostgreSQL local
docker run --name postgres-local -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres:15-alpine

# 2. Crear base de datos staging local
docker exec postgres-local psql -U postgres -c "CREATE DATABASE paqueteria_staging;"

# 3. Actualizar .env.staging para usar DB local
DATABASE_URL="postgresql://postgres:postgres@localhost:5432/paqueteria_staging"

# 4. Aplicar migraciones
cd CODE
alembic upgrade head

# 5. Iniciar staging
docker-compose -f docker-compose.staging.yml up -d
```

---

## 💡 RECOMENDACIÓN

La forma más fácil es:

1. **Usar AWS Console** para crear la base de datos
2. **Copiar los scripts** al servidor de producción/staging
3. **Ejecutar desde ahí** la sincronización

O si prefieres, puedo ayudarte a configurar el acceso a RDS desde tu máquina local.

---

**Creado:** 27 de enero de 2026  
**Estado:** Archivos preparados, pendiente de ejecución en servidor con acceso a RDS
