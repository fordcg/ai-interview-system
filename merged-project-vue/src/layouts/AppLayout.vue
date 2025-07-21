<template>
  <v-app id="app" style="background-color: #F5F7FA;">
    <!-- 亮色主题顶部导航栏 -->
    <v-app-bar 
      color="white" 
      light 
      app 
      :elevate-on-scroll="true"
      :scroll-threshold="0"
      class="px-4 light-navbar"
      :class="{'navbar-hidden': !showNavbar}"
    >
      <v-toolbar-title class="d-flex align-center">
        <img src="@/assets/images/logo.png" alt="Logo" class="mr-3" style="height: 32px;"/>
        <span class="custom-logo-text">面试星途</span>
      </v-toolbar-title>
      
      <v-spacer></v-spacer>

      <!-- 流程步骤栏 -->
      <div class="process-steps d-none d-md-flex">
        <div class="process-step" :class="{ 'active': isCurrentStep(1), 'completed': isStepCompleted(1) }">
          <div class="step-number">1</div>
          <div class="step-label">准备简历</div>
        </div>

        <div class="step-connector"></div>

        <div class="process-step" :class="{ 'active': isCurrentStep(2), 'completed': isStepCompleted(2) }">
          <div class="step-number">2</div>
          <div class="step-label">选择职位</div>
        </div>

        <div class="step-connector"></div>

        <div class="process-step" :class="{ 'active': isCurrentStep(3), 'completed': isStepCompleted(3) }">
          <div class="step-number">3</div>
          <div class="step-label">面试分析</div>
        </div>

        <div class="step-connector"></div>

        <div class="process-step" :class="{ 'active': isCurrentStep(4), 'completed': isStepCompleted(4) }">
          <div class="step-number">4</div>
          <div class="step-label">面试模拟</div>
        </div>

        <div class="step-connector"></div>

        <div class="process-step" :class="{ 'active': isCurrentStep(5), 'completed': isStepCompleted(5) }">
          <div class="step-number">5</div>
          <div class="step-label">查看报告</div>
        </div>
      </div>

      <v-spacer></v-spacer>
      
      <!-- 通知按钮 -->
      <v-btn icon class="mr-3 notification-btn">
        <v-badge dot color="error" overlap>
          <v-icon>mdi-bell-outline</v-icon>
        </v-badge>
      </v-btn>
      
      <!-- 用户菜单 -->
      <v-menu offset-y :close-on-content-click="true" transition="slide-y-transition">
        <template v-slot:activator="{ on, attrs }">
          <div class="user-menu-activator" v-bind="attrs" v-on="on">
            <v-avatar size="40" class="cursor-pointer">
              <v-img :src="avatar || require('../assets/images/default-avatar.png')"></v-img>
            </v-avatar>
            <div class="user-info ml-2 d-none d-sm-block">
              <div class="user-name">{{ username || '用户' }}</div>
            </div>
            <v-icon class="ml-1 chevron-icon">mdi-chevron-down</v-icon>
          </div>
        </template>
        <v-card class="user-menu-card">
          <v-list class="user-menu-list" dense>
            <v-list-item class="user-card-header">
               <v-list-item-avatar>
                 <v-img :src="avatar || require('../assets/images/default-avatar.png')"></v-img>
               </v-list-item-avatar>
               <v-list-item-content>
                 <v-list-item-title class="font-weight-bold">{{ username || '用户' }}</v-list-item-title>
                 <v-list-item-subtitle>普通用户</v-list-item-subtitle>
               </v-list-item-content>
            </v-list-item>
            <v-divider class="my-1"></v-divider>
            <v-list-item to="/user/center" class="menu-item">
              <v-list-item-icon class="mr-3">
                <v-icon size="20">mdi-account-circle-outline</v-icon>
              </v-list-item-icon>
              <v-list-item-title>个人中心</v-list-item-title>
            </v-list-item>
            <v-list-item to="/user/profile" class="menu-item">
              <v-list-item-icon class="mr-3">
                <v-icon size="20">mdi-account-outline</v-icon>
              </v-list-item-icon>
              <v-list-item-title>个人资料</v-list-item-title>
            </v-list-item>
            <v-list-item to="/user/settings" class="menu-item">
              <v-list-item-icon class="mr-3">
                <v-icon size="20">mdi-cog-outline</v-icon>
              </v-list-item-icon>
              <v-list-item-title>设置</v-list-item-title>
            </v-list-item>
            <v-divider class="my-1"></v-divider>
            <v-list-item @click="logout" class="menu-item">
              <v-list-item-icon class="mr-3">
                <v-icon size="20">mdi-logout</v-icon>
              </v-list-item-icon>
              <v-list-item-title>退出</v-list-item-title>
            </v-list-item>
          </v-list>
        </v-card>
      </v-menu>
    </v-app-bar>
    
    <!-- 移动端流程步骤 -->
    <v-bottom-navigation
      app
      grow
      color="primary"
      class="d-md-none"
    >
      <v-btn @click="setCurrentStep(1)" :value="1" :input-value="currentStep === 1">
        <span>简历</span>
        <v-icon>mdi-file-document-outline</v-icon>
      </v-btn>
      
      <v-btn @click="setCurrentStep(2)" :value="2" :input-value="currentStep === 2">
        <span>职位</span>
        <v-icon>mdi-briefcase-outline</v-icon>
      </v-btn>
      
      <v-btn @click="setCurrentStep(3)" :value="3" :input-value="currentStep === 3">
        <span>分析</span>
        <v-icon>mdi-file-search-outline</v-icon>
      </v-btn>
      
      <v-btn @click="setCurrentStep(4)" :value="4" :input-value="currentStep === 4">
        <span>面试</span>
        <v-icon>mdi-account-voice-outline</v-icon>
      </v-btn>
      
      <v-btn @click="setCurrentStep(5)" :value="5" :input-value="currentStep === 5">
        <span>报告</span>
        <v-icon>mdi-chart-box-outline</v-icon>
      </v-btn>
    </v-bottom-navigation>
    
    <!-- 路由视图 -->
    <v-main class="pa-0">
      <transition name="fade" mode="out-in">
        <router-view />
      </transition>
    </v-main>
  </v-app>
