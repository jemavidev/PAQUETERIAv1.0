# 🚀 Deploy Manager Universal

Sistema unificado de deploy multi-entorno configurable para gestionar deploys locales y remotos de forma genérica.

## 📋 Características

- ✅ **Multi-entorno**: localhost, staging, producción, etc.
- ✅ **Configurable**: Todo mediante archivos de configuración
- ✅ **Local y Remoto**: Deploy en localhost o servidores remotos vía SSH
- ✅ **Modular**: Librerías separadas (Git, Docker, SSH)
- ✅ **Interactivo**: Menú completo con navegación
- ✅ **CLI**: Comandos para automatización
- ✅ **Genérico**: Reutilizable en cualquier proyecto
- ✅ **Hooks**: Scripts personalizados pre/post deploy
- ✅ **Backups**: Automáticos antes de deploy
- ✅ **Health Checks**: Verificación automática
- ✅ **Migraciones**: Gestión de migraciones de BD
- ✅ **Historial**: Registro de todas las operaciones

## 📁 Estructura

```
deploy/
├── deploy.sh                    # Script principal
├── config/
│   ├── deploy.conf              # Configuración global
│   ├── localhost.conf           # Config localhost
│   ├── papyrus.conf             # Config servidor papyrus
│   └── staging.conf             # Config servidor staging
├── lib/
│   ├── colors.sh                # Funciones de UI
│   ├── git.sh                   # Operaciones Git
│   ├── docker.sh                # Operaciones Docker (próximamente)
│   └── ssh.sh                   # Operaciones SSH (próximamente)
├── hooks/
│   ├── pre-deploy-papyrus.sh   # Hook pre-deploy
│   └── post-deploy-papyrus.sh  # Hook post-deploy
├── profiles/
│   └── quick-fix.profile        # Perfil de deploy rápido
└── templates/
    └── environment.conf.example # Template de configuración
```

## 🚀 Inicio Rápido

### 1. Modo Interactivo

```bash
cd deploy
./deploy.sh
```

Esto abrirá un menú interactivo donde podrás:
1. Seleccionar entorno (localhost, papyrus, staging)
2. Ejecutar operaciones (deploy, restart, logs, etc.)

### 2. Modo CLI

```bash
# Listar entornos disponibles
./deploy.sh --list-envs

# Deploy en localhost
./deploy.sh --env localhost --deploy

# Deploy en papyrus
./deploy.sh --env papyrus --deploy

# Restart en cualquier entorno
./deploy.sh --env localhost --restart
./deploy.sh --env papyrus --restart

# Ver logs
./deploy.sh --env localhost --logs

# Health check
./deploy.sh --env papyrus --health

# Crear backup
./deploy.sh --env papyrus --backup
```

## ⚙️ Configuración

### Crear Nuevo Entorno

1. Copia el template:
```bash
cp templates/environment.conf.example config/mi-entorno.conf
```

2. Edita `config/mi-entorno.conf` con tus valores

3. Agrega el entorno a `config/deploy.conf`:
```bash
ENVIRONMENTS=("localhost" "papyrus" "staging" "mi-entorno")
```

### Configuración por Entorno

Cada entorno tiene su archivo `.conf` con variables como:

```bash
# Tipo de entorno
ENV_TYPE="local"  # o "remote"

# SSH (solo para remote)
SSH_HOST="servidor.com"
SSH_USER="usuario"

# Docker
DOCKER_COMPOSE_FILE="docker-compose.dev.yml"

# Paths
PROJECT_PATH="."

# Health Check
HEALTH_CHECK_URL="http://localhost:8000/health"

# Y muchas más...
```

## 🎯 Casos de Uso

### Caso 1: Desarrollo Local

```bash
# Seleccionar localhost
./deploy.sh --env localhost

# Deploy local
./deploy.sh --env localhost --deploy

# Ver logs
./deploy.sh --env localhost --logs
```

### Caso 2: Deploy a Producción

```bash
# Deploy a papyrus
./deploy.sh --env papyrus --deploy

# Verificar estado
./deploy.sh --env papyrus --health

# Ver logs si hay problemas
./deploy.sh --env papyrus --logs
```

### Caso 3: Cambiar entre Entornos

```bash
# Modo interactivo
./deploy.sh
# Opción E1 para cambiar entorno
```

### Caso 4: Automatización (CI/CD)

```bash
#!/bin/bash
# Script de CI/CD

# Deploy a staging
./deploy/deploy.sh --env staging --deploy

# Si es exitoso, deploy a producción
if [ $? -eq 0 ]; then
    ./deploy/deploy.sh --env papyrus --deploy
fi
```

