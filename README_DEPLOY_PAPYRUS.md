# 🚀 DEPLOY_PAPYRUS.sh - Guía de Uso

## 📋 Descripción

Script unificado e interactivo para gestionar deploys desde localhost al servidor AWS Cloud "papyrus". Incluye gestión completa de Git, Docker, migraciones, backups y monitoreo.

## ✨ Características

- ✅ **Menú interactivo** con 13+ opciones
- ✅ **Deploy completo** (commit + push + deploy)
- ✅ **Gestión de Git** (commit, push, rollback, stash, reset)
- ✅ **Gestión remota** (restart, rebuild, cleanup)
- ✅ **Migraciones** (ejecutar, rollback, historial)
- ✅ **Monitoreo** (logs, health check, métricas)
- ✅ **Backups** (crear y descargar)
- ✅ **Historial** de deploys
- ✅ **Modo CLI** para automatización

## 🚀 Uso Rápido

### Modo Interactivo (Recomendado)

```bash
./DEPLOY_PAPYRUS.sh
```

Esto abrirá un menú interactivo con todas las opciones disponibles.

### Modo CLI (Automatización)

```bash
# Deploy completo
./DEPLOY_PAPYRUS.sh --deploy

# Solo commit y push
./DEPLOY_PAPYRUS.sh --commit "fix: corregir bug"

# Restart remoto
./DEPLOY_PAPYRUS.sh --restart

# Ver estado del servidor
./DEPLOY_PAPYRUS.sh --status

# Ver logs en tiempo real
./DEPLOY_PAPYRUS.sh --logs

# Health check
./DEPLOY_PAPYRUS.sh --health

# Ver ayuda
./DEPLOY_PAPYRUS.sh --help

# Ver versión
./DEPLOY_PAPYRUS.sh --version
```

## 📖 Menú Principal

```
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║           🚀 DEPLOY MANAGER - PAQUETEX v4.0               ║
║                                                            ║
║              Servidor: papyrus                             ║
║              Versión: 1.0.0                                ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝

SELECCIONA UNA OPCIÓN:
────────────────────────────────────────────────────────────

  [1]  🚀 Deploy Completo (commit + push + deploy)
  [2]  📤 Solo Commit y Push a GitHub
  [3]  📥 Solo Deploy a AWS (sin commit)
  [4]  🔄 Restart Servidor Remoto
  [5]  📊 Ver Estado del Servidor
  [6]  📋 Ver Logs Remotos
  [7]  🔨 Rebuild Contenedores Remotos
  [8]  🗄️  Ejecutar Migraciones Remotas
  [9]  ⏮️  Rollback (volver a commit anterior)
  [10] 🧹 Limpiar Recursos Docker Remotos
  [11] 💾 Backup Base de Datos Remota
  [12] 🔍 Health Check Completo
  [13] 📜 Ver Historial de Deploys

────────────────────────────────────────────────────────────
  [20] 📝 Gestionar Cambios Locales
  [0]  ❌ Salir

────────────────────────────────────────────────────────────
```

## 🎯 Casos de Uso

### 1. Deploy Completo (Opción 1)

**Cuándo usar:** Tienes cambios locales y quieres deployarlos a producción.

**Qué hace:**
1. Muestra el estado de Git
2. Te pide un mensaje de commit
3. Hace commit y push a GitHub
4. Conecta al servidor remoto
5. Hace pull de los cambios
6. Actualiza los servicios Docker
7. Ejecuta health checks
8. Muestra métricas

**Ejemplo:**
```bash
./DEPLOY_PAPYRUS.sh
# Selecciona opción 1
# Ingresa mensaje: "fix: corregir caché de paquetes"
# Confirma y espera
```

### 2. Solo Commit y Push (Opción 2)

**Cuándo usar:** Quieres guardar cambios en GitHub sin deployar.

**Qué hace:**
1. Muestra cambios locales
2. Te pide mensaje de commit
3. Hace commit y push
4. NO hace deploy

### 3. Solo Deploy (Opción 3)

**Cuándo usar:** Ya hiciste push y solo quieres actualizar el servidor.

**Qué hace:**
1. Conecta al servidor
2. Hace pull de GitHub
3. Actualiza servicios
4. Ejecuta health checks

### 4. Restart Servidor (Opción 4)

**Cuándo usar:** El servidor está lento o necesita reiniciarse.

