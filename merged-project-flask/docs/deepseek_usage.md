# DeepSeek API 使用指南

## 概述

本项目已完整集成 DeepSeek API，提供了客户端工具类和 REST API 接口。

## 功能特性

### 1. DeepSeek 客户端工具类 (`utils/deepseek_client.py`)

- ✅ **基础聊天功能**: 支持对话模式和文本生成
- ✅ **流式响应**: 支持实时流式文本生成
- ✅ **面试分析**: 专门的面试回答分析功能
- ✅ **简历分析**: 简历内容结构化分析
- ✅ **错误处理**: 完善的异常处理和重试机制
- ✅ **配置验证**: 自动验证 API 配置和可用性

### 2. REST API 接口 (`api/deepseek_api.py`)

提供以下 HTTP 接口：

#### 连接测试
```
GET /api/deepseek/test
```

#### 面试问题生成
```
POST /api/deepseek/generate/interview-question
Content-Type: application/json

{
    "job_position": "Python开发工程师",
    "star_workflow_data": "项目STAR结构数据",
    "job_analysis_result": "岗位要求分析结果",
    "original_workflow_content": "简历能力项数据",
    "job_resume_workflow_result": "评估结果",
    "resume_upload_data": "简历文本数据"
}
```

#### 面试回答分析
```
POST /api/deepseek/analyze/interview
Content-Type: application/json

{
    "question": "请介绍一下你的项目经验",
    "answer": "我参与过多个Web开发项目...",
    "job_position": "Web开发工程师"
}
```



#### 配置信息
```
GET /api/deepseek/config
```

## 使用步骤

### 1. 安装依赖

```bash
# 进入项目目录
cd merged-project-flask

# 激活虚拟环境（如果使用）
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装 OpenAI SDK
pip install openai
```

### 2. 配置 API Key

在 `config.py` 文件中设置您的 DeepSeek API Key：

```python
# DeepSeek API配置
DEEPSEEK_API_KEY = 'your_actual_api_key_here'  # 替换为实际的API Key
DEEPSEEK_ENABLED = True  # 启用功能
```

### 3. 测试配置

```bash
# 测试客户端工具类
python utils/deepseek_client.py

# 测试配置示例
python utils/deepseek_example.py
```

### 4. 启动服务

```bash
# 启动 Flask 应用
python app.py
```

### 5. 测试 API 接口

```bash
# 测试连接
curl http://localhost:5000/api/deepseek/test

# 测试面试问题生成
curl -X POST http://localhost:5000/api/deepseek/generate/interview-question \
  -H "Content-Type: application/json" \
  -d '{"job_position": "Python开发工程师", "star_workflow_data": "项目经历", "job_analysis_result": "岗位要求", "original_workflow_content": "技能匹配", "job_resume_workflow_result": "评估结果", "resume_upload_data": "简历内容"}'
```

## 代码示例

### 在 Python 代码中使用

```python
from utils.deepseek_client import DeepSeekClient

# 创建客户端
client = DeepSeekClient()

# 检查可用性
if client.is_available():
    # 生成面试问题
    questions = client.generate_interview_questions(
        job_position="Python开发工程师",
        star_workflow_data="项目STAR结构数据",
        job_analysis_result="岗位要求分析结果",
        original_workflow_content="简历能力项数据",
        job_resume_workflow_result="评估结果",
        resume_upload_data="简历文本数据"
    )
    print(questions)

    # 面试分析
    analysis = client.analyze_interview_answer(
        question="请介绍你的技术栈",
        answer="我熟悉Python、JavaScript和数据库技术",
        job_position="全栈开发工程师"
    )
    print(analysis)
```

### 在 JavaScript 中调用 API

```javascript
// 面试问题生成接口
async function generateInterviewQuestions(jobPosition, starData, jobAnalysis, workflowContent, evaluationResult, resumeData) {
    const response = await fetch('/api/deepseek/generate/interview-question', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            job_position: jobPosition,
            star_workflow_data: starData,
            job_analysis_result: jobAnalysis,
            original_workflow_content: workflowContent,
            job_resume_workflow_result: evaluationResult,
            resume_upload_data: resumeData
        })
    });

    const result = await response.json();
    return result;
}

// 面试分析接口
async function analyzeInterview(question, answer, jobPosition) {
    const response = await fetch('/api/deepseek/analyze/interview', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            question: question,
            answer: answer,
            job_position: jobPosition
        })
    });
    
    const result = await response.json();
    return result;
}
```

## 模型选择

### deepseek-chat (默认)
- **适用场景**: 一般对话、文本生成、简历分析
- **特点**: 响应速度快，适合大多数场景

### deepseek-reasoner
- **适用场景**: 复杂推理、面试分析、逻辑判断
- **特点**: 推理能力强，适合需要深度分析的任务

## 注意事项

1. **API Key 安全**: 不要将 API Key 提交到版本控制系统
2. **费用控制**: DeepSeek API 按使用量计费，注意控制调用频率
3. **网络连接**: 确保服务器能访问 `https://api.deepseek.com`
4. **错误处理**: 生产环境中要做好错误处理和降级方案
5. **并发限制**: 注意 API 的并发调用限制

## 故障排除

### 常见问题

1. **"DeepSeek 客户端不可用"**
   - 检查 `DEEPSEEK_ENABLED` 是否为 `True`
   - 检查 `DEEPSEEK_API_KEY` 是否设置
   - 检查是否安装了 `openai` 包

2. **"连接测试失败"**
   - 检查网络连接
   - 验证 API Key 是否正确
   - 检查防火墙设置

3. **"未安装 openai 包"**
   ```bash
   pip install openai
   ```

### 调试模式

在 `config.py` 中启用调试模式：

```python
DEBUG = True
```

这将输出详细的错误信息和调用日志。
