#!/bin/bash
# Script para verificar preferencias en staging

echo "=========================================="
echo "Verificando Preferencias en Staging"
echo "=========================================="

# Ejecutar script Python en el contenedor
docker exec paquetes-backend-1 python3 -c "
import sys
sys.path.insert(0, '/app')

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.customer import Customer
from app.models.customer_preferences import CustomerPreferences
from app.utils.phone_utils import normalize_phone

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
    
    print(f'✅ Cliente: {customer.full_name}')
    print(f'   ID: {customer.id}')
    
    # Buscar preferencias
    prefs = db.query(CustomerPreferences).filter(
        CustomerPreferences.customer_id == customer.id
    ).first()
    
    if not prefs:
        print('⚠️  Cliente SIN preferencias configuradas')
    else:
        print(f'📋 Preferencias:')
        print(f'   SMS: {prefs.sms_notifications_enabled}')
        print(f'   Email: {prefs.email_notifications_enabled}')
        print(f'   Paquete Recibido: {prefs.notify_package_received}')
        print(f'   Paquete Entregado: {prefs.notify_package_delivered}')
        
finally:
    db.close()
"

echo ""
echo "=========================================="
echo "Verificación completada"
echo "=========================================="
