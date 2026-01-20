#!/usr/bin/env python3
"""
Script para crear la tabla cufe_records en staging
Ejecutar desde el contenedor de la app en staging
"""
import sys
sys.path.insert(0, '/app/src')

from sqlalchemy import text
from app.database import engine

def crear_tabla_cufe():
    print("🚀 Creando tabla cufe_records...")
    print("=" * 60)
    
    with engine.connect() as conn:
        # 1. Crear ENUM
        print("\n1️⃣ Creando tipo ENUM cufestatus...")
        try:
            conn.execute(text("""
                CREATE TYPE cufestatus AS ENUM (
                    'pending', 
                    'downloading', 
                    'downloaded', 
                    'processing', 
                    'processed', 
                    'error'
                )
            """))
            conn.commit()
            print("   ✅ ENUM creado")
        except Exception as e:
            if "already exists" in str(e):
                print("   ℹ️  ENUM ya existe")
            else:
                print(f"   ⚠️  Error: {e}")
        
        # 2. Crear tabla
        print("\n2️⃣ Creando tabla cufe_records...")
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS cufe_records (
                    id SERIAL PRIMARY KEY,
                    cufe VARCHAR(96) NOT NULL,
                    status cufestatus NOT NULL DEFAULT 'pending',
                    supplier_name VARCHAR(255),
                    invoice_number VARCHAR(100),
                    invoice_id INTEGER,
                    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMP,
                    created_by INTEGER NOT NULL,
                    error_message TEXT,
                    retry_count INTEGER NOT NULL DEFAULT 0,
                    CONSTRAINT fk_cufe_records_created_by FOREIGN KEY (created_by) REFERENCES users(id),
                    CONSTRAINT fk_cufe_records_invoice_id FOREIGN KEY (invoice_id) REFERENCES invoices(id)
                )
            """))
            conn.commit()
            print("   ✅ Tabla creada")
        except Exception as e:
            print(f"   ⚠️  Error: {e}")
        
        # 3. Crear índices
        print("\n3️⃣ Creando índices...")
        indices = [
            "CREATE INDEX IF NOT EXISTS ix_cufe_records_id ON cufe_records(id)",
            "CREATE UNIQUE INDEX IF NOT EXISTS ix_cufe_records_cufe ON cufe_records(cufe)",
            "CREATE INDEX IF NOT EXISTS ix_cufe_records_status ON cufe_records(status)",
            "CREATE INDEX IF NOT EXISTS ix_cufe_records_created_at ON cufe_records(created_at)"
        ]
        
        for idx_sql in indices:
            try:
                conn.execute(text(idx_sql))
                conn.commit()
                print(f"   ✅ {idx_sql.split('INDEX')[1].split('ON')[0].strip()}")
            except Exception as e:
                print(f"   ⚠️  Error: {e}")
        
        # 4. Verificar
        print("\n4️⃣ Verificando tabla...")
        result = conn.execute(text("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'cufe_records'
            ORDER BY ordinal_position
        """))
        
        columns = result.fetchall()
        if columns:
            print("   ✅ Tabla cufe_records existe con las siguientes columnas:")
            for col in columns:
                print(f"      - {col[0]}: {col[1]} (nullable: {col[2]})")
        else:
            print("   ❌ ERROR: Tabla no encontrada")
        
        # 5. Actualizar alembic_version
        print("\n5️⃣ Actualizando registro de migración...")
        try:
            conn.execute(text("""
                INSERT INTO alembic_version (version_num)
                VALUES ('create_cufe_records')
                ON CONFLICT (version_num) DO NOTHING
            """))
            conn.commit()
            print("   ✅ Registro de migración actualizado")
        except Exception as e:
            print(f"   ⚠️  Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Proceso completado")
    print("\nAhora puedes usar el tab CUFE en https://staging.jemavi.co/invoices")

if __name__ == "__main__":
    crear_tabla_cufe()
