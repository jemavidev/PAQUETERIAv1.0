# 📱 Configuración Final SMS - PAQUETEX EL CLUB

**Fecha de Actualización:** 17 de Noviembre de 2025  
**Estado:** ✅ OPERATIVO Y PROBADO

---

## 🎯 Resumen Ejecutivo

El sistema de SMS está completamente funcional usando Liwa.co como proveedor. Se identificó y corrigió el problema de formato del API que impedía el envío de mensajes.

---

## 🔧 Configuración Técnica

### Endpoints Liwa.co
```
Autenticación: https://api.liwa.co/v2/auth/login
Envío Individual: https://api.liwa.co/v2/sms/single
Envío Masivo: https://api.liwa.co/v2/sms/multiple
```

### Credenciales
```
Cuenta: 00486396309
API Key: b0cfb7e312af71b70338fd5fe0e5f1ee7cfb4ee7
Password: 6fEuRnd*$#NfFAS
Remitente: PAQUETES
```

### Variables de Entorno (.env)
```bash
LIWA_API_KEY=b0cfb7e312af71b70338fd5fe0e5f1ee7cfb4ee7
LIWA_ACCOUNT=00486396309
LIWA_PASSWORD=6fEuRnd*$#NfFAS
LIWA_AUTH_URL=https://api.liwa.co/v2/auth/login
LIWA_FROM_NAME="PAQUETEX EL CLUB"
```

---

## 📋 Formato Correcto del API

### 1. Autenticación
```http
POST https://api.liwa.co/v2/auth/login
Content-Type: application/json

{
  "account": "00486396309",
  "password": "6fEuRnd*$#NfFAS"
}
```

**Respuesta:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiJ9..."
}
```

### 2. Envío de SMS Individual
```http
POST https://api.liwa.co/v2/sms/single
Authorization: Bearer {token}
API-KEY: b0cfb7e312af71b70338fd5fe0e5f1ee7cfb4ee7
Content-Type: application/json

{
  "number": "573002596319",
  "message": "Mensaje de prueba",
  "type": 1
}
```

**Respuesta Exitosa:**
```json
{
  "success": true,
  "message": "Enviado",
  "number": "573002596319",
  "menssageId": 299303865
}
```

### 3. Envío de SMS Masivo
```http
POST https://api.liwa.co/v2/sms/multiple
Authorization: Bearer {token}
API-KEY: b0cfb7e312af71b70338fd5fe0e5f1ee7cfb4ee7
Content-Type: application/json

{
  "name": "Campaña de prueba",
  "sendingDate": "2025-11-17 15:00:00",
  "messages": [
    {
      "codeCountry": "57",
      "number": "3002596319",
      "message": "Mensaje personalizado 1",
      "type": 1
    },
    {
      "codeCountry": "57",
      "number": "3044000678",
      "message": "Mensaje personalizado 2",
      "type": 1
    }
  ]
}
```

---

## ⚠️ Puntos Críticos

### Headers Requeridos
1. **Authorization:** `Bearer {token}` - Token JWT obtenido de autenticación
2. **API-KEY:** `b0cfb7e312af71b70338fd5fe0e5f1ee7cfb4ee7` - API Key sin prefijo X-
3. **Content-Type:** `application/json`

### Formato del Payload
- ✅ Usar `"number"` (no `"to"`)
- ✅ Incluir código de país: `"57"` para Colombia
- ✅ Incluir `"type": 1` (requerido)
- ❌ NO usar campo `"from"` (remitente)

### Endpoint Correcto
- ✅ `/v2/sms/single` para SMS individual
- ✅ `/v2/sms/multiple` para SMS masivo
- ❌ NO usar `/v2/sms/send` (endpoint incorrecto)

---

## 🧪 Pruebas Realizadas

### Números Probados (17/11/2025)
```
✅ 3044000678 - Message ID: 299303869
✅ 3002596319 - Message ID: 299303870
✅ 3008103849 - Message ID: 299303871
```

### Script de Diagnóstico
```bash
cd CODE
python3 scripts/diagnostico_sms.py
```

**Resultado:**
```
✅ OK - database
✅ OK - service_config
✅ OK - authentication
✅ OK - sms_send

