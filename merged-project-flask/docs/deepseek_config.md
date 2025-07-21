# DeepSeek API 配置说明

## 概述

本项目已集成 DeepSeek API 配置，支持使用 DeepSeek 的对话模型和推理模型。

## 配置项说明

在 `config.py` 文件中，已添加以下 DeepSeek API 相关配置：

### 基础配置常量

```python
# DeepSeek API配置
DEEPSEEK_API_KEY = ''  # 需要替换为实际的DeepSeek API Key
DEEPSEEK_BASE_URL = 'https://api.deepseek.com'  # DeepSeek API基础URL
DEEPSEEK_MODEL_CHAT = 'deepseek-chat'  # DeepSeek对话模型
DEEPSEEK_MODEL_REASONER = 'deepseek-reasoner'  # DeepSeek推理模型
DEEPSEEK_ENABLED = False  # 是否启用DeepSeek API功能
```

### Config 类属性

在 `Config` 类中，这些配置会被自动加载：

```python
# DeepSeek API配置
DEEPSEEK_API_KEY = DEEPSEEK_API_KEY
DEEPSEEK_BASE_URL = DEEPSEEK_BASE_URL
DEEPSEEK_MODEL_CHAT = DEEPSEEK_MODEL_CHAT
DEEPSEEK_MODEL_REASONER = DEEPSEEK_MODEL_REASONER
DEEPSEEK_ENABLED = DEEPSEEK_ENABLED
```

## 使用步骤

### 1. 获取 API Key

1. 访问 [DeepSeek 官网](https://platform.deepseek.com/)
2. 注册账号并申请 API Key
3. 复制您的 API Key

### 2. 配置 API Key

在 `config.py` 文件中，将 `DEEPSEEK_API_KEY` 设置为您的实际 API Key：

```python
DEEPSEEK_API_KEY = 'your_actual_api_key_here'
```

### 3. 启用功能

将 `DEEPSEEK_ENABLED` 设置为 `True`：

```python
DEEPSEEK_ENABLED = True
```

### 4. 验证配置

运行测试脚本验证配置是否正确：

```bash
python merged-project-flask/utils/deepseek_example.py
```

## 模型说明

### deepseek-chat
- **用途**: 通用对话模型
- **特点**: 适用于一般的对话和文本生成任务
- **对应模型**: DeepSeek-V3-0324

### deepseek-reasoner  
- **用途**: 推理模型
- **特点**: 适用于需要复杂推理的任务
- **对应模型**: DeepSeek-R1-0528

## API 兼容性

DeepSeek API 与 OpenAI API 格式兼容，可以使用 OpenAI SDK 进行调用：

```python
from openai import OpenAI

client = OpenAI(
    api_key="your_deepseek_api_key", 
    base_url="https://api.deepseek.com"
)

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"},
    ],
    stream=False
)
```

## 注意事项

1. **API Key 安全**: 请妥善保管您的 API Key，不要将其提交到版本控制系统
2. **费用控制**: 使用 API 会产生费用，请注意控制调用频率
3. **网络连接**: 确保服务器能够访问 `https://api.deepseek.com`
4. **依赖安装**: 使用前需要安装 OpenAI SDK：`pip install openai`

## 下一步

配置完成后，您可以：

1. 在现有的 API 中集成 DeepSeek 调用
2. 创建专门的 DeepSeek API 客户端工具类
3. 在面试分析、简历处理等功能中使用 DeepSeek 模型
