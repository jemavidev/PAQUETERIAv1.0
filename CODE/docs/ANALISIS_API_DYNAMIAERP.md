# Análisis de la API de DynamiaERP

**URL Base:** http://api.pos.dynamiaerp.co/swagger-ui/index.html  
**Versión:** 2  
**Contacto:** devteam@dynamiasoluciones.com

## Resumen Ejecutivo

La API de DynamiaERP es una API REST completa que proporciona 144 endpoints organizados en 13 categorías principales. Está diseñada para conectar sistemas externos con el ERP Dynamia, cubriendo operaciones de ventas, facturación electrónica, inventario, contabilidad, restaurante y más.

## Servidores Disponibles

- **Producción:** https://api.dynamiaerp.co
- **Desarrollo Local:** http://api.localhost.com:8282

## Categorías de Endpoints

### 1. Facturación Electrónica (13 endpoints)
Operaciones para enviar y consultar facturas electrónicas.

**Endpoints principales:**
- `POST /api/ventas/facturaElectronica` - Enviar documento electrónico
- `GET /api/ventas/facturaElectronica/{cufe}` - Consultar factura por CUFE
- `GET /api/ventas/facturaElectronica/{cufe}/pdf` - Exportar PDF de factura
- `POST /api/ventas/facturaElectronica/{cufe}/notaCredito` - Enviar nota crédito
- `POST /api/ventas/facturaElectronica/{cufe}/anular` - Anular factura electrónica
- `GET /api/ventas/facturaElectronica/{cufe}/enviarEmail` - Enviar factura por email
- `POST /api/ventas/facturaElectronica/{cufe}/enviarEmail` - Enviar con datos personalizados
- `GET /api/ventas/facturaElectronica/{cufe}/reenviar` - Reenviar factura
- `GET /api/ventas/facturaElectronica/{cufe}/print` - Imprimir factura
- `GET /api/ventas/facturaElectronica/status` - Estado del emisor
- `GET /api/ventas/face/reenviar-pendientes` - Reenviar facturas pendientes

### 2. Ventas (23 endpoints)
Operaciones sobre ventas y clientes.

**Endpoints principales:**
- `POST /api/ventas` - Crear nueva venta
- `GET /api/ventas/{id}` - Obtener venta por ID
- `GET /api/ventas/{id}/print` - Imprimir venta
- `GET /api/ventas/clientes` - Listar clientes
- `POST /api/ventas/clientes` - Crear cliente
- `GET /api/ventas/clientes/{id}` - Obtener cliente
- `PUT /api/ventas/clientes/{id}` - Actualizar cliente
- `GET /api/ventas/vendedor/{id}` - Obtener vendedor
- `PUT /api/ventas/vendedor/{id}` - Actualizar vendedor
- `POST /api/ventas/vendedor` - Crear vendedor

### 3. VentasPOS (11 endpoints)
Operaciones sobre puntos de venta.

**Endpoints principales:**
- `POST /api/ventas/pos/{uuid}/venta` - Crear venta en POS
- `GET /api/ventas/pos/{uuid}` - Obtener información del POS
- `GET /api/ventas/pos/{uuid}/estado-caja` - Estado de caja
- `GET /api/ventas/pos/{uuid}/cerrar-caja` - Cerrar caja
- `GET /api/ventas/pos/{uuid}/template.xml` - Obtener template XML

### 4. Inventario (12 endpoints)
Gestión de productos y existencias.

**Endpoints principales:**
- `GET /api/inventario/items` - Listar productos
- `GET /api/inventario/items/ultimos` - Últimos productos creados
- `GET /api/inventario/items/existencias` - Consultar existencias
- `GET /api/inventario/items/tipos` - Tipos de items
- `GET /api/inventario/bodegas` - Listar bodegas
- `GET /api/inventario/marcas` - Listar marcas
- `GET /api/inventario/lineas` - Listar líneas de productos
- `GET /api/inventario/fabricantes` - Listar fabricantes
- `GET /api/inventario/presentaciones` - Listar presentaciones
- `GET /api/inventario/presentaciones/grupos` - Grupos de presentaciones
- `POST /api/inventario/importar` - Importar inventario
- `POST /api/inventario/importar/lineas` - Importar líneas

