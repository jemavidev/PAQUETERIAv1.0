# 🚀 Guía de Despliegue Automatizado - PAQUETERÍA v1.0

## 📋 Flujo de Trabajo Actual vs Propuesto

### ✅ Estado Actual del Proyecto

Tu proyecto **YA TIENE** la infraestructura necesaria para el despliegue automatizado:

```
Localhost (Desarrollo)
    ↓ git push
GitHub (Repositorio)
    ↓ git pull
AWS Server (Producción)
```

**Scripts disponibles:**
- ✅ `deploy-lightsail.sh` - Despliegue completo en AWS Lightsail
- ✅ `DOCS/scripts/deployment/deploy.sh` - Despliegue desde GitHub
- ✅ `DOCS/scripts/deployment/pull-only.sh` - Solo actualizar código
- ✅ `DOCS/scripts/deployment/pull-update.sh` - Pull + análisis inteligente
- ✅ `.gitignore` - Configurado correctamente

---

## 🎯 Flujo de Trabajo Recomendado

### 1️⃣ **En tu Localhost (Desarrollo)**

```bash
# 1. Hacer cambios en el código
vim CODE/src/app/routes/packages.py

# 2. Probar localmente
docker compose -f docker-compose.prod.yml restart app

# 3. Commit y push a GitHub
git add .
git commit -m "feat: agregar nueva funcionalidad de paquetes"
git push origin main
```

### 2️⃣ **En el Servidor AWS (Producción)**

**Opción A: Actualización Rápida (solo código)**
```bash
# Conectar por SSH
ssh usuario@tu-servidor-aws.com

# Ir al directorio del proyecto
cd /opt/paqueteria/Paqueteria-v1.0

# Actualizar código desde GitHub (sin rebuild)
./DOCS/scripts/deployment/pull-only.sh main

# Reiniciar app (hot reload aplicará cambios automáticamente)
docker compose -f docker-compose.prod.yml restart app
```

**Opción B: Actualización Inteligente (análisis automático)**
```bash
# Este script detecta qué cambió y decide qué hacer
./DOCS/scripts/deployment/pull-update.sh
```

**Opción C: Despliegue Completo (rebuild + restart)**
```bash
# Para cambios en dependencias o Dockerfile
./DOCS/scripts/deployment/deploy.sh main
```

---

## 🔧 Configuración Inicial (Una sola vez)

### En tu Localhost

#### 1. Configurar Git (si no lo has hecho)

```bash
# Verificar configuración actual
git remote -v

# Si no tienes remoto configurado
git remote add origin https://github.com/tu-usuario/paqueteria-v1.0.git

# Configurar credenciales
git config user.name "Tu Nombre"
git config user.email "tu@email.com"
```

#### 2. Crear archivo `.env` local (no se sube a GitHub)

```bash
# Copiar desde ejemplo
cp CODE/env.example .env

# Editar con tus valores de desarrollo
nano .env
```

**Importante:** El `.gitignore` ya está configurado para NO subir `.env` a GitHub.

### En el Servidor AWS

#### 1. Clonar el repositorio (primera vez)

```bash
# Conectar por SSH
ssh usuario@tu-servidor-aws.com

# Crear directorio
sudo mkdir -p /opt/paqueteria
sudo chown $USER:$USER /opt/paqueteria
cd /opt/paqueteria

# Clonar repositorio
git clone https://github.com/tu-usuario/paqueteria-v1.0.git
cd paqueteria-v1.0
```

#### 2. Configurar `.env` de producción

```bash
# Copiar desde ejemplo
cp CODE/env.example .env

# Editar con valores de producción (RDS, S3, etc.)
nano .env
```

**Variables críticas para producción:**
```bash
# Base de datos (AWS RDS)
DATABASE_URL=postgresql://usuario:password@tu-rds-endpoint.rds.amazonaws.com:5432/paqueteria

# Seguridad
SECRET_KEY=$(openssl rand -hex 32)
REDIS_PASSWORD=$(openssl rand -hex 16)

# AWS S3
AWS_ACCESS_KEY_ID=tu-access-key
AWS_SECRET_ACCESS_KEY=tu-secret-key
AWS_S3_BUCKET=tu-bucket-name
AWS_REGION=us-east-1

# SMTP (para emails)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu-email@gmail.com
SMTP_PASSWORD=tu-app-password

# SMS (LIWA.co)
LIWA_API_KEY=tu-api-key
LIWA_ACCOUNT=tu-cuenta
LIWA_PASSWORD=tu-password

# Ambiente
ENVIRONMENT=production
DEBUG=false
```

