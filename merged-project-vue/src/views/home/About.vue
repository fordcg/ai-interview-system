<template>
  <div class="about-page">
    <!-- 顶部导航栏 -->
    <header class="header">
      <div class="header-content">
        <div class="logo-container">
          <img src="@/assets/images/logo.png" alt="面试星途" class="logo" />
          <span class="logo-text">面试星途</span>
        </div>
        <nav class="nav-links">
          <a @click="navigateTo('/')" class="nav-link">首页</a>
          <a v-if="isLoggedIn" @click="navigateTo('/interview')" class="nav-link">面试中心</a>
          <a v-if="isLoggedIn" @click="navigateTo('/user/center')" class="nav-link">个人中心</a>
          <a v-if="!isLoggedIn" @click="navigateTo('/features')" class="nav-link">功能介绍</a>
          <a @click="navigateTo('/about')" class="nav-link active">关于我们</a>
        </nav>
        <div class="auth-buttons">
          <div v-if="!isLoggedIn">
            <router-link to="/login" class="login-btn">登录</router-link>
            <router-link to="/register" class="register-btn">注册</router-link>
          </div>
          <div v-else class="user-info">
            <span class="welcome-text">欢迎，{{ username }}</span>
            <button @click="logout" class="logout-btn">退出</button>
          </div>
        </div>
      </div>
    </header>

    <!-- 主要内容区 -->
    <main class="main-content">
      <!-- 英雄区域 -->
      <section class="hero-section">
        <div class="hero-content">
          <h1 class="hero-title">关于面试星途</h1>
          <p class="hero-description">
            专业的AI面试准备平台，致力于帮助求职者提升面试技能，实现职业梦想
          </p>
        </div>
      </section>

      <!-- 使命愿景区域 -->
      <section class="mission-section">
        <div class="container">
          <div class="mission-content">
            <div class="mission-text">
              <h2 class="section-title">我们的使命</h2>
              <p class="mission-description">
                用AI技术革新面试准备体验，帮助每一位求职者充分展示自己的价值，
                在竞争激烈的就业市场中脱颖而出，实现职业梦想。
              </p>
              <div class="mission-points">
                <div class="point">
                  <v-icon color="#1867FF" size="24" class="point-icon">mdi-target</v-icon>
                  <span>提供专业的面试准备工具</span>
                </div>
                <div class="point">
                  <v-icon color="#1867FF" size="24" class="point-icon">mdi-brain</v-icon>
                  <span>运用AI技术提升求职效率</span>
                </div>
                <div class="point">
                  <v-icon color="#1867FF" size="24" class="point-icon">mdi-heart</v-icon>
                  <span>助力求职者实现职业梦想</span>
                </div>
              </div>
            </div>
            <div class="mission-image">
              <v-icon size="150" color="#1867FF">mdi-rocket-launch</v-icon>
            </div>
          </div>
        </div>
      </section>

      <!-- 团队介绍区域 -->
      <section class="team-section">
        <div class="container">
          <h2 class="section-title">我们的团队</h2>
          <p class="section-description">
            一支充满激情的技术团队，致力于用创新技术改变求职体验
          </p>

          <div class="team-grid">
            <div class="team-card" v-for="(member, index) in team" :key="index">
              <div class="member-avatar">
                <img :src="member.avatar" :alt="member.name" />
              </div>
              <h3 class="member-name">{{ member.name }}</h3>
              <p class="member-role">{{ member.role }}</p>
              <p class="member-description">{{ member.description }}</p>
              <div class="member-social">
                <a href="#" class="social-link">
                  <v-icon size="20">mdi-email</v-icon>
                </a>
                <a href="#" class="social-link">
                  <v-icon size="20">mdi-linkedin</v-icon>
                </a>
                <a href="#" class="social-link">
                  <v-icon size="20">mdi-github</v-icon>
                </a>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 技术栈区域 -->
      <section class="tech-section">
        <div class="container">
          <h2 class="section-title">技术架构</h2>
          <p class="section-description">
            采用现代化技术栈，确保系统的稳定性、可扩展性和用户体验
          </p>

          <div class="tech-grid">
            <div class="tech-category">
              <div class="tech-header">
                <v-icon size="32" color="#1867FF">mdi-laptop</v-icon>
                <h3>前端技术</h3>
              </div>
              <div class="tech-list">
                <div class="tech-item" v-for="(tech, index) in frontendTech" :key="index">
                  <v-icon :color="tech.color" size="24">{{ tech.icon }}</v-icon>
                  <div class="tech-info">
                    <h4>{{ tech.name }}</h4>
                    <p>{{ tech.description }}</p>
                  </div>
                </div>
              </div>
            </div>

            <div class="tech-category">
              <div class="tech-header">
                <v-icon size="32" color="#1867FF">mdi-server</v-icon>
                <h3>后端技术</h3>
              </div>
              <div class="tech-list">
                <div class="tech-item" v-for="(tech, index) in backendTech" :key="index">
                  <v-icon :color="tech.color" size="24">{{ tech.icon }}</v-icon>
                  <div class="tech-info">
                    <h4>{{ tech.name }}</h4>
                    <p>{{ tech.description }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 联系我们区域 -->
      <section class="contact-section">
        <div class="contact-content">
          <h2 class="contact-title">联系我们</h2>
          <p class="contact-description">
            如果您对我们的系统有任何建议或问题，欢迎随时联系我们。
            我们将不断完善系统功能，为用户提供更好的体验。
          </p>
          <div class="contact-buttons">
            <a href="mailto:support@interviewstar.com" class="contact-button secondary">
              <v-icon left>mdi-email</v-icon>
              发送邮件
            </a>
            <router-link to="/help" class="contact-button secondary">
              <v-icon left>mdi-help-circle</v-icon>
              帮助中心
            </router-link>
          </div>
        </div>
      </section>
    </main>

    <!-- 页脚 -->
    <footer class="footer">
      <div class="footer-content">
        <div class="footer-section">
          <h3 class="footer-title">面试星途</h3>
          <p class="footer-description">
            专业的面试准备平台，助力您的职业发展
          </p>
        </div>
        <div class="footer-section">
          <h3 class="footer-title">快速链接</h3>
          <ul class="footer-links">
            <li><router-link to="/">首页</router-link></li>
            <li><router-link to="/features">功能介绍</router-link></li>
            <li><router-link to="/about">关于我们</router-link></li>
          </ul>
        </div>
      </div>
      <div class="footer-bottom">
        <p>&copy; {{ new Date().getFullYear() }} 面试星途 - 专业面试准备平台</p>
      </div>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'AboutPage',
  data() {
    return {
      team: [
        {
          name: '张伟（技术负责人）',
          role: '全栈开发工程师',
          avatar: require('@/assets/images/avatars/1.png'),
          description: '负责系统架构设计和核心功能开发，拥有5年AI和Web开发经验。'
        },
        {
          name: '李雪',
          role: 'UI/UX设计师',
          avatar: require('@/assets/images/avatars/2.png'),
          description: '负责产品设计和用户体验优化，专注于创造直观易用的界面。'
        },
        {
          name: '王强',
          role: 'AI算法工程师',
          avatar: require('@/assets/images/default-avatar.png'),
          description: '专注于自然语言处理和机器学习算法，为面试评估提供技术支持。'
        },
        {
          name: '陈敏',
          role: '产品经理',
          avatar: require('@/assets/images/default-avatar.png'),
          description: '负责产品规划和需求分析，致力于打造最佳的用户体验。'
        }
      ],
      frontendTech: [
        {
          name: 'Vue.js',
          icon: 'mdi-vuejs',
          color: 'green',
          description: '渐进式JavaScript框架，用于构建用户界面'
        },
        {
          name: 'Vuetify',
          icon: 'mdi-material-design',
          color: 'blue',
          description: 'Material Design组件框架，提供美观的UI组件'
        },
        {
          name: 'Axios',
          icon: 'mdi-api',
          color: 'purple',
          description: '基于Promise的HTTP客户端，用于浏览器和Node.js'
        },
        {
          name: 'Vuex',
          icon: 'mdi-database',
          color: 'deep-purple',
          description: '状态管理模式和库，用于Vue.js应用'
        }
      ],
      backendTech: [
        {
          name: 'Flask',
          icon: 'mdi-flask',
          color: 'blue-grey',
          description: '轻量级Python Web应用框架'
        },
        {
          name: 'TensorFlow',
          icon: 'mdi-tensorflow',
          color: 'orange',
          description: '开源机器学习平台，用于模型训练和推理'
        },
        {
          name: 'MySQL',
          icon: 'mdi-database',
          color: 'blue',
          description: '关系型数据库管理系统'
        },
        {
          name: 'Redis',
          icon: 'mdi-database-lock',
          color: 'red',
          description: '内存数据结构存储，用作数据库、缓存和消息代理'
        }
      ]
    }
  },
  computed: {
    isLoggedIn() {
      return !!this.$store.state.user.token
    },
    username() {
      return this.$store.state.user.username || '用户'
    }
  },
  methods: {
    navigateTo(path) {
      console.log('Navigating to:', path)
      console.log('Current route:', this.$route.path)
      console.log('Router instance:', this.$router)

      // 尝试多种导航方式
      if (path === this.$route.path) {
        console.log('Already on this page')
        return
      }

      try {
        // 方法1: 使用push
        this.$router.push(path).then(() => {
          console.log('Navigation successful with push')
        }).catch(err => {
          console.error('Push navigation error:', err)

          // 方法2: 如果push失败，尝试replace
          this.$router.replace(path).then(() => {
            console.log('Navigation successful with replace')
          }).catch(err2 => {
            console.error('Replace navigation error:', err2)

            // 方法3: 如果都失败，使用window.location
            console.log('Using window.location as fallback')
            window.location.href = path
          })
        })
      } catch (error) {
        console.error('Navigation method error:', error)
        window.location.href = path
      }
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
    }
  },
  mounted() {
    document.title = '关于我们 - 面试星途';
  }
}
</script>

