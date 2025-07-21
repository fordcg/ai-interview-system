import axios from 'axios';

// 创建axios实例
const api = axios.create({
  baseURL: process.env.VUE_APP_API_URL || 'http://localhost:5000/api',
  timeout: 60000, // 请求超时时间
  headers: {
    'Content-Type': 'application/json'
  },
  // 添加CORS支持
  withCredentials: false
});

// 创建文件上传专用的axios实例
const uploadApi = axios.create({
  baseURL: process.env.VUE_APP_API_URL || 'http://localhost:5000/api',
  timeout: 180000, // 增加上传文件超时时间到3分钟
  headers: {
    'Content-Type': 'multipart/form-data'
  },
  // 添加CORS支持
  withCredentials: false
});

// 创建工作流API专用的axios实例
const workflowApi = axios.create({
  baseURL: process.env.VUE_APP_WORKFLOW_URL || 'http://localhost:8000/api',
  timeout: 300000, // 5分钟超时，支持3分钟工作流处理时间
  headers: {
    'Content-Type': 'application/json'
  },
  // 添加CORS支持
  withCredentials: false
});

// 添加请求拦截器，记录请求信息
api.interceptors.request.use(
  config => {
    console.log(`[API请求] ${config.method.toUpperCase()} ${config.url}`);
    return config;
  },
  error => {
    console.error('[API请求错误]', error);
    return Promise.reject(error);
  }
);

uploadApi.interceptors.request.use(
  config => {
    console.log(`[上传请求] ${config.method.toUpperCase()} ${config.url}`);
    return config;
  },
  error => {
    console.error('[上传请求错误]', error);
    return Promise.reject(error);
  }
);

/**
 * 上传简历文件
 * @param {File} file 简历文件
 * @returns {Promise} 上传结果
 */
export function uploadResumeFile(file) {
  const formData = new FormData();
  formData.append('file', file);
  
  console.log(`开始上传文件: ${file.name}, 大小: ${file.size} 字节`);
  console.log(`上传URL: ${uploadApi.defaults.baseURL}/upload`);
  
  return uploadApi.post('/upload', formData).then(response => {
    console.log('上传API响应:', response.data);
    
    // 处理不同的返回格式
    if (response.data && response.data.code === 0) {
      // 主Flask后端的返回格式
      const filename = response.data.data.filename;
      // 使用完整的文件URL
      const fileUrl = `${uploadApi.defaults.baseURL}/uploads/${filename}`;
      
      console.log('API返回的文件名:', filename);
      console.log('构建的文件URL:', fileUrl);
      
      return {
        data: {
          success: true,
          message: '文件上传成功',
          data: {
            filename: filename,
            url: fileUrl,
            size: file.size
          }
        }
      };
    }
    
    // 返回原始响应
    return response;
  }).catch(error => {
    console.error('上传文件失败:', error);
    if (error.response) {
      console.error('错误响应数据:', error.response.data);
      console.error('错误状态码:', error.response.status);
    } else if (error.request) {
      console.error('未收到响应，请确认服务器是否运行');
    }
    throw error;
  });
}

/**
 * 处理简历工作流
 * @param {string} pdfLink PDF文档链接或文本内容
 * @param {boolean} isText 是否是文本内容
 * @returns {Promise} 处理结果
 */
