#!/bin/bash

# 阿里云轻量服务器初始化脚本
# 使用方法: bash server-setup.sh

set -e

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

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# 检查是否为root用户
check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_error "请使用root用户运行此脚本"
        exit 1
    fi
}

# 更新系统
update_system() {
    print_step "更新系统包..."
    apt update && apt upgrade -y
    apt install -y curl wget git vim htop unzip software-properties-common
}

# 安装Docker
install_docker() {
    print_step "安装Docker..."
    
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
    docker --version
}

# 安装Docker Compose
install_docker_compose() {
    print_step "安装Docker Compose..."
    
    # 下载最新版本的Docker Compose
    DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
    curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    
    # 添加执行权限
    chmod +x /usr/local/bin/docker-compose
    
    # 创建软链接
    ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
    
    print_message "Docker Compose安装完成"
    docker-compose --version
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
    ufw status
}

# 创建部署用户
create_deploy_user() {
    print_step "创建部署用户..."
    
    # 创建用户
    useradd -m -s /bin/bash deploy || true
    
    # 添加到docker组
    usermod -aG docker deploy
    
    # 创建SSH目录
    mkdir -p /home/deploy/.ssh
    chmod 700 /home/deploy/.ssh
    
    # 设置权限
    chown -R deploy:deploy /home/deploy/.ssh
    
    print_message "部署用户创建完成"
}

# 创建项目目录
create_project_directory() {
    print_step "创建项目目录..."
    
    # 创建项目目录
    mkdir -p /opt/interview-system
    chown -R deploy:deploy /opt/interview-system
    
    # 创建日志目录
    mkdir -p /var/log/interview-system
    chown -R deploy:deploy /var/log/interview-system
    
    print_message "项目目录创建完成"
}

# 配置Git
configure_git() {
    print_step "配置Git..."
    
    # 切换到deploy用户
    sudo -u deploy bash << 'EOF'
        cd /opt/interview-system
        
        # 配置Git（如果需要）
        git config --global user.name "Deploy Bot"
        git config --global user.email "deploy@example.com"
        
        # 克隆项目（需要手动配置）
        echo "请手动克隆项目到 /opt/interview-system"
        echo "git clone https://github.com/your-username/your-repo.git ."
EOF
}

# 安装Nginx
install_nginx() {
    print_step "安装Nginx..."
    
    apt install -y nginx
    
    # 启动Nginx
    systemctl start nginx
    systemctl enable nginx
    
    # 创建SSL目录
    mkdir -p /etc/nginx/ssl
    
    print_message "Nginx安装完成"
    nginx -v
}

# 配置系统优化
optimize_system() {
    print_step "优化系统配置..."
    
    # 增加文件描述符限制
    cat >> /etc/security/limits.conf << 'EOF'
* soft nofile 65536
* hard nofile 65536
root soft nofile 65536
root hard nofile 65536
EOF

    # 优化内核参数
    cat >> /etc/sysctl.conf << 'EOF'
# 网络优化
net.core.somaxconn = 65535
net.core.netdev_max_backlog = 5000
net.ipv4.tcp_max_syn_backlog = 65535
net.ipv4.tcp_fin_timeout = 10
net.ipv4.tcp_keepalive_time = 1200
net.ipv4.tcp_keepalive_intvl = 15
net.ipv4.tcp_keepalive_probes = 5

# 内存优化
vm.swappiness = 10
vm.dirty_ratio = 15
vm.dirty_background_ratio = 5
EOF

    # 应用内核参数
    sysctl -p
    
    print_message "系统优化完成"
}

# 创建监控脚本
create_monitoring_script() {
    print_step "创建监控脚本..."
    
    cat > /opt/interview-system/monitor.sh << 'EOF'
#!/bin/bash

# 系统监控脚本
LOG_FILE="/var/log/interview-system/monitor.log"

# 检查Docker服务
check_docker() {
    if ! systemctl is-active --quiet docker; then
        echo "$(date): Docker服务异常，正在重启..." >> $LOG_FILE
        systemctl restart docker
    fi
}

# 检查应用服务
check_app() {
    cd /opt/interview-system
    
    # 检查容器状态
    if ! docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
        echo "$(date): 应用容器异常，正在重启..." >> $LOG_FILE
        docker-compose -f docker-compose.prod.yml restart
    fi
}

# 清理日志
cleanup_logs() {
    find /var/log/interview-system -name "*.log" -mtime +7 -delete
    find /opt/interview-system/merged-project-flask/logs -name "*.log" -mtime +7 -delete
}

# 执行检查
check_docker
check_app
cleanup_logs

echo "$(date): 监控检查完成" >> $LOG_FILE
EOF

    chmod +x /opt/interview-system/monitor.sh
    chown deploy:deploy /opt/interview-system/monitor.sh
    
    # 添加到crontab
    (crontab -u deploy -l 2>/dev/null; echo "*/5 * * * * /opt/interview-system/monitor.sh") | crontab -u deploy -
    
    print_message "监控脚本创建完成"
}

# 显示完成信息
show_completion_info() {
    print_message "服务器初始化完成！"
    echo ""
    echo "🎉 阿里云轻量服务器已配置完成！"
    echo ""
    echo "📋 接下来的步骤："
    echo "1. 配置SSH密钥到 /home/deploy/.ssh/authorized_keys"
    echo "2. 克隆项目到 /opt/interview-system"
    echo "3. 配置环境变量文件 .env"
    echo "4. 配置SSL证书到 /etc/nginx/ssl/"
    echo "5. 在GitHub中配置Secrets"
    echo ""
    echo "🔧 GitHub Secrets配置："
    echo "   SSH_PRIVATE_KEY: 私钥内容"
    echo "   SSH_USER: deploy"
    echo "   SERVER_HOST: $(curl -s ifconfig.me)"
    echo "   GITHUB_TOKEN: 自动提供"
    echo ""
    echo "📁 重要目录："
    echo "   项目目录: /opt/interview-system"
    echo "   日志目录: /var/log/interview-system"
    echo "   SSL证书: /etc/nginx/ssl"
    echo ""
}

# 主函数
main() {
    print_message "开始初始化阿里云轻量服务器..."
    echo ""
    
    check_root
    update_system
    install_docker
    install_docker_compose
    configure_firewall
    create_deploy_user
    create_project_directory
    configure_git
    install_nginx
    optimize_system
    create_monitoring_script
    show_completion_info
}

# 执行主函数
main "$@"
