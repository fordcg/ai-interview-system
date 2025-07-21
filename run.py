#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
职位与面试系统启动脚本 - 重构版
提供更清晰的结构和更好的错误处理
"""

import os
import sys
import subprocess
import threading
import time
import webbrowser
import platform
import sqlite3
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("system_startup.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 颜色常量
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

# 系统配置
class Config:
    """系统配置"""
    # 目录配置
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
    BACKEND_DIR = os.path.join(PROJECT_ROOT, 'merged-project-flask')
    FRONTEND_DIR = os.path.join(PROJECT_ROOT, 'merged-project-vue')
    WORKFLOW_DIR = os.path.join(BACKEND_DIR, 'scripts', 'workflow')
    
    # 虚拟环境配置
    VENV_DIR = os.path.join(BACKEND_DIR, 'venv')
    
    # 数据库配置
    DB_PATH = os.path.join(BACKEND_DIR, 'merged_job_interview.db')
    
    # 服务配置
    BACKEND_PORT = 5000
    WORKFLOW_PORT = 8000
    FRONTEND_PORT = 8080
    
    # 超时配置
    BACKEND_TIMEOUT = 12  # 秒
    WORKFLOW_TIMEOUT = 12  # 秒
    FRONTEND_TIMEOUT = 15  # 秒
    
    # 核心依赖包
    CORE_PACKAGES = ['flask', 'flask-cors', 'werkzeug', 'requests', 'numpy', 'pandas']

def print_banner():
    """打印启动横幅"""
    banner = f"""
{Colors.BLUE}{Colors.BOLD}
 ██████╗ ██████╗ ██████╗     ██╗███╗   ██╗████████╗███████╗██████╗ ██╗   ██╗██╗███████╗██╗    ██╗
██╔════╝██╔═══██╗██╔══██╗    ██║████╗  ██║╚══██╔══╝██╔════╝██╔══██╗██║   ██║██║██╔════╝██║    ██║
╚█████╗ ██║   ██║██████╔╝    ██║██╔██╗ ██║   ██║   █████╗  ██████╔╝██║   ██║██║█████╗  ██║ █ ██║
 ╚═══██╗██║   ██║██╔══██╗    ██║██║╚██╗██║   ██║   ██╔══╝  ██╔══██╗╚██╗ ██╔╝██║██╔══╝  ██║███╗██║
██████╔╝╚██████╔╝██████╔╝    ██║██║ ╚████║   ██║   ███████╗██║  ██║ ╚████╔╝ ██║███████╗╚███╔███╔╝
╚═════╝  ╚═════╝ ╚═════╝     ╚═╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝ ╚══╝╚══╝ 
                                                                                                  
