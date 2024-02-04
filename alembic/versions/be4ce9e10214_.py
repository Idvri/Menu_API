"""empty message

Revision ID: be4ce9e10214
Revises: 48562e213a7e
Create Date: 2024-01-19 22:31:38.650043

"""
from typing import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'be4ce9e10214'
down_revision: str | None = '48562e213a7e'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('menu',
                    sa.Column('id', sa.Uuid(), nullable=False),
                    sa.Column('title', sa.String(), nullable=False),
                    sa.Column('description', sa.Text(), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('submenu',
                    sa.Column('menu_id', sa.Uuid(), nullable=False),
                    sa.Column('id', sa.Uuid(), nullable=False),
                    sa.Column('title', sa.String(), nullable=False),
                    sa.Column('description', sa.Text(), nullable=False),
                    sa.ForeignKeyConstraint(['menu_id'], ['menu.id'], ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('dish',
                    sa.Column('price', sa.Float(), nullable=False),
                    sa.Column('submenu_id', sa.Uuid(), nullable=False),
                    sa.Column('id', sa.Uuid(), nullable=False),
                    sa.Column('title', sa.String(), nullable=False),
                    sa.Column('description', sa.Text(), nullable=False),
                    sa.ForeignKeyConstraint(['submenu_id'], ['submenu.id'], ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id')
                    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('dish')
    op.drop_table('submenu')
    op.drop_table('menu')
    # ### end Alembic commands ###