**Qué hace:**
1. Reinicia todos los contenedores Docker
2. Espera health check
3. Verifica que responda

### 5. Ver Estado (Opción 5)

**Cuándo usar:** Quieres ver cómo está el servidor.

**Qué muestra:**
- Estado de servicios (app, redis, postgres)
- Uso de recursos (CPU, RAM)
- Espacio en disco

### 6. Ver Logs (Opción 6)

**Cuándo usar:** Necesitas debuggear o ver qué está pasando.

**Opciones:**
- Ver últimas 50/100 líneas
- Ver en tiempo real (tail -f)
- Buscar texto específico (grep)
- Ver logs de servicio específico

### 7. Rebuild Contenedores (Opción 7)

**Cuándo usar:** Cambios en Dockerfile o dependencias.

**Qué hace:**
1. Detiene contenedores
2. Reconstruye imágenes (sin caché)
3. Inicia servicios
4. Ejecuta health check

⚠️ **Advertencia:** Puede tardar varios minutos.

### 8. Migraciones (Opción 8)

**Cuándo usar:** Cambios en la base de datos.

**Opciones:**
- Ver migraciones pendientes
- Ejecutar migraciones (upgrade head)
- Rollback última migración
- Ver historial

### 9. Rollback (Opción 9)

**Cuándo usar:** El último deploy causó problemas.

**Qué hace:**
1. Muestra últimos 10 commits
2. Seleccionas a cuál volver
3. Hace reset --hard
4. Hace push forzado
5. Opcionalmente deploya el rollback

⚠️ **Advertencia:** Esto reescribe el historial de Git.

### 10. Limpiar Recursos (Opción 10)

**Cuándo usar:** El servidor está quedando sin espacio.

**Qué hace:**
- Elimina contenedores detenidos
- Elimina imágenes no usadas
- Elimina volúmenes huérfanos
- Muestra espacio liberado

### 11. Backup Base de Datos (Opción 11)

**Cuándo usar:** Antes de cambios importantes o periódicamente.

**Qué hace:**
1. Crea dump de PostgreSQL
2. Lo guarda en el servidor
3. Opcionalmente lo descarga localmente

**Archivo generado:** `backup_YYYYMMDD_HHMMSS.sql`

### 12. Health Check (Opción 12)

**Cuándo usar:** Verificar que todo esté funcionando.

**Qué verifica:**
- ✓ Servicios corriendo
- ✓ Endpoints respondiendo (200 OK)
- ✓ Recursos (CPU, RAM, Disco)
- ✓ Conectividad (Redis, PostgreSQL)
- ✓ Estado general

### 13. Historial de Deploys (Opción 13)

**Cuándo usar:** Ver qué se ha deployado recientemente.

**Qué muestra:**
- Últimos 10 deploys
- Fecha y hora
- Tipo de operación
- Descripción
- Usuario

### 20. Gestionar Cambios Locales (Opción 20)

**Cuándo usar:** Tienes cambios locales que necesitas gestionar.

**Opciones:**
- Commitear todos los cambios
- Ver diff de cambios
- Hacer stash (guardar temporalmente)
- Descartar cambios (reset --hard)

## 🔧 Configuración

### Variables de Configuración

Edita estas variables al inicio del script si es necesario:

```bash
AWS_HOST="papyrus"                      # Alias SSH del servidor
AWS_PROJECT_PATH="/home/ubuntu/paqueteria"  # Ruta del proyecto
GIT_BRANCH="main"                       # Rama de Git
```

### Requisitos Previos

1. **SSH configurado:**
   ```bash
   # Verifica que puedas conectarte
   ssh papyrus
   ```

2. **Git configurado:**
   ```bash
   git config --global user.name "Tu Nombre"
   git config --global user.email "tu@email.com"
   ```

3. **Permisos de ejecución:**
   ```bash
   chmod +x DEPLOY_PAPYRUS.sh
   ```

## 📊 Flujo de Deploy Completo

