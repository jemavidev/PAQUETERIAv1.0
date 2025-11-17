# ✅ Solución SMS Liwa.co - PAQUETEX EL CLUB

**Fecha:** 17 de Noviembre de 2025  
**Estado:** ✅ RESUELTO Y FUNCIONANDO

---

## 🎯 Problema Identificado

El sistema intentaba enviar SMS usando el formato incorrecto del API de Liwa.co:

### ❌ Formato Incorrecto (que estábamos usando)
```
POST https://api.liwa.co/v2/sms/send
Headers:
  - Authorization: Bearer {token}
  - Content-Type: application/json

Body:
{
  "to": "3002596319",
  "message": "Mensaje de prueba",
  "from": "PAQUETES"
}
```

### ✅ Formato Correcto (solución)
```
POST https://api.liwa.co/v2/sms/single
Headers:
  - Authorization: Bearer {token}
  - API-KEY: c52d8399ac63a24563ee8a967bafffc6cb8d8dfa
  - Content-Type: application/json

Body:
{
  "number": "573002596319",
  "message": "Mensaje de prueba",
  "type": 1
}
```

---

## 🔑 Diferencias Clave

| Aspecto | Incorrecto | Correcto |
|---------|-----------|----------|
| **Endpoint** | `/v2/sms/send` | `/v2/sms/single` |
| **Header API Key** | ❌ No incluido o `X-API-Key` | ✅ `API-KEY` (sin prefijo X) |
| **Campo número** | `"to"` | `"number"` |
| **Código de país** | Opcional | Requerido (57 para Colombia) |
| **Campo remitente** | `"from"` | ❌ No se usa |
| **Campo type** | ❌ No incluido | ✅ `"type": 1` (requerido) |

---

## 📝 Cambios Realizados

### 1. Servicio SMS (`CODE/src/app/services/sms_service.py`)

#### Método `_send_liwa_sms` actualizado:
```python
async def _send_liwa_sms(self, config: SMSConfiguration, recipient: str, message: str) -> Dict[str, Any]:
    """Envía SMS usando Liwa.co API"""
    try:
        # Autenticar
        token = await self.authenticate_liwa(config)

        # Preparar payload con formato correcto de Liwa.co
        # Asegurar que el número tenga código de país
        phone_number = recipient
        if not phone_number.startswith("57"):
            phone_number = f"57{phone_number}"
        
        payload = {
            "number": phone_number,
            "message": message,
            "type": 1  # Tipo 1 para SMS estándar
        }

        # Enviar SMS usando endpoint correcto /v2/sms/single
        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = {
                "Authorization": f"Bearer {token}",
                "API-KEY": config.api_key,  # Header API-KEY requerido
                "Content-Type": "application/json"
            }

            # Usar endpoint correcto
            sms_url = config.api_url.replace("/sms/send", "/sms/single")
            
            response = await client.post(sms_url, json=payload, headers=headers)
            response.raise_for_status()

            data = response.json()

            if data.get("success"):
                return {
                    "success": True,
                    "message_id": data.get("menssageId", str(uuid.uuid4())),  # Nota: "menssageId" con doble 's'
                    "message": data.get("message", "SMS enviado exitosamente")
                }
            else:
                return {
                    "success": False,
                    "error": data.get("message", "Error en respuesta de Liwa")
                }
    except httpx.HTTPStatusError as e:
        error_data = e.response.json() if e.response.content else {}
        return {
            "success": False,
            "error": f"Error HTTP {e.response.status_code}: {error_data.get('message', str(e))}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error de conexión: {str(e)}"
        }
```

#### Configuración por defecto actualizada:
```python
config = SMSConfiguration(
    provider="liwa",
    api_key=settings.liwa_api_key,
    account_id=settings.liwa_account,
    password=settings.liwa_password,
    auth_url=settings.liwa_auth_url or "https://api.liwa.co/v2/auth/login",
    api_url="https://api.liwa.co/v2/sms/single",  # Endpoint correcto
    default_sender="PAQUETES",
    cost_per_sms_cents=50
)
```

### 2. Base de Datos

```sql
UPDATE sms_configuration 
SET 
    api_url = 'https://api.liwa.co/v2/sms/single',
    enable_test_mode = false
WHERE is_active = true;
```

### 3. Script de Diagnóstico (`CODE/scripts/diagnostico_sms.py`)

Actualizado para usar el formato correcto en las pruebas.

