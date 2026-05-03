"""add cufe manual entry fields to invoices_v2

Revision ID: 20260503_061946
Revises: 20260211_092552
Create Date: 2026-05-03 06:19:46

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260503_061946'
down_revision = '20260211_092552'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Agregar columnas nuevas
    op.add_column('invoices_v2', sa.Column('cufe_origen', sa.String(20), nullable=False, server_default='automatico'))
    op.add_column('invoices_v2', sa.Column('cufe_validado_usuario', sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column('invoices_v2', sa.Column('codigo_alternativo', sa.String(100), nullable=True))
    op.add_column('invoices_v2', sa.Column('codigo_alternativo_tipo', sa.String(20), nullable=True))

    # Remover server_default después de migration (PostgreSQL best practice)
    op.alter_column('invoices_v2', 'cufe_origen',
               existing_type=sa.String(20),
               nullable=False,
               server_default=None)
    op.alter_column('invoices_v2', 'cufe_validado_usuario',
               existing_type=sa.Boolean(),
               nullable=False,
               server_default=None)


def downgrade() -> None:
    op.drop_column('invoices_v2', 'codigo_alternativo_tipo')
    op.drop_column('invoices_v2', 'codigo_alternativo')
    op.drop_column('invoices_v2', 'cufe_validado_usuario')
    op.drop_column('invoices_v2', 'cufe_origen')
