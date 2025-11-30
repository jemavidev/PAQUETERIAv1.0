# 🚀 COMANDOS PARA CONFIGURAR STAGING

Copia y pega estos comandos en orden. Todo está listo para funcionar sin conflictos.

---

## 📍 PASO 1: CREAR RAMA STAGING (Desde tu máquina local)

```bash
# Ir al proyecto
cd "/home/stk/Insync/dispapyrussas@gmail.com/Google Drive/PAPYRUS/EL CLUB/SERVICIO DE PAQUETERIA/PAQUETERIA v1.0"

# Crear rama staging
git checkout main
git pull origin main
git checkout -b staging
git push -u origin staging

# Verificar
git branch -a
```

---

## 📍 PASO 2: CLONAR EN SERVIDOR (Desde el servidor)

```bash
# Conectar al servidor
ssh papyrus

# Obtener URL del repositorio (necesitas esto)
# Ve a GitHub y copia la URL de tu repo
# Ejemplo: https://github.com/usuario/paqueteria.git

# Clonar en ruta staging
cd /home/ubuntu
git clone TU_URL_DE_GITHUB paqueteria-staging
cd paqueteria-staging
git checkout staging

# Verificar
pwd
git branch
```

---

## 📍 PASO 3: CONFIGURAR NGINX (Desde el servidor)

```bash
# Copiar configuración
sudo cp /home/ubuntu/paqueteria-staging/.deploy/templates/nginx-staging.conf /etc/nginx/sites-available/staging

# Crear symlink
sudo ln -s /etc/nginx/sites-available/staging /etc/nginx/sites-enabled/staging

# Verificar y recargar
sudo nginx -t
sudo systemctl reload nginx

# Abrir puertos
sudo ufw allow 8080/tcp
sudo ufw allow 8443/tcp
```

---

## 📍 PASO 4: PRIMER DEPLOY (Desde tu máquina local)

```bash
# Volver a tu máquina local
cd "/home/stk/Insync/dispapyrussas@gmail.com/Google Drive/PAPYRUS/EL CLUB/SERVICIO DE PAQUETERIA/PAQUETERIA v1.0"

# Deploy a staging
./deploy.sh --env staging --deploy
```

---

## 📍 PASO 5: VERIFICAR (Desde tu máquina local)

```bash
# Ver estado
./deploy.sh --env staging --status

# Ver logs
./deploy.sh --env staging --logs

# Probar health check
curl http://staging.jemavi.co:8080/health

# O desde navegador:
# http://staging.jemavi.co:8080
```

---

## 📍 PASO 6 (OPCIONAL): CONFIGURAR SSL

```bash
# Desde el servidor
ssh papyrus

# Obtener certificado
sudo certbot certonly --nginx -d staging.jemavi.co

# Editar configuración de Nginx
sudo nano /etc/nginx/sites-available/staging

# Descomentar estas líneas (quitar el #):
# ssl_certificate /etc/letsencrypt/live/staging.jemavi.co/fullchain.pem;
# ssl_certificate_key /etc/letsencrypt/live/staging.jemavi.co/privkey.pem;
# include /etc/letsencrypt/options-ssl-nginx.conf;
# ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

# Guardar (Ctrl+O, Enter, Ctrl+X)

# Recargar Nginx
sudo nginx -t
sudo systemctl reload nginx

# Probar HTTPS
curl https://staging.jemavi.co:8443/health
```

---

## ✅ VERIFICACIÓN FINAL

```bash
# Desde el servidor
ssh papyrus

# Ver contenedores de staging
docker ps | grep staging

# Debe mostrar:
# paqueteria_staging_app
# paqueteria_staging_redis

# Ver contenedores de producción (deben seguir corriendo)
docker ps | grep prod

# Ver puertos en uso
ss -tlnp | grep -E '8000|8001|6379|6380|8080|8443'

# Producción: 8000, 6379
# Staging: 8001, 6380, 8080, 8443
```

---

## 🎯 USO DIARIO

### Hacer cambios estéticos:

```bash
# 1. Editar archivos (CSS, HTML, JS, templates)
# 2. Commit a staging
git checkout staging
git add .
git commit -m "Cambios estéticos: descripción"
git push origin staging

# 3. Deploy a staging
./deploy.sh --env staging --deploy

# 4. Ver en navegador:
# http://staging.jemavi.co:8080

# 5. Si todo OK, llevar a producción:
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

# Ver logs
./deploy.sh --env staging --logs

# Restart staging
./deploy.sh --env staging --restart

# Pull última versión
./deploy.sh --env staging --pull

# Health check
./deploy.sh --env staging --health

# Cambiar entre entornos
./deploy.sh  # Modo interactivo
```

---

## ⚠️ IMPORTANTE

- ✅ Staging usa puertos diferentes (sin conflictos)
- ✅ Staging usa contenedores separados
- ✅ Staging usa ruta separada
- ⚠️ Staging comparte la misma base de datos
- ❌ NO ejecutar migraciones en staging
- ❌ NO hacer backups desde staging
- ✅ Staging es SOLO para cambios visuales

---

## 🆘 SI ALGO FALLA

### Puerto 8001 ocupado:
```bash
ssh papyrus "sudo lsof -i :8001"
ssh papyrus "sudo kill -9 PID"
```

### Nginx no funciona:
```bash
ssh papyrus "sudo nginx -t"
ssh papyrus "sudo systemctl restart nginx"
ssh papyrus "sudo systemctl status nginx"
```

### No se ve el sitio:
```bash
# Verificar DNS
nslookup staging.jemavi.co

# Verificar firewall
ssh papyrus "sudo ufw status"
```

### Ver logs de contenedores:
```bash
ssh papyrus "cd /home/ubuntu/paqueteria-staging && docker compose -f docker-compose.staging.yml logs -f"
```

---

## 📞 NECESITAS LA URL DE GITHUB

Antes de ejecutar el PASO 2, necesitas la URL de tu repositorio de GitHub.

**¿Dónde encontrarla?**
1. Ve a tu repositorio en GitHub
2. Click en el botón verde "Code"
3. Copia la URL HTTPS
4. Ejemplo: `https://github.com/usuario/paqueteria.git`

**Úsala en el comando:**
```bash
git clone TU_URL_AQUI paqueteria-staging
```

---

¡Listo! Con estos comandos tendrás staging funcionando sin conflictos.
