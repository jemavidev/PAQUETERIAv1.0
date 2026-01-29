# 🔧 Fix: Error "docker: command not found"

**Fecha:** 27 de enero de 2026  
**Error:** El servicio no puede ejecutar Docker  
**Solución:** Agregar usuario al grupo docker

---

## 🎯 Problema

El monitor de sincronización falla con:
```
docker: command not found
```

O:
```
permission denied while trying to connect to the Docker daemon socket
```

---

## ✅ Solución Rápida (3 pasos)

### 1️⃣ Agregar usuario al grupo docker

```bash
ssh staging
sudo usermod -aG docker $USER
```

### 2️⃣ Cerrar sesión y reconectar

```bash
exit
ssh staging
```

### 3️⃣ Verificar y reiniciar servicio

```bash
# Verificar que ahora estás en el grupo docker
groups

# Debe mostrar: rocky ... docker

# Reiniciar el servicio
sudo systemctl restart staging-sync-monitor

# Ver logs
sudo journalctl -u staging-sync-monitor -f
```

---

## 🔍 Diagnóstico

Ejecuta el script de diagnóstico:

```bash
chmod +x diagnostico_sync.sh
./diagnostico_sync.sh
```

Esto te mostrará:
- ✅ Si Docker está instalado
- ✅ Si tienes permisos para usar Docker
- ✅ Estado del servicio
- ✅ Logs recientes

---

## 🛠️ Soluciones Alternativas

### Opción A: Usar simple_sync.sh (sin Docker)

Si Docker no está disponible, el monitor automáticamente usará `simple_sync.sh`:

```bash
# Verificar que existe
ls -la ~/simple_sync.sh

# Si no existe, crearlo
cat > ~/simple_sync.sh << 'EOF'
#!/bin/bash
set -e

HOST="ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com"
USER="jveyes"
PASS='a?HC!2.*1#?[==:|289qAI=)#V4kDzl$'

export PGPASSWORD="$PASS"

echo "🔄 Sincronizando producción → staging..."
pg_dump -h "$HOST" -U "$USER" -d paqueteria_v4 -F c -f /tmp/backup.dump --no-owner --no-acl
pg_restore -h "$HOST" -U "$USER" -d paqueteria_staging /tmp/backup.dump --clean --if-exists --no-owner --no-acl 2>&1 | grep -v "^WARNING" || true
echo "✅ Sincronización completada"
EOF

chmod +x ~/simple_sync.sh
```

Luego reinicia el servicio:
```bash
sudo systemctl restart staging-sync-monitor
```

### Opción B: Ejecutar como root (no recomendado)

Editar el servicio:
```bash
sudo nano /etc/systemd/system/staging-sync-monitor.service
```

Cambiar:
```ini
User=rocky
```

Por:
```ini
User=root
```

Recargar y reiniciar:
```bash
sudo systemctl daemon-reload
sudo systemctl restart staging-sync-monitor
```

---

## 📋 Verificación

### 1. Verificar permisos de Docker

```bash
# Debe funcionar sin sudo
docker ps

# Si funciona, estás listo ✅
```

### 2. Verificar servicio

```bash
sudo systemctl status staging-sync-monitor
```

Debe mostrar: `Active: active (running)`

### 3. Ver logs en tiempo real

```bash
sudo journalctl -u staging-sync-monitor -f
```

Debe mostrar:
```
🔍 Monitor de sincronización iniciado...
🐳 Docker encontrado en: /usr/bin/docker
📁 Esperando señal en: /tmp/staging_sync_request
```

### 4. Probar desde navegador

1. Abrir staging
2. Click en "🔄 Sincronizar"
3. Confirmar
4. Esperar

---

## 🐛 Troubleshooting

### Error: "Cannot connect to Docker daemon"

**Causa:** Usuario no tiene permisos

**Solución:**
```bash
sudo usermod -aG docker $USER
exit
ssh staging
sudo systemctl restart staging-sync-monitor
```

### Error: "docker: command not found"

**Causa:** Docker no está en el PATH del servicio

**Solución:** El script ahora detecta automáticamente la ubicación de Docker. Si persiste:

```bash
# Encontrar Docker
which docker

# Editar el script y agregar la ruta completa
nano ~/sync_staging_monitor.sh

# Cambiar "docker" por la ruta completa, ejemplo:
# /usr/bin/docker run --rm ...
```

### El servicio usa simple_sync.sh pero falla

**Causa:** PostgreSQL client tools no instaladas

**Solución:**
```bash
# Instalar PostgreSQL client
sudo dnf install postgresql -y

# O usar Docker (recomendado)
sudo usermod -aG docker $USER
exit
ssh staging
```

---

## 📝 Resumen de Comandos

```bash
# 1. Agregar usuario a grupo docker
sudo usermod -aG docker $USER

# 2. Reconectar
exit
ssh staging

# 3. Verificar grupos
groups

# 4. Ejecutar diagnóstico
./diagnostico_sync.sh

# 5. Reinstalar si es necesario
./setup_sync_monitor.sh

# 6. Ver logs
sudo journalctl -u staging-sync-monitor -f

# 7. Probar desde navegador
# Click en botón "🔄 Sincronizar"
```

---

## ✅ Checklist

- [ ] Usuario agregado al grupo docker
- [ ] Sesión cerrada y reconectada
- [ ] `groups` muestra "docker"
- [ ] `docker ps` funciona sin sudo
- [ ] Servicio reiniciado
- [ ] Logs muestran "Docker encontrado"
- [ ] Botón probado desde navegador
- [ ] Sincronización completada exitosamente

---

**Actualizado:** 27 de enero de 2026  
**Estado:** ✅ SOLUCIONADO
