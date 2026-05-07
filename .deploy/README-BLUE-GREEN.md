# Blue-Green Deployment — Setup y Operación

## 📋 Visión General

**Blue-Green deployment** permite desplegar cambios sin downtime usando dos instancias de la aplicación (blue en puerto 8001, green en 8002). Nginx cambia el tráfico entre ellas mediante `nginx -s reload` (~0ms de latencia).

```
Antes (Old)     →  Blue (8001) ← ACTIVO
                →  Green (8002) ← INACTIVO

Nuevo Deploy    →  Blue (8001) ← INACTIVO
                →  Green (8002) ← ACTIVO (nuevo)
```

---

## 🔧 Setup Inicial (One-Time en el Servidor)

Estos pasos se ejecutan SOLO UNA VEZ en `/home/ubuntu/paqueteria-staging` del servidor.

### 1. Crear archivos de estado

```bash
# SSH al servidor
ssh ubuntu@staging.jemavi.co

# Cambiar a directorio del proyecto
cd /home/ubuntu/paqueteria-staging

# Crear archivo de estado (tracking active slot)
echo "blue" > active-slot

# Crear upstream inicial (apuntando a blue = puerto 8001)
cat > active-upstream.conf << 'EOF'
upstream fastapi_staging {
    server 127.0.0.1:8001 max_fails=3 fail_timeout=30s;
    keepalive 32;
}
EOF

# Ver archivos creados
cat active-slot
cat active-upstream.conf
```

### 2. Actualizar Nginx config (Host)

El archivo nginx real en el servidor está en `/etc/nginx/sites-available/staging.jemavi.co` (o similar, dependiendo de tu setup).

**Tarea:** Reemplazar el bloque `upstream fastapi_staging { ... }` con una directiva `include`.

```bash
# Hacer backup del config actual
sudo cp /etc/nginx/sites-available/staging.jemavi.co /etc/nginx/sites-available/staging.jemavi.co.bak

# Editar config
sudo nano /etc/nginx/sites-available/staging.jemavi.co
```

**En el editor:**
- Buscar la línea `upstream fastapi_staging {`
- Reemplazar el bloque completo (desde `upstream` hasta `}`) con:
```nginx
include /home/ubuntu/paqueteria-staging/active-upstream.conf;
```

**Salvar:** Ctrl+O, Enter, Ctrl+X

**Validar y reload:**
```bash
# Verificar sintaxis
sudo nginx -t
# Output esperado: nginx: configuration file test is successful

# Reload sin downtime
sudo nginx -s reload
```

### 3. Autorizar Nginx reload sin password (sudo)

El script `bg-deploy.sh` necesita ejecutar `sudo nginx -s reload` sin pedir password.

```bash
# Abrir sudoers de forma segura
sudo visudo -f /etc/sudoers.d/nginx-reload

# Pegar estas líneas al final:
ubuntu ALL=(ALL) NOPASSWD: /usr/sbin/nginx -s reload, /usr/sbin/nginx -t

# Salvar: Ctrl+O, Enter, Ctrl+X
```

**Verificar:**
```bash
sudo nginx -t  # Sin pedir password
```

### 4. Renombrar container actual → blue (si aplica)

Si ya hay un container corriendo con el nombre `paqueteria_staging_app`:

```bash
# Listar containers actuales
docker ps -a | grep paqueteria_staging

# Renombrar si existe
docker rename paqueteria_staging_app paqueteria_staging_blue 2>/dev/null || echo "No app container found"

# Crear blue profile en compose (opcional: lanzar blue manualmente después)
docker compose -f docker-compose.staging.yml --profile blue up -d app_blue
```

### 5. Verificar estado final

```bash
# Archivos de estado creados
ls -la active-*

# Containers corriendo (debe estar blue)
docker ps -f "name=paqueteria_staging"

# Nginx config validado
sudo nginx -t

# Probar salud
curl http://localhost:8001/health
# Output esperado: {"status": "healthy", ...}
```

---

## 🚀 Operación: Flujo de Deploy

### Antes: Cambios en el código

```bash
# En tu local
git checkout staging
git add .
git commit -m "feat: nueva feature"
git push origin staging
```

### Durante: GitHub Actions Automático

El workflow `.github/workflows/deploy-staging.yml` se dispara automáticamente:

