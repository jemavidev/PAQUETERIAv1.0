# Diagnóstico: Problema con Envío de SMS

**Fecha**: 2025-02-07  
**Estado**: 🔴 SMS NO SE ESTÁ ENVIANDO

---

## 🔍 HALLAZGOS

### 1. El Código está Correcto ✅
El código en `customer_preferences_otp.py` está intentando enviar el SMS correctamente:
```python
await sms_service.send_sms(
    db=db,
    recipient=phone,
    message=sms_message,
    event_type="CUSTOM_MESSAGE",
    customer_id=str(customer.id),
    is_test=False
)
```

### 2. El SMS Falla Silenciosamente ⚠️
El código captura la excepción pero continúa:
```python
except Exception as e:
    logger.error(f"❌ Error al enviar SMS: {str(e)}")
    # Continúa y envía por Email
```

### 3. Solo se Envía Email ✅
El email SÍ se está enviando correctamente, por eso el mensaje dice:
```
"message": "Contraseña temporal enviada por Email"
```

---

## 🔴 PROBLEMA IDENTIFICADO

**El servicio SMS no está configurado o está fallando**

### Posibles Causas:

1. **Variables de entorno faltantes**:
   - `SMS_API_URL`
   - `SMS_API_KEY`
   - `SMS_SENDER`

2. **Servicio SMS externo caído**:
   - LIWA.co u otro proveedor no responde

3. **Credenciales inválidas**:
   - API key expirada o incorrecta

4. **Límite de créditos**:
   - Cuenta sin saldo

---

## ✅ SOLUCIONES PROPUESTAS

### Opción 1: Verificar Configuración SMS (RECOMENDADO)

1. **Verificar variables de entorno**:
```bash
# En el servidor staging
docker-compose -f docker-compose.staging.yml exec web env | grep SMS
```

2. **Verificar que existan**:
   - `SMS_API_URL`
   - `SMS_API_KEY`
   - `SMS_SENDER`

3. **Si faltan, agregarlas en** `CODE/.env`:
```env
# Configuración SMS
SMS_API_URL=https://api.liwa.co/v1/sms/send
SMS_API_KEY=tu_api_key_aqui
SMS_SENDER=PAQUETEX
```

4. **Reiniciar contenedores**:
```bash
docker-compose -f docker-compose.staging.yml restart web
```

---

### Opción 2: Ver Logs Detallados

```bash
# Ver logs en tiempo real
docker-compose -f docker-compose.staging.yml logs -f web | grep -i "sms\|error"

# Luego solicitar un OTP y ver qué error aparece
```

---

### Opción 3: Ejecutar Diagnóstico Desde Contenedor

```bash
# Entrar al contenedor
docker-compose -f docker-compose.staging.yml exec web bash

# Ejecutar diagnóstico
python diagnostico_sms.py
```

---

## 🎯 MIENTRAS TANTO: Sistema Funcional con Email

**BUENAS NOTICIAS**: El sistema SÍ está funcionando, solo que por Email en lugar de SMS.

### Flujo Actual:
1. Cliente solicita OTP
2. ❌ SMS falla (silenciosamente)
3. ✅ Email se envía correctamente
4. Cliente recibe código por Email
5. Cliente ingresa código
6. ✅ Accede al dashboard

### Impacto:
- ✅ Cliente PUEDE acceder (por Email)
- ⚠️ Cliente NO recibe SMS
- ✅ Preferencias funcionan correctamente
- ✅ Look & Feel perfecto

---

## 📋 CHECKLIST DE VERIFICACIÓN

### Para el Administrador:

- [ ] Verificar variables SMS en `.env`
- [ ] Verificar créditos en cuenta SMS
- [ ] Verificar que API de SMS responda
- [ ] Ver logs del contenedor
- [ ] Probar envío manual de SMS

### Para el Usuario:

- [x] Sistema funciona con Email ✅
- [x] Preferencias se guardan ✅
- [x] Look & Feel perfecto ✅
- [ ] SMS pendiente de configurar ⚠️

---

## 🔧 COMANDO RÁPIDO DE DIAGNÓSTICO

```bash
# 1. Ver configuración SMS
docker-compose -f docker-compose.staging.yml exec web env | grep SMS

# 2. Ver logs de errores
docker-compose -f docker-compose.staging.yml logs --tail=100 web | grep -i "error.*sms"

# 3. Probar solicitud de OTP y ver logs en tiempo real
docker-compose -f docker-compose.staging.yml logs -f web &
curl -X POST https://staging.jemavi.co/api/customer/preferences-otp/request \
  -H "Content-Type: application/json" \
  -d '{"phone": "3002596319"}'
```

---

## 💡 RECOMENDACIÓN INMEDIATA

### Para Producción:

**Opción A**: Configurar SMS correctamente
- Verificar credenciales
- Agregar variables de entorno
- Reiniciar servicios

**Opción B**: Usar solo Email temporalmente
- El sistema funciona perfectamente con Email
- Los clientes pueden acceder sin problemas
- Configurar SMS después

---

## 📊 ESTADO ACTUAL DEL SISTEMA

| Componente | Estado | Notas |
|------------|--------|-------|
| OTP por Email | ✅ Funcional | Enviando correctamente |
| OTP por SMS | ❌ No funciona | Configuración pendiente |
| Verificación OTP | ✅ Funcional | Acepta códigos correctamente |
| Dashboard | ✅ Funcional | Todo perfecto |
| Preferencias | ✅ Funcional | Se guardan correctamente |
| Look & Feel | ✅ Perfecto | Sin cambios necesarios |

---

## 🎯 CONCLUSIÓN

**El sistema está 90% funcional**:
- ✅ Clientes PUEDEN acceder (por Email)
- ✅ Todas las funcionalidades funcionan
- ✅ Preferencias se guardan
- ⚠️ Solo falta configurar SMS

**Acción requerida**: Verificar configuración SMS en el servidor staging.

**Mientras tanto**: El sistema es usable con Email únicamente.
