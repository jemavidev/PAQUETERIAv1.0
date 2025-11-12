# 📋 Resumen de Configuración - PAQUETERÍA v1.0 PROD

## ✅ Cambios Realizados

### 1. Stack de Contenedores
- **Nombre del stack**: `PAQUETERIA v1.0 PROD`
- **Contenedores renombrados**:
  - `paqueteria_v1_prod_redis`
  - `paqueteria_v1_prod_app`
  - `paqueteria_v1_prod_celery`
- **Red Docker**: `paqueteria_v1_prod_network`

### 2. Rutas Corregidas
- Cambiado de `CODE/LOCAL` a `CODE`
- Archivo `.env` ahora en `CODE/.env`
- Configuración actualizada para usar `CODE/.env`

### 3. Configuración Actualizada
- `docker-compose.prod.yml` actualizado
- `config.py` actualizado para usar variables de entorno
- `Dockerfile` corregido
- `alembic.ini` actualizado para usar `DATABASE_URL` del .env

## 📁 Archivos Creados/Modificados

### Archivos Modificados:
1. `docker-compose.prod.yml` - Stack renombrado y rutas corregidas
2. `CODE/src/app/config.py` - Configuración para usar variables de entorno
3. `CODE/Dockerfile` - Comando de inicio corregido
4. `CODE/alembic.ini` - Usa variables de entorno

### Archivos Creados:
1. `CODE/env.example` - Plantilla de variables de entorno
2. `CONFIGURACION_RDS.md` - Guía completa de configuración
3. `RESUMEN_CONFIGURACION.md` - Este archivo

## 🔧 Lo que Necesitas para Ejecutar

### 1. Archivo .env

**Ubicación**: `CODE/.env`

**Crear desde plantilla**:
```bash
cd "PAQUETERIA v1.0"
cp CODE/env.example CODE/.env
```

**Editar con tus valores reales**:
```bash
nano CODE/.env
# o
vim CODE/.env
```

### 2. Variables OBLIGATORIAS

```bash
# Base de Datos RDS
DATABASE_URL=postgresql://usuario:password@tu-rds-endpoint.us-east-1.rds.amazonaws.com:5432/paqueteria_v4

# Seguridad
SECRET_KEY=tu-secret-key-super-seguro-generar-con-openssl-rand-hex-32
ALGORITHM=HS256

# Redis
REDIS_PASSWORD=tu_redis_password_seguro

# AWS S3 (recomendado)
AWS_ACCESS_KEY_ID=tu_aws_access_key_id
AWS_SECRET_ACCESS_KEY=tu_aws_secret_access_key
AWS_S3_BUCKET=tu-bucket-s3-paqueteria
AWS_REGION=us-east-1
```

### 3. Generar SECRET_KEY

```bash
# Generar una clave secreta segura
openssl rand -hex 32

# Copiar el resultado y pegarlo en SECRET_KEY en CODE/.env
```

### 4. Configurar Security Group de RDS

En AWS Console:
1. Ve a **RDS** → **Databases** → Selecciona tu instancia
2. Ve a **Connectivity & security** → **Security groups**
3. Edita el Security Group
4. Agrega una regla de entrada:
   - **Type**: PostgreSQL
   - **Port**: 5432
   - **Source**: Tu IP pública (o `0.0.0.0/0` para desarrollo, **NO recomendado para producción**)

### 5. Verificar Conexión a RDS

```bash
# Instalar cliente PostgreSQL (si no lo tienes)
# Ubuntu/Debian:
sudo apt-get install postgresql-client

# macOS:
brew install postgresql

# Probar conexión
psql -h tu-rds-endpoint.us-east-1.rds.amazonaws.com -U tu_usuario -d paqueteria_v4

# Si conecta correctamente, puedes salir con \q
```

## 🚀 Pasos para Ejecutar

### Paso 1: Crear archivo .env
```bash
cd "PAQUETERIA v1.0"
cp CODE/env.example CODE/.env
nano CODE/.env  # Editar con tus valores reales
```

### Paso 2: Configurar variables de entorno
Editar `CODE/.env` con:
- `DATABASE_URL` (RDS endpoint)
- `SECRET_KEY` (generar con `openssl rand -hex 32`)
- `REDIS_PASSWORD`
- Credenciales de AWS S3
- Credenciales de SMTP (opcional)
- Credenciales de LIWA.co (opcional)

### Paso 3: Ejecutar migraciones
```bash
# Opción 1: Desde el contenedor (recomendado)
docker compose -f docker-compose.prod.yml run --rm app alembic upgrade head

# Opción 2: Desde tu máquina local (si tienes Python instalado)
cd CODE
export $(cat .env | xargs)
alembic upgrade head
```

### Paso 4: Construir y ejecutar contenedores
```bash
# Construir las imágenes
docker compose -f docker-compose.prod.yml build

# Iniciar los servicios
docker compose -f docker-compose.prod.yml up -d

# Ver logs
docker compose -f docker-compose.prod.yml logs -f app
```

