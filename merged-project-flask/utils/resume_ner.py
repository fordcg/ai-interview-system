#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
简历命名实体识别模块
使用ModelScope的RANER模型进行简历实体识别
"""

import os
import logging
import jieba
import re
from typing import Dict, List, Any, Optional, Tuple, Set
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 获取项目根目录
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# 本地模型路径
LOCAL_MODEL_PATH = os.path.join(PROJECT_ROOT, 'models', 'nlp', 'raner_resume')


class ResumeNER:
    """简历命名实体识别类"""
    
    def __init__(self, model_path: str = None):
        """
        初始化简历命名实体识别模型
        
        Args:
            model_path: 模型路径，可以是本地路径或ModelScope模型ID
                       如果为None，则使用本地模型路径
        """
        # 如果没有指定模型路径，则使用本地模型路径
        if model_path is None:
            if os.path.exists(LOCAL_MODEL_PATH):
                self.model_path = LOCAL_MODEL_PATH
                logger.info(f"使用本地模型路径: {self.model_path}")
            else:
                # 如果本地模型不存在，则使用ModelScope模型ID
                self.model_path = 'damo/nlp_raner_named-entity-recognition_chinese-base-resume'
                logger.info(f"本地模型不存在，使用ModelScope模型ID: {self.model_path}")
        else:
            self.model_path = model_path
            
        self.ner_pipeline = None
        self.entity_types = {
            'CONT': '国籍',
            'EDU': '教育背景',
            'LOC': '籍贯',
            'NAME': '人名',
            'ORG': '组织名',
            'PRO': '专业',
            'RACE': '民族',
            'TITLE': '职称'
        }
        
        # 技能词典：常见技术技能和专业技能
        self.skill_dict = {
            # 编程语言
            'python', 'java', 'c++', 'c#', 'javascript', 'typescript', 'php', 'ruby', 'go', 'rust', 'swift', 'kotlin', 'r',
            # 前端技术
            'html', 'css', 'react', 'vue', 'angular', 'jquery', 'bootstrap', 'webpack', 'sass', 'less',
            # 后端技术
            'node.js', 'django', 'flask', 'spring', 'express', 'laravel', 'asp.net', 'ruby on rails',
            # 数据库
            'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'sqlite', 'oracle', 'sql server',
            # 大数据技术
            'hadoop', 'spark', 'hive', 'flink', 'kafka', 'storm',
            # 云计算
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'openstack',
            # AI/机器学习
            '机器学习', '深度学习', 'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'nlp', '自然语言处理',
            '计算机视觉', '图像处理', '推荐系统',
            # 移动开发
            'android', 'ios', 'flutter', 'react native', 'swift', 'objective-c',
            # 测试
            '自动化测试', '单元测试', '集成测试', '性能测试', 'selenium', 'junit', 'pytest',
            # 运维
            'devops', 'ci/cd', 'jenkins', 'git', 'linux', 'shell', 'ansible', 'puppet', 'chef',
            # 项目管理
            '敏捷开发', 'scrum', '项目管理', 'pmp', 'prince2',
            # 办公软件
            'office', 'word', 'excel', 'powerpoint', 'visio', 'project',
            # 设计
            'photoshop', 'illustrator', 'sketch', 'figma', 'ui设计', 'ux设计',
            # 通用技能
            '沟通能力', '团队协作', '问题解决', '时间管理', '领导力', '创新思维', '分析能力', '批判性思维',
            '英语', '日语', '法语', '德语', '西班牙语',
            # 金融领域
            '财务分析', '风险管理', '投资分析', '会计', '审计', '税务', 'cpa', 'cfa', 'frm',
            # 市场营销
            '市场分析', '品牌管理', '数字营销', '内容营销', 'seo', 'sem', '社交媒体营销',
            # 人力资源
            '招聘', '培训', '绩效管理', '薪酬福利', '员工关系', '人才发展',
            # 销售
            '客户关系管理', '销售策略', '谈判技巧', '客户开发', '销售管理',
            # 其他常见技能
            '数据分析', '报告撰写', '研究能力', '演讲能力', '谈判能力'
        }
        
        # 职称到技能的映射
        self.title_to_skills = {
            '软件工程师': ['编程', '软件开发', '代码审查', '调试', '单元测试'],
            '前端工程师': ['html', 'css', 'javascript', '前端框架', '响应式设计', 'ui开发'],
            '后端工程师': ['服务器开发', 'api设计', '数据库', '性能优化', '系统架构'],
            '全栈工程师': ['前端开发', '后端开发', '数据库设计', 'api开发', '全栈开发'],
            '数据分析师': ['数据分析', '数据可视化', '统计分析', '报告撰写', '数据挖掘'],
            '数据科学家': ['机器学习', '统计建模', '数据挖掘', '算法设计', '预测分析'],
            '产品经理': ['产品规划', '用户需求分析', '市场分析', '产品设计', '项目管理'],
            '项目经理': ['项目管理', '团队管理', '风险管理', '资源规划', '进度控制'],
            '测试工程师': ['软件测试', '测试用例设计', '自动化测试', '性能测试', '缺陷管理'],
            '运维工程师': ['系统运维', '服务器管理', '网络配置', '安全维护', '监控系统'],
            '网络工程师': ['网络配置', '网络安全', '路由器配置', '防火墙管理', 'vpn设置'],
            '安全工程师': ['网络安全', '安全审计', '漏洞分析', '安全测试', '安全策略'],
            '人工智能工程师': ['机器学习', '深度学习', '自然语言处理', '计算机视觉', '算法设计'],
            '区块链工程师': ['区块链开发', '智能合约', '分布式系统', '密码学', 'web3'],
            '游戏开发工程师': ['游戏开发', '3d建模', '游戏引擎', '物理引擎', '动画设计'],
            '移动开发工程师': ['移动应用开发', 'android开发', 'ios开发', '跨平台开发', '移动ui设计'],
            '嵌入式工程师': ['嵌入式系统', '单片机开发', '实时操作系统', '硬件接口', '驱动开发'],
            '云计算工程师': ['云服务', '虚拟化', '容器技术', '分布式系统', '云安全'],
            '大数据工程师': ['大数据处理', '数据仓库', '数据挖掘', '分布式计算', '数据建模'],
            'ui设计师': ['用户界面设计', '交互设计', '视觉设计', '原型设计', '用户体验'],
            'ux设计师': ['用户体验设计', '用户研究', '交互设计', '信息架构', '可用性测试'],
            '财务分析师': ['财务分析', '财务报告', '预算管理', '成本控制', '投资分析'],
            '会计': ['财务会计', '成本会计', '税务会计', '审计', '财务报表'],
            '市场营销专员': ['市场策略', '品牌推广', '市场调研', '营销活动', '市场分析'],
            '人力资源专员': ['招聘', '培训发展', '绩效管理', '员工关系', '薪酬福利'],
            '销售代表': ['销售技巧', '客户开发', '谈判能力', '关系管理', '销售策略'],
            '客户服务代表': ['客户沟通', '问题解决', '服务意识', '投诉处理', '客户满意度'],
            '研究员': ['研究方法', '数据分析', '文献综述', '报告撰写', '实验设计'],
            '教师': ['教学设计', '课程开发', '教学评估', '班级管理', '教育心理学']
        }
        
        # 专业到技能的映射
        self.major_to_skills = {
            '计算机科学': ['编程', '算法', '数据结构', '操作系统', '计算机网络', '数据库系统'],
            '软件工程': ['软件开发', '软件测试', '软件设计', '需求分析', '项目管理', '软件架构'],
            '信息技术': ['网络技术', '信息系统', '数据管理', 'it服务管理', '信息安全'],
            '电子工程': ['电路设计', '信号处理', '嵌入式系统', '电子元件', '控制系统'],
            '通信工程': ['通信系统', '信号处理', '无线通信', '网络协议', '移动通信'],
            '自动化': ['控制理论', '自动控制', 'plc编程', '传感器技术', '机器人技术'],
            '机械工程': ['机械设计', '机械制造', 'cad', '材料力学', '热力学'],
            '土木工程': ['结构设计', '建筑材料', '工程力学', '建筑设计', '工程管理'],
            '电气工程': ['电力系统', '电气控制', '高压技术', '电机学', '电力电子学'],
            '化学工程': ['化学反应', '化工设计', '化学分析', '工艺流程', '化工安全'],
            '材料科学': ['材料性能', '材料制备', '材料表征', '材料测试', '纳米材料'],
            '生物工程': ['生物技术', '基因工程', '细胞培养', '生物反应器', '生物信息学'],
            '环境工程': ['环境监测', '污染控制', '环境评估', '废物处理', '环境规划'],
            '数学': ['数学分析', '代数学', '几何学', '统计学', '运筹学'],
            '物理学': ['力学', '电磁学', '热学', '光学', '量子物理'],
            '化学': ['有机化学', '无机化学', '物理化学', '分析化学', '化学实验'],
            '生物学': ['分子生物学', '细胞生物学', '生态学', '遗传学', '生物化学'],
            '医学': ['临床医学', '基础医学', '药理学', '病理学', '解剖学'],
            '药学': ['药物化学', '药剂学', '药物分析', '临床药学', '药物设计'],
            '心理学': ['认知心理学', '发展心理学', '社会心理学', '心理测量', '心理咨询'],
            '经济学': ['微观经济学', '宏观经济学', '计量经济学', '国际经济学', '经济政策'],
            '金融学': ['金融市场', '投资学', '公司金融', '风险管理', '金融分析'],
            '会计学': ['财务会计', '管理会计', '成本会计', '审计学', '税务会计'],
            '管理学': ['组织行为学', '战略管理', '人力资源管理', '运营管理', '市场营销'],
            '市场营销': ['市场调研', '消费者行为', '品牌管理', '营销策略', '广告学'],
            '人力资源管理': ['招聘选拔', '培训发展', '绩效管理', '薪酬福利', '员工关系'],
            '国际贸易': ['国际商务', '贸易理论', '国际结算', '外贸实务', '国际市场营销'],
            '法学': ['民法', '刑法', '商法', '国际法', '宪法'],
            '新闻传播学': ['新闻学', '传播理论', '媒体研究', '广播电视', '网络传播'],
            '教育学': ['教育心理学', '课程与教学', '教育管理', '教育评价', '教育技术'],
            '艺术设计': ['视觉设计', '产品设计', '环境设计', '交互设计', '多媒体设计'],
            '音乐': ['音乐理论', '器乐演奏', '声乐', '作曲', '音乐史'],
            '体育': ['运动训练', '体育教育', '运动生理学', '体育管理', '体育心理学']
        }
        
        try:
            logger.info(f"正在加载NER模型: {self.model_path}")
            self.ner_pipeline = pipeline(Tasks.named_entity_recognition, self.model_path)
            logger.info("NER模型加载成功")
        except Exception as e:
            logger.error(f"加载NER模型失败: {str(e)}")
            raise RuntimeError(f"加载NER模型失败: {str(e)}")
    
    def _split_text_into_segments(self, text: str, max_length: int = 450) -> List[str]:
        """
        将长文本分割成适合模型处理的段落

        Args:
            text: 待分割的文本
            max_length: 每段的最大长度

        Returns:
            分割后的文本段落列表
        """
        if len(text) <= max_length:
            return [text]

        segments = []
        current_segment = ""

        # 按句子分割（中文句号、英文句号、感叹号、问号）
        sentences = []
        current_sentence = ""

        for char in text:
            current_sentence += char
            if char in ['。', '.', '!', '！', '?', '？', '\n']:
                if current_sentence.strip():
                    sentences.append(current_sentence.strip())
                current_sentence = ""

        # 处理最后一个句子
        if current_sentence.strip():
            sentences.append(current_sentence.strip())

        # 将句子组合成段落
        for sentence in sentences:
            if len(current_segment) + len(sentence) <= max_length:
                current_segment += sentence + " "
            else:
                if current_segment.strip():
                    segments.append(current_segment.strip())
                current_segment = sentence + " "

        # 处理最后一个段落
        if current_segment.strip():
            segments.append(current_segment.strip())

        # 如果还有超长段落，强制按字符分割
        final_segments = []
        for segment in segments:
            if len(segment) <= max_length:
                final_segments.append(segment)
            else:
                # 强制分割超长段落
                for i in range(0, len(segment), max_length):
                    final_segments.append(segment[i:i + max_length])

        return final_segments

    def recognize(self, text: str) -> List[Dict[str, Any]]:
        """
        识别文本中的命名实体

        Args:
            text: 待识别的文本

        Returns:
            识别出的实体列表，每个实体包含类型、开始位置、结束位置和文本内容
        """
        if not self.ner_pipeline:
            logger.error("NER模型未初始化")
            return []

        try:
            # 检查文本长度，如果超过限制则分段处理
            if len(text) > 450:
                logger.info(f"文本长度({len(text)})超过限制，进行分段处理")
                return self._recognize_long_text(text)

            result = self.ner_pipeline(text)
            entities = result.get('output', [])

            # 添加中文实体类型名称
            for entity in entities:
                entity_type = entity.get('type')
                entity['type_zh'] = self.entity_types.get(entity_type, entity_type)

            return entities
        except Exception as e:
            logger.error(f"实体识别失败: {str(e)}")
            return []

    def _recognize_long_text(self, text: str) -> List[Dict[str, Any]]:
        """
        处理长文本的实体识别

        Args:
            text: 长文本

        Returns:
            合并后的实体列表
        """
        segments = self._split_text_into_segments(text)
        all_entities = []
        current_offset = 0

        logger.info(f"将文本分为{len(segments)}段进行处理")

        for i, segment in enumerate(segments):
            try:
                logger.info(f"处理第{i+1}段，长度: {len(segment)}")
                result = self.ner_pipeline(segment)
                entities = result.get('output', [])

                # 调整实体位置偏移量
                for entity in entities:
                    entity_type = entity.get('type')
                    entity['type_zh'] = self.entity_types.get(entity_type, entity_type)

                    # 调整在原文本中的位置
                    if 'start' in entity:
                        entity['start'] += current_offset
                    if 'end' in entity:
                        entity['end'] += current_offset

                all_entities.extend(entities)

            except Exception as e:
                logger.error(f"处理第{i+1}段时出错: {str(e)}")
                continue

            # 更新偏移量（加上当前段落长度和一个空格）
            current_offset += len(segment) + 1

        logger.info(f"长文本处理完成，共识别出{len(all_entities)}个实体")
        return all_entities
    
    def extract_structured_info(self, text: str) -> Dict[str, Any]:
        """
        提取文本中的结构化信息
        
        Args:
            text: 待提取的文本
        
        Returns:
            结构化的简历信息，包含各类实体
        """
        entities = self.recognize(text)
        
        # 按类型分组
        structured_info = {
            'name': [],
            'education': [],
            'organization': [],
            'title': [],
            'major': [],
            'nationality': [],
            'ethnicity': [],
            'location': [],
            'raw_entities': entities  # 保留原始实体列表
        }
        
        # 将实体分类
        for entity in entities:
            entity_type = entity.get('type')
            entity_text = entity.get('span')
            
            if entity_type == 'NAME':
                structured_info['name'].append(entity_text)
            elif entity_type == 'EDU':
                structured_info['education'].append(entity_text)
            elif entity_type == 'ORG':
                structured_info['organization'].append(entity_text)
            elif entity_type == 'TITLE':
                structured_info['title'].append(entity_text)
            elif entity_type == 'PRO':
                structured_info['major'].append(entity_text)
            elif entity_type == 'CONT':
                structured_info['nationality'].append(entity_text)
            elif entity_type == 'RACE':
                structured_info['ethnicity'].append(entity_text)
            elif entity_type == 'LOC':
                structured_info['location'].append(entity_text)
        
        # 提取技能信息
        skills = self.extract_skills(text, structured_info)
        structured_info['skills'] = skills
        
        return structured_info
    
    def extract_skills(self, text: str, structured_info: Dict[str, Any] = None) -> List[str]:
        """
        从文本中提取技能关键词
        
        Args:
            text: 待提取的文本
            structured_info: 已提取的结构化信息，包含职称和专业等信息
        
        Returns:
            提取的技能列表
        """
        skills = set()
        
        # 1. 基于职称提取技能
        if structured_info and 'title' in structured_info:
            for title in structured_info['title']:
                # 将职称转换为小写，便于匹配
                title_lower = title.lower()
                # 检查是否在职称-技能映射中
                for known_title, related_skills in self.title_to_skills.items():
                    if known_title in title_lower:
                        skills.update(related_skills)
        
        # 2. 基于专业提取技能
        if structured_info and 'major' in structured_info:
            for major in structured_info['major']:
                # 将专业转换为小写，便于匹配
                major_lower = major.lower()
                # 检查是否在专业-技能映射中
                for known_major, related_skills in self.major_to_skills.items():
                    if known_major in major_lower:
                        skills.update(related_skills)
        
        # 3. 基于关键词匹配提取技能
        # 使用jieba分词
        words = jieba.lcut(text)
        # 提取2-3个词的组合，可能是技能短语
        phrases = []
        for i in range(len(words)):
            if i < len(words) - 1:
                phrases.append(words[i] + words[i+1])
            if i < len(words) - 2:
                phrases.append(words[i] + words[i+1] + words[i+2])
        
        # 将单词和短语与技能词典匹配
        for word in words + phrases:
            word_lower = word.lower()
            if word_lower in self.skill_dict:
                skills.add(word_lower)
        
        # 4. 使用正则表达式匹配常见技能模式
        # 例如：熟练掌握XXX、精通XXX、了解XXX等
        skill_patterns = [
            r'熟练掌握\s*([^\s，。、；：""''（）,.;:\'\"]+)',
            r'精通\s*([^\s，。、；：""''（）,.;:\'\"]+)',
            r'熟悉\s*([^\s，。、；：""''（）,.;:\'\"]+)',
            r'了解\s*([^\s，。、；：""''（）,.;:\'\"]+)',
            r'掌握\s*([^\s，。、；：""''（）,.;:\'\"]+)',
            r'使用\s*([^\s，。、；：""''（）,.;:\'\"]+)经验',
            r'([^\s，。、；：""''（）,.;:\'\"]+)\s*开发经验',
            r'([^\s，。、；：""''（）,.;:\'\"]+)\s*工程师',
            r'([^\s，。、；：""''（）,.;:\'\"]+)\s*专员',
            r'([^\s，。、；：""''（）,.;:\'\"]+)\s*经理'
        ]
        
        for pattern in skill_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                skill = match.group(1).strip().lower()
                if len(skill) > 1:  # 避免单个字符
                    skills.add(skill)
        
        # 5. 处理技能别名和规范化
        normalized_skills = set()
        for skill in skills:
            # 处理一些常见的别名和缩写
            if skill in ['js', 'javascript', 'javascripts']:
                normalized_skills.add('javascript')
            elif skill in ['py', 'python']:
                normalized_skills.add('python')
            elif skill in ['java', 'java语言']:
                normalized_skills.add('java')
            elif skill in ['r', 'r语言']:
                normalized_skills.add('R语言')  # 将r标准化为R语言
            else:
                normalized_skills.add(skill)


        # 6. 二次模型提取（基于NER实体信息进行深度技能推断）
        enhanced_skills = self._enhance_skills_with_ner(text, list(normalized_skills), structured_info)

        return enhanced_skills

    def _enhance_skills_with_ner(self, text: str, initial_skills: List[str], structured_info: Dict[str, Any]) -> List[str]:
        """
        基于NER实体信息进行二次技能提取和增强

        Args:
            text: 原始文本
            initial_skills: 初次提取的技能列表
            structured_info: NER提取的结构化信息

        Returns:
            增强后的技能列表
        """
        enhanced_skills = set(initial_skills)

        try:
            # 1. 基于组织名称推断技能
            if structured_info and 'organization' in structured_info:
                for org in structured_info['organization']:
                    org_skills = self._infer_skills_from_organization(org)
                    enhanced_skills.update(org_skills)

            # 2. 基于教育背景推断技能
            if structured_info and 'education' in structured_info:
                for edu in structured_info['education']:
                    edu_skills = self._infer_skills_from_education(edu)
                    enhanced_skills.update(edu_skills)

            # 3. 基于上下文分析提取技能
            context_skills = self._extract_skills_from_context(text, structured_info)
            enhanced_skills.update(context_skills)

            # 4. 基于实体周围文本提取技能
            entity_skills = self._extract_skills_around_entities(text, structured_info)
            enhanced_skills.update(entity_skills)

            # 5. 技能去重和过滤
            filtered_skills = self._filter_and_deduplicate_skills(list(enhanced_skills))

            logger.info(f"二次提取完成: 初始技能数量 {len(initial_skills)}, 增强后技能数量 {len(filtered_skills)}")
            return filtered_skills

        except Exception as e:
            logger.error(f"二次技能提取失败: {str(e)}")
            return initial_skills

    def _infer_skills_from_organization(self, organization: str) -> List[str]:
        """基于组织名称推断相关技能"""
        skills = []
        org_lower = organization.lower()

        # 科技公司技能映射
        tech_companies = {
            '阿里巴巴': ['java', 'spring', 'mysql', 'redis', 'dubbo', '分布式系统'],
            '腾讯': ['c++', 'go', 'mysql', 'redis', '游戏开发', '社交网络'],
            '百度': ['python', '机器学习', '深度学习', '自然语言处理', '搜索引擎'],
            '字节跳动': ['go', 'python', '推荐系统', '大数据', 'kafka'],
            '华为': ['c++', 'java', '网络技术', '5g', '云计算'],
            '小米': ['android', 'java', 'iot', '移动开发'],
            '美团': ['java', 'spring', 'mysql', 'redis', 'o2o'],
            '滴滴': ['go', 'java', '地图服务', '实时计算'],
            'google': ['python', 'go', 'tensorflow', '云计算', '搜索'],
            'microsoft': ['c#', '.net', 'azure', 'sql server'],
            'amazon': ['aws', 'java', 'python', '云服务'],
            'facebook': ['react', 'php', 'mysql', '社交网络'],
            'apple': ['swift', 'objective-c', 'ios', 'macos']
        }

        for company, company_skills in tech_companies.items():
            if company in org_lower:
                skills.extend(company_skills)
                break

        # 行业关键词技能映射
        if any(keyword in org_lower for keyword in ['银行', '金融', '证券', '保险']):
            skills.extend(['金融', '风险管理', '数据分析', 'sql'])
        elif any(keyword in org_lower for keyword in ['医院', '医疗', '制药']):
            skills.extend(['医疗', '生物信息学', '数据分析'])
        elif any(keyword in org_lower for keyword in ['教育', '学校', '培训']):
            skills.extend(['教学', '课程设计', '教育技术'])

        return skills

    def _infer_skills_from_education(self, education: str) -> List[str]:
        """基于教育背景推断相关技能"""
        skills = []
        edu_lower = education.lower()

        # 学历层次技能映射
        if any(keyword in edu_lower for keyword in ['博士', 'phd', '博士学位']):
            skills.extend(['研究能力', '学术写作', '数据分析', '项目管理'])
        elif any(keyword in edu_lower for keyword in ['硕士', 'master', '研究生']):
            skills.extend(['研究能力', '数据分析', '学术写作'])

        # 学校类型技能映射
        if any(keyword in edu_lower for keyword in ['985', '211', '清华', '北大', '复旦', '交大']):
            skills.extend(['学习能力', '分析能力', '解决问题'])

        return skills

    def _extract_skills_from_context(self, text: str, structured_info: Dict[str, Any]) -> List[str]:
        """基于上下文分析提取技能"""
        skills = []

        # 项目经验相关技能提取
        project_patterns = [
            r'项目[中使用了|采用了|运用了]\s*([^。，；\n]+)',
            r'负责\s*([^。，；\n]*?)(开发|设计|实现)',
            r'参与\s*([^。，；\n]*?)(项目|系统|平台)',
            r'开发了\s*([^。，；\n]+)',
            r'设计了\s*([^。，；\n]+)',
            r'实现了\s*([^。，；\n]+)'
        ]

        for pattern in project_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                context = match.group(1).strip()
                # 从上下文中提取技能词汇
                context_skills = self._extract_skills_from_text_segment(context)
                skills.extend(context_skills)

        return skills

    def _extract_skills_around_entities(self, text: str, structured_info: Dict[str, Any]) -> List[str]:
        """基于实体周围文本提取技能"""
        skills = []

        if not structured_info or 'raw_entities' not in structured_info:
            return skills

        # 分析每个实体周围的文本
        for entity in structured_info['raw_entities']:
            start = entity.get('start', 0)
            end = entity.get('end', 0)

            # 获取实体前后的上下文（前后各50个字符）
            context_start = max(0, start - 50)
            context_end = min(len(text), end + 50)
            context = text[context_start:context_end]

            # 从上下文中提取技能
            context_skills = self._extract_skills_from_text_segment(context)
            skills.extend(context_skills)

        return skills

    def _extract_skills_from_text_segment(self, text_segment: str) -> List[str]:
        """从文本片段中提取技能"""
        skills = []

        # 使用jieba分词
        words = jieba.lcut(text_segment)

        # 检查每个词是否在技能词典中
        for word in words:
            word_lower = word.lower().strip()
            if len(word_lower) > 1 and word_lower in self.skill_dict:
                skills.append(word_lower)

        return skills

    def _filter_and_deduplicate_skills(self, skills: List[str]) -> List[str]:
        """技能去重和过滤"""
        # 去重
        unique_skills = list(set(skills))

        # 过滤掉过短或无意义的技能
        filtered_skills = []

        # 单字符技能白名单（只有这些单字符才被认为是有效技能）
        single_char_whitelist = {'r'}  # R语言（但会被标准化为"R语言"）

        # 无效技能黑名单
        invalid_skills = {
            '的', '了', '在', '和', '与', '或', '及', '等', '有', '是', '为',
            'c',  # 移除单字符c，因为它通常是误提取
            'a', 'b', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
            'n', 'o', 'p', 'q', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
            '1', '2', '3', '4', '5', '6', '7', '8', '9', '0'
        }

        # 无效模式（正则表达式）
        import re
        invalid_patterns = [
            r'^\d+名',  # 如"3名初级"
            r'^\d+年',  # 如"2023年网页"
            r'^\d+个',  # 如"5个模块"
            r'^\d+%',   # 如"35%"
            r'^\d+万',  # 如"10万次"
            r'^\d+\.?\d*%',  # 如"99.8%"
            r'^第\d+',  # 如"第1段"
            r'.*担任.*',  # 如"曾在阿里巴巴担任高级软件"
            r'.*具有.*',  # 如"具有5年python"
            r'.*拥有.*',  # 如"拥有本科教育"
            r'.*负责.*',  # 如"负责整合"
            r'.*主导.*',  # 如"主导开发"
            r'.*指导.*',  # 如"指导3名"
            r'.*参与.*',  # 如"参与开发"
            r'.*使用.*',  # 如"使用Java"
            r'.*利用.*',  # 如"利用云计算"
            r'.*通过.*',  # 如"通过自动化"
            r'.*基于.*',  # 如"基于以太坊"
            r'.*进行.*',  # 如"进行数据存储"
            r'.*实现.*',  # 如"实现核心功能"
            r'.*完成.*',  # 如"完成5个模块"
            r'.*掌握.*',  # 如"掌握PHP开发技能"
            r'.*熟悉.*',  # 如"熟悉PostgreSQL"
            r'.*精通.*',  # 如"精通前端技术"
            r'.*了解.*',  # 如"了解区块链"
        ]

        for skill in unique_skills:
            original_skill = skill.strip()
            skill_lower = original_skill.lower()

            # 过滤条件
            if skill_lower in invalid_skills:
                continue

            # 检查无效模式
            is_invalid = False
            for pattern in invalid_patterns:
                if re.match(pattern, original_skill):
                    is_invalid = True
                    break

            if is_invalid:
                continue

            # 单字符技能特殊处理
            if len(skill_lower) == 1:
                if skill_lower in single_char_whitelist:
                    filtered_skills.append(skill_lower)
                continue

            # 长度大于1的技能
            if (len(skill_lower) > 1 and
                not skill_lower.isdigit() and
                not skill_lower.isspace() and
                len(skill_lower) <= 20):  # 限制最大长度，避免提取到句子

                # 进一步检查是否是有效的技能词汇
                # 技能通常是名词或技术术语，不应包含动词短语
                if not any(word in skill_lower for word in ['担任', '具有', '拥有', '负责', '主导', '指导', '参与', '使用', '利用', '通过', '基于', '进行', '实现', '完成', '掌握', '熟悉', '精通', '了解']):
                    filtered_skills.append(original_skill)

        return filtered_skills

# 单例模式，确保只加载一次模型
_resume_ner_instance = None

def get_resume_ner(model_path: str = None) -> ResumeNER:
    """
    获取ResumeNER实例（单例模式）
    
    Args:
        model_path: 模型路径，可以是本地路径或ModelScope模型ID
                  如果为None则使用默认路径
    
    Returns:
        ResumeNER实例
    """
    global _resume_ner_instance
    
    if _resume_ner_instance is None:
        _resume_ner_instance = ResumeNER(model_path)
    elif model_path is not None and model_path != _resume_ner_instance.model_path:
        # 如果指定了不同的模型路径，则重新创建实例
        logger.info(f"重新加载模型，路径: {model_path}")
        _resume_ner_instance = ResumeNER(model_path)
    
    return _resume_ner_instance 