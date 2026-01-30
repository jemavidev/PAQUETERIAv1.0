# 🚀 Despliegue del Sistema de Facturas V2

## ⚠️ PROBLEMA ACTUAL

```
Health check timeout ❌
```

**Causa**: La migración de base de datos no se ha aplicado.

---

## ✅ SOLUCIÓN INMEDIATA

### Ejecuta SOLO este comando:

```bash
docker-compose -f docker-compose.staging.yml exec app alembic upgrade head && \
docker-compose -f docker-compose.staging.yml restart app
```

**¡Listo!** En 30 segundos estará funcionando.

---

## 📋 Pasos Detallados (Si lo prefieres)

### 1️⃣ Aplicar Migración
```bash
docker-compose -f docker-compose.staging.yml exec app alembic upgrade head
```

**Salida esperada:**
```
INFO  [alembic.runtime.migration] Running upgrade -> 20260130_invoice_v2, create invoice system v2
```

### 2️⃣ Reiniciar App
```bash
docker-compose -f docker-compose.staging.yml restart app
```

**Salida esperada:**
```
Container paqueteria_staging_app Restarted
```

### 3️⃣ Verificar Estado
```bash
docker-compose -f docker-compose.staging.yml ps
```

**Salida esperada:**
```
NAME                    STATUS
paqueteria_staging_app  Up (healthy) ✅
```

---

## 🎯 Verificación

### Health Check
```bash
curl http://localhost:8000/health
```

**Respuesta esperada:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-30T...",
  "version": "1.0.0",
  "environment": "staging"
}
```

### Ruta de Facturas
```bash
curl -I http://localhost:8000/invoices/facturas
```

**Respuesta esperada:**
```
HTTP/1.1 200 OK
```
o
```
HTTP/1.1 302 Found (redirect a login)
```

---

## 🌐 Acceso

Una vez desplegado, accede a:

```
http://localhost:8000/invoices/facturas
```

O haz click en **"Facturas"** en el header (entre "Consulta" y "DynamiaERP").

---

## 📊 Estructura del Sistema

```
Header: [Logo] Paquetes | Mensajes | Clientes | Consulta | FACTURAS | DynamiaERP
                                                            ↑
                                                    Nuevo enlace

Tabs:   FACTURAS | CUFE | PRODUCTOS
        ↑
        Vista por defecto
```

---

## 🔍 Troubleshooting

### Ver Logs
```bash
docker-compose -f docker-compose.staging.yml logs -f app
```

### Ver Migración Actual
```bash
docker-compose -f docker-compose.staging.yml exec app alembic current
```

**Debería mostrar:**
```
20260130_invoice_v2 (head)
```

### Verificar Tablas en DB
```bash
docker-compose -f docker-compose.staging.yml exec db psql -U postgres -d paquetex_staging -c "\dt invoices_v2"
```

**Debería mostrar:**
```
 Schema |    Name     | Type  |  Owner   
--------+-------------+-------+----------
 public | invoices_v2 | table | postgres
```

---

## 🆘 Si Sigue Fallando

### Reinicio Completo
```bash
# 1. Detener todo
docker-compose -f docker-compose.staging.yml down

# 2. Iniciar servicios
docker-compose -f docker-compose.staging.yml up -d

# 3. Esperar 10 segundos
sleep 10

# 4. Aplicar migración
docker-compose -f docker-compose.staging.yml exec app alembic upgrade head

# 5. Reiniciar app
docker-compose -f docker-compose.staging.yml restart app

# 6. Verificar
docker-compose -f docker-compose.staging.yml ps
```

---

## 📚 Documentación

- **Guía Rápida**: `PASOS_DESPLIEGUE_RAPIDO.md`
- **Solución Detallada**: `SOLUCION_HEALTH_CHECK_TIMEOUT.md`
- **Integración Completa**: `INTEGRACION_FACTURAS_COMPLETADA.md`
- **Resumen Final**: `RESUMEN_FINAL_INTEGRACION.md`

---

## ✅ Checklist

- [ ] Aplicar migración
- [ ] Reiniciar app
- [ ] Verificar health check
- [ ] Acceder a /invoices/facturas
- [ ] Ver enlace en header

---

## 🎉 Resultado Final

Después de aplicar la migración:

✅ Health check pasa  
✅ Servicio "Up (healthy)"  
✅ Ruta `/invoices/facturas` funciona  
✅ Enlace "Facturas" visible en header  
✅ Sistema completamente funcional  

---

## ⏱️ Tiempo Total

**30 segundos** para aplicar la migración y reiniciar.

---

## 💡 Nota

**La migración solo se aplica UNA VEZ.**

Después de esto, todos los reinicios funcionarán normalmente.

---

## 🚀 Comando Único (Copy & Paste)

```bash
docker-compose -f docker-compose.staging.yml exec app alembic upgrade head && docker-compose -f docker-compose.staging.yml restart app && echo "✅ Sistema de Facturas V2 desplegado correctamente!"
```

---

**¡Eso es todo!** 🎊

Ejecuta el comando y en 30 segundos tendrás el sistema funcionando.