✅ TODAS LAS PRUEBAS PASARON
El sistema está listo para enviar SMS
```

---

## 💻 Implementación en el Código

### Servicio SMS (sms_service.py)

```python
async def _send_liwa_sms(self, config: SMSConfiguration, recipient: str, message: str) -> Dict[str, Any]:
    """Envía SMS usando Liwa.co API"""
    try:
        # Autenticar
        token = await self.authenticate_liwa(config)

        # Preparar número con código de país
        phone_number = recipient
        if not phone_number.startswith("57"):
            phone_number = f"57{phone_number}"
        
        # Payload correcto
        payload = {
            "number": phone_number,
            "message": message,
            "type": 1
        }

        # Headers correctos
        headers = {
            "Authorization": f"Bearer {token}",
            "API-KEY": config.api_key,
            "Content-Type": "application/json"
        }

        # Endpoint correcto
        sms_url = "https://api.liwa.co/v2/sms/single"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(sms_url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

            if data.get("success"):
                return {
                    "success": True,
                    "message_id": data.get("menssageId"),
                    "message": data.get("message")
                }
            else:
                return {
                    "success": False,
                    "error": data.get("message")
                }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
```

---

## 📊 Base de Datos

### Configuración SMS
```sql
SELECT * FROM sms_configuration WHERE is_active = true;
```

**Resultado:**
```
provider: liwa
api_key: b0cfb7e312af71b70338fd5fe0e5f1ee7cfb4ee7
account_id: 00486396309
api_url: https://api.liwa.co/v2/sms/single
auth_url: https://api.liwa.co/v2/auth/login
default_sender: PAQUETES
enable_test_mode: false
is_active: true
cost_per_sms_cents: 50
```

### Notificaciones Enviadas
```sql
SELECT 
    id,
    recipient,
    message,
    status,
    sent_at,
    external_message_id,
    cost_cents
FROM notifications
WHERE notification_type = 'sms'
ORDER BY created_at DESC
LIMIT 10;
```

---

## 💰 Costos y Saldo

### Información de Cuenta
```
Saldo Actual: 73,598 créditos
Costo por SMS: 50 centavos COP
SMS Disponibles: ~147,196 mensajes
Tipo de Pago: Prepago
Fecha de Corte: 2024-12-15
```

### Cálculo de Costos
```python
# Costo por SMS
cost_per_sms = 0.50  # COP

# Ejemplo: 100 SMS
total_sms = 100
total_cost = total_sms * cost_per_sms  # 50 COP
```

---

## 🚀 Uso del Sistema

### Desde Python (Servicio)
```python
from app.services.sms_service import SMSService
from app.database import SessionLocal

db = SessionLocal()
sms_service = SMSService()

# Enviar SMS individual
result = await sms_service.send_sms(
    db=db,
    recipient="3002596319",
    message="Su paquete ha sido recibido",
    event_type=NotificationEvent.PACKAGE_RECEIVED
)

print(f"Status: {result.status}")
print(f"Message ID: {result.notification_id}")
```

### Desde API REST
```bash
curl -X POST "http://localhost/api/v1/notifications/sms/send" \
  -H "Authorization: Bearer {jwt_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient": "3002596319",
    "message": "Su paquete ha sido recibido",
    "event_type": "package_received"
  }'
```

### SMS Masivo
```python
result = await sms_service.send_bulk_sms(
    db=db,
    recipients=["3002596319", "3044000678", "3008103849"],
    message="Notificación masiva",
    event_type=NotificationEvent.CUSTOM_MESSAGE
)

print(f"Enviados: {result.sent_count}")
print(f"Fallidos: {result.failed_count}")
```

---

## 🔍 Troubleshooting

### Error: "Missing or invalid API KEY"
**Causa:** Header incorrecto o faltante  
**Solución:** Usar `API-KEY` (sin prefijo X-) en los headers

### Error: 404 Not Found
**Causa:** Endpoint incorrecto  
**Solución:** Usar `/v2/sms/single` en lugar de `/v2/sms/send`

### Error: 500 Internal Server Error
**Causa:** Formato de payload incorrecto  
**Solución:** Verificar que el payload tenga `number`, `message` y `type: 1`

### SMS no llega
**Verificar:**
1. Número tiene código de país (57)
2. Token no ha expirado (24 horas)
3. Hay saldo disponible
4. Número no está bloqueado

---

## 📞 Soporte

### Liwa.co
- **Soporte:** https://liwa.co/soporte
- **Documentación:** https://api.liwa.co/docs
- **Email:** jesus@papyrus.com.co
- **Teléfono:** 573002596319

### PAQUETEX EL CLUB
- **Empresa:** PAPYRUS SOLUCIONES INTEGRALES
- **NIT:** 901210008
- **Dirección:** Cra 91 #54-120, Local 12, Cartagena
- **Email:** paquetex@papyrus.com.co
- **Teléfono:** 3334004007

---

## 📚 Documentación Relacionada

- `SOLUCION_SMS_LIWA.md` - Solución detallada del problema
- `REPORTE_PRUEBAS_LIWA.md` - Reporte completo de pruebas
- `ANALISIS_SISTEMA_SMS.md` - Análisis del sistema SMS
- `CODE/scripts/diagnostico_sms.py` - Script de diagnóstico

---

## ✅ Checklist de Verificación

- [x] Credenciales configuradas en .env
- [x] API Key actualizado en base de datos
- [x] Endpoint correcto configurado
- [x] Headers correctos implementados
- [x] Formato de payload correcto
- [x] Código de país agregado automáticamente
- [x] Modo de prueba desactivado
- [x] Pruebas exitosas con 3 números
- [x] Servicio SMS funcionando
- [x] Documentación actualizada

---

**Última Actualización:** 17 de Noviembre de 2025  
**Responsable:** Equipo de Desarrollo PAQUETEX  
**Estado:** ✅ PRODUCCIÓN - OPERATIVO