{Colors.GREEN}职位与面试系统 v1.0.0{Colors.ENDC}
"""
    print(banner)

def colored_print(color, message):
    """带颜色的打印"""
    print(f"{color}{message}{Colors.ENDC}")

def check_dependencies():
    """检查依赖项是否安装"""
    colored_print(Colors.HEADER, "正在检查依赖项...")
    
    # 检查Python版本
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        colored_print(Colors.FAIL, "错误: 需要Python 3.8或更高版本")
        colored_print(Colors.WARNING, f"当前Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
        return False
    else:
        colored_print(Colors.GREEN, f"Python版本检查通过: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # 检查requests库
    try:
        import requests
        colored_print(Colors.GREEN, "requests库已安装")
    except ImportError:
        colored_print(Colors.WARNING, "未安装requests库，正在尝试安装...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
            colored_print(Colors.GREEN, "requests库安装成功")
        except Exception as e:
            colored_print(Colors.FAIL, f"安装requests库失败: {str(e)}")
            colored_print(Colors.WARNING, "请手动安装requests库: pip install requests")
            return False
    
    # 检查Node.js
    try:
        # 在Windows上使用shell=True来确保找到node命令
        if platform.system() == 'Windows':
            node_version = subprocess.check_output('node -v', shell=True).decode().strip()
        else:
            node_version = subprocess.check_output(['node', '-v']).decode().strip()
        colored_print(Colors.GREEN, f"Node.js版本: {node_version}")
    except Exception as e:
        colored_print(Colors.FAIL, f"错误: 未安装Node.js或无法访问 - {str(e)}")
        return False
    
    # 检查npm
    try:
        # 在Windows上使用shell=True来确保找到npm命令
        if platform.system() == 'Windows':
            npm_version = subprocess.check_output('npm -v', shell=True).decode().strip()
        else:
            npm_version = subprocess.check_output(['npm', '-v']).decode().strip()
        colored_print(Colors.GREEN, f"npm版本: {npm_version}")
    except Exception as e:
        colored_print(Colors.FAIL, f"错误: 未安装npm或无法访问 - {str(e)}")
        return False
    
    # 检查数据库文件
    if os.path.exists(Config.DB_PATH):
        try:
            # 检查数据库连接和表结构
            conn = sqlite3.connect(Config.DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM tb_job")
            count = cursor.fetchone()[0]
            conn.close()
            colored_print(Colors.GREEN, f"数据库检查通过: 找到{count}条职位记录")
        except Exception as e:
            colored_print(Colors.WARNING, f"数据库存在但无法正常访问: {str(e)}")
            return False
    else:
        colored_print(Colors.FAIL, f"错误: 数据库文件不存在: {Config.DB_PATH}")
        colored_print(Colors.WARNING, "请确保merged_job_interview.db文件已放置在正确位置")
        return False
    
    return True

def find_executable(venv_dir, exec_name):
    """
    在虚拟环境中查找可执行文件
    
    Args:
        venv_dir: 虚拟环境目录
        exec_name: 可执行文件名(不带扩展名)
    
    Returns:
        可执行文件的路径或命令名
    """
    is_windows = platform.system() == 'Windows'
    extension = '.exe' if is_windows else ''
    
    # 首先检查主要目录
    primary_dir = 'Scripts' if is_windows else 'bin'
    exec_path = os.path.join(venv_dir, primary_dir, exec_name)
    
    if os.path.exists(exec_path + extension):
        return exec_path
    
    # 检查备用目录
    alt_dir = 'bin' if primary_dir == 'Scripts' else 'Scripts'
    exec_path = os.path.join(venv_dir, alt_dir, exec_name)
    
    if os.path.exists(exec_path + extension):
        return exec_path
    
    # 尝试带3后缀的版本
    exec_path = os.path.join(venv_dir, primary_dir, f"{exec_name}3")
    if os.path.exists(exec_path + extension):
        return exec_path
    
    exec_path = os.path.join(venv_dir, alt_dir, f"{exec_name}3")
    if os.path.exists(exec_path + extension):
        return exec_path
    
    # 找不到，返回系统命令
    colored_print(Colors.WARNING, f"在虚拟环境中未找到{exec_name}，使用系统命令")
    return exec_name

def ensure_venv():
    """
    确保虚拟环境存在
    
    Returns:
        成功创建返回True，否则返回False
    """
    if not os.path.exists(Config.VENV_DIR):
        colored_print(Colors.WARNING, "未找到虚拟环境，正在创建...")
        try:
            subprocess.run([sys.executable, '-m', 'venv', Config.VENV_DIR], check=True)
            colored_print(Colors.GREEN, "虚拟环境创建成功")
            return True
        except subprocess.CalledProcessError as e:
            colored_print(Colors.FAIL, f"创建虚拟环境失败: {str(e)}")
            return False
        except Exception as e:
            colored_print(Colors.FAIL, f"创建虚拟环境时发生未知错误: {str(e)}")
            return False
    return True

def install_dependencies(pip_path, requirements_file, max_attempts=2):
    """
    安装依赖项
    
    Args:
        pip_path: pip可执行文件路径
        requirements_file: requirements.txt文件路径
        max_attempts: 最大尝试次数
    
    Returns:
        安装成功返回True，否则返回False
    """
    colored_print(Colors.HEADER, "安装依赖项...")
    is_windows = platform.system() == 'Windows'
    
    # 确保使用绝对路径
    pip_absolute_path = os.path.abspath(pip_path) if pip_path != 'pip' else pip_path
    colored_print(Colors.HEADER, f"使用pip路径: {pip_absolute_path}")
    
    for attempt in range(max_attempts):
        try:
            if is_windows:
                colored_print(Colors.HEADER, f"执行命令: {pip_absolute_path} install -r {requirements_file}")
                result = subprocess.run(f'"{pip_absolute_path}" install -r {requirements_file}', 
                                       shell=True, capture_output=True, text=True)
            else:
                result = subprocess.run([pip_absolute_path, 'install', '-r', requirements_file], 
                                       capture_output=True, text=True)
                
            if result.returncode != 0:
                colored_print(Colors.FAIL, "安装依赖失败，错误信息:")
                colored_print(Colors.WARNING, result.stderr)
                
                # 尝试安装核心依赖
                colored_print(Colors.HEADER, "尝试单独安装核心依赖...")
                for package in Config.CORE_PACKAGES:
                    colored_print(Colors.HEADER, f"安装 {package}...")
                    if is_windows:
                        subprocess.run(f'"{pip_absolute_path}" install {package}', shell=True)
                    else:
                        subprocess.run([pip_absolute_path, 'install', package])
                
                if attempt < max_attempts - 1:
                    colored_print(Colors.WARNING, f"安装依赖失败，正在重试... ({attempt+1}/{max_attempts})")
                    time.sleep(2)
                    continue
                else:
                    colored_print(Colors.FAIL, f"安装依赖失败: {result.returncode}")
                    colored_print(Colors.WARNING, f"请尝试手动安装依赖: {pip_absolute_path} install -r {requirements_file}")
                    colored_print(Colors.WARNING, f"或者尝试手动安装核心依赖: {pip_absolute_path} install {' '.join(Config.CORE_PACKAGES)}")
                    colored_print(Colors.WARNING, "尝试继续运行，但可能会出现功能缺失...")
                    return False
            else:
                colored_print(Colors.GREEN, "依赖安装成功")
                return True
                
        except Exception as e:
            colored_print(Colors.FAIL, f"安装依赖时发生未知错误: {str(e)}")
            if attempt < max_attempts - 1:
                colored_print(Colors.WARNING, f"正在重试... ({attempt+1}/{max_attempts})")
                time.sleep(2)
            else:
                colored_print(Colors.WARNING, "尝试继续运行，但可能会出现功能缺失...")
                return False
    
    return False

def run_command(cmd, shell=False, cwd=None):
    """
    运行命令
    
    Args:
        cmd: 命令（字符串或列表）
        shell: 是否使用shell
        cwd: 工作目录
        
    Returns:
        成功返回True，否则返回False
    """
    try:
        subprocess.run(cmd, shell=shell, check=True, cwd=cwd)
        return True
    except subprocess.CalledProcessError as e:
        colored_print(Colors.FAIL, f"命令执行失败: {str(e)}")
        return False
    except Exception as e:
        colored_print(Colors.FAIL, f"命令执行时发生未知错误: {str(e)}")
        return False

def run_backend():
    """运行后端服务"""
    colored_print(Colors.HEADER, "准备启动后端服务...")
    
    # 切换到后端目录
    os.chdir(Config.BACKEND_DIR)
    
    # 确保虚拟环境存在
    if not ensure_venv():
        return False
    
    # 查找pip和python
    pip_cmd = find_executable(Config.VENV_DIR, 'pip')
    python_cmd = find_executable(Config.VENV_DIR, 'python')
    
    # 使用绝对路径
    python_absolute_path = os.path.abspath(python_cmd) if python_cmd != 'python' else python_cmd
    colored_print(Colors.HEADER, f"使用python路径: {python_absolute_path}")
    
    # 安装依赖
    requirements_file = os.path.join(Config.BACKEND_DIR, 'requirements.txt')
    install_dependencies(pip_cmd, requirements_file)
    
    # 运行后端
    colored_print(Colors.GREEN, "启动后端服务器...")
    is_windows = platform.system() == 'Windows'
    
    # 确保在后端目录中执行命令
    current_dir = os.getcwd()
    if current_dir != Config.BACKEND_DIR:
        colored_print(Colors.WARNING, f"当前目录 {current_dir} 不是后端目录，切换到 {Config.BACKEND_DIR}")
        os.chdir(Config.BACKEND_DIR)
    
    app_path = os.path.join(Config.BACKEND_DIR, 'app.py')
    if not os.path.exists(app_path):
        colored_print(Colors.FAIL, f"错误: 后端应用文件不存在: {app_path}")
        return False
    
    colored_print(Colors.HEADER, f"使用app.py启动服务: {app_path}")
    
    if is_windows:
        if python_cmd == 'python':
            return run_command('python app.py', shell=True, cwd=Config.BACKEND_DIR)
        else:
            return run_command(f'"{python_absolute_path}" app.py', shell=True, cwd=Config.BACKEND_DIR)
    else:
        if python_cmd == 'python':
            return run_command(['python', 'app.py'], cwd=Config.BACKEND_DIR)
        else:
            return run_command([python_absolute_path, 'app.py'], cwd=Config.BACKEND_DIR)

def run_workflow_server():
    """运行工作流服务器"""
    colored_print(Colors.HEADER, "准备启动工作流服务器...")
    
    # 切换到工作流目录
    workflow_dir = Config.WORKFLOW_DIR
    if not os.path.exists(workflow_dir):
        colored_print(Colors.FAIL, f"错误: 工作流目录不存在: {workflow_dir}")
        return False
    
    os.chdir(workflow_dir)
    colored_print(Colors.HEADER, f"切换到工作流目录: {workflow_dir}")
    
    # 查找python
    python_cmd = find_executable(Config.VENV_DIR, 'python')
    
    # 使用绝对路径
    python_absolute_path = os.path.abspath(python_cmd) if python_cmd != 'python' else python_cmd
    colored_print(Colors.HEADER, f"使用python路径: {python_absolute_path}")
    
    # 检查工作流服务器脚本是否存在
    workflow_script = os.path.join(workflow_dir, 'run_workflow_server.py')
    if not os.path.exists(workflow_script):
        colored_print(Colors.FAIL, f"错误: 工作流服务器脚本不存在: {workflow_script}")
        return False
    
    # 运行工作流服务器
    colored_print(Colors.GREEN, "启动工作流服务器...")
    is_windows = platform.system() == 'Windows'
    
    if is_windows:
        colored_print(Colors.HEADER, f"使用run_workflow_server.py启动服务，端口{Config.WORKFLOW_PORT}")
        if python_cmd == 'python':
            return run_command(f'python run_workflow_server.py --port {Config.WORKFLOW_PORT}', shell=True, cwd=workflow_dir)
        else:
            return run_command(f'"{python_absolute_path}" run_workflow_server.py --port {Config.WORKFLOW_PORT}', shell=True, cwd=workflow_dir)
    else:
        colored_print(Colors.HEADER, f"使用run_workflow_server.py启动服务，端口{Config.WORKFLOW_PORT}")
        if python_cmd == 'python':
            return run_command(['python', 'run_workflow_server.py', '--port', str(Config.WORKFLOW_PORT)], cwd=workflow_dir)
        else:
            return run_command([python_absolute_path, 'run_workflow_server.py', '--port', str(Config.WORKFLOW_PORT)], cwd=workflow_dir)

def run_frontend():
    """运行前端服务"""
    colored_print(Colors.HEADER, "准备启动前端服务...")
    
    # 切换到前端目录
    os.chdir(Config.FRONTEND_DIR)
    
    # 安装依赖
    colored_print(Colors.HEADER, "安装前端依赖项...")
    is_windows = platform.system() == 'Windows'
    
    try:
        if is_windows:
            subprocess.run('npm install', shell=True, check=True)
        else:
            subprocess.run(['npm', 'install'], check=True)
        colored_print(Colors.GREEN, "前端依赖安装成功")
    except subprocess.CalledProcessError as e:
        colored_print(Colors.FAIL, f"安装前端依赖失败: {str(e)}")
        return False
    
    # 运行前端
    colored_print(Colors.GREEN, "启动前端服务器...")
    try:
        if is_windows:
            subprocess.run('npm run dev', shell=True)
        else:
            subprocess.run(['npm', 'run', 'dev'])
        return True
    except subprocess.CalledProcessError as e:
        colored_print(Colors.FAIL, f"启动前端服务失败: {str(e)}")
        return False

def check_service_status(url, max_attempts, service_name):
    """
    检查服务状态
    
    Args:
        url: 服务URL
        max_attempts: 最大尝试次数
        service_name: 服务名称
        
    Returns:
        服务可用返回True，否则返回False
    """
    for attempt in range(max_attempts):
        try:
            import requests
            response = requests.get(url)
            if response.status_code == 200:
                colored_print(Colors.GREEN, f"{service_name}已成功启动")
                return True
        except:
            pass
        
        colored_print(Colors.HEADER, f"等待{service_name}启动... ({attempt+1}/{max_attempts})")
        time.sleep(2)
    
    colored_print(Colors.WARNING, f"{service_name}可能未正常启动")
    return False

def check_backend_status():
    """检查后端服务是否启动"""
    return check_service_status(
        f"http://localhost:{Config.BACKEND_PORT}/", 
        Config.BACKEND_TIMEOUT, 
        "后端服务"
    )

def check_workflow_status():
    """检查工作流服务器是否启动"""
    return check_service_status(
        f"http://localhost:{Config.WORKFLOW_PORT}/", 
        Config.WORKFLOW_TIMEOUT, 
        "工作流服务器"
    )

def check_frontend_status():
    """检查前端服务是否启动"""
    return check_service_status(
        f"http://localhost:{Config.FRONTEND_PORT}/", 
        Config.FRONTEND_TIMEOUT, 
        "前端服务"
    )

def main():
    """主函数"""
    print_banner()
    
    if not check_dependencies():
        colored_print(Colors.FAIL, "依赖项检查失败，请解决问题后重试")
        return
    
    # 获取当前脚本的目录
    os.chdir(Config.PROJECT_ROOT)
    
    # 修复前端main.js文件中的插件引用
    try:
        fix_frontend_plugins()
    except Exception as e:
        colored_print(Colors.WARNING, f"修复前端插件引用失败: {str(e)}")
    
    # 启动后端线程
    backend_thread = threading.Thread(target=run_backend)
    backend_thread.daemon = True
    backend_thread.start()
    
    # 启动工作流服务器线程
    workflow_thread = threading.Thread(target=run_workflow_server)
    workflow_thread.daemon = True
    workflow_thread.start()
    
    # 等待后端启动
    check_backend_status()
    
    # 等待工作流服务器启动
    check_workflow_status()
    
    # 启动前端
    frontend_thread = threading.Thread(target=run_frontend)
    frontend_thread.daemon = True
    frontend_thread.start()
    
    # 等待前端启动
    if check_frontend_status():
        # 打开浏览器
        colored_print(Colors.GREEN, "在浏览器中打开应用...")
        webbrowser.open(f'http://localhost:{Config.FRONTEND_PORT}')
    else:
        colored_print(Colors.WARNING, f"应用可能未完全启动，请手动访问http://localhost:{Config.FRONTEND_PORT}")
    
    # 等待线程结束
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        colored_print(Colors.WARNING, "\n正在关闭服务...")
        sys.exit(0)

def fix_frontend_plugins():
    """修复前端main.js中的插件引用"""
    main_js_path = os.path.join(Config.FRONTEND_DIR, 'src', 'main.js')
    if not os.path.exists(main_js_path):
        colored_print(Colors.WARNING, f"前端main.js文件不存在: {main_js_path}")
        return
    
    colored_print(Colors.HEADER, "修复前端main.js中的插件引用...")
    
    # 读取main.js文件
    with open(main_js_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 移除不存在的插件引用
    plugins_to_remove = [
        "import './plugins/echarts'",
        "import './plugins/vee-validate'",
        "import './plugins/vue-markdown'",
        "import './plugins/vue-json-viewer'",
        "import './plugins/vue-highlightjs'",
        "import './plugins/vue-codemirror'",
        "import './plugins/vue-pdf'"
    ]
    
    for plugin in plugins_to_remove:
        content = content.replace(plugin, f"// {plugin} // 已注释，插件可能不存在")
    
    # 写回文件
    with open(main_js_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    colored_print(Colors.GREEN, "前端main.js插件引用已修复")

if __name__ == "__main__":
    main() 