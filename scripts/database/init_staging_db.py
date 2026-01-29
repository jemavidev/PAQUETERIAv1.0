#!/usr/bin/env python3
"""
Script para inicializar la base de datos staging con las tablas necesarias
"""
import sys
sys.path.insert(0, '/app/src')

from sqlalchemy import create_engine, text
from app.database import Base
from app.models.user import User
from app.models.customer import Customer
from app.models.package import Package
from app.models.announcement import Announcement
from app.models.rate import Rate
from app.models.notification import Notification
from app.models.message import Message
from app.models.file_upload import FileUpload
from app.models.customer_preferences import CustomerPreferences

# Importar todos los modelos adicionales que existan
try:
    from app.models.product import Product
except:
    pass

try:
    from app.models.supplier_invoice import SupplierInvoice
except:
    pass

try:
    from app.models.cufe_record import CUFERecord
except:
    pass

# Conexión a staging
DATABASE_URL = "postgresql://jveyes:a?HC!2.*1#?[==:|289qAI=)#V4kDzl$@ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com:5432/paqueteria_staging"

print('🔧 Inicializando base de datos staging...')
print(f'📊 Base de datos: paqueteria_staging')
print()

try:
    # Crear engine
    engine = create_engine(DATABASE_URL)
    
    # Crear todas las tablas
    print('📋 Creando tablas...')
    Base.metadata.create_all(bind=engine)
    
    # Verificar tablas creadas
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public' 
            ORDER BY tablename
        """))
        tables = [row[0] for row in result]
    
    print(f'✅ {len(tables)} tablas creadas:')
    for table in tables:
        print(f'   - {table}')
    
    print()
    print('✅ Base de datos inicializada correctamente')
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
    exit(1)
