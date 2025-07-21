#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
技能分类和映射工具
将具体技能映射到更高级别的技能类别
"""

# 技能分类映射表
SKILL_CATEGORIES = {
    # 前端技术
    'frontend': {
        'name': '前端开发',
        'skills': [
            'javascript', 'html', 'css', 'react', 'vue', 'angular', 'jquery', 
            'bootstrap', 'webpack', 'sass', 'less', 'typescript', 'redux', 
            'node.js', 'npm', 'yarn', 'responsive design', 'spa', 'pwa', 
            'web开发', '前端开发', '前端工程师', 'ui开发', '网页开发',
            'javascripts', 'js', 'web', 'web前端', '网页设计', '网页制作',
            '前端', 'h5', 'html5', 'css3', '网站开发', '网站建设', '网站设计',
            'ui', '用户界面', 'ux', '用户体验', '界面设计', '交互设计'
        ],
        'weight': 1.5  # 增加前端技能的权重
    },
    # 后端技术
    'backend': {
        'name': '后端开发',
        'skills': [
            'python', 'java', 'c++', 'c#', 'go', 'rust', 'php', 'ruby',
            'django', 'flask', 'spring', 'express', 'laravel', 'asp.net',
            'ruby on rails', 'node.js', '后端开发', '服务器端开发', '后端工程师'
        ]
    },
    # 数据库
    'database': {
        'name': '数据库',
        'skills': [
            'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'sqlite',
            'oracle', 'sql server', 'sql', 'nosql', '数据库管理', '数据库设计'
        ]
    },
    # 大数据技术
    'bigdata': {
        'name': '大数据',
        'skills': [
            'hadoop', 'spark', 'hive', 'flink', 'kafka', 'storm', 'big data',
            '大数据', '数据仓库', '数据挖掘', '数据分析', 'etl', 'data lake'
        ]
    },
    # 云计算
    'cloud': {
        'name': '云计算',
        'skills': [
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'openstack',
            'cloud', '云计算', '云架构', '云原生', 'serverless', 'iaas', 'paas', 'saas'
        ]
    },
    # AI/机器学习
    'ai': {
        'name': '人工智能/机器学习',
        'skills': [
            '机器学习', '深度学习', 'tensorflow', 'pytorch', 'keras', 'scikit-learn',
            'nlp', '自然语言处理', '计算机视觉', '图像处理', '推荐系统', '人工智能',
            'ai', 'ml', 'cv', '神经网络', '深度神经网络'
        ]
    },
    # 移动开发
    'mobile': {
        'name': '移动开发',
        'skills': [
            'android', 'ios', 'flutter', 'react native', 'swift', 'objective-c',
            'kotlin', '移动开发', 'app开发', '手机应用开发'
        ]
    },
    # 测试
    'testing': {
        'name': '测试',
        'skills': [
            '自动化测试', '单元测试', '集成测试', '性能测试', 'selenium', 'junit', 'pytest',
            'qa', '质量保证', '软件测试', '测试工程师'
        ]
    },
    # 运维
    'devops': {
        'name': 'DevOps/运维',
        'skills': [
            'devops', 'ci/cd', 'jenkins', 'git', 'linux', 'shell', 'ansible', 'puppet', 'chef',
            '运维', '系统管理', '网络管理', '系统运维', '运维工程师', '系统管理员'
        ]
    },
    # 项目管理
    'management': {
        'name': '项目管理',
        'skills': [
            '敏捷开发', 'scrum', '项目管理', 'pmp', 'prince2', '项目经理',
            '产品经理', '项目协调', '项目规划', '需求分析'
        ]
    },
    # 设计
    'design': {
        'name': '设计',
        'skills': [
            'photoshop', 'illustrator', 'sketch', 'figma', 'ui设计', 'ux设计',
            '用户体验', '用户界面', '平面设计', '交互设计', '视觉设计'
        ]
    },
    # 通用技能（软技能）- 权重较低
    'soft_skills': {
        'name': '通用技能',
        'skills': [
            '沟通能力', '团队协作', '问题解决', '时间管理', '领导力', '创新思维',
            '分析能力', '批判性思维', '英语', '日语', '法语', '德语', '西班牙语'
        ],
        'weight': 0.5  # 软技能权重较低
    }
}

# 反向映射：从具体技能到类别
SKILL_TO_CATEGORY = {}
for category, info in SKILL_CATEGORIES.items():
    weight = info.get('weight', 1.0)  # 默认权重为1.0
    for skill in info['skills']:
        SKILL_TO_CATEGORY[skill] = {
            'category': category,
            'name': info['name'],
            'weight': weight
        }

def classify_skill(skill):
    """
    将具体技能映射到类别
    
    Args:
        skill: 具体技能名称
    
    Returns:
        包含类别信息的字典，如果没有匹配则返回None
    """
    skill_lower = skill.lower()
    return SKILL_TO_CATEGORY.get(skill_lower)

def classify_skills(skills):
    """
    将技能列表映射到类别
    
    Args:
        skills: 技能列表
    
    Returns:
        分类后的技能字典，包含类别和原始技能
    """
    result = {
        'categories': {},  # 按类别分组的技能
        'uncategorized': [],  # 未分类的技能
        'all_skills': skills.copy()  # 所有原始技能
    }
    
    for skill in skills:
        skill_info = classify_skill(skill)
        if skill_info:
            category = skill_info['category']
            if category not in result['categories']:
                result['categories'][category] = {
                    'name': skill_info['name'],
                    'skills': [],
                    'weight': skill_info['weight']
                }
            result['categories'][category]['skills'].append(skill)
        else:
            result['uncategorized'].append(skill)
    
    return result

def get_weighted_skills(skills):
    """
    获取带权重的技能列表
    
    Args:
        skills: 技能列表
    
    Returns:
        带权重的技能列表，格式为 [(技能, 权重), ...]
    """
    weighted_skills = []
    for skill in skills:
        skill_info = classify_skill(skill)
        if skill_info:
            weighted_skills.append((skill, skill_info['weight']))
        else:
            weighted_skills.append((skill, 1.0))  # 默认权重为1.0
    
    return weighted_skills

def get_skill_categories(skills):
    """
    获取技能所属的类别列表
    
    Args:
        skills: 技能列表
    
    Returns:
        技能类别列表，格式为 [类别名称, ...]
    """
    categories = set()
    for skill in skills:
        skill_info = classify_skill(skill)
        if skill_info:
            categories.add(skill_info['name'])
    
    return list(categories)

def get_display_skills(skills):
    """
    获取用于显示的技能信息，将技能分类并添加类别标签
    
    Args:
        skills: 技能列表
    
    Returns:
        处理后的技能信息，包含类别和原始技能
    """
    classified = classify_skills(skills)
    
    # 构建显示信息
    display_info = {
        'skill_categories': [],  # 技能类别列表
        'categorized_skills': {},  # 按类别分组的技能
        'all_skills': skills  # 所有原始技能
    }
    
    # 添加分类的技能
    for category, info in classified['categories'].items():
        display_info['skill_categories'].append(info['name'])
        display_info['categorized_skills'][info['name']] = info['skills']
    
    # 添加未分类的技能
    if classified['uncategorized']:
        display_info['skill_categories'].append('其他技能')
        display_info['categorized_skills']['其他技能'] = classified['uncategorized']
    
    return display_info 