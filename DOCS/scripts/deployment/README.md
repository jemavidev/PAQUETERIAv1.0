# 🚀 Scripts de Despliegue - PAQUETERÍA v1.0

## 📋 Descripción

Este directorio contiene scripts esenciales para el despliegue y mantenimiento del proyecto PAQUETERÍA v1.0 en producción.

## 📁 Scripts Disponibles

### 1. `deploy.sh` - Despliegue desde GitHub
**Uso**: `./DOCS/scripts/deployment/deploy.sh [branch|tag]`

Despliega el proyecto desde GitHub:
- Actualiza código desde GitHub
- Construye imágenes Docker
- Inicia servicios en producción
- Limpia imágenes huérfanas

**Requisitos**:
- Git instalado
- Docker y Docker Compose instalados
- Archivo `.env` en la raíz del proyecto
- Archivo `docker-compose.prod.yml` en la raíz

**Ejemplo**:
```bash
./DOCS/scripts/deployment/deploy.sh main
./DOCS/scripts/deployment/deploy.sh v1.0.0
```

---

### 2. `rollback.sh` - Rollback a versión anterior
**Uso**: `./DOCS/scripts/deployment/rollback.sh <tag|commit>`

Hace rollback a una versión anterior del proyecto:
- Cambia a tag/commit especificado
- Reconstruye imágenes Docker
- Reinicia servicios

**Requisitos**:
- Git instalado
- Docker y Docker Compose instalados
- Archivo `.env` en la raíz del proyecto

**Ejemplo**:
```bash
./DOCS/scripts/deployment/rollback.sh v1.0.0
./DOCS/scripts/deployment/rollback.sh abc1234
```

---

### 3. `setup-production.sh` - Configuración de producción
**Uso**: `sudo ./DOCS/scripts/deployment/setup-production.sh [domain] [email] [project_dir]`

Configura el servidor para producción:
- Configura Nginx con proxy reverso
- Configura servicio systemd para auto-start
- Configura SSL con Let's Encrypt (opcional)
- Instala scripts de verificación

**Requisitos**:
- Ejecutar como root (sudo)
- Nginx instalado
- Certbot instalado (para SSL)

**Ejemplo**:
```bash
sudo ./DOCS/scripts/deployment/setup-production.sh paquetex.papyrus.com.co admin@papyrus.com.co /opt/paqueteria/Paqueteria-v1.0
```

---

### 4. `setup-env.sh` - Configuración de .env
**Uso**: `./DOCS/scripts/deployment/setup-env.sh`

Crea y configura el archivo `.env`:
- Crea `.env` desde `CODE/env.example`
- Genera `SECRET_KEY` automáticamente
- Muestra instrucciones para completar configuración

**Requisitos**:
- Archivo `CODE/env.example` existente
- OpenSSL instalado (para generar SECRET_KEY)

**Ejemplo**:
```bash
./DOCS/scripts/deployment/setup-env.sh
```

**Nota**: Este script está disponible también como `start.sh` en la raíz del proyecto.

---

### 5. `dev-up.sh` - Desarrollo con hot reload
**Uso**: `./DOCS/scripts/deployment/dev-up.sh [branch|tag]`

Inicia el proyecto en modo desarrollo con hot reload:
- Actualiza código desde GitHub
- Inicia servicios con hot reload
- Permite cambios en tiempo real

**Requisitos**:
- Git instalado
- Docker y Docker Compose instalados
- Archivo `.env` en la raíz del proyecto
- Archivo `docker-compose.dev.override.yml` (opcional)

**Ejemplo**:
```bash
./DOCS/scripts/deployment/dev-up.sh main
```

---

### 6. `pull-only.sh` - Solo actualización de código
**Uso**: `./DOCS/scripts/deployment/pull-only.sh [branch|tag]`

Actualiza solo el código desde GitHub sin reconstruir imágenes:
- Actualiza archivos desde GitHub
- No reconstruye imágenes Docker
- No reinicia servicios
- Útil para actualizaciones rápidas sin downtime

**Requisitos**:
- Git instalado
- Repositorio Git configurado

**Ejemplo**:
```bash
./DOCS/scripts/deployment/pull-only.sh main
```

---

### 7. `deploy-aws.sh` - Despliegue a AWS
**Uso**: `./DOCS/scripts/deployment/deploy-aws.sh [branch|tag]`

Script para desplegar a AWS (pendiente de implementación completa).

---

## 📄 Archivos de Configuración

### `nginx-production.conf`
Configuración de Nginx para producción:
- Proxy reverso a aplicación FastAPI
- Configuración de SSL (modificada por certbot)
- Headers de seguridad
- Configuración de uploads

### `paqueteria.service`
Servicio systemd para auto-start:
- Inicia servicios Docker Compose al arrancar
- Reinicia servicios en caso de fallo
- Configuración de timeouts y reintentos

---

## 🔧 Configuración Previa

Antes de usar estos scripts, asegúrate de:

1. **Archivo `.env`** en la raíz del proyecto:
   ```bash
   cp CODE/env.example .env
   # Editar .env con tus valores reales
   ```

2. **Docker y Docker Compose** instalados:
   ```bash
   docker --version
   docker compose version
   ```

3. **Git** configurado:
   ```bash
   git remote -v
   ```

4. **Permisos de ejecución**:
   ```bash
   chmod +x DOCS/scripts/deployment/*.sh
   ```

---

## 🚀 Flujo de Despliegue Típico

1. **Configuración inicial**:
   ```bash
   ./DOCS/scripts/deployment/setup-env.sh
   # Editar .env con valores reales
   ```

2. **Primer despliegue**:
   ```bash
   ./DOCS/scripts/deployment/deploy.sh main
   ```

3. **Configuración de producción** (en servidor):
   ```bash
   sudo ./DOCS/scripts/deployment/setup-production.sh paquetex.papyrus.com.co admin@papyrus.com.co
   ```

4. **Actualizaciones futuras**:
   ```bash
   ./DOCS/scripts/deployment/deploy.sh main
   # O solo actualizar código:
   ./DOCS/scripts/deployment/pull-only.sh main
   docker compose restart app
   ```

5. **Rollback si es necesario**:
   ```bash
   ./DOCS/scripts/deployment/rollback.sh v1.0.0
   ```

---

## 📝 Notas Importantes

- **`.env`**: Todos los scripts esperan el archivo `.env` en la raíz del proyecto (no en `CODE/LOCAL/.env`).
- **Docker Compose**: Los scripts detectan automáticamente `docker-compose.prod.yml` o `docker-compose.yml`.
- **Permisos**: Algunos scripts requieren permisos de root (especialmente `setup-production.sh`).
- **Git**: Los scripts asumen que el proyecto está en un repositorio Git con remoto configurado.

---

## 🔍 Verificación

Después del despliegue, verifica que todo funcione:

```bash
# Verificar contenedores
docker compose ps

# Verificar health check
curl http://localhost:8000/health

# Ver logs
docker compose logs -f app
```

---

## 📚 Documentación Relacionada

- **README.md** - Documentación principal del proyecto
- **DOCS/documentacion/README_DEPLOY.md** - Guía detallada de despliegue
- **DOCS/documentacion/CHECKLIST_PRODUCCION.md** - Checklist de producción

---

**Última actualización**: 2025-11-12  
**Versión**: 1.0.0

