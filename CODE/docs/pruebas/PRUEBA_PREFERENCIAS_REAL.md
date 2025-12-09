# Prueba Real de Preferencias de Notificaciones

## Aclaración Importante

**El OTP para acceder al portal NO debe respetar las preferencias.** Esto es correcto por seguridad.

Las preferencias solo aplican a **notificaciones de paquetes** (recibido, entregado, etc.).

## Cambios Realizados

He agregado logging detallado en los servicios SMS y Email para ver exactamente qué está pasando cuando se verifican las preferencias.

## Cómo Probar

### Paso 1: Desplegar los cambios en staging

```bash
# En tu máquina local
cd CODE
git add .
git commit -m "feat: agregar logging detallado para preferencias"
git push

# En staging
ssh staging
cd /ruta/del/proyecto
git pull
docker-compose restart backend
```

### Paso 2: Configurar preferencias

1. Ir a: https://staging.jemavi.co/customer/verify
2. Ingresar con teléfono: `573002596319`
3. Solicitar y verificar OTP (esto SÍ debe llegar aunque las preferencias estén desactivadas)
4. Ir a "Preferencias"
5. **Desactivar ambos switches** (SMS y Email)
6. Guardar
7. Recargar la página y verificar que los switches sigan desactivados

### Paso 3: Probar con notificación de paquete REAL

**IMPORTANTE:** No solicitar otro OTP. En su lugar, cambiar el estado de un paquete del cliente.

#### Opción A: Desde el dashboard administrativo

1. Buscar un paquete del cliente JESUS VILLALOBOS (tel: 573002596319)
2. Cambiar el estado del paquete (ej: de ANUNCIADO a RECIBIDO)
3. Esto debería generar una notificación

#### Opción B: Crear un paquete de prueba

```bash
ssh staging
docker exec -it paquetes-backend-1 python3 -c "
import sys
sys.path.insert(0, '/app')

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.customer import Customer
from app.models.package import Package, PackageStatus, PackageType, PackageCondition
from app.utils.phone_utils import normalize_phone
from app.utils.datetime_utils import get_colombia_now
from decimal import Decimal
import uuid

db = SessionLocal()

try:
    # Buscar cliente
    phone = normalize_phone('3002596319')
    customer = db.query(Customer).filter(
        Customer.phone == phone,
        Customer.is_active == True
    ).first()
    
    if not customer:
        print('❌ Cliente no encontrado')
        sys.exit(1)
    
    print(f'✅ Cliente: {customer.full_name} (ID: {customer.id})')
    
    # Crear paquete de prueba
    package = Package(
        customer_id=customer.id,
        guide_number='TEST-' + str(uuid.uuid4())[:8],
        tracking_number='PAP' + str(uuid.uuid4())[:8],
        status=PackageStatus.ANUNCIADO,
        package_type=PackageType.NORMAL,
        package_condition=PackageCondition.BUENO,
        base_fee=Decimal('5000'),
        storage_fee=Decimal('0'),
        total_amount=Decimal('5000'),
        announced_at=get_colombia_now()
    )
    
    db.add(package)
    db.commit()
    db.refresh(package)
    
    print(f'✅ Paquete creado: {package.tracking_number}')
    print(f'   ID: {package.id}')
    print(f'   Estado: {package.status.value}')
    
except Exception as e:
    print(f'❌ Error: {str(e)}')
    import traceback
    traceback.print_exc()
finally:
    db.close()
"
```

### Paso 4: Cambiar estado del paquete

Esto generará las notificaciones que SÍ deben respetar las preferencias.

