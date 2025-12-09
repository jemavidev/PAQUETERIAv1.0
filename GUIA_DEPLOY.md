# 🚀 GUÍA DE DESPLIEGUE - PAQUETES EL CLUB

**Sistema de Deploy Multi-Entorno v2.2.0**  
**Última actualización:** 2025-12-09

---

## 📋 ÍNDICE

1. [Inicio Rápido](#inicio-rápido)
2. [Entornos Disponibles](#entornos-disponibles)
3. [Comandos Principales](#comandos-principales)
4. [Ejemplos de Uso](#ejemplos-de-uso)
5. [Troubleshooting](#troubleshooting)

---

## 🚀 Inicio Rápido

### Requisitos Previos
- Git configurado
- Acceso SSH a servidores (staging/papyrus)
- Docker y Docker Compose instalados en servidores

### Uso Básico

```bash
# Modo interactivo (recomendado para principiantes)
./deploy.sh

# Deploy directo a un entorno
./deploy.sh --env [entorno] --deploy

# Ver ayuda
./deploy.sh --help
```

---

## 🌍 Entornos Disponibles

### 1. **localhost** - Desarrollo Local
- **Uso:** Desarrollo y pruebas locales
- **Comando:** `./deploy.sh --env localhost --deploy`
- **Características:**
  - No requiere SSH
  - Deploy instantáneo
  - Ideal para pruebas rápidas

### 2. **staging** - Servidor de Pruebas
- **URL:** https://staging.jemavi.co
- **Comando:** `./deploy.sh --env staging --deploy`
- **Características:**
  - Entorno de pruebas pre-producción
  - Datos de prueba
  - Configuración similar a producción

### 3. **papyrus** - Producción
- **URL:** https://paquetex.papyrus.com.co
- **Comando:** `./deploy.sh --env papyrus --deploy`
- **Características:**
  - Entorno de producción
  - Datos reales
  - Requiere precaución

---

## 📝 Comandos Principales

### Deploy Completo

```bash
# Deploy último commit
./deploy.sh --env staging --deploy

# Deploy commit específico
./deploy.sh --env staging --deploy
# (El sistema te preguntará qué commit desplegar)
```

### Sincronización de Código

```bash
# Solo sincronizar código (sin reiniciar servicios)
./deploy.sh --env staging --sync
```

### Reiniciar Servicios

```bash
# Solo reiniciar servicios (sin actualizar código)
./deploy.sh --env staging --restart
```

### Ver Estado

```bash
# Ver estado del entorno
./deploy.sh --env staging --status
```

### Rollback

```bash
# Volver a versión anterior
./deploy.sh --env staging --rollback
```

---

## 💡 Ejemplos de Uso

### Ejemplo 1: Deploy a Staging (Modo Interactivo)

```bash
$ ./deploy.sh

╔════════════════════════════════════════════════════════════════════════════╗
║                    DEPLOY MANAGER UNIVERSAL                                ║
║                         PAQUETEX v4.0                                      ║
╚════════════════════════════════════════════════════════════════════════════╝

Selecciona el entorno:
1) localhost
2) staging
3) papyrus
Opción: 2

Selecciona la acción:
1) Deploy completo
2) Solo sincronizar código
3) Solo reiniciar servicios
4) Ver estado
5) Rollback
Opción: 1

¿Desplegar último commit o seleccionar uno específico?
1) Último commit
2) Seleccionar commit
Opción: 1

[Proceso de deploy...]
✅ Deploy completado exitosamente
```

### Ejemplo 2: Deploy Rápido a Staging

```bash
$ ./deploy.sh --env staging --deploy

🚀 Iniciando deploy a staging...
📦 Sincronizando código...
🔄 Reiniciando servicios...
✅ Deploy completado exitosamente
```

### Ejemplo 3: Deploy a Commit Específico

```bash
$ ./deploy.sh --env papyrus --deploy

¿Desplegar último commit o seleccionar uno específico?
1) Último commit
2) Seleccionar commit
Opción: 2

Últimos 10 commits:
1) abc1234 - feat: Nueva funcionalidad OTP (2025-12-09)
2) def5678 - fix: Corrección de preferencias (2025-12-08)
3) ghi9012 - docs: Actualización documentación (2025-12-07)
...

Selecciona el commit: 1

🚀 Desplegando commit abc1234...
✅ Deploy completado exitosamente
```

### Ejemplo 4: Rollback Rápido

```bash
$ ./deploy.sh --env staging --rollback

📋 Historial de deploys:
1) 2025-12-09 10:30 - abc1234 - feat: Nueva funcionalidad
2) 2025-12-08 15:20 - def5678 - fix: Corrección de bug
3) 2025-12-07 09:15 - ghi9012 - docs: Actualización

¿A qué versión deseas volver? 2

🔄 Haciendo rollback a def5678...
✅ Rollback completado exitosamente
```

---

## 🛠️ Troubleshooting

### Problema: "Error de conexión SSH"

**Causa:** No tienes acceso SSH al servidor

**Solución:**
```bash
# Verificar conexión SSH
ssh ubuntu@staging.jemavi.co

# Si falla, contactar al administrador del servidor
```

### Problema: "Conflictos de Git"

**Causa:** Cambios locales no commiteados en el servidor

**Solución:**
```bash
# El sistema usa fetch + reset --hard automáticamente
# Si persiste, ejecutar manualmente en el servidor:
ssh ubuntu@staging.jemavi.co
cd ~/paqueteria-staging
git fetch origin
git reset --hard origin/main
```

### Problema: "Docker no responde"

**Causa:** Servicios Docker no están corriendo

**Solución:**
```bash
# Conectar al servidor
ssh ubuntu@staging.jemavi.co

# Verificar estado de Docker
sudo systemctl status docker

# Reiniciar Docker si es necesario
sudo systemctl restart docker

# Reiniciar servicios
cd ~/paqueteria-staging
docker-compose restart
```

### Problema: "Puerto en uso"

**Causa:** El puerto ya está siendo usado por otro proceso

**Solución:**
```bash
# Ver qué está usando el puerto
sudo lsof -i :8000

# Detener el proceso
sudo kill -9 [PID]

# O usar el script de corrección
bash CODE/scripts/deployment/fix-port-conflict.sh
```

---

## 📁 Estructura del Sistema

```
./
├── deploy.sh                    # Script principal
├── .deploy/                     # Sistema de deploy
│   ├── config/                  # Configuraciones
│   │   ├── deploy.conf         # Config global
│   │   ├── localhost.conf      # Config localhost
│   │   ├── staging.conf        # Config staging
│   │   └── papyrus.conf        # Config papyrus
│   ├── docs/                    # Documentación
│   ├── hooks/                   # Pre/post deploy hooks
│   ├── lib/                     # Librerías
│   ├── logs/                    # Logs de deploy
│   │   └── deploy.log          # Log principal
│   ├── profiles/                # Perfiles de deploy
│   └── templates/               # Templates
├── .deploy-current              # Estado actual
└── .deploy-history              # Historial
```

---

## 🔐 Configuración de Entornos

### Archivo: `.deploy/config/staging.conf`

```bash
# Configuración de Staging
ENV_NAME="staging"
ENV_HOST="staging.jemavi.co"
ENV_USER="ubuntu"
ENV_PATH="~/paqueteria-staging"
ENV_BRANCH="main"
ENV_COMPOSE_FILE="docker-compose.staging.yml"
```

### Archivo: `.deploy/config/papyrus.conf`

```bash
# Configuración de Papyrus (Producción)
ENV_NAME="papyrus"
ENV_HOST="papyrus.com.co"
ENV_USER="ubuntu"
ENV_PATH="~/paqueteria-prod"
ENV_BRANCH="main"
ENV_COMPOSE_FILE="docker-compose.prod.yml"
```

---

## 📊 Logs y Monitoreo

### Ver Logs de Deploy

```bash
# Ver últimos logs
tail -f .deploy/logs/deploy.log

# Ver logs completos
cat .deploy/logs/deploy.log
```

### Ver Historial de Deploys

```bash
# Ver historial
cat .deploy-history

# Ver estado actual
cat .deploy-current
```

### Monitorear Servicios

```bash
# Ver logs de la aplicación
ssh ubuntu@staging.jemavi.co
cd ~/paqueteria-staging
docker-compose logs -f --tail=100
```

---

## 🎯 Mejores Prácticas

### 1. Antes de Deploy a Producción

- ✅ Probar en staging primero
- ✅ Ejecutar pruebas completas
- ✅ Hacer backup de base de datos
- ✅ Notificar al equipo
- ✅ Tener plan de rollback

### 2. Durante el Deploy

- ✅ Monitorear logs en tiempo real
- ✅ Verificar que los servicios inicien correctamente
- ✅ Probar funcionalidades críticas
- ✅ Estar disponible para soporte

### 3. Después del Deploy

- ✅ Verificar que todo funciona
- ✅ Monitorear errores en logs
- ✅ Verificar métricas de rendimiento
- ✅ Documentar cualquier problema

---

## 📞 Soporte

### Problemas con el Sistema de Deploy

1. Revisar logs: `.deploy/logs/deploy.log`
2. Verificar configuración: `.deploy/config/[entorno].conf`
3. Consultar documentación: `.deploy/docs/`
4. Contactar al equipo de desarrollo

### Scripts Adicionales

- **Diagnóstico:** `CODE/scripts/deployment/diagnostics/`
- **Correcciones:** `CODE/scripts/deployment/fixes/`
- **Mantenimiento:** `CODE/scripts/deployment/maintenance/`

---

## 📚 Documentación Adicional

- **Sistema de Deploy:** `.deploy/docs/README.md`
- **Ejemplos:** `.deploy/docs/EXAMPLES.md`
- **Setup Staging:** `.deploy/docs/SETUP_STAGING.md`
- **Quick Start:** `.deploy/docs/QUICKSTART.md`

---

**Última actualización:** 2025-12-09  
**Versión del sistema:** 2.2.0  
**Mantenido por:** Equipo de Desarrollo PAQUETES EL CLUB
