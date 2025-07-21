-- 职位与面试系统数据库初始化脚本
-- 创建时间: 2025年7月
-- 版本: v1.0

-- 设置字符集
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS interview_system 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE interview_system;

-- 用户表
DROP TABLE IF EXISTS `tb_user`;
CREATE TABLE `tb_user` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '用户ID',
  `username` varchar(80) NOT NULL COMMENT '用户名',
  `email` varchar(120) NOT NULL COMMENT '邮箱',
  `password` varchar(200) NOT NULL COMMENT '密码',
  `role` varchar(20) DEFAULT 'student' COMMENT '角色',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `realname` varchar(50) DEFAULT NULL COMMENT '真实姓名',
  `age` int DEFAULT NULL COMMENT '年龄',
  `phone` varchar(20) DEFAULT NULL COMMENT '手机号',
  `avatar` varchar(255) DEFAULT NULL COMMENT '头像',
  `intro` text COMMENT '个人介绍',
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`),
  KEY `idx_username` (`username`),
  KEY `idx_email` (`email`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- 职位表
DROP TABLE IF EXISTS `tb_job`;
CREATE TABLE `tb_job` (
  `id` varchar(50) NOT NULL COMMENT '职位ID',
  `title` varchar(200) NOT NULL COMMENT '职位名称',
  `company` varchar(200) NOT NULL COMMENT '公司名称',
  `location` varchar(100) DEFAULT NULL COMMENT '工作地点',
  `salary_min` int DEFAULT NULL COMMENT '最低薪资',
  `salary_max` int DEFAULT NULL COMMENT '最高薪资',
  `currency` varchar(10) DEFAULT 'CNY' COMMENT '货币单位',
  `experience` varchar(50) DEFAULT NULL COMMENT '经验要求',
  `education` varchar(50) DEFAULT NULL COMMENT '学历要求',
  `skills` json DEFAULT NULL COMMENT '技能要求',
  `description` text COMMENT '职位描述',
  `requirements` text COMMENT '任职要求',
  `benefits` text COMMENT '福利待遇',
  `posted_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '发布时间',
  `deadline` timestamp NULL DEFAULT NULL COMMENT '截止时间',
  `status` varchar(20) DEFAULT 'active' COMMENT '状态',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_title` (`title`),
  KEY `idx_company` (`company`),
  KEY `idx_location` (`location`),
  KEY `idx_posted_date` (`posted_date`),
  FULLTEXT KEY `idx_description` (`description`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='职位表';

-- 面试会话表
DROP TABLE IF EXISTS `tb_interview_session`;
CREATE TABLE `tb_interview_session` (
  `id` varchar(36) NOT NULL COMMENT '会话ID',
  `user_id` int NOT NULL COMMENT '用户ID',
  `job_id` varchar(50) DEFAULT NULL COMMENT '职位ID',
  `status` enum('created','started','paused','completed','cancelled') DEFAULT 'created' COMMENT '状态',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `started_at` timestamp NULL DEFAULT NULL COMMENT '开始时间',
  `completed_at` timestamp NULL DEFAULT NULL COMMENT '完成时间',
  `config` json DEFAULT NULL COMMENT '配置信息',
  `total_questions` int DEFAULT 0 COMMENT '总问题数',
  `answered_questions` int DEFAULT 0 COMMENT '已回答问题数',
  `overall_score` decimal(5,2) DEFAULT 0.00 COMMENT '总分',
  `technical_score` decimal(5,2) DEFAULT 0.00 COMMENT '技术分数',
  `communication_score` decimal(5,2) DEFAULT 0.00 COMMENT '沟通分数',
  `problem_solving_score` decimal(5,2) DEFAULT 0.00 COMMENT '问题解决分数',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_job_id` (`job_id`),
  KEY `idx_status` (`status`),
  KEY `idx_created_at` (`created_at`),
  KEY `idx_session_user_status` (`user_id`,`status`),
  CONSTRAINT `fk_interview_session_user` FOREIGN KEY (`user_id`) REFERENCES `tb_user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='面试会话表';

-- 面试问答记录表
DROP TABLE IF EXISTS `tb_interview_qa`;
CREATE TABLE `tb_interview_qa` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `session_id` varchar(36) NOT NULL COMMENT '会话ID',
  `question_index` int NOT NULL COMMENT '问题序号',
  `question` text NOT NULL COMMENT '问题内容',
  `answer` text COMMENT '回答内容',
  `technical_score` decimal(5,2) DEFAULT NULL COMMENT '技术分数',
  `communication_score` decimal(5,2) DEFAULT NULL COMMENT '沟通分数',
  `problem_solving_score` decimal(5,2) DEFAULT NULL COMMENT '问题解决分数',
  `overall_score` decimal(5,2) DEFAULT NULL COMMENT '总分',
  `question_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '问题时间',
  `answer_time` timestamp NULL DEFAULT NULL COMMENT '回答时间',
  `response_duration` int DEFAULT NULL COMMENT '回答时长(秒)',
  `analysis_result` json DEFAULT NULL COMMENT '分析结果',
  PRIMARY KEY (`id`),
  KEY `idx_session_id` (`session_id`),
  KEY `idx_question_index` (`question_index`),
  CONSTRAINT `fk_interview_qa_session` FOREIGN KEY (`session_id`) REFERENCES `tb_interview_session` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='面试问答记录表';

