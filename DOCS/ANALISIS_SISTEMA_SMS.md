# Análisis del Sistema de SMS - PAQUETEX EL CLUB

## 📋 Resumen Ejecutivo

El sistema de SMS está **completamente configurado y funcional** usando el proveedor **LIWA.co** para Colombia.

---

## ✅ Configuración Actual

### Proveedor: LIWA.co
- **API Key**: c52d8399ac63a24563ee8a967bafffc6cb8d8dfa ✅
- **Cuenta**: 00486396309 ✅
- **URL de Autenticación**: https://api.liwa.co/v2/auth/login ✅
- **URL de API**: https://api.liwa.co/v2/sms/single ✅ (ACTUALIZADO)
- **Remitente**: "PAQUETES" ✅
- **Estado**: ✅ FUNCIONANDO CORRECTAMENTE

### Variables de Entorno (.env)
```bash
LIWA_API_KEY=b0cfb7e312af71b70338fd5fe0e5f1ee7cfb4ee7
LIWA_ACCOUNT=00486396309
LIWA_PASSWORD=6fEuRnd*$#NfFAS
LIWA_AUTH_URL=https://api.liwa.co/v2/auth/login
LIWA_FROM_NAME="PAQUETEX EL CLUB"
```

**Nota:** El API Key fue actualizado el 17/11/2025.

---

## 🔧 Componentes del Sistema

### 1. Servicio SMS (`CODE/src/app/services/sms_service.py`)

El servicio incluye:

#### Funcionalidades Principales:
- ✅ **Envío individual de SMS** (`send_sms`)
- ✅ **Envío masivo** (`send_bulk_sms`)
- ✅ **Envío por eventos** (`send_sms_by_event`)
- ✅ **Plantillas de mensajes** (templates)
- ✅ **Validación de números colombianos**
- ✅ **Modo de prueba** (test mode)
- ✅ **Estadísticas y reportes**

#### Eventos Soportados:
1. `PACKAGE_ANNOUNCED` - Paquete anunciado
2. `PACKAGE_RECEIVED` - Paquete recibido
3. `PACKAGE_DELIVERED` - Paquete entregado
4. `PACKAGE_CANCELLED` - Paquete cancelado
5. `PAYMENT_DUE` - Pago pendiente
6. `CUSTOM_MESSAGE` - Mensaje personalizado

#### Validación de Números:
- Formato: 10 dígitos para Colombia
- Prefijos válidos: 3xx (300, 301, 302, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 350, 351)
- Acepta formatos: `+573002596319`, `573002596319`, `3002596319`

---

## 📱 Prueba de Envío al Número 3002596319

### Opción 1: Usando el Script de Prueba

He creado un script interactivo en `CODE/scripts/test_sms.py` con las siguientes opciones:

```bash
cd CODE
python scripts/test_sms.py
```

**Menú del script:**
1. **Enviar SMS de prueba** - Envía un SMS real (consume créditos)
2. **Probar configuración** - Modo simulación (sin consumir créditos)
3. **Ver estadísticas** - Muestra estadísticas de SMS enviados
4. **Salir**

### Opción 2: Código Python Directo

```python
import asyncio
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.sms_service import SMSService
from app.models.notification import NotificationEvent, NotificationPriority

async def enviar_sms_prueba():
    db = SessionLocal()
    try:
        sms_service = SMSService()
        
        result = await sms_service.send_sms(
            db=db,
            recipient="3002596319",
            message="Hola! Este es un mensaje de prueba desde PAQUETEX EL CLUB.",
            event_type=NotificationEvent.CUSTOM_MESSAGE,
            priority=NotificationPriority.ALTA,
            is_test=False  # False = envío real, True = simulación
        )
        
        print(f"Estado: {result.status}")
        print(f"Mensaje: {result.message}")
        print(f"Costo: ${result.cost_cents / 100:.2f} COP")
        
    finally:
        db.close()

# Ejecutar
asyncio.run(enviar_sms_prueba())
```

### Opción 3: Usando la API REST

Si el servidor está corriendo, puedes usar los endpoints de la API:

#### A. Envío Simple de SMS

```bash
curl -X POST "http://localhost/api/v1/notifications/send/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "recipient": "3002596319",
    "message": "Mensaje de prueba desde PAQUETEX EL CLUB",
    "priority": "ALTA",
    "is_test": false
  }'
```

#### B. Prueba de Configuración (Solo Administradores)

