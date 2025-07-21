/**
 * 人脸检测相关API
 */
import request from '@/utils/request'

/**
 * 分析人脸表情
 * @param {Object} data - 请求数据
 * @param {String} data.image - Base64编码的图像
 * @returns {Promise} - 返回Promise对象
 */
export function analyzeFace(data) {
  return request({
    url: '/facial-expression/analyze',
    method: 'post',
    data
  })
}

/**
 * 使用增强的表情分析器分析人脸表情
 * @param {Object} data - 请求数据
 * @param {String} data.image - Base64编码的图像
 * @returns {Promise} - 返回Promise对象
 */
export function analyzeExpression(data) {
  return request({
    url: '/facial-expression/analyze',
    method: 'post',
    data
  })
}

/**
 * 上传图像并分析人脸表情
 * @param {FormData} formData - 包含图像文件的表单数据
 * @returns {Promise} - 返回Promise对象
 */
export function uploadAndAnalyzeExpression(formData) {
  return request({
    url: '/facial-expression/upload',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 获取情绪分布统计
 * @returns {Promise} - 返回Promise对象
 */
export function getEmotionDistribution() {
  return request({
    url: '/facial-expression/emotion-distribution',
    method: 'get'
  })
}

/**
 * 重置情绪分布统计
 * @returns {Promise} - 返回Promise对象
 */
export function resetEmotionStats() {
  return request({
    url: '/facial-expression/reset-stats',
    method: 'post'
  })
}

/**
 * 获取当前表情状态
 * @returns {Promise} - 返回Promise对象
 */
export function getCurrentEmotion() {
  return request({
    url: '/facial-expression/current-emotion',
    method: 'get'
  })
} 