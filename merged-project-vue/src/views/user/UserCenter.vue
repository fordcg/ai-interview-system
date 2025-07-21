<template>
  <div class="user-center">
    <!-- 顶部导航栏 -->
    <header class="header">
      <div class="header-content">
        <div class="logo-container">
          <img src="@/assets/images/logo.png" alt="面试星途" class="logo" />
          <span class="logo-text">面试星途</span>
        </div>
        <nav class="nav-links">
          <a @click="navigateTo('/')" class="nav-link">首页</a>
          <a @click="navigateTo('/interview')" class="nav-link">面试中心</a>
          <a @click="navigateTo('/user/center')" class="nav-link active">个人中心</a>
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
            <v-icon large color="accent" class="mr-2">mdi-account-circle</v-icon>
            个人中心
          </h1>
        </v-col>
      </v-row>
      
      <v-row>
        <!-- 用户信息卡片 -->
        <v-col cols="12" md="4">
          <v-card class="mb-4 custom-card" elevation="0">
            <v-card-text class="text-center">
              <v-avatar size="120" class="mb-4 profile-avatar">
                <v-img :src="userAvatar"></v-img>
              </v-avatar>
              
              <h2 class="text-h5 font-weight-bold gradient-text">{{ user.username || '未登录' }}</h2>
              <p class="text-subtitle-1 accent--text">{{ user.email || '暂无邮箱' }}</p>
              
              <v-chip color="primary" small class="mr-1 user-chip">
                <v-icon left small>mdi-star</v-icon>
                {{ user.level || '初级用户' }}
              </v-chip>
              
              <v-chip color="success" small class="user-chip">
                <v-icon left small>mdi-check-circle</v-icon>
                {{ user.status || '正常' }}
              </v-chip>
              
              <v-divider class="my-4 divider-light"></v-divider>
              
              <v-btn block outlined color="accent" class="mb-2 custom-btn" to="/user/profile">
                <v-icon left>mdi-account-edit</v-icon>
                编辑个人资料
              </v-btn>
              
              <v-btn block outlined color="primary" class="custom-btn" to="/user/account-settings">
                <v-icon left>mdi-cog</v-icon>
                账户设置
              </v-btn>
            </v-card-text>
          </v-card>
          
          <!-- 用户统计信息 -->
          <v-card elevation="0" class="custom-card">
            <v-list class="transparent-list">
              <v-list-item class="stat-item">
                <v-list-item-icon>
                  <v-icon color="accent">mdi-calendar-check</v-icon>
                </v-list-item-icon>
                <v-list-item-content>
                  <v-list-item-title class="white--text">注册时间</v-list-item-title>
                  <v-list-item-subtitle class="info--text">{{ formatDate(user.register_time) }}</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
              
              <v-divider class="divider-light"></v-divider>
              
              <v-list-item class="stat-item">
                <v-list-item-icon>
                  <v-icon color="success">mdi-account-voice</v-icon>
                </v-list-item-icon>
                <v-list-item-content>
                  <v-list-item-title class="white--text">面试次数</v-list-item-title>
                  <v-list-item-subtitle class="info--text">{{ stats.interview_count || 0 }}次</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
              
              <v-divider class="divider-light"></v-divider>
              
              <v-list-item class="stat-item">
                <v-list-item-icon>
                  <v-icon color="warning">mdi-star</v-icon>
                </v-list-item-icon>
                <v-list-item-content>
                  <v-list-item-title class="white--text">平均分数</v-list-item-title>
                  <v-list-item-subtitle class="info--text">{{ stats.avg_score || 0 }}分</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
              
              <v-divider class="divider-light"></v-divider>
              
              <v-list-item class="stat-item">
                <v-list-item-icon>
                  <v-icon color="error">mdi-heart</v-icon>
                </v-list-item-icon>
                <v-list-item-content>
                  <v-list-item-title class="white--text">收藏职位</v-list-item-title>
                  <v-list-item-subtitle class="info--text">{{ stats.favorite_count || 0 }}个</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
            </v-list>
          </v-card>
        </v-col>
        
        <!-- 右侧内容区 -->
        <v-col cols="12" md="8">
          <!-- 最近面试 -->
          <v-card class="mb-4 custom-card" elevation="0">
            <v-card-title class="card-title">
              <v-icon left color="accent">mdi-history</v-icon>
              最近面试
            </v-card-title>
            
            <v-card-text class="pa-0">
              <v-data-table
                :headers="interviewHeaders"
                :items="recentInterviews"
                :items-per-page="5"
                hide-default-footer
                class="elevation-0 transparent-table"
                dark
              >
                <template v-slot:item.score="{ item }">
                  <v-chip
                    small
                    :color="getScoreColor(item.score)"
                    text-color="white"
                    class="score-chip"
                  >
                    {{ item.score }}分
                  </v-chip>
                </template>
                
                <template v-slot:item.interview_time="{ item }">
                  {{ formatDate(item.interview_time) }}
                </template>
                
                <template v-slot:item.actions="{ item }">
                  <v-btn
                    x-small
                    text
                    color="accent"
                    :to="`/interview/report/${item.id}`"
                    class="action-btn"
                  >
                    查看报告
                  </v-btn>
                </template>
                
                <template v-slot:no-data>
                  <div class="text-center py-3">
                    <v-icon color="accent" size="48">mdi-clipboard-text</v-icon>
                    <div class="text-subtitle-1 accent--text mt-2">暂无面试记录</div>
                  </div>
                </template>
              </v-data-table>
            </v-card-text>
            
            <v-card-actions class="justify-end">
              <v-btn text color="accent" to="/interview/history" class="view-all-btn">
                查看全部
                <v-icon right small>mdi-chevron-right</v-icon>
              </v-btn>
            </v-card-actions>
          </v-card>
          
          <!-- 收藏职位 -->
          <v-card class="mb-4 custom-card" elevation="0">
            <v-card-title class="card-title">
              <v-icon left color="error">mdi-heart</v-icon>
              收藏职位
            </v-card-title>
            
            <v-card-text v-if="favoriteJobs.length" class="pa-0">
              <v-list class="transparent-list">
                <v-list-item
                  v-for="job in favoriteJobs"
                  :key="job.id"
                  :to="`/job/detail/${job.id}`"
                  class="job-item"
                >
                  <v-list-item-avatar class="job-avatar">
                    <v-img :src="getCompanyLogo(job.company_logo)"></v-img>
                  </v-list-item-avatar>
                  
                  <v-list-item-content>
                    <v-list-item-title class="white--text">{{ job.position_name }}</v-list-item-title>
                    <v-list-item-subtitle class="info--text">
                      {{ job.company_name }} · {{ job.city }} · {{ job.salary0 }}-{{ job.salary1 }}元
                    </v-list-item-subtitle>
                  </v-list-item-content>
                  
                  <v-list-item-action>
                    <v-btn icon small @click.stop="removeFromFavorites(job.id)" class="favorite-btn">
                      <v-icon color="error">mdi-heart</v-icon>
                    </v-btn>
                  </v-list-item-action>
                </v-list-item>
              </v-list>
            </v-card-text>
            
            <v-card-text v-else>
              <div class="text-center py-3">
                <v-icon color="accent" size="48">mdi-heart-outline</v-icon>
                <div class="text-subtitle-1 accent--text mt-2">暂无收藏职位</div>
                <div class="text-body-2 info--text">
                  浏览职位列表，点击心形图标收藏感兴趣的职位
                </div>
              </div>
            </v-card-text>
            
            <v-card-actions class="justify-end">
              <v-btn text color="accent" to="/job/favorites" class="view-all-btn">
                查看全部
                <v-icon right small>mdi-chevron-right</v-icon>
              </v-btn>
            </v-card-actions>
          </v-card>
          
          <!-- 能力分析 -->
          <v-card elevation="0" class="custom-card">
            <v-card-title class="card-title">
              <v-icon left color="primary">mdi-chart-arc</v-icon>
              能力分析
            </v-card-title>
            
            <v-card-text>
              <v-row>
                <v-col cols="12" md="6">
                  <div class="text-center mb-4">
                    <div class="subtitle-1 font-weight-bold mb-4 white--text">能力雷达图</div>
                    <v-sheet height="250" class="d-flex justify-center radar-chart-container">
                      <!-- 这里可以使用图表库如Chart.js或Echarts绘制雷达图 -->
                      <div class="radar-chart-placeholder d-flex align-center justify-center">
                        <div class="text-center">
                          <v-icon size="64" color="accent">mdi-chart-areaspline</v-icon>
                          <div class="caption accent--text mt-2">能力雷达图</div>
                        </div>
                      </div>
                    </v-sheet>
                  </div>
                </v-col>
                
                <v-col cols="12" md="6">
                  <div class="subtitle-1 font-weight-bold mb-4 white--text">能力详情</div>
                  <v-list class="transparent-list">
                    <v-list-item v-for="(ability, index) in abilities" :key="index" class="ability-item">
                      <v-list-item-icon>
                        <v-icon :color="getScoreColor(ability.score)">{{ ability.icon }}</v-icon>
                      </v-list-item-icon>
                      
                      <v-list-item-content>
                        <v-list-item-title class="white--text">{{ ability.name }}</v-list-item-title>
                        <v-list-item-subtitle>
                          <v-progress-linear
                            :value="ability.score"
                            height="6"
                            rounded
                            :color="getScoreColor(ability.score)"
                            class="mt-1 ability-progress"
                          ></v-progress-linear>
                        </v-list-item-subtitle>
                      </v-list-item-content>
                      
                      <v-list-item-action>
                        <div class="font-weight-medium white--text">{{ ability.score }}</div>
                      </v-list-item-action>
                    </v-list-item>
                  </v-list>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
    </div>
  </div>
