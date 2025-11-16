# 🚀 Empezar Hoy - Despliegue Automatizado

## ✅ Checklist Rápido (15 minutos)

### Paso 1: Configurar Git y GitHub (5 min)

```bash
# 1. Verificar que tienes Git configurado
git config user.name
git config user.email

# Si no están configurados:
git config --global user.name "Tu Nombre"
git config --global user.email "tu@email.com"

# 2. Verificar remoto de GitHub
git remote -v

# Si no tienes remoto, agregarlo:
git remote add origin https://github.com/tu-usuario/paqueteria-v1.0.git

# 3. Hacer primer push (si no lo has hecho)
git add .
git commit -m "initial commit: proyecto base"
git push -u origin main
```

---

### Paso 2: Configurar SSH al Servidor AWS (5 min)

```bash
# 1. Generar clave SSH (si no tienes)
ssh-keygen -t ed25519 -C "tu@email.com"
# Presiona Enter 3 veces (usa valores por defecto)

# 2. Copiar clave al servidor AWS
ssh-copy-id usuario@tu-servidor-aws.com
# Ingresa tu contraseña cuando te la pida

# 3. Probar conexión
ssh usuario@tu-servidor-aws.com "echo 'Conexión exitosa'"
```

**Nota:** Si usas AWS EC2, necesitas usar tu archivo .pem:
```bash
# Agregar clave al agente SSH
ssh-add ~/.ssh/tu-clave-aws.pem

# O especificar la clave al conectar
ssh -i ~/.ssh/tu-clave-aws.pem ubuntu@tu-servidor-aws.com
```

---

### Paso 3: Configurar Script de Despliegue (2 min)

```bash
# Editar deploy-to-aws.sh
nano deploy-to-aws.sh
```

Cambiar estas líneas (12-14):
```bash
AWS_HOST="ubuntu@ec2-xx-xx-xx-xx.compute.amazonaws.com"  # Tu servidor
AWS_PROJECT_PATH="/opt/paqueteria/Paqueteria-v1.0"       # Ruta en servidor
GIT_BRANCH="main"                                         # Rama a usar
```

Guardar: `Ctrl+O`, `Enter`, `Ctrl+X`

```bash
# Dar permisos de ejecución
chmod +x deploy-to-aws.sh
```

---

### Paso 4: Configurar Servidor AWS (Primera vez - 10 min)

```bash
# 1. Conectar al servidor
ssh usuario@tu-servidor-aws.com

# 2. Instalar Docker (si no está instalado)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker

# 3. Crear directorio del proyecto
sudo mkdir -p /opt/paqueteria
sudo chown $USER:$USER /opt/paqueteria
cd /opt/paqueteria

# 4. Clonar repositorio
git clone https://github.com/tu-usuario/paqueteria-v1.0.git
cd paqueteria-v1.0

# 5. Configurar .env de producción
cp CODE/env.example .env
nano .env
```

**Variables críticas a configurar en .env:**
```bash
# Base de datos (AWS RDS)
DATABASE_URL=postgresql://usuario:password@tu-rds.rds.amazonaws.com:5432/paqueteria

# Seguridad (generar con: openssl rand -hex 32)
SECRET_KEY=tu-secret-key-generado

# Redis
REDIS_PASSWORD=tu-redis-password

# AWS S3
AWS_ACCESS_KEY_ID=tu-access-key
AWS_SECRET_ACCESS_KEY=tu-secret-key
AWS_S3_BUCKET=tu-bucket
AWS_REGION=us-east-1

# Ambiente
ENVIRONMENT=production
DEBUG=false
```

```bash
# 6. Dar permisos a scripts
chmod +x deploy-lightsail.sh
chmod +x DOCS/scripts/deployment/*.sh

# 7. Primer despliegue
./deploy-lightsail.sh
# O si no usas Lightsail:
./DOCS/scripts/deployment/deploy.sh main

# 8. Salir del servidor
exit
```

---

## 🎯 Primer Despliegue de Prueba (2 min)

Ahora que todo está configurado, prueba el flujo completo:

```bash
# 1. En tu localhost, hacer un cambio pequeño
echo "# Test de despliegue" >> README.md

# 2. Desplegar con un solo comando
./deploy-to-aws.sh "test: primer despliegue automatizado"

# 3. Observar el proceso
# El script hará:
# - Commit del cambio
# - Push a GitHub
# - Pull en AWS
# - Verificación automática
```

**Resultado esperado:**
```
========================================
🚀 DESPLIEGUE AUTOMATIZADO A AWS
========================================

ℹ️  Verificando configuración...
✅ Configuración verificada

▶️  Verificando estado del repositorio local...
ℹ️  Cambios detectados:
 M README.md

▶️  Preparando commit...
ℹ️  Haciendo commit...
✅ Commit realizado: test: primer despliegue automatizado
ℹ️  Subiendo cambios a GitHub...
✅ Cambios subidos a GitHub correctamente

▶️  Desplegando en servidor AWS...
ℹ️  Conectando a: ubuntu@tu-servidor.com
✅ Conexión SSH verificada

ℹ️  Ejecutando actualización en AWS...
─────────────────────────────────────────
[Logs del servidor...]
✅ Pull completado exitosamente
─────────────────────────────────────────

▶️  Verificando despliegue...
✅ Health check exitoso

========================================
✅ DESPLIEGUE COMPLETADO
========================================

✨ Todo listo!
```

---

## 📝 Uso Diario (30 segundos)

Una vez configurado, tu flujo diario es súper simple:

```bash
# 1. Hacer cambios en tu código
vim CODE/src/app/routes/packages.py

# 2. Desplegar
./deploy-to-aws.sh "fix: corregir validación de paquetes"

# ¡Listo! En 30 segundos está en producción
```

---

