# Integración DynamiaERP con Sistema de Paquetería

## Objetivo

Integrar el sistema de paquetería actual con DynamiaERP para:
1. Sincronizar clientes
2. Generar facturas electrónicas automáticamente
3. Mantener inventario actualizado
4. Recibir notificaciones en tiempo real

## Arquitectura de Integración

```
┌─────────────────────────────────────────────────────────────┐
│                  Sistema de Paquetería                      │
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│  │   Frontend   │───▶│   Backend    │───▶│  PostgreSQL  │ │
│  │   (Jinja2)   │    │   (FastAPI)  │    │              │ │
│  └──────────────┘    └──────┬───────┘    └──────────────┘ │
│                             │                              │
└─────────────────────────────┼──────────────────────────────┘
                              │
                              │ API REST
                              │
                    ┌─────────▼─────────┐
                    │  DynamiaERP API   │
                    │                   │
                    │  - Facturación    │
                    │  - Clientes       │
                    │  - Inventario     │
                    │  - Webhooks       │
                    └───────────────────┘
```

## Flujos de Integración

### 1. Sincronización de Clientes

**Flujo:**
1. Usuario crea/actualiza cliente en sistema de paquetería
2. Sistema valida datos del cliente
3. Sistema envía datos a DynamiaERP
4. DynamiaERP retorna ID del cliente
5. Sistema guarda ID de DynamiaERP en BD local

**Endpoints:**
- `POST /api/ventas/clientes` - Crear cliente
- `PUT /api/ventas/clientes/{id}` - Actualizar cliente
- `GET /api/ventas/clientes/{id}` - Consultar cliente

**Mapeo de Datos:**

| Campo Paquetería | Campo DynamiaERP | Notas |
|------------------|------------------|-------|
| customer_id | id | ID local |
| dynamia_customer_id | id | ID en DynamiaERP |
| identification | identificacion | NIT/CC |
| identification_type_id | tipoIdentificacionId | 1=CC, 2=NIT, etc. |
| first_name | nombres | |
| last_name | apellidos | |
| business_name | razonSocial | Para empresas |
| email | datosContacto.email | |
| phone | datosContacto.telefono | |
| address | datosContacto.direccion | |
| city | ciudad.nombre | |
| neighborhood | barrio.nombre | |

### 2. Creación de Ventas y Facturación

**Flujo:**
1. Usuario vende paquete en sistema
2. Sistema crea venta local
3. Sistema envía venta a DynamiaERP
4. DynamiaERP genera factura electrónica
5. Sistema recibe CUFE y PDF
6. Sistema guarda CUFE y envía email al cliente

**Endpoints:**
- `POST /api/ventas` - Crear venta
- `POST /api/ventas/facturaElectronica` - Generar factura electrónica
- `GET /api/ventas/facturaElectronica/{cufe}` - Consultar factura
- `POST /api/ventas/facturaElectronica/{cufe}/enviarEmail` - Enviar por email

**Mapeo de Datos:**

| Campo Paquetería | Campo DynamiaERP | Notas |
|------------------|------------------|-------|
| sale_id | id | ID local |
| dynamia_sale_id | id | ID en DynamiaERP |
| cufe | cufe | Código único factura |
| customer_id | cliente.id | ID del cliente |
| package_id | detalles[].producto.id | ID del paquete |
| quantity | detalles[].cantidad | Cantidad |
| unit_price | detalles[].precio | Precio unitario |
| subtotal | subtotal | Subtotal |
| tax_amount | totalImpuestos | IVA |
| total | total | Total |
| payment_method | pago.formaPago | Efectivo, tarjeta, etc. |
| sale_date | fecha | Fecha de venta |

### 3. Gestión de Inventario

**Flujo:**
1. Sistema consulta existencias en DynamiaERP
2. Usuario vende paquete
3. Sistema actualiza inventario local
4. Sistema notifica a DynamiaERP (si aplica)

**Endpoints:**
- `GET /api/inventario/items` - Listar productos
- `GET /api/inventario/items/existencias` - Consultar existencias
- `POST /api/inventario/importar` - Importar inventario

### 4. Webhooks para Sincronización

**Flujo:**
1. Sistema configura webhook en DynamiaERP
2. DynamiaERP envía notificaciones de eventos
3. Sistema procesa eventos y actualiza BD local

**Eventos Relevantes:**
- `VENTA_CREADA` - Nueva venta creada
- `FACTURA_APROBADA` - Factura aprobada por DIAN
- `FACTURA_RECHAZADA` - Factura rechazada
- `CLIENTE_ACTUALIZADO` - Cliente modificado

