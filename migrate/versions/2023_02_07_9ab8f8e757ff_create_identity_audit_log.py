"""Create identity audit log

Revision ID: 9ab8f8e757ff
Revises: e91656ef5b71
Create Date: 2023-02-07 12:17:41.383485

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9ab8f8e757ff'
down_revision = 'e91656ef5b71'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic ###
    op.create_table('identity_audit',
    sa.Column('id', sa.Integer(), sa.Identity(always=False), nullable=False),
    sa.Column('client_id', sa.String(), nullable=False),
    sa.Column('user_id', sa.String(), nullable=True),
    sa.Column('command', sa.Enum('signup', 'login', 'verify_email', 'change_password', 'create', 'edit', 'delete', name='identitycommand'), nullable=False),
    sa.Column('completed', sa.Boolean(), nullable=False),
    sa.Column('error', sa.String(), nullable=True),
    sa.Column('timestamp', sa.TIMESTAMP(timezone=True), nullable=False),
    sa.Column('_id', sa.String(), nullable=True),
    sa.Column('_email', sa.String(), nullable=True),
    sa.Column('_active', sa.String(), nullable=True),
    sa.Column('_roles', sa.ARRAY(sa.String()), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic ###
    op.drop_table('identity_audit')
    # ### end Alembic commands ###