<style scoped>
/* 基础样式 */
.about-page {
  font-family: PingFangSC-Regular, 'PingFang SC', 'Microsoft YaHei', sans-serif;
  color: #333;
  line-height: 1.6;
  background-color: #fff;
}

/* 顶部导航栏 */
.header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background-color: rgba(255, 255, 255, 0.98);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  z-index: 100;
  padding: 0.8rem 0;
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
  padding-top: 70px;
}

/* 英雄区域 */
.hero-section {
  background: linear-gradient(135deg, #F5F9FF 0%, #FFFFFF 100%);
  padding: 5rem 2rem;
  text-align: center;
}

.hero-title {
  font-size: 2.8rem;
  font-weight: 600;
  color: #1B2B3D;
  margin-bottom: 1.5rem;
  background: linear-gradient(135deg, #1867FF 0%, #0052D9 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-description {
  font-size: 1.2rem;
  color: #666666;
  max-width: 600px;
  margin: 0 auto;
}

/* 通用容器和标题 */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}

.section-title {
  font-size: 2.2rem;
  font-weight: 700;
  color: #1B2B3D;
  text-align: center;
  margin-bottom: 1rem;
}

.section-description {
  font-size: 1.1rem;
  color: #666666;
  text-align: center;
  margin-bottom: 3rem;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

/* 使命愿景区域 */
.mission-section {
  padding: 5rem 0;
  background-color: #fff;
}

.mission-content {
  display: flex;
  align-items: center;
  gap: 4rem;
}

.mission-text {
  flex: 1;
}

.mission-description {
  font-size: 1.1rem;
  color: #666666;
  margin-bottom: 2rem;
  line-height: 1.7;
}

.mission-points {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.point {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  font-size: 1rem;
  color: #555;
}

.point-icon {
  flex-shrink: 0;
}

.mission-image {
  flex: 0 0 200px;
  text-align: center;
  background: rgba(24, 103, 255, 0.05);
  border-radius: 20px;
  padding: 2rem;
}

/* 团队介绍区域 */
.team-section {
  padding: 5rem 0;
  background-color: #F5F9FF;
}

.team-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 2rem;
}

.team-card {
  background: white;
  padding: 2rem;
  border-radius: 16px;
  text-align: center;
  box-shadow: 0 4px 20px rgba(24, 103, 255, 0.08);
  transition: transform 0.3s;
}

.team-card:hover {
  transform: translateY(-5px);
}

.member-avatar {
  width: 120px;
  height: 120px;
  margin: 0 auto 1.5rem;
  border-radius: 50%;
  overflow: hidden;
  border: 4px solid #1867FF;
}

.member-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.member-name {
  font-size: 1.3rem;
  font-weight: 600;
  color: #1B2B3D;
  margin-bottom: 0.5rem;
}

.member-role {
  font-size: 1rem;
  color: #1867FF;
  font-weight: 500;
  margin-bottom: 1rem;
}

.member-description {
  font-size: 0.95rem;
  color: #666666;
  line-height: 1.6;
  margin-bottom: 1.5rem;
}

.member-social {
  display: flex;
  justify-content: center;
  gap: 0.8rem;
}

.social-link {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background-color: #f5f5f5;
  border-radius: 50%;
  color: #666;
  text-decoration: none;
  transition: all 0.3s;
}

.social-link:hover {
  background-color: #1867FF;
  color: white;
}

/* 技术栈区域 */
.tech-section {
  padding: 5rem 0;
  background-color: #fff;
}

.tech-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 3rem;
}

.tech-category {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 4px 20px rgba(24, 103, 255, 0.08);
}

.tech-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #f0f0f0;
}

