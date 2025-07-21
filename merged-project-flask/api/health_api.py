# -*- coding: utf-8 -*-
"""
健康检查API
提供系统状态监控和健康检查功能
"""

from flask import Blueprint, jsonify, current_app
import time
import psutil
import os
from datetime import datetime
from sqlalchemy import text
from base.core import db
import redis

health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """
    系统健康检查
    返回系统各组件的健康状态
    """
    try:
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0',
            'uptime': get_uptime(),
            'components': {}
        }
        
        # 检查数据库连接
        db_status = check_database()
        health_status['components']['database'] = db_status
        
        # 检查Redis连接
        redis_status = check_redis()
        health_status['components']['redis'] = redis_status
        
        # 检查系统资源
        system_status = check_system_resources()
        health_status['components']['system'] = system_status
        
        # 检查AI服务
        ai_status = check_ai_services()
        health_status['components']['ai_services'] = ai_status

        # 检查环境变量
        env_status = check_environment_variables()
        health_status['components']['environment'] = env_status
        
        # 检查文件系统
        filesystem_status = check_filesystem()
        health_status['components']['filesystem'] = filesystem_status
        
        # 判断整体健康状态
        overall_healthy = all(
            component.get('status') == 'healthy' 
            for component in health_status['components'].values()
        )
        
        if not overall_healthy:
            health_status['status'] = 'degraded'
        
        return jsonify(health_status), 200 if overall_healthy else 503
        
    except Exception as e:
        current_app.logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e)
        }), 503

@health_bp.route('/health/database', methods=['GET'])
def database_health():
    """数据库健康检查"""
    return jsonify(check_database())

@health_bp.route('/health/redis', methods=['GET'])
def redis_health():
    """Redis健康检查"""
    return jsonify(check_redis())

@health_bp.route('/health/system', methods=['GET'])
def system_health():
    """系统资源健康检查"""
    return jsonify(check_system_resources())

def get_uptime():
    """获取系统运行时间"""
    try:
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])
            return uptime_seconds
    except:
        # Windows或其他系统的备用方案
        return time.time() - psutil.boot_time()

def check_database():
    """检查数据库连接状态"""
    try:
        start_time = time.time()
        
        # 执行简单查询测试连接
        result = db.session.execute(text('SELECT 1'))
        result.fetchone()
        
        response_time = (time.time() - start_time) * 1000  # 转换为毫秒
        
        # 检查连接池状态
        pool_status = {
            'size': db.engine.pool.size(),
            'checked_in': db.engine.pool.checkedin(),
            'checked_out': db.engine.pool.checkedout(),
            'overflow': db.engine.pool.overflow(),
            'invalid': db.engine.pool.invalid()
        }
        
        return {
            'status': 'healthy',
            'response_time_ms': round(response_time, 2),
            'pool_status': pool_status,
            'message': 'Database connection successful'
        }
        
    except Exception as e:
        current_app.logger.error(f"Database health check failed: {str(e)}")
        return {
            'status': 'unhealthy',
            'error': str(e),
            'message': 'Database connection failed'
        }

def check_redis():
    """检查Redis连接状态"""
    try:
        # 这里需要根据实际的Redis配置进行调整
        redis_url = current_app.config.get('REDIS_URL', 'redis://localhost:6379/0')
        
        start_time = time.time()
        r = redis.from_url(redis_url)
        
        # 测试连接
        r.ping()
        
        response_time = (time.time() - start_time) * 1000
        
        # 获取Redis信息
        info = r.info()
        
        return {
            'status': 'healthy',
            'response_time_ms': round(response_time, 2),
            'version': info.get('redis_version'),
            'memory_usage': info.get('used_memory_human'),
            'connected_clients': info.get('connected_clients'),
            'message': 'Redis connection successful'
        }
        
    except Exception as e:
        current_app.logger.error(f"Redis health check failed: {str(e)}")
        return {
            'status': 'unhealthy',
            'error': str(e),
            'message': 'Redis connection failed'
        }

def check_system_resources():
    """检查系统资源状态"""
    try:
        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # 内存使用情况
        memory = psutil.virtual_memory()
        
        # 磁盘使用情况
        disk = psutil.disk_usage('/')
        
        # 判断资源状态
        status = 'healthy'
        warnings = []
        
        if cpu_percent > 80:
            status = 'degraded'
            warnings.append(f'High CPU usage: {cpu_percent}%')
        
        if memory.percent > 85:
            status = 'degraded'
            warnings.append(f'High memory usage: {memory.percent}%')
        
        if disk.percent > 90:
            status = 'degraded'
            warnings.append(f'High disk usage: {disk.percent}%')
        
        return {
            'status': status,
            'cpu_percent': cpu_percent,
            'memory': {
                'total': memory.total,
                'available': memory.available,
                'percent': memory.percent,
                'used': memory.used
            },
            'disk': {
                'total': disk.total,
                'used': disk.used,
                'free': disk.free,
                'percent': disk.percent
            },
            'warnings': warnings,
            'message': 'System resources checked'
        }
        
    except Exception as e:
        current_app.logger.error(f"System resource check failed: {str(e)}")
        return {
            'status': 'unhealthy',
            'error': str(e),
            'message': 'System resource check failed'
        }

