#!/bin/bash

# 阿里云快速部署脚本
# 一键完成从服务器初始化到项目部署的全过程

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 配置变量
GITHUB_REPO=""
DOMAIN=""
EMAIL=""
DEPLOY_USER="deploy"
PROJECT_DIR="/opt/interview-system"

# 打印函数
print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# 显示帮助信息
show_help() {
    echo "阿里云快速部署脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -r, --repo REPO         GitHub仓库地址 (必需)"
    echo "  -d, --domain DOMAIN     域名 (可选)"
    echo "  -e, --email EMAIL       邮箱地址 (SSL证书需要)"
    echo "  -h, --help              显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 -r https://github.com/username/repo.git -d example.com -e admin@example.com"
    echo "  $0 -r https://github.com/username/repo.git"
}

# 解析命令行参数
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -r|--repo)
                GITHUB_REPO="$2"
                shift 2
                ;;
            -d|--domain)
                DOMAIN="$2"
                shift 2
                ;;
            -e|--email)
                EMAIL="$2"
                shift 2
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                print_error "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 验证必需参数
    if [ -z "$GITHUB_REPO" ]; then
        print_error "GitHub仓库地址是必需的"
        show_help
        exit 1
    fi
}

# 检查系统环境
check_environment() {
    print_step "检查系统环境..."
    
    # 检查是否为root用户
    if [ "$EUID" -ne 0 ]; then
        print_error "请使用root用户运行此脚本"
        exit 1
    fi
    
    # 检查操作系统
    if [[ "$OSTYPE" != "linux-gnu"* ]]; then
        print_error "此脚本仅支持Linux系统"
        exit 1
    fi
    
    # 检查网络连接
    if ! ping -c 1 google.com &> /dev/null; then
        print_error "网络连接失败，请检查网络设置"
        exit 1
    fi
    
    print_message "系统环境检查通过"
}

# 更新系统
update_system() {
    print_step "更新系统..."
    
    apt update && apt upgrade -y
    apt install -y curl wget git vim htop unzip software-properties-common
    
    print_message "系统更新完成"
}

# 安装Docker
install_docker() {
    print_step "安装Docker..."
    
    if command -v docker &> /dev/null; then
        print_message "Docker已安装，跳过安装步骤"
        return
    fi
    
    # 卸载旧版本
    apt remove -y docker docker-engine docker.io containerd runc || true
    
    # 安装依赖
    apt install -y apt-transport-https ca-certificates curl gnupg lsb-release
    
    # 添加Docker官方GPG密钥
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    # 添加Docker仓库
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # 安装Docker
    apt update
    apt install -y docker-ce docker-ce-cli containerd.io
    
    # 启动Docker服务
    systemctl start docker
    systemctl enable docker
    
    print_message "Docker安装完成"
}

# 安装Docker Compose
install_docker_compose() {
    print_step "安装Docker Compose..."
    
    if command -v docker-compose &> /dev/null; then
        print_message "Docker Compose已安装，跳过安装步骤"
        return
    fi
    
    # 下载最新版本的Docker Compose
    DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
    curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    
    # 添加执行权限
    chmod +x /usr/local/bin/docker-compose
    
    # 创建软链接
    ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
    
    print_message "Docker Compose安装完成"
}

# 配置防火墙
configure_firewall() {
    print_step "配置防火墙..."
    
    # 安装ufw
    apt install -y ufw
    
    # 重置防火墙规则
    ufw --force reset
    
    # 设置默认策略
    ufw default deny incoming
    ufw default allow outgoing
    
    # 允许SSH
    ufw allow 22/tcp
    
    # 允许HTTP和HTTPS
    ufw allow 80/tcp
    ufw allow 443/tcp
    
    # 启用防火墙
    ufw --force enable
    
    print_message "防火墙配置完成"
}

# 创建部署用户
create_deploy_user() {
    print_step "创建部署用户..."
    
    # 创建用户
    if ! id "$DEPLOY_USER" &>/dev/null; then
        useradd -m -s /bin/bash "$DEPLOY_USER"
        print_message "用户 $DEPLOY_USER 创建成功"
    else
        print_message "用户 $DEPLOY_USER 已存在"
    fi
    
    # 添加到docker组
    usermod -aG docker "$DEPLOY_USER"
    
    # 创建SSH目录
    mkdir -p "/home/$DEPLOY_USER/.ssh"
    chmod 700 "/home/$DEPLOY_USER/.ssh"
    chown -R "$DEPLOY_USER:$DEPLOY_USER" "/home/$DEPLOY_USER/.ssh"
    
    print_message "部署用户配置完成"
}