</template>

<script>
export default {
  name: "AppLayout",
  data: () => ({
    currentStep: 1,
    completedSteps: [],
    lastScrollPosition: 0,
    showNavbar: true,
    scrollTicking: false
  }),
  computed: {
    screenIsSmall() {
      return this.$vuetify.breakpoint.smAndDown
    },
    avatar() {
      return this.$store.state.user && this.$store.state.user.avatar
    },
    username() {
      return this.$store.state.user && this.$store.state.user.username
    }
  },
  methods: {
    logout() {
      this.$store.dispatch('user/logout')
        .then(() => {
          this.$router.push('/')
        })
        .catch(error => {
          console.error('退出登录失败:', error)
        })
    },
    isCurrentStep(step) {
      return this.currentStep === step
    },
    isStepCompleted(step) {
      return this.completedSteps.includes(step) || step < this.currentStep
    },
    setCurrentStep(step) {
      // 根据步骤跳转到对应页面
      const stepRoutes = {
        1: '/dashboard',
        2: '/job/list',
        3: '/interview/analysis',
        4: '/interview/process',
        5: '/interview/report'
      }
      
      if (stepRoutes[step]) {
        this.$router.push(stepRoutes[step])
      }
      
      this.currentStep = step
    },
    // 监听路由变化，更新当前步骤
    updateCurrentStepFromRoute() {
      const routeStepMap = {
        '/dashboard': 1,
        '/job/list': 2,
        '/job/detail': 2,
        '/interview/analysis': 3,
        '/interview/process': 4,
        '/interview/report': 5
      }
      
      // 检查当前路由是否匹配任何步骤
      const currentPath = this.$route.path
      
      for (const [route, step] of Object.entries(routeStepMap)) {
        if (currentPath.startsWith(route)) {
          this.currentStep = step
          break
        }
      }
    },
    // 处理滚动事件
    handleScroll() {
      if (!this.scrollTicking) {
        window.requestAnimationFrame(() => {
          this.processScrollEvent();
          this.scrollTicking = false;
        });
        this.scrollTicking = true;
      }
    },
    
    // 处理实际的滚动逻辑
    processScrollEvent() {
      const currentScrollPosition = window.pageYOffset || document.documentElement.scrollTop;
      
      // 调试输出
      console.log('Scroll position:', currentScrollPosition);
      
      // 根据滚动位置和方向控制导航栏显示
      if (currentScrollPosition <= 100) {
        // 在顶部时显示导航栏
        this.showNavbar = true;
        console.log('At top, showing navbar');
      } else if (currentScrollPosition > 100) {
        // 不在顶部时隐藏导航栏
        this.showNavbar = false;
        console.log('Not at top, hiding navbar');
      }
      
      this.lastScrollPosition = currentScrollPosition;
    }
  },
  watch: {
    '$route'() {
      this.updateCurrentStepFromRoute()
    }
  },
  mounted() {
    this.updateCurrentStepFromRoute();
    
    // 初始化滚动位置
    this.lastScrollPosition = window.pageYOffset || document.documentElement.scrollTop;
    
    // 添加滚动事件监听
    window.addEventListener('scroll', this.handleScroll, { passive: true });
    console.log('Scroll event listener added');
    
    // 确保初始状态正确
    this.$nextTick(() => {
      console.log('Initial scroll position check');
      this.processScrollEvent();
    });
    
    // 强制触发一次滚动事件处理，确保初始状态正确
    setTimeout(() => {
      console.log('Forced scroll event processing');
      this.processScrollEvent();
    }, 500);
  },
  beforeDestroy() {
    // 移除滚动事件监听
    window.removeEventListener('scroll', this.handleScroll);
  }
}
</script>

