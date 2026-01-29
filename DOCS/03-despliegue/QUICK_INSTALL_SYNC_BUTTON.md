# ⚡ Instalación Rápida - Botón de Sincronización

**Tiempo:** 2 minutos  
**Dificultad:** Fácil

---

## 🚀 Instalación en 4 Pasos

### 1️⃣ Subir archivos al servidor

```bash
scp sync_staging_monitor.sh staging:~/
scp staging-sync-monitor.service staging:~/
scp setup_sync_monitor.sh staging:~/
scp diagnostico_sync.sh staging:~/
```

### 2️⃣ Conectar y agregar permisos Docker

```bash
ssh staging
sudo usermod -aG docker $USER
exit
ssh staging
```

### 3️⃣ Ejecutar instalación

```bash
chmod +x setup_sync_monitor.sh
./setup_sync_monitor.sh
```

### 4️⃣ Verificar

```bash
sudo systemctl status staging-sync-monitor
```

Deberías ver: `Active: active (running)`

---

## ✅ Probar

1. Abrir staging en el navegador
2. Ver botón "🔄 Sincronizar" en el header
3. Click → Confirmar → Esperar
4. ✅ Listo!

---

## 🐛 Si hay error "docker: command not found"

```bash
# Agregar usuario al grupo docker
sudo usermod -aG docker $USER

# Cerrar y reconectar
exit
ssh staging

# Verificar
groups  # Debe mostrar "docker"

# Reiniciar servicio
sudo systemctl restart staging-sync-monitor
```

Ver guía completa: `FIX_ERROR_DOCKER.md`

---

## 📝 Comandos Útiles

```bash
# Ver logs en tiempo real
sudo journalctl -u staging-sync-monitor -f

# Diagnóstico completo
./diagnostico_sync.sh

# Reiniciar servicio
sudo systemctl restart staging-sync-monitor

# Ver estado
sudo systemctl status staging-sync-monitor
```

---

## 🐛 Si algo falla

```bash
# Ejecutar diagnóstico
./diagnostico_sync.sh

# Limpiar y reintentar
rm -f /tmp/staging_sync_*
sudo systemctl restart staging-sync-monitor
```

---

## 📚 Documentación Completa

- **Fix Docker:** `FIX_ERROR_DOCKER.md`
- **Documentación:** `SOLUCION_BOTON_SINCRONIZACION.md`
- **Diagnóstico:** `diagnostico_sync.sh`

---

**¡Eso es todo!** 🎉