# 创建项目目录
create_project_directory() {
    print_step "创建项目目录..."
    
    mkdir -p "$PROJECT_DIR"
    chown -R "$DEPLOY_USER:$DEPLOY_USER" "$PROJECT_DIR"
    
    # 创建日志目录
    mkdir -p /var/log/interview-system
    chown -R "$DEPLOY_USER:$DEPLOY_USER" /var/log/interview-system
    
    print_message "项目目录创建完成"
}

# 克隆项目
clone_project() {
    print_step "克隆项目..."
    
    # 切换到deploy用户执行
    sudo -u "$DEPLOY_USER" bash << EOF
        cd "$PROJECT_DIR"
        
        # 克隆项目
        if [ -d ".git" ]; then
            print_message "项目已存在，拉取最新代码..."
            git pull origin main
        else
            print_message "克隆项目..."
            git clone "$GITHUB_REPO" .
        fi
        
        # 配置Git
        git config user.name "Deploy Bot"
        git config user.email "deploy@example.com"
EOF
    
    print_message "项目克隆完成"
}

# 配置环境变量
configure_environment() {
    print_step "配置环境变量..."
    
    cd "$PROJECT_DIR"
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.production" ]; then
            cp .env.production .env
            print_message "已复制生产环境配置"
        else
            print_warning "未找到环境变量模板，请手动创建.env文件"
            return
        fi
    fi
    
    # 生成随机密钥
    SECRET_KEY=$(openssl rand -base64 32)
    JWT_SECRET_KEY=$(openssl rand -base64 32)
    MYSQL_ROOT_PASSWORD=$(openssl rand -base64 16)
    MYSQL_PASSWORD=$(openssl rand -base64 16)
    
    # 更新环境变量
    sed -i "s/your-production-secret-key-change-this/$SECRET_KEY/g" .env
    sed -i "s/your-jwt-secret-key-change-this/$JWT_SECRET_KEY/g" .env
    sed -i "s/YourStrongRootPassword2024!/$MYSQL_ROOT_PASSWORD/g" .env
    sed -i "s/YourStrongUserPassword2024!/$MYSQL_PASSWORD/g" .env
    
    if [ ! -z "$DOMAIN" ]; then
        sed -i "s/your-domain\.com/$DOMAIN/g" .env
    fi
    
    # 设置权限
    chmod 600 .env
    chown "$DEPLOY_USER:$DEPLOY_USER" .env
    
    print_message "环境变量配置完成"
    print_warning "请编辑 $PROJECT_DIR/.env 文件配置API密钥"
}

# 安装Nginx
install_nginx() {
    print_step "安装Nginx..."
    
    if command -v nginx &> /dev/null; then
        print_message "Nginx已安装，跳过安装步骤"
        return
    fi
    
    apt install -y nginx
    
    # 启动Nginx
    systemctl start nginx
    systemctl enable nginx
    
    # 创建SSL目录
    mkdir -p /etc/nginx/ssl
    
    print_message "Nginx安装完成"
}

# 配置SSL证书
configure_ssl() {
    if [ ! -z "$DOMAIN" ] && [ ! -z "$EMAIL" ]; then
        print_step "配置SSL证书..."
        
        # 运行SSL配置脚本
        if [ -f "$PROJECT_DIR/scripts/setup-ssl.sh" ]; then
            bash "$PROJECT_DIR/scripts/setup-ssl.sh" -d "$DOMAIN" -e "$EMAIL" -t letsencrypt
        else
            print_warning "SSL配置脚本不存在，跳过SSL配置"
        fi
    else
        print_warning "未提供域名或邮箱，跳过SSL配置"
    fi
}

# 首次部署
initial_deployment() {
    print_step "执行首次部署..."
    
    cd "$PROJECT_DIR"
    
    # 切换到deploy用户执行
    sudo -u "$DEPLOY_USER" bash << 'EOF'
        # 创建必要目录
        mkdir -p merged-project-flask/logs
        mkdir -p merged-project-flask/uploads
        
        # 启动服务
        docker-compose -f docker-compose.prod.yml up -d
        
        # 等待服务启动
        sleep 30
        
        # 检查服务状态
        docker-compose -f docker-compose.prod.yml ps
EOF
    
    print_message "首次部署完成"
}

