import axios from 'axios'
import store from '@/store'
import { Message } from 'element-ui'

// 创建axios实例
const service = axios.create({
  // 使用相对路径，依赖Vue代理配置
  baseURL: '/api',
  timeout: 30000, // 请求超时时间增加到30秒
  withCredentials: false // 关闭跨域请求时发送cookies，避免CORS问题
})

// 请求拦截器
service.interceptors.request.use(
  config => {
    // 在请求发送前做一些处理
    if (store.getters.token) {
      // 让每个请求携带token
      config.headers['Authorization'] = 'Bearer ' + store.state.user.token
    }
    return config
  },
  error => {
    // 请求错误处理
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  response => {
    const res = response.data

    // 检查响应格式
    // 1. 如果包含success字段，直接根据success判断
    if (res.hasOwnProperty('success')) {
      if (res.success === true) {
        return res
      } else {
        Message({
          message: res.message || '请求失败',
          type: 'error',
          duration: 5 * 1000
        })
        return Promise.reject(new Error(res.message || '请求失败'))
      }
    }
    
    // 2. 如果包含code字段，根据code判断
    // 成功状态码可能是0或200
    if (res.code !== 0 && res.code !== 200) {
      Message({
        message: res.msg || res.message || '请求错误',
        type: 'error',
        duration: 5 * 1000
      })

      // 401: 未登录或token过期
      if (res.code === 401) {
        // 重新登录
        store.dispatch('user/fedLogout').then(() => {
          location.reload()
        })
      }
      return Promise.reject(new Error(res.msg || res.message || '请求错误'))
    } else {
      return res
    }
  },
  error => {
    console.error('响应错误:', error)
    
    // 获取错误信息
    let message = error.message
    if (error.response) {
      switch (error.response.status) {
        case 400:
          message = '请求错误'
          break
        case 401:
          message = '未授权，请重新登录'
          // 重新登录
          store.dispatch('user/fedLogout').then(() => {
            location.reload()
          })
          break
        case 403:
          message = '拒绝访问'
          break
        case 404:
          message = '请求地址出错'
          break
        case 408:
          message = '请求超时'
          break
        case 500:
          message = '服务器内部错误'
          break
        case 501:
          message = '服务未实现'
          break
        case 502:
          message = '网关错误'
          break
        case 503:
          message = '服务不可用'
          break
        case 504:
          message = '网关超时'
          break
        case 505:
          message = 'HTTP版本不受支持'
          break
        default:
          message = `连接错误${error.response.status}`
      }
    }
    
    Message({
      message: message,
      type: 'error',
      duration: 5 * 1000
    })
    
    return Promise.reject(error)
  }
)

export default service 