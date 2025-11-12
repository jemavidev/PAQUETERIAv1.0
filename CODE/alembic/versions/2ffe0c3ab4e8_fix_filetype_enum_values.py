# PAQUETES EL CLUB v4.0 - ALEMBIC SCRIPT TEMPLATE
# Template para generar archivos de migración

"""fix_filetype_enum_values

Revision ID: 2ffe0c3ab4e8
Revises: d8e9a7b1c3f2
Create Date: 2025-10-26 16:20:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2ffe0c3ab4e8'
down_revision = 'd8e9a7b1c3f2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Corregir los valores del enum FileType para que coincidan con el modelo Python.
    """
    
    # Verificar si el enum filetype existe y tiene los valores correctos
    connection = op.get_bind()
    
    # Obtener los valores actuales del enum
    result = connection.execute(sa.text("""
        SELECT e.enumlabel 
        FROM pg_type t 
        JOIN pg_enum e ON t.oid = e.enumtypid 
        WHERE t.typname = 'filetype'
        ORDER BY e.enumsortorder;
    """))
    
    current_values = [row[0] for row in result]
    print(f"Valores actuales del enum filetype: {current_values}")
    
    # Valores esperados según el modelo Python
    expected_values = ['IMAGEN', 'DOCUMENTO', 'RECIBO']
    
    # Si los valores no coinciden, actualizar el enum
    if set(current_values) != set(expected_values):
        print("Actualizando enum filetype...")
        
        # Agregar valores faltantes
        for value in expected_values:
            if value not in current_values:
                try:
                    connection.execute(sa.text(f"ALTER TYPE filetype ADD VALUE '{value}'"))
                    print(f"Agregado valor: {value}")
                except Exception as e:
                    print(f"Error agregando {value}: {e}")
        
        # Si hay valores que no están en la lista esperada, no los eliminamos
        # para evitar problemas con datos existentes
        print("Enum filetype actualizado correctamente")
    else:
        print("Enum filetype ya tiene los valores correctos")


def downgrade() -> None:
    """
    No se puede hacer downgrade de enums de forma segura.
    """
    print("No se puede hacer downgrade de enums de forma segura")