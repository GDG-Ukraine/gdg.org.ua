"""Added hidden field in events table

Revision ID: 30911189537
Revises: 2110c1a297
Create Date: 2015-07-14 11:11:21.016545

"""

# revision identifiers, used by Alembic.
revision = '30911189537'
down_revision = '2110c1a297'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import GDGUkraine.model


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('gdg_events', sa.Column('hidden', GDGUkraine.model.JSONEncodedDict(length=512), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('gdg_events', 'hidden')
    ### end Alembic commands ###