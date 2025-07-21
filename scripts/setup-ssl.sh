#!/bin/bash

# SSL证书自动申请和配置脚本
# 支持Let's Encrypt免费证书和自签名证书

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 配置变量
DOMAIN=""
EMAIL=""
SSL_DIR="/etc/nginx/ssl"
NGINX_CONF_DIR="/etc/nginx/sites-available"
CERT_TYPE=""

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
    echo "SSL证书配置脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -d, --domain DOMAIN     域名 (必需)"
    echo "  -e, --email EMAIL       邮箱地址 (Let's Encrypt需要)"
    echo "  -t, --type TYPE         证书类型: letsencrypt 或 selfsigned"
    echo "  -h, --help              显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 -d example.com -e admin@example.com -t letsencrypt"
    echo "  $0 -d localhost -t selfsigned"
}

# 解析命令行参数
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -d|--domain)
                DOMAIN="$2"
                shift 2
                ;;
            -e|--email)
                EMAIL="$2"
                shift 2
                ;;
            -t|--type)
                CERT_TYPE="$2"
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
    if [ -z "$DOMAIN" ]; then
        print_error "域名是必需的"
        show_help
        exit 1
    fi
    
    if [ -z "$CERT_TYPE" ]; then
        print_warning "未指定证书类型，将根据域名自动选择"
        if [ "$DOMAIN" = "localhost" ] || [[ "$DOMAIN" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
            CERT_TYPE="selfsigned"
        else
            CERT_TYPE="letsencrypt"
        fi
    fi
    
    if [ "$CERT_TYPE" = "letsencrypt" ] && [ -z "$EMAIL" ]; then
        print_error "Let's Encrypt证书需要邮箱地址"
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
        print_warning "网络连接可能有问题"
    fi
    
    print_message "系统环境检查完成"
}

# 安装依赖
install_dependencies() {
    print_step "安装必要的依赖..."
    
    # 更新包列表
    apt update
    
    if [ "$CERT_TYPE" = "letsencrypt" ]; then
        # 安装certbot
        if ! command -v certbot &> /dev/null; then
            print_message "安装certbot..."
            apt install -y certbot python3-certbot-nginx
        else
            print_message "certbot已安装"
        fi
    fi
    
    # 安装openssl（用于自签名证书）
    if ! command -v openssl &> /dev/null; then
        print_message "安装openssl..."
        apt install -y openssl
    else
        print_message "openssl已安装"
    fi
    
    # 安装nginx（如果未安装）
    if ! command -v nginx &> /dev/null; then
        print_message "安装nginx..."
        apt install -y nginx
    else
        print_message "nginx已安装"
    fi
}

# 创建SSL目录
create_ssl_directory() {
    print_step "创建SSL证书目录..."
    
    mkdir -p "$SSL_DIR"
    chmod 755 "$SSL_DIR"
    
    print_message "SSL目录创建完成: $SSL_DIR"
}

# 申请Let's Encrypt证书
setup_letsencrypt() {
    print_step "申请Let's Encrypt证书..."
    
    # 检查域名解析
    print_message "检查域名解析..."
    if ! nslookup "$DOMAIN" &> /dev/null; then
        print_warning "域名解析可能有问题，但继续尝试申请证书"
    fi
    
    # 停止nginx（避免端口冲突）
    if systemctl is-active --quiet nginx; then
        print_message "临时停止nginx服务..."
        systemctl stop nginx
        NGINX_WAS_RUNNING=true
    else
        NGINX_WAS_RUNNING=false
    fi
    
    # 申请证书
    print_message "申请证书中..."
    if certbot certonly --standalone \
        --non-interactive \
        --agree-tos \
        --email "$EMAIL" \
        -d "$DOMAIN" \
        --rsa-key-size 4096; then
        
        print_message "Let's Encrypt证书申请成功"
        
        # 复制证书到nginx目录
        cp "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" "$SSL_DIR/cert.pem"
        cp "/etc/letsencrypt/live/$DOMAIN/privkey.pem" "$SSL_DIR/key.pem"
        
        # 设置权限
        chmod 644 "$SSL_DIR/cert.pem"
        chmod 600 "$SSL_DIR/key.pem"
        
        # 设置自动续期
        setup_auto_renewal
        
    else
        print_error "Let's Encrypt证书申请失败"
        
        # 重启nginx（如果之前在运行）
        if [ "$NGINX_WAS_RUNNING" = true ]; then
            systemctl start nginx
        fi
        
        exit 1
    fi
    
    # 重启nginx（如果之前在运行）
    if [ "$NGINX_WAS_RUNNING" = true ]; then
        systemctl start nginx
    fi
}

# 生成自签名证书
setup_selfsigned() {
    print_step "生成自签名证书..."
    
    # 生成私钥
    openssl genrsa -out "$SSL_DIR/key.pem" 4096
    
    # 生成证书签名请求配置
    cat > "$SSL_DIR/cert.conf" << EOF
[req]
default_bits = 4096
prompt = no
default_md = sha256
distinguished_name = dn
req_extensions = v3_req

[dn]
C=CN
ST=Beijing
L=Beijing
O=Interview System
OU=IT Department
CN=$DOMAIN

[v3_req]
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
subjectAltName = @alt_names

[alt_names]
DNS.1 = $DOMAIN
DNS.2 = www.$DOMAIN
EOF

    # 如果是IP地址，添加IP扩展
    if [[ "$DOMAIN" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        echo "IP.1 = $DOMAIN" >> "$SSL_DIR/cert.conf"
    fi
    
    # 生成自签名证书
    openssl req -new -x509 -key "$SSL_DIR/key.pem" \
        -out "$SSL_DIR/cert.pem" \
        -days 365 \
        -config "$SSL_DIR/cert.conf" \
        -extensions v3_req
    
    # 设置权限
    chmod 644 "$SSL_DIR/cert.pem"
    chmod 600 "$SSL_DIR/key.pem"
    chmod 600 "$SSL_DIR/cert.conf"
    
    print_message "自签名证书生成完成"
    print_warning "自签名证书仅用于测试，浏览器会显示安全警告"
}

# 设置自动续期
setup_auto_renewal() {
    print_step "设置证书自动续期..."
    
    # 创建续期脚本
    cat > /usr/local/bin/renew-ssl.sh << 'EOF'
#!/bin/bash

# SSL证书自动续期脚本
LOG_FILE="/var/log/ssl-renewal.log"

echo "$(date): 开始检查SSL证书续期..." >> $LOG_FILE

# 续期证书
if certbot renew --quiet --no-self-upgrade; then
    echo "$(date): 证书续期检查完成" >> $LOG_FILE
    
    # 如果证书被更新，重新加载nginx
    if certbot renew --dry-run --quiet; then
        # 复制新证书到nginx目录
        DOMAIN=$(certbot certificates | grep "Certificate Name" | head -1 | cut -d: -f2 | tr -d ' ')
        if [ ! -z "$DOMAIN" ]; then
            cp "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" "/etc/nginx/ssl/cert.pem"
            cp "/etc/letsencrypt/live/$DOMAIN/privkey.pem" "/etc/nginx/ssl/key.pem"
            
            # 重新加载nginx
            if systemctl reload nginx; then
                echo "$(date): Nginx重新加载成功" >> $LOG_FILE
            else
                echo "$(date): Nginx重新加载失败" >> $LOG_FILE
            fi
        fi
    fi
else
    echo "$(date): 证书续期失败" >> $LOG_FILE
fi
EOF

    chmod +x /usr/local/bin/renew-ssl.sh
    
    # 添加到crontab
    (crontab -l 2>/dev/null; echo "0 12 * * * /usr/local/bin/renew-ssl.sh") | crontab -
    
    print_message "自动续期设置完成"
}

# 验证证书
verify_certificate() {
    print_step "验证SSL证书..."
    
    if [ -f "$SSL_DIR/cert.pem" ] && [ -f "$SSL_DIR/key.pem" ]; then
        # 检查证书有效性
        if openssl x509 -in "$SSL_DIR/cert.pem" -text -noout &> /dev/null; then
            print_message "证书文件有效"
            
            # 显示证书信息
            CERT_SUBJECT=$(openssl x509 -in "$SSL_DIR/cert.pem" -subject -noout | cut -d= -f2-)
            CERT_EXPIRY=$(openssl x509 -in "$SSL_DIR/cert.pem" -enddate -noout | cut -d= -f2)
            
            print_message "证书主题: $CERT_SUBJECT"
            print_message "证书到期时间: $CERT_EXPIRY"
            
            # 检查私钥匹配
            CERT_MODULUS=$(openssl x509 -in "$SSL_DIR/cert.pem" -modulus -noout)
            KEY_MODULUS=$(openssl rsa -in "$SSL_DIR/key.pem" -modulus -noout)
            
            if [ "$CERT_MODULUS" = "$KEY_MODULUS" ]; then
                print_message "证书和私钥匹配"
            else
                print_error "证书和私钥不匹配"
                return 1
            fi
        else
            print_error "证书文件无效"
            return 1
        fi
    else
        print_error "证书文件不存在"
        return 1
    fi
}

# 更新nginx配置
update_nginx_config() {
    print_step "更新nginx配置..."
    
    # 备份原配置
    if [ -f "/opt/interview-system/nginx/nginx.prod.conf" ]; then
        cp "/opt/interview-system/nginx/nginx.prod.conf" "/opt/interview-system/nginx/nginx.prod.conf.bak"
        
        # 更新域名配置
        sed -i "s/your-domain\.com/$DOMAIN/g" "/opt/interview-system/nginx/nginx.prod.conf"
        
        print_message "nginx配置已更新"
    else
        print_warning "nginx配置文件不存在，请手动配置"
    fi
}

# 显示完成信息
show_completion_info() {
    print_message "SSL证书配置完成！"
    echo ""
    echo "🎉 SSL证书已成功配置！"
    echo ""
    echo "📋 证书信息:"
    echo "   域名: $DOMAIN"
    echo "   类型: $CERT_TYPE"
    echo "   证书路径: $SSL_DIR/cert.pem"
    echo "   私钥路径: $SSL_DIR/key.pem"
    echo ""
    
    if [ "$CERT_TYPE" = "letsencrypt" ]; then
        echo "🔄 自动续期:"
        echo "   已设置自动续期任务"
        echo "   续期日志: /var/log/ssl-renewal.log"
        echo ""
    fi
    
    echo "🔧 下一步操作:"
    echo "1. 重启nginx服务: systemctl restart nginx"
    echo "2. 测试HTTPS访问: https://$DOMAIN"
    echo "3. 检查证书状态: openssl s_client -connect $DOMAIN:443"
    echo ""
    
    if [ "$CERT_TYPE" = "selfsigned" ]; then
        echo "⚠️  注意:"
        echo "   自签名证书会在浏览器中显示安全警告"
        echo "   生产环境建议使用Let's Encrypt证书"
        echo ""
    fi
}

# 主函数
main() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}    SSL证书配置脚本${NC}"
    echo -e "${BLUE}================================${NC}"
    echo ""
    
    parse_args "$@"
    check_environment
    install_dependencies
    create_ssl_directory
    
    case "$CERT_TYPE" in
        "letsencrypt")
            setup_letsencrypt
            ;;
        "selfsigned")
            setup_selfsigned
            ;;
        *)
            print_error "不支持的证书类型: $CERT_TYPE"
            exit 1
            ;;
    esac
    
    verify_certificate
    update_nginx_config
    show_completion_info
}

# 执行主函数
main "$@"