-- 人脸检测数据表
DROP TABLE IF EXISTS `tb_face_analysis`;
CREATE TABLE `tb_face_analysis` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `session_id` varchar(36) NOT NULL COMMENT '会话ID',
  `timestamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '时间戳',
  `face_detected` tinyint(1) DEFAULT 0 COMMENT '是否检测到人脸',
  `emotion` varchar(20) DEFAULT NULL COMMENT '情绪',
  `attention_score` decimal(3,2) DEFAULT NULL COMMENT '注意力分数',
  `confidence_level` decimal(3,2) DEFAULT NULL COMMENT '自信度',
  `eye_contact` tinyint(1) DEFAULT 0 COMMENT '是否眼神接触',
  `landmarks` json DEFAULT NULL COMMENT '关键点数据',
  PRIMARY KEY (`id`),
  KEY `idx_session_id` (`session_id`),
  KEY `idx_timestamp` (`timestamp`),
  CONSTRAINT `fk_face_analysis_session` FOREIGN KEY (`session_id`) REFERENCES `tb_interview_session` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='人脸检测数据表';

-- 简历表
DROP TABLE IF EXISTS `tb_resume`;
CREATE TABLE `tb_resume` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `user_id` int NOT NULL COMMENT '用户ID',
  `filename` varchar(255) NOT NULL COMMENT '文件名',
  `file_path` varchar(500) NOT NULL COMMENT '文件路径',
  `file_size` int DEFAULT NULL COMMENT '文件大小',
  `content` longtext COMMENT '解析内容',
  `skills` json DEFAULT NULL COMMENT '技能列表',
  `experience` text COMMENT '工作经验',
  `education` text COMMENT '教育背景',
  `analysis_result` json DEFAULT NULL COMMENT '分析结果',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_created_at` (`created_at`),
  CONSTRAINT `fk_resume_user` FOREIGN KEY (`user_id`) REFERENCES `tb_user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='简历表';

-- 用户职位收藏表
DROP TABLE IF EXISTS `tb_user_job_favorite`;
CREATE TABLE `tb_user_job_favorite` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `user_id` int NOT NULL COMMENT '用户ID',
  `job_id` varchar(50) NOT NULL COMMENT '职位ID',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_user_job` (`user_id`,`job_id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_job_id` (`job_id`),
  CONSTRAINT `fk_favorite_user` FOREIGN KEY (`user_id`) REFERENCES `tb_user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户职位收藏表';

-- 系统配置表
DROP TABLE IF EXISTS `tb_system_config`;
CREATE TABLE `tb_system_config` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `config_key` varchar(100) NOT NULL COMMENT '配置键',
  `config_value` text COMMENT '配置值',
  `description` varchar(255) DEFAULT NULL COMMENT '描述',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_config_key` (`config_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统配置表';

-- 插入初始数据
INSERT INTO `tb_system_config` (`config_key`, `config_value`, `description`) VALUES
('system_name', '面试星途', '系统名称'),
('system_version', '1.0.0', '系统版本'),
('max_interview_duration', '3600', '最大面试时长(秒)'),
('max_questions_per_interview', '10', '每次面试最大问题数'),
('enable_face_detection', 'true', '是否启用人脸检测'),
('enable_tts', 'true', '是否启用语音合成'),
('enable_ai_analysis', 'true', '是否启用AI分析');

-- 插入测试用户
INSERT INTO `tb_user` (`username`, `email`, `password`, `role`, `realname`, `age`) VALUES
('admin', 'admin@interview.com', 'pbkdf2:sha256:260000$salt$hash', 'admin', '系统管理员', 30),
('testuser', 'test@interview.com', 'pbkdf2:sha256:260000$salt$hash', 'student', '测试用户', 22);

-- 插入测试职位
INSERT INTO `tb_job` (`id`, `title`, `company`, `location`, `salary_min`, `salary_max`, `skills`, `description`) VALUES
('job_001', 'Python后端开发工程师', '科技创新公司', '北京', 15000, 25000, '["Python", "Django", "MySQL", "Redis"]', '负责后端系统开发和维护，要求熟悉Python和相关框架。'),
('job_002', '前端开发工程师', '互联网公司', '上海', 12000, 20000, '["Vue.js", "JavaScript", "CSS", "HTML"]', '负责前端页面开发和用户体验优化，要求熟悉Vue.js框架。'),
('job_003', '数据分析师', '数据科技公司', '深圳', 10000, 18000, '["Python", "SQL", "数据分析", "机器学习"]', '负责数据分析和挖掘工作，要求有统计学或相关专业背景。');

SET FOREIGN_KEY_CHECKS = 1;

-- 创建索引优化查询性能
CREATE INDEX idx_interview_date ON tb_interview_session(created_at);
CREATE INDEX idx_job_skills ON tb_job(skills(100));
CREATE INDEX idx_face_analysis_emotion ON tb_face_analysis(emotion);

-- 创建视图
CREATE VIEW v_user_interview_summary AS
SELECT 
    u.id as user_id,
    u.username,
    u.realname,
    COUNT(s.id) as total_interviews,
    AVG(s.overall_score) as avg_score,
    MAX(s.completed_at) as last_interview_date
FROM tb_user u
LEFT JOIN tb_interview_session s ON u.id = s.user_id
WHERE s.status = 'completed'
GROUP BY u.id, u.username, u.realname;

-- 数据库初始化完成
SELECT 'Database initialization completed successfully!' as message;
