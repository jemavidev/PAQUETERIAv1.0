# ⚡ Fix Rápido: Timeout de Pip

## 🎯 El Problema
```
ReadTimeoutError: Read timed out.
```

Pip no puede descargar paquetes de PyPI por timeout de red.

---

## ✅ SOLUCIÓN RÁPIDA (Elige Una)

### Opción 1: Script Automático (RECOMENDADO) ⭐
```bash
bash build_with_retry.sh
```
**Hace todo automáticamente con 3 reintentos.**

---

### Opción 2: Reintentar Manualmente
```bash
# Limpiar cache
docker builder prune -f

# Reintentar
docker-compose -f docker-compose.staging.yml build app
```

---

### Opción 3: Build sin Cache
```bash
docker-compose -f docker-compose.staging.yml build --no-cache app
```

---

## 🔍 ¿Por Qué Pasa?

1. **Red lenta** - PyPI está lejos o tu conexión es lenta
2. **Timeout muy corto** - Pip se rinde muy rápido
3. **PyPI sobrecargado** - Muchas personas descargando
4. **Firewall/Proxy** - Bloqueando la conexión

---

## ✅ Lo Que Ya Hice

Actualicé el `Dockerfile` con:
- ✅ Timeout aumentado a 300 segundos
- ✅ 5 reintentos automáticos
- ✅ Múltiples mirrors de PyPI

**Solo necesitas volver a intentar el build.**

---

## 🚀 Pasos Recomendados

### 1. Usar Script Automático
```bash
bash build_with_retry.sh
```

### 2. Si Falla, Verificar Red
```bash
ping pypi.org
```

### 3. Si Red OK, Esperar y Reintentar
```bash
# Esperar 10 minutos
sleep 600

# Reintentar
docker-compose -f docker-compose.staging.yml build app
```

---

## 💡 Tips

- **No hagas `docker builder prune` innecesariamente** - El cache ayuda
- **Intenta en horarios de menos tráfico** - Madrugada funciona mejor
- **Verifica tu conexión a internet** - Debe ser estable
- **Si tienes VPN, prueba sin ella** - A veces causa problemas

---

## 🎯 Resultado Esperado

Después del build exitoso:
```
Successfully built abc123def456
Successfully tagged paqueteria_staging_app:latest
```

Luego:
```bash
docker-compose -f docker-compose.staging.yml up -d
docker-compose -f docker-compose.staging.yml exec app alembic upgrade head
docker-compose -f docker-compose.staging.yml restart app
```

---

## 📚 Documentación Completa

Ver: `SOLUCION_TIMEOUT_PIP.md`

---

## ⏱️ Tiempo Estimado

- **Con script automático**: 5-10 minutos
- **Manual**: 2-5 minutos por intento

---

## 🆘 Si Nada Funciona

1. Verifica que PyPI esté funcionando: https://status.python.org/
2. Intenta desde otra red (móvil, otra WiFi)
3. Espera 30 minutos e intenta de nuevo
4. Usa el `Dockerfile.robust` (ver documentación completa)

---

**¡Ejecuta el script y listo!** 🚀

```bash
bash build_with_retry.sh
```
