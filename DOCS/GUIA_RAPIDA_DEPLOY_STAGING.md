# 🚀 Guía Rápida: Deploy a Staging

## ⚡ Comando Rápido (Todo en Uno)

```bash
ssh papyrus "cd /home/ubuntu/paqueteria && \
  git fetch origin staging && \
  git reset --hard origin/staging && \
  docker compose -f docker-compose.staging.yml build --no-cache app && \
  docker compose -f docker-compose.staging.yml up -d && \
  sleep 10 && \
  curl -s http://localhost:8001/health | python3 -m json.tool"
```

---

## 📋 Paso a Paso

### 1. Conectar al Servidor
```bash
ssh papyrus
cd /home/ubuntu/paqueteria
```

### 2. Actualizar Código
```bash
git fetch origin staging
git reset --hard origin/staging
git log --oneline -1  # Verificar commit
```

### 3. Reconstruir Imagen (IMPORTANTE)
```bash
docker compose -f docker-compose.staging.yml build --no-cache app
```
⏱️ Tiempo estimado: ~2 minutos

### 4. Reiniciar Servicios
```bash
docker compose -f docker-compose.staging.yml up -d
```
⏱️ Tiempo estimado: ~30 segundos

### 5. Verificar Estado
```bash
# Ver contenedores
docker compose -f docker-compose.staging.yml ps

# Health check
curl http://localhost:8001/health

# Ver logs
docker compose -f docker-compose.staging.yml logs app --tail 50
```

---

## 🔍 Verificación Rápida

### ✅ Todo OK si ves:
```json
{
  "status": "healthy",
  "timestamp": "...",
  "version": "4.0.0",
  "environment": "staging"
}
```

### ❌ Problemas si ves:
- `Connection refused` → Contenedor no está corriendo
- `Health check timeout` → Aplicación no inició correctamente
- `502 Bad Gateway` → Nginx no puede conectar con la app

---

## 🛠️ Troubleshooting

### Ver Logs en Tiempo Real
```bash
docker compose -f docker-compose.staging.yml logs -f app
```

### Reiniciar Completamente
```bash
docker compose -f docker-compose.staging.yml down
docker compose -f docker-compose.staging.yml up -d
```

### Limpiar Todo y Empezar de Cero
```bash
docker compose -f docker-compose.staging.yml down -v
docker system prune -f
docker compose -f docker-compose.staging.yml build --no-cache app
docker compose -f docker-compose.staging.yml up -d
```

### Entrar al Contenedor
```bash
docker compose -f docker-compose.staging.yml exec app bash
```

---

## 📊 Información del Entorno

- **Servidor:** papyrus
- **Directorio:** `/home/ubuntu/paqueteria`
- **Puerto:** 8001
- **Rama:** staging
- **Compose File:** `docker-compose.staging.yml`
- **Health Check:** `http://localhost:8001/health`

---

## ⚠️ Notas Importantes

1. **SIEMPRE reconstruir la imagen** después de cambios en el código
2. El flag `--no-cache` asegura que se use el código más reciente
3. Los volúmenes montados permiten hot-reload, pero la imagen base debe estar actualizada
4. El health check tarda ~20-30 segundos en pasar

---

## 🔗 Enlaces Útiles

- **Staging URL:** http://staging.paquetex.com
- **Health Check:** http://localhost:8001/health (desde el servidor)
- **Logs:** `docker compose -f docker-compose.staging.yml logs app`
- **Documentación:** Ver `RESUMEN_FIX_DEPLOY_STAGING.md`

