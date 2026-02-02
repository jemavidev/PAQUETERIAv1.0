#!/usr/bin/env python3
"""
Script para resolver conflicto de migraciones duplicadas
Marca las migraciones problemáticas como aplicadas
"""
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def main():
    # Obtener DATABASE_URL
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ ERROR: DATABASE_URL no está configurada")
        sys.exit(1)
    
    print(f"🔗 Conectando a la base de datos...")
    print(f"   Host: {database_url.split('@')[1].split('/')[0]}")
    print(f"   Database: {database_url.split('/')[-1]}")
    
    try:
        # Crear engine
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Verificar migraciones actuales
            print("\n📋 Verificando migraciones actuales...")
            result = conn.execute(text("""
                SELECT version_num, applied_at 
                FROM alembic_version 
                ORDER BY applied_at DESC
                LIMIT 5
            """))
            
            current_migrations = result.fetchall()
            if current_migrations:
                print("   Últimas migraciones aplicadas:")
                for migration in current_migrations:
                    print(f"   - {migration[0]} ({migration[1]})")
            else:
                print("   No hay migraciones aplicadas")
            
            # Verificar si cufe_status existe
            print("\n🔍 Verificando estructura de la tabla invoices...")
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'invoices' 
                AND column_name IN ('cufe_status', 'dian_status')
                ORDER BY column_name
            """))
            
            existing_columns = [row[0] for row in result.fetchall()]
            if existing_columns:
                print(f"   ✓ Columnas encontradas: {', '.join(existing_columns)}")
            else:
                print("   ℹ️  No se encontraron las columnas cufe_status/dian_status")
            
            # Verificar si cufe_records existe
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name = 'cufe_records'
            """))
            
            cufe_records_exists = result.fetchone() is not None
            if cufe_records_exists:
                print("   ✓ Tabla cufe_records existe")
            else:
                print("   ℹ️  Tabla cufe_records no existe")
            
            # Marcar migraciones como aplicadas
            print("\n🔧 Aplicando correcciones...")
            
            migrations_to_mark = []
            
            # Si cufe_status existe, marcar add_cufe_dian_status_fields
            if 'cufe_status' in existing_columns:
                migrations_to_mark.append('add_cufe_dian_status_fields')
            
            # Si cufe_records existe, marcar create_cufe_records_table
            if cufe_records_exists:
                migrations_to_mark.append('create_cufe_records_table')
            
            if not migrations_to_mark:
                print("   ℹ️  No hay migraciones que marcar")
            else:
                for migration in migrations_to_mark:
                    # Verificar si ya está marcada
                    result = conn.execute(text("""
                        SELECT 1 FROM alembic_version 
                        WHERE version_num = :migration
                    """), {"migration": migration})
                    
                    if result.fetchone():
                        print(f"   ⏭️  {migration} ya está marcada como aplicada")
                    else:
                        # Marcar como aplicada
                        conn.execute(text("""
                            INSERT INTO alembic_version (version_num)
                            VALUES (:migration)
                        """), {"migration": migration})
                        conn.commit()
                        print(f"   ✅ {migration} marcada como aplicada")
            
            # Verificar resultado final
            print("\n📊 Estado final de migraciones:")
            result = conn.execute(text("""
                SELECT version_num, applied_at 
                FROM alembic_version 
                ORDER BY applied_at DESC
                LIMIT 10
            """))
            
            final_migrations = result.fetchall()
            for migration in final_migrations:
                print(f"   - {migration[0]} ({migration[1]})")
            
            print("\n✅ Proceso completado exitosamente")
            print("\n💡 Ahora puedes ejecutar:")
            print("   cd CODE && alembic upgrade head")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
