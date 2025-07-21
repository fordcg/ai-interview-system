#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
状态码
"""

# 成功
SUCCESS = 0

# 通用错误
PARAM_ERROR = 1000  # 参数错误
AUTH_ERROR = 1001   # 认证错误
PERMISSION_ERROR = 1002  # 权限错误
NOT_FOUND = 1003    # 资源不存在
SERVER_ERROR = 1004  # 服务器错误

# 用户相关错误
USER_NOT_EXIST = 2000  # 用户不存在
USER_ALREADY_EXIST = 2001  # 用户已存在
PASSWORD_ERROR = 2002  # 密码错误
LOGIN_REQUIRED = 2003  # 需要登录

# 业务相关错误
JOB_NOT_EXIST = 3000  # 职位不存在
INTERVIEW_NOT_EXIST = 3001  # 面试不存在
FILE_TYPE_ERROR = 3002  # 文件类型错误
FILE_UPLOAD_ERROR = 3003  # 文件上传错误 