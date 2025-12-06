# 🎯 Portal de Autogestión de Clientes - PAQUETEX

## 📋 Descripción

Portal público donde los clientes pueden acceder a sus datos y gestionar su información de forma segura mediante autenticación por SMS (OTP).

## ✨ Características

- ✅ **Autenticación por SMS**: Código OTP de 6 dígitos válido por 5 minutos
- ✅ **Acceso seguro**: Solo clientes registrados pueden acceder
- ✅ **Edición de datos**: Nombre, email, dirección, edificio (teléfono NO editable)
- ✅ **Historial de paquetes**: Ver últimos 20 paquetes con estados
- ✅ **Sesión temporal**: Token JWT válido por 1 hora
- ✅ **Rate limiting**: Máximo 3 intentos de OTP por hora

## 🚀 Instalación

### 1. Ejecutar migración de base de datos

```bash
cd CODE
python3 -m alembic upgrade head
```

Esto creará la tabla `customer_otps` necesaria para el sistema de verificación.

### 2. Verificar configuración SMS

Asegúrate de tener configuradas las variables de entorno para Liwa.co:

```env
LIWA_API_KEY=tu_api_key
LIWA_ACCOUNT=tu_cuenta
LIWA_PASSWORD=tu_password
LIWA_AUTH_URL=https://api.liwa.co/v2/auth/login
```

### 3. Reiniciar la aplicación

```bash
# Desarrollo
uvicorn src.main:app --reload

# Producción (con Docker)
docker-compose restart
```

## 📱 Uso del Portal

### Para Clientes

1. **Acceder al portal**: `https://tu-dominio.com/customer-portal`
2. **Ingresar teléfono**: El número debe estar registrado en el sistema
3. **Recibir código SMS**: Código de 6 dígitos válido por 5 minutos
4. **Verificar código**: Ingresar el código recibido
5. **Acceder al dashboard**: Ver y editar datos, consultar paquetes

### Flujo de Autenticación

```
┌─────────────────┐
│ Ingresa Teléfono│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ ¿Cliente existe?│
└────────┬────────┘
         │ Sí
         ▼
┌─────────────────┐
│  Envía SMS OTP  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Verifica Código │
└────────┬────────┘
         │ Correcto
         ▼
┌─────────────────┐
│ Genera Token JWT│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Dashboard     │
└─────────────────┘
```

## 🔐 Seguridad

### Rate Limiting
- **3 OTPs por hora** por número de teléfono
- **3 intentos** por código OTP
- Códigos expiran en **5 minutos**

### Tokens JWT
- Válidos por **1 hora**
- Tipo: `customer_portal`
- Almacenados en `localStorage` del navegador

### Campos NO Editables
- ❌ Teléfono (es el identificador único)
- ❌ ID del cliente
- ❌ Fechas de creación/modificación
- ❌ Estadísticas de paquetes

### Campos Editables
- ✅ Nombre y apellido
- ✅ Email
- ✅ Dirección completa
- ✅ Ciudad y departamento
- ✅ Conjunto residencial, torre, apartamento

## 🛠️ API Endpoints

### Públicos (sin autenticación)

#### Solicitar OTP
```http
POST /api/customer-portal/request-otp
Content-Type: application/json

{
  "phone": "+573001234567"
}
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Código de verificación enviado por SMS",
  "expires_in_seconds": 300
}
```

#### Verificar OTP
```http
POST /api/customer-portal/verify-otp
Content-Type: application/json

{
  "phone": "+573001234567",
  "code": "123456"
}
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Verificación exitosa",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Protegidos (requieren token)

#### Obtener mis datos
```http
GET /api/customer-portal/me
Authorization: Bearer {token}
```

#### Actualizar mis datos
```http
PUT /api/customer-portal/me
Authorization: Bearer {token}
Content-Type: application/json

{
  "first_name": "Juan",
  "last_name": "Pérez",
  "email": "juan@example.com",
  "address_street": "Calle 123 #45-67",
  "building_name": "Edificio Central",
  "tower": "A",
  "apartment": "501"
}
```

#### Obtener mis paquetes
```http
GET /api/customer-portal/packages?limit=20
Authorization: Bearer {token}
```

#### Cerrar sesión
```http
POST /api/customer-portal/logout
Authorization: Bearer {token}
```

## 🎨 Vistas HTML

- `/customer-portal` - Página de entrada (solicitar OTP)
- `/customer-portal/verify` - Verificar código OTP
- `/customer-portal/dashboard` - Dashboard del cliente

## 📊 Base de Datos

### Tabla: customer_otps

```sql
CREATE TABLE customer_otps (
    id UUID PRIMARY KEY,
    customer_phone VARCHAR(20) NOT NULL,
    otp_code VARCHAR(6) NOT NULL,
    attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,
    is_verified BOOLEAN DEFAULT FALSE,
    is_expired BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    verified_at TIMESTAMP NULL
);

CREATE INDEX ix_customer_otps_customer_phone ON customer_otps(customer_phone);
```

## 🧪 Testing

### Probar envío de SMS

```python
from app.services.customer_portal_service import CustomerPortalService
from app.schemas.customer_portal import OTPRequest

service = CustomerPortalService()
request = OTPRequest(phone="+573001234567")

# Solicitar OTP
response = await service.request_otp(db, request)
print(response)
```

### Probar verificación

```python
from app.schemas.customer_portal import OTPVerifyRequest

verify_request = OTPVerifyRequest(
    phone="+573001234567",
    code="123456"
)

response = await service.verify_otp(db, verify_request)
print(response.access_token)
```

## 🐛 Troubleshooting

### Error: "Cliente no encontrado"
- Verificar que el cliente existe en la tabla `customers`
- Verificar que el teléfono está normalizado correctamente
- Verificar que `is_active = true`

### Error: "Ha excedido el límite de intentos"
- Esperar 1 hora desde el último intento
- O limpiar registros antiguos en `customer_otps`

### Error: "Código incorrecto"
- Verificar que el código no haya expirado (5 minutos)
- Verificar que no se hayan agotado los 3 intentos
- Solicitar un nuevo código

### SMS no llega
- Verificar configuración de Liwa.co en `.env`
- Revisar logs del servidor: `docker logs paquetex-app`
- Verificar saldo en cuenta de Liwa.co

## 📝 Notas Importantes

1. **Auto-registro**: El portal NO crea clientes nuevos. Los clientes deben ser creados previamente al anunciar paquetes.

2. **Teléfono único**: El teléfono es el identificador único y NO puede ser modificado por el cliente.

3. **Sesiones**: Las sesiones son stateless (JWT). No se almacenan en servidor.

4. **Limpieza**: Los OTPs antiguos deben limpiarse periódicamente (recomendado: cronjob diario).

## 🔄 Mantenimiento

### Limpiar OTPs expirados (ejecutar diariamente)

```sql
DELETE FROM customer_otps 
WHERE created_at < NOW() - INTERVAL '24 hours';
```

O crear un cronjob:

```bash
# Agregar a crontab
0 2 * * * psql -d paquetex -c "DELETE FROM customer_otps WHERE created_at < NOW() - INTERVAL '24 hours';"
```

## 📞 Soporte

Para problemas o preguntas, contactar al equipo de desarrollo.

---

**Versión**: 1.0.0  
**Fecha**: 2025-01-30  
**Autor**: Equipo de Desarrollo PAQUETEX
