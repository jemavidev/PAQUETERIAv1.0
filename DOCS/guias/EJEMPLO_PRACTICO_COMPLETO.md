# 💡 Ejemplo Práctico Completo: Notificar Cliente con Preferencias

## 🎯 Escenario Real

Tienes un paquete que acaba de llegar y quieres notificar al cliente, respetando sus preferencias.

---

## 📝 Código Completo Listo para Usar

### **Ejemplo 1: Notificar Recepción de Paquete (Simple)**

```python
# En routes/packages.py o donde manejes paquetes

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.package import Package
from app.models.notification import NotificationEvent
from app.services.sms_service import SMSService
from app.services.email_service import EmailService

router = APIRouter()

@router.post("/packages/{package_id}/notify-received")
async def notify_package_received(
    package_id: int,
    db: Session = Depends(get_db)
):
    """Notifica al cliente que su paquete fue recibido"""
    
    # Obtener paquete
    package = db.query(Package).filter(Package.id == package_id).first()
    if not package or not package.customer:
        return {"error": "Paquete o cliente no encontrado"}
    
    customer = package.customer
    
    # Enviar SMS
    if customer.phone:
        sms_service = SMSService()
        sms_result = await sms_service.send_sms(
            db=db,
            recipient=customer.phone,
            message=f"PAQUETEX: Su paquete {package.tracking_number} ha sido RECIBIDO en nuestras instalaciones.",
            event_type=NotificationEvent.PACKAGE_RECEIVED,
            customer_id=customer.id  # ← Verifica preferencias automáticamente
        )
        
        print(f"SMS: {sms_result.status}")  # "sent" o "blocked"
    
    # Enviar Email
    if customer.email:
        email_service = EmailService()
        
        html_content = f"""
        <h1>Paquete Recibido</h1>
        <p>Hola {customer.full_name},</p>
        <p>Tu paquete con guía <strong>{package.tracking_number}</strong> ha sido recibido en nuestras instalaciones.</p>
        <p>Pronto te contactaremos para coordinar la entrega.</p>
        """
        
        email_result = await email_service.send_email(
            db=db,
            recipient=customer.email,
            subject="Paquete Recibido - PAQUETEX",
            html_content=html_content,
            event_type=NotificationEvent.PACKAGE_RECEIVED,
            customer_id=customer.id  # ← Verifica preferencias automáticamente
        )
        
        print(f"Email: {email_result['status']}")  # "sent" o "blocked"
    
    return {
        "success": True,
        "message": "Notificaciones enviadas (respetando preferencias del cliente)"
    }
```

---

### **Ejemplo 2: Notificar con Link de Preferencias (Completo)**

```python
from app.utils.customer_preferences_helper import (
    get_preferences_url,
    add_preferences_footer_to_sms,
    add_preferences_footer_to_email
)

@router.post("/packages/{package_id}/notify-received-with-link")
async def notify_package_received_with_preferences_link(
    package_id: int,
    db: Session = Depends(get_db)
):
    """Notifica al cliente incluyendo link para gestionar preferencias"""
    
    # Obtener paquete
    package = db.query(Package).filter(Package.id == package_id).first()
    if not package or not package.customer:
        return {"error": "Paquete o cliente no encontrado"}
    
    customer = package.customer
    
    # Obtener URL de preferencias del cliente
    prefs_url = get_preferences_url(db, customer.id)
    # Resultado: https://paquetex.com/customer/preferences?token=abc123xyz
    
    # === ENVIAR SMS ===
    if customer.phone:
        # Crear mensaje
        sms_message = f"PAQUETEX: Su paquete {package.tracking_number} ha sido RECIBIDO."
        
        # Agregar footer con link de preferencias
        sms_message = add_preferences_footer_to_sms(sms_message, prefs_url)
        # Resultado:
        # "PAQUETEX: Su paquete X123 ha sido RECIBIDO.
        #
        # Gestiona tus notificaciones: https://paquetex.com/customer/preferences?token=abc123"
        
        # Enviar SMS
        sms_service = SMSService()
        sms_result = await sms_service.send_sms(
            db=db,
            recipient=customer.phone,
            message=sms_message,
            event_type=NotificationEvent.PACKAGE_RECEIVED,
            customer_id=customer.id
        )
        
        print(f"SMS: {sms_result.status}")
    
    # === ENVIAR EMAIL ===
    if customer.email:
        # Crear contenido HTML
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #1e40af; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background: #f9fafb; }}
                .button {{ display: inline-block; padding: 12px 24px; background: #1e40af; color: white; text-decoration: none; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Paquete Recibido</h1>
                </div>
                <div class="content">
                    <p>Hola <strong>{customer.full_name}</strong>,</p>
                    <p>Tu paquete con guía <strong>{package.tracking_number}</strong> ha sido recibido en nuestras instalaciones.</p>
                    <p>Pronto te contactaremos para coordinar la entrega.</p>
                    <p style="text-align: center; margin-top: 30px;">
                        <a href="{prefs_url}" class="button">Ver Estado del Paquete</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Agregar footer con link de preferencias
        html_content = add_preferences_footer_to_email(html_content, prefs_url)
        
        # Enviar email
        email_service = EmailService()
        email_result = await email_service.send_email(
            db=db,
            recipient=customer.email,
            subject=f"Paquete {package.tracking_number} Recibido - PAQUETEX",
            html_content=html_content,
            event_type=NotificationEvent.PACKAGE_RECEIVED,
            customer_id=customer.id
        )
        
        print(f"Email: {email_result['status']}")
    
    return {
        "success": True,
        "message": "Notificaciones enviadas con link de preferencias",
        "preferences_url": prefs_url
    }
```

