# 📋 Configuración para ejecutar con AWS RDS en localhost

## 🎯 Resumen

Esta guía explica cómo configurar y ejecutar **PAQUETERÍA v1.0** en localhost usando una base de datos PostgreSQL en AWS RDS.

## ✅ Cambios Realizados

1. **Stack de contenedores renombrado**: `PAQUETERIA v1.0 PROD`
2. **Rutas corregidas**: Cambiado de `CODE/LOCAL` a `CODE`
3. **Configuración de .env**: Actualizada para usar `CODE/.env`
4. **Dockerfile corregido**: Comando de inicio actualizado
5. **Alembic configurado**: Usa variables de entorno para RDS

## 📋 Requisitos Previos

### 1. Software Necesario

- **Docker** (versión 20.10 o superior)
- **Docker Compose** (versión 2.0 o superior)
- **Git** (para clonar el repositorio)
- **Acceso a AWS RDS** (endpoint, usuario, contraseña)

### 2. Credenciales de AWS RDS

Necesitas tener:
- **Endpoint de RDS**: `tu-rds-endpoint.us-east-1.rds.amazonaws.com`
- **Puerto**: `5432` (por defecto)
- **Usuario de base de datos**: `tu_usuario`
- **Contraseña**: `tu_password`
- **Nombre de la base de datos**: `paqueteria_v4` (o el que hayas creado)

### 3. Credenciales de AWS S3 (opcional pero recomendado)

- **AWS_ACCESS_KEY_ID**
- **AWS_SECRET_ACCESS_KEY**
- **AWS_REGION**: `us-east-1` (o la región de tu bucket)
- **AWS_S3_BUCKET**: Nombre de tu bucket S3

### 4. Configuración de RDS

Asegúrate de que tu instancia RDS:
- ✅ Permite conexiones desde tu IP local (Security Groups)
- ✅ Tiene el puerto 5432 abierto
- ✅ Tiene la base de datos creada
- ✅ Tiene el usuario configurado con permisos adecuados

## 🔧 Pasos de Configuración

### Paso 1: Crear archivo .env

```bash
# Ir al directorio del proyecto
cd "PAQUETERIA v1.0"

# Copiar el archivo de ejemplo
cp CODE/env.example CODE/.env

# Editar el archivo .env con tus valores reales
nano CODE/.env
# o
vim CODE/.env
```

### Paso 2: Configurar Variables de Entorno

Edita `CODE/.env` y configura las siguientes variables **OBLIGATORIAS**:

#### 🔴 Variables OBLIGATORIAS:

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

#### 🟡 Variables RECOMENDADAS:

```bash
# SMTP (para emails)
SMTP_HOST=smtp.tu-servidor.com
SMTP_PORT=587
SMTP_USER=tu_email@dominio.com
SMTP_PASSWORD=tu_password_email
SMTP_FROM_EMAIL=tu_email@dominio.com

# SMS (LIWA.co)
LIWA_API_KEY=tu_liwa_api_key
LIWA_ACCOUNT=tu_liwa_account
LIWA_PASSWORD=tu_liwa_password
```

### Paso 3: Generar SECRET_KEY

```bash
# Generar una clave secreta segura
openssl rand -hex 32

# Copiar el resultado y pegarlo en SECRET_KEY en el archivo .env
```

### Paso 4: Configurar Security Group de RDS

En AWS Console:
1. Ve a **RDS** → **Databases** → Selecciona tu instancia
2. Ve a **Connectivity & security** → **Security groups**
3. Edita el Security Group
4. Agrega una regla de entrada:
   - **Type**: PostgreSQL
   - **Port**: 5432
   - **Source**: Tu IP pública (o `0.0.0.0/0` para desarrollo, **NO recomendado para producción**)

### Paso 5: Verificar Conexión a RDS

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

### Paso 6: Ejecutar Migraciones

```bash
# Opción 1: Desde el contenedor (recomendado)
docker compose -f docker-compose.prod.yml run --rm app alembic upgrade head

# Opción 2: Desde tu máquina local (si tienes Python instalado)
cd CODE
export $(cat .env | xargs)
alembic upgrade head
```

### Paso 7: Iniciar Contenedores

```bash
# Construir las imágenes
docker compose -f docker-compose.prod.yml build

# Iniciar los servicios
docker compose -f docker-compose.prod.yml up -d

# Ver logs
docker compose -f docker-compose.prod.yml logs -f app
```

### Paso 8: Verificar que todo funciona