# 验证部署
verify_deployment() {
    print_step "验证部署..."
    
    # 等待服务完全启动
    sleep 10
    
    # 检查后端健康状态
    if curl -f http://localhost:5000/api/health &> /dev/null; then
        print_message "后端服务正常"
    else
        print_warning "后端服务可能未完全启动"
    fi
    
    # 检查前端服务
    if curl -f http://localhost:8080 &> /dev/null; then
        print_message "前端服务正常"
    else
        print_warning "前端服务可能未完全启动"
    fi
    
    # 检查容器状态
    cd "$PROJECT_DIR"
    RUNNING_CONTAINERS=$(docker-compose -f docker-compose.prod.yml ps --services --filter "status=running" | wc -l)
    TOTAL_CONTAINERS=$(docker-compose -f docker-compose.prod.yml ps --services | wc -l)
    
    print_message "运行中的容器: $RUNNING_CONTAINERS/$TOTAL_CONTAINERS"
}

# 创建监控脚本
setup_monitoring() {
    print_step "设置监控..."
    
    # 创建监控脚本
    cat > /opt/interview-system/monitor.sh << 'EOF'
#!/bin/bash
LOG_FILE="/var/log/interview-system/monitor.log"

# 检查Docker服务
if ! systemctl is-active --quiet docker; then
    echo "$(date): Docker服务异常，正在重启..." >> $LOG_FILE
    systemctl restart docker
fi

# 检查应用服务
cd /opt/interview-system
if ! docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
    echo "$(date): 应用容器异常，正在重启..." >> $LOG_FILE
    docker-compose -f docker-compose.prod.yml restart
fi

# 清理日志
find /var/log/interview-system -name "*.log" -mtime +7 -delete
find /opt/interview-system/merged-project-flask/logs -name "*.log" -mtime +7 -delete

echo "$(date): 监控检查完成" >> $LOG_FILE
EOF

    chmod +x /opt/interview-system/monitor.sh
    chown "$DEPLOY_USER:$DEPLOY_USER" /opt/interview-system/monitor.sh
    
    # 添加到crontab
    (crontab -u "$DEPLOY_USER" -l 2>/dev/null; echo "*/5 * * * * /opt/interview-system/monitor.sh") | crontab -u "$DEPLOY_USER" -
    
    print_message "监控设置完成"
}

# 显示完成信息
show_completion_info() {
    print_message "部署完成！"
    echo ""
    echo "🎉 AI面试系统已成功部署到阿里云！"
    echo ""
    echo "📱 访问地址:"
    SERVER_IP=$(curl -s ifconfig.me)
    echo "   前端: http://$SERVER_IP:8080"
    echo "   后端API: http://$SERVER_IP:5000"
    
    if [ ! -z "$DOMAIN" ]; then
        echo "   域名: https://$DOMAIN"
    fi
    
    echo ""
    echo "🔧 管理命令:"
    echo "   查看日志: cd $PROJECT_DIR && docker-compose -f docker-compose.prod.yml logs -f"
    echo "   重启服务: cd $PROJECT_DIR && docker-compose -f docker-compose.prod.yml restart"
    echo "   停止服务: cd $PROJECT_DIR && docker-compose -f docker-compose.prod.yml down"
    echo ""
    echo "📁 重要文件:"
    echo "   项目目录: $PROJECT_DIR"
    echo "   环境配置: $PROJECT_DIR/.env"
    echo "   监控日志: /var/log/interview-system/monitor.log"
    echo ""
    echo "⚠️  下一步操作:"
    echo "1. 编辑 $PROJECT_DIR/.env 配置API密钥"
    echo "2. 重启服务使配置生效"
    echo "3. 在GitHub中配置Secrets启用自动部署"
    echo ""
}

# 主函数
main() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}    阿里云快速部署脚本${NC}"
    echo -e "${BLUE}================================${NC}"
    echo ""
    
    parse_args "$@"
    check_environment
    update_system
    install_docker
    install_docker_compose
    configure_firewall
    create_deploy_user
    create_project_directory
    clone_project
    configure_environment
    install_nginx
    configure_ssl
    initial_deployment
    verify_deployment
    setup_monitoring
    show_completion_info
}

# 执行主函数
main "$@"
