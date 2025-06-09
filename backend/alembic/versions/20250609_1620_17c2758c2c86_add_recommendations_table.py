"""Add recommendations table

Revision ID: 17c2758c2c86
Revises: bd368dd8de8b
Create Date: 2025-06-09 16:20:47.491326

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON, ENUM


# revision identifiers, used by Alembic.
revision = '17c2758c2c86'
down_revision = 'bd368dd8de8b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """升级数据库架构 - 创建推荐表"""
    # 创建枚举类型（如果不存在）
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'recommendationtype') THEN
                CREATE TYPE recommendationtype AS ENUM ('cashback', 'points', 'travel', 'dining', 'shopping', 'fuel');
            END IF;
        END
        $$;
    """)
    
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'recommendationstatus') THEN
                CREATE TYPE recommendationstatus AS ENUM ('active', 'expired', 'applied', 'rejected');
            END IF;
        END
        $$;
    """)
    
    op.create_table(
        'recommendations',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        
        # 用户关联
        sa.Column('user_id', UUID(as_uuid=True), nullable=False, comment='用户ID，推荐的目标用户'),
        
        # 银行和卡片信息
        sa.Column('bank_name', sa.String(50), nullable=False, comment='银行名称'),
        sa.Column('card_name', sa.String(100), nullable=False, comment='信用卡名称'),
        
        # 推荐信息
        sa.Column('recommendation_type', ENUM('cashback', 'points', 'travel', 'dining', 'shopping', 'fuel', name='recommendationtype', create_type=False), nullable=False, comment='推荐类型'),
        sa.Column('title', sa.String(100), nullable=False, comment='推荐标题'),
        sa.Column('description', sa.Text(), nullable=False, comment='推荐描述'),
        
        # 卡片特性
        sa.Column('features', JSON, comment='卡片特色功能列表，JSON格式存储'),
        sa.Column('annual_fee', sa.Numeric(8, 2), default=0, comment='年费金额'),
        sa.Column('credit_limit_range', sa.String(50), nullable=False, comment='额度范围'),
        
        # 推荐评分
        sa.Column('approval_difficulty', sa.Integer(), nullable=False, comment='申请难度等级，1-5分'),
        sa.Column('recommendation_score', sa.Numeric(5, 2), nullable=False, comment='推荐分数，0-100分'),
        
        # 推荐理由
        sa.Column('match_reasons', JSON, comment='匹配原因列表，JSON格式存储'),
        sa.Column('pros', JSON, comment='优点列表，JSON格式存储'),
        sa.Column('cons', JSON, comment='缺点列表，JSON格式存储'),
        
        # 申请信息
        sa.Column('apply_url', sa.String(500), comment='申请链接'),
        
        # 状态信息
        sa.Column('status', ENUM('active', 'expired', 'applied', 'rejected', name='recommendationstatus', create_type=False), default='active', comment='推荐状态'),
        sa.Column('expires_at', sa.DateTime(timezone=True), comment='推荐过期时间'),
        sa.Column('is_featured', sa.Boolean(), default=False, comment='是否为精选推荐'),
        
        # 用户交互统计
        sa.Column('view_count', sa.Integer(), default=0, comment='查看次数'),
        sa.Column('last_viewed_at', sa.DateTime(timezone=True), comment='最后查看时间'),
    )
    
    # 创建索引
    op.create_index('idx_recommendations_user_id', 'recommendations', ['user_id'])
    op.create_index('idx_recommendations_type', 'recommendations', ['recommendation_type'])
    op.create_index('idx_recommendations_status', 'recommendations', ['status'])
    op.create_index('idx_recommendations_score', 'recommendations', ['recommendation_score'])
    op.create_index('idx_recommendations_bank', 'recommendations', ['bank_name'])
    op.create_index('idx_recommendations_featured', 'recommendations', ['is_featured'])
    op.create_index('idx_recommendations_user_status', 'recommendations', ['user_id', 'status'])
    op.create_index('idx_recommendations_expires', 'recommendations', ['expires_at'])


def downgrade() -> None:
    """回滚数据库架构 - 删除推荐表"""
    # 删除索引
    op.drop_index('idx_recommendations_expires', 'recommendations')
    op.drop_index('idx_recommendations_user_status', 'recommendations')
    op.drop_index('idx_recommendations_featured', 'recommendations')
    op.drop_index('idx_recommendations_bank', 'recommendations')
    op.drop_index('idx_recommendations_score', 'recommendations')
    op.drop_index('idx_recommendations_status', 'recommendations')
    op.drop_index('idx_recommendations_type', 'recommendations')
    op.drop_index('idx_recommendations_user_id', 'recommendations')
    
    # 删除表
    op.drop_table('recommendations') 