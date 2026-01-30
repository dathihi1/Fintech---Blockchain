"""Initial migration with User model

Revision ID: 001
Revises:
Create Date: 2026-01-30

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('is_superuser', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    # Create trades table
    op.create_table(
        'trades',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('symbol', sa.String(), nullable=False),
        sa.Column('side', sa.String(), nullable=False),
        sa.Column('entry_price', sa.Float(), nullable=False),
        sa.Column('exit_price', sa.Float(), nullable=True),
        sa.Column('quantity', sa.Float(), nullable=False),
        sa.Column('leverage', sa.Integer(), nullable=True, default=1),
        sa.Column('entry_time', sa.DateTime(), nullable=True),
        sa.Column('exit_time', sa.DateTime(), nullable=True),
        sa.Column('hold_duration_minutes', sa.Integer(), nullable=True),
        sa.Column('pnl', sa.Float(), nullable=True),
        sa.Column('pnl_pct', sa.Float(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('nlp_sentiment', sa.Float(), nullable=True),
        sa.Column('nlp_emotions', sa.JSON(), nullable=True),
        sa.Column('nlp_quality_score', sa.Float(), nullable=True),
        sa.Column('behavioral_flags', sa.JSON(), nullable=True),
        sa.Column('market_context', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_trades_id'), 'trades', ['id'], unique=False)
    op.create_index(op.f('ix_trades_symbol'), 'trades', ['symbol'], unique=False)
    op.create_index(op.f('ix_trades_user_id'), 'trades', ['user_id'], unique=False)

    # Create nlp_analyses table
    op.create_table(
        'nlp_analyses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('trade_id', sa.Integer(), nullable=True),
        sa.Column('language', sa.String(), nullable=True),
        sa.Column('sentiment_score', sa.Float(), nullable=True),
        sa.Column('sentiment_label', sa.String(), nullable=True),
        sa.Column('emotions', sa.JSON(), nullable=True),
        sa.Column('behavioral_flags', sa.JSON(), nullable=True),
        sa.Column('quality_score', sa.Float(), nullable=True),
        sa.Column('warnings', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['trade_id'], ['trades.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_nlp_analyses_id'), 'nlp_analyses', ['id'], unique=False)
    op.create_index(op.f('ix_nlp_analyses_trade_id'), 'nlp_analyses', ['trade_id'], unique=False)

    # Create behavioral_alerts table
    op.create_table(
        'behavioral_alerts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('trade_id', sa.Integer(), nullable=True),
        sa.Column('alert_type', sa.String(), nullable=False),
        sa.Column('severity', sa.String(), nullable=False),
        sa.Column('score', sa.Integer(), nullable=True),
        sa.Column('reasons', sa.JSON(), nullable=True),
        sa.Column('recommendation', sa.Text(), nullable=True),
        sa.Column('acknowledged', sa.Boolean(), nullable=True, default=False),
        sa.Column('acknowledged_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['trade_id'], ['trades.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_behavioral_alerts_created_at'), 'behavioral_alerts', ['created_at'], unique=False)
    op.create_index(op.f('ix_behavioral_alerts_id'), 'behavioral_alerts', ['id'], unique=False)
    op.create_index(op.f('ix_behavioral_alerts_user_id'), 'behavioral_alerts', ['user_id'], unique=False)

    # Create user_sessions table
    op.create_table(
        'user_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('session_start', sa.DateTime(), nullable=True),
        sa.Column('session_pnl', sa.Float(), nullable=True, default=0.0),
        sa.Column('trade_count', sa.Integer(), nullable=True, default=0),
        sa.Column('win_count', sa.Integer(), nullable=True, default=0),
        sa.Column('loss_count', sa.Integer(), nullable=True, default=0),
        sa.Column('peak_balance', sa.Float(), nullable=True, default=0.0),
        sa.Column('current_drawdown_pct', sa.Float(), nullable=True, default=0.0),
        sa.Column('last_trade_pnl', sa.Float(), nullable=True),
        sa.Column('last_trade_time', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_sessions_id'), 'user_sessions', ['id'], unique=False)
    op.create_index(op.f('ix_user_sessions_user_id'), 'user_sessions', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_user_sessions_user_id'), table_name='user_sessions')
    op.drop_index(op.f('ix_user_sessions_id'), table_name='user_sessions')
    op.drop_table('user_sessions')

    op.drop_index(op.f('ix_behavioral_alerts_user_id'), table_name='behavioral_alerts')
    op.drop_index(op.f('ix_behavioral_alerts_id'), table_name='behavioral_alerts')
    op.drop_index(op.f('ix_behavioral_alerts_created_at'), table_name='behavioral_alerts')
    op.drop_table('behavioral_alerts')

    op.drop_index(op.f('ix_nlp_analyses_trade_id'), table_name='nlp_analyses')
    op.drop_index(op.f('ix_nlp_analyses_id'), table_name='nlp_analyses')
    op.drop_table('nlp_analyses')

    op.drop_index(op.f('ix_trades_user_id'), table_name='trades')
    op.drop_index(op.f('ix_trades_symbol'), table_name='trades')
    op.drop_index(op.f('ix_trades_id'), table_name='trades')
    op.drop_table('trades')

    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
