# 讯飞简历API响应数据样本

这个目录包含了模拟讯飞简历API的响应数据样本，用于测试简历解析功能。

## 样本文件说明

1. `xf_resume_response1.json` - 标准简历模板响应，包含3个基本模板
2. `xf_resume_response2.json` - 带有专业分类的简历模板响应，包含IT和Finance类别的模板
3. `xf_resume_response3.json` - 中文简历模板响应，包含带有中文名称的模板
4. `xf_resume_response4.json` - 空链接响应，links数组中的URL为null
5. `xf_resume_response5.json` - 错误响应，API返回错误码和错误信息
6. `xf_resume_response6.json` - 格式错误响应，返回的JSON中缺少links字段
7. `xf_real_api_response.json` - 真实API返回的数据，包含3个实际的简历模板链接

## 测试结果

我们已经验证了所有样本数据都可以被正确解析：
- 5个样本可以成功解析出模板链接
- 2个样本预期会失败（错误响应和格式错误响应）

真实API返回数据测试结果：
```
找到 3 个模板

模板 1:
  img_url: https://statics.zcmima.cn/uploads/resume/cover/20250712/14fd584f-6b50-47de-88f2-a5b16b431358.jpg
  word_url: https://file.duhuitech.com/o/9b7b3a56385721eb6cb8f5aea6a88b896/421d0929-d541-47e4-a26e-c1bd218d69f0.docx

模板 2:
  img_url: https://statics.zcmima.cn/uploads/resume/cover/20250712/e611aca1-21a4-4cfe-8cec-2d89c06d896f.jpg
  word_url: https://file.duhuitech.com/o/fe3ae1b77836bf777c82403d0cea243a7/58363209-80a8-49c2-a313-25463e15590b.docx

模板 3:
  img_url: https://statics.zcmima.cn/uploads/resume/cover/20250712/043786b5-f1e0-4f86-91ff-3d0c55464bce.jpg
  word_url: https://file.duhuitech.com/o/ca83a6ae5e933cb243d831e3ca13cc374/f268f274-b127-4eb0-aac7-ee0de276f05a.docx
```

## 使用方法

可以使用 `test_resume_samples.py` 脚本测试这些样本数据：

```bash
python test_resume_samples.py -a  # 测试所有样本
python test_resume_samples.py -r  # 测试真实API返回数据
```

或者使用 `resume_api_test_suite.py` 脚本进行更多高级测试：

```bash
python resume_api_test_suite.py --show-help  # 显示帮助信息
```

还可以直接在您的代码中使用这些样本数据进行测试：

```python
import json
from resume_job_matcher_api import parse_resume_api_response

# 读取样本数据
with open('resume_samples/xf_real_api_response.json', 'r', encoding='utf-8') as f:
    response_data = f.read()

# 解析数据
templates = parse_resume_api_response(response_data)

# 处理解析结果
if templates:
    print(f"找到 {len(templates)} 个简历模板")
    for i, template in enumerate(templates, 1):
        print(f"模板 {i}:")
        print(f"  预览图: {template.get('img_url')}")
        print(f"  下载链接: {template.get('word_url')}")
else:
    print("未找到简历模板")
``` 