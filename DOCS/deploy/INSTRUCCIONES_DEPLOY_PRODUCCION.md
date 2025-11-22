# 🚀 Instrucciones para Deploy en Producción

**Fecha**: 22 de noviembre de 2025  
**Versión**: 1.0

---

## ⚠️ Importante: Leer Antes de Aplicar

Los cambios en volúmenes ya están implementados en los archivos docker-compose. Esta guía te ayuda a aplicarlos en producción de forma segura.

---

## 📋 Pre-requisitos

Antes de aplicar los cambios en producción:

1. ✅ Verificar que el proyecto funciona en localhost (ya verificado)
2. ✅ Hacer backup de la base de datos
3. ✅ Hacer backup de los volúmenes actuales
4. ✅ Notificar a los usuarios de mantenimiento programado
5. ✅ Tener acceso SSH al servidor de producción

---

## 🔄 Proceso de Deploy

### Opción A: Deploy en AWS Lightsail (Recomendado)

```bash
# 1. Conectar al servidor
ssh usuario@tu-servidor-lightsail

# 2. Ir al directorio del proyecto
cd /ruta/al/proyecto

# 3. Hacer backup de volúmenes actuales
docker compose -f docker-compose.lightsail.yml exec app tar czf /tmp/backup-$(date +%Y%m%d).tar.gz /app/uploads /app/logs

# 4. Copiar backup al host
docker cp paqueteria_app:/tmp/backup-$(date +%Y%m%d).tar.gz ./backups/

# 5. Actualizar archivos desde GitHub
git pull origin main

# 6. Detener contenedores actuales
docker compose -f docker-compose.lightsail.yml down

# 7. Reconstruir y levantar con nueva configuración
docker compose -f docker-compose.lightsail.yml up -d --build

# 8. Verificar logs
docker compose -f docker-compose.lightsail.yml logs -f app

# 9. Verificar health check
curl http://localhost:8000/health
```

### Opción B: Deploy en Producción Local

```bash
# 1. Ir al directorio del proyecto
cd /ruta/al/proyecto

# 2. Hacer backup de volúmenes actuales
docker compose -f docker-compose.prod.yml exec app tar czf /tmp/backup-$(date +%Y%m%d).tar.gz /app/uploads /app/logs

# 3. Copiar backup al host
docker cp paqueteria_v1_prod_app:/tmp/backup-$(date +%Y%m%d).tar.gz ./backups/

# 4. Actualizar archivos desde GitHub
git pull origin main

# 5. Detener contenedores actuales (sin eliminar volúmenes)
docker compose -f docker-compose.prod.yml down

# 6. Reconstruir y levantar con nueva configuración
docker compose -f docker-compose.prod.yml up -d --build

# 7. Verificar logs de todos los servicios
docker compose -f docker-compose.prod.yml logs -f

# 8. Verificar health checks
curl http://localhost:8000/health
curl http://localhost:9090/-/healthy  # Prometheus
curl http://localhost:3000/api/health # Grafana
```

---

## 🧪 Verificación Post-Deploy

### 1. Verificar que los contenedores están corriendo
```bash
# Lightsail
docker compose -f docker-compose.lightsail.yml ps

# Producción
docker compose -f docker-compose.prod.yml ps
```

**Esperado**: Todos los servicios en estado "Up"

### 2. Verificar volúmenes montados
```bash
# Lightsail
docker inspect paqueteria_app | grep -A 30 "Mounts"

# Producción
docker inspect paqueteria_v1_prod_app | grep -A 30 "Mounts"
```

**Esperado**: Ver los siguientes bind mounts:
- `/CODE/src/app` → `/app/src/app:ro`
- `/CODE/src/static` → `/app/src/static`
- `/CODE/src/templates` → `/app/src/templates`

### 3. Verificar que la aplicación responde
```bash
# Health check
curl http://localhost:8000/health

# Página principal
curl -I http://localhost:8000/
```

**Esperado**: Status 200 OK

### 4. Verificar archivos estáticos
```bash
# Lightsail
docker exec paqueteria_app ls -la /app/src/static/css

# Producción
docker exec paqueteria_v1_prod_app ls -la /app/src/static/css
```

**Esperado**: Ver todos los archivos CSS

### 5. Probar edición en caliente (opcional)
```bash
# Agregar comentario a un CSS
echo "/* Test $(date) */" >> CODE/src/static/css/main.css

# Verificar dentro del contenedor
docker exec paqueteria_app tail -1 /app/src/static/css/main.css

# Limpiar
sed -i '$ d' CODE/src/static/css/main.css
```

**Esperado**: Cambio reflejado instantáneamente

---

## 🔧 Modificar Archivos en Producción

### Archivos Estáticos (CSS, JS, Imágenes, PDFs)

```bash
# 1. Editar archivo en el servidor
nano CODE/src/static/css/custom.css

# 2. Guardar cambios (Ctrl+O, Enter, Ctrl+X)

# 3. Refrescar navegador (Ctrl+F5)
# ✅ Cambios visibles inmediatamente
```

**No requiere**: rebuild, restart, ni downtime

