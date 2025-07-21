import axios from 'axios'

// 创建axios实例
const service = axios.create({
  baseURL: process.env.VUE_APP_BASE_API || 'http://localhost:5000', // API基础URL
  timeout: 60000 // 请求超时时间，增加到60秒
})

export default service 