<style scoped>
:root {
  --primary-color: #1867FF;
  --text-color: #1B2B3D;
  --secondary-text-color: #555;
  --border-color: #EAEAEA;
  --bg-color-light: #F5F7FA;
}

/* 亮色主题导航栏 */
.light-navbar {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06) !important;
  border-bottom: 1px solid var(--border-color) !important;
  transition: transform 0.2s ease-out !important; /* 加快过渡动画时间，使用ease-out让展开更快 */
  transform: translateY(0); /* 确保默认状态是显示的 */
  z-index: 100 !important; /* 确保导航栏在圆形动画和所有内容之上 */
}

/* 导航栏隐藏时的样式 */
.navbar-hidden {
  transform: translateY(-100%) !important; /* 使用 !important 确保样式被应用 */
  transition: transform 0.3s ease-in !important; /* 收起时使用稍慢的速度，ease-in效果 */
}

.custom-logo-text {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-color);
}

/* 流程步骤样式 */
.process-steps {
  display: flex;
  align-items: center;
  height: 100%;
  padding: 0 16px;
}

.process-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  padding: 0 8px;
  transition: all 0.3s ease;
  cursor: pointer;
}

.step-number {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: #e0e0e0;
  color: #757575;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  margin-bottom: 4px;
  transition: all 0.3s ease;
}

.step-label {
  font-size: 0.85rem;
  color: #757575;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.step-connector {
  height: 2px;
  width: 40px;
  background-color: #e0e0e0;
  margin: 0 4px;
  position: relative;
  top: -14px;
}

.process-step.active .step-number {
  background-color: #1867FF;
  color: white;
  box-shadow: 0 2px 8px rgba(24, 103, 255, 0.3);
}

.process-step.active .step-label {
  color: #1867FF;
  font-weight: 600;
}

.process-step.completed .step-number {
  background-color: #4CAF50;
  color: white;
}

.process-step.completed .step-label {
  color: #4CAF50;
}

.process-step:hover .step-number {
  transform: scale(1.1);
}

/* 用户菜单 */
.user-menu-activator {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 50px;
  transition: all 0.3s ease;
}

.user-menu-activator:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.user-name {
  font-weight: 500;
  font-size: 0.95rem;
  color: var(--text-color);
}

.user-menu-card {
  border-radius: 8px !important;
  border: 1px solid var(--border-color) !important;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1) !important;
}

.user-menu-list {
  background-color: white !important;
}

.user-card-header {
  background-color: #F5F9FF;
}

.menu-item {
  transition: all 0.2s ease;
}

.menu-item:hover {
  background-color: rgba(24, 103, 255, 0.08) !important;
}

.menu-item .v-list-item__title {
  color: var(--secondary-text-color);
}
.menu-item:hover .v-list-item__title {
  color: var(--primary-color);
}
.menu-item .v-list-item__icon .v-icon {
  color: var(--secondary-text-color);
}
.menu-item:hover .v-list-item__icon .v-icon {
  color: var(--primary-color);
}

/* 通知按钮 */
.notification-btn {
  color: var(--secondary-text-color);
  transition: all 0.3s ease;
}

.notification-btn:hover {
  color: var(--primary-color);
}

/* 页面过渡动画 */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter, .fade-leave-to {
  opacity: 0;
}

/* 底部导航栏样式 */
.v-bottom-navigation {
  z-index: 100 !important; /* 确保底部导航栏在圆形动画和所有内容之上 */
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.06) !important;
}
</style> 