### Templates HTML

```bash
# 1. Editar template
nano CODE/src/templates/dashboard/index.html

# 2. Guardar cambios

# 3. Refrescar navegador
# ✅ Cambios visibles inmediatamente
```

**No requiere**: rebuild, restart, ni downtime

### Código Python

```bash
# 1. Editar archivo Python
nano CODE/src/app/routes/dashboard.py

# 2. Guardar cambios

# 3. Reiniciar solo el contenedor de la app
docker compose -f docker-compose.prod.yml restart app

# 4. Verificar logs
docker compose -f docker-compose.prod.yml logs -f app
```

**Requiere**: restart (sin rebuild), ~10 segundos de downtime

---

## 🔄 Rollback en Caso de Problemas

Si algo sale mal, puedes volver a la versión anterior:

```bash
# 1. Detener contenedores
docker compose -f docker-compose.prod.yml down

# 2. Volver a la versión anterior en Git
git checkout HEAD~1

# 3. Levantar contenedores con versión anterior
docker compose -f docker-compose.prod.yml up -d

# 4. Verificar que funciona
curl http://localhost:8000/health
```

---

## 📊 Monitoreo Post-Deploy

### Logs en Tiempo Real
```bash
# Ver logs de la app
docker compose -f docker-compose.prod.yml logs -f app

# Ver logs de todos los servicios
docker compose -f docker-compose.prod.yml logs -f

# Ver últimas 100 líneas
docker compose -f docker-compose.prod.yml logs --tail 100 app
```

### Métricas (Solo Producción)
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000
- **Node Exporter**: http://localhost:9100/metrics

### Health Checks
```bash
# App
curl http://localhost:8000/health

# Redis
docker compose -f docker-compose.prod.yml exec redis redis-cli -a $REDIS_PASSWORD ping

# Prometheus
curl http://localhost:9090/-/healthy

# Grafana
curl http://localhost:3000/api/health
```

---

## ⚠️ Troubleshooting

### Problema: Contenedor no inicia

**Solución**:
```bash
# Ver logs detallados
docker compose -f docker-compose.prod.yml logs app

# Verificar que los archivos existen
ls -la CODE/src/static
ls -la CODE/src/templates

# Verificar permisos
chmod -R 755 CODE/src/static
chmod -R 755 CODE/src/templates
```

### Problema: Archivos estáticos no se ven

**Solución**:
```bash
# Verificar que el volumen está montado
docker inspect paqueteria_v1_prod_app | grep static

# Verificar archivos dentro del contenedor
docker exec paqueteria_v1_prod_app ls -la /app/src/static

# Limpiar caché del navegador (Ctrl+Shift+R)
```

### Problema: Cambios en CSS no se reflejan

**Solución**:
```bash
# 1. Verificar que el archivo se modificó en el host
cat CODE/src/static/css/main.css | tail -5

# 2. Verificar que el cambio está en el contenedor
docker exec paqueteria_v1_prod_app cat /app/src/static/css/main.css | tail -5

# 3. Limpiar caché del navegador (Ctrl+Shift+R)

# 4. Si no funciona, verificar volumen
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d
```

### Problema: Base de datos no conecta

**Solución**:
```bash
# Verificar variables de entorno
docker compose -f docker-compose.prod.yml exec app env | grep DATABASE

# Verificar conectividad
docker compose -f docker-compose.prod.yml exec app ping -c 3 ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com

# Ver logs de conexión
docker compose -f docker-compose.prod.yml logs app | grep -i database
```

---

## 📝 Checklist de Deploy

Antes de dar por completado el deploy, verifica:

- [ ] Todos los contenedores están en estado "Up"
- [ ] Health check responde correctamente
- [ ] Página principal carga correctamente
- [ ] Archivos estáticos (CSS, JS, imágenes) cargan
- [ ] Login funciona
- [ ] Dashboard carga correctamente
- [ ] Base de datos conecta correctamente
- [ ] Redis funciona (verificar caché)
- [ ] Logs no muestran errores críticos
- [ ] Prometheus recolecta métricas (solo prod)
- [ ] Grafana muestra dashboards (solo prod)
- [ ] Volúmenes están montados correctamente
- [ ] Backups están en su lugar

---

## 🎯 Ventajas de la Nueva Configuración

### En Desarrollo
- ✅ Hot reload de código Python
- ✅ Cambios instantáneos en CSS/JS/HTML
- ✅ No requiere rebuild para cambios de diseño

### En Producción
- ✅ Código Python protegido (read-only)
- ✅ Actualizaciones rápidas de diseño sin downtime
- ✅ Datos persistentes fuera del contenedor
- ✅ Backups más fáciles de gestionar

---

## 📞 Soporte

Si encuentras problemas durante el deploy:

1. Revisa los logs: `docker compose logs -f app`
2. Verifica el estado: `docker compose ps`
3. Consulta esta guía de troubleshooting
4. Revisa `GUIA_VOLUMENES_DOCKER.md` para más detalles

---

**Última actualización**: 22 de noviembre de 2025  
**Versión**: 1.0  
**Autor**: Kiro AI
