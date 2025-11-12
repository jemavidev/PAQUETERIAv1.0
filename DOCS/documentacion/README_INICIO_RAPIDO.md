# 🚀 Inicio Rápido - PAQUETERÍA v1.0 PROD

## ⚡ Inicio Rápido en 3 Pasos

### 1. Configurar Variables de Entorno

```bash
# Editar el archivo .env con tus valores reales
nano CODE/.env
```

**Variables OBLIGATORIAS:**
- `DATABASE_URL` - URL de conexión a RDS
- `REDIS_PASSWORD` - Contraseña de Redis
- `AWS_ACCESS_KEY_ID` - Clave de acceso de AWS
- `AWS_SECRET_ACCESS_KEY` - Clave secreta de AWS
- `AWS_S3_BUCKET` - Nombre del bucket S3

**NOTA:** La `SECRET_KEY` ya fue generada automáticamente.

### 2. Configurar Security Group de RDS

En AWS Console, permitir tu IP en el Security Group de RDS:
- **Type**: PostgreSQL
- **Port**: 5432
- **Source**: Tu IP pública

### 3. Ejecutar el Sistema

```bash
# Opción 1: Script automatizado (recomendado)
./start.sh

# Opción 2: Manual
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml run --rm app alembic upgrade head
docker compose -f docker-compose.prod.yml up -d
```

## ✅ Verificar que Funciona

```bash
# Verificar health check
curl http://localhost:8000/health

# Ver logs
docker compose -f docker-compose.prod.yml logs -f app

# Ver estado
docker compose -f docker-compose.prod.yml ps
```

## 📋 Variables de Entorno Requeridas

### OBLIGATORIAS:

```bash
DATABASE_URL=postgresql://usuario:password@rds-endpoint.us-east-1.rds.amazonaws.com:5432/paqueteria_v4
REDIS_PASSWORD=tu_redis_password_seguro
AWS_ACCESS_KEY_ID=tu_aws_access_key_id
AWS_SECRET_ACCESS_KEY=tu_aws_secret_access_key
AWS_S3_BUCKET=tu-bucket-s3-paqueteria
AWS_REGION=us-east-1
```

### RECOMENDADAS:

```bash
SMTP_HOST=smtp.tu-servidor.com
SMTP_PORT=587
SMTP_USER=tu_email@dominio.com
SMTP_PASSWORD=tu_password_email
LIWA_API_KEY=tu_liwa_api_key
LIWA_ACCOUNT=tu_liwa_account
LIWA_PASSWORD=tu_liwa_password
```

## 🐛 Solución de Problemas

### Error: No se puede conectar a RDS
- Verificar que el Security Group permite tu IP
- Verificar que el endpoint de RDS es correcto
- Verificar que las credenciales son correctas

### Error: Password contiene caracteres especiales
Usar URL encoding:
- `@` → `%40`
- `#` → `%23`
- `$` → `%24`
- `&` → `%26`
- `=` → `%3D`
- `?` → `%3F`
- `[` → `%5B`
- `]` → `%5D`

## 📞 Comandos Útiles

```bash
# Ver logs
docker compose -f docker-compose.prod.yml logs -f app

# Reiniciar
docker compose -f docker-compose.prod.yml restart app

# Detener
docker compose -f docker-compose.prod.yml down

# Ejecutar migraciones
docker compose -f docker-compose.prod.yml run --rm app alembic upgrade head
```

## 📚 Documentación Completa

- `CONFIGURACION_RDS.md` - Guía completa de configuración
- `RESUMEN_CONFIGURACION.md` - Resumen de configuración
- `IMPLEMENTACION.md` - Estado de la implementación

---

**¡Listo!** 🎉 Solo falta configurar el archivo `.env` con tus valores reales.