1. Checkea el código (`staging` branch)
2. Valida Python syntax
3. SSH al servidor
4. `git pull` + `git reset`
5. **Llama a `bg-deploy.sh`** ← el corazón del Blue-Green

### Después: Validación Manual

```bash
# SSH al servidor
ssh ubuntu@staging.jemavi.co
cd /home/ubuntu/paqueteria-staging

# Ver slot activo actual
cat active-slot
# Output: "green" (si el último deploy fue blue → green)

# Ver container corriendo
docker ps -f "name=paqueteria_staging"
# Debe estar el slot inactivo DETENIDO (p.ej., paqueteria_staging_blue stopped)

# Probar salud
curl https://staging.jemavi.co/health
# Debe responder 200 sin errores
```

---

## 🔙 Rollback: Revertir a versión anterior

Si el deploy nuevo causa problemas, rollback es instantáneo:

```bash
# SSH al servidor
ssh ubuntu@staging.jemavi.co
cd /home/ubuntu/paqueteria-staging

# Ejecutar rollback
bash .deploy/scripts/bg-rollback.sh

# Output esperado:
# 🔙 Rollback: green → blue (puerto 8001)
# ✅ Rollback completo: green → blue
```

**¿Por qué es rápido?**
- Revert del upstream en Nginx (~0ms)
- Stop del container nuevo (que ya está stopping de todas formas)
- El contenedor antiguo ya está corriendo en el otro slot

**Pre-requisito:** El slot anterior debe estar corriendo (no muerto). El script verifica esto.

---

## 📊 Monitoreo Durante Deploy

Para ver en vivo qué sucede:

```bash
# Terminal 1: Monitoring de health check
while true; do
    echo "$(date '+%H:%M:%S'): $(curl -s https://staging.jemavi.co/health | jq -r .status)"
    sleep 1
done

# Terminal 2: Monitoreo de containers
watch -n 1 'docker ps -f "name=paqueteria_staging"'

# Terminal 3: Ver logs del container activo (Linux tail)
docker logs -f paqueteria_staging_blue  # o green, según activo
```

**Expectativa:** Health check nunca devuelve error durante el deploy completo.

---

## 🧪 Test Manual de Blue-Green

Para probar sin esperar a un push real:

```bash
# SSH al servidor
ssh ubuntu@staging.jemavi.co
cd /home/ubuntu/paqueteria-staging

# Simular deploy: build → start green, test → switch
bash .deploy/scripts/bg-deploy.sh

# Verificar cambio
cat active-slot  # Debe mostrar "green" (opuesto a antes)

# Hacer rollback
bash .deploy/scripts/bg-rollback.sh

# Verificar cambio de regreso
cat active-slot  # Debe mostrar "blue"
```

---

## ⚙️ Troubleshooting

### ❌ "Health check failed tras 30s"
- Container nuevo no está arrancando
- Revisar logs: `docker logs paqueteria_staging_green`
- Causas típicas: DB unavailable, env vars faltando, migrations errando

### ❌ "Nginx reload failed"
- Sintaxis inválida en `/home/ubuntu/paqueteria-staging/active-upstream.conf`
- Verificar: `sudo nginx -t` 
- Revisar sudoers: `sudo -u ubuntu sudo nginx -t` (debe funcionar sin password)

### ❌ Rollback falla: "Slot X no está corriendo"
- El slot anterior fue detenido o muerto inesperadamente
- Iniciar manual: `docker compose --profile green up -d app_green`
- Luego reintentar rollback

### ❌ Ambos containers detenidos
- SSH: `docker compose -f docker-compose.staging.yml --profile blue up -d app_blue`
- Luego: `echo "blue" > active-slot`
- Reintentar operación

---

## 📝 Checklist: Antes de Primer Deploy Blue-Green

- [ ] Archivos `active-slot` y `active-upstream.conf` creados
- [ ] Nginx config actualizado con `include` (no upstream hardcodeado)
- [ ] `sudo nginx -t` pasa sin errores
- [ ] Sudoers permite `nginx reload` sin password
- [ ] Container `paqueteria_staging_blue` está corriendo
- [ ] Git push de cambios code con Docker Compose + scripts

---

## 🎯 Resultados Esperados

**Antes:** Deploy causa ~2-3 min downtime (docker down → up)  
**Después:** Deploy causa ~0 min downtime (nginx reload ~0ms)

**Validación:** Durante un deploy, `curl https://staging.jemavi.co/health` NUNCA falla.

