<template>
  <div class="interview-home">
    <!-- 顶部导航栏 -->
    <header class="header">
      <div class="header-content">
        <div class="logo-container">
          <img src="@/assets/images/logo.png" alt="面试星途" class="logo" />
          <span class="logo-text">面试星途</span>
        </div>
        <nav class="nav-links">
          <a @click="navigateTo('/')" class="nav-link">首页</a>
          <a @click="navigateTo('/interview')" class="nav-link active">面试中心</a>
          <a @click="navigateTo('/user/center')" class="nav-link">个人中心</a>
          <a @click="navigateTo('/about')" class="nav-link">关于我们</a>
        </nav>

        <button class="mobile-menu-btn" @click="toggleMobileMenu">
          <v-icon>{{ showMobileMenu ? 'mdi-close' : 'mdi-menu' }}</v-icon>
        </button>
        <div class="auth-buttons">
          <div v-if="!isLoggedIn">
            <a @click="navigateTo('/login')" class="login-btn">登录</a>
            <a @click="navigateTo('/register')" class="register-btn">注册</a>
          </div>
          <div v-else class="user-info">
            <span class="welcome-text">欢迎，{{ username }}</span>
            <button @click="logout" class="logout-btn">退出</button>
          </div>
        </div>
      </div>
    </header>

    <!-- 主要内容区 -->
    <div class="main-content">
    <v-container>
      <v-row>
        <v-col cols="12">
          <h1 class="text-h4 mb-6 gradient-text">
            <v-icon large color="accent" class="mr-2">mdi-account-voice</v-icon>
            面试中心
          </h1>
        </v-col>
      </v-row>
      
      <v-row>
        <v-col cols="12" md="8">
          <v-card class="mb-4 custom-card" elevation="0">
            <v-img
              height="200"
              src="../../assets/images/id-card.png"
              gradient="to bottom, rgba(0,0,0,.3), rgba(0,0,0,.7)"
              class="white--text align-end"
            >
              <v-card-title class="text-h4 gradient-text">AI智能面试系统</v-card-title>
              <v-card-subtitle class="pb-0 info--text">提升您的面试技能，获得更好的职业机会</v-card-subtitle>
            </v-img>
            
            <v-card-text>
              <p class="text-body-1 light--text">
                欢迎使用AI智能面试系统！这是一个专为求职者设计的模拟面试平台，
                可以帮助您在真实面试前进行充分准备，提高面试成功率。
              </p>
              
              <v-divider class="my-4 divider-light"></v-divider>
              
              <v-row>
                <v-col cols="12" sm="4">
                  <v-card outlined class="text-center pa-4 feature-card">
                    <v-icon color="accent" size="48" class="mb-2 feature-icon">mdi-account-voice</v-icon>
                    <div class="text-subtitle-1 font-weight-bold light--text">模拟面试</div>
                    <div class="text-body-2 info--text">根据职位要求进行针对性面试</div>
                  </v-card>
                </v-col>
                
                <v-col cols="12" sm="4">
                  <v-card outlined class="text-center pa-4 feature-card">
                    <v-icon color="success" size="48" class="mb-2 feature-icon">mdi-chart-line</v-icon>
                    <div class="text-subtitle-1 font-weight-bold light--text">能力评估</div>
                    <div class="text-body-2 info--text">全方位评估您的面试表现</div>
                  </v-card>
                </v-col>
                
                <v-col cols="12" sm="4">
                  <v-card outlined class="text-center pa-4 feature-card">
                    <v-icon color="primary" size="48" class="mb-2 feature-icon">mdi-lightbulb-on</v-icon>
                    <div class="text-subtitle-1 font-weight-bold light--text">智能建议</div>
                    <div class="text-body-2 info--text">提供个性化改进建议</div>
                  </v-card>
                </v-col>
              </v-row>
              
              <v-divider class="my-4 divider-light"></v-divider>
              
              <div class="text-center">
                <v-btn
                  color="primary"
                  x-large
                  class="px-8 mt-2 custom-btn-primary"
                  to="/job/list"
                  elevation="0"
                >
                  <v-icon left>mdi-briefcase-search</v-icon>
                  选择职位开始面试
                </v-btn>
              </div>
            </v-card-text>
          </v-card>
          
          <v-card elevation="0" class="custom-card">
            <v-card-title class="card-title">
              <v-icon left color="warning">mdi-star</v-icon>
              热门职位面试
            </v-card-title>
            
            <v-card-text>
              <v-row>
                <v-col cols="12" sm="6" md="4" v-for="(job, index) in popularJobs" :key="index">
                  <v-card outlined hover class="popular-job-card">
                    <v-list-item three-line>
                      <v-list-item-avatar size="40" color="grey lighten-3" class="company-avatar">
                        <v-img :src="getCompanyLogo(job.company_logo)"></v-img>
                      </v-list-item-avatar>
                      
                      <v-list-item-content>
                        <v-list-item-title class="font-weight-medium light--text">{{ job.position_name }}</v-list-item-title>
                        <v-list-item-subtitle class="info--text">{{ job.company_name }}</v-list-item-subtitle>
                        <v-list-item-subtitle>
                          <v-chip x-small color="success" text-color="white" class="mr-1 stat-chip">
                            {{ job.interview_count || 0 }}人已面试
                          </v-chip>
                          <v-chip x-small color="primary" text-color="white" class="stat-chip">
                            {{ job.avg_score || 0 }}分
                          </v-chip>
                        </v-list-item-subtitle>
                      </v-list-item-content>
                    </v-list-item>
                    
                    <v-card-actions>
                      <v-btn
                        text
                        small
                        color="accent"
                        @click="startInterview(job.id)"
                        class="job-action-btn"
                      >
                        开始面试
                      </v-btn>
                      <v-btn
                        text
                        small
                        color="info"
                        :to="`/job/detail/${job.id}`"
                        class="job-action-btn"
                      >
                        查看详情
                      </v-btn>
                    </v-card-actions>
                  </v-card>
                </v-col>
              </v-row>
              
              <div v-if="!popularJobs.length" class="text-center py-5">
                <v-icon size="64" color="accent">mdi-clipboard-text-search</v-icon>
                <div class="text-h6 accent--text mt-3">暂无热门职位数据</div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
        
        <v-col cols="12" md="4">
          <v-card class="mb-4 custom-card" elevation="0">
            <v-card-title class="card-title">
              <v-icon left color="accent">mdi-history</v-icon>
              我的面试记录
            </v-card-title>
            
            <v-card-text v-if="loading">
              <v-skeleton-loader
                type="list-item-three-line"
                :loading="loading"
                class="mx-auto skeleton-loader"
              ></v-skeleton-loader>
            </v-card-text>
            
            <template v-else>
              <v-list v-if="interviewHistory.length" class="transparent-list">
                <v-list-item
                  v-for="(interview, index) in interviewHistory"
                  :key="index"
                  :to="`/interview/report/${interview.id}`"
                  class="history-item"
                >
                  <v-list-item-avatar>
                    <v-icon
                      :color="getScoreColor(interview.score)"
                      large
                    >
                      {{ getScoreIcon(interview.score) }}
                    </v-icon>
                  </v-list-item-avatar>
                  
                  <v-list-item-content>
                    <v-list-item-title class="light--text">{{ interview.position_name }}</v-list-item-title>
                    <v-list-item-subtitle class="info--text">
                      <v-icon small class="mr-1">mdi-office-building</v-icon>
                      {{ interview.company_name }}
                    </v-list-item-subtitle>
                    <v-list-item-subtitle class="info--text">
                      <v-icon small class="mr-1">mdi-calendar</v-icon>
                      {{ formatDate(interview.interview_time) }}
                    </v-list-item-subtitle>
                  </v-list-item-content>
                  
                  <v-list-item-action>
                    <v-chip
                      small
                      :color="getScoreColor(interview.score)"
                      text-color="white"
                      class="score-chip"
                    >
                      {{ interview.score }}分
                    </v-chip>
                  </v-list-item-action>
                </v-list-item>
              </v-list>
              
              <v-card-text v-else class="text-center py-4">
                <v-icon size="48" color="accent">mdi-clipboard-text</v-icon>
                <div class="text-subtitle-1 accent--text mt-2">暂无面试记录</div>
                <div class="text-body-2 info--text">
                  选择一个职位开始您的第一次面试吧
                </div>
              </v-card-text>
              
              <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn
                  text
                  color="accent"
                  to="/interview/ranking"
                  class="view-all-btn"
                >
                  <v-icon left small>mdi-trophy</v-icon>
                  面试排行榜
                </v-btn>
              </v-card-actions>
            </template>
          </v-card>
          
          <v-card elevation="0" class="custom-card">
            <v-card-title class="card-title">
              <v-icon left color="primary">mdi-lightbulb-on-outline</v-icon>
              面试技巧
            </v-card-title>
            
            <v-list class="transparent-list">
              <v-list-item v-for="(tip, index) in interviewTips" :key="index" class="tip-item">
                <v-list-item-icon>
                  <v-icon color="warning">mdi-check-circle</v-icon>
                </v-list-item-icon>
                
                <v-list-item-content>
                  <v-list-item-title class="white--text">{{ tip.title }}</v-list-item-title>
                  <v-list-item-subtitle class="info--text">{{ tip.description }}</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
            </v-list>
            
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn text color="accent" class="view-all-btn">
                查看更多技巧
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>
      
      <!-- 面试确认对话框 -->
      <v-dialog v-model="interviewDialog" max-width="500">
        <v-card class="custom-card">
          <v-card-title class="gradient-text">开始面试</v-card-title>
          <v-card-text>
            <p class="white--text">您确定要开始"{{ selectedJob ? selectedJob.position_name : '' }}"的模拟面试吗？</p>
            <p class="text-caption info--text">
              面试将包含多个问题，您需要在规定时间内完成回答。系统将对您的回答进行评分和分析。
            </p>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn text @click="interviewDialog = false" color="accent">取消</v-btn>
            <v-btn 
              color="primary" 
              :loading="interviewLoading"
              @click="confirmInterview"
              class="custom-btn-primary"
              elevation="0"
            >
              开始面试
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </v-container>
    </div>
  </div>