```bash
# Verificar estado de los contenedores
docker compose -f docker-compose.prod.yml ps

# Verificar health check
curl http://localhost:8000/health

# Deberías ver una respuesta JSON con status: "healthy"
```

## 🐛 Solución de Problemas

### Error: No se puede conectar a RDS

**Problema**: `Connection refused` o `timeout`

**Soluciones**:
1. Verificar que el Security Group de RDS permite tu IP
2. Verificar que el endpoint de RDS es correcto
3. Verificar que el puerto es 5432
4. Verificar que las credenciales son correctas
5. Verificar que la base de datos existe

### Error: DATABASE_URL no encontrada

**Problema**: `DATABASE_URL environment variable is required`

**Soluciones**:
1. Verificar que el archivo `CODE/.env` existe
2. Verificar que `DATABASE_URL` está definida en el archivo
3. Verificar que no hay espacios alrededor del `=`
4. Verificar que la contraseña no tiene caracteres especiales sin escapar

### Error: Password contiene caracteres especiales

**Problema**: Contraseña de RDS tiene caracteres especiales como `@`, `#`, `$`, etc.

**Soluciones**:
1. **URL encode**: Escapar caracteres especiales en la URL
   - `@` → `%40`
   - `#` → `%23`
   - `$` → `%24`
   - `&` → `%26`
   - `=` → `%3D`
   - `?` → `%3F`
   - `[` → `%5B`
   - `]` → `%5D`

2. **Ejemplo**:
   ```
   # Contraseña original: a?HC!2.*1#?[==:
   # URL encoded: a%3FHC%212.%2A1%23%3F%5B%3D%3D%3A
   DATABASE_URL=postgresql://usuario:a%3FHC%212.%2A1%23%3F%5B%3D%3D%3A@rds-endpoint:5432/paqueteria_v4
   ```

3. **Usar comillas** (si tu shell lo permite):
   ```bash
   DATABASE_URL="postgresql://usuario:password@rds-endpoint:5432/paqueteria_v4"
   ```

### Error: Alembic no encuentra los modelos

**Problema**: `No module named 'app.models'`

**Soluciones**:
1. Verificar que el PYTHONPATH está configurado correctamente
2. Verificar que los modelos están importados en `alembic/env.py`
3. Verificar que el Dockerfile copia correctamente los archivos

### Error: Redis no conecta

**Problema**: `Connection refused` a Redis

**Soluciones**:
1. Verificar que el contenedor de Redis está corriendo
2. Verificar que `REDIS_PASSWORD` está configurada correctamente
3. Verificar que `REDIS_URL` usa la contraseña correcta

## 📊 Estructura de Archivos

```
PAQUETERIA v1.0/
├── CODE/
│   ├── .env                    # ← Archivo de configuración (crear desde env.example)
│   ├── env.example             # ← Archivo de ejemplo
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── src/
│   │   └── app/
│   │       └── config.py       # ← Lee CODE/.env
│   └── alembic/
│       └── env.py              # ← Usa DATABASE_URL del .env
├── docker-compose.prod.yml     # ← Stack: PAQUETERIA v1.0 PROD
└── CONFIGURACION_RDS.md        # ← Esta guía
```

## 🔐 Seguridad

### ⚠️ Importante:

1. **NUNCA** subas el archivo `.env` al repositorio
2. **NUNCA** compartas tus credenciales de AWS
3. **SIEMPRE** usa contraseñas seguras
4. **SIEMPRE** limita el acceso al Security Group de RDS
5. **SIEMPRE** usa HTTPS en producción
6. **SIEMPRE** rota tus credenciales periódicamente

## 📝 Checklist de Configuración

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

## 🚀 Comandos Útiles

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

# Crear nueva migración
docker compose -f docker-compose.prod.yml run --rm app alembic revision --autogenerate -m "descripcion"

# Acceder al shell del contenedor
docker compose -f docker-compose.prod.yml exec app sh

# Ver estado de los contenedores
docker compose -f docker-compose.prod.yml ps
```

## 📞 Soporte

Si tienes problemas:
1. Revisa los logs: `docker compose -f docker-compose.prod.yml logs -f`
2. Verifica la configuración en `CODE/.env`
3. Verifica la conectividad a RDS
4. Revisa esta guía de solución de problemas
5. Contacta al equipo de desarrollo

---

**¡Listo!** Ahora deberías poder ejecutar PAQUETERÍA v1.0 en localhost usando AWS RDS. 🎉

