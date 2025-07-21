import Vue from 'vue'
import * as resumeApi from '@/api/resume'
import * as jobApi from '@/api/job'
import * as userApi from '@/api/user'

// 创建API对象
const api = {
  resume: resumeApi,
  job: jobApi,
  user: userApi
}

// 注册API插件
export default {
  install(Vue) {
    Vue.prototype.$api = api
  }
} 