#!/bin/bash

# 部署前检查脚本
# 验证所有必要的配置和依赖是否就绪

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 计数器
CHECKS_PASSED=0
CHECKS_FAILED=0
WARNINGS=0

# 打印函数
print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}    部署前环境检查脚本${NC}"
    echo -e "${BLUE}================================${NC}"
    echo ""
}

print_check() {
    echo -e "${BLUE}[检查]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
    ((CHECKS_PASSED++))
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
    ((CHECKS_FAILED++))
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
    ((WARNINGS++))
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# 检查Docker环境
check_docker() {
    print_check "检查Docker环境..."
    
    if command -v docker &> /dev/null; then
        DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
        print_success "Docker已安装 (版本: $DOCKER_VERSION)"
        
        # 检查Docker服务状态
        if systemctl is-active --quiet docker; then
            print_success "Docker服务正在运行"
        else
            print_error "Docker服务未运行"
            return 1
        fi
        
        # 检查Docker权限
        if docker ps &> /dev/null; then
            print_success "Docker权限正常"
        else
            print_error "Docker权限不足，请确保当前用户在docker组中"
            return 1
        fi
    else
        print_error "Docker未安装"
        return 1
    fi
}

# 检查Docker Compose
check_docker_compose() {
    print_check "检查Docker Compose..."
    
    if command -v docker-compose &> /dev/null; then
        COMPOSE_VERSION=$(docker-compose --version | cut -d' ' -f3 | cut -d',' -f1)
        print_success "Docker Compose已安装 (版本: $COMPOSE_VERSION)"
    else
        print_error "Docker Compose未安装"
        return 1
    fi
}

# 检查Git环境
check_git() {
    print_check "检查Git环境..."
    
    if command -v git &> /dev/null; then
        GIT_VERSION=$(git --version | cut -d' ' -f3)
        print_success "Git已安装 (版本: $GIT_VERSION)"
        
        # 检查是否在Git仓库中
        if git rev-parse --git-dir &> /dev/null; then
            print_success "当前目录是Git仓库"
            
            # 检查远程仓库
            if git remote -v | grep -q origin; then
                REMOTE_URL=$(git remote get-url origin)
                print_success "远程仓库已配置: $REMOTE_URL"
            else
                print_warning "未配置远程仓库"
            fi
        else
            print_error "当前目录不是Git仓库"
            return 1
        fi
    else
        print_error "Git未安装"
        return 1
    fi
}

# 检查环境变量文件
check_env_files() {
    print_check "检查环境变量文件..."
    
    if [ -f ".env.production" ]; then
        print_success ".env.production文件存在"
        
        # 检查必要的环境变量
        required_vars=(
            "MYSQL_ROOT_PASSWORD"
            "MYSQL_PASSWORD"
            "SECRET_KEY"
            "JWT_SECRET_KEY"
            "DEEPSEEK_API_KEY"
            "XUNFEI_APP_ID"
            "XUNFEI_API_KEY"
            "XUNFEI_API_SECRET"
        )
        
        missing_vars=()
        for var in "${required_vars[@]}"; do
            if grep -q "^${var}=" .env.production && ! grep -q "^${var}=your-" .env.production; then
                print_success "环境变量 $var 已配置"
            else
                missing_vars+=("$var")
                print_error "环境变量 $var 未配置或使用默认值"
            fi
        done
        
        if [ ${#missing_vars[@]} -gt 0 ]; then
            print_error "请配置以下环境变量: ${missing_vars[*]}"
            return 1
        fi
    else
        print_error ".env.production文件不存在"
        return 1
    fi
}

# 检查Docker配置文件
check_docker_configs() {
    print_check "检查Docker配置文件..."
    
    if [ -f "docker-compose.prod.yml" ]; then
        print_success "docker-compose.prod.yml文件存在"
        
        # 验证配置文件语法
        if docker-compose -f docker-compose.prod.yml config &> /dev/null; then
            print_success "Docker Compose配置语法正确"
        else
            print_error "Docker Compose配置语法错误"
            return 1
        fi
    else
        print_error "docker-compose.prod.yml文件不存在"
        return 1
    fi
    
    # 检查Dockerfile
    if [ -f "merged-project-flask/Dockerfile" ]; then
        print_success "后端Dockerfile存在"
    else
        print_error "后端Dockerfile不存在"
        return 1
    fi
    
    if [ -f "merged-project-vue/Dockerfile" ]; then
        print_success "前端Dockerfile存在"
    else
        print_error "前端Dockerfile不存在"
        return 1
    fi
}

# 检查GitHub Actions配置
check_github_actions() {
    print_check "检查GitHub Actions配置..."
    
    if [ -f ".github/workflows/deploy.yml" ]; then
        print_success "GitHub Actions工作流文件存在"
        
        # 检查工作流语法（简单检查）
        if grep -q "name:" .github/workflows/deploy.yml && grep -q "on:" .github/workflows/deploy.yml; then
            print_success "GitHub Actions工作流语法基本正确"
        else
            print_warning "GitHub Actions工作流语法可能有问题"
        fi
    else
        print_error "GitHub Actions工作流文件不存在"
        return 1
    fi
}

# 检查项目依赖文件
check_dependencies() {
    print_check "检查项目依赖文件..."
    
    # 检查Python依赖
    if [ -f "merged-project-flask/requirements.txt" ]; then
        print_success "Python requirements.txt存在"
        
        # 检查关键依赖
        key_deps=("Flask" "gunicorn" "PyMySQL" "redis")
        for dep in "${key_deps[@]}"; do
            if grep -qi "$dep" merged-project-flask/requirements.txt; then
                print_success "关键依赖 $dep 已列出"
            else
                print_warning "关键依赖 $dep 未在requirements.txt中找到"
            fi
        done
    else
        print_error "Python requirements.txt不存在"
        return 1
    fi
    
    # 检查Node.js依赖
    if [ -f "merged-project-vue/package.json" ]; then
        print_success "Node.js package.json存在"
        
        # 检查构建脚本
        if grep -q '"build"' merged-project-vue/package.json; then
            print_success "构建脚本已配置"
        else
            print_error "构建脚本未配置"
            return 1
        fi
    else
        print_error "Node.js package.json不存在"
        return 1
    fi
}

# 检查网络连接
check_network() {
    print_check "检查网络连接..."
    
    # 检查GitHub连接
    if curl -s --connect-timeout 5 https://github.com &> /dev/null; then
        print_success "GitHub连接正常"
    else
        print_warning "GitHub连接可能有问题"
    fi
    
    # 检查Docker Hub连接
    if curl -s --connect-timeout 5 https://hub.docker.com &> /dev/null; then
        print_success "Docker Hub连接正常"
    else
        print_warning "Docker Hub连接可能有问题"
    fi
    
    # 检查PyPI连接
    if curl -s --connect-timeout 5 https://pypi.org &> /dev/null; then
        print_success "PyPI连接正常"
    else
        print_warning "PyPI连接可能有问题"
    fi
}

# 检查磁盘空间
check_disk_space() {
    print_check "检查磁盘空间..."
    
    AVAILABLE_SPACE=$(df . | awk 'NR==2 {print $4}')
    AVAILABLE_GB=$((AVAILABLE_SPACE / 1024 / 1024))
    
    if [ $AVAILABLE_GB -gt 5 ]; then
        print_success "磁盘空间充足 (${AVAILABLE_GB}GB可用)"
    elif [ $AVAILABLE_GB -gt 2 ]; then
        print_warning "磁盘空间较少 (${AVAILABLE_GB}GB可用)"
    else
        print_error "磁盘空间不足 (${AVAILABLE_GB}GB可用，建议至少5GB)"
        return 1
    fi
}

# 检查系统资源
check_system_resources() {
    print_check "检查系统资源..."
    
    # 检查内存
    if command -v free &> /dev/null; then
        TOTAL_MEM=$(free -m | awk 'NR==2{print $2}')
        if [ $TOTAL_MEM -gt 3000 ]; then
            print_success "内存充足 (${TOTAL_MEM}MB)"
        elif [ $TOTAL_MEM -gt 1500 ]; then
            print_warning "内存较少 (${TOTAL_MEM}MB)"
        else
            print_error "内存不足 (${TOTAL_MEM}MB，建议至少2GB)"
            return 1
        fi
    else
        print_warning "无法检查内存使用情况"
    fi
    
    # 检查CPU核心数
    CPU_CORES=$(nproc)
    if [ $CPU_CORES -gt 1 ]; then
        print_success "CPU核心数充足 (${CPU_CORES}核)"
    else
        print_warning "CPU核心数较少 (${CPU_CORES}核)"
    fi
}

# 生成检查报告
generate_report() {
    echo ""
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}        检查结果汇总${NC}"
    echo -e "${BLUE}================================${NC}"
    echo ""
    echo -e "通过的检查: ${GREEN}$CHECKS_PASSED${NC}"
    echo -e "失败的检查: ${RED}$CHECKS_FAILED${NC}"
    echo -e "警告数量: ${YELLOW}$WARNINGS${NC}"
    echo ""
    
    if [ $CHECKS_FAILED -eq 0 ]; then
        echo -e "${GREEN}✓ 所有关键检查都已通过，可以进行部署！${NC}"
        if [ $WARNINGS -gt 0 ]; then
            echo -e "${YELLOW}! 请注意上述警告信息${NC}"
        fi
        return 0
    else
        echo -e "${RED}✗ 有 $CHECKS_FAILED 项检查失败，请修复后再进行部署${NC}"
        return 1
    fi
}

# 主函数
main() {
    print_header
    
    # 执行所有检查
    check_docker || true
    check_docker_compose || true
    check_git || true
    check_env_files || true
    check_docker_configs || true
    check_github_actions || true
    check_dependencies || true
    check_network || true
    check_disk_space || true
    check_system_resources || true
    
    # 生成报告
    generate_report
}

# 执行主函数
main "$@"
