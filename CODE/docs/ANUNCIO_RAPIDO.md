# Anuncio Rápido de Paquetes

## Descripción

El sistema de **Anuncio Rápido** permite a los clientes registrados anunciar paquetes de forma simplificada, ingresando únicamente su número de teléfono. El sistema automáticamente:

1. Busca al cliente en la base de datos por su teléfono
2. Autocompleta el nombre del cliente
3. Genera un número de guía temporal único
4. Crea el anuncio y envía notificaciones

## Características

### ✅ Ventajas

- **Proceso simplificado**: Solo requiere el número de teléfono
- **Búsqueda automática**: El sistema encuentra al cliente automáticamente
- **Guía temporal**: Se genera un número de guía con formato `TEMP-XXXXXX`
- **Notificaciones automáticas**: Envía SMS y email al cliente
- **Validación en tiempo real**: Verifica el teléfono mientras el usuario escribe

### 📋 Requisitos

- El cliente debe estar previamente registrado en el sistema
- El número de teléfono debe estar en formato válido (+573001234567 o 3001234567)
- El cliente debe aceptar los términos y condiciones

## Acceso

### URL Pública
```
https://staging.jemavi.co/announce-quick
```

### Comparación con Anuncio Normal

| Característica | Anuncio Normal | Anuncio Rápido |
|----------------|----------------|----------------|
| URL | `/announce` | `/announce-quick` |
| Campos requeridos | Nombre, Teléfono, Guía | Solo Teléfono |
| Número de guía | Manual | Automático (TEMP-XXXXXX) |
| Cliente nuevo | Sí | No (solo clientes existentes) |
| Búsqueda automática | No | Sí |

## Flujo de Usuario

### 1. Ingreso de Teléfono
El usuario ingresa su número de teléfono en el campo correspondiente.

```
Formato aceptado:
- +573001234567
- 3001234567
```

### 2. Búsqueda Automática
Después de 500ms de inactividad, el sistema busca automáticamente al cliente:

- **Cliente encontrado**: Muestra el nombre y un mensaje de confirmación ✓
- **Cliente no encontrado**: Muestra advertencia y sugiere usar el formulario completo ⚠

### 3. Confirmación
El usuario acepta los términos y condiciones y hace clic en "Anunciar Paquete".

### 4. Resultado
El sistema:
- Genera un número de guía temporal (ej: `TEMP-A3B7C9`)
- Genera un código de consulta (ej: `X7Y2`)
- Crea el anuncio en la base de datos
- Envía SMS al cliente con los códigos
- Envía email si el cliente tiene correo registrado
- Muestra modal de éxito con los códigos generados

## Endpoints API

### 1. Buscar Cliente por Teléfono

**Endpoint**: `GET /api/customers/search-by-phone`

**Parámetros**:
- `phone` (query): Número de teléfono a buscar

**Respuesta exitosa** (200):
```json
{
  "id": "uuid",
  "full_name": "JUAN PEREZ",
  "display_name": "Juan Perez",
  "phone": "+573001234567",
  "email": "juan@example.com",
  "is_vip": false,
  "total_packages_received": 5
}
```

**Cliente no encontrado** (404):
```json
{
  "detail": "Cliente no encontrado"
}
```

### 2. Crear Anuncio Rápido

**Endpoint**: `POST /api/announcements/quick`

**Body**:
```json
{
  "customer_phone": "+573001234567"
}
```

**Respuesta exitosa** (200):
```json
{
  "success": true,
  "message": "Anuncio creado exitosamente",
  "announcement": {
    "id": "uuid",
    "customer_name": "JUAN PEREZ",
    "customer_phone": "+573001234567",
    "guide_number": "TEMP-A3B7C9",
    "tracking_code": "X7Y2",
    "announced_at": "2025-12-11T10:30:00",
    "status": "pendiente"
  }
}
```

**Errores posibles**:
- 400: Teléfono inválido o cliente no encontrado
- 500: Error al generar códigos únicos

## Implementación Técnica

### Frontend (announce_quick.html)

**Características**:
- Debounce de 500ms en el campo de teléfono
- Loader animado durante la búsqueda
- Validación en tiempo real
- Modal de éxito con códigos generados
- Responsive design

**JavaScript**:
```javascript
// Búsqueda automática con debounce
document.getElementById('customer_phone').addEventListener('input', function(e) {
    clearTimeout(debounceTimer);
    if (phone.length >= 10) {
        debounceTimer = setTimeout(() => {
            searchCustomerByPhone(phone);
        }, 500);
    }
});
```

### Backend (public.py)

**Funciones principales**:

1. **search_customer_by_phone_public**: Busca cliente por teléfono normalizado
2. **create_quick_announcement**: Crea anuncio con guía temporal

**Generación de códigos**:
```python
# Guía temporal: TEMP-XXXXXX (6 caracteres alfanuméricos)
guide_number = f"TEMP-{''.join(random.choice(allowed_chars) for _ in range(6))}"

# Tracking code: XXXX (4 caracteres, sin O ni 0)
allowed_chars = string.ascii_uppercase.replace('O', '') + string.digits.replace('0', '')
tracking_code = ''.join(random.choice(allowed_chars) for _ in range(4))
```

## Notificaciones

### SMS
Se envía automáticamente un SMS al cliente con:
- Número de guía temporal
- Código de consulta
- URL de tracking

### Email
Si el cliente tiene email registrado, se envía un correo con:
- Confirmación del anuncio
- Número de guía y código de consulta
- Enlace directo para consultar el estado

## Casos de Uso

### Caso 1: Cliente Frecuente
Un cliente que ya ha usado el servicio varias veces puede anunciar un nuevo paquete en segundos:
1. Ingresa su teléfono
2. El sistema lo reconoce
3. Acepta términos
4. Recibe confirmación

**Tiempo estimado**: 15-20 segundos

### Caso 2: Cliente Nuevo
Un cliente que nunca ha usado el servicio debe usar el formulario completo (`/announce`):
1. Ingresa nombre, teléfono y número de guía
2. Se crea el cliente en el sistema
3. Se crea el anuncio

### Caso 3: Actualización de Guía
Si el cliente recibe el número de guía real después, un operador puede:
1. Buscar el anuncio por código de tracking
2. Actualizar el número de guía de `TEMP-XXXXXX` a la guía real
3. El sistema mantiene el historial

## Seguridad

- ✅ Validación de formato de teléfono
- ✅ Normalización automática de números
- ✅ Generación de códigos únicos con reintentos
- ✅ Protección contra duplicados
- ✅ Logs de auditoría
- ✅ Manejo de errores robusto

## Mejoras Futuras

1. **Autenticación opcional**: Permitir login rápido con SMS OTP
2. **Historial de anuncios**: Mostrar anuncios previos del cliente
3. **Múltiples paquetes**: Permitir anunciar varios paquetes a la vez
4. **Foto del paquete**: Opción de subir foto desde el móvil
5. **Geolocalización**: Detectar ubicación para optimizar logística

## Soporte

Para problemas o preguntas sobre el sistema de anuncio rápido:
- Email: soporte@jemavi.co
- Teléfono: +57 300 123 4567
- Documentación: https://docs.jemavi.co
