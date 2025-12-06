#!/bin/bash
# Comandos rápidos para diagnosticar OTP en staging
# Copia y pega estos comandos según necesites

echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║          COMANDOS RÁPIDOS - DIAGNÓSTICO OTP STAGING                 ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""

# Función para mostrar comandos
show_command() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  $1"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "$2"
    echo ""
}

show_command "1. VERIFICACIÓN RÁPIDA" \
"cd CODE && python3 check_otp_issue.py"

show_command "2. DIAGNÓSTICO COMPLETO (INTERACTIVO)" \
"cd CODE && python3 debug_otp_staging.py"

show_command "3. PROBAR VERIFICACIÓN EN VIVO" \
"cd CODE && python3 test_otp_verification_live.py"

show_command "4. VER ÚLTIMOS 10 OTPs" \
"cd CODE && python3 -c \"
import sys
sys.path.insert(0, 'src')
from app.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
result = db.execute(text('''
    SELECT customer_phone, otp_code, is_verified, is_expired, 
           attempts, created_at
    FROM customer_otps
    ORDER BY created_at DESC
    LIMIT 10
'''))

print('\\nÚltimos 10 OTPs:')
print('-' * 80)
for row in result:
    status = '✅ VERIFICADO' if row[2] else ('❌ EXPIRADO' if row[3] else '⏳ PENDIENTE')
    print(f'{row[0]} | {row[1]} | {status} | Intentos: {row[4]} | {row[5]}')

db.close()
\""

show_command "5. VER OTPs PENDIENTES" \
"cd CODE && python3 -c \"
import sys
sys.path.insert(0, 'src')
from app.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
result = db.execute(text('''
    SELECT customer_phone, otp_code, attempts, 
           EXTRACT(EPOCH FROM (expires_at - NOW())) as segundos
    FROM customer_otps
    WHERE is_verified = FALSE AND is_expired = FALSE
    ORDER BY created_at DESC
'''))

print('\\nOTPs Pendientes:')
print('-' * 80)
for row in result:
    if row[3] and row[3] > 0:
        mins = int(row[3] / 60)
        print(f'{row[0]} | {row[1]} | Intentos: {row[2]} | Expira en: {mins}m')
    else:
        print(f'{row[0]} | {row[1]} | ❌ EXPIRADO')

db.close()
\""

show_command "6. VERIFICAR TABLA EXISTE" \
"cd CODE && python3 -c \"
import sys
sys.path.insert(0, 'src')
from app.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    result = db.execute(text('SELECT COUNT(*) FROM customer_otps'))
    print(f'✅ Tabla existe con {result.scalar()} registros')
except Exception as e:
    print(f'❌ Error: {e}')
    print('\\nEjecuta: python3 create_customer_otps_table.py')
db.close()
\""

show_command "7. CREAR TABLA SI NO EXISTE" \
"cd CODE && python3 create_customer_otps_table.py"

show_command "8. VER LOGS EN TIEMPO REAL" \
"tail -f logs/app.log | grep -i otp"

show_command "9. BUSCAR ERRORES EN LOGS" \
"grep -i 'error.*otp\\|otp.*error' logs/app.log | tail -20"

show_command "10. LIMPIAR OTPs ANTIGUOS (>1 hora)" \
"cd CODE && python3 -c \"
import sys
sys.path.insert(0, 'src')
from app.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
result = db.execute(text('''
    DELETE FROM customer_otps 
    WHERE created_at < NOW() - INTERVAL '1 hour'
'''))
db.commit()
print(f'✅ {result.rowcount} OTPs eliminados')
db.close()
\""

show_command "11. RESETEAR OTPs DE UN CLIENTE" \
"cd CODE && python3 -c \"
import sys
sys.path.insert(0, 'src')
from app.database import SessionLocal
from sqlalchemy import text

PHONE = input('Teléfono (ej: +573001234567): ')

db = SessionLocal()
result = db.execute(text('''
    UPDATE customer_otps 
    SET is_expired = TRUE
    WHERE customer_phone = :phone AND is_verified = FALSE
'''), {'phone': PHONE})
db.commit()
print(f'✅ {result.rowcount} OTPs expirados para {PHONE}')
db.close()
\""

show_command "12. CREAR OTP MANUAL PARA PRUEBAS" \
"cd CODE && python3 -c \"
import sys
sys.path.insert(0, 'src')
from app.database import SessionLocal
from app.models.customer_otp import CustomerOTP

PHONE = input('Teléfono (ej: +573001234567): ')

db = SessionLocal()
otp = CustomerOTP(customer_phone=PHONE)
db.add(otp)
db.commit()
db.refresh(otp)

print(f'\\n✅ OTP creado: {otp.otp_code}')
print(f'   Expira en: 5 minutos')

db.close()
\""

show_command "13. VERIFICAR TIMEZONE DEL SERVIDOR" \
"date && timedatectl"

show_command "14. VERIFICAR CLIENTE EXISTE Y ESTÁ ACTIVO" \
"cd CODE && python3 -c \"
import sys
sys.path.insert(0, 'src')
from app.database import SessionLocal
from app.models.customer import Customer

PHONE = input('Teléfono (ej: +573001234567): ')

db = SessionLocal()
customer = db.query(Customer).filter(Customer.phone == PHONE).first()

if customer:
    print(f'\\n✅ Cliente encontrado:')
    print(f'   ID: {customer.id}')
    print(f'   Nombre: {customer.full_name}')
    print(f'   Activo: {customer.is_active}')
else:
    print(f'\\n❌ No existe cliente con teléfono {PHONE}')

db.close()
\""

show_command "15. REINICIAR SERVIDOR" \
"sudo systemctl restart paquetex
# O si usas uvicorn directamente:
# pkill -f uvicorn && cd CODE/src && uvicorn main:app --reload --host 0.0.0.0 --port 8000"

echo ""
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                    📖 MÁS INFORMACIÓN                                ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Lee la documentación completa:"
echo "  cat CODE/DIAGNOSTICO_OTP_STAGING.md"
echo ""
echo "O ejecuta el diagnóstico interactivo:"
echo "  cd CODE && python3 debug_otp_staging.py"
echo ""
