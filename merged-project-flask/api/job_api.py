#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
职位相关API
整合了原job_api.py与api/job_api.py的功能
"""

import os
import json
import sqlite3
import math
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from flask_cors import CORS

# 创建Blueprint
jobBp = Blueprint('job_api', __name__)

# 数据库路径
DB_PATH = 'merged_job_interview.db'

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 设置行工厂，使结果可以通过列名访问
    return conn

# 统一的响应格式
def create_response(code=200, message="success", data=None):
    """创建统一格式的响应"""
    return jsonify({
        'code': code,
        'message': message,
        'data': data
    })

@jobBp.route('/')
def index():
    """API根路径"""
    return create_response(
        code=200,
        message='职位API服务运行中',
        data={
            'version': '1.0.0',
            'endpoints': [
                '/api/jobs',            # 获取职位列表(分页)
                '/api/job/<id>',        # 获取职位详情
                '/api/search',          # 关键词搜索
                '/api/cities',          # 获取城市列表
                '/api/provinces',       # 获取省份列表
                '/api/stats/salary',    # 获取薪资统计
                '/api/stats/city',      # 获取城市职位数量统计
                '/api/test',            # 测试数据库连接
                '/job/get',             # 原接口：获取职位列表
                '/job/getWordCut',      # 原接口：获取词云数据
                '/job/getRecomendation',# 原接口：获取推荐
                '/job/getChart1',       # 原接口：获取薪资分布
                '/job/getAreaChart',    # 原接口：获取区域分布
                '/job/getPanel'         # 原接口：获取统计面板
            ]
        }
    )

# ============ 新API接口 (/api/...) ============

@jobBp.route('/api/jobs', methods=['GET'])
def get_jobs():
    """获取职位列表(分页)"""
    # 获取分页参数
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('pageSize', 10))
    
    # 获取筛选参数
    keyword = request.args.get('keyword', '')
    city = request.args.get('city', '')
    salary = request.args.get('salary', '')
    worktime = request.args.get('worktime', '')
    education = request.args.get('education', '')
    company_size = request.args.get('companySize', '')
    
    # 构建查询条件
    conditions = []
    params = []
    
    # 关键词搜索
    if keyword:
        conditions.append("position_name LIKE ?")
        params.append(f"%{keyword}%")
    
    if city:
        conditions.append("city = ?")
        params.append(city)
    
    if salary:
        # 根据薪资范围筛选
        salary_ranges = {
            '0': (0, 3),
            '1': (3, 5),
            '2': (5, 10),
            '3': (10, 15),
            '4': (15, 20),
            '5': (20, 50)
        }
        if salary in salary_ranges:
            min_salary, max_salary = salary_ranges[salary]
            conditions.append("(salary0 >= ? AND salary0 <= ?)")
            params.extend([min_salary, max_salary])
    
    if worktime:
        # 根据工作经验筛选
        worktime_ranges = {
            '0': (0, 1),
            '1': (1, 3),
            '2': (3, 5),
            '3': (5, 10),
            '4': (10, 100)
        }
        if worktime in worktime_ranges:
            min_work, max_work = worktime_ranges[worktime]
            conditions.append("(worktime0 >= ? AND worktime0 <= ?)")
            params.extend([min_work, max_work])
    
    if education:
        conditions.append("education LIKE ?")
        params.append(f"%{education}%")
    
    if company_size:
        # 根据公司规模筛选
        size_ranges = {
            '0': (0, 20),
            '1': (20, 99),
            '2': (100, 499),
            '3': (500, 999),
            '4': (1000, 9999),
            '5': (10000, 1000000)
        }
        if company_size in size_ranges:
            min_size, max_size = size_ranges[company_size]
            conditions.append("(cosize0 >= ? AND cosize0 <= ?)")
            params.extend([min_size, max_size])
    
    # 构建SQL查询
    query = "SELECT * FROM tb_job"
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    # 添加分页
    offset = (page - 1) * page_size
    query += f" LIMIT {page_size} OFFSET {offset}"
    
    # 查询总数的SQL
    count_query = "SELECT COUNT(*) as total FROM tb_job"
    if conditions:
        count_query += " WHERE " + " AND ".join(conditions)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取总数
        cursor.execute(count_query, params)
        total = cursor.fetchone()['total']
        
        # 获取职位数据
        cursor.execute(query, params)
        jobs = [dict(row) for row in cursor.fetchall()]
        
        # 计算总页数
        total_pages = math.ceil(total / page_size)
        
        conn.close()
        
        return create_response(
            code=200,
            message='success',
            data={
                'list': jobs,
                'pageNum': page,
                'pageSize': page_size,
                'total': total,
                'totalPages': total_pages
            }
        )
    except Exception as e:
        return create_response(
            code=500,
            message=f'Error: {str(e)}',
            data=None
        )

@jobBp.route('/api/job/<int:job_id>', methods=['GET'])
def get_job_detail(job_id):
    """获取职位详情"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 查询职位详情
        cursor.execute("SELECT * FROM tb_job WHERE id = ?", (job_id,))
        job = cursor.fetchone()
        
        conn.close()
        
        if job:
            return create_response(
                code=200,
                message='success',
                data=dict(job)
            )
        else:
            return create_response(
                code=404,
                message='Job not found',
                data=None
            )
    except Exception as e:
        return create_response(
            code=500,
            message=f'Error: {str(e)}',
            data=None
        )