**Endpoints:**
- `POST /api/webhooks` - Configurar webhook
- `PUT /api/webhooks/{id}` - Actualizar webhook
- `DELETE /api/webhooks/{id}` - Eliminar webhook

## Implementación

### Paso 1: Crear Servicio de Integración

Crear archivo `CODE/src/app/services/dynamia_service.py`:

```python
from typing import Dict, Any, Optional, List
import requests
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DynamiaService:
    """Servicio para integración con DynamiaERP"""
    
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.token: Optional[str] = None
        self.account_id: Optional[int] = None
        
    def authenticate(self) -> bool:
        """Autenticar con DynamiaERP"""
        try:
            response = requests.post(
                f"{self.base_url}/api/seguridad/gettoken",
                json={"username": self.username, "password": self.password}
            )
            response.raise_for_status()
            
            data = response.json()
            self.token = data.get('token')
            
            # Obtener account_id
            context = self.get_account_context()
            self.account_id = context.get('accountId')
            
            logger.info("Autenticación exitosa con DynamiaERP")
            return True
            
        except Exception as e:
            logger.error(f"Error en autenticación: {e}")
            return False
    
    def get_headers(self) -> Dict[str, str]:
        """Obtener headers con autenticación"""
        if not self.token:
            self.authenticate()
        
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def sync_customer(self, customer_data: Dict[str, Any]) -> Optional[int]:
        """
        Sincronizar cliente con DynamiaERP
        
        Args:
            customer_data: Datos del cliente del sistema local
            
        Returns:
            ID del cliente en DynamiaERP o None si falla
        """
        try:
            # Mapear datos locales a formato DynamiaERP
            dynamia_customer = {
                "accountId": self.account_id,
                "identificacion": customer_data.get('identification'),
                "tipoIdentificacionId": customer_data.get('identification_type_id', 1),
                "nombres": customer_data.get('first_name'),
                "apellidos": customer_data.get('last_name'),
                "razonSocial": customer_data.get('business_name'),
                "datosContacto": {
                    "email": customer_data.get('email'),
                    "telefono": customer_data.get('phone'),
                    "direccion": customer_data.get('address')
                }
            }
            
            # Si ya existe ID de DynamiaERP, actualizar
            if customer_data.get('dynamia_customer_id'):
                response = requests.put(
                    f"{self.base_url}/api/ventas/clientes/{customer_data['dynamia_customer_id']}",
                    headers=self.get_headers(),
                    json=dynamia_customer
                )
            else:
                # Crear nuevo cliente
                response = requests.post(
                    f"{self.base_url}/api/ventas/clientes",
                    headers=self.get_headers(),
                    json=dynamia_customer
                )
            
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"Cliente sincronizado: {data.get('id')}")
            return data.get('id')
            
        except Exception as e:
            logger.error(f"Error sincronizando cliente: {e}")
            return None
    
    def create_sale_and_invoice(self, sale_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Crear venta y generar factura electrónica
        
        Args:
            sale_data: Datos de la venta del sistema local
            
        Returns:
            Datos de la factura (CUFE, PDF, etc.) o None si falla
        """
        try:
            # Mapear datos de venta a formato DynamiaERP
            documento = {
                "tipo": "FACTURA",
                "fecha": sale_data.get('sale_date', datetime.now().isoformat()),
                "cliente": {
                    "id": sale_data.get('dynamia_customer_id'),
                    "identificacion": sale_data.get('customer_identification'),
                    "nombre": sale_data.get('customer_name'),
                    "email": sale_data.get('customer_email')
                },
                "detalles": [],
                "formasPagos": [
                    {
                        "formaPago": sale_data.get('payment_method', 'EFECTIVO'),
                        "valor": sale_data.get('total')
                    }
                ],
                "observaciones": sale_data.get('notes', '')
            }
            
            # Agregar detalles de productos/paquetes
            for item in sale_data.get('items', []):
                documento['detalles'].append({
                    "descripcion": item.get('description'),
                    "cantidad": item.get('quantity'),
                    "precioUnitario": item.get('unit_price'),
                    "impuesto": item.get('tax_rate', 19)  # IVA por defecto
                })
            
            # Enviar documento electrónico
            response = requests.post(
                f"{self.base_url}/api/ventas/facturaElectronica",
                headers=self.get_headers(),
                json=documento
            )
            response.raise_for_status()
            
            factura = response.json()
            
            logger.info(f"Factura creada: CUFE={factura.get('cufe')}")
            
            return {
                'cufe': factura.get('cufe'),
                'numero': factura.get('numero'),
                'pdf': factura.get('pdf'),
                'estado': factura.get('estado'),
                'dynamia_sale_id': factura.get('id')
            }
            
        except Exception as e:
            logger.error(f"Error creando factura: {e}")
            return None
    
    def send_invoice_email(self, cufe: str, emails: List[str], pdf: Optional[str] = None) -> bool:
        """
        Enviar factura por email
        
        Args:
            cufe: CUFE de la factura
            emails: Lista de emails destinatarios
            pdf: PDF en base64 (opcional)
            
        Returns:
            True si se envió exitosamente
        """
        try:
            payload = {"emails": emails}
            if pdf:
                payload["pdf"] = pdf
            
            response = requests.post(
                f"{self.base_url}/api/ventas/facturaElectronica/{cufe}/enviarEmail",
                headers=self.get_headers(),
                json=payload
            )
            response.raise_for_status()
            
            logger.info(f"Email enviado para CUFE: {cufe}")
            return True
            
        except Exception as e:
            logger.error(f"Error enviando email: {e}")
            return False
    
    def get_invoice_status(self, cufe: str) -> Optional[Dict[str, Any]]:
        """
        Consultar estado de factura
        
        Args:
            cufe: CUFE de la factura
            
        Returns:
            Datos de la factura o None si falla
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/ventas/facturaElectronica/{cufe}",
                headers=self.get_headers()
            )
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error consultando factura: {e}")
            return None
    
    def configure_webhook(self, target_url: str, event_type: str, alias: str) -> Optional[str]:
        """
        Configurar webhook para recibir notificaciones
        
        Args:
            target_url: URL donde recibir notificaciones
            event_type: Tipo de evento (VENTA_CREADA, FACTURA_APROBADA, etc.)
            alias: Nombre descriptivo
            
        Returns:
            ID del webhook o None si falla
        """
        try:
            webhook = {
                "accountId": self.account_id,
                "targetUrl": target_url,
                "eventType": event_type,
                "active": True,
                "alias": alias
            }
            
            response = requests.post(
                f"{self.base_url}/api/webhooks",
                headers=self.get_headers(),
                json=webhook
            )
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Webhook configurado: {data.get('id')}")
            
            return data.get('id')
            
        except Exception as e:
            logger.error(f"Error configurando webhook: {e}")
            return None
```

