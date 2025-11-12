# Deploy a Producción - PAQUETERÍA v4.0

## Resumen de cambios recientes
- Única fuente de entorno: `CODE/LOCAL/.env` (no se versiona).
- `docker-compose.prod.yml` sin servicio `nginx` (se usa Nginx del host).
- Fix de arranque: se asegura `src/uploads` antes de iniciar Uvicorn.
- Scripts de despliegue:
  - `DOCS/scripts/deployment/deploy.sh` (pull + build + up -d)
  - `DOCS/scripts/deployment/rollback.sh` (checkout a tag/commit + up -d)
  - `DOCS/scripts/deployment/dev-up.sh` (hot reload con override)
- Override de hot reload: `docker-compose.dev.override.yml`.
- Sparse checkout en el servidor para sincronizar únicamente archivos de producción.

## Requisitos en el servidor
- Git, Docker, Docker Compose plugin.
- Archivo `CODE/LOCAL/.env` (producción) con variables reales.
- Nginx instalado en el host (no en contenedor) y puertos 80/443 abiertos.
- DNS: `paquetex.papyrus.com.co` → 18.214.124.14.

## Estructura mínima (sparse checkout)
En el servidor, dentro del repositorio, usamos sparse-checkout para traer solo archivos de producción:
```
git config core.sparseCheckout true
# modo no-cone para permitir archivos sueltos
git sparse-checkout init --no-cone
# paths requeridos (usar slash inicial)
git sparse-checkout set \
  /docker-compose.prod.yml \
  /docker-compose.dev.override.yml \
  /README_DEPLOY.md \
  /DOCS/scripts/deployment \
  /CODE/Dockerfile \
  /CODE/requirements.txt \
  /CODE/alembic \
  /CODE/alembic.ini \
  /CODE/src

git checkout main && git pull --ff-only
```

## Preparación del entorno
1) Crear `.env` de producción (no versionado):
```
/opt/paqueteria/Paqueteria-v1.0/.env
chmod 600 .env
```
2) Verificar Docker Compose versión: `docker compose version`

## Despliegue (producción estable)

### Deploy Completo (con rebuild)
```
./DOCS/scripts/deployment/deploy.sh main
# Ver estado
docker compose -f docker-compose.prod.yml ps
# Logs app
docker compose -f docker-compose.prod.yml logs --tail=100 app
```

### Solo Actualizar Código (sin rebuild)
```
# Actualizar archivos desde GitHub sin reconstruir
./DOCS/scripts/deployment/pull-only.sh main

# Después, si es necesario reiniciar para aplicar cambios:
docker compose restart app
# O hacer deploy completo si hay cambios en dependencias:
./DOCS/scripts/deployment/deploy.sh main
```

**Cuándo usar cada uno:**
- `pull-only.sh`: Cambios en código que no requieren rebuild (hot-reload activo)
- `deploy.sh`: Cambios que requieren rebuild (nuevas dependencias, cambios en Dockerfile)

## Hot reload remoto (sin rebuild)
```
./DOCS/scripts/deployment/dev-up.sh main
# Edita código o realiza git pull → Uvicorn recarga automáticamente
```
Para volver a producción estable, ejecuta de nuevo `./DOCS/scripts/deployment/deploy.sh main`.

## Nginx del host (reverse proxy + SSL)
Usamos Nginx del host, sin contenedor `nginx` en Compose. La app escucha en `127.0.0.1:8000`.

Ejemplo de server block (Ubuntu/Debian):
```
# /etc/nginx/sites-available/paquetex.papyrus.com.co
server {
    listen 80;
    server_name paquetex.papyrus.com.co;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name paquetex.papyrus.com.co;

    ssl_certificate /etc/letsencrypt/live/paquetex.papyrus.com.co/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/paquetex.papyrus.com.co/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```
Habilitar sitio + Certbot:
```
sudo mkdir -p /var/www/certbot
sudo ln -s /etc/nginx/sites-available/paquetex.papyrus.com.co /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# Certbot (standalone o nginx)
sudo certbot --nginx -d paquetex.papyrus.com.co --non-interactive --agree-tos -m admin@papyrus.com.co
# Renovación automática ya la maneja certbot.timer
```

## Rollback
```
# Volver a un tag o commit específico
./DOCS/scripts/deployment/rollback.sh v1.0.0
```

## Solución de problemas
- App ‘unhealthy’ por `src/uploads` ausente:
  - Compuesto solucionado: el arranque crea `/app/src/uploads` si no existe.
- Puerto 80 ocupado al levantar Compose:
  - El Nginx del host usa 80/443; por eso el servicio `nginx` del Compose está deshabilitado.
- Variables faltantes (DATABASE_URL, SECRET_KEY, AWS_*):
  - Completar en `CODE/LOCAL/.env` del servidor.
- Health check:
  - `curl -sSf http://127.0.0.1:8000/health`

## Configuración Permanente (Auto-Start)

### Servicio Systemd para Docker Compose

Para que Docker Compose se inicie automáticamente después de reinicios:

```bash
# Copiar servicio systemd
sudo cp DOCS/scripts/deployment/paqueteria.service /etc/systemd/system/

# Si el directorio del proyecto es diferente, editarlo:
sudo nano /etc/systemd/system/paqueteria.service
# Cambiar WorkingDirectory si es necesario

# Habilitar para auto-start
sudo systemctl daemon-reload
sudo systemctl enable paqueteria.service
sudo systemctl start paqueteria.service
```

### Script de Configuración Automática

Para configurar todo automáticamente (Nginx + Systemd + SSL):

```bash
sudo ./DOCS/scripts/deployment/setup-production.sh paquetex.papyrus.com.co admin@papyrus.com.co
```

Este script:
- Configura Nginx con proxy reverso
- Crea servicio systemd para auto-start
- Opcionalmente configura SSL con Let's Encrypt
- Instala scripts de verificación

### Verificación Post-Reinicio

Después de reiniciar el servidor, verificar que todo está funcionando:

```bash
sudo /usr/local/bin/verify-paqueteria.sh
```

Ver documentación completa: `DOCS/DEPLOY_PRODUCTION_COMPLETE.md`

## Buenas prácticas
- Mantén `.env` fuera de Git.
- Usa tags semánticos para releases y `rollback.sh` para volver rápidamente.
- Automatiza `deploy.sh` desde CI (opcional) con un job que conecte por SSH.
- Configura servicios systemd para persistencia después de reinicios.