</template>

<script>
// import { getUserProfile, getUserStats } from '@/api/user'
// import { getUserInterviewHistory } from '@/api/interview'
// import { getFavoriteJobs } from '@/api/job'

export default {
  name: 'UserCenter',
  data() {
    return {
      showMobileMenu: false,
      user: {},
      stats: {},
      recentInterviews: [],
      favoriteJobs: [],
      abilities: [
        { name: '专业技能', score: 85, icon: 'mdi-code-tags' },
        { name: '沟通表达', score: 78, icon: 'mdi-account-voice' },
        { name: '逻辑思维', score: 82, icon: 'mdi-brain' },
        { name: '团队协作', score: 80, icon: 'mdi-account-group' },
        { name: '学习能力', score: 88, icon: 'mdi-book-open-page-variant' },
        { name: '抗压能力', score: 75, icon: 'mdi-weight-lifter' }
      ],
      interviewHeaders: [
        { text: '职位名称', value: 'position_name', class: 'white--text' },
        { text: '公司', value: 'company_name', class: 'white--text' },
        { text: '面试时间', value: 'interview_time', class: 'white--text' },
        { text: '得分', value: 'score', align: 'center', class: 'white--text' },
        { text: '操作', value: 'actions', align: 'center', sortable: false, class: 'white--text' }
      ]
    }
  },
  computed: {
    userAvatar() {
      return this.user.avatar || require('../../assets/images/default-avatar.png')
    }
  },
  created() {
    // 延迟加载数据，避免阻塞页面渲染
    this.$nextTick(() => {
      this.fetchUserProfile()
      this.fetchUserStats()
      this.fetchRecentInterviews()
      this.fetchFavoriteJobs()
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
    document.title = '个人中心 - 面试星途'
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
    async fetchUserProfile() {
      // 使用Vuex中的用户信息或默认数据
      this.user = {
        username: this.$store.state.user.username || 'admin',
        email: 'admin@example.com',
        level: '高级用户',
        status: '正常',
        avatar: this.$store.state.user.avatar || require('../../assets/images/default-avatar.png')
      }
    },
    
    async fetchUserStats() {
      // 使用模拟统计数据
      this.stats = {
        totalInterviews: 15,
        averageScore: 85,
        bestScore: 95,
        improvementRate: 12
      }
    },
    
    async fetchRecentInterviews() {
      // 使用模拟面试记录
      this.recentInterviews = []
    },
    
    async fetchFavoriteJobs() {
      // 使用模拟收藏职位数据
      this.favoriteJobs = []
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
    
    async removeFromFavorites(jobId) {
      // 这里可以添加从收藏夹移除的API调用
      this.favoriteJobs = this.favoriteJobs.filter(job => job.id !== jobId)
      
      this.$store.dispatch('snackbar/showMessage', {
        message: '已从收藏夹移除',
        color: 'info'
      })
      
      // 更新统计信息
      if (this.stats.favorite_count > 0) {
        this.stats.favorite_count--
      }
    }
  }
}
</script>

<style scoped>
.user-center {
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

.profile-avatar {
  border: 3px solid rgba(76, 201, 240, 0.5);
  box-shadow: 0 0 15px rgba(76, 201, 240, 0.5);
}

.user-chip {
  margin-top: 8px;
  font-size: 0.75rem;
}

.divider-light {
  border-color: rgba(255, 255, 255, 0.1) !important;
}

.transparent-list {
  background: transparent !important;
}

.stat-item {
  transition: all 0.3s ease;
  border-radius: 8px;
  margin: 4px 0;
}

.stat-item:hover {
  background: rgba(255, 255, 255, 0.1) !important;
}

.card-title {
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding-bottom: 16px;
}

.transparent-table {
  background: transparent !important;
}

.transparent-table >>> .v-data-table__wrapper {
  background: transparent !important;
}

.transparent-table >>> tbody tr {
  background: transparent !important;
  transition: all 0.3s ease;
}

.transparent-table >>> tbody tr:hover {
  background: rgba(255, 255, 255, 0.1) !important;
}

.transparent-table >>> th {
  color: #a0d2eb !important;
  font-weight: 500 !important;
}

.score-chip {
  font-size: 0.75rem;
}

.action-btn {
  transition: all 0.3s ease;
}

.action-btn:hover {
  transform: translateY(-3px);
}

.view-all-btn {
  transition: all 0.3s ease;
}

.view-all-btn:hover {
  transform: translateX(5px);
}

.job-item {
  transition: all 0.3s ease;
  border-radius: 8px;
  margin: 4px 0;
}

.job-item:hover {
  background: rgba(255, 255, 255, 0.1) !important;
}

.job-avatar {
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.favorite-btn {
  transition: all 0.3s ease;
}

.favorite-btn:hover {
  transform: scale(1.2);
}

.radar-chart-container {
  background: transparent !important;
}

.radar-chart-placeholder {
  width: 100%;
  height: 100%;
  border: 2px dashed rgba(255, 255, 255, 0.2);
  border-radius: 8px;
}

.ability-item {
  transition: all 0.3s ease;
  border-radius: 8px;
  margin: 4px 0;
}

.ability-item:hover {
  background: rgba(255, 255, 255, 0.1) !important;
}

.ability-progress {
  height: 8px !important;
  border-radius: 4px;
  box-shadow: 0 0 5px rgba(0, 0, 0, 0.2);
}

.custom-btn {
  transition: all 0.3s ease;
}

.custom-btn:hover {
  transform: translateY(-3px);
  background: rgba(255, 255, 255, 0.1) !important;
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
.user-center {
  background-color: #ffffff !important;
  min-height: 100vh;
}

.user-center .v-container {
  background: transparent !important;
}

.user-center .v-main {
  background-color: #ffffff !important;
}

.user-center .v-application {
  background-color: #ffffff !important;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .nav-links {
    display: none;
  }

  .mobile-menu-btn {
    display: block;
  }
}
</style>