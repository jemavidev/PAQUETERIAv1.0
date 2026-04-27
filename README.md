# 📦 PAQUETEX EL CLUB v1.0

Sistema de gestión de paquetería para PAQUETES EL CLUB.

---

## 🚀 Inicio Rápido

```bash
# 1. Clonar el repositorio
git clone <repository-url>
cd "PAQUETEX v1.0"

# 2. Configurar variables de entorno
cp CODE/.env.staging.example CODE/.env.staging
# Editar CODE/.env.staging con tus credenciales

# 3. Levantar el proyecto
docker compose -f docker-compose.staging.yml up -d

# 4. Acceder
# http://localhost:8001
```

---

## 📚 Documentación

Toda la documentación está organizada en la carpeta [`DOCS/`](./DOCS/):

- 🚀 **[Inicio Rápido](./DOCS/00-inicio/)** - Empieza aquí
- 🏗️ **[Arquitectura](./DOCS/01-arquitectura/)** - Diseño del sistema
- ⚙️ **[Configuración](./DOCS/02-configuracion/)** - Setup de entornos
- 🚀 **[Despliegue](./DOCS/03-despliegue/)** - Guías de deploy
- 🗄️ **[Base de Datos](./DOCS/04-base-datos/)** - Documentación de BD
- ✨ **[Features](./DOCS/05-features/)** - Funcionalidades
- 🔧 **[Fixes](./DOCS/06-fixes/)** - Soluciones a problemas
- 📊 **[Análisis](./DOCS/07-analisis/)** - Análisis técnicos

---

## 🏗️ Estructura del Proyecto

```
PAQUETEX v1.0/
├── CODE/                    # Código de la aplicación
│   ├── src/                # Código fuente
│   ├── tests/              # Tests
│   ├── alembic/            # Migraciones de BD
│   └── requirements.txt    # Dependencias Python
├── DOCS/                    # Documentación organizada
├── scripts/                 # Scripts de utilidad
│   ├── database/           # Scripts de BD
│   ├── deployment/         # Scripts de deploy
│   ├── staging/            # Scripts de staging
│   └── maintenance/        # Scripts de mantenimiento
├── .deploy/                 # Sistema de deploy
├── docker-compose*.yml      # Configuraciones Docker
└── deploy.sh               # Script principal de deploy
```

---

## 🗄️ Base de Datos

El proyecto usa **PostgreSQL en AWS RDS** (sin bases de datos locales):

- **Producción**: `paqueteria_v4` (Puerto 8000, Redis 6379)
- **Staging**: `paqueteria_staging` (Puerto 8001, Redis 6380)
- **Desarrollo**: `paqueteria_staging` (Puerto 8000, Redis 6379)

Ver [Arquitectura de Base de Datos](./DOCS/01-arquitectura/ARQUITECTURA_BASE_DATOS.md) para más detalles.

---

## 🚀 Despliegue

### Staging
```bash
./deploy.sh --env staging --deploy
```

### Producción
```bash
./deploy.sh --env papyrus --deploy
```

Ver [Guía de Despliegue](./DOCS/03-despliegue/DEPLOY_STAGING_CHECKLIST.md) para más información.

---

## 🔧 Scripts Útiles

```bash
# Sincronizar staging
python scripts/staging/sync_staging_SIMPLE.py

# Verificar instalación
bash scripts/staging/verificar_instalacion.sh

# Limpiar facturas
python scripts/maintenance/limpiar_facturas.py
```

Ver [Scripts README](./scripts/README.md) para lista completa.

---

## 🤖 BetterAgentX - Sistema de Agentes IA

El proyecto integra **BetterAgentX**, un sistema inteligente de 13 agentes especializados para desarrollo:

```bash
# Inicializar BetterAgentX
./init-betteragentx.sh

# Usar en Kiro
@agentx "Ayúdame con el proyecto"
```

**Documentación:**
- ⚡ [Inicio Rápido](QUICKSTART-BETTERAGENTX.md)
- 📖 [Guía Completa](README-BETTERAGENTX.md)
- 📚 [Índice](INDEX-BETTERAGENTX.md)

**Agentes disponibles:** architect, coder, security, tester, devops, ux-designer, writer, y más.

---

## 🛠️ Tecnologías

- **Backend**: Python 3.11, FastAPI, SQLAlchemy
- **Frontend**: Jinja2, TailwindCSS, Alpine.js
- **Base de Datos**: PostgreSQL (AWS RDS)
- **Cache**: Redis
- **Storage**: AWS S3
- **Deployment**: Docker, Docker Compose
- **AI Agents**: BetterAgentX (13 agentes especializados)

---

## 📝 Configuración de Entornos

### Desarrollo Local
```bash
# Usar CODE/.env
DATABASE_URL=postgresql://...paqueteria_staging
PORT=8000
```

### Staging
```bash
# Usar CODE/.env.staging
DATABASE_URL=postgresql://...paqueteria_staging
PORT=8001
REDIS_PORT=6380
S3_PREFIX=staging/
```

### Producción
```bash
# Usar CODE/.env.production
DATABASE_URL=postgresql://...paqueteria_v4
PORT=8000
REDIS_PORT=6379
```

---

## 🔐 Seguridad

- ⚠️ **Nunca** commitear archivos `.env` con credenciales
- ✅ Usar archivos `.env.example` como plantillas
- ✅ Credenciales en variables de entorno
- ✅ Claves SSH en `.ssh_keys/` (no en git)

---

## 📞 Soporte

Para problemas o preguntas:
1. Revisa la [documentación](./DOCS/)
2. Busca en [fixes](./DOCS/06-fixes/)
3. Consulta los [análisis](./DOCS/07-analisis/)

---

## 📄 Licencia

Propietario: PAQUETES EL CLUB

---

**Última actualización**: 2026-01-29  
**Versión**: 1.0.0  
**Rama**: mainv2.1
