# 🚀 SETUP STAGING - GUÍA COMPLETA

Esta guía te llevará paso a paso para configurar el entorno de staging.

## 📋 INFORMACIÓN DEL ENTORNO

**STAGING:**
- Servidor: 18.214.124.14 (mismo que producción)
- Dominio: staging.jemavi.co
- Ruta: /home/ubuntu/paqueteria-staging
- Puertos HTTP: 8080
- Puertos HTTPS: 8443
- App: Puerto 8001
- Redis: Puerto 6380
- Rama Git: staging

**SIN CONFLICTOS CON PRODUCCIÓN:**
- ✅ Rutas separadas
- ✅ Puertos diferentes
- ✅ Contenedores con nombres únicos
- ✅ Red Docker separada
- ✅ Volúmenes separados
- ⚠️ Misma base de datos (solo cambios visuales)

---

## 🔧 PASO 1: CREAR RAMA STAGING EN GIT

Desde tu máquina local:

```bash
# Ir al directorio del proyecto
cd "/home/stk/Insync/dispapyrussas@gmail.com/Google Drive/PAPYRUS/EL CLUB/SERVICIO DE PAQUETERIA/PAQUETERIA v1.0"

# Crear rama staging desde main
git checkout main
git pull origin main
git checkout -b staging
git push -u origin staging

# Verificar
git branch -a
```

---

## 🔧 PASO 2: CLONAR PROYECTO EN SERVIDOR (RUTA STAGING)

```bash
# Conectar al servidor
ssh papyrus

# Clonar en ruta separada
cd /home/ubuntu
git clone https://github.com/TU_USUARIO/TU_REPO.git paqueteria-staging
cd paqueteria-staging

# Cambiar a rama staging
git checkout staging

# Verificar
pwd  # Debe mostrar: /home/ubuntu/paqueteria-staging
git branch  # Debe mostrar: * staging
```

---

## 🔧 PASO 3: CONFIGURAR NGINX PARA STAGING

```bash
# Copiar configuración de Nginx
sudo cp /home/ubuntu/paqueteria-staging/.deploy/templates/nginx-staging.conf /etc/nginx/sites-available/staging

# Crear symlink
sudo ln -s /etc/nginx/sites-available/staging /etc/nginx/sites-enabled/staging

# Verificar configuración
sudo nginx -t

# Si todo OK, recargar Nginx
sudo systemctl reload nginx

# Verificar que Nginx está corriendo
sudo systemctl status nginx
```

---

## 🔧 PASO 4: CONFIGURAR SSL CON CERTBOT (OPCIONAL)

```bash
# Instalar Certbot si no está instalado
sudo apt update
sudo apt install certbot python3-certbot-nginx -y

# Obtener certificado SSL para staging
sudo certbot certonly --nginx -d staging.jemavi.co

# Editar configuración de Nginx para habilitar SSL
sudo nano /etc/nginx/sites-available/staging

# Descomentar las líneas SSL:
# ssl_certificate /etc/letsencrypt/live/staging.jemavi.co/fullchain.pem;
# ssl_certificate_key /etc/letsencrypt/live/staging.jemavi.co/privkey.pem;
# include /etc/letsencrypt/options-ssl-nginx.conf;
# ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

# Recargar Nginx
sudo nginx -t
sudo systemctl reload nginx
```

---

## 🔧 PASO 5: PRIMER DEPLOY DE STAGING

Desde tu máquina local:

```bash
# Usar el sistema de deploy
./deploy.sh

# Seleccionar entorno: staging (opción 3)
# Luego: Deploy Completo (opción 1)
```

O directamente:

```bash
./deploy.sh --env staging --deploy
```

---

## 🔧 PASO 6: VERIFICAR QUE TODO FUNCIONA

```bash
# Verificar contenedores
ssh papyrus "docker ps | grep staging"

# Debe mostrar:
# paqueteria_staging_app
# paqueteria_staging_redis

# Verificar puertos
ssh papyrus "netstat -tlnp | grep -E '8001|6380|8080|8443'"

# Verificar health check
curl http://staging.jemavi.co:8080/health
# O con SSL:
curl https://staging.jemavi.co:8443/health

# Ver logs
./deploy.sh --env staging --logs
```

---

## 📊 VERIFICACIÓN DE NO CONFLICTOS

```bash
# Verificar que producción sigue corriendo
ssh papyrus "docker ps | grep prod"

# Debe mostrar todos los contenedores de producción activos

# Verificar puertos en uso
ssh papyrus "ss -tlnp | grep -E '80|443|8000|8001|6379|6380|8080|8443'"

# Producción: 80, 443, 8000, 6379
# Staging: 8080, 8443, 8001, 6380
```

---

## 🎯 FLUJO DE TRABAJO DIARIO

### Para hacer cambios estéticos:

```bash
# 1. Hacer cambios en tu código local (CSS, HTML, JS)
# 2. Commit a rama staging
git checkout staging
git add .
git commit -m "Cambios estéticos: descripción"
git push origin staging

# 3. Deploy a staging
./deploy.sh --env staging --deploy

# 4. Verificar en: http://staging.jemavi.co:8080
# O con SSL: https://staging.jemavi.co:8443

# 5. Si todo OK, merge a main y deploy a producción
git checkout main
git merge staging
git push origin main
./deploy.sh --env papyrus --deploy
```

---

## 🔍 COMANDOS ÚTILES

```bash
# Ver estado de staging
./deploy.sh --env staging --status

# Ver logs de staging
./deploy.sh --env staging --logs

# Restart staging
./deploy.sh --env staging --restart

# Pull última versión
./deploy.sh --env staging --pull

# Health check
./deploy.sh --env staging --health
```

---

## ⚠️ IMPORTANTE

1. **NO ejecutar migraciones en staging** (comparte BD con producción)
2. **NO hacer backups desde staging** (misma BD)
3. **Staging es SOLO para cambios visuales/estéticos**
4. **Siempre probar en staging antes de producción**

---

## 🆘 TROUBLESHOOTING

### Problema: Puerto 8001 ya en uso
```bash
ssh papyrus "sudo lsof -i :8001"
# Matar proceso si es necesario
ssh papyrus "sudo kill -9 PID"
```

### Problema: Nginx no recarga
```bash
ssh papyrus "sudo nginx -t"
ssh papyrus "sudo systemctl restart nginx"
```

### Problema: Contenedores no inician
```bash
ssh papyrus "cd /home/ubuntu/paqueteria-staging && docker compose -f docker-compose.staging.yml logs"
```

### Problema: No se ve el sitio
```bash
# Verificar DNS
nslookup staging.jemavi.co

# Verificar firewall
ssh papyrus "sudo ufw status"
ssh papyrus "sudo ufw allow 8080/tcp"
ssh papyrus "sudo ufw allow 8443/tcp"
```

---

## ✅ CHECKLIST FINAL

- [ ] Rama staging creada y pusheada
- [ ] Proyecto clonado en /home/ubuntu/paqueteria-staging
- [ ] Nginx configurado y funcionando
- [ ] SSL configurado (opcional)
- [ ] Primer deploy exitoso
- [ ] Contenedores corriendo sin conflictos
- [ ] Sitio accesible en staging.jemavi.co:8080
- [ ] Producción sigue funcionando normalmente

---

¡Listo! Ahora tienes staging funcionando sin conflictos con producción.
