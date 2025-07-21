<template>
  <div class="features-page">
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
          <a v-if="!isLoggedIn" @click="navigateTo('/features')" class="nav-link active">功能介绍</a>
          <a @click="navigateTo('/about')" class="nav-link">关于我们</a>
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
      <!-- 功能介绍标题区域 -->
      <section class="hero-section">
        <div class="hero-content">
          <h1 class="hero-title">强大的面试准备功能</h1>
          <p class="hero-description">
            全方位的面试准备工具，助您在求职路上脱颖而出
          </p>
        </div>
      </section>

      <!-- 核心功能详细介绍 -->
      <section class="features-detail-section">
        <div class="container">
          <!-- 简历准备功能 -->
          <div class="feature-block">
            <div class="feature-content">
              <div class="feature-text">
                <h2 class="feature-title">智能简历准备</h2>
                <p class="feature-description">
                  支持简历上传和AI智能生成，快速创建专业简历。系统会自动提取您的技能信息，
                  为您推荐最匹配的职位机会。
                </p>
                <ul class="feature-list">
                  <li>支持多种格式简历上传（PDF、Word等）</li>
                  <li>AI智能简历生成，个性化定制</li>
                  <li>自动技能提取和分析</li>
                  <li>智能职位推荐匹配</li>
                </ul>
              </div>
              <div class="feature-image">
                <v-icon size="120" color="#1867FF">mdi-file-document-edit</v-icon>
              </div>
            </div>
          </div>

          <!-- 职位分析功能 -->
          <div class="feature-block reverse">
            <div class="feature-content">
              <div class="feature-image">
                <v-icon size="120" color="#1867FF">mdi-chart-line</v-icon>
              </div>
              <div class="feature-text">
                <h2 class="feature-title">职位智能分析</h2>
                <p class="feature-description">
                  深度分析职位要求，为您提供详细的职位匹配度分析和准备建议。
                  帮助您了解目标职位的核心要求。
                </p>
                <ul class="feature-list">
                  <li>职位要求深度解析</li>
                  <li>技能匹配度分析</li>
                  <li>薪资水平参考</li>
                  <li>面试准备建议</li>
                </ul>
              </div>
            </div>
          </div>

          <!-- 面试模拟功能 -->
          <div class="feature-block">
            <div class="feature-content">
              <div class="feature-text">
                <h2 class="feature-title">沉浸式面试模拟</h2>
                <p class="feature-description">
                  真实的面试场景模拟，支持语音交互和实时反馈。
                  通过反复练习提升您的面试表现和自信心。
                </p>
                <ul class="feature-list">
                  <li>真实面试场景还原</li>
                  <li>语音交互面试体验</li>
                  <li>多种面试类型支持</li>
                  <li>实时表现分析反馈</li>
                </ul>
              </div>
              <div class="feature-image">
                <v-icon size="120" color="#1867FF">mdi-account-voice</v-icon>
              </div>
            </div>
          </div>

          <!-- 面试报告功能 -->
          <div class="feature-block reverse">
            <div class="feature-content">
              <div class="feature-image">
                <v-icon size="120" color="#1867FF">mdi-chart-bar</v-icon>
              </div>
              <div class="feature-text">
                <h2 class="feature-title">详细面试报告</h2>
                <p class="feature-description">
                  全面的面试表现分析报告，包含优势分析、改进建议和历史对比。
                  帮助您持续提升面试技能。
                </p>
                <ul class="feature-list">
                  <li>多维度表现评估</li>
                  <li>详细改进建议</li>
                  <li>历史表现对比</li>
                  <li>技能发展轨迹</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 技术特色 -->
      <section class="tech-features-section">
        <div class="container">
          <h2 class="section-title">技术特色</h2>
          <div class="tech-grid">
            <div class="tech-card">
              <v-icon size="48" color="#1867FF" class="mb-4">mdi-brain</v-icon>
              <h3>AI智能分析</h3>
              <p>基于先进的AI技术，提供精准的简历分析和面试评估</p>
            </div>
            <div class="tech-card">
              <v-icon size="48" color="#1867FF" class="mb-4">mdi-microphone</v-icon>
              <h3>语音识别</h3>
              <p>先进的语音识别技术，支持自然语言交互</p>
            </div>
            <div class="tech-card">
              <v-icon size="48" color="#1867FF" class="mb-4">mdi-database</v-icon>
              <h3>大数据支持</h3>
              <p>基于海量面试数据，提供准确的行业洞察</p>
            </div>
            <div class="tech-card">
              <v-icon size="48" color="#1867FF" class="mb-4">mdi-security</v-icon>
              <h3>数据安全</h3>
              <p>严格的数据保护措施，确保您的隐私安全</p>
            </div>
          </div>
        </div>
      </section>

      <!-- 开始使用 -->
      <section class="cta-section">
        <div class="cta-content">
          <h2 class="cta-title">准备好开始您的面试之旅了吗？</h2>
          <p class="cta-description">
            立即注册，体验专业的面试准备服务
          </p>
          <div class="cta-buttons">
            <router-link to="/register" class="cta-button secondary">免费注册</router-link>
            <router-link to="/dashboard" class="cta-button secondary">立即体验</router-link>
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
  name: 'FeaturesPage',
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
    document.title = '功能介绍 - 面试星途';
  }
}
</script>