@jobBp.route('/api/cities', methods=['GET'])
def get_cities():
    """获取城市列表"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 查询所有不同的城市
        cursor.execute("SELECT DISTINCT city FROM tb_job WHERE city != '' ORDER BY city")
        cities = [row['city'] for row in cursor.fetchall()]
        
        conn.close()
        
        return create_response(
            code=200,
            message='success',
            data=cities
        )
    except Exception as e:
        return create_response(
            code=500,
            message=f'Error: {str(e)}',
            data=None
        )

@jobBp.route('/api/provinces', methods=['GET'])
def get_provinces():
    """获取省份列表"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 查询所有不同的省份
        cursor.execute("SELECT DISTINCT province FROM tb_job WHERE province != '' ORDER BY province")
        provinces = [row['province'] for row in cursor.fetchall()]
        
        conn.close()
        
        return create_response(
            code=200,
            message='success',
            data=provinces
        )
    except Exception as e:
        return create_response(
            code=500,
            message=f'Error: {str(e)}',
            data=None
        )

@jobBp.route('/api/stats/salary', methods=['GET'])
def get_salary_stats():
    """获取薪资统计数据"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 查询不同薪资范围的职位数量
        ranges = [
            (0, 3, "3K以下"),
            (3, 5, "3K-5K"),
            (5, 10, "5K-10K"),
            (10, 15, "10K-15K"),
            (15, 20, "15K-20K"),
            (20, 50, "20K以上")
        ]
        
        stats = []
        for min_val, max_val, label in ranges:
            cursor.execute(
                "SELECT COUNT(*) as count FROM tb_job WHERE salary0 >= ? AND salary0 <= ?",
                (min_val, max_val)
            )
            count = cursor.fetchone()['count']
            stats.append({
                'name': label,
                'value': count
            })
        
        conn.close()
        
        return create_response(
            code=200,
            message='success',
            data=stats
        )
    except Exception as e:
        return create_response(
            code=500,
            message=f'Error: {str(e)}',
            data=None
        )

@jobBp.route('/api/stats/city', methods=['GET'])
def get_city_stats():
    """获取城市职位数量统计"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 查询每个城市的职位数量（前10名）
        cursor.execute("""
            SELECT city, COUNT(*) as count 
            FROM tb_job 
            WHERE city != '' 
            GROUP BY city 
            ORDER BY count DESC 
            LIMIT 10
        """)
        
        stats = []
        for row in cursor.fetchall():
            stats.append({
                'name': row['city'],
                'value': row['count']
            })
        
        conn.close()
        
        return create_response(
            code=200,
            message='success',
            data=stats
        )
    except Exception as e:
        return create_response(
            code=500,
            message=f'Error: {str(e)}',
            data=None
        )