### 5. Contabilidad (7 endpoints)
Gestión de elementos contables.

**Endpoints principales:**
- `GET /api/contabilidad/comprobantes` - Listar comprobantes con filtros
- `POST /api/contabilidad/comprobantes` - Crear comprobante contable
- `GET /api/contabilidad/comprobantes/hoy` - Comprobantes del día
- `GET /api/contabilidad/plan-cuentas` - Plan de cuentas contables
- `GET /api/contabilidad/fuentes` - Fuentes contables

### 6. Restaurante (7 endpoints)
Operaciones básicas de restaurante.

**Endpoints principales:**
- `GET /api/restaurante/mesas` - Listar mesas
- `GET /api/restaurante/mesas/disponibles` - Mesas disponibles
- `GET /api/restaurante/meseros` - Listar meseros
- `GET /api/restaurante/configuracion` - Configuración del restaurante
- `GET /api/restaurante/motivos-anulacion` - Motivos de anulación

### 7. RestauranteOrdenMesa (13 endpoints)
Operaciones sobre órdenes de mesa.

**Endpoints principales:**
- `POST /api/restaurante/ordenes/abrir-mesa` - Abrir mesa
- `POST /api/restaurante/ordenes/{id}/detalles` - Agregar items a orden
- `GET /api/restaurante/ordenes/{id}/detalles` - Obtener detalles de orden
- `PUT /api/restaurante/ordenes/{id}/finalizar` - Finalizar orden
- `PUT /api/restaurante/ordenes/{id}/cerrar` - Cerrar orden

### 8. NotasElectronicas (3 endpoints)
Envío de notas crédito y débito electrónicas.

**Endpoints principales:**
- `POST /api/notasElectronica/notaCredito` - Enviar nota crédito
- `POST /api/notasElectronica/notaDebito` - Enviar nota débito
- `GET /api/notasElectronica/reenviar-pendientes` - Reenviar pendientes

### 9. Webhooks (7 endpoints)
Gestión de webhooks.

**Endpoints principales:**
- `GET /api/webhooks` - Listar webhooks
- `POST /api/webhooks` - Crear webhook
- `PUT /api/webhooks/{id}` - Actualizar webhook
- `DELETE /api/webhooks/{id}` - Eliminar webhook

### 10. Seguridad (7 endpoints)
Consulta de usuarios y roles.

**Endpoints principales:**
- `POST /api/seguridad/gettoken` - Obtener token de autenticación
- `GET /api/seguridad/usuarios` - Listar usuarios
- `GET /api/seguridad/usuarios/{id}` - Obtener usuario
- `GET /api/seguridad/usuarios/{id}/roles` - Roles del usuario
- `GET /api/seguridad/usuarios/{id}/permisos` - Permisos del usuario

### 11. VentaQuery (1 endpoint)
Consultas personalizadas para ventas.

**Endpoint:**
- `POST /api/ventas/query` - Consulta con campos y filtros específicos

### 12. VentasNotificaciones (2 endpoints)
Notificaciones de ventas realizadas.

**Endpoints:**
- `GET /api/ventas/notificaciones/ventas/hoy` - Ventas de hoy
- `GET /api/ventas/notificaciones/ventas/ayer` - Ventas de ayer

### 13. Notifications (3 endpoints)
Envío de notificaciones a usuarios.

**Endpoints:**
- `GET /api/notifications` - Listar notificaciones
- `POST /api/notifications` - Crear notificación
- `GET /api/notifications/count` - Contar notificaciones

---

## Modelos de Datos Principales

### DocumentoElectronico
Modelo principal para facturación electrónica.

