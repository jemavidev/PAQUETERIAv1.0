# PAQUETERÍA v1.0 - Versión de Producción

## 📋 Información

Esta es la versión de producción del sistema PAQUETERÍA v4.0.

**Fecha de creación**: 2025-01-24  
**Versión**: 1.0.0  
**Estado**: Producción  
**Stack**: PAQUETERIA v1.0 PROD

---

## 🚀 Inicio Rápido

### Requisitos Previos

- Docker y Docker Compose instalados
- Archivo `.env` configurado en la raíz del proyecto
- Credenciales de AWS RDS configuradas
- Credenciales de AWS S3 configuradas

### Despliegue

```bash
# 1. Configurar variables de entorno
# Editar .env con valores de producción

# 2. Ejecutar migraciones (si es necesario)
docker compose -f docker-compose.prod.yml run --rm app alembic upgrade head

# 3. Iniciar servicios
docker compose -f docker-compose.prod.yml up -d

# O usar el script de inicio
./start.sh
```

---

## 📁 Estructura

```
PAQUETERIA v1.0/
├── CODE/
│   ├── src/                  # Código fuente
│   ├── alembic/              # Migraciones
│   ├── requirements.txt      # Dependencias
│   ├── Dockerfile            # Imagen Docker
│   └── env.example           # Plantilla de variables de entorno
├── DOCS/                     # Documentación y archivos no esenciales
│   ├── documentacion/        # Documentación del proyecto
│   ├── scripts/              # Scripts (despliegue, base de datos, monitoreo)
│   │   └── deployment/       # Scripts de despliegue esenciales
│   ├── tests/                # Tests
│   ├── templates-prueba/     # Templates de prueba/debug
│   └── componentes-docs/     # Documentación interna
├── docker-compose.prod.yml   # Docker Compose producción
├── start.sh                  # Script de inicio
├── .env                      # Variables de entorno (crear desde env.example)
└── README.md                 # Este archivo
```

---

## 🔧 Configuración

### Variables de Entorno

Crear `.env` en la raíz del proyecto (usar `CODE/env.example` como plantilla):

- `DATABASE_URL` - URL de PostgreSQL (AWS RDS)
- `SECRET_KEY` - Clave secreta para JWT
- `AWS_ACCESS_KEY_ID` - Credenciales AWS
- `AWS_SECRET_ACCESS_KEY` - Credenciales AWS
- `AWS_S3_BUCKET` - Bucket de S3
- `REDIS_PASSWORD` - Contraseña de Redis
- Y otras variables según necesidad

### Configuración Rápida

```bash
# Copiar plantilla
cp CODE/env.example .env

# Editar con tus valores
nano .env

# Generar SECRET_KEY
openssl rand -hex 32
```

---

## 📚 Documentación

Toda la documentación detallada está en la carpeta `DOCS/`:

### Documentación Técnica Principal

- **🐳 Contenedores Docker**: `DOCS/documentacion/DOCUMENTACION_CONTENEDORES.md` - Descripción detallada de todos los contenedores del stack
- **⚙️ Servicios de la Aplicación**: `DOCS/documentacion/DOCUMENTACION_SERVICIOS.md` - Documentación completa de todos los servicios y su funcionalidad

### Documentación de Configuración

- **Configuración RDS**: `DOCS/documentacion/CONFIGURACION_RDS.md`
- **Configuración ENV**: `DOCS/documentacion/CONFIGURACION_ENV.md`
- **Inicio Rápido**: `DOCS/documentacion/README_INICIO_RAPIDO.md`
- **Despliegue**: `DOCS/documentacion/README_DEPLOY.md`
- **Seguridad**: `DOCS/documentacion/SECURITY.md`
- **Implementación**: `DOCS/documentacion/IMPLEMENTACION.md`
- **Índice completo**: `DOCS/README.md`

---

## 🎯 Comandos Útiles

```bash
# Iniciar servicios
./start.sh

# Ver logs
docker compose -f docker-compose.prod.yml logs -f app

# Ver estado
docker compose -f docker-compose.prod.yml ps

# Reiniciar aplicación
docker compose -f docker-compose.prod.yml restart app

# Detener servicios
docker compose -f docker-compose.prod.yml down

# Ejecutar migraciones
docker compose -f docker-compose.prod.yml run --rm app alembic upgrade head
```

---

## ✅ Características

- ✅ Hot Reload activado (cambios sin reiniciar)
- ✅ Conectado a AWS RDS
- ✅ Almacenamiento en AWS S3
- ✅ Email SMTP configurado
- ✅ SMS LIWA.co configurado
- ✅ **Celery Worker** - Tareas asíncronas
- ✅ **Celery Beat** - Tareas programadas
- ✅ **Prometheus** - Métricas y monitoreo
- ✅ **Grafana** - Dashboards de monitoreo
- ✅ **Node Exporter** - Métricas del sistema
- ✅ Logs estructurados
- ✅ Health checks

---

## 🆘 Soporte

Para problemas o preguntas, consultar la documentación en `DOCS/documentacion/`.

---

**Versión de Producción - PAQUETERÍA v1.0**
