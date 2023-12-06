"""add email templates table

Revision ID: b4ab73e539f6
Revises: f9280b745a5b
Create Date: 2023-11-26 20:01:18.557192

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b4ab73e539f6'
down_revision: Union[str, None] = 'f9280b745a5b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'email_templates',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('onboarding_subject', sa.String(250)),
        sa.Column('onboarding_body', sa.String),
        sa.Column('employee_updates_subject', sa.String(250)),
        sa.Column('employee_updates_body', sa.String),
        sa.Column('offboarding_subject', sa.String(250)),
        sa.Column('offboarding_body', sa.String),
        sa.Column('welcome_email_subject', sa.String(250)),
        sa.Column('welcome_email_body', sa.String)
    )

def downgrade() -> None:
    op.drop_table('email_templates')