```bash
# Obtener el ID del paquete del paso anterior
# Luego cambiar su estado

docker exec -it paquetes-backend-1 python3 -c "
import sys
sys.path.insert(0, '/app')
import asyncio

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.package import Package, PackageStatus
from app.services.package_state_service import PackageStateService

async def cambiar_estado():
    db = SessionLocal()
    
    try:
        # Buscar el paquete (reemplazar con el tracking_number del paso anterior)
        tracking = 'PAP...'  # Poner el tracking number aquí
        package = db.query(Package).filter(
            Package.tracking_number == tracking
        ).first()
        
        if not package:
            print('❌ Paquete no encontrado')
            return
        
        print(f'📦 Paquete: {package.tracking_number}')
        print(f'   Estado actual: {package.status.value}')
        print(f'   Cliente ID: {package.customer_id}')
        
        # Cambiar estado a RECIBIDO (esto debe generar notificaciones)
        print(f'\\n🔄 Cambiando estado a RECIBIDO...')
        
        history = await PackageStateService.update_package_status(
            db=db,
            package=package,
            new_status=PackageStatus.RECIBIDO,
            changed_by='test_user',
            additional_data={},
            observations='Prueba de preferencias'
        )
        
        print(f'✅ Estado cambiado exitosamente')
        print(f'   Historial ID: {history.id}')
        
    except Exception as e:
        print(f'❌ Error: {str(e)}')
        import traceback
        traceback.print_exc()
    finally:
        db.close()

asyncio.run(cambiar_estado())
"
```

### Paso 5: Revisar los logs

```bash
# Ver logs en tiempo real
docker logs -f paquetes-backend-1 | grep -E "SMS|EMAIL|preferencias|bloqueado|customer_id"
```

**Logs esperados si funciona correctamente:**

```
🔍 Verificando preferencias para customer_id: <UUID>
📋 Preferencias encontradas para cliente <UUID>
   SMS habilitado: False
   Evento: package_received
   ¿Debe enviar?: False
📵 SMS bloqueado por preferencias del cliente <UUID>

🔍 [EMAIL] Verificando preferencias para customer_id: <UUID>
📋 [EMAIL] Preferencias encontradas para cliente <UUID>
   Email habilitado: False
   Evento: package_received
   ¿Debe enviar?: False
📧❌ Email bloqueado por preferencias del cliente <UUID>
```

**Logs si NO funciona:**

```
⚠️ No se encontraron preferencias para cliente <UUID>
```

O simplemente no aparecen logs de verificación.

## Resultado Esperado

1. **OTP para acceder:** SÍ debe llegar (SMS y Email) aunque las preferencias estén desactivadas ✅
2. **Notificación de paquete:** NO debe llegar si las preferencias están desactivadas ✅

## Si las notificaciones de paquete siguen llegando

Revisar en los logs:

1. **Si dice "No se encontraron preferencias":**
   - El cliente no tiene preferencias en la BD
   - Necesitas crearlas manualmente

2. **Si dice "¿Debe enviar?: True" cuando debería ser False:**
   - Hay un problema en la lógica de `should_send_notification`
   - Verificar que las preferencias estén guardadas correctamente en la BD

3. **Si no aparecen logs de verificación:**
   - El `customer_id` no se está pasando correctamente
   - Verificar que el paquete tenga `customer_id` asignado

## Consulta SQL para verificar

```sql
-- Ver preferencias del cliente
SELECT 
    c.id,
    c.full_name,
    c.phone,
    cp.sms_notifications_enabled,
    cp.email_notifications_enabled,
    cp.notify_package_received,
    cp.notify_package_delivered,
    cp.updated_at
FROM customers c
LEFT JOIN customer_preferences cp ON c.id = cp.customer_id
WHERE c.phone = '573002596319';

-- Ver últimas notificaciones
SELECT 
    n.id,
    n.notification_type,
    n.event_type,
    n.status,
    n.customer_id,
    n.error_message,
    n.created_at
FROM notifications n
JOIN customers c ON n.customer_id = c.id
WHERE c.phone = '573002596319'
ORDER BY n.created_at DESC
LIMIT 10;
```

## Siguiente Paso

Después de desplegar los cambios y probar con un paquete real, comparte:
1. Los logs del servidor
2. El resultado de las consultas SQL
3. Si la notificación llegó o no

Con esa información sabré exactamente qué está fallando.
