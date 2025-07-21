#!/bin/bash

# 职位与面试系统 - 快速启动脚本
# 作者: 面试星途开发团队
# 版本: v1.0

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        log_error "$1 未安装，请先安装 $1"
        exit 1
    fi
}

# 显示帮助信息
show_help() {
    echo "职位与面试系统 - 快速启动脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  docker          使用Docker启动（推荐）"
    echo "  stop            停止所有服务"
    echo "  status          查看服务状态"
    echo "  help            显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 docker       # 使用Docker启动系统"
    echo "  $0 stop         # 停止所有服务"
    echo ""
}

# Docker启动
start_docker() {
    log_info "使用Docker启动系统..."

    # 检查Docker是否安装
    check_command docker
    check_command docker-compose

    # 检查环境变量文件
    if [ ! -f .env ]; then
        log_warning ".env 文件不存在，从示例文件创建..."
        cp .env.example .env
        log_warning "请编辑 .env 文件并填入正确的配置值"
        read -p "按回车键继续..."
    fi

    # 构建并启动服务
    log_info "构建Docker镜像..."
    docker-compose build

    log_info "启动服务..."
    docker-compose up -d

    # 等待服务启动
    log_info "等待服务启动..."
    sleep 30

    # 检查服务状态
    check_services_docker
}

# 显示访问信息
show_access_info() {
    echo ""
    log_success "=== 系统启动成功 ==="
    echo ""
    echo "🌐 前端地址: http://localhost:8080"
    echo "🔧 后端API: http://localhost:5000"
    echo ""
    echo "📝 查看日志: $0 logs"
    echo "📊 查看状态: $0 status"
    echo "🛑 停止服务: $0 stop"
    echo ""
}

# 检查服务状态
check_services_docker() {
    log_info "检查Docker服务状态..."
    docker-compose ps

    show_access_info
}

# 停止服务
stop_services() {
    log_info "停止服务..."

    if [ -f docker-compose.yml ] && docker-compose ps | grep -q "Up"; then
        log_info "停止Docker服务..."
        docker-compose down
    fi

    log_success "所有服务已停止"
}

# 主函数
main() {
    case "${1:-docker}" in
        "docker")
            start_docker
            ;;
        "stop")
            stop_services
            ;;
        "status")
            check_services_docker
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            log_error "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"