def check_ai_services():
    """检查AI服务状态"""
    try:
        services_status = {}
        
        # 检查DeepSeek API配置
        deepseek_key = current_app.config.get('DEEPSEEK_API_KEY')
        services_status['deepseek'] = {
            'configured': bool(deepseek_key),
            'status': 'configured' if deepseek_key else 'not_configured'
        }
        
        # 检查讯飞TTS配置
        xunfei_app_id = current_app.config.get('XUNFEI_APP_ID')
        xunfei_api_key = current_app.config.get('XUNFEI_API_KEY')
        services_status['xunfei_tts'] = {
            'configured': bool(xunfei_app_id and xunfei_api_key),
            'status': 'configured' if (xunfei_app_id and xunfei_api_key) else 'not_configured'
        }
        
        # 检查MediaPipe是否可用
        try:
            import mediapipe as mp
            services_status['mediapipe'] = {
                'available': True,
                'status': 'available',
                'version': mp.__version__
            }
        except ImportError:
            services_status['mediapipe'] = {
                'available': False,
                'status': 'not_available'
            }
        
        # 检查PyTorch是否可用
        try:
            import torch
            services_status['pytorch'] = {
                'available': True,
                'status': 'available',
                'version': torch.__version__,
                'cuda_available': torch.cuda.is_available()
            }
        except ImportError:
            services_status['pytorch'] = {
                'available': False,
                'status': 'not_available'
            }
        
        # 判断整体AI服务状态
        all_configured = all(
            service.get('status') in ['configured', 'available'] 
            for service in services_status.values()
        )
        
        return {
            'status': 'healthy' if all_configured else 'degraded',
            'services': services_status,
            'message': 'AI services checked'
        }
        
    except Exception as e:
        current_app.logger.error(f"AI services check failed: {str(e)}")
        return {
            'status': 'unhealthy',
            'error': str(e),
            'message': 'AI services check failed'
        }

def check_filesystem():
    """检查文件系统状态"""
    try:
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        
        # 检查上传目录是否存在和可写
        upload_writable = os.path.exists(upload_folder) and os.access(upload_folder, os.W_OK)
        
        # 检查日志目录
        log_folder = 'logs'
        log_writable = os.path.exists(log_folder) and os.access(log_folder, os.W_OK)
        
        # 检查模型目录
        model_folder = 'models'
        model_readable = os.path.exists(model_folder) and os.access(model_folder, os.R_OK)
        
        status = 'healthy'
        issues = []
        
        if not upload_writable:
            status = 'degraded'
            issues.append('Upload folder not writable')
        
        if not log_writable:
            status = 'degraded'
            issues.append('Log folder not writable')
        
        if not model_readable:
            status = 'degraded'
            issues.append('Model folder not readable')
        
        return {
            'status': status,
            'upload_folder': {
                'path': upload_folder,
                'writable': upload_writable
            },
            'log_folder': {
                'path': log_folder,
                'writable': log_writable
            },
            'model_folder': {
                'path': model_folder,
                'readable': model_readable
            },
            'issues': issues,
            'message': 'Filesystem checked'
        }
        
    except Exception as e:
        current_app.logger.error(f"Filesystem check failed: {str(e)}")
        return {
            'status': 'unhealthy',
            'error': str(e),
            'message': 'Filesystem check failed'
        }

def check_environment_variables():
    """
    检查环境变量配置状态
    """
    try:
        required_vars = {
            'DEEPSEEK_API_KEY': 'DeepSeek API密钥',
            'XUNFEI_APP_ID': '讯飞APP ID',
            'XUNFEI_API_KEY': '讯飞API密钥',
            'XUNFEI_API_SECRET': '讯飞API密钥',
            'SPARK_API_KEY': '星火API密钥',
            'SPARK_API_SECRET': '星火API密钥',
            'SPARK_APP_ID': '星火APP ID'
        }

        env_status = {}
        missing_vars = []

        for var_name, description in required_vars.items():
            value = os.getenv(var_name)
            if value and value != f'your-{var_name.lower().replace("_", "-")}':
                env_status[var_name] = {
                    'loaded': True,
                    'description': description,
                    'has_value': bool(value)
                }
            else:
                env_status[var_name] = {
                    'loaded': False,
                    'description': description,
                    'has_value': False
                }
                missing_vars.append(var_name)

        # 检查.env文件是否存在
        env_file_exists = os.path.exists('.env')

        status = 'healthy' if not missing_vars else 'warning'

        return {
            'status': status,
            'env_file_exists': env_file_exists,
            'variables': env_status,
            'missing_variables': missing_vars,
            'total_required': len(required_vars),
            'loaded_count': len(required_vars) - len(missing_vars)
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }
