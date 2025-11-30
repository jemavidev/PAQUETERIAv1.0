# 🔧 Fix: SMS no se envían en Portal de Clientes

**Fecha:** 2024-11-30  
**Problema:** Los códigos OTP no llegan por SMS al solicitar acceso al portal de clientes  
**Causa:** Configuración de SMS en modo de prueba (test mode)

---

## 🔍 Diagnóstico

El sistema de SMS tiene dos modos:
- **Modo de Prueba** (`enable_test_mode=True`): Simula el envío, no envía SMS reales
- **Modo Real** (`enable_test_mode=False`): Envía SMS reales a través de Liwa.co

El problema es que la configuración en la base de datos tiene `enable_test_mode=True`, por lo que los SMS se simulan pero no se envían.

### Archivos Involucrados:
- `CODE/src/app/services/customer_portal_service.py` - Solicitud de OTP
- `CODE/src/app/services/sms_service.py` - Envío de SMS
- `CODE/src/app/models/notification.py` - Modelo SMSConfiguration

---

## ✅ Solución

### Paso 1: Subir cambios a GitHub

Los siguientes archivos tienen correcciones:
- ✅ `CODE/src/main.py` - Eliminada duplicación de router
- ✅ `CODE/src/app/middleware/auth_middleware.py` - Limpiado código de debug
- ✅ `CODE/fix_sms_config.py` - Script para verificar/corregir configuración

### Paso 2: En Staging, ejecutar script de diagnóstico

```bash
# Conectar al servidor staging
ssh staging

# Ir al directorio del proyecto
cd /ruta/al/proyecto

# Ejecutar script de diagnóstico
docker-compose exec web python fix_sms_config.py
```

El script mostrará:
- Configuración actual de SMS
- Si está en modo de prueba o real
- Credenciales configuradas
- Opción para desactivar modo de prueba

### Paso 3: Desactivar modo de prueba

Cuando el script pregunte:
```
¿Desactivar modo de prueba para enviar SMS reales? (s/n):
```

Responder: **s**

Esto cambiará `enable_test_mode` de `True` a `False` en la base de datos.

### Paso 4: Verificar envío

1. Ir al portal de clientes: `https://staging.paquetex.com/customer-portal`
2. Ingresar un número de teléfono registrado
3. Solicitar código OTP
4. Verificar que el SMS llegue al teléfono

---

## 🔐 Verificación de Credenciales

Las credenciales de Liwa.co están en `.env`:

```bash
LIWA_API_KEY=c52d8399ac63a24563ee8a967bafffc6cb8d8dfa
LIWA_ACCOUNT=00486396309
LIWA_PASSWORD=6fEuRnd*$$#NfFAS
LIWA_AUTH_URL=https://api.liwa.co/v2/auth/login
```

El script verificará que estas credenciales estén configuradas correctamente en la base de datos.

---

## 📋 Checklist de Verificación

- [ ] Código subido a GitHub (branch staging)
- [ ] Pull en servidor staging
- [ ] Script `fix_sms_config.py` ejecutado
- [ ] Modo de prueba desactivado
- [ ] SMS de prueba enviado y recibido
- [ ] Portal de clientes funcional

---

## 🐛 Troubleshooting

### Si el SMS sigue sin llegar:

1. **Verificar logs del servidor:**
   ```bash
   docker-compose logs -f web | grep -i sms
   ```

2. **Buscar errores de autenticación:**
   ```bash
   docker-compose logs -f web | grep -i "liwa\|401\|token"
   ```

3. **Verificar que el número esté registrado:**
   ```bash
   docker-compose exec web python -c "
   from src.app.database import SessionLocal
   from src.app.models.customer import Customer
   db = SessionLocal()
   phone = '+573334004007'  # Cambiar por el número a verificar
   customer = db.query(Customer).filter(Customer.phone == phone).first()
   if customer:
       print(f'✅ Cliente encontrado: {customer.full_name}')
   else:
       print(f'❌ Cliente no encontrado con teléfono: {phone}')
   db.close()
   "
   ```

4. **Probar envío directo de SMS:**
   ```bash
   docker-compose exec web python -c "
   import asyncio
   from src.app.database import SessionLocal
   from src.app.services.sms_service import SMSService
   
   async def test():
       db = SessionLocal()
       service = SMSService()
       result = await service.send_sms(
           db=db,
           recipient='+573334004007',
           message='PAQUETEX: Prueba de SMS - Código: 123456',
           is_test=False
       )
       print(f'Resultado: {result}')
       db.close()
   
   asyncio.run(test())
   "
   ```

---

## 📝 Notas Adicionales

- El código OTP tiene una validez de **5 minutos**
- Se permiten máximo **3 intentos** de verificación por código
- Se pueden solicitar máximo **3 códigos por hora** por número
- Cada SMS tiene un costo de **50 centavos COP**
- Los SMS se registran en la tabla `notifications` con `notification_type='sms'`

---

## ✅ Cambios Realizados

### `main.py`
- Eliminada duplicación de `debug_portal_router`

### `auth_middleware.py`
- Eliminado código de debug (logs del portal)
- Eliminado reload forzado de config_routes

### Nuevos archivos
- `fix_sms_config.py` - Script de diagnóstico y corrección
- `PORTAL_CLIENTES_SMS_FIX.md` - Esta documentación

---

**Estado:** ✅ Listo para probar en staging
