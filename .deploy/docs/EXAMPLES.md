# 📚 Ejemplos de Uso - Deploy Manager

## 🎯 Escenarios Comunes

### 1. Desarrollo Local Diario

```bash
# Iniciar día - levantar servicios
./deploy/deploy.sh --env localhost --deploy

# Ver logs mientras desarrollas
./deploy/deploy.sh --env localhost --logs

# Restart después de cambios
./deploy/deploy.sh --env localhost --restart

# Health check
./deploy/deploy.sh --env localhost --health
```

### 2. Deploy a Producción

```bash
# 1. Asegurarte que local funciona
./deploy/deploy.sh --env localhost --health

# 2. Crear backup de producción
./deploy/deploy.sh --env papyrus --backup

# 3. Deploy a producción
./deploy/deploy.sh --env papyrus --deploy

# 4. Verificar que funciona
./deploy/deploy.sh --env papyrus --health

# 5. Monitorear logs
./deploy/deploy.sh --env papyrus --logs
```

### 3. Hotfix Urgente

```bash
# 1. Fix en local
# ... hacer cambios ...

# 2. Deploy rápido (sin backup, sin rebuild)
./deploy/deploy.sh --env papyrus --deploy --profile quick-fix

# 3. Verificar inmediatamente
./deploy/deploy.sh --env papyrus --health
```

### 4. Migración de Base de Datos

```bash
# 1. Backup antes de migración
./deploy/deploy.sh --env papyrus --backup

# 2. Deploy con migraciones
./deploy/deploy.sh --env papyrus --deploy

# 3. Ejecutar migraciones manualmente si es necesario
./deploy/deploy.sh --env papyrus --migrations

# 4. Verificar
./deploy/deploy.sh --env papyrus --health
```

### 5. Cambiar entre Entornos

```bash
# Modo interactivo
./deploy/deploy.sh
# Opción E1 - Cambiar Entorno
# Seleccionar nuevo entorno

# O directo
./deploy/deploy.sh --env localhost --deploy
./deploy/deploy.sh --env staging --deploy
./deploy/deploy.sh --env papyrus --deploy
```

## 🔧 Operaciones Específicas

### Git Operations

```bash
# Ver estado
git status

# Commit y push manual
git add .
git commit -m "feat: nueva funcionalidad"
git push

# O usar el deploy manager
./deploy/deploy.sh --env localhost
# Opción 2 - Solo Git
```

### Docker Operations

```bash
# Ver estado de contenedores
./deploy/deploy.sh --env localhost --status

# Restart servicios
./deploy/deploy.sh --env localhost --restart

# Rebuild completo
./deploy/deploy.sh --env localhost
# Opción 6 - Rebuild Contenedores

# Ver logs en tiempo real
./deploy/deploy.sh --env localhost --logs
```

### Backups

```bash
# Crear backup manual
./deploy/deploy.sh --env papyrus --backup

# Backup se guarda en:
# Local: ./backups/localhost/
# Papyrus: /home/ubuntu/backups/

# Descargar backup remoto
scp papyrus:/home/ubuntu/backups/backup_*.sql ./backups/
```

## 🎨 Modo Interactivo

### Flujo Completo

```bash
./deploy/deploy.sh

# 1. Seleccionar entorno
[E1] 🌍 Cambiar Entorno
> 2 (papyrus)

# 2. Ver configuración
[E2] 📋 Ver Configuración Actual

# 3. Deploy
[1] 🚀 Deploy Completo

# 4. Verificar
[9] 🔍 Health Check

# 5. Ver logs si hay problemas
[5] 📋 Ver Logs
```

## 🔄 Workflows Completos

### Workflow 1: Feature Nueva

```bash
# 1. Desarrollo local
./deploy/deploy.sh --env localhost --deploy

# 2. Probar localmente
curl http://localhost:8000/api/nueva-feature

# 3. Commit cambios
git add .
git commit -m "feat: nueva feature"
git push

# 4. Deploy a staging (opcional)
./deploy/deploy.sh --env staging --deploy

# 5. Probar en staging
curl https://staging.paquetex.com/api/nueva-feature

# 6. Deploy a producción
./deploy/deploy.sh --env papyrus --deploy

# 7. Verificar producción
./deploy/deploy.sh --env papyrus --health
```

### Workflow 2: Bug Fix

```bash
# 1. Reproducir bug en local
./deploy/deploy.sh --env localhost --deploy

# 2. Fix y probar
# ... hacer cambios ...
./deploy/deploy.sh --env localhost --restart

# 3. Commit
git add .
git commit -m "fix: corregir bug en X"
git push

# 4. Deploy directo a producción
./deploy/deploy.sh --env papyrus --deploy

# 5. Verificar fix
./deploy/deploy.sh --env papyrus --health
```

### Workflow 3: Rollback