@jobBp.route('/api/test', methods=['GET'])
def test_db():
    """测试数据库连接"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 执行简单查询
        cursor.execute("SELECT COUNT(*) as count FROM tb_job")
        count = cursor.fetchone()['count']
        
        conn.close()
        
        return create_response(
            code=200,
            message='Database connection successful',
            data={
                'job_count': count
            }
        )
    except Exception as e:
        return create_response(
            code=500,
            message=f'Database error: {str(e)}',
            data=None
        )

@jobBp.route('/api/search', methods=['GET'])
def test_search():
    """测试关键词搜索"""
    keyword = request.args.get('keyword', '')
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 执行关键词搜索
        query = "SELECT * FROM tb_job WHERE position_name LIKE ? LIMIT 10"
        cursor.execute(query, (f'%{keyword}%',))
        jobs = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return create_response(
            code=200,
            message='Search successful',
            data={
                'list': jobs,
                'keyword': keyword,
                'count': len(jobs)
            }
        )
    except Exception as e:
        return create_response(
            code=500,
            message=f'Search error: {str(e)}',
            data=None
        )

@jobBp.route('/api/jobs/recommend-by-skills', methods=['GET'])
def recommend_jobs_by_skills():
    """根据技能推荐相关岗位"""
    try:
        # 导入技能分类工具
        from utils.skill_classifier import classify_skills, get_weighted_skills, get_skill_categories, get_display_skills
        
        # 获取技能参数
        skills_param = request.args.get('skills', '')
        
        if not skills_param:
            return jsonify({
                'code': 400,
                'message': '缺少技能参数',
                'data': None
            })
        
        # 解析技能列表
        skills = skills_param.split(',')
        skills = [skill.strip().lower() for skill in skills if skill.strip()]
        
        if not skills:
            return jsonify({
                'code': 400,
                'message': '无效的技能参数',
                'data': None
            })
        
        # 对技能进行分类和权重处理
        classified_skills = classify_skills(skills)
        weighted_skills = get_weighted_skills(skills)
        skill_categories = get_skill_categories(skills)
        
        print(f"根据技能推荐岗位: {skills}")
        print(f"技能分类: {skill_categories}")
        
        # 连接数据库
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 构建查询条件
        # 使用LIKE语句匹配职位名称、描述等字段中包含技能关键词的职位
        conditions = []
        params = []
        
        # 添加技能类别作为搜索条件，增加权重
        for category in skill_categories:
            # 对类别名称进行更广泛的匹配，增加匹配几率
            conditions.append("(position_name LIKE ? OR welfare LIKE ? OR coattr LIKE ? OR company_name LIKE ?)")
            params.extend([f"%{category}%", f"%{category}%", f"%{category}%", f"%{category}%"])
            
            # 特殊处理前端开发类别
            if category.lower() == '前端开发':
                # 添加更多前端相关的关键词
                frontend_keywords = ['前端', '网页', 'web', 'ui', '界面', '网站']
                for keyword in frontend_keywords:
                    conditions.append("(position_name LIKE ?)")
                    params.append(f"%{keyword}%")
        
        # 放宽匹配条件：为每个技能添加更多可能的匹配字段
        for skill, weight in weighted_skills:
            # 对每个技能，检查更多字段以增加匹配几率
            # 技术技能优先级更高，软技能优先级较低
            if weight >= 1.0:  # 技术技能，完整匹配
                conditions.append("(position_name LIKE ? OR education LIKE ? OR welfare LIKE ? OR company_name LIKE ? OR coattr LIKE ?)")
                params.extend([f"%{skill}%", f"%{skill}%", f"%{skill}%", f"%{skill}%", f"%{skill}%"])
                
                # 添加技能的部分匹配（如果技能名称较长）
                if len(skill) > 3:
                    # 使用技能的前3个字符进行模糊匹配
                    skill_prefix = skill[:3]
                    conditions.append("(position_name LIKE ? OR welfare LIKE ?)")
                    params.extend([f"%{skill_prefix}%", f"%{skill_prefix}%"])
            else:  # 软技能，仅匹配福利和教育要求
                conditions.append("(welfare LIKE ? OR education LIKE ?)")
                params.extend([f"%{skill}%", f"%{skill}%"])
        
        # 组合条件
        if conditions:
            # 使用OR连接所有条件，只要满足任一条件即可
            where_clause = " OR ".join(conditions)
            query = f"""
                SELECT * FROM tb_job
                WHERE {where_clause}        
                LIMIT 50  -- 增加返回的结果数量
            """
        else:
            # 如果没有条件，返回最新的职位
            query = "SELECT * FROM tb_job ORDER BY id DESC LIMIT 20"
        
        print(f"执行查询: {query}")
        print(f"查询参数: {params}")
        
        # 执行查询
        cursor.execute(query, params)
        jobs = cursor.fetchall()
        
        print(f"查询结果数量: {len(jobs)}")
        
        # 如果没有匹配的岗位，返回一些热门岗位
        if not jobs:
            print("没有匹配的岗位，返回热门岗位")
            cursor.execute("SELECT * FROM tb_job ORDER BY id DESC LIMIT 10")
            jobs = cursor.fetchall()
        
        # 转换为字典列表
        column_names = [description[0] for description in cursor.description]
        job_list = []
        
        for job in jobs:
            job_dict = dict(zip(column_names, job))
            # 添加匹配的技能
            job_dict['matched_skills'] = []
            job_dict['matched_categories'] = []
            
            # 检查技能匹配
            for skill, weight in weighted_skills:
                skill_lower = skill.lower()
                # 检查更多字段以找出匹配的技能
                job_fields = [
                    job_dict.get('position_name', '').lower(),
                    job_dict.get('education', '').lower(),
                    job_dict.get('welfare', '').lower(),
                    job_dict.get('company_name', '').lower(),
                    job_dict.get('coattr', '').lower()
                ]
                
                if any(skill_lower in field for field in job_fields if field):
                    job_dict['matched_skills'].append(skill)
            
            # 检查类别匹配
            for category in skill_categories:
                category_lower = category.lower()
                # 检查职位名称和公司属性是否匹配类别
                if (category_lower in job_dict.get('position_name', '').lower() or 
                    category_lower in job_dict.get('coattr', '').lower() or
                    category_lower in job_dict.get('welfare', '').lower()):
                    job_dict['matched_categories'].append(category)
            
            # 添加匹配分数：匹配的技能数量 + 匹配的类别数量*2
            job_dict['match_score'] = len(job_dict['matched_skills']) + len(job_dict['matched_categories']) * 2
            
            job_list.append(job_dict)
        
        # 按匹配分数排序
        job_list.sort(key=lambda x: x['match_score'], reverse=True)
        
        conn.close()
        
        print(f"返回岗位数量: {len(job_list)}")
        
        # 获取用于显示的技能信息
        display_skills = get_display_skills(skills)
        
        return jsonify({
            'code': 200,
            'message': '获取推荐岗位成功',
            'data': {
                'list': job_list,
                'total': len(job_list),
                'skills': skills,
                'skill_categories': skill_categories,
                'display_skills': display_skills
            }
        })
    
    except Exception as e:
        print(f"推荐岗位失败: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'code': 500,
            'message': f"服务器错误: {str(e)}",
            'data': None
        })

@jobBp.route('/api/job/analyze', methods=['POST', 'OPTIONS'])
def analyze_job():
    """分析岗位信息并提供与简历匹配的建议"""
    # 处理OPTIONS请求（CORS预检请求）
    if request.method == 'OPTIONS':
        response = jsonify({'code': 200, 'message': 'OK'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        return response
    
    try:
        data = request.get_json()
        
        # 获取请求参数
        job_name = data.get('jobName', '未知职位')
        
        # 只使用职位名称作为参数，不再组合公司名称
        position_info = job_name
        
        # 导入岗位分析工作流
        from scripts.workflow.job_analysis_workflow import analyze_job_position
        
        # 调用岗位分析工作流
        result = analyze_job_position(position_info)
        
        return jsonify({
            'code': 0,
            'message': '岗位分析成功',
            'data': result
        })
    
    except Exception as e:
        import traceback
        print(f"岗位分析错误: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'code': 500,
            'message': f"岗位分析错误: {str(e)}",
            'data': None
        })

# ============ 原接口 (/job/...) ============

@jobBp.route('/job/get', methods=['GET'])
def job_get():
    """获取职位列表(原接口)"""
    page = int(request.args.get('page', 1))
    size = int(request.args.get('size', 10))
    keyword = request.args.get('keyword', '')
    city = request.args.get('city', '')
    
    # 分页查询
    offset = (page - 1) * size
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 构建查询条件
        conditions = []
        params = []
        
        # 关键词搜索
        if keyword:
            conditions.append("position_name LIKE ?")
            params.append(f"%{keyword}%")
        
        # 城市筛选
        if city:
            conditions.append("city = ?")
            params.append(city)
        
        # 构建SQL查询
        query = "SELECT * FROM tb_job"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        # 添加分页
        query += f" LIMIT {size} OFFSET {offset}"
        
        # 查询总数的SQL
        count_query = "SELECT COUNT(*) as total FROM tb_job"
        if conditions:
            count_query += " WHERE " + " AND ".join(conditions)
        
        # 获取总数
        cursor.execute(count_query, params)
        total = cursor.fetchone()['total']
        
        # 获取职位数据
        cursor.execute(query, params)
        jobs = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        # 返回前端需要的数据结构
        return jsonify({
            'code': 0,  # 原接口返回code=0表示成功
            'msg': 'success',
            'data': {
                'total': total,
                'items': jobs,
                'page': page,
                'limit': size,
                'pages': (total + size - 1) // size
            }
        })
    except Exception as e:
        return jsonify({
            'code': 1,
            'msg': f'Error: {str(e)}',
            'data': None
        })

@jobBp.route('/job/getWordCut', methods=['GET'])
def job_get_word_cut():
    """获取词云数据(原接口)"""
    # 模拟词云数据
    word_cut = [
        {"name": "Python", "value": 80},
        {"name": "Java", "value": 75},
        {"name": "前端", "value": 72},
        {"name": "后端", "value": 68},
        {"name": "算法", "value": 65},
        {"name": "开发", "value": 60},
        {"name": "测试", "value": 55},
        {"name": "产品", "value": 50},
        {"name": "运维", "value": 45},
        {"name": "数据分析", "value": 40}
    ]
    
    return jsonify({
        'code': 0,
        'msg': 'success',
        'data': word_cut
    })

@jobBp.route('/job/getRecomendation', methods=['GET'])
def job_get_recommendation():
    """获取职位推荐(原接口)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取推荐职位（示例：取薪资最高的5个）
        cursor.execute("""
            SELECT * FROM tb_job 
            WHERE salary0 > 0 
            ORDER BY salary0 DESC 
            LIMIT 5
        """)
        
        jobs = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            'code': 0,
            'msg': 'success',
            'data': jobs
        })
    except Exception as e:
        return jsonify({
            'code': 1,
            'msg': f'Error: {str(e)}',
            'data': None
        })