**Propiedades clave:**
- `id`, `numero`, `tipo`, `consecutivo`, `prefijo`
- `cufe` - Código único de factura electrónica
- `fecha`, `fechaEnvio`, `fechaVencimiento`
- `sucursal`, `centroCosto`
- `cliente` (ClienteDocElectronico)
- `proveedor` (ProveedorDocElectronico)
- `vendedor` (VendedorDocElectronico)
- `detalles` (array de DetalleDocumentoElectronico)
- `totales` (Totales)
- `totalImpuestos` (array de TotalImpuesto)
- `totalRetenciones` (array de TotalRetencion)
- `tipoDoc`, `tipoNotaCredito`, `tipoNotaDebito`
- `pdf` - PDF en base64
- `emailsAdicionales` (array)
- `formasPagos` (array de FormaPago)
- `procesarPago` (boolean)
- `estado` (EstadoDocumento)
- `resolucion` (ResolucionDocumento)
- `descuentosGlobales` (array de Descuento)
- `moneda`
- `webhookURL`
- Campos extra: `extra0` a `extra9`

### Venta
Modelo completo de venta.

**Propiedades clave:**
- `id`, `uuid`, `numero`, `anio`, `prefijo`, `consecutivo`
- `accountId` (requerido)
- `tipo` (TipoVenta - requerido)
- `encabezado` (EncabezadoVenta - requerido)
- `estado` (requerido)
- `cliente` (Cliente - requerido)
- `sucursalId` (requerido)
- `vendedor` (Vendedor - requerido)
- `detalles` (array de DetalleVenta)
- `impuestos` (array de ImpuestoVenta)
- `descuentos` (array de DescuentoVenta)
- `retenciones` (array de RetencionVenta)
- Totales: `subtotal`, `totalGravado`, `totalExentoImpuestos`, `totalImpuestos`, `totalDescuentos`, `total`
- `costoTotal`, `totalBaseGravable`
- `pago` (Pago)
- `fechaProgramadoPago`, `fechaVencimiento`, `fechaEntrega`
- `observaciones`, `observacionesInternas`, `observacionesEmail`
- `domicilio` (boolean), `valorEnvio`
- `cufe`, `contenidoQR`, `docUuid`
- `faceEnviada`, `faceRechazada` (boolean)
- `linkPago`
- Campos extra: `extra0` a `extra9`
- `ordenCompraCliente`
- `centroCostoId`, `bodegaId`, `cajaId`
- `moneda`, `trm`
- `facturaElectronica` (boolean)

### VentaDTO
Versión simplificada de Venta para transferencia de datos.

**Propiedades clave:**
- `id`, `uuid`, `numero`, `estado`
- `tipoVenta`, `tipoVentaId`
- `clienteId`, `terceroId`, `vendedorId`
- `datosCliente` (ClienteDTO)
- `vendedor`, `cliente`, `identificacionCliente`
- `detalles` (array de DetalleVentaDTO)
- `pago` (PagoVentaDTO)
- Totales: `subtotal`, `totalImpuestos`, `totalDescuentos`, `total`
- `cufe`, `contenidoQR`, `docUuid`
- `faceEnviada`, `faceRechazada`
- `data` (object) - Datos adicionales

### Cliente
Información completa del cliente.

**Propiedades clave:**
- `id`, `codigo`, `identificacion`
- `accountId` (requerido)
- `tipoIdentificacionId` (requerido)
- `nombres`, `apellidos`, `razonSocial`
- `terceroId`, `grupoTerceroId`
- `grupo` (GrupoCliente)
- `datosContacto` (ContactInfo)
- `ciudad` (Ciudad), `localidad`, `barrio` (Barrio)
- `vendedorAsignado` (Vendedor)
- `ventasBloqueadas` (boolean), `motivoBloqueo`
- `impuestosExcluidos` (boolean)
- `tipoPrecioVenta`
- `descuento`, `tipoDescuento`
- `contacto`, `telefonoContacto`, `emailContacto`
- `puntosAcumulados`, `puntosUsados`, `puntosDisponibles`
- `responsabilidades`
- `cuentaContable`, `esquemaImpuesto`
- `prospecto` (boolean)
- `noEnviarEmail` (boolean)

### EmailDTO
Para envío de emails personalizados.

**Propiedades:**
- `emails` (array) - Lista de correos electrónicos
- `pdf` (string) - PDF en base64

