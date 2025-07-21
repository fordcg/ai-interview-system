/**
 * localStorage 管理工具
 * 统一管理应用中的localStorage数据，包括临时数据的清理
 */

// 定义临时数据的键名
export const TEMP_DATA_KEYS = {
  EXTRACTED_SKILLS: 'extractedSkills',
  RESUME_UPLOAD_DATA: 'resumeUploadData',
  STAR_WORKFLOW_DATA: 'starWorkflowData',
  JOB_ANALYSIS_RESULT: 'jobAnalysisResult',
  ORIGINAL_WORKFLOW_CONTENT: 'originalWorkflowContent',
  AI_GENERATED_RESUME_DATA: 'aiGeneratedResumeData',
  JOB_RECOMMEND_WORKFLOW_DATA: 'jobRecommendWorkflowData',
  JOB_RESUME_WORKFLOW_RESULT: 'jobResumeWorkflowResult',
  INTERVIEW_ANALYSES: 'interviewAnalyses',
  DEEPSEEK_INTERVIEW_QUESTIONS: 'deepseekInterviewQuestions',
  UPLOAD_RESULT: 'uploadResult'
}

// 定义用户相关数据的键名
export const USER_DATA_KEYS = {
  TOKEN: 'token',
  USER_ID: 'userId',
  USERNAME: 'username',
  AVATAR: 'avatar'
}

/**
 * 清理所有临时数据
 * 在用户退出登录、重新登录或开始新流程时调用
 */
export function clearTempData() {
  console.log('开始清理localStorage临时数据...')
  
  const clearedKeys = []
  
  Object.values(TEMP_DATA_KEYS).forEach(key => {
    if (localStorage.getItem(key)) {
      localStorage.removeItem(key)
      clearedKeys.push(key)
    }
  })
  
  if (clearedKeys.length > 0) {
    console.log('已清理以下临时数据:', clearedKeys)
  } else {
    console.log('没有需要清理的临时数据')
  }
  
  return clearedKeys
}

/**
 * 清理用户相关数据
 * 在用户退出登录时调用
 */
export function clearUserData() {
  console.log('开始清理localStorage用户数据...')
  
  const clearedKeys = []
  
  Object.values(USER_DATA_KEYS).forEach(key => {
    if (localStorage.getItem(key)) {
      localStorage.removeItem(key)
      clearedKeys.push(key)
    }
  })
  
  if (clearedKeys.length > 0) {
    console.log('已清理以下用户数据:', clearedKeys)
  } else {
    console.log('没有需要清理的用户数据')
  }
  
  return clearedKeys
}

/**
 * 清理所有数据（用户数据 + 临时数据）
 * 在完全重置应用状态时调用
 */
export function clearAllData() {
  console.log('开始清理所有localStorage数据...')
  
  const tempKeys = clearTempData()
  const userKeys = clearUserData()
  
  return {
    tempKeys,
    userKeys,
    total: tempKeys.length + userKeys.length
  }
}

/**
 * 清理特定的简历相关数据
 * 在开始新的简历上传流程时调用
 */
export function clearResumeData() {
  console.log('开始清理简历相关数据...')
  
  const resumeKeys = [
    TEMP_DATA_KEYS.EXTRACTED_SKILLS,
    TEMP_DATA_KEYS.RESUME_UPLOAD_DATA,
    TEMP_DATA_KEYS.STAR_WORKFLOW_DATA,
    TEMP_DATA_KEYS.ORIGINAL_WORKFLOW_CONTENT,
    TEMP_DATA_KEYS.AI_GENERATED_RESUME_DATA,
    TEMP_DATA_KEYS.UPLOAD_RESULT
  ]
  
  const clearedKeys = []
  
  resumeKeys.forEach(key => {
    if (localStorage.getItem(key)) {
      localStorage.removeItem(key)
      clearedKeys.push(key)
    }
  })
  
  if (clearedKeys.length > 0) {
    console.log('已清理以下简历数据:', clearedKeys)
  } else {
    console.log('没有需要清理的简历数据')
  }
  
  return clearedKeys
}

/**
 * 清理特定的职位分析相关数据
 * 在开始新的职位分析流程时调用
 */
export function clearJobAnalysisData() {
  console.log('开始清理职位分析相关数据...')
  
  const jobKeys = [
    TEMP_DATA_KEYS.JOB_ANALYSIS_RESULT,
    TEMP_DATA_KEYS.JOB_RECOMMEND_WORKFLOW_DATA,
    TEMP_DATA_KEYS.JOB_RESUME_WORKFLOW_RESULT
  ]
  
  const clearedKeys = []
  
  jobKeys.forEach(key => {
    if (localStorage.getItem(key)) {
      localStorage.removeItem(key)
      clearedKeys.push(key)
    }
  })
  
  if (clearedKeys.length > 0) {
    console.log('已清理以下职位分析数据:', clearedKeys)
  } else {
    console.log('没有需要清理的职位分析数据')
  }
  
  return clearedKeys
}

/**
 * 检查是否存在临时数据
 * 用于调试和状态检查
 */
export function checkTempDataExists() {
  const existingData = {}
  
  Object.entries(TEMP_DATA_KEYS).forEach(([name, key]) => {
    const data = localStorage.getItem(key)
    if (data) {
      existingData[name] = {
        key,
        size: data.length,
        preview: data.substring(0, 100) + (data.length > 100 ? '...' : '')
      }
    }
  })
  
  return existingData
}

/**
 * 安全地获取localStorage数据
 * 包含错误处理和类型转换
 */
export function safeGetItem(key, defaultValue = null) {
  try {
    const item = localStorage.getItem(key)
    if (item === null) return defaultValue
    
    // 尝试解析JSON
    try {
      return JSON.parse(item)
    } catch {
      // 如果不是JSON，返回原始字符串
      return item
    }
  } catch (error) {
    console.error(`获取localStorage数据失败 (${key}):`, error)
    return defaultValue
  }
}

/**
 * 安全地设置localStorage数据
 * 包含错误处理和自动JSON序列化
 */
export function safeSetItem(key, value) {
  try {
    const serializedValue = typeof value === 'string' ? value : JSON.stringify(value)
    localStorage.setItem(key, serializedValue)
    return true
  } catch (error) {
    console.error(`设置localStorage数据失败 (${key}):`, error)
    return false
  }
}

export default {
  TEMP_DATA_KEYS,
  USER_DATA_KEYS,
  clearTempData,
  clearUserData,
  clearAllData,
  clearResumeData,
  clearJobAnalysisData,
  checkTempDataExists,
  safeGetItem,
  safeSetItem
}
