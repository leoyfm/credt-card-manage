# 信用卡管理系统 Docker 部署脚本 (PowerShell 版本)

param(
    [string]$Action = ""
)

# 颜色输出函数
function Write-ColorMessage {
    param(
        [string]$Message,
        [string]$Color = "Green"
    )
    Write-Host "[信息] $Message" -ForegroundColor $Color
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[警告] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[错误] $Message" -ForegroundColor Red
}

# 检查Docker是否安装
function Test-Docker {
    try {
        $dockerVersion = docker --version
        $composeVersion = docker-compose --version
        Write-ColorMessage "Docker 环境检查通过"
        return $true
    }
    catch {
        Write-Error "Docker 或 Docker Compose 未安装，请先安装相应软件"
        return $false
    }
}

# 生产环境部署
function Deploy-Production {
    Write-ColorMessage "开始生产环境部署..."
    
    # 停止并删除现有容器
    docker-compose down
    
    # 构建并启动服务
    docker-compose up -d --build
    
    Write-ColorMessage "等待服务启动..."
    Start-Sleep -Seconds 10
    
    # 检查服务状态
    docker-compose ps
    
    Write-ColorMessage "生产环境部署完成！"
    Write-ColorMessage "前端地址: http://localhost"
    Write-ColorMessage "后端API: http://localhost:8000"
    Write-ColorMessage "数据库管理: http://localhost:8080"
}

# 开发环境部署
function Deploy-Development {
    Write-ColorMessage "开始开发环境部署..."
    
    # 停止并删除现有容器
    docker-compose -f docker-compose.dev.yml down
    
    # 构建并启动服务
    docker-compose -f docker-compose.dev.yml up -d --build
    
    Write-ColorMessage "等待服务启动..."
    Start-Sleep -Seconds 10
    
    # 检查服务状态
    docker-compose -f docker-compose.dev.yml ps
    
    Write-ColorMessage "开发环境部署完成！"
    Write-ColorMessage "后端API: http://localhost:8001 (支持热重载)"
    Write-ColorMessage "数据库管理: http://localhost:8081"
}

# 停止服务
function Stop-Services {
    Write-ColorMessage "停止所有服务..."
    docker-compose down
    docker-compose -f docker-compose.dev.yml down
    Write-ColorMessage "服务已停止"
}

# 查看日志
function Show-Logs {
    Write-Host "选择要查看日志的服务:"
    Write-Host "1) 后端服务"
    Write-Host "2) 前端服务"
    Write-Host "3) 数据库"
    Write-Host "4) Redis"
    Write-Host "5) 所有服务"
    
    $choice = Read-Host "请输入选项 (1-5)"
    
    switch ($choice) {
        "1" { docker-compose logs -f backend }
        "2" { docker-compose logs -f frontend }
        "3" { docker-compose logs -f postgres }
        "4" { docker-compose logs -f redis }
        "5" { docker-compose logs -f }
        default { Write-Error "无效选项" }
    }
}

# 数据库备份
function Backup-Database {
    Write-ColorMessage "开始数据库备份..."
    $backupFile = "backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').sql"
    docker-compose exec postgres pg_dump -U credit_user credit_card_db | Out-File -FilePath $backupFile -Encoding UTF8
    Write-ColorMessage "数据库已备份到: $backupFile"
}

# 清理未使用的镜像和容器
function Clean-Docker {
    Write-Warning "这将删除未使用的Docker镜像和容器"
    $confirm = Read-Host "确认继续? (y/N)"
    if ($confirm -eq "y" -or $confirm -eq "Y" -or $confirm -eq "yes" -or $confirm -eq "Yes") {
        docker system prune -f
        Write-ColorMessage "清理完成"
    }
}

# 主菜单
function Show-Menu {
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host "       信用卡管理系统 - 部署管理工具" -ForegroundColor Cyan
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host "1) 生产环境部署"
    Write-Host "2) 开发环境部署"
    Write-Host "3) 停止所有服务"
    Write-Host "4) 查看服务日志"
    Write-Host "5) 数据库备份"
    Write-Host "6) 清理Docker资源"
    Write-Host "7) 退出"
    Write-Host "============================================" -ForegroundColor Cyan
    
    $choice = Read-Host "请选择操作 (1-7)"
    
    switch ($choice) {
        "1" { Deploy-Production }
        "2" { Deploy-Development }
        "3" { Stop-Services }
        "4" { Show-Logs }
        "5" { Backup-Database }
        "6" { Clean-Docker }
        "7" { exit 0 }
        default { Write-Error "无效选项，请重新选择" }
    }
}

# 主程序
function Main {
    if (-not (Test-Docker)) {
        exit 1
    }
    
    if ($Action -eq "") {
        # 交互模式
        while ($true) {
            Show-Menu
        }
    }
    else {
        # 命令行参数模式
        switch ($Action) {
            "prod" { Deploy-Production }
            "dev" { Deploy-Development }
            "stop" { Stop-Services }
            "logs" { Show-Logs }
            "backup" { Backup-Database }
            "cleanup" { Clean-Docker }
            default {
                Write-Host "用法: .\deploy.ps1 [prod|dev|stop|logs|backup|cleanup]"
                Write-Host "或直接运行 .\deploy.ps1 进入交互模式"
                exit 1
            }
        }
    }
}

# 执行主程序
Main 