### Webhook
Configuración de webhooks.

**Propiedades:**
- `id`, `accountId` (requerido)
- `targetUrl` (requerido) - URL destino
- `eventType` (requerido) - Tipo de evento
- `active` (boolean) - Activo/Inactivo
- `alias` - Nombre descriptivo
- `authorization` - Token de autorización
- `lastTriggered` - Última ejecución
- `triggerCount` - Contador de ejecuciones

---

## Esquemas Disponibles (163 total)

La API proporciona 163 esquemas de datos diferentes. Los más relevantes incluyen:

**Facturación y Ventas:**
- DocumentoElectronico, Venta, VentaDTO, DetalleVenta, DetalleVentaDTO
- Cliente, ClienteDTO, Vendedor, VendedorDTO
- TipoVenta, EncabezadoVenta, EstadoDocumento
- ImpuestoVenta, DescuentoVenta, RetencionVenta
- Pago, PagoVentaDTO, DetallePago
- FormaPago, Totales, TotalImpuesto, TotalRetencion

**Inventario:**
- ItemInventario, LineaInventario, SubitemInventario
- Presentacion, GrupoPresentacion
- Marca, Fabricante, Bodega
- TipoItemInventario, EstadoItemInventario
- ExistenciasDTO

**Contabilidad:**
- ComprobanteContable, ComprobanteContableDTO
- DetalleComprobanteContable
- CuentaContable, CuentaContableDTO
- FuenteContable, CategoriaContable
- TerceroContableDTO

**Restaurante:**
- OrdenMesa, DetalleOrdenMesa
- Mesa, MesaDTO, Mesero
- AmbienteMesa, ConfiguracionRestaurante
- MotivoAnulacion, Comanda

**Otros:**
- Usuario, Perfil, Permiso
- Webhook, WebhookEvent
- Notification, GlobalMessage
- EmpresaDTO, SucursalDTO
- Ciudad, Barrio, ContactInfo

---

## Autenticación

La API utiliza autenticación basada en tokens:

**Endpoint de autenticación:**
```
POST /api/seguridad/gettoken
```

**Request Body (TokenRequest):**
```json
{
  "username": "usuario",
  "password": "contraseña"
}
```

**Response (TokenResponse):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expiresIn": 3600,
  "tokenType": "Bearer"
}
```

El token debe incluirse en las peticiones subsecuentes:
```
Authorization: Bearer {token}
```

---

## Casos de Uso Comunes

### 1. Crear y Enviar Factura Electrónica

```
POST /api/ventas/facturaElectronica
Content-Type: application/json
Authorization: Bearer {token}

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
      "descripcion": "Producto 1",
      "cantidad": 2,
      "precioUnitario": 50000,
      "impuesto": 19
    }
  ],
  "formasPagos": [
    {
      "formaPago": "EFECTIVO",
      "valor": 119000
    }
  ]
}
```

### 2. Consultar Factura por CUFE

```
GET /api/ventas/facturaElectronica/{cufe}
Authorization: Bearer {token}
```

### 3. Enviar Factura por Email

```
POST /api/ventas/facturaElectronica/{cufe}/enviarEmail
Content-Type: application/json
Authorization: Bearer {token}

{
  "emails": ["cliente@example.com", "copia@example.com"],
  "pdf": "base64_encoded_pdf_optional"
}
```

### 4. Crear Venta

```
POST /api/ventas
Content-Type: application/json
Authorization: Bearer {token}

{
  "accountId": 123,
  "tipo": {
    "id": 1,
    "nombre": "FACTURA"
  },
  "encabezado": {
    "resolucion": "18760000001",
    "prefijo": "FV"
  },
  "estado": "ACTIVA",
  "numero": "FV-001",
  "anio": 2026,
  "cliente": {
    "id": 456,
    "identificacion": "123456789"
  },
  "sucursalId": 1,
  "vendedor": {
    "id": 789
  },
  "detalles": [
    {
      "producto": {
        "id": 100
      },
      "cantidad": 2,
      "precio": 50000
    }
  ]
}
```

### 5. Consultar Existencias de Inventario

```
GET /api/inventario/items/existencias?bodegaId=1&itemId=100
Authorization: Bearer {token}
```

### 6. Crear Cliente

```
POST /api/ventas/clientes
Content-Type: application/json
Authorization: Bearer {token}

