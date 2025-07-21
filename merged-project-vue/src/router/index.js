import Vue from 'vue'
import VueRouter from 'vue-router'
import { clearTempData } from '@/utils/localStorage'
import Layout from '../layouts/AppLayout.vue'

// 解决 Element UI 导航栏中的 vue-router 在 3.0 版本以上重复点菜单报错问题
const originalPush = VueRouter.prototype.push
VueRouter.prototype.push = function push(location) {
  return originalPush.call(this, location).catch(err => err)
}

Vue.use(VueRouter)

// 路由懒加载
const Login = () => import('@/views/user/Login.vue')
const Register = () => import('@/views/user/Register.vue')
const Home = () => import('@/views/home/Home.vue')
const Features = () => import('@/views/home/Features.vue')
const UserCenter = () => import('@/views/user/UserCenter.vue')
const Profile = () => import('@/views/user/Profile.vue')
const AccountSettings = () => import('@/views/user/AccountSettings.vue')
const About = () => import('@/views/home/About.vue')

const ResumePreparation = () => import('@/views/dashboard/ResumePreparation.vue')
const JobList = () => import('@/views/job/JobList.vue')
const JobDetail = () => import('@/views/job/JobDetail.vue')
const JobAnalysis = () => import('@/views/job/JobAnalysis.vue')

const InterviewHome = () => import('@/views/interview/InterviewHome.vue')
const ImmersiveInterviewPage = () => import('@/views/interview/ImmersiveInterviewPage.vue')


const InterviewReport = () => import('@/views/interview/InterviewReport.vue')
const InterviewRanking = () => import('@/views/interview/InterviewRanking.vue')
const InterviewAnalysis = () => import('@/views/interview/InterviewAnalysis.vue')

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: {
      title: '首页 - 面试星途',
      requiresAuth: false
    }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: {
      title: '登录 - 面试星途',
      requiresAuth: false
    }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: {
      title: '注册 - 面试星途',
      requiresAuth: false
    }
  },
  // 用户中心路由 (不使用Layout)
  {
    path: '/user/center',
    name: 'UserCenter',
    component: UserCenter,
    meta: {
      title: '个人中心 - 面试星途',
      requiresAuth: true
    }
  },
  // 其他用户相关路由 (使用Layout)
  {
    path: '/user',
    component: Layout,
    children: [
      {
        path: 'profile',
        name: 'Profile',
        component: Profile
      },
      {
        path: 'settings',
        name: 'AccountSettings',
        component: AccountSettings
      }
    ]
  },
  // 职位相关路由 (来自a2)
  {
    path: '/job',
    component: Layout,
    children: [
      {
        path: 'list',
        name: 'JobList',
        component: JobList
      },
      {
        path: 'detail/:id',
        name: 'JobDetail',
        component: JobDetail
      },
      {
        path: 'analysis',
        name: 'JobAnalysis',
        component: JobAnalysis
      }
    ]
  },
  // 面试相关路由 (来自a1)
  {
    path: '/interview',
    name: 'Interview',
    component: InterviewHome,
    meta: {
      title: '面试中心 - 面试星途',
      requiresAuth: true
    }
  },
  {
    path: '/interview',
    component: Layout,
    children: [
      {
        path: 'report/:id',
        name: 'InterviewReport',
        component: InterviewReport
      },
      {
        path: 'ranking',
        name: 'InterviewRanking',
        component: InterviewRanking
      },
      {
        path: 'analysis',
        name: 'InterviewAnalysis',
        component: InterviewAnalysis
      },
      {
        path: 'sparkos',
        redirect: '/interview/immersive'
      },
      {
        path: 'process/:id?',
        redirect: to => `/interview/immersive/${to.params.id || ''}`
      },
      {
        path: 'immersive/:id?',
        name: 'ImmersiveInterview',
        component: ImmersiveInterviewPage,
        meta: {
          title: '沉浸式面试 - 面试星途',
          requiresAuth: true,
          fullscreen: true
        }
      },


    ]
  },
  // 仪表盘路由
  {
    path: '/dashboard',
    component: Layout,
    children: [
      {
        path: '',
        name: 'ResumePreparation',
        component: ResumePreparation
      }
    ]
  },
  {
    path: '/features',
    name: 'Features',
    component: Features,
    meta: {
      title: '功能介绍 - 面试星途',
      requiresAuth: false
    }
  },
  {
    path: '/about',
    name: 'About',
    component: About,
    meta: {
      title: '关于我们 - 面试星途',
      requiresAuth: false
    }
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

// 全局前置守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = to.meta.title || '面试星途'

  // 在特定路由跳转时清理临时数据
  if (to.path === '/' || to.path === '/dashboard') {
    // 导航到主页或仪表板时清理所有临时数据
    clearTempData()
    console.log('导航到主页，已清理所有临时数据')
  } else if (to.path === '/interview/analysis') {
    // 进入面试分析页面时，不清理数据，因为需要使用之前的数据
    console.log('进入面试分析页面，保留现有数据')
  } else if (to.path.startsWith('/resume/') && from.path !== to.path) {
    // 进入简历相关页面时，如果是从其他页面跳转过来的，清理旧的简历数据
    // 但如果是在简历页面内部跳转，则不清理
    if (!from.path.startsWith('/resume/')) {
      console.log('从非简历页面进入简历流程，清理旧的临时数据')
      clearTempData()
    }
  }
  
  const token = localStorage.getItem('token')
  
  if (token) {
    // 如果用户已登录
    if (to.path === '/login' || to.path === '/register') {
      // 如果已登录用户试图访问登录或注册页面，则重定向到首页
      next({ path: '/' })
    } else {
      // 否则，允许访问任何其他页面
      next()
    }
  } else {
    // 如果用户未登录
    if (to.matched.some(record => record.meta.requiresAuth)) {
      // 如果目标页面需要认证，则重定向到登录页
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
    } else {
      // 否则，允许访问公共页面
      next()
    }
  }
})

export default router