@jobBp.route('/job/getChart1', methods=['GET'])
def job_get_chart1():
    """获取薪资分布图表数据(原接口)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 薪资区间统计
        salary_ranges = [
            {'name': '3k以下', 'value': 0},
            {'name': '3k-5k', 'value': 0},
            {'name': '5k-10k', 'value': 0},
            {'name': '10k-15k', 'value': 0},
            {'name': '15k-20k', 'value': 0},
            {'name': '20k以上', 'value': 0}
        ]
        
        # 查询各区间数量
        cursor.execute("SELECT COUNT(*) as count FROM tb_job WHERE salary0 < 3")
        salary_ranges[0]['value'] = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM tb_job WHERE salary0 >= 3 AND salary0 <= 5")
        salary_ranges[1]['value'] = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM tb_job WHERE salary0 >= 5 AND salary0 <= 10")
        salary_ranges[2]['value'] = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM tb_job WHERE salary0 >= 10 AND salary0 <= 15")
        salary_ranges[3]['value'] = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM tb_job WHERE salary0 >= 15 AND salary0 <= 20")
        salary_ranges[4]['value'] = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM tb_job WHERE salary0 >= 20")
        salary_ranges[5]['value'] = cursor.fetchone()['count']
        
        conn.close()
        
        return jsonify({
            'code': 0,
            'msg': 'success',
            'data': salary_ranges
        })
    except Exception as e:
        return jsonify({
            'code': 1,
            'msg': f'Error: {str(e)}',
            'data': None
        })

@jobBp.route('/job/getAreaChart', methods=['GET'])
def job_get_area_chart():
    """获取区域分布图表数据(原接口)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 查询每个城市的职位数量（前10名）
        cursor.execute("""
            SELECT city, COUNT(*) as count 
            FROM tb_job 
            WHERE city != '' 
            GROUP BY city 
            ORDER BY count DESC 
            LIMIT 10
        """)
        
        city_data = []
        for row in cursor.fetchall():
            city_data.append({
                'name': row['city'],
                'value': row['count']
            })
        
        conn.close()
        
        return jsonify({
            'code': 0,
            'msg': 'success',
            'data': city_data
        })
    except Exception as e:
        return jsonify({
            'code': 1,
            'msg': f'Error: {str(e)}',
            'data': None
        })

