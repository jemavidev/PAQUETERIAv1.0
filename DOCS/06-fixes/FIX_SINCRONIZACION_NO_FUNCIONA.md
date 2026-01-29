# 🔧 Fix: Sincronización No Funciona

**Fecha:** 27 de enero de 2026  
**Problema:** El botón no sincroniza (sin errores)  
**Causa:** `/tmp` del contenedor y `/tmp` del host son diferentes

---

## 🎯 Problema

El contenedor escribe en `/tmp/staging_sync_request` **dentro del contenedor**.  
El monitor lee `/tmp/staging_sync_request` **en el host**.  
Son sistemas de archivos diferentes, por eso no se comunican.

---

## ✅ Solución

Montar `/tmp` del host en el contenedor para que compartan el mismo directorio.

---

## 🚀 Aplicar Fix (3 pasos)

### Opción A: Automática (Recomendada)

```bash
# 1. Subir archivos actualizados
scp docker-compose.staging.yml staging:~/paqueteria-staging/
scp fix_sync_volumes.sh staging:~/

# 2. Conectar y ejecutar
ssh staging
cd ~
chmod +x fix_sync_volumes.sh
./fix_sync_volumes.sh

# 3. Verificar
./debug_sync.sh
```

### Opción B: Manual

```bash
# 1. Conectar al servidor
ssh staging
cd ~/paqueteria-staging

# 2. Editar docker-compose.staging.yml
nano docker-compose.staging.yml

# 3. Agregar en la sección volumes del servicio app:
#    Después de la línea "- logs_staging_data:/app/logs"
#    Agregar:
      # Compartir /tmp para sincronización (archivos señal)
      - /tmp:/tmp

# 4. Guardar (Ctrl+O, Enter, Ctrl+X)

# 5. Reiniciar contenedor
docker compose -f docker-compose.staging.yml down app
docker compose -f docker-compose.staging.yml up -d app

# 6. Verificar
docker ps | grep staging_app
```

---

## 🔍 Verificación

### 1. Verificar que el volumen está montado

```bash
# Ver configuración del contenedor
docker inspect paqueteria_staging_app | grep -A 5 "Mounts"
```

Debe mostrar algo como:
```json
"Mounts": [
    {
        "Type": "bind",
        "Source": "/tmp",
        "Destination": "/tmp",
        ...
    }
]
```

### 2. Probar comunicación entre host y contenedor

```bash
# En el host, crear archivo
echo "test" > /tmp/test_sync

# Verificar que el contenedor lo ve
docker exec paqueteria_staging_app ls /tmp/test_sync

# Debe mostrar: /tmp/test_sync

# Limpiar
rm /tmp/test_sync
```

### 3. Probar sincronización

```bash
# Ver logs del monitor
sudo journalctl -u staging-sync-monitor -f

# En el navegador:
# 1. Abrir staging
# 2. Click en "🔄 Sincronizar"
# 3. Observar logs en la terminal

# Deberías ver:
# 🔔 Señal de sincronización detectada!
# 🔄 Iniciando sincronización...
```

---

## 📊 Antes vs Después

### ❌ Antes (No funciona)

```
CONTENEDOR                    HOST
/tmp/staging_sync_request  ≠  /tmp/staging_sync_request
(archivo A)                   (archivo B - diferente)

App escribe en A → Monitor lee B → No se comunican
```

### ✅ Después (Funciona)

```
CONTENEDOR                    HOST
/tmp/staging_sync_request  =  /tmp/staging_sync_request
(mismo archivo compartido)

App escribe → Monitor lee → ✅ Funciona
```

---

## 🐛 Troubleshooting

### El contenedor no inicia después del cambio

```bash
# Ver logs del contenedor
docker logs paqueteria_staging_app

# Ver si hay error de permisos
ls -lad /tmp

# Reintentar
docker compose -f docker-compose.staging.yml restart app
```

### El volumen no se monta

```bash
# Verificar sintaxis del docker-compose.yml
docker compose -f docker-compose.staging.yml config

# Si hay error, corregir y reintentar
nano docker-compose.staging.yml
```

### Aún no sincroniza

```bash
# Ejecutar debug completo
./debug_sync.sh

# Ver logs del monitor
sudo journalctl -u staging-sync-monitor -f

# Crear señal manualmente
echo "test" > /tmp/staging_sync_request

# Ver si el monitor la detecta (en los logs)
```

---

## 📝 Cambios en docker-compose.staging.yml

```yaml
# ANTES:
volumes:
  - ./CODE/src/app:/app/src/app:ro
  - ./CODE/src/templates:/app/src/templates
  - uploads_staging_data:/app/uploads
  - logs_staging_data:/app/logs

# DESPUÉS:
volumes:
  - ./CODE/src/app:/app/src/app:ro
  - ./CODE/src/templates:/app/src/templates
  - uploads_staging_data:/app/uploads
  - logs_staging_data:/app/logs
  # Compartir /tmp para sincronización (archivos señal)
  - /tmp:/tmp
```

---

## ✅ Checklist

- [ ] Archivo docker-compose.staging.yml actualizado
- [ ] Volumen `/tmp:/tmp` agregado
- [ ] Contenedor reiniciado
- [ ] Contenedor corriendo (`docker ps`)
- [ ] Volumen montado (verificado con `docker inspect`)
- [ ] Comunicación host-contenedor funciona (test con archivo)
- [ ] Monitor detecta señal (logs)
- [ ] Sincronización funciona desde navegador

---

## 🎉 Resultado

Después de aplicar este fix:

✅ El contenedor y el host comparten `/tmp`  
✅ Los archivos señal se comunican correctamente  
✅ El monitor detecta cuando el usuario hace click  
✅ La sincronización se ejecuta  
✅ El usuario recibe notificación de éxito  

---

## 📚 Archivos Relacionados

- `docker-compose.staging.yml` - Configuración actualizada
- `fix_sync_volumes.sh` - Script automático
- `debug_sync.sh` - Diagnóstico
- `COMANDOS_DEBUG.txt` - Comandos de debug

---

**Actualizado:** 27 de enero de 2026  
**Estado:** ✅ SOLUCIONADO