<style scoped>
/* 基础样式 */
.features-page {
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

/* 功能详细介绍 */
.features-detail-section {
  padding: 5rem 0;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}

.feature-block {
  margin-bottom: 5rem;
}

.feature-content {
  display: flex;
  align-items: center;
  gap: 4rem;
}

.feature-block.reverse .feature-content {
  flex-direction: row-reverse;
}

.feature-text {
  flex: 1;
}

.feature-image {
  flex: 0 0 200px;
  text-align: center;
  background: rgba(24, 103, 255, 0.05);
  border-radius: 20px;
  padding: 2rem;
}

.feature-title {
  font-size: 2rem;
  font-weight: 600;
  color: #1B2B3D;
  margin-bottom: 1rem;
}

.feature-description {
  font-size: 1.1rem;
  color: #666666;
  margin-bottom: 1.5rem;
  line-height: 1.7;
}

.feature-list {
  list-style: none;
  padding: 0;
}

.feature-list li {
  padding: 0.5rem 0;
  color: #555;
  position: relative;
  padding-left: 1.5rem;
}

.feature-list li::before {
  content: "✓";
  position: absolute;
  left: 0;
  color: #1867FF;
  font-weight: bold;
}

/* 技术特色 */
.tech-features-section {
  background-color: #F5F9FF;
  padding: 5rem 0;
}

.section-title {
  font-size: 2.2rem;
  font-weight: 700;
  color: #1B2B3D;
  text-align: center;
  margin-bottom: 3rem;
}

.tech-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
}

.tech-card {
  background: white;
  padding: 2rem;
  border-radius: 16px;
  text-align: center;
  box-shadow: 0 4px 20px rgba(24, 103, 255, 0.08);
  transition: transform 0.3s;
}

.tech-card:hover {
  transform: translateY(-5px);
}

.tech-card h3 {
  font-size: 1.3rem;
  font-weight: 600;
  color: #1B2B3D;
  margin-bottom: 1rem;
}

.tech-card p {
  color: #666666;
  font-size: 0.95rem;
}

/* 开始使用区域 */
.cta-section {
  padding: 5rem 2rem;
  background: linear-gradient(135deg, #1867FF 0%, #0052D9 100%);
  color: white;
  text-align: center;
}

.cta-title {
  font-size: 2.2rem;
  font-weight: 700;
  margin-bottom: 1rem;
}

.cta-description {
  font-size: 1.1rem;
  margin-bottom: 2rem;
  opacity: 0.9;
}

.cta-buttons {
  display: flex;
  justify-content: center;
  gap: 1rem;
}

.cta-button {
  padding: 1rem 2rem;
  border-radius: 6px;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.3s;
}

.cta-button.primary {
  background: white;
  color: #1867FF;
}

.cta-button.primary:hover {
  background: #f0f0f0;
}

.cta-button.secondary {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid white;
}

.cta-button.secondary:hover {
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
  
  .feature-content {
    flex-direction: column;
    text-align: center;
  }
  
  .feature-block.reverse .feature-content {
    flex-direction: column;
  }
  
  .cta-buttons {
    flex-direction: column;
    align-items: center;
  }
  
  .cta-button {
    width: 100%;
    max-width: 300px;
  }
}
</style>