</template>

<script>
// import { getPopularJobs } from '@/api/job'
// import { getUserInterviewHistory, startInterview } from '@/api/interview'

export default {
  name: 'InterviewHome',
  data() {
    return {
      showMobileMenu: false,
      loading: true,
      popularJobs: [],
      interviewHistory: [],
      interviewDialog: false,
      interviewLoading: false,
      selectedJob: null,
      interviewTips: [
        { 
          title: '提前准备',
          description: '研究公司背景和职位要求，准备相关问题的回答' 
        },
        { 
          title: '着装得体',
          description: '选择专业、整洁的着装，给面试官留下良好的第一印象' 
        },
        { 
          title: '积极倾听',
          description: '认真聆听面试官的问题，确保理解后再回答' 
        },
        { 
          title: '展示成果',
          description: '用具体的数据和案例说明您的成就和能力' 
        },
        { 
          title: '提问环节',
          description: '准备有深度的问题，展示您对公司的兴趣和研究' 
        }
      ]
    }
  },
  created() {
    // 延迟加载数据，避免阻塞页面渲染
    this.$nextTick(() => {
      this.fetchPopularJobs()
      this.fetchInterviewHistory()
    })
  },
  computed: {
    isLoggedIn() {
      return !!this.$store.state.user.token
    },
    username() {
      return this.$store.state.user.username || '用户'
    }
  },
  mounted() {
    document.title = '面试中心 - 面试星途'
  },
  methods: {
    navigateTo(path) {
      console.log('Navigating to:', path)
      this.$router.push(path).catch(err => {
        console.error('Navigation error:', err)
      })
    },
    toggleMobileMenu() {
      this.showMobileMenu = !this.showMobileMenu
    },
    async logout() {
      try {
        await this.$store.dispatch('user/fedLogout')
        this.$store.dispatch('snackbar/showMessage', {
          content: '已成功退出登录',
          color: 'success'
        })
      } catch (error) {
        console.error('退出登录失败:', error)
        this.$store.dispatch('snackbar/showMessage', {
          content: '退出登录失败',
          color: 'error'
        })
      }
    },
    async fetchPopularJobs() {
      // 暂时使用模拟数据，确保页面能正常显示
      this.popularJobs = [
        {
          id: 1,
          position_name: '前端开发工程师',
          company_name: '科技公司',
          salary_range: '15-25K',
          company_logo: require('@/assets/images/default-avatar.png')
        },
        {
          id: 2,
          position_name: '后端开发工程师',
          company_name: '互联网公司',
          salary_range: '18-30K',
          company_logo: require('@/assets/images/default-avatar.png')
        },
        {
          id: 3,
          position_name: 'Java开发工程师',
          company_name: '大型企业',
          salary_range: '20-35K',
          company_logo: require('@/assets/images/default-avatar.png')
        },
        {
          id: 4,
          position_name: 'Python开发工程师',
          company_name: 'AI公司',
          salary_range: '22-40K',
          company_logo: require('@/assets/images/default-avatar.png')
        }
      ]
    },
    
    async fetchInterviewHistory() {
      this.loading = true
      // 暂时使用空数组，避免API调用错误
      this.interviewHistory = []
      this.loading = false
    },
    
    getCompanyLogo(src) {
      let trueSrc = ''
      if (src != null && src.startsWith("http")) {
        trueSrc = src
      } else if (src != null && src != '') {
        trueSrc = 'https://images.weserv.nl/?url=' + src
      } else {
        trueSrc = require("../../assets/images/nologo.png")
      }
      return trueSrc
    },
    
    formatDate(dateString) {
      if (!dateString) return '未知时间'
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    
    getScoreColor(score) {
      if (!score) return 'grey'
      if (score >= 90) return 'success'
      if (score >= 75) return 'primary'
      if (score >= 60) return 'warning'
      return 'error'
    },
    
    getScoreIcon(score) {
      if (!score) return 'mdi-help-circle'
      if (score >= 90) return 'mdi-emoticon-excited'
      if (score >= 75) return 'mdi-emoticon'
      if (score >= 60) return 'mdi-emoticon-neutral'
      return 'mdi-emoticon-sad'
    },
    
    startInterview(jobId) {
      this.interviewLoading = false
      this.selectedJob = this.popularJobs.find(job => job.id === jobId) || null
      this.interviewDialog = true
    },
    
    async confirmInterview() {
      if (!this.selectedJob) return

      this.interviewLoading = true
      try {
        // 直接跳转到沉浸式面试页面，避免API调用
        this.$router.push({
          name: 'ImmersiveInterview',
          params: { id: 'demo' },
          query: {
            jobName: this.selectedJob.position_name,
            mode: 'demo',
            testMode: 'true'
          }
        })
      } finally {
        this.interviewLoading = false
        this.interviewDialog = false
      }
    }
  }
}
</script>

<style scoped>
.interview-home {
  padding: 20px 0;
}

.custom-card {
  background: rgba(255, 255, 255, 0.08) !important;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 15px !important;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  overflow: hidden;
}

.custom-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2) !important;
}

