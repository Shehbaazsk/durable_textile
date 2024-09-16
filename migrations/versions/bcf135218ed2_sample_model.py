"""sample model

Revision ID: bcf135218ed2
Revises: 09d425e33141
Create Date: 2024-09-17 00:53:39.436864

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bcf135218ed2'
down_revision: Union[str, None] = '09d425e33141'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('sample',
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('mill_reference_number', sa.String(length=255), nullable=True),
    sa.Column('buyer_reference_construction', sa.String(length=255), nullable=True),
    sa.Column('composition', sa.String(length=255), nullable=True),
    sa.Column('construction', sa.String(length=255), nullable=True),
    sa.Column('gsm', sa.Integer(), nullable=True),
    sa.Column('width', sa.Integer(), nullable=True),
    sa.Column('count', sa.String(length=255), nullable=True),
    sa.Column('hanger_id', sa.BigInteger(), nullable=True),
    sa.Column('sample_image_id', sa.BigInteger(), nullable=True),
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('uuid', sa.CHAR(length=50), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('is_delete', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['hanger_id'], ['hangers.id'], ),
    sa.ForeignKeyConstraint(['sample_image_id'], ['document_master.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_sample_uuid'), 'sample', ['uuid'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_sample_uuid'), table_name='sample')
    op.drop_table('sample')
    # ### end Alembic commands ###