---

## ✅ Resultados de Pruebas

### Prueba Final - 3 Números
```
✅ EXITOSO - 3044000678 (Message ID: 299303869)
✅ EXITOSO - 3002596319 (Message ID: 299303870)
✅ EXITOSO - 3008103849 (Message ID: 299303871)
```

### Respuesta del API
```json
{
  "success": true,
  "message": "Enviado",
  "number": "573044000678",
  "menssageId": 299303869
}
```

---

## 📊 Estado del Sistema

### Componentes
- ✅ Autenticación con Liwa.co
- ✅ Envío de SMS individual
- ✅ Registro en base de datos
- ✅ Validación de números
- ✅ Manejo de errores
- ✅ Modo de prueba (desactivado)

### Credenciales Activas
```
Account: 00486396309
API Key: c52d8399ac63a24563ee8a967bafffc6cb8d8dfa
Auth URL: https://api.liwa.co/v2/auth/login
SMS URL: https://api.liwa.co/v2/sms/single
Saldo: 73,598 créditos
```

---

## 🚀 Uso del Sistema

### Enviar SMS Individual

```python
from app.services.sms_service import SMSService
from app.database import SessionLocal

db = SessionLocal()
sms_service = SMSService()

result = await sms_service.send_sms(
    db=db,
    recipient="3002596319",  # Sin código de país (se agrega automáticamente)
    message="Hola desde PAQUETEX EL CLUB",
    event_type=NotificationEvent.CUSTOM_MESSAGE,
    priority=NotificationPriority.MEDIA
)

print(f"Status: {result.status}")
print(f"Message ID: {result.notification_id}")
```

### Enviar SMS Masivo

```python
result = await sms_service.send_bulk_sms(
    db=db,
    recipients=["3002596319", "3044000678", "3008103849"],
    message="Mensaje masivo desde PAQUETEX EL CLUB",
    event_type=NotificationEvent.CUSTOM_MESSAGE
)

print(f"Enviados: {result.sent_count}")
print(f"Fallidos: {result.failed_count}")
print(f"Costo total: ${result.total_cost_cents / 100} COP")
```

### API REST

```bash
# Enviar SMS
POST /api/v1/notifications/sms/send
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "recipient": "3002596319",
  "message": "Hola desde PAQUETEX EL CLUB",
  "event_type": "custom_message",
  "priority": "media"
}
```

---

## 📋 Endpoints Disponibles

### SMS Individual
```
POST https://api.liwa.co/v2/sms/single
```

### SMS Masivo
```
POST https://api.liwa.co/v2/sms/multiple

Body:
{
  "name": "Nombre de la campaña",
  "sendingDate": "2025-11-17 15:00:00",
  "messages": [
    {
      "codeCountry": "57",
      "number": "3002596319",
      "message": "Mensaje personalizado",
      "type": 1
    }
  ]
}
```

---

## 🔍 Diagnóstico

Para verificar el estado del sistema:

```bash
cd CODE
python3 scripts/diagnostico_sms.py
```

Este script verifica:
- ✅ Conexión a base de datos
- ✅ Configuración del servicio
- ✅ Autenticación con Liwa.co
- ✅ Envío de SMS a múltiples números

---

## 💰 Costos

- **Costo por SMS:** $0.50 COP (50 centavos)
- **Saldo actual:** 73,598 créditos
- **SMS disponibles:** ~147,196 mensajes

---

## 📞 Soporte

### Liwa.co
- **Web:** https://liwa.co/soporte
- **Documentación:** https://api.liwa.co/docs
- **Email:** jesus@papyrus.com.co
- **Teléfono:** 573002596319

### Sistema PAQUETEX
- **Empresa:** PAPYRUS SOLUCIONES INTEGRALES
- **Documento:** 901210008
- **Cuenta Liwa:** 00486396309

---

## 📚 Documentación Adicional

- `REPORTE_PRUEBAS_LIWA.md` - Reporte completo de todas las pruebas realizadas
- `CODE/scripts/diagnostico_sms.py` - Script de diagnóstico
- `CODE/src/app/services/sms_service.py` - Servicio SMS completo

---

**Estado Final:** ✅ Sistema SMS completamente funcional y probado  
**Fecha de Resolución:** 17 de Noviembre de 2025  
**Tiempo de Resolución:** ~2 horas  
**Problema Principal:** Formato incorrecto del API (endpoint y headers)
