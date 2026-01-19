import sys
sys.path.insert(0, 'src')
from app.database import SessionLocal
from app.models.invoice import SupplierInvoice
from datetime import datetime
import re

db = SessionLocal()

print('Corrigiendo fechas futuras...')
now = datetime.now()

future_si = db.query(SupplierInvoice).filter(
    SupplierInvoice.invoice_date > now
).all()

print(f'Encontradas {len(future_si)} facturas con fechas futuras')

for si in future_si:
    print(f'ID {si.id}: {si.invoice_date.strftime("%Y-%m-%d")} -> ', end='')
    
    # Extraer fecha del nombre del archivo: _YYYYMMDD
    match = re.search(r'_(\d{8})', si.original_filename)
    if match:
        fecha_str = match.group(1)
        try:
            fecha = datetime.strptime(fecha_str, '%Y%m%d')
            if fecha <= now:
                si.invoice_date = fecha
                print(f'{fecha.strftime("%Y-%m-%d")} OK')
            else:
                si.invoice_date = si.uploaded_at
                print(f'{si.uploaded_at.strftime("%Y-%m-%d")} (uploaded)')
        except:
            si.invoice_date = si.uploaded_at
            print(f'{si.uploaded_at.strftime("%Y-%m-%d")} (uploaded)')
    else:
        si.invoice_date = si.uploaded_at
        print(f'{si.uploaded_at.strftime("%Y-%m-%d")} (uploaded)')

db.commit()
print('Fechas corregidas')
db.close()
