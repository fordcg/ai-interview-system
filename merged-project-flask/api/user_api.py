#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
用户相关API (整合a1和a2)
"""

from flask import Blueprint, request, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import and_

from models.user import User, user_schema
from base.core import db
from base.response import ResMsg

userBp = Blueprint('user', __name__)

@userBp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    res = ResMsg()
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        res.update(code=1, msg="用户名和密码不能为空")
        return res.data
    
    user = User.query.filter_by(username=username).first()
    
    if not user or not check_password_hash(user.password, password):
        res.update(code=1, msg="用户名或密码错误")
        return res.data
    
    # 登录用户
    login_user(user)
    
    # 返回用户信息
    user_data = user_schema.dump(user)
    res.update(code=0, data=user_data)
    return res.data

@userBp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    res = ResMsg()
    data = request.json
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    
    if not username or not password or not email:
        res.update(code=1, msg="用户名、密码和邮箱不能为空")
        return res.data
    
    # 检查用户名是否已存在
    if User.query.filter_by(username=username).first():
        res.update(code=1, msg="用户名已存在")
        return res.data
    
    # 检查邮箱是否已存在
    if User.query.filter_by(email=email).first():
        res.update(code=1, msg="邮箱已存在")
        return res.data
    
    # 创建新用户
    hashed_password = generate_password_hash(password)
    user = User(
        username=username,
        password=hashed_password,
        email=email
    )
    
    db.session.add(user)
    db.session.commit()
    
    # 登录新用户
    login_user(user)
    
    # 返回用户信息
    user_data = user_schema.dump(user)
    res.update(code=0, data=user_data)
    return res.data

@userBp.route('/logout')
@login_required
def logout():
    """用户登出"""
    res = ResMsg()
    logout_user()
    res.update(code=0, msg="登出成功")
    return res.data

@userBp.route('/get/<int:user_id>')
def get_user(user_id):
    """获取用户信息"""
    res = ResMsg()
    user = User.query.get(user_id)
    
    if not user:
        res.update(code=1, msg="用户不存在")
        return res.data
    
    user_data = user_schema.dump(user)
    res.update(code=0, data=user_data)
    return res.data

@userBp.route('/update', methods=['POST'])
@login_required
def update_user():
    """更新用户信息"""
    res = ResMsg()
    data = request.json
    
    # 只能更新当前登录用户的信息
    user = User.query.get(current_user.id)
    
    if not user:
        res.update(code=1, msg="用户不存在")
        return res.data
    
    # 更新可编辑的字段
    if 'email' in data:
        # 检查邮箱是否已被其他用户使用
        existing_user = User.query.filter(and_(User.email == data['email'], User.id != user.id)).first()
        if existing_user:
            res.update(code=1, msg="邮箱已被使用")
            return res.data
        user.email = data['email']
    
    if 'realname' in data:
        user.realname = data['realname']
    
    if 'avatar' in data:
        user.avatar = data['avatar']
    
    if 'phone' in data:
        user.phone = data['phone']
    
    if 'intro' in data:
        user.intro = data['intro']
    
    if 'addr' in data:
        user.addr = data['addr']
    
    if 'password' in data and data['password']:
        user.password = generate_password_hash(data['password'])
    
    db.session.commit()
    
    user_data = user_schema.dump(user)
    res.update(code=0, data=user_data)
    return res.data

@userBp.route('/profile')
@login_required
def profile():
    """获取当前用户个人资料"""
    res = ResMsg()
    
    user_data = user_schema.dump(current_user)
    
    # 获取用户的面试统计数据
    from models.interview import Interview
    
    interview_count = Interview.query.filter_by(user_id=current_user.id).count()
    avg_score = db.session.query(db.func.avg(Interview.overall_score)).filter_by(user_id=current_user.id).scalar() or 0
    
    profile_data = {
        'user': user_data,
        'stats': {
            'interview_count': interview_count,
            'avg_score': round(float(avg_score), 1)
        }
    }
    
    res.update(code=0, data=profile_data)
    return res.data

@userBp.route('/idconfirm', methods=['POST'])
@login_required
def id_confirm():
    """身份认证"""
    res = ResMsg()
    data = request.json
    
    user = User.query.get(current_user.id)
    
    if not user:
        res.update(code=1, msg="用户不存在")
        return res.data
    
    # 更新身份信息
    if 'idno' in data:
        user.idno = data['idno']
    
    if 'realname' in data:
        user.realname = data['realname']
    
    db.session.commit()
    
    user_data = user_schema.dump(user)
    res.update(code=0, data=user_data)
    return res.data 