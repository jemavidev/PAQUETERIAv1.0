# 🚀 Guía de Inicio Rápido - Deploy Manager

## 1️⃣ Primera Vez

### Paso 1: Verificar Estructura

```bash
cd tu-proyecto
ls deploy/
# Deberías ver: deploy.sh, config/, lib/, etc.
```

### Paso 2: Ejecutar por Primera Vez

```bash
cd deploy
./deploy.sh
```

Esto te mostrará un menú para seleccionar el entorno.

### Paso 3: Seleccionar Entorno

```
Entornos disponibles:
  [1] localhost - Desarrollo Local
  [2] papyrus   - Servidor AWS Producción
  [3] staging   - Servidor de Pruebas

Selecciona entorno [1-3]: 1
```

## 2️⃣ Uso Diario

### Desarrollo Local

```bash
# Deploy local
./deploy/deploy.sh --env localhost --deploy

# Ver logs
./deploy/deploy.sh --env localhost --logs

# Restart
./deploy/deploy.sh --env localhost --restart
```

### Deploy a Producción

```bash
# Deploy completo
./deploy/deploy.sh --env papyrus --deploy

# Health check
./deploy/deploy.sh --env papyrus --health
```

## 3️⃣ Crear Alias (Opcional)

Agrega a tu `~/.bashrc` o `~/.zshrc`:

```bash
alias deploy='./deploy/deploy.sh'
alias deploy-local='./deploy/deploy.sh --env localhost --deploy'
alias deploy-prod='./deploy/deploy.sh --env papyrus --deploy'
alias deploy-logs='./deploy/deploy.sh --logs'
```

Luego:

```bash
source ~/.bashrc

# Usar alias
deploy-local
deploy-prod
deploy-logs
```

## 4️⃣ Agregar Nuevo Entorno

### Paso 1: Copiar Template

```bash
cp deploy/templates/environment.conf.example deploy/config/mi-servidor.conf
```

### Paso 2: Editar Configuración

```bash
nano deploy/config/mi-servidor.conf
```

Cambia:
- `ENV_NAME="mi-servidor"`
- `SSH_HOST="tu-servidor.com"`
- `PROJECT_PATH="/ruta/proyecto"`
- etc.

### Paso 3: Registrar Entorno

Edita `deploy/config/deploy.conf`:

```bash
ENVIRONMENTS=("localhost" "papyrus" "staging" "mi-servidor")
```

### Paso 4: Usar Nuevo Entorno

```bash
./deploy/deploy.sh --env mi-servidor --deploy
```

## 5️⃣ Comandos Más Usados

```bash
# Ver entornos disponibles
./deploy/deploy.sh --list-envs

# Deploy
./deploy/deploy.sh --env <nombre> --deploy

# Restart
./deploy/deploy.sh --env <nombre> --restart

# Logs en tiempo real
./deploy/deploy.sh --env <nombre> --logs

# Health check
./deploy/deploy.sh --env <nombre> --health

# Backup
./deploy/deploy.sh --env <nombre> --backup

# Migraciones
./deploy/deploy.sh --env <nombre> --migrations
```

## 6️⃣ Modo Interactivo

```bash
./deploy/deploy.sh

# Luego navega con el menú:
# E1 - Cambiar entorno
# 1  - Deploy completo
# 3  - Restart
# 5  - Ver logs
# 9  - Health check
```

## 7️⃣ Troubleshooting Rápido

### No conecta a servidor remoto

```bash
# Verifica SSH manualmente
ssh papyrus

# Si falla, revisa config/papyrus.conf
nano deploy/config/papyrus.conf
```

### Health check falla

```bash
# Aumenta timeout en config
HEALTH_CHECK_TIMEOUT=120

# O verifica URL
curl http://localhost:8000/health
```

### Deploy falla

```bash
# Ver logs detallados
./deploy/deploy.sh --env <nombre> --logs

# Modo verbose
./deploy/deploy.sh --env <nombre> --deploy --verbose
```

## 8️⃣ Tips

### Backup Antes de Deploy Importante

```bash
# Crear backup manual
./deploy/deploy.sh --env papyrus --backup

# O habilitar automático en config
BACKUP_AUTO_BEFORE_DEPLOY=true
```

### Dry Run (Simular)

```bash
# Ver qué haría sin ejecutar
./deploy/deploy.sh --env papyrus --deploy --dry-run
```

### Ver Configuración Actual

```bash
# Modo interactivo
./deploy/deploy.sh
# Opción E2

# O directamente
cat deploy/config/papyrus.conf
```

## 9️⃣ Integración CI/CD

### GitHub Actions

```yaml
name: Deploy
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Production
        run: ./deploy/deploy.sh --env papyrus --deploy
```

### GitLab CI

```yaml
deploy:
  stage: deploy
  script:
    - ./deploy/deploy.sh --env papyrus --deploy
  only:
    - main
```

## 🎯 Flujo Recomendado

### Desarrollo

```bash
1. Trabajar en localhost
   ./deploy/deploy.sh --env localhost --deploy

2. Probar localmente
   ./deploy/deploy.sh --env localhost --health

3. Commit cambios
   git add .
   git commit -m "feat: nueva funcionalidad"
   git push

4. Deploy a staging (opcional)
   ./deploy/deploy.sh --env staging --deploy

5. Deploy a producción
   ./deploy/deploy.sh --env papyrus --deploy
```

---

¿Necesitas ayuda? Revisa `deploy/README.md` para documentación completa.
