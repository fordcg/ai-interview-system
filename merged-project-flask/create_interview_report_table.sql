-- 创建面试报告表
CREATE TABLE IF NOT EXISTS tb_interview_report (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    report_type VARCHAR(100) NOT NULL,
    title VARCHAR(200),
    analysis_data TEXT,  -- JSON格式的分析数据
    raw_data TEXT,       -- JSON格式的原始数据
    report_metadata TEXT, -- JSON格式的元数据
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active',
    FOREIGN KEY (user_id) REFERENCES tb_user (id)
);

-- 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_interview_report_user_id ON tb_interview_report(user_id);
CREATE INDEX IF NOT EXISTS idx_interview_report_type ON tb_interview_report(report_type);
CREATE INDEX IF NOT EXISTS idx_interview_report_status ON tb_interview_report(status);
CREATE INDEX IF NOT EXISTS idx_interview_report_created_at ON tb_interview_report(created_at);
