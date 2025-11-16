# 🚀 README - Desarrollo y Despliegue

## ⚡ Inicio Rápido

### Desarrollo en Localhost

```bash
# Iniciar
docker compose -f docker-compose.prod.yml up -d

# Ver logs
docker logs -f paqueteria_v1_prod_app

# Detener
docker compose -f docker-compose.prod.yml down
```

### Desplegar al Servidor

```bash
# Despliegue seguro (recomendado)
./deploy-safe.sh
```

## 📚 Documentación

- **`GUIA_DESARROLLO_Y_DESPLIEGUE.md`** - Guía completa del flujo de trabajo
- **`RESUMEN_SINCRONIZACION.md`** - Resumen de la sincronización realizada
- **`RESUMEN_FINAL_CORRECCION.md`** - Resumen de la corrección de imágenes

## 🛠️ Scripts Disponibles

| Script | Descripción | Cuándo Usar |
|--------|-------------|-------------|
| `sync-configs.sh` | Verifica sincronización | Antes de cada despliegue |
| `deploy-safe.sh` | Despliegue seguro | Para desplegar al servidor |
| `deploy-to-papyrus.sh` | Despliegue directo | Despliegue rápido |
| `diagnose-server-deep.sh` | Diagnóstico profundo | Si hay problemas |
| `test-static-access.sh` | Test de archivos estáticos | Verificar imágenes |

## ✅ Checklist Rápido

Antes de desplegar:

```bash
# 1. Verificar configuración
./sync-configs.sh

# 2. Probar en localhost
curl http://localhost:8000/health

# 3. Desplegar
./deploy-safe.sh
```

## 🔍 Verificación

### Localhost
```bash
curl http://localhost:8000/health
curl http://localhost:8000/static/images/favicon.png
```

### Servidor
```bash
curl https://paquetex.papyrus.com.co/health
curl https://paquetex.papyrus.com.co/static/images/favicon.png
```

## 🆘 Problemas Comunes

### Las imágenes no se ven

```bash
# Verificar configuración
./sync-configs.sh

# Si hay problemas, recrear contenedores
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d
```

### Error al desplegar

```bash
# Ejecutar diagnóstico
./diagnose-server-deep.sh

# Ver logs del servidor
ssh papyrus "docker logs paqueteria_v1_prod_app --tail 50"
```

## 📞 Ayuda

Si tienes problemas:

1. Lee `GUIA_DESARROLLO_Y_DESPLIEGUE.md`
2. Ejecuta `./sync-configs.sh` para verificar
3. Ejecuta `./diagnose-server-deep.sh` para diagnosticar
4. Revisa los logs: `docker logs paqueteria_v1_prod_app`

## 🎯 Configuración Correcta

```yaml
# ✅ CORRECTO
volumes:
  - ./CODE/src:/app/src
  - uploads_data:/app/uploads
  - logs_data:/app/logs

# ❌ INCORRECTO
volumes:
  - ./CODE/src:/app/src
  - ./CODE/src/static:/app/static  # ← NO DEBE EXISTIR
```

---

**Estado:** ✅ Configuración sincronizada y funcionando  
**Última actualización:** 2025-11-16
