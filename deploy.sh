#!/bin/bash

# 信用卡管理系统 Docker 部署脚本

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 打印彩色消息
print_message() {
    echo -e "${GREEN}[信息]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[警告]${NC} $1"
}

print_error() {
    echo -e "${RED}[错误]${NC} $1"
}

# 检查Docker是否安装
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi
    
    print_message "Docker 环境检查通过"
}

# 生产环境部署
deploy_production() {
    print_message "开始生产环境部署..."
    
    # 停止并删除现有容器
    docker-compose down
    
    # 构建并启动服务
    docker-compose up -d --build
    
    print_message "等待服务启动..."
    sleep 10
    
    # 检查服务状态
    docker-compose ps
    
    print_message "生产环境部署完成！"
    print_message "前端地址: http://localhost"
    print_message "后端API: http://localhost:8000"
    print_message "数据库管理: http://localhost:8080"
}

# 开发环境部署
deploy_development() {
    print_message "开始开发环境部署..."
    
    # 停止并删除现有容器
    docker-compose -f docker-compose.dev.yml down
    
    # 构建并启动服务
    docker-compose -f docker-compose.dev.yml up -d --build
    
    print_message "等待服务启动..."
    sleep 10
    
    # 检查服务状态
    docker-compose -f docker-compose.dev.yml ps
    
    print_message "开发环境部署完成！"
    print_message "后端API: http://localhost:8001 (支持热重载)"
    print_message "数据库管理: http://localhost:8081"
}

# 停止服务
stop_services() {
    print_message "停止所有服务..."
    docker-compose down
    docker-compose -f docker-compose.dev.yml down
    print_message "服务已停止"
}

# 查看日志
view_logs() {
    echo "选择要查看日志的服务:"
    echo "1) 后端服务"
    echo "2) 前端服务"
    echo "3) 数据库"
    echo "4) Redis"
    echo "5) 所有服务"
    read -p "请输入选项 (1-5): " choice
    
    case $choice in
        1) docker-compose logs -f backend ;;
        2) docker-compose logs -f frontend ;;
        3) docker-compose logs -f postgres ;;
        4) docker-compose logs -f redis ;;
        5) docker-compose logs -f ;;
        *) print_error "无效选项" ;;
    esac
}

# 数据库备份
backup_database() {
    print_message "开始数据库备份..."
    BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql"
    docker-compose exec postgres pg_dump -U credit_user credit_card_db > $BACKUP_FILE
    print_message "数据库已备份到: $BACKUP_FILE"
}

# 清理未使用的镜像和容器
cleanup() {
    print_warning "这将删除未使用的Docker镜像和容器"
    read -p "确认继续? (y/N): " confirm
    if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
        docker system prune -f
        print_message "清理完成"
    fi
}

# 主菜单
main_menu() {
    echo ""
    echo "============================================"
    echo "       信用卡管理系统 - 部署管理工具"
    echo "============================================"
    echo "1) 生产环境部署"
    echo "2) 开发环境部署"
    echo "3) 停止所有服务"
    echo "4) 查看服务日志"
    echo "5) 数据库备份"
    echo "6) 清理Docker资源"
    echo "7) 退出"
    echo "============================================"
    read -p "请选择操作 (1-7): " choice
    
    case $choice in
        1) deploy_production ;;
        2) deploy_development ;;
        3) stop_services ;;
        4) view_logs ;;
        5) backup_database ;;
        6) cleanup ;;
        7) exit 0 ;;
        *) print_error "无效选项，请重新选择" ;;
    esac
}

# 主程序
main() {
    check_docker
    
    if [ $# -eq 0 ]; then
        # 交互模式
        while true; do
            main_menu
        done
    else
        # 命令行参数模式
        case $1 in
            "prod") deploy_production ;;
            "dev") deploy_development ;;
            "stop") stop_services ;;
            "logs") view_logs ;;
            "backup") backup_database ;;
            "cleanup") cleanup ;;
            *) 
                echo "用法: $0 [prod|dev|stop|logs|backup|cleanup]"
                echo "或直接运行 $0 进入交互模式"
                exit 1
                ;;
        esac
    fi
}

main "$@" 