{
  "accountId": 123,
  "identificacion": "987654321",
  "tipoIdentificacionId": 1,
  "nombres": "Juan",
  "apellidos": "Pérez",
  "datosContacto": {
    "email": "juan.perez@example.com",
    "telefono": "3001234567",
    "direccion": "Calle 123 #45-67"
  }
}
```

### 7. Configurar Webhook

```
POST /api/webhooks
Content-Type: application/json
Authorization: Bearer {token}

{
  "accountId": 123,
  "targetUrl": "https://mi-sistema.com/webhook/dynamia",
  "eventType": "VENTA_CREADA",
  "active": true,
  "alias": "Notificación de ventas",
  "authorization": "Bearer mi-token-secreto"
}
```

---

## Integración con Sistema de Paquetería

### Endpoints Relevantes para el Sistema

Para integrar con el sistema de paquetería actual, los endpoints más relevantes son:

1. **Facturación Electrónica:**
   - Enviar facturas electrónicas de paquetes
   - Consultar estado de facturas
   - Enviar facturas por email a clientes

2. **Ventas:**
   - Crear ventas de paquetes
   - Consultar ventas realizadas
   - Gestionar clientes

3. **Clientes:**
   - Sincronizar información de clientes
   - Actualizar datos de contacto
   - Gestionar puntos de fidelización

4. **Inventario:**
   - Consultar disponibilidad de paquetes
   - Actualizar existencias
   - Gestionar productos/servicios

5. **Webhooks:**
   - Recibir notificaciones de eventos
   - Sincronización automática

### Flujo de Integración Propuesto

1. **Autenticación:**
   - Obtener token al iniciar la aplicación
   - Renovar token antes de expiración

2. **Sincronización de Clientes:**
   - Al crear cliente en sistema de paquetería → crear en DynamiaERP
   - Mantener sincronización bidireccional

3. **Creación de Ventas:**
   - Al vender paquete → crear venta en DynamiaERP
   - Generar factura electrónica automáticamente

4. **Facturación:**
   - Enviar documento electrónico a DIAN
   - Obtener CUFE y PDF
   - Enviar factura por email al cliente

5. **Webhooks:**
   - Configurar webhook para recibir actualizaciones
   - Procesar eventos de facturas aprobadas/rechazadas

---

## Notas Importantes

1. **Autenticación:** Todos los endpoints requieren autenticación mediante token Bearer.

2. **AccountId:** La mayoría de operaciones requieren el `accountId` que identifica la cuenta/empresa en DynamiaERP.

3. **CUFE:** El Código Único de Factura Electrónica es el identificador principal para operaciones de facturación electrónica.

4. **Campos Extra:** Muchos modelos incluyen campos `extra0` a `extra9` para datos personalizados.

5. **Webhooks:** Permiten recibir notificaciones en tiempo real de eventos del sistema.

6. **Paginación:** Algunos endpoints de listado soportan parámetros de paginación (verificar documentación específica).

7. **Filtros:** Los endpoints de consulta suelen aceptar parámetros de filtrado por fecha, estado, etc.

---

## Recursos Adicionales

- **Swagger UI:** http://api.pos.dynamiaerp.co/swagger-ui/index.html
- **OpenAPI Spec:** http://api.pos.dynamiaerp.co/v3/api-docs
- **Contacto:** devteam@dynamiasoluciones.com
- **Términos:** https://www.dynamiaerp.co/terminos-y-condiciones/

---

## Próximos Pasos

1. Obtener credenciales de acceso (usuario y contraseña)
2. Probar autenticación y obtención de token
3. Identificar el `accountId` de la empresa
4. Probar endpoints básicos (consultar clientes, productos)
5. Implementar integración con sistema de paquetería
6. Configurar webhooks para sincronización automática
7. Implementar manejo de errores y reintentos
8. Documentar flujos de integración específicos

