#!/bin/bash

# 腾讯云快速部署脚本
# 使用方法: bash deploy.sh

set -e

echo "🚀 开始部署面试星途系统..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否为root用户
check_root() {
    if [ "$EUID" -eq 0 ]; then
        print_warning "检测到root用户，建议使用普通用户运行"
    fi
}

# 检查系统环境
check_system() {
    print_message "检查系统环境..."
    
    # 检查操作系统
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        print_message "操作系统: Linux ✓"
    else
        print_error "不支持的操作系统: $OSTYPE"
        exit 1
    fi
    
    # 检查Docker
    if command -v docker &> /dev/null; then
        print_message "Docker已安装 ✓"
        docker --version
    else
        print_error "Docker未安装，请先安装Docker"
        exit 1
    fi
    
    # 检查Docker Compose
    if command -v docker-compose &> /dev/null; then
        print_message "Docker Compose已安装 ✓"
        docker-compose --version
    else
        print_error "Docker Compose未安装，请先安装Docker Compose"
        exit 1
    fi
}

# 创建环境变量文件
create_env_file() {
    print_message "创建环境变量文件..."
    
    if [ ! -f .env ]; then
        cp .env.example .env
        print_message "已创建.env文件，请编辑配置"
        
        # 生成随机密钥
        SECRET_KEY=$(openssl rand -base64 32)
        JWT_SECRET_KEY=$(openssl rand -base64 32)
        
        # 替换默认密钥
        sed -i "s/your-super-secret-key-change-this-in-production/$SECRET_KEY/g" .env
        sed -i "s/your-jwt-secret-key-change-this-too/$JWT_SECRET_KEY/g" .env
        
        print_message "已生成随机密钥"
    else
        print_message ".env文件已存在"
    fi
}

# 创建必要目录
create_directories() {
    print_message "创建必要目录..."
    
    mkdir -p merged-project-flask/logs
    mkdir -p merged-project-flask/uploads
    mkdir -p nginx/ssl
    
    print_message "目录创建完成"
}

# 构建和启动服务
deploy_services() {
    print_message "构建和启动服务..."
    
    # 停止现有服务
    docker-compose -f docker-compose.prod.yml down 2>/dev/null || true
    
    # 构建镜像
    print_message "构建Docker镜像..."
    docker-compose -f docker-compose.prod.yml build --no-cache
    
    # 启动服务
    print_message "启动服务..."
    docker-compose -f docker-compose.prod.yml up -d
    
    print_message "等待服务启动..."
    sleep 30
}

# 检查服务状态
check_services() {
    print_message "检查服务状态..."
    
    # 检查容器状态
    docker-compose -f docker-compose.prod.yml ps
    
    # 检查服务健康状态
    print_message "检查数据库连接..."
    if docker-compose -f docker-compose.prod.yml exec -T database mysqladmin ping -h localhost --silent; then
        print_message "数据库连接正常 ✓"
    else
        print_error "数据库连接失败"
    fi
    
    print_message "检查后端服务..."
    if curl -f http://localhost:5000/api/health &>/dev/null; then
        print_message "后端服务正常 ✓"
    else
        print_warning "后端服务可能未完全启动，请稍后检查"
    fi
    
    print_message "检查前端服务..."
    if curl -f http://localhost:8080 &>/dev/null; then
        print_message "前端服务正常 ✓"
    else
        print_warning "前端服务可能未完全启动，请稍后检查"
    fi
}

# 显示访问信息
show_access_info() {
    print_message "部署完成！"
    echo ""
    echo "🎉 面试星途系统已成功部署！"
    echo ""
    echo "📱 访问地址:"
    echo "   前端: http://$(curl -s ifconfig.me):8080"
    echo "   后端API: http://$(curl -s ifconfig.me):5000"
    echo ""
    echo "🔧 管理命令:"
    echo "   查看日志: docker-compose -f docker-compose.prod.yml logs -f"
    echo "   重启服务: docker-compose -f docker-compose.prod.yml restart"
    echo "   停止服务: docker-compose -f docker-compose.prod.yml down"
    echo ""
    echo "⚠️  重要提醒:"
    echo "   1. 请确保防火墙已开放8080和5000端口"
    echo "   2. 请编辑.env文件配置AI服务密钥"
    echo "   3. 建议配置域名和SSL证书"
    echo ""
}

# 主函数
main() {
    print_message "腾讯云面试星途系统快速部署脚本"
    echo ""
    
    check_root
    check_system
    create_env_file
    create_directories
    deploy_services
    check_services
    show_access_info
}

# 执行主函数
main "$@"
