# 📱 API LIWA.CO - Guía de Referencia Completa
**PAQUETEX EL CLUB**  
**Última actualización:** 26 de noviembre de 2025

---

## 📋 Índice
1. [Información General](#información-general)
2. [Autenticación](#autenticación)
3. [Endpoints Disponibles](#endpoints-disponibles)
4. [Envío de SMS Individual](#envío-de-sms-individual)
5. [Envío de SMS Masivo](#envío-de-sms-masivo)
6. [Códigos de Respuesta](#códigos-de-respuesta)
7. [Limitaciones de la API](#limitaciones-de-la-api)
8. [Ejemplos de Uso](#ejemplos-de-uso)
9. [Troubleshooting](#troubleshooting)
10. [Información de Cuenta](#información-de-cuenta)

---

## 📌 Información General

### Proveedor
- **Nombre:** LIWA.co
- **Sitio web:** https://liwa.co
- **Panel de control:** https://liwa.co/dashboard
- **Documentación oficial:** https://api.liwa.co/docs
- **Soporte:** soporte@liwa.co

### Credenciales de PAQUETEX
```
Cuenta: 00486396309
API Key: c52d8399ac63a24563ee8a967bafffc6cb8d8dfa
Remitente: PAQUETEX
```

### Base URL
```
https://api.liwa.co/v2
```

---

## 🔐 Autenticación

### Endpoint
```
POST /v2/auth/login
```

### Request
```http
POST https://api.liwa.co/v2/auth/login
Content-Type: application/json

{
  "account": "00486396309",
  "password": "6fEuRnd*$#NfFAS"
}
```

### Response Exitosa
```json
{
  "token": "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIwMDQ4NjM5NjMwOSIsImlhdCI6MTczMjY1..."
}
```

### Características del Token
- **Tipo:** JWT (JSON Web Token)
- **Duración:** 24 horas
- **Uso:** Incluir en header `Authorization: Bearer {token}`
- **Renovación:** Obtener nuevo token cuando expire

### Ejemplo en Python
```python
import httpx

async def authenticate():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.liwa.co/v2/auth/login",
            json={
                "account": "00486396309",
                "password": "6fEuRnd*$#NfFAS"
            }
        )
        data = response.json()
        return data.get("token")
```

---

## 🌐 Endpoints Disponibles

### ✅ Endpoints Funcionales (Documentación Oficial)

| Método | Endpoint | Descripción | Estado |
|--------|----------|-------------|--------|
| POST | `/v2/auth/login` | Autenticación | ✅ Funcional |
| GET | `/v2/sms/single` | Envío SMS individual (método alternativo) | ✅ Funcional |
| POST | `/v2/sms/single` | Envío SMS individual | ✅ Funcional |
| POST | `/v2/sms/multiple` | Envío SMS masivo | ✅ Funcional |
| POST | `/v2/sms/text2speech` | Envío de texto a voz o SMS | ✅ Funcional |

### ❌ Endpoints NO Disponibles

Los siguientes endpoints fueron probados y **NO están disponibles** públicamente:

**Información de Cuenta:**
- `/v2/account` - 404
- `/v2/account/info` - 404
- `/v2/account/balance` - 404
- `/v2/user` - 404
- `/v2/me` - 404

**Saldo y Créditos:**
- `/v2/balance` - 404
- `/v2/credits` - 404
- `/v2/wallet` - 404

**Historial:**
- `/v2/sms/history` - 500
- `/v2/sms/sent` - 500
- `/v2/messages/history` - 404

**Estadísticas:**
- `/v2/stats` - 404
- `/v2/sms/stats` - 500
- `/v2/reports` - 404

**Otros:**
- `/v2/campaigns` - 404
- `/v2/contacts` - 404
- `/v2/templates` - 500
- `/v2/webhooks` - 404

### 💡 Conclusión
La API de LIWA está enfocada en **envío de mensajes** (SMS y texto a voz). Para consultar saldo, historial o estadísticas, debes usar el **panel web** en https://liwa.co/dashboard

### 📚 Documentación Oficial
- **OpenAPI Spec:** https://apidoc.liwa.co/openapi.json
- **Documentación Web:** https://apidoc.liwa.co/
- **Versión API:** 2.0.0
- **Servidores:**
  - Producción: https://api.liwa.co/v2
  - Staging: https://api-dev.liwa.co/v2

---

## 📤 Envío de SMS Individual

### Endpoint
```
POST /v2/sms/single
```

### Headers Requeridos
```http
Authorization: Bearer {token}
API-KEY: c52d8399ac63a24563ee8a967bafffc6cb8d8dfa
Content-Type: application/json
```

### Request Body
```json
{
  "number": "573002596319",
  "message": "Su paquete ha sido recibido",
  "type": 1
}
```

### Parámetros

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `number` | string | ✅ Sí | Número con código de país (57 para Colombia) |
| `message` | string | ✅ Sí | Texto del mensaje (máx. 160 caracteres por SMS) |
| `type` | integer | ✅ Sí | Tipo de mensaje (1 = SMS estándar) |

### Response Exitosa
```json
{
  "success": true,
  "message": "Enviado",
  "number": "573002596319",
  "menssageId": 300484651
}
```

### Response de Error
```json
{
  "success": false,
  "message": "Lo sentimos el mensaje tiene caracteres inválidos"
}
```

### Ejemplo Completo en Python
```python
import httpx

async def send_sms(token, phone, message):
    # Asegurar código de país
    if not phone.startswith("57"):
        phone = f"57{phone}"
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.liwa.co/v2/sms/single",
            headers={
                "Authorization": f"Bearer {token}",
                "API-KEY": "c52d8399ac63a24563ee8a967bafffc6cb8d8dfa",
                "Content-Type": "application/json"
            },
            json={
                "number": phone,
                "message": message,
                "type": 1
            }
        )
        return response.json()
```

### Ejemplo en cURL
```bash
curl -X POST "https://api.liwa.co/v2/sms/single" \
  -H "Authorization: Bearer {token}" \
  -H "API-KEY: c52d8399ac63a24563ee8a967bafffc6cb8d8dfa" \
  -H "Content-Type: application/json" \
  -d '{
    "number": "573002596319",
    "message": "Su paquete ha sido recibido",
    "type": 1
  }'
```

### Método Alternativo: GET
También puedes enviar SMS usando el método GET con headers:

```bash
curl -X GET "https://api.liwa.co/v2/sms/single" \
  -H "apiKey: c52d8399ac63a24563ee8a967bafffc6cb8d8dfa" \
  -H "account: 00486396309" \
  -H "password: 6fEuRnd*$#NfFAS" \
  -H "number: 573002596319" \
  -H "message: Su paquete ha sido recibido" \
  -H "type: 1"
```

**Nota:** Este método no requiere autenticación previa (no usa JWT), pero expone las credenciales en cada request. Se recomienda usar el método POST con JWT.

---

## 📨 Envío de SMS Masivo

### Endpoint
```
POST /v2/sms/multiple
```

### Headers Requeridos
```http
Authorization: Bearer {token}
API-KEY: c52d8399ac63a24563ee8a967bafffc6cb8d8dfa
Content-Type: application/json
```

### Request Body
```json
{
  "name": "Campaña Notificaciones",
  "sendingDate": "2025-11-26 15:00:00",
  "messages": [
    {
      "codeCountry": "57",
      "number": "3002596319",
      "message": "Su paquete ABC123 está listo",
      "type": 1
    },
    {
      "codeCountry": "57",
      "number": "3008103849",
      "message": "Su paquete XYZ456 está listo",
      "type": 1
    }
  ]
}
```

### Parámetros

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `name` | string | ✅ Sí | Nombre de la campaña |
| `sendingDate` | string | ✅ Sí | Fecha y hora de envío (formato: YYYY-MM-DD HH:MM:SS) |
| `messages` | array | ✅ Sí | Lista de mensajes a enviar |
| `messages[].codeCountry` | string | ✅ Sí | Código de país (57 para Colombia) |
| `messages[].number` | string | ✅ Sí | Número sin código de país |
| `messages[].message` | string | ✅ Sí | Texto del mensaje |
| `messages[].type` | integer | ✅ Sí | Tipo de mensaje (1 = SMS estándar) |

### Response Exitosa
```json
{
  "success": true,
  "message": "Campaña creada exitosamente",
  "campaignId": "12345"
}
```

### Ejemplo en Python
```python
async def send_bulk_sms(token, recipients):
    messages = []
    for phone, message in recipients:
        messages.append({
            "codeCountry": "57",
            "number": phone.replace("57", ""),  # Sin código de país
            "message": message,
            "type": 1
        })
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.liwa.co/v2/sms/multiple",
            headers={
                "Authorization": f"Bearer {token}",
                "API-KEY": "c52d8399ac63a24563ee8a967bafffc6cb8d8dfa",
                "Content-Type": "application/json"
            },
            json={
                "name": "Notificaciones Automáticas",
                "sendingDate": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "messages": messages
            }
        )
        return response.json()
```

---

## 📞 Envío de Texto a Voz (Text2Speech)

### Endpoint
```
POST /v2/sms/text2speech
```

### Descripción
Permite enviar un mensaje que puede ser entregado como:
- **SMS** (type: 0)
- **Llamada de voz** (type: 1)
- **Ambos** (type: 2)

### Headers Requeridos
```http
Authorization: Bearer {token}
API-KEY: c52d8399ac63a24563ee8a967bafffc6cb8d8dfa
Content-Type: application/json
```

### Request Body
```json
{
  "number": "3002596319",
  "countryCode": "57",
  "message": "Su paquete ha sido entregado",
  "type": 0
}
```

### Parámetros

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `number` | string | ✅ Sí | Número de teléfono (incluir indicativo de ciudad para llamadas) |
| `countryCode` | string | ✅ Sí | Código de país (57 para Colombia) |
| `message` | string | ✅ Sí | Mensaje a enviar |
| `type` | integer | ✅ Sí | 0=SMS, 1=VOZ, 2=Ambos |

### Response Exitosa
```json
[
  {
    "id": 12345,
    "status": true,
    "message": "Mensaje enviado exitosamente"
  }
]
```

### Ejemplo en Python
```python
async def send_text2speech(token, phone, message, delivery_type=0):
    """
    delivery_type:
    0 = Solo SMS
    1 = Solo llamada de voz
    2 = SMS y llamada de voz
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.liwa.co/v2/sms/text2speech",
            headers={
                "Authorization": f"Bearer {token}",
                "API-KEY": "c52d8399ac63a24563ee8a967bafffc6cb8d8dfa",
                "Content-Type": "application/json"
            },
            json={
                "number": phone,
                "countryCode": "57",
                "message": message,
                "type": delivery_type
            }
        )
        return response.json()
```

### Casos de Uso
- **Notificaciones urgentes:** Usar type=2 (SMS + Voz)
- **Confirmaciones importantes:** Usar type=1 (Solo voz)
- **Notificaciones estándar:** Usar type=0 (Solo SMS)

---

## 📊 Códigos de Respuesta

### Códigos HTTP

| Código | Significado | Descripción |
|--------|-------------|-------------|
| 200 | OK | Solicitud exitosa |
| 400 | Bad Request | Error en el formato de la solicitud |
| 401 | Unauthorized | Token inválido o expirado |
| 404 | Not Found | Endpoint no existe |
| 500 | Internal Server Error | Error del servidor |

### Mensajes de Error Comunes

| Error | Causa | Solución |
|-------|-------|----------|
| "Missing or invalid API KEY" | Header API-KEY incorrecto | Verificar que sea `API-KEY` (sin X-) |
| "Token expired" | Token JWT expirado | Obtener nuevo token |
| "caracteres inválidos" | Mensaje con emojis o caracteres especiales | Usar solo texto ASCII |
| "Invalid phone number" | Formato de número incorrecto | Usar formato 57XXXXXXXXXX |

---

## ⚠️ Limitaciones de la API

### Funcionalidad Limitada
- ❌ **NO** se puede consultar saldo de créditos
- ❌ **NO** se puede consultar historial de SMS
- ❌ **NO** se puede consultar estadísticas
- ❌ **NO** se puede gestionar contactos
- ❌ **NO** se puede gestionar plantillas
- ❌ **NO** hay webhooks para notificaciones de entrega
- ✅ **SÍ** se puede enviar SMS individual
- ✅ **SÍ** se puede enviar SMS masivo

### Restricciones de Contenido
- ❌ No se permiten emojis
- ❌ No se permiten caracteres especiales (tildes limitadas)
- ✅ Solo texto ASCII estándar
- ✅ Máximo 466 caracteres por mensaje (según documentación oficial)
- ✅ Mensajes largos se dividen automáticamente en múltiples SMS

### Tipos de Mensaje
Según la documentación oficial, existen 3 tipos de mensaje:

| Tipo | Descripción | Uso |
|------|-------------|-----|
| 1 | Mensaje de una vía (internacional) | SMS estándar, sin respuesta |
| 2 | Mensaje de doble vía | SMS con posibilidad de respuesta |
| 3 | Mensaje de una vía (internacional) | Alternativa al tipo 1 |

**Recomendación:** Usar `type: 1` para notificaciones estándar de PAQUETEX

### Formato de Números
- ✅ Debe incluir código de país (57 para Colombia)
- ✅ Formato: 57XXXXXXXXXX (10 dígitos después del 57)
- ✅ Ejemplo válido: 573002596319
- ❌ No usar +57 (sin el símbolo +)
- ❌ No usar espacios ni guiones

### Rate Limits
- No documentado oficialmente
- Recomendación: No más de 10 SMS por segundo
- Para envíos masivos, usar endpoint `/v2/sms/multiple`

---

## 💻 Ejemplos de Uso

### Ejemplo 1: Envío Simple
```python
import asyncio
import httpx

async def main():
    # 1. Autenticar
    async with httpx.AsyncClient() as client:
        auth_response = await client.post(
            "https://api.liwa.co/v2/auth/login",
            json={
                "account": "00486396309",
                "password": "6fEuRnd*$#NfFAS"
            }
        )
        token = auth_response.json()["token"]
        
        # 2. Enviar SMS
        sms_response = await client.post(
            "https://api.liwa.co/v2/sms/single",
            headers={
                "Authorization": f"Bearer {token}",
                "API-KEY": "c52d8399ac63a24563ee8a967bafffc6cb8d8dfa",
                "Content-Type": "application/json"
            },
            json={
                "number": "573002596319",
                "message": "Hola desde PAQUETEX",
                "type": 1
            }
        )
        
        result = sms_response.json()
        print(f"SMS enviado: {result}")

asyncio.run(main())
```

### Ejemplo 2: Envío con Caché de Token
```python
class LiwaClient:
    def __init__(self):
        self.token = None
        self.token_expires_at = None
    
    async def get_token(self):
        # Usar token cacheado si aún es válido
        if self.token and datetime.now() < self.token_expires_at:
            return self.token
        
        # Obtener nuevo token
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.liwa.co/v2/auth/login",
                json={
                    "account": "00486396309",
                    "password": "6fEuRnd*$#NfFAS"
                }
            )
            self.token = response.json()["token"]
            self.token_expires_at = datetime.now() + timedelta(hours=23)
            return self.token
    
    async def send_sms(self, phone, message):
        token = await self.get_token()
        
        if not phone.startswith("57"):
            phone = f"57{phone}"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.liwa.co/v2/sms/single",
                headers={
                    "Authorization": f"Bearer {token}",
                    "API-KEY": "c52d8399ac63a24563ee8a967bafffc6cb8d8dfa",
                    "Content-Type": "application/json"
                },
                json={
                    "number": phone,
                    "message": message,
                    "type": 1
                }
            )
            return response.json()
```

### Ejemplo 3: Envío Masivo
```python
async def send_notifications(recipients):
    # recipients = [("3002596319", "Mensaje 1"), ("3008103849", "Mensaje 2")]
    
    # Autenticar
    token = await authenticate()
    
    # Preparar mensajes
    messages = []
    for phone, message in recipients:
        messages.append({
            "codeCountry": "57",
            "number": phone.replace("57", ""),
            "message": message,
            "type": 1
        })
    
    # Enviar
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.liwa.co/v2/sms/multiple",
            headers={
                "Authorization": f"Bearer {token}",
                "API-KEY": "c52d8399ac63a24563ee8a967bafffc6cb8d8dfa",
                "Content-Type": "application/json"
            },
            json={
                "name": f"Campaña {datetime.now().strftime('%Y%m%d_%H%M')}",
                "sendingDate": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "messages": messages
            }
        )
        return response.json()
```

---

## 🔧 Troubleshooting

### Problema: Token Expirado
**Síntoma:** Error 401 Unauthorized  
**Causa:** El token JWT tiene 24 horas de validez  
**Solución:** Obtener nuevo token con `/v2/auth/login`

### Problema: Caracteres Inválidos
**Síntoma:** "Lo sentimos el mensaje tiene caracteres inválidos"  
**Causa:** Mensaje contiene emojis o caracteres especiales  
**Solución:** Usar solo texto ASCII estándar, sin emojis

### Problema: SMS No Llega
**Verificar:**
1. ✅ Número tiene código de país (57)
2. ✅ Número es válido (10 dígitos)
3. ✅ Hay saldo disponible en la cuenta
4. ✅ Mensaje no tiene caracteres inválidos
5. ✅ Token no ha expirado

### Problema: Error 404
**Síntoma:** Endpoint no encontrado  
**Causa:** URL incorrecta o endpoint no existe  
**Solución:** Verificar que sea `/v2/sms/single` (no `/v2/sms/send`)

### Problema: Error 500
**Síntoma:** Internal Server Error  
**Causa:** Error en el servidor de LIWA o endpoint no implementado  
**Solución:** Verificar formato del request o contactar soporte

---

## 💰 Información de Cuenta

### Datos de la Cuenta PAQUETEX
```
Cuenta: 00486396309
Empresa: PAPYRUS SOLUCIONES INTEGRALES
NIT: 901210008
Tipo: Prepago
```

### Costos
```
Costo por SMS: $0.50 COP
Tipo de facturación: Prepago
Moneda: COP (Pesos Colombianos)
```

### Saldo (Última actualización: 17/11/2025)
```
Saldo: 73,598 créditos
SMS disponibles: ~147,196 mensajes
```

### Consultar Saldo Actual
⚠️ **No disponible por API**

Para consultar el saldo actual:
1. Ir a https://liwa.co/dashboard
2. Iniciar sesión con las credenciales
3. Ver saldo en el panel principal

### Recargar Saldo
1. Contactar a LIWA: soporte@liwa.co
2. O desde el panel web: https://liwa.co/dashboard

---

## 📞 Soporte y Contacto

### LIWA.co
- **Sitio web:** https://liwa.co
- **Email:** soporte@liwa.co
- **Documentación:** https://api.liwa.co/docs
- **Panel:** https://liwa.co/dashboard

### PAQUETEX EL CLUB
- **Empresa:** PAPYRUS SOLUCIONES INTEGRALES
- **Email:** paquetex@papyrus.com.co
- **Teléfono:** 3334004007
- **Dirección:** Cra 91 #54-120, Local 12, Cartagena

---

## 📝 Notas Importantes

1. **Token JWT:** Cachear el token por 23 horas para optimizar llamadas
2. **Formato de números:** Siempre incluir código de país (57)
3. **Caracteres:** Solo ASCII estándar, sin emojis
4. **Longitud:** Máximo 160 caracteres por SMS
5. **Saldo:** Consultar solo desde panel web
6. **Historial:** No disponible por API, usar panel web
7. **Webhooks:** No disponibles, implementar polling si es necesario
8. **Rate limits:** No documentados, usar con moderación

---

## 🔄 Historial de Cambios

### 26/11/2025 - v2.0
- ✅ Descarga de documentación oficial OpenAPI
- ✅ Descubrimiento de endpoint Text2Speech
- ✅ Documentación de método GET alternativo
- ✅ Actualización de límites de caracteres (466)
- ✅ Documentación de tipos de mensaje (1, 2, 3)
- ✅ Confirmación de servidores (producción y staging)
- ✅ Exploración completa de la API
- ✅ Confirmación de endpoints disponibles
- ✅ Documentación de limitaciones

### 17/11/2025 - v1.0
- ✅ Corrección de formato de API
- ✅ Pruebas exitosas de envío
- ✅ Documentación inicial

---

## 📚 Referencias

- **Documentación oficial:** https://apidoc.liwa.co/
- **OpenAPI Specification:** https://apidoc.liwa.co/openapi.json
- **Panel de control:** https://liwa.co/dashboard
- **Términos y condiciones:** https://www.cellvoz.com/wp-content/uploads/2021/03/Terminos-y-Condiciones-022021.pdf
- **Contacto:** contacto@cellvoz.com.co

---

**Documento creado:** 26 de noviembre de 2025  
**Última actualización:** 26 de noviembre de 2025  
**Versión:** 2.0  
**Estado:** ✅ Completo y Verificado con Documentación Oficial
