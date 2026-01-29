# ✅ Checklist - Instalación Botón de Sincronización

**Fecha:** 27 de enero de 2026  
**Servidor:** Staging  
**Tiempo estimado:** 5 minutos

---

## 📋 Pre-requisitos

- [ ] Acceso SSH al servidor staging
- [ ] Usuario con permisos sudo
- [ ] Docker instalado y corriendo
- [ ] Archivos descargados en tu máquina local:
  - [ ] `sync_staging_monitor.sh`
  - [ ] `staging-sync-monitor.service`
  - [ ] `setup_sync_monitor.sh`

---

## 🚀 Instalación

### Paso 1: Subir Archivos

- [ ] Abrir terminal en tu máquina local
- [ ] Navegar al directorio con los archivos
- [ ] Ejecutar:
  ```bash
  scp sync_staging_monitor.sh staging:~/
  scp staging-sync-monitor.service staging:~/
  scp setup_sync_monitor.sh staging:~/
  ```
- [ ] Verificar que no hubo errores

### Paso 2: Conectar al Servidor

- [ ] Ejecutar: `ssh staging`
- [ ] Verificar que estás en el servidor correcto
- [ ] Ejecutar: `hostname` (debe mostrar el hostname de staging)

### Paso 3: Ejecutar Instalación

- [ ] Dar permisos de ejecución:
  ```bash
  chmod +x setup_sync_monitor.sh
  ```
- [ ] Ejecutar instalación:
  ```bash
  ./setup_sync_monitor.sh
  ```
- [ ] Verificar que no hubo errores
- [ ] Ver mensaje: "✅ Configuración completada!"

### Paso 4: Verificar Servicio

- [ ] Ejecutar:
  ```bash
  sudo systemctl status staging-sync-monitor
  ```
- [ ] Verificar que muestra: `Active: active (running)`
- [ ] Verificar que no hay errores en rojo

### Paso 5: Ver Logs

- [ ] Ejecutar:
  ```bash
  sudo journalctl -u staging-sync-monitor -f
  ```
- [ ] Verificar que muestra:
  ```
  🔍 Monitor de sincronización iniciado...
  📁 Esperando señal en: /tmp/staging_sync_request
  ```
- [ ] Presionar Ctrl+C para salir

---

## 🧪 Pruebas

### Prueba 1: Verificar Botón en Navegador

- [ ] Abrir staging en el navegador
- [ ] Verificar que aparece el badge "🟡 Staging"
- [ ] Verificar que aparece el botón "🔄 Sincronizar"
- [ ] Verificar que el botón está habilitado (no gris)

### Prueba 2: Probar Sincronización

- [ ] Click en el botón "🔄 Sincronizar"
- [ ] Verificar que aparece confirmación
- [ ] Click en "Aceptar"
- [ ] Verificar que el botón cambia a "Sincronizando..."
- [ ] Verificar que el icono gira
- [ ] Verificar que muestra progreso (0% → 100%)
- [ ] Esperar a que complete (1-3 minutos)
- [ ] Verificar que aparece: "✅ Sincronización completada"
- [ ] Verificar que la página se recarga automáticamente
- [ ] Verificar que el botón vuelve a "🔄 Sincronizar"

### Prueba 3: Verificar Logs del Servidor

- [ ] En el servidor, ejecutar:
  ```bash
  sudo journalctl -u staging-sync-monitor -n 50
  ```
- [ ] Verificar que muestra:
  ```
  🔔 Señal de sincronización detectada!
  🔄 Iniciando sincronización...
  📦 Exportando producción...
  ✅ Exportado
  📥 Restaurando en staging...
  ✅ Restaurado
  ✅ Sincronización completada exitosamente
  ```

---

## 🔍 Verificación Post-Instalación

### Archivos Creados

- [ ] Verificar en el servidor:
  ```bash
  ls -la ~/sync_staging_monitor.sh
  ls -la /etc/systemd/system/staging-sync-monitor.service
  ```
- [ ] Ambos archivos deben existir

### Servicio Habilitado

- [ ] Verificar:
  ```bash
  sudo systemctl is-enabled staging-sync-monitor
  ```
- [ ] Debe mostrar: `enabled`

### Servicio Activo

- [ ] Verificar:
  ```bash
  sudo systemctl is-active staging-sync-monitor
  ```
- [ ] Debe mostrar: `active`

---

## 🐛 Troubleshooting

### Si el servicio no inicia

- [ ] Ver logs de error:
  ```bash
  sudo journalctl -u staging-sync-monitor -n 50
  ```
- [ ] Verificar permisos:
  ```bash
  chmod +x ~/sync_staging_monitor.sh
  ```
- [ ] Reintentar:
  ```bash
  sudo systemctl restart staging-sync-monitor
  ```

### Si el botón no aparece

- [ ] Verificar que estás en staging (no producción)
- [ ] Refrescar con Ctrl+Shift+R
- [ ] Abrir consola del navegador (F12)
- [ ] Buscar errores en la consola

### Si la sincronización falla

- [ ] Ver logs del monitor:
  ```bash
  sudo journalctl -u staging-sync-monitor -n 100
  ```
- [ ] Verificar conectividad a RDS:
  ```bash
  docker run --rm postgres:17-alpine \
    psql -h ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com \
    -U jveyes -d paqueteria_v4 -c "SELECT 1;"
  ```
- [ ] Limpiar archivos temporales:
  ```bash
  rm -f /tmp/staging_sync_*
  ```
- [ ] Reintentar desde el navegador

---

## 📝 Comandos de Mantenimiento

### Ver Estado

```bash
sudo systemctl status staging-sync-monitor
```

### Ver Logs en Tiempo Real

```bash
sudo journalctl -u staging-sync-monitor -f
```

### Ver Últimos Logs

```bash
sudo journalctl -u staging-sync-monitor -n 100
```

### Reiniciar Servicio

```bash
sudo systemctl restart staging-sync-monitor
```

### Detener Servicio

```bash
sudo systemctl stop staging-sync-monitor
```

### Iniciar Servicio

```bash
sudo systemctl start staging-sync-monitor
```

### Deshabilitar Auto-Start

```bash
sudo systemctl disable staging-sync-monitor
```

### Habilitar Auto-Start

```bash
sudo systemctl enable staging-sync-monitor
```

---

## ✅ Confirmación Final

- [ ] Servicio instalado y corriendo
- [ ] Botón visible en el navegador
- [ ] Sincronización probada y funcionando
- [ ] Logs verificados sin errores
- [ ] Documentación revisada

---

## 📚 Documentación de Referencia

- [ ] `QUICK_INSTALL_SYNC_BUTTON.md` - Guía rápida
- [ ] `SOLUCION_BOTON_SINCRONIZACION.md` - Documentación completa
- [ ] `DIAGRAMA_FLUJO_SINCRONIZACION.md` - Diagrama visual
- [ ] `RESUMEN_SOLUCION_SYNC_BUTTON.md` - Resumen ejecutivo

---

## 🎉 Instalación Completada

Si todos los checkboxes están marcados, la instalación está completa y el botón de sincronización está funcionando correctamente.

**Fecha de instalación:** _______________  
**Instalado por:** _______________  
**Verificado por:** _______________

---

**Creado por:** Kiro AI  
**Fecha:** 27 de enero de 2026  
**Versión:** 1.0