```bash
# Si algo sale mal después de deploy

# 1. Ver logs
./deploy/deploy.sh --env papyrus --logs

# 2. Rollback Git
git log --oneline -5
git reset --hard <commit-anterior>
git push -f

# 3. Deploy versión anterior
./deploy/deploy.sh --env papyrus --deploy

# 4. Verificar
./deploy/deploy.sh --env papyrus --health
```

## 🛠️ Personalización

### Crear Nuevo Entorno "Production-2"

```bash
# 1. Copiar template
cp deploy/templates/environment.conf.example deploy/config/production2.conf

# 2. Editar
nano deploy/config/production2.conf

# Cambiar:
ENV_NAME="production2"
ENV_TYPE="remote"
SSH_HOST="prod2.example.com"
PROJECT_PATH="/var/www/paqueteria"
# ... etc

# 3. Registrar
nano deploy/config/deploy.conf
# Agregar "production2" a ENVIRONMENTS

# 4. Usar
./deploy/deploy.sh --env production2 --deploy
```

### Crear Hook Personalizado

```bash
# 1. Crear archivo
nano deploy/hooks/pre-deploy-production2.sh

#!/bin/bash
echo "🔍 Verificaciones personalizadas..."
# Tu código aquí
exit 0

# 2. Hacer ejecutable
chmod +x deploy/hooks/pre-deploy-production2.sh

# 3. Configurar en environment
nano deploy/config/production2.conf
PRE_DEPLOY_HOOK="deploy/hooks/pre-deploy-production2.sh"
```

### Crear Perfil Personalizado

```bash
# 1. Crear archivo
nano deploy/profiles/staging-fast.profile

# Configuración para staging rápido
BACKUP_AUTO_BEFORE_DEPLOY=false
DOCKER_REBUILD_ON_DEPLOY=false
MIGRATIONS_AUTO=true
HEALTH_CHECK_TIMEOUT=30

# 2. Usar
./deploy/deploy.sh --env staging --deploy --profile staging-fast
```

## 🔍 Debugging

### Ver Qué Haría Sin Ejecutar

```bash
./deploy/deploy.sh --env papyrus --deploy --dry-run
```

### Modo Verbose

```bash
./deploy/deploy.sh --env papyrus --deploy --verbose
```

### Ver Configuración Actual

```bash
# Modo interactivo
./deploy/deploy.sh
# Opción E2

# O directamente
cat deploy/config/papyrus.conf
```

### Ver Historial de Deploys

```bash
cat .deploy-history
```

## 📊 Monitoreo

### Monitoreo Continuo

```bash
# Terminal 1: Logs en tiempo real
./deploy/deploy.sh --env papyrus --logs

# Terminal 2: Health checks periódicos
watch -n 30 './deploy/deploy.sh --env papyrus --health'

# Terminal 3: Estado de contenedores
watch -n 10 './deploy/deploy.sh --env papyrus --status'
```

## 🚨 Emergencias

### Servidor No Responde

```bash
# 1. Ver logs
./deploy/deploy.sh --env papyrus --logs

# 2. Restart
./deploy/deploy.sh --env papyrus --restart

# 3. Si no funciona, rebuild
./deploy/deploy.sh --env papyrus
# Opción 6 - Rebuild

# 4. Último recurso: rollback
git reset --hard HEAD~1
git push -f
./deploy/deploy.sh --env papyrus --deploy
```

### Base de Datos Corrupta

```bash
# 1. Detener servicios
./deploy/deploy.sh --env papyrus
# Opción 3 - Restart (con down primero)

# 2. Restaurar desde backup
scp papyrus:/home/ubuntu/backups/backup_latest.sql ./
# Restaurar manualmente

# 3. Reiniciar
./deploy/deploy.sh --env papyrus --restart
```

## 🎓 Tips Avanzados

### Alias Útiles

```bash
# Agregar a ~/.bashrc
alias d='./deploy/deploy.sh'
alias dl='./deploy/deploy.sh --env localhost'
alias dp='./deploy/deploy.sh --env papyrus'
alias ds='./deploy/deploy.sh --env staging'

# Usar
dl --deploy
dp --health
ds --logs
```

### Script de Deploy Automático

```bash
#!/bin/bash
# auto-deploy.sh

# Deploy a todos los entornos secuencialmente
./deploy/deploy.sh --env localhost --deploy && \
./deploy/deploy.sh --env staging --deploy && \
./deploy/deploy.sh --env papyrus --deploy

echo "✅ Deploy completado en todos los entornos"
```

### Integración con Git Hooks

```bash
# .git/hooks/pre-push
#!/bin/bash

# Verificar que local funciona antes de push
./deploy/deploy.sh --env localhost --health

if [ $? -ne 0 ]; then
    echo "❌ Health check falló. Push cancelado."
    exit 1
fi
```

---

¿Más ejemplos? Revisa `deploy/README.md` para documentación completa.
