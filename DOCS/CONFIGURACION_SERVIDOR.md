# 🖥️ Configuración del Servidor AWS - PAQUETERÍA v1.0

## 📊 Análisis del Servidor Actual

### Información del Servidor
```
Hostname: paquetex.papyrus.com.co
Usuario: ubuntu
Sistema: Ubuntu 24.04.3 LTS (Noble Numbat)
Kernel: 6.14.0-1016-aws
Arquitectura: x86_64
```

### Recursos del Servidor
```
RAM: 914 MB (634 MB usados, 279 MB disponibles)
Swap: 2.0 GB (696 MB usados, 1.3 GB disponibles)
Disco: 38 GB (8.3 GB usados, 30 GB disponibles - 22% uso)
```

### Software Instalado
```
Docker: 29.0.1
Docker Compose: v2.40.3
Nginx: Activo y funcionando
Git: Configurado
```

---

## ✅ Estado Actual del Proyecto

### Ubicación del Proyecto
```
Ruta: /home/ubuntu/paqueteria
Repositorio: https://github.com/jemavidev/PAQUETERIAv1.0.git
Rama: main
Estado: Sincronizado con origin/main
```

### Contenedores en Ejecución
```
✅ paqueteria_v1_prod_app          - Up 9 hours (healthy) - Puerto 8000
✅ paqueteria_v1_prod_redis        - Up 9 hours (healthy)
✅ paqueteria_v1_prod_celery       - Up 9 hours (healthy)
✅ paqueteria_v1_prod_celery_beat  - Up 9 hours
✅ paqueteria_v1_prod_prometheus   - Up 9 hours (healthy) - Puerto 9090
✅ paqueteria_v1_prod_grafana      - Up 9 hours (healthy) - Puerto 3000
✅ paqueteria_v1_prod_node_exporter- Up 9 hours (healthy) - Puerto 9100
```

### Health Check
```json
{
  "status": "healthy",
  "timestamp": "2025-11-16T12:05:42.077823",
  "version": "4.0.0",
  "environment": "production"
}
```

### Nginx
```
Estado: Activo (running)
Uptime: 9 horas
Workers: 2 procesos
```

---

## 🔧 Configuración Actual

### Variables de Entorno (.env)
```bash
# Ambiente
ENVIRONMENT=production
DEBUG=False

# Base de datos (AWS RDS)
DATABASE_URL=postgresql://jveyes:***@ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com:5432/paqueteria_v4

# AWS S3
AWS_ACCESS_KEY_ID=AKIASQJ3NGZ3AT4KNLJ4
AWS_SECRET_ACCESS_KEY=***
AWS_S3_BUCKET=elclub-paqueteria
AWS_REGION=us-east-1
```

### Docker Compose
```
Archivo activo: docker-compose.prod.yml
Stack: PAQUETERIA v1.0 PROD
```

---

## 🚀 Configuración del Despliegue Automatizado

### Script deploy-to-aws.sh Configurado
```bash
AWS_HOST="papyrus"  # Alias SSH ya configurado
AWS_PROJECT_PATH="/home/ubuntu/paqueteria"
GIT_BRANCH="main"
```

### Flujo de Despliegue
```
Localhost → GitHub → Servidor AWS
    ↓          ↓           ↓
  Commit    Push        Pull
```

---

## 📝 Scripts Disponibles en el Servidor

### Scripts en /home/ubuntu/paqueteria/
```bash
✅ deploy-lightsail.sh      - Despliegue completo Lightsail
✅ deploy.sh                - Despliegue desde GitHub
✅ pull-update.sh           - Actualización inteligente
✅ pull-only.sh             - Solo pull sin rebuild
✅ update.sh                - Actualización rápida
✅ monitor.sh               - Monitoreo del sistema
✅ start.sh                 - Inicio del sistema
✅ setup-production.sh      - Configuración de producción
```

---

## 🎯 Comandos Útiles para el Servidor

### Conexión SSH
```bash
# Desde localhost
ssh papyrus

# O con ruta completa
ssh ubuntu@paquetex.papyrus.com.co
```

### Gestión de Contenedores
```bash
# Ver estado
cd /home/ubuntu/paqueteria
docker compose ps

# Ver logs
docker compose logs -f app

# Reiniciar aplicación
docker compose restart app

# Ver uso de recursos
docker stats
```

### Actualización del Código
```bash
# Método 1: Actualización inteligente (recomendado)
cd /home/ubuntu/paqueteria
./pull-update.sh

# Método 2: Solo pull
./pull-only.sh

# Método 3: Despliegue completo
./deploy.sh main
```

### Monitoreo
```bash
# Health check
curl http://localhost:8000/health

# Ver logs de Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Uso de recursos
free -h
df -h
docker stats --no-stream
```

---

## 🔍 Verificación del Sistema