```
┌─────────────────────────────────────────────────────────┐
│ 1. LOCALHOST                                            │
│    ├─ Verificar cambios locales                        │
│    ├─ Mostrar archivos modificados                     │
│    ├─ Solicitar mensaje de commit                      │
│    ├─ git add .                                         │
│    ├─ git commit -m "mensaje"                          │
│    └─ git push origin main                             │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│ 2. GITHUB                                               │
│    └─ Repositorio actualizado                          │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│ 3. SERVIDOR AWS (papyrus)                               │
│    ├─ [1/6] git pull origin main                       │
│    ├─ [2/6] Analizar cambios                           │
│    ├─ [3/6] docker compose pull                        │
│    ├─ [3/6] docker compose up -d                       │
│    ├─ [4/6] Esperar health check                       │
│    ├─ [5/6] Tests de humo (endpoints)                  │
│    └─ [6/6] Verificar métricas                         │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│ 4. RESULTADO                                            │
│    ├─ ✅ Deploy completado en Xs                       │
│    ├─ 📊 Métricas mostradas                            │
│    └─ 📝 Guardado en historial                         │
└─────────────────────────────────────────────────────────┘
```

## 🎨 Características de UI

### Colores

- 🔵 **Azul:** Información
- 🟢 **Verde:** Éxito
- 🟡 **Amarillo:** Advertencia
- 🔴 **Rojo:** Error
- 🔷 **Cyan:** Pasos/Acciones

### Feedback Visual

- ✅ Checkmarks para éxito
- ❌ X para errores
- ⚠️  Triángulo para advertencias
- ℹ️  i para información
- ▶️  Flecha para pasos

### Separadores

```
────────────────────────────────────────────────────────────
```

## 🔒 Seguridad

### Buenas Prácticas

1. **Siempre revisa los cambios** antes de commitear
2. **Usa mensajes de commit descriptivos**
3. **Haz backup antes de cambios importantes**
4. **Verifica health check después de deploy**
5. **Monitorea logs después de deploy**

### Rollback Rápido

Si algo sale mal:

```bash
./DEPLOY_PAPYRUS.sh
# Opción 9 (Rollback)
# Selecciona commit anterior
# Confirma deploy del rollback
```

## 📝 Historial de Deploys

El script guarda un historial en `.deploy-history`:

```
2024-11-22 10:30:45|deploy|success|45s|developer
2024-11-22 09:15:20|commit|fix: corregir caché|developer
2024-11-21 16:45:10|deploy|success|52s|developer
```

## 🐛 Troubleshooting

### Error: "No se pudo conectar a papyrus"

**Solución:**
```bash
# Verifica conexión SSH
ssh papyrus

# Si falla, verifica tu config SSH
cat ~/.ssh/config
```

### Error: "Git push failed"

**Solución:**
```bash
# Verifica que estés en la rama correcta
git branch

# Verifica que tengas permisos
git remote -v
```

### Error: "Health check timeout"

**Solución:**
- Espera un poco más (el servidor puede estar iniciando)
- Verifica logs: Opción 6
- Verifica estado: Opción 5

### Servidor no responde después de deploy

**Solución:**
```bash
./DEPLOY_PAPYRUS.sh
# Opción 4 (Restart)
# O Opción 9 (Rollback)
```

## 📞 Soporte

Si encuentras problemas:

1. Revisa los logs: `./DEPLOY_PAPYRUS.sh --logs`
2. Verifica el estado: `./DEPLOY_PAPYRUS.sh --status`
3. Ejecuta health check: `./DEPLOY_PAPYRUS.sh --health`
4. Revisa el historial: Opción 13

## 🎯 Tips y Trucos

### Deploy Rápido

```bash
# Alias en ~/.bashrc o ~/.zshrc
alias deploy='./DEPLOY_PAPYRUS.sh --deploy'
alias deploy-status='./DEPLOY_PAPYRUS.sh --status'
alias deploy-logs='./DEPLOY_PAPYRUS.sh --logs'
```

### Backup Automático

Crea un cron job para backups diarios:

```bash
# Editar crontab
crontab -e

# Agregar línea (backup diario a las 2 AM)
0 2 * * * cd /ruta/proyecto && ./DEPLOY_PAPYRUS.sh --backup
```

### Monitoreo Continuo

```bash
# Ver logs en tiempo real en otra terminal
./DEPLOY_PAPYRUS.sh --logs

# Ver métricas cada 5 segundos
watch -n 5 './DEPLOY_PAPYRUS.sh --status'
```

## 📚 Recursos Adicionales

- [Documentación de Docker Compose](https://docs.docker.com/compose/)
- [Guía de Git](https://git-scm.com/doc)
- [SSH Config](https://www.ssh.com/academy/ssh/config)

---

**Versión:** 1.0.0  
**Última actualización:** 2024-11-22  
**Autor:** Equipo de Desarrollo PAQUETEX
