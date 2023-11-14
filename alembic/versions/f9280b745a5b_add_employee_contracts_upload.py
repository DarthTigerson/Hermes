"""add employee contracts upload

Revision ID: f9280b745a5b
Revises: 478fb4dae08e
Create Date: 2023-11-14 22:34:00.774515

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f9280b745a5b'
down_revision: Union[str, None] = '478fb4dae08e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'employee_contracts',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('employee_id', sa.Integer, sa.ForeignKey('employees.id')),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id')),
        sa.Column('start_date', sa.String(50)),
        sa.Column('end_date', sa.String(50)),
        sa.Column('contract_name', sa.String(250)),
        sa.Column('notes', sa.String(250)),
        sa.Column('contract_file', sa.String),
    )


def downgrade():
    op.drop_table('employee_contracts')