### Paso 5: Verificar que todo funciona
```bash
# Ver estado de los contenedores
docker compose -f docker-compose.prod.yml ps

# Verificar health check
curl http://localhost:8000/health

# Deberías ver una respuesta JSON con status: "healthy"
```

## 📊 Estructura de Archivos

```
PAQUETERIA v1.0/
├── CODE/
│   ├── .env                    # ← Archivo de configuración (crear desde env.example)
│   ├── env.example             # ← Plantilla de variables de entorno
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── src/
│   │   └── app/
│   │       └── config.py       # ← Lee variables de entorno
│   └── alembic/
│       └── env.py              # ← Usa DATABASE_URL del .env
├── docker-compose.prod.yml     # ← Stack: PAQUETERIA v1.0 PROD
├── CONFIGURACION_RDS.md        # ← Guía completa
└── RESUMEN_CONFIGURACION.md    # ← Este archivo
```

## 🐛 Solución de Problemas

### Error: No se puede conectar a RDS
1. Verificar que el Security Group de RDS permite tu IP
2. Verificar que el endpoint de RDS es correcto
3. Verificar que el puerto es 5432
4. Verificar que las credenciales son correctas
5. Verificar que la base de datos existe

### Error: Password contiene caracteres especiales
Si tu contraseña de RDS tiene caracteres especiales, usar URL encoding:
- `@` → `%40`
- `#` → `%23`
- `$` → `%24`
- `&` → `%26`
- `=` → `%3D`
- `?` → `%3F`
- `[` → `%5B`
- `]` → `%5D`

Ejemplo:
```
# Contraseña original: a?HC!2.*1#?[==:
# URL encoded: a%3FHC%212.%2A1%23%3F%5B%3D%3D%3A
DATABASE_URL=postgresql://usuario:a%3FHC%212.%2A1%23%3F%5B%3D%3D%3A@rds-endpoint:5432/paqueteria_v4
```

### Error: DATABASE_URL no encontrada
1. Verificar que el archivo `CODE/.env` existe
2. Verificar que `DATABASE_URL` está definida en el archivo
3. Verificar que no hay espacios alrededor del `=`
4. Verificar que la contraseña está correctamente codificada

## 🔐 Seguridad

### ⚠️ Importante:
1. **NUNCA** subas el archivo `.env` al repositorio
2. **NUNCA** compartas tus credenciales de AWS
3. **SIEMPRE** usa contraseñas seguras
4. **SIEMPRE** limita el acceso al Security Group de RDS
5. **SIEMPRE** rota tus credenciales periódicamente

## 📝 Checklist

- [ ] Docker y Docker Compose instalados
- [ ] Archivo `CODE/.env` creado desde `env.example`
- [ ] `DATABASE_URL` configurada con credenciales de RDS
- [ ] `SECRET_KEY` generada y configurada
- [ ] `REDIS_PASSWORD` configurada
- [ ] Credenciales de AWS S3 configuradas (opcional)
- [ ] Security Group de RDS configurado para permitir tu IP
- [ ] Conexión a RDS verificada
- [ ] Migraciones ejecutadas (`alembic upgrade head`)
- [ ] Contenedores construidos (`docker compose build`)
- [ ] Contenedores iniciados (`docker compose up -d`)
- [ ] Health check verificado (`curl http://localhost:8000/health`)

## 📞 Comandos Útiles

```bash
# Ver logs de la aplicación
docker compose -f docker-compose.prod.yml logs -f app

# Ver logs de Redis
docker compose -f docker-compose.prod.yml logs -f redis

# Ver logs de Celery
docker compose -f docker-compose.prod.yml logs -f celery_worker

# Reiniciar un servicio
docker compose -f docker-compose.prod.yml restart app

# Detener todos los servicios
docker compose -f docker-compose.prod.yml down

# Detener y eliminar volúmenes
docker compose -f docker-compose.prod.yml down -v

# Ejecutar migraciones
docker compose -f docker-compose.prod.yml run --rm app alembic upgrade head

# Ver estado de los contenedores
docker compose -f docker-compose.prod.yml ps
```

## 🎯 Próximos Pasos

1. **Crear archivo .env**: `cp CODE/env.example CODE/.env`
2. **Configurar variables**: Editar `CODE/.env` con tus valores reales
3. **Generar SECRET_KEY**: `openssl rand -hex 32`
4. **Configurar Security Group**: Permitir tu IP en RDS
5. **Verificar conexión**: `psql -h tu-rds-endpoint -U tu_usuario -d paqueteria_v4`
6. **Ejecutar migraciones**: `docker compose -f docker-compose.prod.yml run --rm app alembic upgrade head`
7. **Construir contenedores**: `docker compose -f docker-compose.prod.yml build`
8. **Iniciar servicios**: `docker compose -f docker-compose.prod.yml up -d`
9. **Verificar health**: `curl http://localhost:8000/health`

---

**¡Listo!** Ahora deberías poder ejecutar PAQUETERÍA v1.0 en localhost usando AWS RDS. 🎉

Para más información, consulta `CONFIGURACION_RDS.md`.