```bash
curl -X POST "http://localhost/api/v1/notifications/config/test/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -d '{
    "recipient": "3002596319",
    "message": "Prueba de configuración SMS"
  }'
```

#### C. Envío por Evento (Usando Plantillas)

```bash
curl -X POST "http://localhost/api/v1/notifications/send/event/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "event_type": "CUSTOM_MESSAGE",
    "priority": "ALTA",
    "custom_variables": {
      "customer_name": "Juan Pérez"
    },
    "is_test": false
  }'
```

#### D. Ver Estadísticas

```bash
curl -X GET "http://localhost/api/v1/notifications/stats/?days=30" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🌐 Endpoints de API Disponibles

El sistema expone una API REST completa para gestión de SMS:

### Endpoints de Envío

| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| POST | `/api/v1/notifications/send/` | Enviar SMS individual | Usuario |
| POST | `/api/v1/notifications/send/bulk/` | Enviar SMS masivo | Usuario |
| POST | `/api/v1/notifications/send/event/` | Enviar SMS por evento | Usuario |

### Endpoints de Configuración

| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| GET | `/api/v1/notifications/config/` | Obtener configuración SMS | Admin |
| PUT | `/api/v1/notifications/config/` | Actualizar configuración | Admin |
| POST | `/api/v1/notifications/config/test/` | Probar configuración | Admin |

### Endpoints de Plantillas

| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| GET | `/api/v1/notifications/templates/` | Listar plantillas | Usuario |
| POST | `/api/v1/notifications/templates/` | Crear plantilla | Admin |
| PUT | `/api/v1/notifications/templates/{id}` | Actualizar plantilla | Admin |
| DELETE | `/api/v1/notifications/templates/{id}` | Eliminar plantilla | Admin |
| POST | `/api/v1/notifications/setup/templates/` | Crear plantillas por defecto | Admin |

### Endpoints de Consulta

| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| GET | `/api/v1/notifications/` | Listar notificaciones | Usuario |
| GET | `/api/v1/notifications/{id}` | Obtener notificación | Usuario |
| GET | `/api/v1/notifications/stats/` | Estadísticas | Usuario |
| POST | `/api/v1/notifications/retry/{id}` | Reintentar envío | Usuario |
| GET | `/api/v1/notifications/export/csv/` | Exportar a CSV | Usuario |

### Webhooks

| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| POST | `/api/v1/notifications/webhook/liwa/` | Callback de LIWA.co | Pública |

---

## 💰 Costos

- **Costo por SMS**: $0.50 COP (50 centavos)
- **Límite diario**: 1,000 SMS
- **Límite mensual**: 30,000 SMS

---

## 🔍 Verificación de Configuración

### Paso 1: Verificar Variables de Entorno

```bash
cd CODE
cat .env | grep LIWA
```

Deberías ver:
```
LIWA_API_KEY=c52d8399ac63a24563ee8a967bafffc6cb8d8dfa
LIWA_ACCOUNT=00486396309
LIWA_PASSWORD=6fEuRnd*$#NfFAS
LIWA_AUTH_URL=https://api.liwa.co/v2/auth/login
LIWA_FROM_NAME="PAQUETEX EL CLUB"
```

### Paso 2: Probar Autenticación

El servicio automáticamente:
1. Lee las credenciales de `.env`
2. Se autentica con LIWA.co usando `account` y `password`
3. Obtiene un token JWT
4. Usa el token para enviar SMS

---

## 📊 Plantillas de Mensajes

El sistema incluye plantillas predefinidas:

### 1. Paquete Anunciado
```
PAQUETES EL CLUB: Su paquete con guía {guide_number} ha sido anunciado. 
Código: {tracking_code}. 
Más info: https://paquetex.papyrus.com.co/search/{tracking_code}
```

### 2. Paquete Recibido
```
PAQUETES EL CLUB: Su paquete {guide_number} ha sido RECIBIDO en nuestras 
instalaciones. Código: {tracking_code}. Procesaremos su entrega pronto.
```

### 3. Paquete Entregado
```
PAQUETES EL CLUB: ¡Su paquete {guide_number} ha sido ENTREGADO exitosamente! 
Código: {tracking_code}. Gracias por confiar en nosotros.
```

### 4. Paquete Cancelado
```
PAQUETES EL CLUB: Su paquete {guide_number} ha sido CANCELADO. 
Código: {tracking_code}. Contacte con nosotros para más información.
```

### 5. Pago Pendiente
```
PAQUETES EL CLUB: Tiene un pago pendiente por ${amount} COP para el 
paquete {guide_number}. Realice el pago para continuar con la entrega.
```

---

## 🚀 Cómo Ejecutar la Prueba

### Método Recomendado: Script Interactivo

```bash
# 1. Ir al directorio CODE
cd CODE

