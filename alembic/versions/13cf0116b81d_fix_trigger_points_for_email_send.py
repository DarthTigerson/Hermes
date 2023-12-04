"""fix trigger points for email send

Revision ID: 13cf0116b81d
Revises: b4ab73e539f6
Create Date: 2023-12-04 08:45:55.566866

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '13cf0116b81d'
down_revision: Union[str, None] = 'b4ab73e539f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('your_table_name', sa.Column('trigger_welcome_email', sa.Boolean, default=False))

def downgrade():
    op.drop_column('your_table_name', 'trigger_welcome_email')