## 🔍 Verificar que Todo Funciona

### En tu Localhost

```bash
# Verificar Git
git status
git remote -v

# Verificar SSH
ssh usuario@tu-servidor-aws.com "echo 'OK'"

# Verificar script
./deploy-to-aws.sh --help  # (no existe --help, pero verás el error si hay problema)
```

### En el Servidor AWS

```bash
# Conectar
ssh usuario@tu-servidor-aws.com

# Verificar contenedores
cd /opt/paqueteria/Paqueteria-v1.0
docker compose ps

# Verificar health check
curl http://localhost:8000/health

# Ver logs
docker compose logs --tail=50 app
```

---

## 🚨 Solución de Problemas Comunes

### Problema 1: "Permission denied (publickey)"

**Causa:** SSH no configurado correctamente

**Solución:**
```bash
# Verificar que la clave SSH existe
ls -la ~/.ssh/

# Si no existe, crearla
ssh-keygen -t ed25519 -C "tu@email.com"

# Copiar al servidor
ssh-copy-id usuario@tu-servidor-aws.com

# O si usas .pem de AWS:
ssh -i ~/.ssh/tu-clave.pem ubuntu@servidor
```

---

### Problema 2: "No se pudo conectar al servidor AWS"

**Causa:** Firewall o configuración de seguridad

**Solución:**
```bash
# Verificar que el puerto 22 está abierto en AWS Security Group
# En AWS Console:
# EC2 → Security Groups → Tu grupo → Inbound rules
# Debe tener: SSH (22) desde tu IP

# Verificar IP pública del servidor
# En AWS Console: EC2 → Instances → Tu instancia → Public IPv4
```

---

### Problema 3: "Error al hacer push a GitHub"

**Causa:** Credenciales no configuradas

**Solución:**
```bash
# Configurar credenciales
git config --global user.name "Tu Nombre"
git config --global user.email "tu@email.com"

# Si usa HTTPS, configurar token de GitHub
# GitHub → Settings → Developer settings → Personal access tokens
# Crear token y usarlo como password

# O cambiar a SSH
git remote set-url origin git@github.com:tu-usuario/paqueteria-v1.0.git
```

---

### Problema 4: "Health check falló"

**Causa:** Aplicación no inició correctamente

**Solución:**
```bash
# Ver logs
ssh usuario@aws "cd /opt/paqueteria/Paqueteria-v1.0 && docker compose logs --tail=100 app"

# Verificar .env
ssh usuario@aws "cd /opt/paqueteria/Paqueteria-v1.0 && cat .env | grep DATABASE_URL"

# Reiniciar
ssh usuario@aws "cd /opt/paqueteria/Paqueteria-v1.0 && docker compose restart app"
```

---

## 📚 Comandos de Referencia

### Comandos Locales (Localhost)

```bash
# Ver estado de Git
git status

# Ver cambios
git diff

# Desplegar
./deploy-to-aws.sh "mensaje"

# Ver logs remotos
ssh usuario@aws "cd /path && docker compose logs -f app"
```

### Comandos Remotos (AWS)

```bash
# Conectar
ssh usuario@tu-servidor-aws.com

# Ver contenedores
docker compose ps

# Ver logs
docker compose logs -f app

# Reiniciar
docker compose restart app

# Ver uso de recursos
docker stats

# Health check
curl http://localhost:8000/health
```

---

## 🎓 Próximos Pasos

Una vez que tengas el flujo básico funcionando:

### Semana 1
- [ ] Configurar dominio personalizado
- [ ] Configurar SSL con Let's Encrypt
- [ ] Configurar Nginx como reverse proxy

### Semana 2
- [ ] Configurar backups automáticos
- [ ] Configurar monitoreo con alertas
- [ ] Documentar tu configuración específica

### Mes 1
- [ ] Implementar GitHub Actions para CI/CD
- [ ] Configurar staging environment
- [ ] Implementar rollback automático

---

## 📞 Ayuda Rápida

Si algo no funciona:

1. **Verifica la configuración:**
   ```bash
   # Localhost
   git remote -v
   ssh usuario@aws "echo OK"
   cat deploy-to-aws.sh | grep AWS_HOST
   
   # AWS
   ssh usuario@aws "cd /path && docker compose ps"
   ```

2. **Revisa los logs:**
   ```bash
   # Logs de la aplicación
   ssh usuario@aws "cd /path && docker compose logs --tail=100 app"
   
   # Logs de Git
   git log --oneline -5
   ```

3. **Reinicia si es necesario:**
   ```bash
   ssh usuario@aws "cd /path && docker compose restart app"
   ```

---

## ✅ Checklist Final

Antes de considerar que todo está listo:

- [ ] Git configurado con remoto a GitHub
- [ ] SSH funciona sin contraseña al servidor AWS
- [ ] `deploy-to-aws.sh` editado con tus valores
- [ ] Proyecto clonado en servidor AWS
- [ ] `.env` configurado en servidor AWS (no en GitHub)
- [ ] Primer despliegue manual exitoso
- [ ] Primer despliegue con script exitoso
- [ ] Health check responde correctamente
- [ ] Puedes ver logs remotos
- [ ] Documentaste tu configuración específica

---

## 🎉 ¡Felicidades!

Si completaste todos los pasos, ahora tienes:

✅ Despliegue automatizado en un solo comando
✅ Flujo de trabajo eficiente
✅ Hot reload para cambios rápidos
✅ Verificación automática post-despliegue

**Tu nuevo flujo de trabajo:**
```bash
# Hacer cambios → Desplegar → ¡Listo!
vim codigo.py
./deploy-to-aws.sh "mensaje"
# 30 segundos después está en producción
```

---

**Creado:** $(date)
**Tiempo estimado:** 15-30 minutos
**Dificultad:** Baja
