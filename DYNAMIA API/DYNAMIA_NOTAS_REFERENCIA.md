# Notas de Referencia - Integración DynamiaERP

## Resumen Ejecutivo

La API de DynamiaERP proporciona 144 endpoints organizados en 13 categorías para gestión completa de ERP. La integración con el sistema de paquetería permitirá facturación electrónica automática, sincronización de clientes y gestión de inventario.

## Endpoints Críticos para Paquetería

### 1. Facturación Electrónica (Prioridad Alta)

**Crear Factura Electrónica:**
```
POST /api/ventas/facturaElectronica
```
- Genera factura electrónica y la envía a DIAN
- Retorna CUFE (Código Único de Factura Electrónica)
- Genera PDF automáticamente

**Consultar Estado:**
```
GET /api/ventas/facturaElectronica/{cufe}
```
- Verificar si fue aprobada/rechazada por DIAN
- Obtener detalles completos de la factura

**Enviar por Email:**
```
POST /api/ventas/facturaElectronica/{cufe}/enviarEmail
```
- Enviar factura al cliente automáticamente
- Soporta múltiples destinatarios

### 2. Gestión de Clientes (Prioridad Alta)

**Crear Cliente:**
```
POST /api/ventas/clientes
```

**Actualizar Cliente:**
```
PUT /api/ventas/clientes/{id}
```

**Consultar Cliente:**
```
GET /api/ventas/clientes/{id}
```

### 3. Ventas (Prioridad Media)

**Crear Venta:**
```
POST /api/ventas
```
- Crear venta sin facturación electrónica
- Útil para ventas internas o borradores

### 4. Inventario (Prioridad Media)

**Consultar Productos:**
```
GET /api/inventario/items
```

**Consultar Existencias:**
```
GET /api/inventario/items/existencias
```

### 5. Webhooks (Prioridad Baja - Futuro)

**Configurar Webhook:**
```
POST /api/webhooks
```
- Recibir notificaciones automáticas
- Eventos: FACTURA_APROBADA, FACTURA_RECHAZADA, etc.

## Modelos de Datos Clave

### DocumentoElectronico (Factura)

```json
{
  "tipo": "FACTURA",
  "fecha": "2026-01-13",
  "cliente": {
    "identificacion": "123456789",
    "nombre": "Cliente Ejemplo",
    "email": "cliente@example.com"
  },
  "detalles": [
    {
      "descripcion": "Paquete Premium",
      "cantidad": 1,
      "precioUnitario": 100000,
      "impuesto": 19
    }
  ],
  "formasPagos": [
    {
      "formaPago": "EFECTIVO",
      "valor": 119000
    }
  ],
  "observaciones": "Venta de paquete"
}
```

### Cliente

```json
{
  "accountId": 123,
  "identificacion": "123456789",
  "tipoIdentificacionId": 1,
  "nombres": "Juan",
  "apellidos": "Pérez",
  "razonSocial": "Empresa XYZ",
  "datosContacto": {
    "email": "juan@example.com",
    "telefono": "3001234567",
    "direccion": "Calle 123 #45-67"
  }
}
```

## Flujo de Integración Propuesto

### Fase 1: Facturación Básica (Inmediato)
1. ✅ Analizar API completada
2. ⬜ Probar autenticación con credenciales
3. ⬜ Crear servicio de integración básico
4. ⬜ Integrar en endpoint de ventas
5. ⬜ Generar factura al vender paquete
6. ⬜ Enviar factura por email automáticamente

### Fase 2: Sincronización de Clientes (Corto Plazo)
1. ⬜ Agregar campos a tabla customers
2. ⬜ Sincronizar clientes existentes
3. ⬜ Auto-sincronizar nuevos clientes
4. ⬜ Actualización bidireccional

### Fase 3: Gestión de Inventario (Mediano Plazo)
1. ⬜ Sincronizar paquetes como productos
2. ⬜ Actualizar existencias automáticamente
3. ⬜ Alertas de inventario bajo

### Fase 4: Webhooks y Automatización (Largo Plazo)
1. ⬜ Configurar webhooks
2. ⬜ Procesar eventos automáticamente
3. ⬜ Notificaciones en tiempo real

## Cambios Necesarios en BD

### Tabla customers
```sql
ALTER TABLE customers 
ADD COLUMN dynamia_customer_id INTEGER,
ADD COLUMN last_sync_date TIMESTAMP,
ADD COLUMN sync_status VARCHAR(50) DEFAULT 'pending';

CREATE INDEX idx_customers_dynamia_id ON customers(dynamia_customer_id);
```

### Tabla sales
```sql
ALTER TABLE sales
ADD COLUMN dynamia_sale_id INTEGER,
ADD COLUMN cufe VARCHAR(255) UNIQUE,
ADD COLUMN invoice_pdf TEXT,
ADD COLUMN invoice_status VARCHAR(50) DEFAULT 'pending',
ADD COLUMN invoice_sent_date TIMESTAMP,
ADD COLUMN invoice_error TEXT;

CREATE INDEX idx_sales_cufe ON sales(cufe);
CREATE INDEX idx_sales_dynamia_id ON sales(dynamia_sale_id);
```