export function processResumeWorkflow(pdfLink, isText = false) {
  if (isText) {
    console.log(`调用工作流API处理简历文本，长度: ${pdfLink.length} 字符`);
    console.log(`工作流API URL: ${workflowApi.defaults.baseURL}/workflow/resume`);
    console.log(`请求参数: `, { text_content: pdfLink.substring(0, 100) + '...' });
  } else {
    console.log(`调用工作流API处理简历链接: ${pdfLink}`);
    console.log(`工作流API URL: ${workflowApi.defaults.baseURL}/workflow/resume`);
    console.log(`请求参数: `, { pdf_link: pdfLink });
  }
  
  // 添加请求拦截器，记录详细的请求信息
  const requestInterceptor = workflowApi.interceptors.request.use(
    config => {
      console.log(`[工作流API请求] ${config.method.toUpperCase()} ${config.url}`);
      console.log(`[工作流API请求头] `, config.headers);
      console.log(`[工作流API请求数据] `, config.data);
      return config;
    },
    error => {
      console.error('[工作流API请求错误]', error);
      return Promise.reject(error);
    }
  );
  
  // 添加响应拦截器，记录详细的响应信息
  const responseInterceptor = workflowApi.interceptors.response.use(
    response => {
      console.log(`[工作流API响应] 状态码: ${response.status}`);
      console.log(`[工作流API响应头] `, response.headers);
      console.log(`[工作流API响应数据] `, response.data);
      return response;
    },
    error => {
      console.error('[工作流API响应错误]', error);
      if (error.response) {
        console.error('错误响应数据:', error.response.data);
        console.error('错误状态码:', error.response.status);
        console.error('错误响应头:', error.response.headers);
      }
      return Promise.reject(error);
    }
  );
  
  // 根据参数类型构建请求数据
  const requestData = isText ? { text_content: pdfLink } : { pdf_link: pdfLink };
  
  return workflowApi.post('/workflow/resume', requestData)
  .then(response => {
    // 移除拦截器
    workflowApi.interceptors.request.eject(requestInterceptor);
    workflowApi.interceptors.response.eject(responseInterceptor);
    return response;
  })
  .catch(error => {
    // 移除拦截器
    workflowApi.interceptors.request.eject(requestInterceptor);
    workflowApi.interceptors.response.eject(responseInterceptor);
    
    console.error('工作流处理失败:', error);
    
    // 检查是否有响应数据，即使是错误响应
    if (error.response && error.response.data) {
      console.error('错误响应数据:', error.response.data);
      
      // 更广泛地查找有效内容
      let content = null;
      let originalData = error.response.data;
      
      // 尝试从各种可能的结构中提取内容
      if (originalData.data && originalData.data.workflow_response && 
          originalData.data.workflow_response.content) {
        content = originalData.data.workflow_response.content;
      } else if (originalData.workflow_response && originalData.workflow_response.content) {
        content = originalData.workflow_response.content;
      } else if (originalData.content) {
        content = originalData.content;
      } else if (originalData.data && originalData.data.choices && 
                originalData.data.choices[0] && 
                originalData.data.choices[0].delta && 
                originalData.data.choices[0].delta.content) {
        content = originalData.data.choices[0].delta.content;
      } else if (typeof originalData === 'string' && originalData.includes('{')) {
        // 尝试解析JSON字符串
        try {
          const parsedData = JSON.parse(originalData);
          if (parsedData.content) {
            content = parsedData.content;
          } else if (parsedData.data && parsedData.data.content) {
            content = parsedData.data.content;
          }
        } catch (e) {
          console.warn('无法解析响应数据为JSON:', e);
        }
      }
      
      // 如果在错误响应中找到了内容，验证其有效性
      if (content) {
        console.log('在错误响应中找到content，验证有效性...');
        console.log('Content长度:', content.length);
        console.log('Content预览:', content.substring(0, 200) + '...');

        // 验证内容有效性
        const isValidContent = content.length >= 100 &&
                              !content.toLowerCase().includes('error') &&
                              !content.toLowerCase().includes('失败') &&
                              !content.toLowerCase().includes('错误');

        if (isValidContent) {
          console.log('内容验证通过，保存到localStorage');

          // 保存原始内容到localStorage
          try {
            localStorage.setItem('originalWorkflowContent', content);
            console.log('已保存有效的原始内容到localStorage');
          } catch (e) {
            console.error('保存原始内容到localStorage失败:', e);
          }
        } else {
          console.warn('内容验证失败，可能是错误信息，不保存到localStorage');
          console.warn('内容详情:', content);
          // 内容无效，不返回成功响应，继续抛出错误
        }

        // 只有内容验证通过才创建成功响应对象
        if (isValidContent) {
          const modifiedResponse = {
            status: 200,
            data: {
              success: true,
              message: '已成功提取内容 (原始API返回为错误状态)',
              data: {
                workflow_response: { content }
              },
              originalError: error.response.data.message || '未知错误'
            }
          };

          return modifiedResponse;
        }
      }
      
      console.error('错误状态码:', error.response.status);
    } else if (error.request) {
      console.error('未收到响应，请确认工作流服务器是否运行在端口8000');
    }
    throw error;
  });
}

/**
 * 获取简历模板
 * @param {string} responseData 讯飞API返回的数据
 * @returns {Promise} 模板列表
 */
export function getResumeTemplates(responseData) {
  return api.post('/resume/parse_templates', {
    response_data: responseData
  });
}

/**
 * 分析简历文档
 * @param {string} resumeUrl 简历文档URL
 * @param {string} resumeText 可选的简历文本内容
 * @returns {Promise} 分析结果
 */
export function analyzeResume(resumeUrl, resumeText) {
  console.log('开始调用简历分析API, URL:', resumeUrl);
  
  // 准备请求数据，如果有文本内容则一并发送
  const requestData = {
    resumeUrl: resumeUrl
  };
  
  if (resumeText) {
    requestData.resumeText = resumeText;
    console.log('同时发送简历文本，长度:', resumeText.length);
  }
  
  // 添加更详细的请求配置
  return api.post('/resume/process', requestData, {
    timeout: 180000, // 增加超时时间到3分钟
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    }
  }).then(response => {
    console.log('简历分析API返回成功:', response.status);
    // 打印完整的响应内容，帮助调试
    console.log('简历分析API响应内容:', JSON.stringify(response.data).substring(0, 500) + '...');
    return response;
  }).catch(error => {
    console.error('简历分析API请求失败:', error.message);
    if (error.response) {
      console.error('错误状态码:', error.response.status);
      console.error('错误响应数据:', error.response.data);
    } else if (error.request) {
      console.error('未收到响应，请检查网络或服务器状态');
    }
    throw error;
  });
}

