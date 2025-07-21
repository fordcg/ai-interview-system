/**
 * 图片工具函数
 */

// 默认头像
const defaultAvatar = require('@/assets/img/default-avatar.png')

// 默认公司logo
const defaultCompanyLogo = require('@/assets/img/nologo.png')

// 默认公司LOGO - 使用相对路径引用
const DEFAULT_LOGO = require('@/assets/img/nologo.png');

/**
 * 获取图片URL，如果图片不存在则返回默认图片
 * @param {string} url - 图片URL
 * @param {string} defaultImg - 默认图片URL
 * @returns {string} - 处理后的图片URL
 */
export function getImageUrl(url, defaultImg = defaultAvatar) {
  if (!url) return defaultImg
  
  // 如果是完整URL，直接返回
  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url
  }
  
  // 如果是相对路径，添加基础路径
  if (url.startsWith('/')) {
    return process.env.VUE_APP_BASE_API + url
  }
  
  return url
}

/**
 * 获取头像URL
 * @param {string} avatar - 头像URL
 * @returns {string} - 处理后的头像URL
 */
export function getAvatarUrl(avatar) {
  return getImageUrl(avatar, defaultAvatar)
}

/**
 * 获取公司logo URL
 * @param {string} logo - 公司logo URL
 * @returns {string} - 处理后的公司logo URL
 */
export function getCompanyLogo(logo) {
  if (!logo || logo === 'null' || logo === 'undefined') {
    return DEFAULT_LOGO;
  }
  
  // 如果是完整URL，直接返回
  if (logo.startsWith('http://') || logo.startsWith('https://')) {
    return logo;
  }
  
  // 如果是相对路径，拼接基础URL
  const baseUrl = process.env.VUE_APP_BASE_API || 'http://localhost:5000';
  return `${baseUrl}${logo.startsWith('/') ? '' : '/'}${logo}`;
}

/**
 * 通过图片代理服务获取图片
 * 用于解决跨域问题或者优化图片加载
 * @param {string} url - 原始图片URL
 * @param {Object} options - 配置选项
 * @returns {string} - 处理后的图片URL
 */
export function getProxyImage(url, options = {}) {
  if (!url) return defaultCompanyLogo
  
  // 如果已经是本地URL，直接返回
  if (url.startsWith('data:') || url.startsWith('blob:')) {
    return url
  }
  
  // 默认配置
  const defaultOptions = {
    width: null,
    height: null,
    quality: 80,
    format: null
  }
  
  const opts = { ...defaultOptions, ...options }
  
  // 使用图片代理服务
  let proxyUrl = 'https://images.weserv.nl/?url=' + encodeURIComponent(url)
  
  // 添加配置参数
  if (opts.width) proxyUrl += '&w=' + opts.width
  if (opts.height) proxyUrl += '&h=' + opts.height
  if (opts.quality) proxyUrl += '&q=' + opts.quality
  if (opts.format) proxyUrl += '&output=' + opts.format
  
  return proxyUrl
}

/**
 * 将图片转换为Base64
 * @param {string} url - 图片URL
 * @returns {Promise<string>} - 转换后的Base64字符串
 */
export function imageToBase64(url) {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.crossOrigin = 'Anonymous'
    img.onload = () => {
      try {
        const canvas = document.createElement('canvas')
        canvas.width = img.width
        canvas.height = img.height
        const ctx = canvas.getContext('2d')
        ctx.drawImage(img, 0, 0)
        const dataURL = canvas.toDataURL('image/png')
        resolve(dataURL)
      } catch (error) {
        reject(error)
      }
    }
    img.onerror = (error) => {
      reject(error)
    }
    img.src = url
  })
}

/**
 * 获取用户头像
 * @param {string} avatar - 用户头像路径
 * @returns {string} - 头像URL
 */
export function getUserAvatar(avatar) {
  if (!avatar || avatar === 'null' || avatar === 'undefined') {
    // 使用正确的default-avatar.png图片
    return require('@/assets/img/default-avatar.png');
  }
  
  // 处理逻辑同公司LOGO
  if (avatar.startsWith('http://') || avatar.startsWith('https://')) {
    return avatar;
  }
  
  const baseUrl = process.env.VUE_APP_BASE_API || 'http://localhost:5000';
  return `${baseUrl}${avatar.startsWith('/') ? '' : '/'}${avatar}`;
}

export default {
  defaultAvatar,
  defaultCompanyLogo,
  getImageUrl,
  getAvatarUrl,
  getCompanyLogo,
  getProxyImage,
  imageToBase64
} 