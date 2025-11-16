# Dependencias de Scripts de Despliegue

## 📋 Archivos que permanecen en la raíz

### `deploy-to-aws.sh`
**Ubicación:** Raíz del proyecto

**Dependencias:**
- `docker-compose.prod.yml` (raíz) - Usado para verificar estado de contenedores
- `docker-compose.lightsail.yml` (raíz) - Usado para verificar estado de contenedores
- `CODE/scripts/deployment/pull-update.sh` - Ejecutado en el servidor remoto vía SSH
- `.git/` - Repositorio Git (verifica que esté en un repo)

**Funcionalidad:**
1. Hace commit y push a GitHub desde localhost
2. Conecta vía SSH al servidor AWS
3. Ejecuta `pull-update.sh` en el servidor para actualizar el código

---

### `deploy-lightsail.sh`
**Ubicación:** Raíz del proyecto

**Dependencias:**
- `docker-compose.lightsail.yml` (raíz) - Archivo de configuración Docker Compose
- `CODE/.env` - Variables de entorno (verifica que exista)
- `CODE/Dockerfile.lightsail` - Dockerfile optimizado para Lightsail
- `CODE/optimize_database.sql` - Script de optimización de BD (opcional)

**Funcionalidad:**
1. Verifica requisitos (Docker, Docker Compose)
2. Verifica archivo `.env`
3. Limpia logs antiguos
4. Detiene contenedores anteriores
5. Construye imagen Docker optimizada
6. Inicia servicios con `docker-compose.lightsail.yml`
7. Verifica que los servicios estén listos
8. Opcionalmente ejecuta migraciones y optimizaciones

---

## 📁 Archivos movidos a `CODE/scripts/deployment/`

Los siguientes archivos fueron movidos desde la raíz a `CODE/scripts/deployment/`:

1. `deploy-to-papyrus.sh`
2. `deploy-safe.sh` (depende de `sync-configs.sh`)
3. `deploy-static-fix-to-server.sh`
4. `redeploy-with-static-fix.sh`
5. `sync-configs.sh` (usado por `deploy-safe.sh`)
6. `fix-port-conflict.sh`
7. `fix-static-files.sh`
8. `fix-static-alternative.sh`
9. `apply-fix-now.sh`
10. `start.sh`
11. `monitor.sh`
12. `limpiar-servidor.sh`
13. `diagnose-server-deep.sh`
14. `diagnose-static-files.sh`
15. `test-static-access.sh`
16. `menu-correccion-imagenes.sh`

---

## 🔗 Referencias actualizadas

Las siguientes referencias fueron actualizadas en los scripts movidos:

### `deploy-safe.sh`
- Actualizado: `./sync-configs.sh` → `./CODE/scripts/deployment/sync-configs.sh`

### `menu-correccion-imagenes.sh`
- Actualizado: `diagnose-static-files.sh` → `CODE/scripts/deployment/diagnose-static-files.sh`
- Actualizado: `redeploy-with-static-fix.sh` → `CODE/scripts/deployment/redeploy-with-static-fix.sh`
- Actualizado: `deploy-static-fix-to-server.sh` → `CODE/scripts/deployment/deploy-static-fix-to-server.sh`

### `apply-fix-now.sh`
- Actualizado: `./deploy-static-fix-to-server.sh` → `./CODE/scripts/deployment/deploy-static-fix-to-server.sh`

### `deploy-static-fix-to-server.sh`
- Actualizado: Referencias a `redeploy-with-static-fix.sh` y `diagnose-static-files.sh` para usar rutas completas

### `limpiar-servidor.sh`
- Actualizado: Lista de archivos válidos en la raíz (removidos `monitor.sh` y `start.sh`)

### `git-add-server-files.sh`
- Actualizado: Referencia a `monitor.sh` → `CODE/scripts/deployment/monitor.sh`

---

## ⚠️ Notas importantes

1. **Ejecución desde la raíz:** Todos los scripts deben ejecutarse desde la raíz del proyecto para que las rutas relativas funcionen correctamente.

2. **Dependencias de docker-compose:** Los archivos `docker-compose.prod.yml` y `docker-compose.lightsail.yml` deben permanecer en la raíz del proyecto.

3. **Scripts en el servidor:** Cuando los scripts se copian al servidor, deben mantener la misma estructura de directorios para que las referencias funcionen.

4. **sync-configs.sh:** Este script verifica que los archivos `docker-compose.prod.yml` y `docker-compose.lightsail.yml` estén en la raíz del proyecto.

