"""update model

Revision ID: 831cf6fa6e0c
Revises: da506f4083cf
Create Date: 2025-04-25 16:21:44.712688

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '831cf6fa6e0c'
down_revision: Union[str, None] = 'da506f4083cf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('generate_history',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('uuid', sa.String(length=255), nullable=False),
    sa.Column('x_screen_name', sa.String(length=255), nullable=False),
    sa.Column('generate_type', sa.String(length=255), nullable=False),
    sa.Column('generated_text', sa.Text(), nullable=False),
    sa.Column('tweet_url', sa.String(length=255), nullable=True),
    sa.Column('cost', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.BigInteger(), nullable=False),
    sa.Column('updated_at', sa.BigInteger(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('prompt_reference',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('ref_url', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('prompt_reference')
    op.drop_table('generate_history')
    # ### end Alembic commands ###
