"""修改信用卡有效期格式_从完整日期改为年月格式

Revision ID: bd368dd8de8b
Revises: 847bc5119087
Create Date: 2025-06-08 22:48:16.120558

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bd368dd8de8b'
down_revision = '847bc5119087'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """升级数据库架构"""
    # 1. 添加新的年月字段（先设为可空）
    with op.batch_alter_table('credit_cards', schema=None) as batch_op:
        batch_op.add_column(sa.Column('expiry_month', sa.Integer(), nullable=True, comment='卡片有效期月份，1-12'))
        batch_op.add_column(sa.Column('expiry_year', sa.Integer(), nullable=True, comment='卡片有效期年份，如2024'))
    
    # 2. 从原有的expiry_date提取年月数据并填充到新字段
    connection = op.get_bind()
    connection.execute(sa.text("""
        UPDATE credit_cards 
        SET expiry_month = EXTRACT(MONTH FROM expiry_date),
            expiry_year = EXTRACT(YEAR FROM expiry_date)
        WHERE expiry_date IS NOT NULL
    """))
    
    # 3. 设置新字段为非空约束
    with op.batch_alter_table('credit_cards', schema=None) as batch_op:
        batch_op.alter_column('expiry_month', nullable=False)
        batch_op.alter_column('expiry_year', nullable=False)
        
        # 4. 删除旧字段和索引，创建新索引
        batch_op.drop_index('idx_credit_cards_expiry_date')
        batch_op.create_index('idx_credit_cards_expiry', ['expiry_year', 'expiry_month'], unique=False)
        batch_op.drop_column('expiry_date')


def downgrade() -> None:
    """回滚数据库架构"""
    # 1. 添加原有的expiry_date字段（先设为可空）
    with op.batch_alter_table('credit_cards', schema=None) as batch_op:
        batch_op.add_column(sa.Column('expiry_date', sa.DATE(), autoincrement=False, nullable=True, comment='卡片有效期'))
    
    # 2. 从年月字段重建日期（设为当月最后一天）
    connection = op.get_bind()
    connection.execute(sa.text("""
        UPDATE credit_cards 
        SET expiry_date = (
            DATE_TRUNC('month', MAKE_DATE(expiry_year, expiry_month, 1)) + INTERVAL '1 month - 1 day'
        )::DATE
        WHERE expiry_month IS NOT NULL AND expiry_year IS NOT NULL
    """))
    
    # 3. 设置expiry_date为非空，删除年月字段
    with op.batch_alter_table('credit_cards', schema=None) as batch_op:
        batch_op.alter_column('expiry_date', nullable=False)
        batch_op.drop_index('idx_credit_cards_expiry')
        batch_op.create_index('idx_credit_cards_expiry_date', ['expiry_date'], unique=False)
        batch_op.drop_column('expiry_year')
        batch_op.drop_column('expiry_month') 