@jobBp.route('/job/getPanel', methods=['GET'])
def job_get_panel():
    """获取统计面板数据(原接口)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取总职位数
        cursor.execute("SELECT COUNT(*) as count FROM tb_job")
        total_jobs = cursor.fetchone()['count']
        
        # 获取城市数量
        cursor.execute("SELECT COUNT(DISTINCT city) as count FROM tb_job WHERE city != ''")
        city_count = cursor.fetchone()['count']
        
        # 获取公司数量
        cursor.execute("SELECT COUNT(DISTINCT company_name) as count FROM tb_job WHERE company_name != ''")
        company_count = cursor.fetchone()['count']
        
        # 获取平均薪资
        cursor.execute("SELECT AVG((salary0 + salary1) / 2) as avg_salary FROM tb_job WHERE salary0 > 0 AND salary1 > 0")
        avg_salary_row = cursor.fetchone()
        avg_salary = round(avg_salary_row['avg_salary'], 2) if avg_salary_row['avg_salary'] else 0
        
        conn.close()
        
        panel_data = {
            'totalJobs': total_jobs,
            'cityCount': city_count,
            'companyCount': company_count,
            'avgSalary': avg_salary
        }
        
        return jsonify({
            'code': 0,
            'msg': 'success',
            'data': panel_data
        })
    except Exception as e:
        return jsonify({
            'code': 1,
            'msg': f'Error: {str(e)}',
            'data': None
        })

# 添加获取本地JSON数据的路由
@jobBp.route('/data/<path:filename>')
def get_data_file(filename):
    """获取数据文件"""
    try:
        # 获取项目根目录
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(base_dir, 'data')
        
        # 确保目录存在
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        # 检查文件是否存在
        file_path = os.path.join(data_dir, filename)
        if not os.path.exists(file_path):
            # 如果文件不存在，尝试从Vue项目的public/data目录复制
            vue_data_dir = os.path.join(base_dir, '..', 'merged-project-vue', 'public', 'data')
            vue_file_path = os.path.join(vue_data_dir, filename)
            
            if os.path.exists(vue_file_path):
                # 读取Vue项目中的文件内容
                with open(vue_file_path, 'r', encoding='utf-8') as f:
                    data = f.read()
                
                # 写入到Flask项目的data目录
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(data)
                
                print(f"已从Vue项目复制文件: {filename}")
            else:
                return jsonify({
                    'code': 404,
                    'message': f"文件不存在: {filename}"
                }), 404
        
        return send_from_directory(data_dir, filename)
    
    except Exception as e:
        print(f"获取数据文件失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'code': 500,
            'message': f"服务器错误: {str(e)}"
        }), 500

if __name__ == '__main__':
    # 这是直接运行此文件时的入口
    from flask import Flask
    app = Flask(__name__)
    CORS(app)
    
    # 注册蓝图
    app.register_blueprint(jobBp)
    
    # 启动应用
    app.run(debug=True, port=5001) 