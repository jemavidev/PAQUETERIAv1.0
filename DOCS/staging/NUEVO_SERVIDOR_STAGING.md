# 🚀 CONFIGURACIÓN RÁPIDA - NUEVO SERVIDOR STAGING

## 📋 INFORMACIÓN DEL NUEVO SERVIDOR

Una vez tengas el nuevo servidor, necesitarás:
- **IP del nuevo servidor**: _____________
- **Dominio**: staging.jemavi.co (actualizar DNS)
- **Recursos recomendados**: Mínimo 2GB RAM

---

## ⚡ PASOS RÁPIDOS (15 minutos)

### 1️⃣ Configurar SSH (2 min)

```bash
# Agregar el nuevo servidor a ~/.ssh/config
nano ~/.ssh/config

# Agregar:
Host staging
    HostName [IP_DEL_NUEVO_SERVIDOR]
    User ubuntu
    IdentityFile ~/.ssh/id_rsa
```

### 2️⃣ Instalar Docker en el nuevo servidor (5 min)

```bash
ssh staging

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Instalar Docker Compose
sudo apt update
sudo apt install docker-compose-plugin -y

# Verificar
docker --version
docker compose version

exit
```

### 3️⃣ Clonar proyecto y configurar (3 min)

```bash
ssh staging

# Clonar proyecto
cd /home/ubuntu
git clone https://github.com/jemavidev/PAQUETERIAv1.0.git paqueteria-staging
cd paqueteria-staging
git checkout staging

# Copiar archivo .env (desde producción o crear nuevo)
# Si tienes acceso a producción:
scp papyrus:/home/ubuntu/paqueteria/CODE/.env ./CODE/.env

exit
```

### 4️⃣ Instalar y configurar Nginx (3 min)

```bash
ssh staging

# Instalar Nginx
sudo apt update
sudo apt install nginx -y

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
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

exit
```

### 5️⃣ Hacer primer deploy (2 min)

Desde tu máquina local:

```bash
# Actualizar .deploy/config/staging.conf con la nueva IP
# Cambiar SSH_HOST de "papyrus" a "staging"

# Deploy
./deploy.sh --env staging --deploy
```

### 6️⃣ Actualizar DNS (manual)

En tu proveedor de DNS:
- Cambiar el registro A de `staging.jemavi.co`
- Nueva IP: [IP_DEL_NUEVO_SERVIDOR]
- TTL: 300 (5 minutos)

### 7️⃣ Configurar SSL (opcional, 2 min)

```bash
ssh staging

# Instalar Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtener certificado
sudo certbot --nginx -d staging.jemavi.co

# Verificar renovación automática
sudo certbot renew --dry-run

exit
```

---

## ✅ VERIFICACIÓN FINAL

```bash
# Probar health check
curl http://staging.jemavi.co:8080/health

# Ver estado
./deploy.sh --env staging --status

# Ver logs
./deploy.sh --env staging --logs

# Acceder desde navegador
http://staging.jemavi.co:8080
```

---

## 🔧 CONFIGURACIÓN ADICIONAL (Opcional)

### Firewall de AWS Lightsail

En la consola de AWS:
1. Ve a tu instancia
2. Pestaña "Networking"
3. Agregar reglas:
   - Custom TCP, Port 8080
   - Custom TCP, Port 8443
   - SSH, Port 22
   - HTTP, Port 80
   - HTTPS, Port 443

### Monitoreo básico

```bash
ssh staging

# Ver recursos
htop

# Ver contenedores
docker ps

# Ver logs de Nginx
sudo tail -f /var/log/nginx/error.log

exit
```

---

## 📝 CHECKLIST

- [ ] Nuevo servidor creado con 2GB+ RAM
- [ ] SSH configurado
- [ ] Docker instalado
- [ ] Proyecto clonado
- [ ] Archivo .env copiado
- [ ] Nginx instalado y configurado
- [ ] Puertos abiertos (firewall)
- [ ] Primer deploy exitoso
- [ ] DNS actualizado
- [ ] SSL configurado (opcional)
- [ ] Staging accesible desde internet

---

## 🆘 SI ALGO FALLA

### Contenedores no inician
```bash
ssh staging
cd /home/ubuntu/paqueteria-staging
docker compose -f docker-compose.staging.yml logs
```

### Nginx da error
```bash
ssh staging
sudo nginx -t
sudo tail -50 /var/log/nginx/error.log
```

### No se puede acceder desde internet
```bash
# Verificar firewall
ssh staging "sudo ufw status"

# Verificar puertos
ssh staging "ss -tlnp | grep -E '8080|8001'"

# Verificar DNS
nslookup staging.jemavi.co
```

---

## 📞 INFORMACIÓN IMPORTANTE

**Archivos ya configurados:**
- ✅ docker-compose.staging.yml
- ✅ .deploy/config/staging.conf
- ✅ .deploy/templates/nginx-staging.conf
- ✅ Rama staging en GitHub

**Solo necesitas:**
1. Nuevo servidor con más recursos
2. Actualizar IP en configuración
3. Seguir los pasos de arriba

**Tiempo total estimado: 15-20 minutos**

---

¡Todo está listo para migrar a un servidor con más recursos!