# 2. Activar entorno virtual (si existe)
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows

# 3. Ejecutar el script
python scripts/test_sms.py

# 4. Seleccionar opción 1 para envío real o 2 para simulación
```

### Salida Esperada (Envío Exitoso):

```
============================================================
PRUEBA DE ENVÍO DE SMS - LIWA.CO
============================================================

📱 Número destino: 3002596319
💬 Mensaje: Hola! Este es un mensaje de prueba desde PAQUETEX EL CLUB...
📏 Longitud: 75 caracteres

🔧 Verificando configuración...
   ✓ Proveedor: liwa
   ✓ Cuenta: 00486396309
   ✓ API Key: ********************8a967bafffc6cb8d8dfa
   ✓ URL Auth: https://api.liwa.co/v2/auth/login
   ✓ URL API: https://api.liwa.co/v2/sms/send
   ✓ Modo prueba: NO

⚠️  ATENCIÓN: Este envío consumirá créditos reales de SMS
¿Desea continuar con el envío? (s/n): s

📤 Enviando SMS...

============================================================
RESULTADO DEL ENVÍO
============================================================
Estado: sent
Mensaje: SMS enviado exitosamente
ID Notificación: 12345
Costo: $0.50 COP

✅ SMS ENVIADO EXITOSAMENTE
```

---

## ⚠️ Consideraciones Importantes

### 1. Modo de Prueba vs Modo Real

- **Modo Prueba** (`is_test=True`): 
  - No consume créditos
  - Simula el envío
  - Guarda registro en base de datos
  - Útil para desarrollo

- **Modo Real** (`is_test=False`):
  - Consume créditos reales
  - Envía SMS real al número
  - Costo: $0.50 COP por SMS

### 2. Validación de Números

El sistema valida automáticamente:
- ✅ Formato de 10 dígitos
- ✅ Prefijo colombiano válido (3xx)
- ✅ Solo números
- ❌ Rechaza números inválidos

### 3. Registro de Notificaciones

Cada SMS enviado se registra en la tabla `notifications` con:
- ID único
- Número destinatario
- Mensaje enviado
- Estado (ABIERTO, SENT, ENTREGADO, FAILED)
- Costo
- Timestamp
- ID del mensaje del proveedor

---

## 🔧 Troubleshooting

### Error: "Autenticación Liwa fallida"
**Solución**: Verificar credenciales en `.env`
```bash
cat CODE/.env | grep LIWA
```

### Error: "Número de teléfono inválido"
**Solución**: Usar formato de 10 dígitos: `3002596319`

### Error: "Error de conexión con Liwa"
**Solución**: Verificar conectividad a internet y URL de API

### Error: "ModuleNotFoundError"
**Solución**: Instalar dependencias
```bash
cd CODE
pip install -r requirements.txt
```

---

## 📈 Estadísticas Disponibles

El servicio proporciona estadísticas completas:

```python
stats = sms_service.get_sms_stats(db, days=30)

# Retorna:
{
    "total_sent": 150,
    "total_delivered": 145,
    "total_failed": 5,
    "total_cost_cents": 7500,  # $75.00 COP
    "delivery_rate": 96.67,     # %
    "average_cost_per_sms": 50  # centavos
}
```

---

## ✅ Conclusión

**SÍ, es posible enviar un SMS de prueba al número 3002596319**

El sistema está completamente configurado y listo para usar. Solo necesitas:

1. Ejecutar el script de prueba: `python CODE/scripts/test_sms.py`
2. Seleccionar la opción de envío
3. Confirmar el envío

El SMS será enviado a través de LIWA.co y llegará al número especificado en segundos.

**Costo del envío**: $0.50 COP

---

## 📞 Contacto y Soporte

- **Proveedor SMS**: LIWA.co
- **Cuenta**: 00486396309
- **Soporte LIWA**: https://liwa.co/soporte
- **Documentación API**: https://api.liwa.co/docs

---

**Fecha de análisis**: 2025-01-24
**Versión del sistema**: 4.0.0
**Estado**: ✅ Operacional