## 🔧 Comandos Disponibles

### Gestión de Entornos

```bash
--env <nombre>          # Seleccionar entorno
--list-envs             # Listar entornos
```

### Operaciones

```bash
--deploy                # Deploy completo
--restart               # Restart servicios
--status                # Ver estado
--logs                  # Ver logs
--health                # Health check
--backup                # Crear backup
--migrations            # Ejecutar migraciones
```

### Opciones

```bash
--dry-run               # Simular sin ejecutar
--verbose               # Modo detallado
--help                  # Ayuda
```

## 📊 Flujo de Deploy Completo

```
[1/6] Git Operations
  ├─ Verificar cambios locales
  ├─ Commit (si hay cambios)
  ├─ Push a GitHub
  └─ Pull en servidor remoto

[2/6] Backup
  └─ Crear backup de BD (si está habilitado)

[3/6] Docker Operations
  ├─ Pull imágenes (si está habilitado)
  ├─ Rebuild (si está habilitado)
  └─ Up servicios

[4/6] Health Check
  └─ Verificar que servicios respondan

[5/6] Migraciones
  └─ Ejecutar migraciones (si está habilitado)

[6/6] Post-Deploy
  └─ Ejecutar hook post-deploy (si existe)
```

## 🎨 Menú Interactivo

```
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║      🚀 DEPLOY MANAGER UNIVERSAL - PAQUETEX               ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝

Entorno Actual: 🌍 papyrus (Servidor AWS Producción)
Tipo: remote

════════════════════════════════════════════════════════════
GESTIÓN DE ENTORNOS:
────────────────────────────────────────────────────────────

  [E1] 🌍 Cambiar Entorno
  [E2] 📋 Ver Configuración Actual
  [E3] 🔄 Comparar Entornos

────────────────────────────────────────────────────────────
OPERACIONES DE DEPLOY:
────────────────────────────────────────────────────────────

  [1]  🚀 Deploy Completo
  [2]  📤 Solo Git (commit + push)
  [3]  🔄 Restart Servicios
  [4]  📊 Ver Estado
  [5]  📋 Ver Logs
  [6]  🔨 Rebuild Contenedores
  [7]  🗄️  Migraciones
  [8]  💾 Crear Backup
  [9]  🔍 Health Check

────────────────────────────────────────────────────────────
  [0]  ❌ Salir
```

## 🔒 Seguridad

- ✅ Confirmaciones antes de operaciones críticas
- ✅ Backups automáticos antes de deploy
- ✅ Modo dry-run para simular
- ✅ Logs de todas las operaciones
- ✅ SSH con claves privadas
- ✅ Timeouts configurables

## 🐛 Troubleshooting

### Error: "Configuración no encontrada"

**Solución:** Verifica que el archivo `.conf` existe en `deploy/config/`

### Error: "No se pudo conectar"

**Solución:** Verifica tu configuración SSH en el archivo `.conf` del entorno

### Deploy falla en health check

**Solución:** 
1. Aumenta `HEALTH_CHECK_TIMEOUT` en la configuración
2. Verifica que la URL de health check sea correcta
3. Revisa los logs: `./deploy.sh --env <nombre> --logs`

## 📝 Ejemplos de Configuración

### Localhost (Desarrollo)

```bash
ENV_TYPE="local"
DOCKER_COMPOSE_FILE="docker-compose.dev.yml"
PROJECT_PATH="."
HEALTH_CHECK_URL="http://localhost:8000/health"
```

### Servidor Remoto (Producción)

```bash
ENV_TYPE="remote"
SSH_HOST="papyrus"
SSH_USER="ubuntu"
DOCKER_COMPOSE_FILE="docker-compose.prod.yml"
PROJECT_PATH="/home/ubuntu/paqueteria"
HEALTH_CHECK_URL="http://localhost:8000/health"
```

## 🎯 Ventajas

1. **Universal**: Un solo sistema para todos los entornos
2. **Configurable**: Sin hardcodear valores
3. **Reutilizable**: Copia `deploy/` a cualquier proyecto
4. **Mantenible**: Código modular y organizado
5. **Escalable**: Agregar entornos es trivial
6. **Seguro**: Validaciones y backups
7. **Flexible**: Modo interactivo y CLI

## 📚 Recursos

- [Documentación de Docker Compose](https://docs.docker.com/compose/)
- [Guía de SSH](https://www.ssh.com/academy/ssh)
- [Bash Scripting Guide](https://www.gnu.org/software/bash/manual/)

---

**Versión:** 2.0.0  
**Última actualización:** 2024-11-22  
**Autor:** Equipo de Desarrollo PAQUETEX
