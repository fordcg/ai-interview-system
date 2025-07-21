#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据库初始化脚本
创建所有必要的数据库表
"""

from app import create_app
from base.core import db

# 导入所有模型以确保表被创建
from models.user import User
from models.job import Job
from models.interview import Interview
from models.progress import Progress
from models.ranking import Ranking
from models.interview_report import InterviewReport

def init_database():
    """初始化数据库"""
    app = create_app()
    
    with app.app_context():
        # 创建所有表
        db.create_all()
        print("数据库表创建成功！")
        
        # 打印创建的表
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"已创建的表: {tables}")

if __name__ == '__main__':
    init_database()