---

### **Ejemplo 3: Función Helper Reutilizable**

```python
# Crear archivo: app/utils/notification_helpers.py

from sqlalchemy.orm import Session
from app.models.customer import Customer
from app.models.package import Package
from app.models.notification import NotificationEvent
from app.services.sms_service import SMSService
from app.services.email_service import EmailService
from app.utils.customer_preferences_helper import (
    get_preferences_url,
    add_preferences_footer_to_sms,
    add_preferences_footer_to_email
)


async def notify_customer_package_event(
    db: Session,
    customer: Customer,
    package: Package,
    event_type: NotificationEvent,
    custom_message: str = None
):
    """
    Función helper para notificar eventos de paquetes a clientes
    Respeta automáticamente las preferencias del cliente
    
    Args:
        db: Sesión de base de datos
        customer: Cliente a notificar
        package: Paquete relacionado
        event_type: Tipo de evento (PACKAGE_RECEIVED, PACKAGE_DELIVERED, etc.)
        custom_message: Mensaje personalizado (opcional)
    
    Returns:
        dict: Resultado del envío
    """
    
    # Mapeo de eventos a mensajes por defecto
    default_messages = {
        NotificationEvent.PACKAGE_ANNOUNCED: f"Su paquete {package.tracking_number} ha sido ANUNCIADO",
        NotificationEvent.PACKAGE_RECEIVED: f"Su paquete {package.tracking_number} ha sido RECIBIDO",
        NotificationEvent.PACKAGE_DELIVERED: f"Su paquete {package.tracking_number} ha sido ENTREGADO",
        NotificationEvent.PAYMENT_DUE: f"Tiene un pago pendiente para el paquete {package.tracking_number}"
    }
    
    # Usar mensaje personalizado o por defecto
    message = custom_message or default_messages.get(event_type, "Actualización de su paquete")
    
    # Obtener URL de preferencias
    prefs_url = get_preferences_url(db, customer.id)
    
    results = {
        "sms": None,
        "email": None,
        "preferences_url": prefs_url
    }
    
    # === ENVIAR SMS ===
    if customer.phone:
        sms_message = f"PAQUETEX: {message}"
        sms_message = add_preferences_footer_to_sms(sms_message, prefs_url)
        
        sms_service = SMSService()
        sms_result = await sms_service.send_sms(
            db=db,
            recipient=customer.phone,
            message=sms_message,
            event_type=event_type,
            package_id=str(package.id),
            customer_id=customer.id
        )
        
        results["sms"] = {
            "status": sms_result.status,
            "message": sms_result.message
        }
    
    # === ENVIAR EMAIL ===
    if customer.email:
        # Mapeo de eventos a asuntos de email
        subjects = {
            NotificationEvent.PACKAGE_ANNOUNCED: "Paquete Anunciado",
            NotificationEvent.PACKAGE_RECEIVED: "Paquete Recibido",
            NotificationEvent.PACKAGE_DELIVERED: "Paquete Entregado",
            NotificationEvent.PAYMENT_DUE: "Pago Pendiente"
        }
        
        subject = f"{subjects.get(event_type, 'Actualización')} - PAQUETEX"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: #1e40af; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0;">
                    <h1 style="margin: 0;">{subjects.get(event_type, 'Actualización')}</h1>
                </div>
                <div style="padding: 30px; background: #f9fafb; border-radius: 0 0 10px 10px;">
                    <p>Hola <strong>{customer.full_name}</strong>,</p>
                    <p>{message}</p>
                    <div style="margin: 30px 0; padding: 20px; background: white; border-left: 4px solid #1e40af; border-radius: 5px;">
                        <p style="margin: 0;"><strong>Guía:</strong> {package.tracking_number}</p>
                        <p style="margin: 10px 0 0 0;"><strong>Estado:</strong> {event_type.value}</p>
                    </div>
                    <p>Gracias por confiar en PAQUETEX.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        html_content = add_preferences_footer_to_email(html_content, prefs_url)
        
        email_service = EmailService()
        email_result = await email_service.send_email(
            db=db,
            recipient=customer.email,
            subject=subject,
            html_content=html_content,
            event_type=event_type,
            package_id=package.id,
            customer_id=customer.id
        )
        
        results["email"] = {
            "status": email_result["status"],
            "message": email_result.get("message", "")
        }
    
    return results


# === USO DE LA FUNCIÓN HELPER ===

@router.post("/packages/{package_id}/notify")
async def notify_package_event(
    package_id: int,
    event_type: NotificationEvent,
    db: Session = Depends(get_db)
):
    """Endpoint simplificado usando la función helper"""
    
    package = db.query(Package).filter(Package.id == package_id).first()
    if not package or not package.customer:
        return {"error": "Paquete o cliente no encontrado"}
    
    # Usar función helper (una sola línea!)
    results = await notify_customer_package_event(
        db=db,
        customer=package.customer,
        package=package,
        event_type=event_type
    )
    
    return {
        "success": True,
        "results": results
    }
```

