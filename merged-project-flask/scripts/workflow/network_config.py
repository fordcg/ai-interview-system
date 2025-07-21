#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
网络配置模块
统一处理代理设置和网络连接配置
"""

import os
import requests
from typing import Optional, Dict, Any

def get_proxy_config() -> Optional[Dict[str, str]]:
    """
    获取代理配置
    
    Returns:
        代理配置字典或None（如果禁用代理）
    """
    # 检查环境变量中的代理设置
    http_proxy = os.environ.get('HTTP_PROXY') or os.environ.get('http_proxy')
    https_proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
    
    # 如果设置了代理环境变量，使用它们
    if http_proxy or https_proxy:
        proxy_config = {}
        if http_proxy:
            proxy_config['http'] = http_proxy
        if https_proxy:
            proxy_config['https'] = https_proxy
        return proxy_config
    
    # 默认禁用代理，避免连接问题
    return None

def create_session() -> requests.Session:
    """
    创建配置好的requests会话
    
    Returns:
        配置好的requests.Session对象
    """
    session = requests.Session()
    
    # 设置代理配置
    proxy_config = get_proxy_config()
    if proxy_config:
        session.proxies.update(proxy_config)
        print(f"使用代理配置: {proxy_config}")
    else:
        # 明确禁用代理
        session.proxies = {}
        print("已禁用代理设置")
    
    # 设置默认超时 - 支持3分钟工作流处理时间
    session.timeout = (100, 300)  # (连接超时60秒, 读取超时300秒=5分钟)
    
    # 禁用重试策略，只请求一次
    from requests.adapters import HTTPAdapter

    # 设置不重试的适配器
    adapter = HTTPAdapter(max_retries=0)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session

def make_api_request(url: str, data: Dict[str, Any], headers: Dict[str, str],
                    timeout: tuple = (100, 300)) -> requests.Response:
    """
    发送API请求的统一方法
    
    Args:
        url: API URL
        data: 请求数据
        headers: 请求头
        timeout: 超时设置 (连接超时, 读取超时)
    
    Returns:
        requests.Response对象
    
    Raises:
        requests.RequestException: 请求失败时抛出异常
    """
    session = create_session()
    
    try:
        print(f"发送POST请求到: {url}")
        print(f"超时设置: 连接{timeout[0]}秒, 读取{timeout[1]}秒")
        
        response = session.post(
            url,
            json=data,
            headers=headers,
            timeout=timeout
        )
        
        response.raise_for_status()
        print(f"请求成功，状态码: {response.status_code}")
        
        return response
        
    except requests.exceptions.ProxyError as e:
        print(f"代理连接错误: {str(e)}")
        print("API很宝贵，不进行重试。请检查网络连接或代理设置。")
        raise
        
    except requests.exceptions.Timeout:
        print("请求超时")
        raise
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {str(e)}")
        raise
    finally:
        session.close()

def test_network_connectivity(url: str = "https://xingchen-api.xf-yun.com") -> bool:
    """
    测试网络连通性
    
    Args:
        url: 测试URL
    
    Returns:
        连通性测试结果
    """
    try:
        session = create_session()
        response = session.get(url, timeout=(10, 30))
        session.close()
        print(f"网络连通性测试成功: {response.status_code}")
        return True
    except Exception as e:
        print(f"网络连通性测试失败: {str(e)}")
        return False

if __name__ == "__main__":
    # 测试网络配置
    print("=== 网络配置测试 ===")
    
    proxy_config = get_proxy_config()
    print(f"代理配置: {proxy_config}")
    
    print("\n=== 网络连通性测试 ===")
    test_network_connectivity()