### Checklist de Verificación
- ✅ Docker y Docker Compose instalados
- ✅ Nginx activo y funcionando
- ✅ Proyecto clonado en /home/ubuntu/paqueteria
- ✅ Git configurado con repositorio remoto
- ✅ .env configurado con valores de producción
- ✅ Contenedores ejecutándose correctamente
- ✅ Health check respondiendo
- ✅ Scripts de despliegue disponibles
- ✅ SSH configurado (alias "papyrus")

### Puntos de Atención
⚠️ **RAM limitada:** 914 MB total (usar swap activamente)
⚠️ **Archivos sin rastrear:** Hay scripts locales en el servidor que no están en Git
✅ **Espacio en disco:** 30 GB disponibles (suficiente)
✅ **Todos los servicios healthy:** Sistema estable

---

## 🎯 Recomendaciones

### Inmediatas
1. ✅ **Configuración completada:** El servidor está listo para despliegue automatizado
2. ✅ **SSH configurado:** Alias "papyrus" funciona correctamente
3. ✅ **Proyecto sincronizado:** Git configurado con el repositorio correcto

### Corto Plazo
1. **Limpiar archivos sin rastrear:** Los scripts locales en el servidor pueden causar conflictos
2. **Monitorear RAM:** Con 914 MB, el sistema usa swap frecuentemente
3. **Configurar alertas:** Para monitorear uso de recursos

### Mediano Plazo
1. **Considerar upgrade de RAM:** Para mejor rendimiento
2. **Implementar backups automáticos:** De base de datos y archivos
3. **Configurar logs rotation:** Para evitar llenar el disco

---

## 🚀 Uso del Despliegue Automatizado

### Desde tu Localhost

```bash
# 1. Hacer cambios en el código
vim CODE/src/app/routes/packages.py

# 2. Desplegar con un solo comando
./deploy-to-aws.sh "fix: corregir validación de paquetes"

# El script hará automáticamente:
# - Commit de cambios
# - Push a GitHub
# - Conexión SSH al servidor
# - Pull en el servidor
# - Análisis de cambios
# - Aplicación de actualizaciones
# - Verificación post-despliegue
```

### Resultado Esperado
```
========================================
🚀 DESPLIEGUE AUTOMATIZADO A AWS
========================================

✅ Configuración verificada
✅ Commit realizado
✅ Cambios subidos a GitHub
✅ Conexión SSH verificada
✅ Actualización en AWS completada
✅ Health check exitoso

========================================
✅ DESPLIEGUE COMPLETADO
========================================
```

---

## 📊 Monitoreo del Servidor

### URLs de Monitoreo
```
Aplicación: http://paquetex.papyrus.com.co
Health Check: http://paquetex.papyrus.com.co/health
Prometheus: http://paquetex.papyrus.com.co:9090 (interno)
Grafana: http://paquetex.papyrus.com.co:3000 (interno)
```

### Comandos de Monitoreo
```bash
# Ver estado general
ssh papyrus "cd /home/ubuntu/paqueteria && docker compose ps"

# Ver logs en tiempo real
ssh papyrus "cd /home/ubuntu/paqueteria && docker compose logs -f app"

# Ver uso de recursos
ssh papyrus "docker stats --no-stream"

# Health check remoto
curl http://paquetex.papyrus.com.co/health
```

---

## 🔐 Seguridad

### Configuración Actual
- ✅ SSH configurado con clave pública
- ✅ Nginx como reverse proxy
- ✅ Variables sensibles en .env (no en Git)
- ✅ Firewall configurado (puertos limitados)
- ✅ HTTPS configurado (Let's Encrypt)

### Recomendaciones de Seguridad
1. ✅ No exponer puertos de base de datos
2. ✅ Usar variables de entorno para secretos
3. ✅ Mantener Docker actualizado
4. ⚠️ Rotar credenciales AWS periódicamente
5. ⚠️ Configurar fail2ban para SSH

---

## 📝 Notas Importantes

1. **Ruta del proyecto:** `/home/ubuntu/paqueteria` (no `/opt/paqueteria`)
2. **Usuario:** `ubuntu` (no root)
3. **Alias SSH:** `papyrus` (ya configurado)
4. **Repositorio:** `https://github.com/jemavidev/PAQUETERIAv1.0.git`
5. **Rama principal:** `main`
6. **Docker Compose:** Usa `docker-compose.prod.yml`
7. **Hot reload:** Activo para cambios en código Python/HTML/CSS/JS

---

## ✅ Estado Final

**El servidor está completamente configurado y listo para despliegue automatizado.**

Puedes empezar a usar el flujo de trabajo inmediatamente:
```bash
./deploy-to-aws.sh "tu mensaje de commit"
```

---

**Fecha de análisis:** 2025-11-16
**Servidor:** paquetex.papyrus.com.co
**Estado:** ✅ Operacional y listo
