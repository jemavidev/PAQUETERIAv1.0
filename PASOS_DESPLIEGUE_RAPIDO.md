# ⚡ Pasos de Despliegue Rápido - Sistema de Facturas V2

## 🎯 El Problema
El health check falla porque **la migración de base de datos no se ha aplicado**.

## ✅ La Solución (3 Comandos)

### Opción A: Automático (Recomendado)
```bash
bash deploy_invoices_v2.sh
```
**Listo!** El script hace todo automáticamente.

---

### Opción B: Manual (Si prefieres control)

#### 1. Aplicar Migración
```bash
docker-compose -f docker-compose.staging.yml exec app alembic upgrade head
```

#### 2. Reiniciar App
```bash
docker-compose -f docker-compose.staging.yml restart app
```

#### 3. Verificar
```bash
docker-compose -f docker-compose.staging.yml logs -f app
```

---

## 🔍 Verificación Rápida

### ¿Está corriendo?
```bash
docker-compose -f docker-compose.staging.yml ps
```

Debería mostrar:
```
NAME                    STATUS
paqueteria_staging_app  Up (healthy)  ← Debe decir "healthy"
```

### ¿Responde?
```bash
curl http://localhost:8000/health
```

Debería responder:
```json
{"status": "healthy", ...}
```

### ¿Funciona la ruta?
```bash
curl -I http://localhost:8000/invoices/facturas
```

Debería responder: `200 OK` o `302 Found`

---

## 🎉 Resultado

Después de aplicar la migración:

1. ✅ El health check pasará
2. ✅ El servicio estará "Up (healthy)"
3. ✅ Podrás acceder a `/invoices/facturas`
4. ✅ Verás el enlace "Facturas" en el header

---

## 🐛 Si Algo Sale Mal

### Ver logs
```bash
docker-compose -f docker-compose.staging.yml logs --tail=50 app
```

### Ver migración actual
```bash
docker-compose -f docker-compose.staging.yml exec app alembic current
```

### Reiniciar todo
```bash
docker-compose -f docker-compose.staging.yml down
docker-compose -f docker-compose.staging.yml up -d
docker-compose -f docker-compose.staging.yml exec app alembic upgrade head
docker-compose -f docker-compose.staging.yml restart app
```

---

## 📚 Documentación Completa

Para más detalles, ver: `SOLUCION_HEALTH_CHECK_TIMEOUT.md`

---

## ⏱️ Tiempo Estimado

- **Opción A (Automático)**: ~2 minutos
- **Opción B (Manual)**: ~1 minuto

---

## 💡 Nota Importante

**La migración solo se aplica UNA VEZ.**

Después de aplicarla, los reinicios normales funcionarán sin problemas.

---

## 🚀 Comando Único (Todo en Uno)

Si tienes prisa, ejecuta esto:

```bash
docker-compose -f docker-compose.staging.yml exec app alembic upgrade head && \
docker-compose -f docker-compose.staging.yml restart app && \
echo "✅ Listo! Accede a: http://localhost:8000/invoices/facturas"
```

---

**¡Eso es todo!** 🎊