#### 3. Primer despliegue

```bash
# Dar permisos de ejecución a scripts
chmod +x deploy-lightsail.sh
chmod +x DOCS/scripts/deployment/*.sh

# Desplegar (primera vez)
./deploy-lightsail.sh
```

---

## 🔄 Flujo de Trabajo Diario

### Escenario 1: Cambios en Código Python/HTML/CSS/JS

**En Localhost:**
```bash
# 1. Hacer cambios
vim CODE/src/app/routes/packages.py

# 2. Commit y push
git add CODE/src/app/routes/packages.py
git commit -m "fix: corregir validación de paquetes"
git push origin main
```

**En AWS:**
```bash
# Opción rápida (recomendada)
ssh usuario@aws "cd /opt/paqueteria/Paqueteria-v1.0 && ./DOCS/scripts/deployment/pull-only.sh main"

# O conectar y ejecutar
ssh usuario@aws
cd /opt/paqueteria/Paqueteria-v1.0
./DOCS/scripts/deployment/pull-only.sh main
```

**Resultado:** Los cambios se aplican automáticamente gracias a hot reload (no necesitas reiniciar).

---

### Escenario 2: Cambios en Dependencias (requirements.txt)

**En Localhost:**
```bash
# 1. Agregar nueva dependencia
echo "nueva-libreria==1.0.0" >> CODE/requirements.txt

# 2. Commit y push
git add CODE/requirements.txt
git commit -m "deps: agregar nueva-libreria"
git push origin main
```

**En AWS:**
```bash
# Despliegue completo (rebuild necesario)
ssh usuario@aws
cd /opt/paqueteria/Paqueteria-v1.0
./DOCS/scripts/deployment/deploy.sh main
```

**Resultado:** Reconstruye la imagen Docker con las nuevas dependencias.

---

### Escenario 3: Cambios en Docker Compose

**En Localhost:**
```bash
# 1. Modificar docker-compose.prod.yml
vim docker-compose.prod.yml

# 2. Commit y push
git add docker-compose.prod.yml
git commit -m "config: ajustar configuración de Redis"
git push origin main
```

**En AWS:**
```bash
# Despliegue completo
./DOCS/scripts/deployment/deploy.sh main
```

---

## 🤖 Automatización Avanzada

### Opción 1: Script de Despliegue con Un Solo Comando

Crea este script en tu localhost: `deploy-to-aws.sh`

```bash
#!/bin/bash
# Script para desplegar desde localhost a AWS en un solo comando

set -e

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Desplegando a AWS...${NC}"

# 1. Commit y push (si hay cambios)
if [[ -n $(git status -s) ]]; then
    echo -e "${BLUE}📝 Detectados cambios locales${NC}"
    git add .
    read -p "Mensaje del commit: " commit_msg
    git commit -m "$commit_msg"
    git push origin main
    echo -e "${GREEN}✅ Cambios subidos a GitHub${NC}"
else
    echo -e "${GREEN}✅ No hay cambios locales${NC}"
fi

# 2. Desplegar en AWS
echo -e "${BLUE}🔄 Actualizando servidor AWS...${NC}"
ssh usuario@tu-servidor-aws.com "cd /opt/paqueteria/Paqueteria-v1.0 && ./DOCS/scripts/deployment/pull-update.sh"

echo -e "${GREEN}✅ Despliegue completado${NC}"
```

**Uso:**
```bash
chmod +x deploy-to-aws.sh
./deploy-to-aws.sh
```

---

### Opción 2: GitHub Actions (CI/CD Automático)

Crea `.github/workflows/deploy.yml`:

```yaml
name: Deploy to AWS

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - name: Deploy to AWS Server
      uses: appleboy/ssh-action@master
      with:
        host: ${{ secrets.AWS_HOST }}
        username: ${{ secrets.AWS_USER }}
        key: ${{ secrets.AWS_SSH_KEY }}
        script: |
          cd /opt/paqueteria/Paqueteria-v1.0
          ./DOCS/scripts/deployment/pull-update.sh
```

**Configurar secrets en GitHub:**
1. Ve a tu repositorio → Settings → Secrets and variables → Actions
2. Agrega:
   - `AWS_HOST`: IP o dominio de tu servidor
   - `AWS_USER`: usuario SSH
   - `AWS_SSH_KEY`: tu clave privada SSH