.divider-light {
  border-color: rgba(255, 255, 255, 0.1) !important;
}

.card-title {
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding-bottom: 16px;
}

.feature-card {
  background: rgba(255, 255, 255, 0.05) !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  border-radius: 12px !important;
  transition: all 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-5px);
  background: rgba(255, 255, 255, 0.1) !important;
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2) !important;
}

.feature-icon {
  filter: drop-shadow(0 0 8px rgba(255, 255, 255, 0.5));
}

.popular-job-card {
  background: rgba(255, 255, 255, 0.05) !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  border-radius: 12px !important;
  transition: all 0.3s ease;
}

.popular-job-card:hover {
  transform: translateY(-5px);
  background: rgba(255, 255, 255, 0.1) !important;
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2) !important;
}

.company-avatar {
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.stat-chip {
  font-size: 0.7rem;
}

.job-action-btn {
  transition: all 0.3s ease;
}

.job-action-btn:hover {
  transform: translateY(-3px);
}

.transparent-list {
  background: transparent !important;
}

.history-item {
  transition: all 0.3s ease;
  border-radius: 8px;
  margin: 4px 0;
}

.history-item:hover {
  background: rgba(255, 255, 255, 0.1) !important;
}

.score-chip {
  font-size: 0.75rem;
}

.view-all-btn {
  transition: all 0.3s ease;
}

.view-all-btn:hover {
  transform: translateX(5px);
}

.tip-item {
  transition: all 0.3s ease;
  border-radius: 8px;
  margin: 4px 0;
}

.tip-item:hover {
  background: rgba(255, 255, 255, 0.1) !important;
}

.skeleton-loader >>> .v-skeleton-loader__bone {
  background: rgba(255, 255, 255, 0.05) !important;
}

/* 顶部导航栏样式 */
.header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background-color: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  padding: 0.5rem 0;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo-container {
  display: flex;
  align-items: center;
}

.logo {
  height: 36px;
  margin-right: 10px;
}

.logo-text {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1B2B3D;
}

.nav-links {
  display: flex;
  gap: 2rem;
}

.nav-link {
  color: #1B2B3D;
  text-decoration: none;
  font-size: 1rem;
  font-weight: 500;
  transition: color 0.3s;
  cursor: pointer;
}

.nav-link:hover, .nav-link.active {
  color: #1867FF;
}

.mobile-menu-btn {
  display: none;
  background: none;
  border: none;
  color: #1B2B3D;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.mobile-menu-btn:hover {
  background-color: rgba(24, 103, 255, 0.1);
}

.auth-buttons {
  display: flex;
  gap: 1rem;
}

.login-btn {
  color: #1867FF;
  text-decoration: none;
  font-weight: 500;
  padding: 0.5rem 1.2rem;
  border-radius: 6px;
  transition: all 0.3s;
  cursor: pointer;
}

.login-btn:hover {
  background-color: rgba(24, 103, 255, 0.1);
}

.register-btn {
  background-color: #1867FF;
  color: white;
  text-decoration: none;
  font-weight: 500;
  padding: 0.5rem 1.2rem;
  border-radius: 6px;
  transition: all 0.3s;
  cursor: pointer;
}

.register-btn:hover {
  background-color: #0052D9;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.welcome-text {
  color: #1B2B3D;
  font-weight: 500;
  font-size: 1rem;
}

.logout-btn {
  background-color: #f5f5f5;
  color: #666;
  border: 1px solid #ddd;
  padding: 0.5rem 1.2rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s;
}

.logout-btn:hover {
  background-color: #e0e0e0;
  color: #333;
}

/* 主要内容区 */
.main-content {
  padding-top: 60px;
}

/* 设置白色背景 */
.interview-home {
  background-color: #ffffff !important;
  min-height: 100vh;
}

.interview-home .v-container {
  background: transparent !important;
}

.interview-home .v-main {
  background-color: #ffffff !important;
}

.interview-home .v-application {
  background-color: #ffffff !important;
}
</style>