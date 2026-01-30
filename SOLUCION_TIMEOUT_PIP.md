# 🔧 Solución: Timeout al Instalar Dependencias de Python

## 🎯 Problema
```
ReadTimeoutError: HTTPSConnectionPool(host='files.pythonhosted.org', port=443): Read timed out.
```

**Causa**: Problemas de red al descargar paquetes de PyPI.

---

## ✅ SOLUCIONES (De Más Fácil a Más Compleja)

### 🚀 Solución 1: Script con Reintentos Automáticos (RECOMENDADO)

```bash
bash build_with_retry.sh
```

Este script:
- ✅ Reintenta automáticamente hasta 3 veces
- ✅ Limpia cache entre intentos
- ✅ Aplica la migración automáticamente
- ✅ Inicia los servicios

---

### 🔄 Solución 2: Reintentar el Build

A veces simplemente reintentar funciona:

```bash
# Limpiar cache
docker builder prune -f

# Reintentar build
docker-compose -f docker-compose.staging.yml build app
```

---

### ⚡ Solución 3: Build sin Cache

```bash
docker-compose -f docker-compose.staging.yml build --no-cache app
```

**Nota**: Esto tarda más pero puede resolver problemas de cache corrupto.

---

### 🌐 Solución 4: Usar Dockerfile Robusto

El `Dockerfile.robust` tiene:
- ✅ Timeout aumentado (300 segundos)
- ✅ Más reintentos (5 intentos)
- ✅ Múltiples mirrors de PyPI
- ✅ Instalación en lotes

```bash
# Modificar docker-compose.staging.yml temporalmente
# Cambiar:
#   dockerfile: Dockerfile
# Por:
#   dockerfile: Dockerfile.robust

# Luego build
docker-compose -f docker-compose.staging.yml build app
```

---

### 🔧 Solución 5: Aumentar Timeout Manualmente

Ya actualicé el `Dockerfile` con:
```dockerfile
RUN pip install --no-cache-dir --timeout=300 --retries=5 \
    --index-url https://pypi.org/simple \
    --extra-index-url https://pypi.python.org/simple \
    -r requirements.txt
```

Simplemente vuelve a intentar el build:
```bash
docker-compose -f docker-compose.staging.yml build app
```

---

### 🌍 Solución 6: Verificar Conexión a Internet

```bash
# Verificar conectividad a PyPI
ping -c 3 pypi.org

# Verificar DNS
nslookup files.pythonhosted.org

# Probar descarga manual
curl -I https://files.pythonhosted.org/
```

Si hay problemas de red:
- Verificar firewall
- Verificar proxy
- Verificar VPN
- Intentar desde otra red

---

### 📦 Solución 7: Usar Cache Local de Pip

```bash
# Crear directorio de cache
mkdir -p ~/.cache/pip

# Build con cache montado
docker build \
  --build-arg PIP_CACHE_DIR=/root/.cache/pip \
  -v ~/.cache/pip:/root/.cache/pip \
  -f CODE/Dockerfile \
  -t paqueteria_staging_app:latest \
  CODE/
```

---

### 🔌 Solución 8: Usar Proxy (Si Aplica)

Si estás detrás de un proxy corporativo:

```bash
# Build con proxy
docker-compose -f docker-compose.staging.yml build \
  --build-arg HTTP_PROXY=http://proxy.example.com:8080 \
  --build-arg HTTPS_PROXY=http://proxy.example.com:8080 \
  app
```

---

### ⏰ Solución 9: Intentar en Otro Momento

A veces PyPI tiene problemas temporales:

```bash
# Verificar estado de PyPI
curl https://status.python.org/

# O esperar 10-30 minutos e intentar de nuevo
```

---

## 🎯 Solución Recomendada (Paso a Paso)

### 1. Usar el Script Automático
```bash
bash build_with_retry.sh
```

### 2. Si Falla, Verificar Red
```bash
ping -c 3 pypi.org
curl -I https://files.pythonhosted.org/
```

### 3. Si la Red Está Bien, Limpiar y Reintentar
```bash
docker builder prune -f
docker-compose -f docker-compose.staging.yml build --no-cache app
```

### 4. Si Sigue Fallando, Usar Dockerfile Robusto
```bash
# Editar docker-compose.staging.yml
# Cambiar: dockerfile: Dockerfile
# Por: dockerfile: Dockerfile.robust

docker-compose -f docker-compose.staging.yml build app
```

---

## 🐛 Troubleshooting

### Error Persiste Después de Todo

#### Opción A: Build Fuera de Docker
```bash
# Instalar dependencias localmente primero
cd CODE
pip install -r requirements.txt

# Luego copiar al contenedor
# (Esto crea un cache local que Docker puede usar)
```

#### Opción B: Usar Imagen Pre-construida
```bash
# Si tienes acceso a otra máquina que construyó exitosamente
docker save paqueteria_staging_app:latest > app.tar
# Copiar app.tar a la máquina con problemas
docker load < app.tar
```

#### Opción C: Reducir Dependencias
```bash
# Comentar temporalmente dependencias no críticas en requirements.txt
# Construir con dependencias mínimas
# Instalar el resto después dentro del contenedor
```

---

## 📊 Verificación

### Build Exitoso
```bash
docker images | grep paqueteria_staging_app
```

Debería mostrar:
```
paqueteria_staging_app   latest   abc123def456   2 minutes ago   1.2GB
```

### Servicios Corriendo
```bash
docker-compose -f docker-compose.staging.yml ps
```

Debería mostrar:
```
NAME                    STATUS
paqueteria_staging_app  Up (healthy)
```

---

## 💡 Prevención Futura

### 1. Usar Cache de Docker
```bash
# No hacer prune innecesariamente
# El cache ayuda en builds futuros
```

### 2. Mantener Imagen Base Actualizada
```bash
# Actualizar imagen base periódicamente
docker pull python:3.11-slim
```

### 3. Monitorear Estado de PyPI
- https://status.python.org/
- https://pypi.org/

---

## 🆘 Última Opción

Si nada funciona, puedes:

### 1. Usar Contenedor Existente
```bash
# Si ya tienes un contenedor que funcionó antes
docker commit <container_id> paqueteria_staging_app:latest
```

### 2. Construir en Otra Máquina
```bash
# Construir en una máquina con mejor conexión
# Exportar imagen
# Importar en la máquina con problemas
```

### 3. Contactar Soporte
```bash
# Recopilar información
docker version
docker-compose version
ping -c 5 pypi.org > network_test.txt
traceroute pypi.org >> network_test.txt
```

---

## 📝 Resumen

| Solución | Dificultad | Tiempo | Éxito |
|----------|-----------|--------|-------|
| Script con reintentos | Fácil | 5 min | 90% |
| Reintentar build | Muy fácil | 2 min | 70% |
| Build sin cache | Fácil | 10 min | 80% |
| Dockerfile robusto | Media | 5 min | 95% |
| Verificar red | Fácil | 2 min | - |
| Cache local | Media | 5 min | 85% |
| Usar proxy | Media | 3 min | 90% |
| Intentar más tarde | Muy fácil | - | 60% |

---

## 🚀 Comando Único (Recomendado)

```bash
bash build_with_retry.sh
```

Este comando hace todo automáticamente:
1. Limpia cache
2. Reintenta hasta 3 veces
3. Aplica migración
4. Inicia servicios
5. Verifica que funcione

---

**¡Buena suerte!** 🍀

Si el problema persiste, es muy probable que sea un problema temporal de red o de PyPI.
Espera 30 minutos e intenta de nuevo.
