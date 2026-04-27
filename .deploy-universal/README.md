# 🚀 Deploy Manager Universal v3.0

Sistema de deploy universal y configurable para cualquier proyecto.

## 📋 Características

- ✅ **Universal:** Funciona con cualquier proyecto
- ✅ **Configurable:** Todo en archivo YAML
- ✅ **Multi-entorno:** Localhost, Staging, Producción
- ✅ **Desatendido:** Modo CI/CD sin interacción
- ✅ **Rollback:** Automático si falla
- ✅ **Modular:** Fácil de extender

## 🎯 Instalación Rápida

```bash
# 1. Copiar a tu proyecto
cp -r .deploy-universal /tu-proyecto/.deploy

# 2. Crear configuración
cd /tu-proyecto
cp .deploy/templates/deploy-config.yml.example .deploy-config.yml

# 3. Editar con tus datos
nano .deploy-config.yml

# 4. Usar
./.deploy/deploy.sh deploy localhost
```

## 📁 Estructura

```
tu-proyecto/
├── .deploy/                      # Sistema de deploy (NO modificar)
│   ├── deploy.sh                 # Script principal
│   ├── lib/                      # Librerías
│   └── templates/                # Templates
│
├── .deploy-config.yml            # TU configuración (modificar)
├── .env.local                    # Variables localhost
├── .env.staging                  # Variables staging
├── .env.production               # Variables producción
└── docker-compose.yml            # Tu docker compose
```

## 🎮 Uso

### Modo Interactivo
```bash
./deploy.sh
```

### Comandos Directos
```bash
# Deploy
./deploy.sh deploy localhost
./deploy.sh deploy staging
./deploy.sh deploy production

# Operaciones
./deploy.sh pull staging
./deploy.sh restart production
./deploy.sh logs production
./deploy.sh status production
./deploy.sh rollback production

# Health check
./deploy.sh health production
```

### Modo Desatendido (CI/CD)
```bash
./deploy.sh deploy production --non-interactive
```

## ⚙️ Configuración

Edita `.deploy-config.yml` con los datos de tu proyecto:

```yaml
project:
  name: "mi-proyecto"              # ← Cambia esto
  version: "1.0.0"

localhost:
  docker:
    compose_file: "docker-compose.dev.yml"  # ← Tu archivo
    services: ["app", "db"]                  # ← Tus servicios

production:
  ssh:
    host: "tu-servidor.com"        # ← Tu servidor
    user: "ubuntu"                 # ← Tu usuario
  paths:
    project: "/var/www/app"        # ← Tu ruta
```

## 📚 Ejemplos

Ver carpeta `examples/` para configuraciones de:
- API Node.js
- App Python/FastAPI
- Frontend React
- Monorepo
- Microservicios

## 🔐 Secrets

**Opción 1: Variables de Entorno**
```yaml
production:
  ssh:
    host: "${PROD_HOST}"
```

**Opción 2: Archivo Separado**
```yaml
production:
  ssh:
    config_file: ".deploy-secrets.yml"  # NO commitear
```

## 🆘 Troubleshooting

### Error: "Config file not found"
```bash
# Crear desde template
cp .deploy/templates/deploy-config.yml.example .deploy-config.yml
```

### Error: "SSH connection failed"
```bash
# Verificar conectividad
ssh usuario@servidor

# Verificar llave
ls -la ~/.ssh/
```

### Error: "Docker command not found"
```bash
# Instalar Docker
curl -fsSL https://get.docker.com | sh
```

## 📖 Documentación Completa

- [Guía de Configuración](docs/CONFIGURATION.md)
- [Ejemplos](examples/)
- [FAQ](docs/FAQ.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

## 🤝 Contribuir

Este es un sistema genérico. Mejoras bienvenidas!

## 📄 Licencia

MIT