---

### **Ejemplo 4: Script de Prueba Completo**

```python
# Crear archivo: test_customer_notifications.py

import asyncio
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.customer import Customer
from app.models.package import Package
from app.models.notification import NotificationEvent
from app.utils.notification_helpers import notify_customer_package_event


async def test_notifications():
    """Script de prueba para notificaciones de clientes"""
    
    db = SessionLocal()
    
    try:
        # 1. Obtener un cliente de prueba
        customer = db.query(Customer).first()
        if not customer:
            print("❌ No hay clientes en la base de datos")
            return
        
        print(f"✅ Cliente encontrado: {customer.full_name}")
        print(f"   Teléfono: {customer.phone}")
        print(f"   Email: {customer.email}")
        
        # 2. Obtener un paquete del cliente
        package = db.query(Package).filter(
            Package.customer_id == customer.id
        ).first()
        
        if not package:
            print("❌ Cliente no tiene paquetes")
            return
        
        print(f"✅ Paquete encontrado: {package.tracking_number}")
        
        # 3. Enviar notificación de prueba
        print("\n📤 Enviando notificaciones...")
        
        results = await notify_customer_package_event(
            db=db,
            customer=customer,
            package=package,
            event_type=NotificationEvent.PACKAGE_RECEIVED,
            custom_message="Esta es una notificación de prueba"
        )
        
        # 4. Mostrar resultados
        print("\n📊 Resultados:")
        
        if results["sms"]:
            print(f"   SMS: {results['sms']['status']}")
            print(f"        {results['sms']['message']}")
        
        if results["email"]:
            print(f"   Email: {results['email']['status']}")
            print(f"          {results['email']['message']}")
        
        print(f"\n🔗 Link de preferencias:")
        print(f"   {results['preferences_url']}")
        
        print("\n✅ Prueba completada!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(test_notifications())
```

**Ejecutar:**
```bash
cd CODE/src
python test_customer_notifications.py
```

---

## 🎯 Resumen de Uso

### **Opción 1: Uso Simple (Recomendado para empezar)**
```python
# Solo agregar customer_id a tus llamadas existentes
await sms_service.send_sms(
    db=db,
    recipient=customer.phone,
    message="Paquete recibido",
    customer_id=customer.id  # ← Solo esto
)
```

### **Opción 2: Uso con Link de Preferencias**
```python
# Agregar link para que el cliente gestione preferencias
from app.utils.customer_preferences_helper import get_preferences_url

prefs_url = get_preferences_url(db, customer.id)
message = f"Paquete recibido. Gestiona notificaciones: {prefs_url}"
```

### **Opción 3: Uso con Función Helper (Recomendado para producción)**
```python
# Usar función helper que hace todo automáticamente
from app.utils.notification_helpers import notify_customer_package_event

await notify_customer_package_event(
    db=db,
    customer=customer,
    package=package,
    event_type=NotificationEvent.PACKAGE_RECEIVED
)
```

---

## ✅ Checklist de Implementación

- [ ] Ejecutar migraciones (`alembic upgrade head`)
- [ ] Reiniciar aplicación
- [ ] Crear preferencias para un cliente de prueba
- [ ] Probar envío de notificación
- [ ] Verificar que se respetan preferencias
- [ ] Agregar función helper a tu código
- [ ] Actualizar código existente para pasar `customer_id`
- [ ] Probar en producción con clientes reales

---

**¡Listo para usar!** Copia cualquiera de estos ejemplos y adáptalos a tu código.
