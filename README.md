# 🚀 PAQUETEX v4.0 - Sistema de Gestión de Paquetería

Sistema completo de gestión de paquetería con recepción, almacenamiento y entrega de paquetes.

## 📋 Descripción

PAQUETEX es un sistema web desarrollado con FastAPI (Python) que permite gestionar el ciclo completo de paquetes:
- Anuncio de paquetes
- Recepción con documentación fotográfica
- Almacenamiento con sistema de posiciones
- Entrega con registro de pagos
- Notificaciones por SMS y Email

## 🚀 Inicio Rápido

### Desarrollo Local

```bash
# 1. Levantar servicios
./deploy.sh --env localhost --deploy

# 2. Acceder a la aplicación
http://localhost:8000
```

### Deploy a Producción

```bash
# Deploy a servidor AWS (papyrus)
./deploy.sh --env papyrus --deploy
```

Ver documentación completa: [README_DEPLOY.md](README_DEPLOY.md)

## 📁 Estructura del Proyecto

```
/
├── CODE/                        # Código fuente de la aplicación
│   ├── src/                     # Código Python
│   │   ├── app/                 # Aplicación FastAPI
│   │   ├── static/              # Archivos estáticos
│   │   └── templates/           # Templates HTML
│   ├── alembic/                 # Migraciones de BD
│   └── requirements.txt         # Dependencias Python
│
├── deploy.sh                    # Sistema de deploy (ejecutable principal)
├── .deploy/                     # Configuración de deploy
│
├── scripts/                     # Scripts utilitarios
│   ├── deploy/                  # Scripts de deploy
│   ├── testing/                 # Scripts de pruebas
│   ├── sync/                    # Scripts de sincronización
│   └── utils/                   # Utilidades
│
├── DOCS/                        # Documentación
│   ├── analisis/                # Análisis de problemas
│   ├── fixes/                   # Documentación de fixes
│   ├── pruebas/                 # Documentación de pruebas
│   ├── resumenes/               # Resúmenes ejecutivos
│   ├── deploy/                  # Docs de deploy
│   ├── guides/                  # Guías y tutoriales
│   └── archived/                # Archivos antiguos
│
├── docker-compose.*.yml         # Configuraciones Docker
└── README_DEPLOY.md             # Guía de deploy
```

## 🛠️ Tecnologías

### Backend
- **FastAPI** - Framework web Python
- **PostgreSQL** - Base de datos
- **Redis** - Caché y sesiones
- **Alembic** - Migraciones de BD
- **SQLAlchemy** - ORM

### Frontend
- **Jinja2** - Templates
- **TailwindCSS** - Estilos
- **JavaScript** - Interactividad

### Infraestructura
- **Docker** - Contenedores
- **Nginx** - Reverse proxy
- **AWS Lightsail** - Hosting
- **AWS S3** - Almacenamiento de imágenes

## 🔧 Configuración

### Variables de Entorno

Copiar y configurar:
```bash
cp CODE/env.example CODE/.env
```

Variables principales:
- `DATABASE_URL` - Conexión a PostgreSQL
- `REDIS_URL` - Conexión a Redis
- `AWS_ACCESS_KEY_ID` - Credenciales AWS
- `AWS_SECRET_ACCESS_KEY` - Credenciales AWS
- `AWS_S3_BUCKET_NAME` - Bucket S3

### Base de Datos

```bash
# Ejecutar migraciones
./deploy.sh --env localhost --migrations
```

## 📚 Documentación

### Guías Principales
- [README_DEPLOY.md](README_DEPLOY.md) - Sistema de deploy
- [DOCS/guides/](DOCS/guides/) - Guías y tutoriales

### Documentación Técnica
- [DOCS/fixes/](DOCS/fixes/) - Soluciones a problemas
- [DOCS/deploy/](DOCS/deploy/) - Documentación de deploy

### Scripts
- [scripts/deploy/](scripts/deploy/) - Scripts de deploy
- [scripts/sync/](scripts/sync/) - Scripts de sincronización

## 🎯 Funcionalidades Principales

### 1. Gestión de Paquetes
- ✅ Anuncio de paquetes
- ✅ Recepción con fotos (AWS S3)
- ✅ Sistema de posiciones (BAROTI)
- ✅ Entrega con registro de pago
- ✅ Cancelación de paquetes

### 2. Gestión de Clientes
- ✅ Registro de clientes
- ✅ Historial de paquetes
- ✅ Notificaciones automáticas

### 3. Notificaciones
- ✅ SMS automáticos (cambios de estado)
- ✅ Emails con templates personalizados
- ✅ Notificaciones en tiempo real

### 4. Reportes
- ✅ Reportes de paquetes
- ✅ Estadísticas de operación
- ✅ Exportación de datos

## 🚀 Deploy

### Entornos Disponibles

```bash
# Desarrollo local
./deploy.sh --env localhost --deploy

# Servidor de producción (AWS)
./deploy.sh --env papyrus --deploy

# Servidor de staging
./deploy.sh --env staging --deploy
```

Ver documentación completa: [README_DEPLOY.md](README_DEPLOY.md)

## 🔒 Seguridad

- ✅ Autenticación con JWT
- ✅ Roles de usuario (Admin, Operador, Cliente)
- ✅ Validación de datos
- ✅ Protección CSRF
- ✅ HTTPS en producción
- ✅ Backups automáticos

## 📊 Monitoreo

```bash
# Ver estado de servicios
./deploy.sh --env papyrus --status

# Ver logs en tiempo real
./deploy.sh --env papyrus --logs

# Health check
./deploy.sh --env papyrus --health
```

## 🐛 Troubleshooting

### Problemas Comunes

Ver documentación de fixes: [DOCS/fixes/](DOCS/fixes/)

### Logs

```bash
# Logs de la aplicación
./deploy.sh --env localhost --logs

# Logs de Docker
docker compose logs -f app
```

## 🤝 Contribuir

1. Crear rama de feature
2. Hacer cambios
3. Probar en localhost
4. Deploy a staging
5. Merge a main
6. Deploy a producción

## 📞 Soporte

- Documentación: [DOCS/](DOCS/)
- Guías: [DOCS/guides/](DOCS/guides/)
- Fixes: [DOCS/fixes/](DOCS/fixes/)

## 📝 Changelog

### v4.0.0 (2024-12-07)
- ✅ Sistema de deploy unificado
- ✅ Mejoras en caché (invalidación automática)
- ✅ Modal de posición rediseñado
- ✅ Documentación completa reorganizada
- ✅ Fix de visualización de imágenes (S3)
- ✅ Corrección de validación de roles
- ✅ Portal de clientes con OTP
- ✅ Scripts de pruebas automatizadas

### v3.x
- Sistema de notificaciones
- Integración con AWS S3
- Sistema de posiciones BAROTI

## 📄 Licencia

Propietario - PAQUETEX © 2024

---

**Versión:** 4.0.0  
**Última actualización:** 2024-12-07  
**Servidor:** AWS Lightsail (papyrus)  
**URL:** https://paquetex.papyrus.com.co

---

## 📂 Organización de Archivos

### Documentación (`DOCS/`)
- **analisis/** - Análisis de problemas y diagnósticos
- **fixes/** - Soluciones y correcciones aplicadas
- **pruebas/** - Documentación de pruebas
- **resumenes/** - Resúmenes ejecutivos

### Scripts (`scripts/`)
- **deploy/** - Scripts de deploy y limpieza
- **testing/** - Scripts de pruebas automatizadas
- **sync/** - Scripts de sincronización
- **utils/** - Utilidades generales

Ver README en cada carpeta para más detalles.
