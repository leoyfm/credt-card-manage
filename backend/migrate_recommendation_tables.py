#!/usr/bin/env python3
"""
推荐模块数据库迁移脚本

创建推荐规则表和推荐记录表，包括索引、触发器和示例数据
"""

import os
import sys
import asyncio
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from app.db.database import engine
from app.core.config import settings


async def run_migration():
    """执行推荐模块数据库迁移"""
    
    print("🚀 开始执行推荐模块数据库迁移...")
    
    try:
        # 读取SQL迁移文件
        sql_file_path = project_root / "migrations" / "create_recommendation_tables.sql"
        
        if not sql_file_path.exists():
            print(f"❌ 迁移文件不存在: {sql_file_path}")
            return False
            
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        
        print(f"📖 读取迁移文件: {sql_file_path}")
        
        # 执行迁移
        with engine.connect() as connection:
            # 开始事务
            trans = connection.begin()
            
            try:
                print("📝 执行数据库迁移...")
                
                # 分割SQL语句并逐个执行
                sql_statements = [stmt.strip() for stmt in migration_sql.split(';') if stmt.strip()]
                
                for i, statement in enumerate(sql_statements, 1):
                    if statement:
                        print(f"   执行语句 {i}/{len(sql_statements)}: {statement[:50]}...")
                        connection.execute(text(statement))
                
                # 提交事务
                trans.commit()
                print("✅ 数据库迁移执行成功!")
                
                # 验证表创建
                print("\n🔍 验证表创建结果...")
                
                # 检查推荐规则表
                result = connection.execute(text("""
                    SELECT COUNT(*) as count 
                    FROM information_schema.tables 
                    WHERE table_name = 'recommendation_rules'
                """))
                rules_table_exists = result.fetchone()[0] > 0
                
                # 检查推荐记录表
                result = connection.execute(text("""
                    SELECT COUNT(*) as count 
                    FROM information_schema.tables 
                    WHERE table_name = 'recommendation_records'
                """))
                records_table_exists = result.fetchone()[0] > 0
                
                # 检查示例数据
                result = connection.execute(text("""
                    SELECT COUNT(*) as count 
                    FROM recommendation_rules
                """))
                sample_rules_count = result.fetchone()[0]
                
                print(f"   📋 推荐规则表: {'✅ 已创建' if rules_table_exists else '❌ 未创建'}")
                print(f"   📋 推荐记录表: {'✅ 已创建' if records_table_exists else '❌ 未创建'}")
                print(f"   📊 示例规则数量: {sample_rules_count}")
                
                if rules_table_exists and records_table_exists:
                    print("\n🎉 推荐模块数据库迁移完成!")
                    
                    # 显示表结构信息
                    print("\n📊 表结构信息:")
                    
                    # 推荐规则表字段
                    result = connection.execute(text("""
                        SELECT column_name, data_type, is_nullable
                        FROM information_schema.columns 
                        WHERE table_name = 'recommendation_rules'
                        ORDER BY ordinal_position
                    """))
                    
                    print("   推荐规则表字段:")
                    for row in result:
                        nullable = "可空" if row[2] == "YES" else "非空"
                        print(f"     - {row[0]}: {row[1]} ({nullable})")
                    
                    # 推荐记录表字段
                    result = connection.execute(text("""
                        SELECT column_name, data_type, is_nullable
                        FROM information_schema.columns 
                        WHERE table_name = 'recommendation_records'
                        ORDER BY ordinal_position
                    """))
                    
                    print("   推荐记录表字段:")
                    for row in result:
                        nullable = "可空" if row[2] == "YES" else "非空"
                        print(f"     - {row[0]}: {row[1]} ({nullable})")
                    
                    # 显示示例规则
                    if sample_rules_count > 0:
                        print(f"\n📝 示例推荐规则 ({sample_rules_count}条):")
                        result = connection.execute(text("""
                            SELECT rule_name, rule_type, priority, is_active
                            FROM recommendation_rules
                            ORDER BY priority DESC
                        """))
                        
                        for row in result:
                            status = "激活" if row[3] else "禁用"
                            print(f"     - {row[0]} ({row[1]}) - 优先级:{row[2]} - {status}")
                    
                    return True
                else:
                    print("❌ 表创建验证失败!")
                    return False
                    
            except Exception as e:
                # 回滚事务
                trans.rollback()
                print(f"❌ 迁移执行失败: {str(e)}")
                return False
                
    except Exception as e:
        print(f"❌ 迁移过程出错: {str(e)}")
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("推荐模块数据库迁移工具")
    print("=" * 60)
    print(f"数据库: {settings.DATABASE_URL}")
    print(f"调试模式: {settings.DEBUG}")
    print("=" * 60)
    
    # 执行迁移
    try:
        success = asyncio.run(run_migration())
        
        if success:
            print("\n🎉 推荐模块迁移完成!")
            print("\n📋 后续步骤:")
            print("   1. 重启应用服务器")
            print("   2. 测试推荐API接口")
            print("   3. 验证推荐功能正常工作")
        else:
            print("\n❌ 迁移失败，请检查错误信息")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n❌ 迁移被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 迁移过程出现异常: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 