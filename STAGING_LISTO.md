# ✅ STAGING COMPLETAMENTE FUNCIONAL

## 🎉 ESTADO FINAL

**Staging está 100% operativo y accesible desde internet**

---

## 📊 INFORMACIÓN DEL SERVIDOR

- **IP**: 3.81.183.102
- **Dominio**: http://staging.jemavi.co
- **SSH**: `ssh staging`
- **RAM**: 416MB + 1GB SWAP
- **CPU**: 2 cores
- **OS**: Ubuntu 24.04 LTS

---

## ✅ CONFIGURACIÓN IMPLEMENTADA

### 1. Docker Compose con `network_mode: host`
```yaml
services:
  app:
    network_mode: host  # Solución al problema de port mapping
    ports: NINGUNO      # No necesarios con host mode
    command: uvicorn --host 127.0.0.1 --port 8000
```

**Ventajas**:
- Sin problemas de port mapping
- Conexión directa entre Nginx y contenedor
- Menor overhead de red

### 2. Nginx
```nginx
upstream fastapi_staging {
    server 127.0.0.1:8000;  # Conecta directamente al contenedor
}
```

### 3. Recursos Actuales
```
RAM:
- Total: 416MB
- Usado: ~270MB
- Libre: ~145MB
- SWAP: 1GB (165MB usado)

Docker:
- App: 98MB RAM (límite 300MB)
- CPU: 0.14%
- Estado: Healthy ✅
```

---

## 🚀 URLs FUNCIONANDO

- **Health**: http://staging.jemavi.co/health ✅
- **Docs**: http://staging.jemavi.co/docs ✅
- **App**: http://staging.jemavi.co/ ✅

---

## 📝 CÓMO USAR

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

### Restart
```bash
./deploy.sh --env staging --restart
```

---

## 🔄 FLUJO DE TRABAJO

### Para cambios CSS/HTML:

1. **Editar localmente**
   ```bash
   # Editar archivos en CODE/src/static/ o CODE/src/templates/
   ```

2. **Commit a staging**
   ```bash
   git checkout staging
   git add .
   git commit -m "Cambios visuales"
   git push origin staging
   ```

3. **Deploy**
   ```bash
   ./deploy.sh --env staging --deploy
   ```

4. **Verificar**
   ```
   http://staging.jemavi.co
   ```

5. **Si OK, merge a main**
   ```bash
   git checkout main
   git merge staging
   git push origin main
   ./deploy.sh --env papyrus --deploy
   ```

---

## 🔧 ARCHIVOS CLAVE

### Docker Compose
```yaml
# docker-compose.staging-minimal.yml
name: "PAQUETERIA_STAGING"

services:
  app:
    network_mode: host
    mem_limit: 300m
    command: uvicorn --host 127.0.0.1 --port 8000
    volumes:
      - ./CODE/src/static:/app/src/static
      - ./CODE/src/templates:/app/src/templates
```

### Nginx
```nginx
# /etc/nginx/sites-available/staging
upstream fastapi_staging {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name staging.jemavi.co;
    location / {
        proxy_pass http://fastapi_staging;
    }
}
```

### Deploy Config
```bash
# .deploy/config/staging.conf
SSH_HOST="staging"
PROJECT_PATH="/home/ubuntu/paqueteria-staging"
DOCKER_COMPOSE_FILE="docker-compose.staging.yml"
GIT_BRANCH="staging"
```

---

## ⚠️ LIMITACIONES

1. **Solo para cambios visuales**
   - CSS, HTML, JavaScript
   - Imágenes, PDFs
   - Templates

2. **NO para**:
   - Cambios en lógica Python (requiere rebuild)
   - Migraciones de BD
   - Tests de carga

3. **Recursos limitados**:
   - 416MB RAM (puede ser lento con muchas peticiones)
   - Sin Redis (sin cache)
   - Sin Celery (sin tareas async)

---

## 🆘 TROUBLESHOOTING

### Contenedor no inicia
```bash
ssh staging "docker logs paqueteria_staging_app"
```

### Nginx da 502
```bash
ssh staging "sudo tail -50 /var/log/nginx/error.log"
ssh staging "curl http://127.0.0.1:8000/health"
```

### Memoria llena
```bash
ssh staging "free -h"
ssh staging "docker restart paqueteria_staging_app"
```

---

## 📞 COMANDOS ÚTILES

```bash
# Ver recursos
ssh staging "htop"

# Ver logs en tiempo real
ssh staging "docker logs -f paqueteria_staging_app"

# Restart rápido
ssh staging "docker restart paqueteria_staging_app"

# Ver estado
ssh staging "docker ps"
ssh staging "docker stats"

# Health check
curl http://staging.jemavi.co/health
```

---

## ✅ CHECKLIST FINAL

- [x] Servidor configurado con SWAP
- [x] Docker instalado
- [x] Nginx configurado
- [x] Proyecto clonado
- [x] Rama staging activa
- [x] .env configurado
- [x] Contenedor corriendo con network_mode: host
- [x] Health check OK
- [x] Nginx funcionando
- [x] URLs accesibles desde internet
- [x] Deploy script configurado
- [x] Recursos optimizados

---

## 🎯 RESUMEN TÉCNICO

**Problema resuelto**: Port mapping de Docker causaba "Connection reset by peer"

**Solución**: Usar `network_mode: host` en Docker Compose

**Resultado**: 
- Contenedor corre directamente en el host
- Nginx se conecta a 127.0.0.1:8000 sin problemas
- Sin overhead de red Docker
- Staging 100% funcional

**Uso de recursos**:
- RAM: 98MB (de 300MB límite)
- CPU: 0.14%
- SWAP: 165MB (de 1GB)

---

**¡Staging está listo para usar!** 🚀

Tiempo total de configuración: ~45 minutos
Perfecto para visualizar cambios CSS/HTML antes de producción.