### Paso 2: Actualizar Modelos de Base de Datos

Agregar campos a la tabla `customers`:

```sql
ALTER TABLE customers 
ADD COLUMN dynamia_customer_id INTEGER,
ADD COLUMN last_sync_date TIMESTAMP,
ADD COLUMN sync_status VARCHAR(50);
```

Agregar campos a la tabla `sales`:

```sql
ALTER TABLE sales
ADD COLUMN dynamia_sale_id INTEGER,
ADD COLUMN cufe VARCHAR(255),
ADD COLUMN invoice_pdf TEXT,
ADD COLUMN invoice_status VARCHAR(50),
ADD COLUMN invoice_sent_date TIMESTAMP;
```

### Paso 3: Integrar en Endpoints Existentes

Modificar `CODE/src/app/routes/customers.py`:

```python
from app.services.dynamia_service import DynamiaService

@router.post("/customers")
async def create_customer(customer_data: dict, db: Session = Depends(get_db)):
    # Crear cliente localmente
    customer = Customer(**customer_data)
    db.add(customer)
    db.commit()
    
    # Sincronizar con DynamiaERP
    dynamia = DynamiaService(
        base_url=settings.DYNAMIA_API_URL,
        username=settings.DYNAMIA_USERNAME,
        password=settings.DYNAMIA_PASSWORD
    )
    
    dynamia_id = dynamia.sync_customer(customer_data)
    if dynamia_id:
        customer.dynamia_customer_id = dynamia_id
        customer.last_sync_date = datetime.now()
        customer.sync_status = "synced"
        db.commit()
    
    return customer
```

Modificar `CODE/src/app/routes/sales.py`:

```python
@router.post("/sales")
async def create_sale(sale_data: dict, db: Session = Depends(get_db)):
    # Crear venta localmente
    sale = Sale(**sale_data)
    db.add(sale)
    db.commit()
    
    # Generar factura electrónica en DynamiaERP
    dynamia = DynamiaService(
        base_url=settings.DYNAMIA_API_URL,
        username=settings.DYNAMIA_USERNAME,
        password=settings.DYNAMIA_PASSWORD
    )
    
    invoice = dynamia.create_sale_and_invoice(sale_data)
    if invoice:
        sale.cufe = invoice['cufe']
        sale.dynamia_sale_id = invoice['dynamia_sale_id']
        sale.invoice_pdf = invoice['pdf']
        sale.invoice_status = invoice['estado']
        db.commit()
        
        # Enviar factura por email
        if sale_data.get('customer_email'):
            dynamia.send_invoice_email(
                cufe=invoice['cufe'],
                emails=[sale_data['customer_email']]
            )
            sale.invoice_sent_date = datetime.now()
            db.commit()
    
    return sale
```