.tech-header h3 {
  font-size: 1.4rem;
  font-weight: 600;
  color: #1B2B3D;
  margin: 0;
}

.tech-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.tech-item {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
}

.tech-info h4 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #1B2B3D;
  margin: 0 0 0.5rem 0;
}

.tech-info p {
  font-size: 0.95rem;
  color: #666666;
  margin: 0;
  line-height: 1.5;
}

/* 联系我们区域 */
.contact-section {
  padding: 5rem 2rem;
  background: linear-gradient(135deg, #1867FF 0%, #0052D9 100%);
  color: white;
  text-align: center;
}

.contact-title {
  font-size: 2.2rem;
  font-weight: 700;
  margin-bottom: 1rem;
}

.contact-description {
  font-size: 1.1rem;
  margin-bottom: 2rem;
  opacity: 0.9;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.contact-buttons {
  display: flex;
  justify-content: center;
  gap: 1rem;
}

.contact-button {
  padding: 1rem 2rem;
  border-radius: 6px;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.contact-button.primary {
  background: white;
  color: #1867FF;
}

.contact-button.primary:hover {
  background: #f0f0f0;
}

.contact-button.secondary {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid white;
}

.contact-button.secondary:hover {
  background: rgba(255, 255, 255, 0.3);
}

/* 页脚 */
.footer {
  background-color: #1B2B3D;
  color: white;
  padding: 3rem 2rem 1rem;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 2rem;
  margin-bottom: 2rem;
}

.footer-title {
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: #1867FF;
}

.footer-description {
  color: #d1d5db;
  font-size: 0.95rem;
  line-height: 1.7;
}

.footer-links {
  list-style: none;
  padding: 0;
  margin: 0;
}

.footer-links li {
  margin-bottom: 0.5rem;
}

.footer-links a {
  color: #d1d5db;
  text-decoration: none;
  transition: color 0.3s;
}

.footer-links a:hover {
  color: white;
}

.footer-bottom {
  text-align: center;
  padding-top: 2rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  color: #9ca3af;
  font-size: 0.9rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .nav-links {
    display: none;
  }

  .hero-title {
    font-size: 2rem;
  }

  .mission-content {
    flex-direction: column;
    text-align: center;
  }

  .tech-grid {
    grid-template-columns: 1fr;
  }

  .team-grid {
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  }

  .contact-buttons {
    flex-direction: column;
    align-items: center;
  }

  .contact-button {
    width: 100%;
    max-width: 300px;
    justify-content: center;
  }

  .section-title {
    font-size: 1.8rem;
  }

  .container {
    padding: 0 1rem;
  }
}

@media (max-width: 480px) {
  .hero-title {
    font-size: 1.6rem;
  }

  .team-grid {
    grid-template-columns: 1fr;
  }

  .tech-grid {
    grid-template-columns: 1fr;
  }
}
</style>