**Resultado:** Cada vez que hagas `git push`, se despliega automáticamente en AWS.

---

### Opción 3: Webhook de GitHub

Configura un webhook en tu servidor AWS que escuche pushes de GitHub:

```bash
# En el servidor AWS, instalar webhook listener
sudo apt install webhook

# Crear configuración
sudo nano /etc/webhook/hooks.json
```

```json
[
  {
    "id": "deploy-paqueteria",
    "execute-command": "/opt/paqueteria/Paqueteria-v1.0/DOCS/scripts/deployment/pull-update.sh",
    "command-working-directory": "/opt/paqueteria/Paqueteria-v1.0",
    "response-message": "Deploying...",
    "trigger-rule": {
      "match": {
        "type": "payload-hash-sha1",
        "secret": "tu-secret-webhook",
        "parameter": {
          "source": "header",
          "name": "X-Hub-Signature"
        }
      }
    }
  }
]
```

---

## 📊 Comparación de Métodos

| Método | Complejidad | Velocidad | Automatización | Recomendado para |
|--------|-------------|-----------|----------------|------------------|
| **SSH Manual** | Baja | Media | 0% | Desarrollo inicial |
| **Script Local** | Baja | Alta | 50% | Uso diario |
| **GitHub Actions** | Media | Alta | 100% | Equipos grandes |
| **Webhook** | Alta | Muy Alta | 100% | Producción crítica |

---

## 🎯 Recomendación para tu Caso

Basándome en tu proyecto actual, te recomiendo:

### **Fase 1: Inmediata (Hoy)**
Usa el script `pull-update.sh` que ya tienes:

```bash
# En AWS (cada vez que hagas cambios)
ssh usuario@aws "cd /opt/paqueteria/Paqueteria-v1.0 && ./DOCS/scripts/deployment/pull-update.sh"
```

### **Fase 2: Corto plazo (Esta semana)**
Crea el script `deploy-to-aws.sh` en tu localhost para automatizar todo en un comando.

### **Fase 3: Mediano plazo (Próximo mes)**
Implementa GitHub Actions para despliegue automático en cada push.

---

## 🔍 Verificación Post-Despliegue

Después de cada despliegue, verifica:

```bash
# 1. Estado de contenedores
docker compose -f docker-compose.prod.yml ps

# 2. Health check
curl http://localhost:8000/health

# 3. Logs (últimas 50 líneas)
docker compose -f docker-compose.prod.yml logs --tail=50 app

# 4. Uso de recursos
docker stats --no-stream
```

---

## 🚨 Troubleshooting

### Problema: "Error al hacer pull"
```bash
# Solución: Verificar cambios locales
git status
git stash  # Guardar cambios temporalmente
git pull
```

### Problema: "Contenedor no inicia después del pull"
```bash
# Solución: Rebuild completo
./DOCS/scripts/deployment/deploy.sh main
```

### Problema: "Hot reload no funciona"
```bash
# Verificar que el volumen esté montado correctamente
docker compose -f docker-compose.prod.yml config | grep volumes -A 5

# Reiniciar contenedor
docker compose -f docker-compose.prod.yml restart app
```

---

## 📝 Checklist de Despliegue

- [ ] `.env` configurado en producción (no en GitHub)
- [ ] Git remoto configurado
- [ ] Scripts tienen permisos de ejecución
- [ ] SSH configurado para acceso al servidor
- [ ] RDS y S3 configurados y accesibles
- [ ] Nginx configurado como reverse proxy
- [ ] SSL/TLS configurado (Let's Encrypt)
- [ ] Backups automáticos configurados

---

## 🎓 Comandos de Referencia Rápida

```bash
# LOCALHOST
git add .
git commit -m "mensaje"
git push origin main

# AWS - Actualización rápida
ssh user@aws "cd /path && ./DOCS/scripts/deployment/pull-only.sh main"

# AWS - Actualización inteligente
ssh user@aws "cd /path && ./DOCS/scripts/deployment/pull-update.sh"

# AWS - Despliegue completo
ssh user@aws "cd /path && ./DOCS/scripts/deployment/deploy.sh main"

# Ver logs remotos
ssh user@aws "cd /path && docker compose -f docker-compose.prod.yml logs -f app"
```

---

**Última actualización:** $(date)
**Versión:** 1.0.0
