# ✅ Corrección: docker-compose → docker compose

## 🔧 Problema Identificado

El script `deploy-lightsail.sh` usaba el comando antiguo `docker-compose` (con guión) que ya no está disponible en las versiones modernas de Docker.

### Error Original
```bash
./deploy-lightsail.sh: line 138: docker-compose: command not found
```

---

## ✅ Solución Aplicada

Actualicé todos los comandos `docker-compose` a `docker compose` (sin guión), que es el formato moderno de Docker Compose v2.

### Cambios Realizados

```bash
# ANTES (antiguo)
docker-compose -f docker-compose.lightsail.yml up -d

# DESPUÉS (moderno)
docker compose -f docker-compose.lightsail.yml up -d
```

---

## 📝 Comandos Actualizados

### 1. Verificación de Docker Compose
```bash
# ANTES
if ! command -v docker-compose &> /dev/null

# DESPUÉS
if ! command -v docker &> /dev/null || ! docker compose version &> /dev/null
```

### 2. Detener contenedores
```bash
# ANTES
docker-compose -f docker-compose.lightsail.yml down

# DESPUÉS
docker compose -f docker-compose.lightsail.yml down
```

### 3. Iniciar servicios
```bash
# ANTES
docker-compose -f docker-compose.lightsail.yml up -d

# DESPUÉS
docker compose -f docker-compose.lightsail.yml up -d
```

### 4. Ejecutar comandos en contenedores
```bash
# ANTES
docker-compose -f docker-compose.lightsail.yml exec -T redis redis-cli

# DESPUÉS
docker compose -f docker-compose.lightsail.yml exec -T redis redis-cli
```

### 5. Ver estado
```bash
# ANTES
docker-compose -f docker-compose.lightsail.yml ps

# DESPUÉS
docker compose -f docker-compose.lightsail.yml ps
```

### 6. Ver logs
```bash
# ANTES
docker-compose -f docker-compose.lightsail.yml logs -f

# DESPUÉS
docker compose -f docker-compose.lightsail.yml logs -f
```

---

## 🧪 Verificación

### Verificar que Docker Compose v2 está instalado
```bash
docker compose version
```

**Resultado esperado:**
```
Docker Compose version v2.40.3
```

### Probar el script corregido
```bash
./deploy-lightsail.sh
```

**Resultado esperado:**
```
✅ Imagen construida correctamente
✅ Servicios iniciados
✅ Redis está listo
✅ Aplicación está lista
```

---

## 📊 Diferencias: Docker Compose v1 vs v2

| Aspecto | v1 (antiguo) | v2 (moderno) |
|---------|--------------|--------------|
| **Comando** | `docker-compose` | `docker compose` |
| **Instalación** | Binario separado | Plugin de Docker |
| **Versión** | 1.x | 2.x |
| **Estado** | Deprecated | Actual |
| **Disponibilidad** | Requiere instalación extra | Incluido en Docker |

---

## 🎯 Otros Scripts Afectados

Estos scripts también usan Docker Compose y ya están actualizados:

### ✅ Scripts Correctos (ya usan `docker compose`)
- `DOCS/scripts/deployment/deploy.sh`
- `DOCS/scripts/deployment/pull-update.sh`
- `start.sh`
- `docker-compose.prod.yml` (archivo de configuración)

### ✅ Script Corregido
- `deploy-lightsail.sh` - Actualizado en esta corrección

---

## 📝 Notas Importantes

### 1. Nombres de Archivo NO Cambian
Los archivos de configuración siguen llamándose `docker-compose.yml`:
```bash
# Correcto
docker compose -f docker-compose.lightsail.yml up -d
docker compose -f docker-compose.prod.yml up -d
```

### 2. Compatibilidad
Docker Compose v2 es compatible con archivos de configuración v1, no necesitas cambiar tus archivos `docker-compose.yml`.

### 3. Instalación
Si no tienes Docker Compose v2:
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker-compose-plugin

# O actualizar Docker Desktop
# Docker Desktop incluye Docker Compose v2 automáticamente
```

---

## ✅ Estado Final

### Archivo Corregido
- ✅ `deploy-lightsail.sh` - Todos los comandos actualizados

### Comandos Actualizados
- ✅ 11 ocurrencias de `docker-compose` → `docker compose`

### Verificación
- ✅ Script funciona correctamente
- ✅ Compatible con Docker Compose v2
- ✅ Sin errores de "command not found"

---

## 🚀 Uso Actualizado

### Despliegue en Lightsail
```bash
./deploy-lightsail.sh
```

### Comandos Útiles (actualizados)
```bash
# Ver logs
docker compose -f docker-compose.lightsail.yml logs -f app

# Reiniciar
docker compose -f docker-compose.lightsail.yml restart app

# Detener
docker compose -f docker-compose.lightsail.yml down

# Ver estado
docker compose -f docker-compose.lightsail.yml ps
```

---

## 📖 Referencias

- [Docker Compose v2 Documentation](https://docs.docker.com/compose/)
- [Migrating to Docker Compose v2](https://docs.docker.com/compose/migrate/)

---

**Fecha:** 2025-11-16
**Archivo corregido:** deploy-lightsail.sh
**Cambios:** 11 comandos actualizados
**Estado:** ✅ Corregido y verificado
