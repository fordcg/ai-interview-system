# Nginx配置说明

本目录包含用于配置Nginx作为Flask应用的反向代理和静态文件服务器的配置文件。

## 配置步骤

1. 安装Nginx（如果尚未安装）：

   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install nginx

   # CentOS/RHEL
   sudo yum install epel-release
   sudo yum install nginx
   ```

2. 修改配置文件：

   打开`flask_app.conf`文件，根据您的环境修改以下内容：

   - 将`server_name`替换为您的域名或服务器IP地址
   - 将`/path/to/your/app/static/uploads/`替换为您的Flask应用上传目录的实际路径
   - 如果需要，调整端口号和其他设置

3. 部署配置文件：

   ```bash
   # 复制配置文件到Nginx配置目录
   sudo cp flask_app.conf /etc/nginx/sites-available/

   # 创建符号链接到sites-enabled目录（Ubuntu/Debian）
   sudo ln -s /etc/nginx/sites-available/flask_app.conf /etc/nginx/sites-enabled/

   # 或者直接复制到conf.d目录（CentOS/RHEL）
   # sudo cp flask_app.conf /etc/nginx/conf.d/
   ```

4. 验证配置文件语法：

   ```bash
   sudo nginx -t
   ```

5. 重启Nginx：

   ```bash
   sudo systemctl restart nginx
   ```

## 修改Flask应用配置

在Flask应用的`config.py`文件中，设置`EXTERNAL_URL_BASE`为您的Nginx服务器URL：

```python
# 外部访问配置
# 设置为Nginx服务的域名或IP，例如：http://example.com 或 http://192.168.1.100
EXTERNAL_URL_BASE = "http://your-server-domain-or-ip"
```

## 文件权限

确保Nginx用户（通常是`www-data`或`nginx`）有权访问Flask应用的上传目录：

```bash
# 查看Nginx用户
grep -i user /etc/nginx/nginx.conf

# 设置目录权限（假设Nginx用户是www-data）
sudo chown -R www-data:www-data /path/to/your/app/static/uploads/
sudo chmod -R 755 /path/to/your/app/static/uploads/
```

## 测试

配置完成后，可以通过以下URL访问您的应用：

- API：`http://your-server-domain-or-ip/api/`
- 上传文件：`http://your-server-domain-or-ip/api/uploads/filename`
- 根路由：`http://your-server-domain-or-ip/` 