/**
 * 生成AI简历
 * @param {Object} formData 简历表单数据
 * @param {string} formData.name 姓名
 * @param {string} formData.education 教育经历
 * @param {Array} formData.skills 技能列表
 * @param {string} formData.experience 工作经历
 * @returns {Promise} 生成结果
 */
export function generateResume(formData) {
  console.log('开始调用AI简历生成API, 表单数据:', formData);
  console.log(`生成简历API URL: ${api.defaults.baseURL}/resume/generate`);

  return api.post('/resume/generate', formData, {
    timeout: 180000, // 增加超时时间到3分钟
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    }
  }).then(response => {
    console.log('AI简历生成API返回成功:', response.status);
    console.log('API响应数据:', response.data);
    return response;
  }).catch(error => {
    console.error('AI简历生成API请求失败:', error.message);
    if (error.response) {
      console.error('错误状态码:', error.response.status);
      console.error('错误响应数据:', error.response.data);
    } else if (error.request) {
      console.error('未收到响应，请检查网络或服务器状态');
    }
    throw error;
  });
}

/**
 * @param {string} textContent 可选的简历文本内容，如果提供则优先使用
 * @returns {Promise} 包含简历分析和STAR分析结果的Promise
 */
export function processResumeWithStar(textContent) {
  // 如果提供了文本内容，直接使用
  if (textContent) {
    return new Promise(async (resolve) => {
      try {
        console.log('使用提供的文本内容进行简历和STAR分析...');
        console.log('同时发起简历分析和STAR分析API请求, 文本长度:', textContent.length);

        // 同时发起两个API请求，而不是等待
        const resumePromise = workflowApi.post('/workflow/resume', {
          text_content: textContent
        },{
          timeout: 300000, // 增加超时时间到5分钟
          retry: 0 // 不重试
        })
        .then(response => {
          console.log('简历分析API返回成功:', response.status);
          console.log('API响应数据结构:', response.data);
          if(response.data && response.data.code === 0){
            // 修复：API返回的data字段直接包含JSON字符串，不需要.content
            localStorage.setItem('originalWorkflowContent', response.data.data);
            console.log('简历分析成功，已保存到localStorage:', response.data.data);
          }
          return response;
        })
        .catch(error => {
          console.error('简历分析API请求失败:', error.message);
          // 返回一个默认的响应对象，避免 resumeResponse 为 undefined
          return {
            data: {
              code: 500,
              message: '简历分析失败',
              data: { text: textContent }
            }
          };
        });

        const starPromise = workflowApi.post('/workflow/star', {
          text: textContent
        },{
          timeout: 300000, // 增加超时时间到5分钟
          retry: 0 // 不重试
        })
        .then(response => {
          console.log('STAR分析API返回成功:', response.status);
          if(response.data && response.data.code === 0){
            localStorage.setItem('starWorkflowData', JSON.stringify(response.data));
            console.log('STAR分析成功，已保存到localStorage');
          }
          return response;
        })
        .catch(error => {
          console.error('STAR分析API请求失败:', error.message);
          // 返回一个默认的响应对象，而不是抛出错误
          return {
            data: {
              code: 500,
              message: 'STAR分析失败',
              error: error.message
            }
          };
        });

        // 使用 Promise.allSettled 等待所有请求完成，即使某个失败也会继续
        console.log('等待所有API请求完成...');
        const results = await Promise.allSettled([resumePromise, starPromise]);

        const resumeResult = results[0];
        const starResult = results[1];

        console.log('简历分析结果状态:', resumeResult.status);
        console.log('STAR分析结果状态:', starResult.status);

        // 获取实际的响应数据
        const resumeResponse = resumeResult.status === 'fulfilled' ? resumeResult.value : resumeResult.reason;
        const starResponse = starResult.status === 'fulfilled' ? starResult.value : starResult.reason;

        // 返回合并的结果
        resolve({
          data: {
            code: 0,
            message: '简历和STAR分析完成',
            data: {
              resumeAnalysis: resumeResponse.data,
              starAnalysis: starResponse.data
            },
            // 添加执行状态信息
            executionStatus: {
              resumeStatus: resumeResult.status,
              starStatus: starResult.status
            }
          }
        });

      } catch (error) {
        console.error('简历和STAR分析失败:', error);
        resolve({
          data: {
            code: 500,
            message: '简历和STAR分析失败',
            error: error.message
          }
        });
      }
    });
  }
}

export default {
  uploadResumeFile,
  processResumeWorkflow,
  getResumeTemplates,
  analyzeResume,
  processResumeWithStar,
  generateResume
};