# 🚀 Cómo Iniciar el Servidor

## ⚠️ Problema Actual

El servidor **NO está corriendo**. Por eso no carga el aplicativo.

## 📋 Archivos Docker Compose Disponibles

Tienes 3 archivos de configuración:

1. **docker-compose.dev.yml** - Para desarrollo local
2. **docker-compose.lightsail.yml** - Para AWS Lightsail
3. **docker-compose.prod.yml** - Para producción

## 🏃 Cómo Iniciar

### Opción 1: Desarrollo Local (Recomendado)

```bash
docker compose -f docker-compose.dev.yml up -d
```

### Opción 2: Producción Local

```bash
docker compose -f docker-compose.prod.yml up -d
```

### Opción 3: Crear Symlink (Para usar `docker compose` sin `-f`)

```bash
# Crear enlace simbólico al archivo de desarrollo
ln -s docker-compose.dev.yml docker-compose.yml

# Ahora puedes usar:
docker compose up -d
```

## 🔍 Verificar que Está Corriendo

```bash
# Ver estado de los contenedores
docker compose -f docker-compose.dev.yml ps

# Ver logs en tiempo real
docker compose -f docker-compose.dev.yml logs -f web

# Ver logs de la base de datos
docker compose -f docker-compose.dev.yml logs -f db
```

## 🛑 Detener el Servidor

```bash
docker compose -f docker-compose.dev.yml down
```

## 🔄 Reiniciar el Servidor

```bash
docker compose -f docker-compose.dev.yml restart
```

## 🐛 Si Hay Errores al Iniciar

### 1. Ver los logs completos:

```bash
docker compose -f docker-compose.dev.yml logs web
```

### 2. Errores comunes:

#### Puerto 8000 ya en uso:
```bash
# Ver qué está usando el puerto
sudo lsof -i :8000

# Matar el proceso
sudo kill -9 <PID>
```

#### Base de datos no inicia:
```bash
# Ver logs de la base de datos
docker compose -f docker-compose.dev.yml logs db

# Reiniciar solo la base de datos
docker compose -f docker-compose.dev.yml restart db
```

#### Errores de Python/Dependencias:
```bash
# Reconstruir las imágenes
docker compose -f docker-compose.dev.yml build --no-cache

# Iniciar de nuevo
docker compose -f docker-compose.dev.yml up -d
```

## ✅ Verificar que Funciona

Una vez iniciado, verifica:

```bash
# 1. Ver que los contenedores están corriendo
docker compose -f docker-compose.dev.yml ps

# Deberías ver algo como:
# NAME                COMMAND                  SERVICE   STATUS
# paqueteria-web-1    "uvicorn main:app ..."   web       Up
# paqueteria-db-1     "docker-entrypoint..."   db        Up

# 2. Probar el endpoint de salud
curl http://localhost:8000/health

# Debería devolver:
# {"status":"healthy","timestamp":"...","version":"1.0.0","environment":"development"}

# 3. Abrir en el navegador
# http://localhost:8000
```

## 📝 Después de Iniciar

Una vez que el servidor esté corriendo:

### 1. Crear la tabla de preferencias (solo primera vez):

```bash
docker compose -f docker-compose.dev.yml exec web python /app/crear_tabla_customer_preferences.py
```

### 2. Probar el sistema:

- **Login:** http://localhost:8000/auth/login
- **Preferencias:** http://localhost:8000/customers/manage

## 🎯 Resumen Rápido

```bash
# 1. Iniciar servidor
docker compose -f docker-compose.dev.yml up -d

# 2. Ver logs
docker compose -f docker-compose.dev.yml logs -f web

# 3. Crear tabla (solo primera vez)
docker compose -f docker-compose.dev.yml exec web python /app/crear_tabla_customer_preferences.py

# 4. Abrir navegador
# http://localhost:8000/auth/login
```

## 🔧 Comandos Útiles

```bash
# Ver todos los contenedores (incluso detenidos)
docker ps -a

# Ver logs de un contenedor específico
docker logs <container_id>

# Entrar a un contenedor
docker compose -f docker-compose.dev.yml exec web bash

# Ver uso de recursos
docker stats

# Limpiar todo (⚠️ CUIDADO: elimina volúmenes)
docker compose -f docker-compose.dev.yml down -v
```

## 📞 Si Nada Funciona

1. **Detener todo:**
   ```bash
   docker compose -f docker-compose.dev.yml down
   ```

2. **Limpiar imágenes:**
   ```bash
   docker system prune -a
   ```

3. **Reconstruir desde cero:**
   ```bash
   docker compose -f docker-compose.dev.yml build --no-cache
   docker compose -f docker-compose.dev.yml up -d
   ```

4. **Ver logs detallados:**
   ```bash
   docker compose -f docker-compose.dev.yml logs --tail=100 web
   ```

---

**Nota:** Todos los cambios que hice están guardados. Solo necesitas iniciar el servidor para que funcionen.