### Nueva tabla: dynamia_sync_log
```sql
CREATE TABLE dynamia_sync_log (
    id SERIAL PRIMARY KEY,
    entity_type VARCHAR(50) NOT NULL,
    entity_id INTEGER NOT NULL,
    operation VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    request_data JSONB,
    response_data JSONB,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sync_log_entity ON dynamia_sync_log(entity_type, entity_id);
CREATE INDEX idx_sync_log_status ON dynamia_sync_log(status);
```

## Configuración de Variables de Entorno

Agregar a `CODE/.env`:

```env
# DynamiaERP Integration
DYNAMIA_API_URL=https://api.dynamiaerp.co
DYNAMIA_ACCOUNT=papyrus
DYNAMIA_USERNAME=jesus
DYNAMIA_PASSWORD=il1111
DYNAMIA_TOKEN=tk80fddb468262bcf5734f1c25f0724c6c6edcbee12cbff8fbde9948879e03650e
DYNAMIA_ENABLED=true
DYNAMIA_AUTO_INVOICE=true
DYNAMIA_AUTO_SYNC_CUSTOMERS=true
```

## Mapeo de Datos

### Tipos de Identificación
- 1 = Cédula de Ciudadanía (CC)
- 2 = NIT
- 3 = Cédula de Extranjería (CE)
- 4 = Pasaporte

### Formas de Pago
- EFECTIVO
- TARJETA_CREDITO
- TARJETA_DEBITO
- TRANSFERENCIA
- CHEQUE

### Estados de Factura
- PENDIENTE - Creada pero no enviada
- ENVIADA - Enviada a DIAN
- APROBADA - Aprobada por DIAN
- RECHAZADA - Rechazada por DIAN
- ANULADA - Anulada

## Manejo de Errores

### Errores Comunes

1. **401 Unauthorized**
   - Token expirado o inválido
   - Solución: Re-autenticar

2. **400 Bad Request**
   - Datos inválidos en el request
   - Solución: Validar datos antes de enviar

3. **404 Not Found**
   - Recurso no existe
   - Solución: Verificar IDs

4. **500 Internal Server Error**
   - Error en servidor de DynamiaERP
   - Solución: Reintentar después de un tiempo

### Estrategia de Reintentos

```python
# Configuración recomendada
MAX_RETRIES = 3
RETRY_DELAY = 5  # segundos
BACKOFF_FACTOR = 2  # exponencial

# Reintentar solo en errores 5xx y timeouts
RETRY_STATUS_CODES = [500, 502, 503, 504]
```

## Monitoreo y Logs

### Métricas Importantes
- Tasa de éxito de facturación
- Tiempo promedio de respuesta
- Facturas pendientes de sincronización
- Errores por tipo

### Logs Críticos
- Todas las llamadas a la API
- Errores de sincronización
- Facturas rechazadas
- Cambios en estado de facturas

## Seguridad

### Mejores Prácticas
1. ✅ Credenciales en variables de entorno
2. ✅ Usar HTTPS siempre
3. ⬜ Implementar rate limiting
4. ⬜ Validar webhooks con firma
5. ⬜ Encriptar datos sensibles en BD
6. ⬜ Auditoría de todas las operaciones

## Testing

### Casos de Prueba Prioritarios

1. **Autenticación**
   - Login exitoso
   - Token inválido
   - Token expirado

2. **Facturación**
   - Crear factura simple
   - Factura con múltiples items
   - Factura con descuentos
   - Factura con diferentes formas de pago
   - Envío de email

3. **Clientes**
   - Crear cliente persona natural
   - Crear cliente empresa
   - Actualizar cliente
   - Cliente duplicado

4. **Manejo de Errores**
   - Red no disponible
   - Timeout
   - Datos inválidos
   - Servidor caído

## Recursos

- **Documentación:** `CODE/docs/ANALISIS_API_DYNAMIAERP.md`
- **Script de Prueba:** `CODE/scripts/test_dynamia_api.py`
- **Plan de Integración:** `CODE/docs/INTEGRACION_DYNAMIA_PAQUETERIA.md`
- **Credenciales:** `CODE/docs/DYNAMIA_CREDENCIALES.md`

## Contacto Soporte DynamiaERP

- **Email:** devteam@dynamiasoluciones.com
- **Términos:** https://www.dynamiaerp.co/terminos-y-condiciones/

## Próximos Pasos Inmediatos

1. ✅ Documentación completada
2. ⬜ Probar conexión con credenciales reales
3. ⬜ Obtener accountId de la cuenta papyrus
4. ⬜ Crear servicio de integración
5. ⬜ Implementar facturación en endpoint de ventas
6. ⬜ Pruebas en ambiente de desarrollo
7. ⬜ Desplegar a producción

---

**Última actualización:** 2026-01-13  
**Responsable:** Sistema de Paquetería Papyrus
