# 🚀 Sistema de Deploy - PAQUETEX v4.0

## 📁 Estructura del Proyecto

```
/
├── deploy.sh                    # ← EJECUTABLE PRINCIPAL (usar este)
├── .deploy/                     # ← Sistema de deploy (no tocar directamente)
│   ├── config/                  # Configuraciones de entornos
│   │   ├── deploy.conf          # Configuración global
│   │   ├── localhost.conf       # Entorno local
│   │   ├── papyrus.conf         # Servidor AWS
│   │   └── staging.conf         # Servidor staging
│   ├── lib/                     # Librerías del sistema
│   │   ├── colors.sh            # UI y logging
│   │   └── git.sh               # Operaciones Git
│   ├── hooks/                   # Scripts personalizados
│   │   ├── pre-deploy-papyrus.sh
│   │   └── post-deploy-papyrus.sh
│   ├── profiles/                # Perfiles de deploy
│   │   └── quick-fix.profile
│   ├── templates/               # Templates de configuración
│   │   └── environment.conf.example
│   ├── docs/                    # Documentación completa
│   │   ├── README.md            # Documentación completa
│   │   ├── QUICKSTART.md        # Guía de inicio rápido
│   │   ├── EXAMPLES.md          # Ejemplos de uso
│   │   └── DEPLOY_SYSTEM_SUMMARY.md
│   └── logs/                    # Logs del sistema (auto-generado)
├── .deploy-history              # Historial de deploys
└── .deploy-current              # Entorno actual seleccionado
```

## 🚀 Uso Rápido

### Modo Interactivo (Recomendado)

```bash
./deploy.sh
```

Esto abre un menú interactivo donde puedes:
- Seleccionar entorno (localhost, papyrus, staging)
- Ejecutar operaciones (deploy, restart, logs, etc.)

### Modo CLI (Comandos Directos)

```bash
# Listar entornos disponibles
./deploy.sh --list-envs

# Deploy en localhost
./deploy.sh --env localhost --deploy

# Deploy en papyrus (producción)
./deploy.sh --env papyrus --deploy

# Restart servicios
./deploy.sh --env papyrus --restart

# Ver logs en tiempo real
./deploy.sh --env papyrus --logs

# Health check
./deploy.sh --env papyrus --health

# Crear backup
./deploy.sh --env papyrus --backup

# Ver ayuda completa
./deploy.sh --help
```

## 📚 Documentación

### Documentación Completa
```bash
cat .deploy/docs/README.md
```

### Guía de Inicio Rápido
```bash
cat .deploy/docs/QUICKSTART.md
```

### Ejemplos de Uso
```bash
cat .deploy/docs/EXAMPLES.md
```

## 🎯 Entornos Disponibles

### 1. localhost (Desarrollo Local)
```bash
./deploy.sh --env localhost --deploy
```
- Desarrollo en tu máquina
- Docker Compose local
- Sin SSH
- Cambios inmediatos

### 2. papyrus (Producción AWS)
```bash
./deploy.sh --env papyrus --deploy
```
- Servidor AWS Lightsail
- Producción real
- Backup automático
- Health checks completos

### 3. staging (Pruebas)
```bash
./deploy.sh --env staging --deploy
```
- Servidor de pruebas
- Validar antes de producción
- Tests automáticos

## 🔧 Configuración

### Ver Configuración Actual
```bash
# Modo interactivo
./deploy.sh
# Opción E2

# O directamente
cat .deploy/config/papyrus.conf
```

### Crear Nuevo Entorno
```bash
# 1. Copiar template
cp .deploy/templates/environment.conf.example .deploy/config/nuevo.conf

# 2. Editar configuración
nano .deploy/config/nuevo.conf

# 3. Registrar en deploy.conf
nano .deploy/config/deploy.conf
# Agregar "nuevo" a ENVIRONMENTS

# 4. Usar
./deploy.sh --env nuevo --deploy
```

## 🎨 Menú Interactivo

```
╔════════════════════════════════════════════════════════════╗
║      🚀 DEPLOY MANAGER UNIVERSAL - PAQUETEX               ║
╚════════════════════════════════════════════════════════════╝

Entorno Actual: 🌍 papyrus (Servidor AWS Producción)

GESTIÓN DE ENTORNOS:
  [E1] 🌍 Cambiar Entorno
  [E2] 📋 Ver Configuración

OPERACIONES:
  [1] 🚀 Deploy Completo
  [2] 📤 Solo Git
  [3] 🔄 Restart
  [4] 📊 Estado
  [5] 📋 Logs
  [6] 🔨 Rebuild
  [7] 🗄️  Migraciones
  [8] 💾 Backup
  [9] 🔍 Health Check
  [0] ❌ Salir
```

## 🔒 Seguridad

- ✅ Backups automáticos antes de deploy (producción)
- ✅ Confirmaciones antes de operaciones críticas
- ✅ Health checks después de cambios
- ✅ Logs de todas las operaciones
- ✅ Modo dry-run para simular

## 🐛 Troubleshooting

### Error: "Directorio .deploy no encontrado"
```bash
# Asegúrate de estar en el directorio raíz del proyecto
pwd
# Debe mostrar: .../PAQUETERIA v1.0
```

### Error: "No se pudo conectar a papyrus"
```bash
# Verifica conexión SSH
ssh papyrus

# Si falla, revisa ~/.ssh/config
```

### Deploy falla
```bash
# Ver logs detallados
./deploy.sh --env papyrus --logs

# Modo verbose
./deploy.sh --env papyrus --deploy --verbose
```

## 📝 Alias Útiles (Opcional)

Agrega a tu `~/.bashrc` o `~/.zshrc`:

```bash
alias deploy='./deploy.sh'
alias deploy-local='./deploy.sh --env localhost --deploy'
alias deploy-prod='./deploy.sh --env papyrus --deploy'
alias deploy-logs='./deploy.sh --env papyrus --logs'
alias deploy-health='./deploy.sh --env papyrus --health'
```

Luego:
```bash
source ~/.bashrc

# Usar
deploy-local
deploy-prod
deploy-health
```

## 🎯 Flujo Recomendado

```bash
# 1. Desarrollo local
./deploy.sh --env localhost --deploy

# 2. Probar localmente
./deploy.sh --env localhost --health

# 3. Commit cambios
git add .
git commit -m "feat: nueva funcionalidad"
git push

# 4. Deploy a producción
./deploy.sh --env papyrus --deploy

# 5. Verificar
./deploy.sh --env papyrus --health
```

## 📞 Ayuda

```bash
# Ver ayuda completa
./deploy.sh --help

# Ver documentación
cat .deploy/docs/README.md

# Ver ejemplos
cat .deploy/docs/EXAMPLES.md
```

## ✨ Características

- ✅ Multi-entorno (localhost, papyrus, staging)
- ✅ Modo interactivo y CLI
- ✅ Configuración externa (sin hardcodear)
- ✅ Backups automáticos
- ✅ Health checks
- ✅ Migraciones de BD
- ✅ Hooks personalizables
- ✅ Logs detallados
- ✅ Historial de deploys

---

**Versión:** 2.0.0  
**Última actualización:** 2024-11-22  
**Documentación completa:** `.deploy/docs/README.md`
