# ✅ STAGING CONFIGURADO - SERVIDOR DEDICADO

## 📊 INFORMACIÓN DEL SERVIDOR

**Servidor Staging:**
- **IP**: 3.81.183.102
- **Dominio**: staging.jemavi.co
- **SSH**: `ssh staging`
- **RAM**: 416MB + 1GB SWAP
- **CPU**: 2 cores
- **Disco**: 19GB (17GB libres)
- **OS**: Ubuntu 24.04 LTS

---

## ✅ CONFIGURACIÓN COMPLETADA

### 1. Infraestructura Base
- ✅ SWAP de 1GB configurado (swappiness=10)
- ✅ Docker 29.1.1 instalado
- ✅ Nginx 1.24.0 instalado
- ✅ Firewall configurado (puertos 22, 80)
- ✅ Git configurado

### 2. Proyecto
- ✅ Repositorio clonado en `/home/ubuntu/paqueteria-staging`
- ✅ Rama `staging` activa
- ✅ Archivo `.env` copiado desde producción

### 3. Docker Compose Ultra-Minimal
- ✅ Solo servicio App (sin Redis, sin Celery)
- ✅ Límite de memoria: 300MB
- ✅ 1 worker de Uvicorn
- ✅ Logs mínimos (5MB max, 2 archivos)
- ✅ Volúmenes para edición sin rebuild:
  - `/static` (CSS, JS, imágenes)
  - `/templates` (HTML)

### 4. Nginx
- ✅ Configuración optimizada para 416MB RAM
- ✅ Proxy a `localhost:8001`
- ✅ Cache de archivos estáticos
- ✅ Timeouts reducidos (20s)

### 5. Deploy Script
- ✅ Configuración `.deploy/config/staging.conf` actualizada
- ✅ SSH_HOST: "staging"
- ✅ PROJECT_PATH: "/home/ubuntu/paqueteria-staging"
- ✅ Health check: 60s timeout, 30 reintentos

---

## 🎯 RECURSOS ACTUALES

```
RAM:
- Total: 416MB
- Usado: ~270MB
- Libre: ~150MB
- SWAP: 1GB (230MB usado)

Docker:
- App: 30MB RAM (límite 300MB)
- CPU: 0.12%
- Estado: Healthy
```

---

## 🚀 CÓMO USAR

### Deploy Completo
```bash
./deploy.sh --env staging --deploy
```

### Ver Estado
```bash
./deploy.sh --env staging --status
```

### Ver Logs
```bash
./deploy.sh --env staging --logs
```

### Git Pull
```bash
./deploy.sh --env staging --pull
```

### Restart
```bash
./deploy.sh --env staging --restart
```

---

## 📝 FLUJO DE TRABAJO

### Para cambios CSS/HTML/JS:

1. **Editar archivos localmente**
   ```bash
   # Editar archivos en CODE/src/static/ o CODE/src/templates/
   ```

2. **Commit a rama staging**
   ```bash
   git checkout staging
   git add .
   git commit -m "Cambios visuales: descripción"
   git push origin staging
   ```

3. **Deploy a staging**
   ```bash
   ./deploy.sh --env staging --deploy
   ```

4. **Verificar en navegador**
   ```
   http://staging.jemavi.co
   ```

5. **Si todo OK, merge a main**
   ```bash
   git checkout main
   git merge staging
   git push origin main
   ```

6. **Deploy a producción**
   ```bash
   ./deploy.sh --env papyrus --deploy
   ```

---

## 🔧 EDICIÓN SIN REBUILD

Los archivos en `/static` y `/templates` son volúmenes montados.
Para ver cambios sin rebuild:

```bash
# 1. Hacer cambios en local
# 2. Push a GitHub
git push origin staging

# 3. Pull en servidor y restart
ssh staging "cd /home/ubuntu/paqueteria-staging && git pull origin staging"
ssh staging "docker restart paqueteria_staging_app"

# Cambios visibles en ~10 segundos
```

---

## ⚠️ LIMITACIONES

1. **Solo para cambios visuales**
   - CSS, HTML, JavaScript
   - Imágenes, PDFs
   - Templates Jinja2

2. **NO para:**
   - Cambios en lógica Python
   - Migraciones de base de datos
   - Cambios en dependencias
   - Tests de carga

3. **Recursos limitados:**
   - 416MB RAM (puede ser lento)
   - Sin Redis (sin cache)
   - Sin Celery (sin tareas async)
   - Sin monitoring

---

## 🆘 TROUBLESHOOTING

### Contenedor no inicia
```bash
ssh staging "cd /home/ubuntu/paqueteria-staging && docker compose -f docker-compose.staging.yml logs"
```

### Nginx da 502
```bash
ssh staging "sudo tail -50 /var/log/nginx/error.log"
ssh staging "curl http://localhost:8001/health"
```

### Memoria llena
```bash
ssh staging "free -h"
ssh staging "docker stats --no-stream"
# Si es necesario, restart:
ssh staging "docker restart paqueteria_staging_app"
```

### No se ven cambios CSS
```bash
# Limpiar cache del navegador (Ctrl+Shift+R)
# O verificar que los archivos se actualizaron:
ssh staging "ls -la /home/ubuntu/paqueteria-staging/CODE/src/static/"
```

---

## 📊 MONITOREO

### Ver recursos
```bash
ssh staging "htop"
```

### Ver logs en tiempo real
```bash
ssh staging "docker logs -f paqueteria_staging_app"
```

### Ver estado de Docker
```bash
ssh staging "docker ps"
ssh staging "docker stats"
```

---

## 🔐 SEGURIDAD

- ✅ Firewall activo (solo puertos 22, 80)
- ✅ SSH con clave privada
- ✅ Contenedor con límites de recursos
- ✅ Nginx con headers de seguridad
- ⚠️ Sin SSL (opcional configurar Let's Encrypt)

---

## 📞 INFORMACIÓN IMPORTANTE

**URLs:**
- Staging: http://staging.jemavi.co
- Health: http://staging.jemavi.co/health
- Docs: http://staging.jemavi.co/docs

**Archivos clave:**
- Docker Compose: `docker-compose.staging.yml`
- Nginx: `/etc/nginx/sites-available/staging`
- Deploy Config: `.deploy/config/staging.conf`
- Logs: `docker logs paqueteria_staging_app`

**Comandos SSH directos:**
```bash
ssh staging "docker ps"
ssh staging "docker logs paqueteria_staging_app --tail 50"
ssh staging "free -h"
ssh staging "docker restart paqueteria_staging_app"
```

---

## ✅ CHECKLIST FINAL

- [x] Servidor configurado con SWAP
- [x] Docker instalado
- [x] Nginx configurado
- [x] Proyecto clonado
- [x] Rama staging activa
- [x] .env configurado
- [x] Contenedor corriendo
- [x] Health check OK
- [x] Nginx proxy OK
- [x] Deploy script configurado
- [x] Firewall configurado
- [x] Recursos optimizados

---

**¡Staging está listo para usar!** 🎉

Tiempo total de setup: ~20 minutos
Uso de RAM: ~30MB por contenedor
Perfecto para visualizar cambios CSS/HTML antes de producción.
