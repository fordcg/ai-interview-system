#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
从SQL文件导入数据到SQLite数据库
"""

import sqlite3
import os
import time
import random

def create_job_table(conn):
    """创建职位表"""
    cursor = conn.cursor()
    # 先删除表（如果存在）
    cursor.execute("DROP TABLE IF EXISTS tb_job")
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tb_job (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        number TEXT,
        company_name TEXT,
        position_name TEXT,
        city TEXT,
        salary0 REAL,
        salary1 REAL,
        degree TEXT,
        company_logo TEXT,
        url TEXT,
        company_url TEXT,
        education TEXT,
        coattr TEXT,
        cosize0 REAL,
        cosize1 REAL,
        worktime0 REAL,
        worktime1 REAL,
        welfare TEXT,
        publish_time TEXT,
        province TEXT
    )
    ''')
    conn.commit()
    print("职位表创建成功")

def generate_sample_data(count=100):
    """生成更多样本数据"""
    positions = ['前端开发工程师', '后端开发工程师', '数据分析师', '机器学习工程师', '产品经理', 
               'UI设计师', '测试工程师', '运维工程师', 'DevOps工程师', 'Java开发工程师',
               'Python开发工程师', 'C++开发工程师', 'Android开发工程师', 'iOS开发工程师',
               '全栈工程师', '数据库管理员', '网络安全工程师', '算法工程师', '游戏开发工程师',
               '项目经理', '技术总监', 'CTO', '系统架构师', '大数据工程师', '云计算工程师']
    
    companies = ['科技有限公司', '互联网科技公司', '数据科技公司', '人工智能公司', '电商平台',
                '金融科技公司', '教育科技公司', '医疗科技公司', '游戏开发公司', '软件开发公司',
                '云计算公司', '大数据公司', '网络安全公司', '移动互联网公司', '智能硬件公司',
                '区块链公司', '虚拟现实公司', '人力资源公司', '咨询公司', '系统集成公司']
    
    cities = ['北京', '上海', '广州', '深圳', '杭州', '南京', '成都', '武汉', '西安', '苏州',
             '天津', '重庆', '厦门', '青岛', '长沙', '郑州', '宁波', '合肥', '福州', '大连']
    
    provinces = {'北京': '北京', '上海': '上海', '广州': '广东', '深圳': '广东', '杭州': '浙江', 
                '南京': '江苏', '成都': '四川', '武汉': '湖北', '西安': '陕西', '苏州': '江苏',
                '天津': '天津', '重庆': '重庆', '厦门': '福建', '青岛': '山东', '长沙': '湖南', 
                '郑州': '河南', '宁波': '浙江', '合肥': '安徽', '福州': '福建', '大连': '辽宁'}
    
    degrees = ['初中及以下', '高中', '大专', '本科', '硕士', '博士']
    
    coattrs = ['私营企业', '国有企业', '外资企业', '合资企业', '上市公司']
    
    welfare_options = ['五险一金', '年终奖', '带薪年假', '免费班车', '定期体检', '股票期权', 
                      '弹性工作', '免费三餐', '专业培训', '团队建设', '节日福利', '绩效奖金',
                      '生日礼物', '加班补助', '通讯补贴', '住房补贴', '交通补贴', '健身房',
                      '旅游福利', '工作餐补贴', '医疗保险', '子女教育基金']
    
    sample_data = []
    
    for i in range(1, count + 1):
        position = random.choice(positions)
        company_prefix = random.choice(['北京', '上海', '广州', '深圳', '杭州', '天津', '苏州', '成都'])
        company_name = f"{company_prefix}{random.choice(companies)}"
        city = random.choice(cities)
        province = provinces.get(city, '')
        
        # 薪资范围
        salary0 = random.randint(5, 50) * 1000
        salary1 = salary0 + random.randint(5, 20) * 1000
        
        # 工作经验
        worktime0 = random.randint(0, 7)
        worktime1 = worktime0 + random.randint(1, 5)
        
        # 公司规模
        cosize0 = random.choice([50, 100, 200, 500, 1000, 2000])
        cosize1 = cosize0 * random.randint(2, 10)
        
        # 福利
        welfare_count = random.randint(3, 8)
        welfare_list = random.sample(welfare_options, welfare_count)
        welfare = ','.join(welfare_list)
        
        # 时间戳
        days_ago = random.randint(1, 90)
        publish_time = time.strftime('%Y-%m-%d', time.localtime(time.time() - days_ago * 86400))
        
        # 学历
        degree = random.choice(degrees)
        
        # 公司属性
        coattr = random.choice(coattrs)
        
        # Job number
        job_number = f"JOB{time.strftime('%Y%m')}{i:05d}"
        
        # 公司logo
        company_logo = f"company_logo{i % 20 + 1}.png"
        
        # URL
        url = f"https://example.com/jobs/{i}"
        company_url = f"https://example.com/company/{i}"
        
        # 教育背景
        education = degree
        
        sample_data.append((
            job_number, company_name, position, city, salary0, salary1, degree, 
            company_logo, url, company_url, education, coattr, cosize0, cosize1, 
            worktime0, worktime1, welfare, publish_time, province
        ))
    
    return sample_data

def import_sample_data(conn, count=100):
    """导入生成的样本数据"""
    cursor = conn.cursor()
    
    # 生成样本数据
    sample_jobs = generate_sample_data(count)
    
    # 插入示例数据
    start_time = time.time()
    cursor.executemany('''
    INSERT INTO tb_job (
        number, company_name, position_name, city, salary0, salary1, degree, 
        company_logo, url, company_url, education, coattr, cosize0, cosize1, 
        worktime0, worktime1, welfare, publish_time, province
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', sample_jobs)
    
    conn.commit()
    end_time = time.time()
    print(f"成功导入 {len(sample_jobs)} 条样本职位数据，耗时：{end_time - start_time:.2f}秒")

def main():
    """主函数"""
    db_path = 'merged_job_interview.db'
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    print(f"已连接到数据库: {db_path}")
    
    # 创建表
    create_job_table(conn)
    
    # 导入样本数据
    import_sample_data(conn, 200)  # 导入200条样本数据
    
    # 查询数据总数
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM tb_job")
    count = cursor.fetchone()[0]
    print(f"数据库中共有 {count} 条职位记录")
    
    # 显示几条记录作为示例
    cursor.execute("SELECT id, company_name, position_name, city, salary0, salary1 FROM tb_job LIMIT 5")
    rows = cursor.fetchall()
    print("\n示例职位记录:")
    for row in rows:
        print(row)
    
    # 关闭连接
    conn.close()
    print("数据导入完成")

if __name__ == "__main__":
    main() 