### Paso 4: Crear Endpoint para Webhooks

Crear `CODE/src/app/routes/webhooks.py`:

```python
from fastapi import APIRouter, Request, HTTPException
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/webhooks/dynamia")
async def receive_dynamia_webhook(request: Request):
    """Recibir notificaciones de DynamiaERP"""
    try:
        data = await request.json()
        event_type = data.get('eventType')
        
        logger.info(f"Webhook recibido: {event_type}")
        
        if event_type == "FACTURA_APROBADA":
            # Actualizar estado de factura
            cufe = data.get('cufe')
            # Buscar venta por CUFE y actualizar estado
            pass
            
        elif event_type == "FACTURA_RECHAZADA":
            # Manejar rechazo de factura
            cufe = data.get('cufe')
            # Notificar al usuario
            pass
            
        elif event_type == "CLIENTE_ACTUALIZADO":
            # Sincronizar datos del cliente
            customer_id = data.get('clienteId')
            # Actualizar datos locales
            pass
        
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"Error procesando webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

### Paso 5: Configurar Variables de Entorno

Agregar a `CODE/.env`:

```env
# DynamiaERP Integration
DYNAMIA_API_URL=https://api.dynamiaerp.co
DYNAMIA_USERNAME=tu_usuario
DYNAMIA_PASSWORD=tu_contraseña
DYNAMIA_ACCOUNT_ID=123
DYNAMIA_WEBHOOK_URL=https://tu-dominio.com/webhooks/dynamia
```

## Pruebas

### 1. Probar Autenticación

```bash
cd CODE
python scripts/test_dynamia_api.py
```

### 2. Probar Sincronización de Cliente

```python
# En Python shell o script de prueba
from app.services.dynamia_service import DynamiaService

dynamia = DynamiaService(
    base_url="https://api.dynamiaerp.co",
    username="tu_usuario",
    password="tu_contraseña"
)

customer_data = {
    "identification": "123456789",
    "identification_type_id": 1,
    "first_name": "Juan",
    "last_name": "Pérez",
    "email": "juan@example.com",
    "phone": "3001234567",
    "address": "Calle 123 #45-67"
}

customer_id = dynamia.sync_customer(customer_data)
print(f"Cliente creado con ID: {customer_id}")
```

### 3. Probar Creación de Factura

```python
sale_data = {
    "dynamia_customer_id": customer_id,
    "customer_identification": "123456789",
    "customer_name": "Juan Pérez",
    "customer_email": "juan@example.com",
    "sale_date": "2026-01-13",
    "payment_method": "EFECTIVO",
    "total": 119000,
    "items": [
        {
            "description": "Paquete Premium",
            "quantity": 1,
            "unit_price": 100000,
            "tax_rate": 19
        }
    ]
}

invoice = dynamia.create_sale_and_invoice(sale_data)
print(f"Factura creada: CUFE={invoice['cufe']}")
```

## Consideraciones

### Seguridad
- Almacenar credenciales en variables de entorno
- Usar HTTPS para todas las comunicaciones
- Validar tokens de webhook
- Implementar rate limiting

### Manejo de Errores
- Implementar reintentos automáticos
- Registrar todos los errores
- Notificar al usuario en caso de fallo
- Mantener cola de sincronización pendiente

### Performance
- Cachear token de autenticación
- Implementar sincronización asíncrona
- Usar cola de tareas (Celery/RQ)
- Batch processing para múltiples operaciones

### Monitoreo
- Registrar todas las operaciones
- Alertas para fallos de sincronización
- Dashboard de estado de integración
- Métricas de uso de API

## Próximos Pasos

1. ✅ Analizar API de DynamiaERP
2. ⬜ Obtener credenciales de acceso
3. ⬜ Implementar servicio de integración
4. ⬜ Actualizar modelos de BD
5. ⬜ Integrar en endpoints existentes
6. ⬜ Crear endpoint de webhooks
7. ⬜ Configurar webhooks en DynamiaERP
8. ⬜ Realizar pruebas de integración
9. ⬜ Desplegar en producción
10. ⬜ Monitorear y optimizar

