<template>
  <div class="home-container">
    <!-- 顶部导航栏 -->
    <header class="header">
      <div class="header-content">
        <div class="logo-container">
          <img src="@/assets/images/logo.png" alt="面试星途" class="logo" />
          <span class="logo-text">面试星途</span>
        </div>
        <nav class="nav-links" :class="{ hidden: !showMobileMenu }">
          <router-link to="/" class="nav-link active">首页</router-link>
          <router-link v-if="isLoggedIn" to="/interview" class="nav-link">面试中心</router-link>
          <router-link v-if="isLoggedIn" to="/user/center" class="nav-link">个人中心</router-link>
          <router-link v-if="!isLoggedIn" to="/features" class="nav-link">功能介绍</router-link>
          <router-link to="/about" class="nav-link">关于我们</router-link>
        </nav>

        <button class="mobile-menu-btn" @click="toggleMobileMenu">
          <v-icon>{{ showMobileMenu ? 'mdi-close' : 'mdi-menu' }}</v-icon>
        </button>
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
    <main>
      <!-- 英雄区域 -->
      <section class="hero-section">
        <div class="hero-content">
          <h1 class="hero-title">多模态智能面试<br />模拟与评估系统</h1>
          <p class="hero-description">
            基于AI大模型技术，提供真实面试场景模拟，全方位评估与反馈，<br />
            帮助您提升面试技能，开启职业新征程
          </p>
          <div class="hero-buttons">
            <router-link to="/dashboard" class="try-now-btn">立即体验</router-link>
            <router-link to="/features" class="learn-more-btn">了解更多</router-link>
          </div>
        </div>
        <div class="hero-image">
          <img src="@/assets/images/hip.png" alt="面试场景" />
        </div>
      </section>

      <!-- 功能特点区域 -->
      <section class="features-section">
        <h2 class="section-title">核心功能</h2>
        <div class="features-grid">
          <div class="feature-card">
            <div class="feature-icon">
              <v-icon size="48" color="#1867FF">mdi-account-voice</v-icon>
            </div>
            <h3 class="feature-title">AI模拟面试</h3>
            <p class="feature-description">
              与AI面试官进行真实对话，体验不同行业、不同职位的面试场景
            </p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">
              <v-icon size="48" color="#1867FF">mdi-chart-bar</v-icon>
            </div>
            <h3 class="feature-title">能力评估分析</h3>
            <p class="feature-description">
              全方位评估您的面试表现，提供专业改进建议和数据分析
            </p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">
              <v-icon size="48" color="#1867FF">mdi-briefcase-search</v-icon>
            </div>
            <h3 class="feature-title">智能职位推荐</h3>
            <p class="feature-description">
              基于您的技能和经验，智能匹配最适合的职位和面试机会
            </p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">
              <v-icon size="48" color="#1867FF">mdi-book-open-variant</v-icon>
            </div>
            <h3 class="feature-title">面试题库</h3>
            <p class="feature-description">
              覆盖各行各业的海量面试题库，帮助您充分准备面试内容
            </p>
          </div>
        </div>
      </section>

      <!-- 用户评价区域 -->
      <section class="testimonials-section">
        <h2 class="section-title">用户评价</h2>
        <div class="testimonials-slider">
          <v-carousel
            hide-delimiters
            :show-arrows="false"
            height="320"
            cycle
            interval="5000"
            class="custom-carousel"
          >
            <v-carousel-item v-for="(testimonial, i) in testimonials" :key="i">
              <div class="testimonial-card">
                <div class="testimonial-content">
                  <div class="quote-icon">
                    <v-icon color="#1867FF" size="32">mdi-format-quote-open</v-icon>
                  </div>
                  <p class="testimonial-text">{{ testimonial.text }}</p>
                  <div class="testimonial-author">
                    <div class="author-avatar">
                      <img :src="testimonial.avatar" :alt="testimonial.name" />
                    </div>
                    <div class="author-info">
                      <h4 class="author-name">{{ testimonial.name }}</h4>
                      <p class="author-title">{{ testimonial.title }}</p>
                    </div>
                  </div>
                </div>
              </div>
            </v-carousel-item>
          </v-carousel>
        </div>
      </section>

      <!-- 数据统计区域 -->
      <section class="stats-section">
        <div class="stats-container">
          <div class="stat-item">
            <div class="stat-number">100,000+</div>
            <div class="stat-label">注册用户</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">500+</div>
            <div class="stat-label">企业合作伙伴</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">50,000+</div>
            <div class="stat-label">成功面试案例</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">98%</div>
            <div class="stat-label">用户满意度</div>
          </div>
        </div>
      </section>

      <!-- 开始使用区域 -->
      <section class="cta-section">
        <div class="cta-content">
          <h2 class="cta-title">准备好提升您的面试技能了吗？</h2>
          <p class="cta-description">
            立即注册，开始您的专业面试训练之旅
          </p>
          <router-link to="/register" class="cta-button">免费注册</router-link>
        </div>
      </section>
    </main>

    <!-- 页脚 -->
    <footer class="footer">
      <div class="footer-content">
        <div class="footer-section">
          <h3 class="footer-title">面试星途</h3>
          <p class="footer-description">
            多模态智能面试模拟与评估系统，助力求职者提升面试技能，开启职业新征程。
          </p>
        </div>
        <div class="footer-section">
          <h3 class="footer-title">快速链接</h3>
          <ul class="footer-links">
            <li><router-link to="/">首页</router-link></li>
            <li><router-link to="/features">功能介绍</router-link></li>
            <li><router-link to="/pricing">价格方案</router-link></li>
            <li><router-link to="/about">关于我们</router-link></li>
          </ul>
        </div>
        <div class="footer-section">
          <h3 class="footer-title">联系我们</h3>
          <ul class="footer-contact">
            <li><v-icon small color="#1867FF" class="mr-2">mdi-email</v-icon> contact@mianshixingtu.com</li>
            <li><v-icon small color="#1867FF" class="mr-2">mdi-phone</v-icon> 400-888-8888</li>
            <li><v-icon small color="#1867FF" class="mr-2">mdi-map-marker</v-icon> 北京市海淀区中关村科技园</li>
          </ul>
        </div>
        <div class="footer-section">
          <h3 class="footer-title">关注我们</h3>
          <div class="social-links">
            <a href="#" class="social-link"><v-icon color="white">mdi-wechat</v-icon></a>
            <a href="#" class="social-link"><v-icon color="white">mdi-sina-weibo</v-icon></a>
            <a href="#" class="social-link"><v-icon color="white">mdi-qqchat</v-icon></a>
          </div>
        </div>
      </div>
      <div class="footer-bottom">
        <p>&copy; {{ new Date().getFullYear() }} 面试星途 - 多模态智能面试模拟与评估系统 | 京ICP备XXXXXXXX号</p>
      </div>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'HomePage',
  data() {
    return {
      showMobileMenu: false,
      testimonials: [
        {
          text: "面试星途帮助我准备了一系列技术面试，AI模拟的面试官提出的问题非常专业，与实际面试几乎一致。通过系统的反馈，我明确了自己的优势和不足，最终成功获得了理想公司的offer！",
          name: "张明",
          title: "前端开发工程师",
          avatar: require('@/assets/images/avatars/1.png')
        },
        {
          text: "作为一名应届毕业生，我对面试非常紧张。面试星途的模拟面试让我能在舒适的环境中反复练习，系统给出的评估报告非常详细，帮助我有针对性地提升。现在我已经顺利入职梦想企业！",
          name: "李婷",
          title: "人力资源专员",
          avatar: require('@/assets/images/avatars/2.png')
        },
        {
          text: "我使用面试星途准备了管理岗位的面试，系统能够根据不同行业和职位调整面试内容和风格，非常智能。通过多次练习，我的表达更加自信清晰，成功晋升为部门经理！",
          name: "王强",
          title: "市场营销经理",
          avatar: require('@/assets/images/default-avatar.png')
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
    async logout() {
      try {
        // 使用Vuex action退出登录
        await this.$store.dispatch('user/fedLogout')

        // 显示退出成功消息
        this.$store.dispatch('snackbar/showMessage', {
          content: '已成功退出登录',
          color: 'success'
        })

        console.log('退出登录成功')
      } catch (error) {
        console.error('退出登录失败:', error)
        this.$store.dispatch('snackbar/showMessage', {
          content: '退出登录失败',
          color: 'error'
        })
      }
    },
    toggleMobileMenu() {
      this.showMobileMenu = !this.showMobileMenu
    }
  },
  mounted() {
    document.title = '面试星途 - 多模态智能面试模拟与评估系统';
  }
}
</script>

<style scoped>
/* 全局样式 */
.home-container {
  font-family: PingFangSC-Regular, 'PingFang SC', 'Microsoft YaHei', sans-serif;
  color: #333;
  line-height: 1.6;
  background-color: #fff;
}

/* 顶部导航栏 */
.home-container .header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background-color: rgba(255, 255, 255, 0.98);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  z-index: 100;
  padding: 0.8rem 0;
}

.home-container .header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.home-container .logo-container {
  display: flex;
  align-items: center;
}

.home-container .logo {
  height: 36px;
  margin-right: 10px;
}

.home-container .logo-text {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1B2B3D;  /* 讯飞星火深色文字 */
}

.home-container .nav-links {
  display: flex;
  gap: 2rem;
}

.home-container .nav-link {
  color: #1B2B3D;
  text-decoration: none;
  font-size: 1rem;
  font-weight: 500;
  transition: color 0.3s;
}

.home-container .nav-link:hover, .home-container .nav-link.active {
  color: #1867FF;  /* 讯飞星火主色调 */
}

.home-container .auth-buttons {
  display: flex;
  gap: 1rem;
}

.home-container .login-btn {
  color: #1867FF;  /* 讯飞星火主色调 */
  text-decoration: none;
  font-weight: 500;
  padding: 0.5rem 1.2rem;
  border-radius: 6px;
  transition: all 0.3s;
}

.home-container .login-btn:hover {
  background-color: rgba(24, 103, 255, 0.1);  /* 讯飞星火主色调带透明度 */
}

.home-container .register-btn {
  background-color: #1867FF;  /* 讯飞星火主色调 */
  color: white;
  text-decoration: none;
  font-weight: 500;
  padding: 0.5rem 1.2rem;
  border-radius: 6px;
  transition: all 0.3s;
}

.home-container .register-btn:hover {
  background-color: #0052D9;  /* 讯飞星火深蓝色 */
}

.home-container .user-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.home-container .welcome-text {
  color: #1B2B3D;
  font-weight: 500;
  font-size: 1rem;
}

.home-container .logout-btn {
  background-color: #f5f5f5;
  color: #666;
  border: 1px solid #ddd;
  padding: 0.5rem 1.2rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s;
}

.home-container .logout-btn:hover {
  background-color: #e0e0e0;
  color: #333;
}

.home-container .mobile-menu-btn {
  display: none;
  background: none;
  border: none;
  color: #1B2B3D;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.home-container .mobile-menu-btn:hover {
  background-color: rgba(24, 103, 255, 0.1);
}

/* 主要内容区 */
.home-container main {
  padding-top: 70px;
}

/* 英雄区域 */
.home-container .hero-section {
  background: linear-gradient(135deg, #F5F9FF 0%, #FFFFFF 100%);  /* 讯飞星火渐变背景 */
  padding: 5rem 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1200px;
  margin: 0 auto;
  border-radius: 0 0 20px 20px;  /* 讯飞星火圆角风格 */
  box-shadow: 0 10px 30px rgba(24, 103, 255, 0.05);  /* 讯飞星火阴影风格 */
}

.home-container .hero-content {
  max-width: 600px;
}

.home-container .hero-title {
  font-size: 2.8rem;
  font-weight: 600;
  color: #1B2B3D;  /* 讯飞星火深色文字 */
  line-height: 1.2;
  margin-bottom: 1.5rem;
  background: linear-gradient(135deg, #1867FF 0%, #0052D9 100%);  /* 讯飞星火标题渐变 */
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.home-container .hero-description {
  font-size: 1.1rem;
  color: #666666;  /* 讯飞星火次要文字颜色 */
  margin-bottom: 2.5rem;
  line-height: 1.7;
}

.home-container .hero-buttons {
  display: flex;
  gap: 1rem;
}

.home-container .try-now-btn {
  background: linear-gradient(135deg, #1867FF 0%, #0052D9 100%);  /* 讯飞星火按钮渐变 */
  color: white;
  text-decoration: none;
  font-weight: 500;
  padding: 0.8rem 2rem;
  border-radius: 6px;
  transition: all 0.3s;
  box-shadow: 0 4px 12px rgba(24, 103, 255, 0.2);
}

.home-container .try-now-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(24, 103, 255, 0.3);
}

.home-container .learn-more-btn {
  border: 1px solid #1867FF;  /* 讯飞星火主色调 */
  color: #1867FF;  /* 讯飞星火主色调 */
  text-decoration: none;
  font-weight: 500;
  padding: 0.8rem 2rem;
  border-radius: 6px;
  transition: all 0.3s;
  background-color: white;
}

.home-container .learn-more-btn:hover {
  background-color: rgba(24, 103, 255, 0.1);  /* 讯飞星火主色调带透明度 */
}

.home-container .hero-image {
  max-width: 500px;
}

.home-container .hero-image img {
  width: 100%;
  height: auto;
  border-radius: 20px;  /* 讯飞星火圆角风格 */
  box-shadow: 0 20px 30px rgba(0, 0, 0, 0.1);
}

/* 功能特点区域 */
.home-container .features-section {
  padding: 5rem 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.home-container .section-title {
  font-size: 2.2rem;
  font-weight: 700;
  color: #1B2B3D;  /* 讯飞星火深色文字 */
  text-align: center;
  margin-bottom: 3rem;
  position: relative;
  display: inline-block;
  left: 50%;
  transform: translateX(-50%);
}

.home-container .section-title::after {
  content: "";
  position: absolute;
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
  width: 60px;
  height: 4px;
  background: linear-gradient(135deg, #1867FF 0%, #0052D9 100%);  /* 讯飞星火渐变 */
  border-radius: 2px;
}

.home-container .features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
}

.home-container .feature-card {
  background-color: white;
  border-radius: 16px;  /* 讯飞星火圆角风格 */
  padding: 2rem;
  text-align: center;
  box-shadow: 0 4px 20px rgba(24, 103, 255, 0.08);  /* 讯飞星火阴影风格 */
  transition: all 0.3s;
  border: 1px solid rgba(24, 103, 255, 0.05);  /* 讯飞星火边框风格 */
}

.home-container .feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 30px rgba(24, 103, 255, 0.12);  /* 讯飞星火阴影风格 */
  border-color: rgba(24, 103, 255, 0.1);  /* 讯飞星火边框风格 */
}

.home-container .feature-icon {
  background-color: rgba(24, 103, 255, 0.1);  /* 讯飞星火主色调带透明度 */
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1.5rem;
  position: relative;
  overflow: hidden;
}

.home-container .feature-icon::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, rgba(24, 103, 255, 0.2) 0%, rgba(0, 82, 217, 0.2) 100%);  /* 讯飞星火渐变 */
  opacity: 0.7;
}

.home-container .feature-title {
  font-size: 1.3rem;
  font-weight: 600;
  color: #1B2B3D;  /* 讯飞星火深色文字 */
  margin-bottom: 1rem;
}

.home-container .feature-description {
  color: #666666;  /* 讯飞星火次要文字颜色 */
  font-size: 0.95rem;
}

/* 用户评价区域 */
.home-container .testimonials-section {
  background-color: #F5F9FF;  /* 讯飞星火浅蓝背景 */
  padding: 5rem 2rem;
  border-radius: 20px;  /* 讯飞星火圆角风格 */
  margin: 2rem;
}

.home-container .testimonials-slider {
  max-width: 800px;
  margin: 0 auto;
}

.home-container .testimonial-card {
  background-color: white;
  border-radius: 16px;  /* 讯飞星火圆角风格 */
  padding: 2rem;
  box-shadow: 0 4px 20px rgba(24, 103, 255, 0.08);  /* 讯飞星火阴影风格 */
  height: 100%;
  display: flex;
  align-items: center;
  border: 1px solid rgba(24, 103, 255, 0.05);  /* 讯飞星火边框风格 */
}

.home-container .testimonial-content {
  text-align: center;
}

.home-container .quote-icon {
  margin-bottom: 1.5rem;
  position: relative;
  display: inline-block;
}

.home-container .quote-icon::before {
  content: "";
  position: absolute;
  width: 40px;
  height: 40px;
  background-color: rgba(24, 103, 255, 0.1);  /* 讯飞星火主色调带透明度 */
  border-radius: 50%;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: -1;
}

.home-container .testimonial-text {
  font-size: 1.1rem;
  color: #4b5563;
  font-style: italic;
  line-height: 1.8;
  margin-bottom: 2rem;
}

.home-container .testimonial-author {
  display: flex;
  align-items: center;
  justify-content: center;
}

.home-container .author-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  overflow: hidden;
  margin-right: 1rem;
  border: 2px solid rgba(24, 103, 255, 0.2);  /* 讯飞星火边框风格 */
}

.home-container .author-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.home-container .author-name {
  font-weight: 600;
  color: #1B2B3D;  /* 讯飞星火深色文字 */
  margin-bottom: 0.2rem;
}

.home-container .author-title {
  color: #666666;  /* 讯飞星火次要文字颜色 */
  font-size: 0.9rem;
}

/* 数据统计区域 */
.home-container .stats-section {
  padding: 5rem 2rem;
  background: linear-gradient(135deg, #1867FF 0%, #0052D9 100%);  /* 讯飞星火渐变背景 */
  color: white;
  border-radius: 20px;  /* 讯飞星火圆角风格 */
  margin: 2rem;
  box-shadow: 0 10px 30px rgba(24, 103, 255, 0.2);  /* 讯飞星火阴影风格 */
}

.home-container .stats-container {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 2rem;
}

.home-container .stat-item {
  text-align: center;
  background-color: rgba(255, 255, 255, 0.1);  /* 讯飞星火半透明背景 */
  border-radius: 16px;  /* 讯飞星火圆角风格 */
  padding: 2rem;
  backdrop-filter: blur(5px);
  transition: all 0.3s;
}

.home-container .stat-item:hover {
  transform: translateY(-5px);
  background-color: rgba(255, 255, 255, 0.15);  /* 讯飞星火半透明背景 */
}

.home-container .stat-number {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.home-container .stat-label {
  font-size: 1.1rem;
  opacity: 0.9;
}

/* 开始使用区域 */
.home-container .cta-section {
  padding: 5rem 2rem;
  background-color: #F5F9FF;  /* 讯飞星火浅色背景 */
  border-radius: 20px;  /* 讯飞星火圆角风格 */
  margin: 2rem;
  position: relative;
  overflow: hidden;
}

.home-container .cta-section::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M11 18c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm48 25c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm-43-7c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm63 31c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM34 90c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm56-76c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM12 86c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm28-65c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm23-11c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-6 60c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm29 22c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zM32 63c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm57-13c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-9-21c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM60 91c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM35 41c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM12 60c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2z' fill='%231867FF' fill-opacity='0.05' fill-rule='evenodd'/%3E%3C/svg%3E") center center;
  opacity: 0.5;
}

.home-container .cta-content {
  max-width: 800px;
  margin: 0 auto;
  text-align: center;
  position: relative;
  z-index: 1;
}

.home-container .cta-title {
  font-size: 2.2rem;
  font-weight: 700;
  color: #1B2B3D;  /* 讯飞星火深色文字 */
  margin-bottom: 1rem;
  background: linear-gradient(135deg, #1867FF 0%, #0052D9 100%);  /* 讯飞星火标题渐变 */
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.home-container .cta-description {
  font-size: 1.1rem;
  color: #666666;  /* 讯飞星火次要文字颜色 */
  margin-bottom: 2rem;
}

.home-container .cta-button {
  background: linear-gradient(135deg, #1867FF 0%, #0052D9 100%);  /* 讯飞星火按钮渐变 */
  color: white;
  text-decoration: none;
  font-weight: 500;
  padding: 1rem 2.5rem;
  border-radius: 6px;
  transition: all 0.3s;
  display: inline-block;
  box-shadow: 0 4px 12px rgba(24, 103, 255, 0.2);
}

.home-container .cta-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(24, 103, 255, 0.3);
}

/* 页脚 */
.home-container .footer {
  background-color: #1B2B3D;  /* 讯飞星火深色背景 */
  color: white;
  padding: 4rem 2rem 1rem;
  border-radius: 20px 20px 0 0;  /* 讯飞星火圆角风格 */
  margin-top: 2rem;
  position: relative;
  overflow: hidden;
}

.home-container .footer::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23FFFFFF' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E") center center;
  opacity: 0.1;
}

.home-container .footer-content {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 3rem;
  margin-bottom: 3rem;
  position: relative;
  z-index: 1;
}

.home-container .footer-title {
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
  color: #1867FF;  /* 讯飞星火主色调 */
}

.home-container .footer-description {
  color: #d1d5db;
  font-size: 0.95rem;
  line-height: 1.7;
}

.home-container .footer-links, .home-container .footer-contact {
  list-style: none;
  padding: 0;
  margin: 0;
}

.home-container .footer-links li, .home-container .footer-contact li {
  margin-bottom: 0.8rem;
}

.home-container .footer-links a {
  color: #d1d5db;
  text-decoration: none;
  transition: color 0.3s;
  position: relative;
  padding-left: 12px;
}

.home-container .footer-links a::before {
  content: "";
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 4px;
  background-color: #1867FF;  /* 讯飞星火主色调 */
  border-radius: 50%;
  opacity: 0;
  transition: opacity 0.3s;
}

.home-container .footer-links a:hover {
  color: white;
}

.home-container .footer-links a:hover::before {
  opacity: 1;
}

.home-container .social-links {
  display: flex;
  gap: 1rem;
}

.home-container .social-link {
  background-color: rgba(255, 255, 255, 0.1);
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
  position: relative;
  overflow: hidden;
}

.home-container .social-link::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, rgba(24, 103, 255, 0.2) 0%, rgba(0, 82, 217, 0.2) 100%);  /* 讯飞星火渐变 */
  opacity: 0;
  transition: opacity 0.3s;
}

.home-container .social-link:hover {
  background-color: rgba(255, 255, 255, 0.2);
  transform: translateY(-3px);
}

.home-container .social-link:hover::before {
  opacity: 1;
}

.home-container .footer-bottom {
  text-align: center;
  padding-top: 2rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  color: #9ca3af;
  font-size: 0.9rem;
  position: relative;
  z-index: 1;
}

/* 响应式调整 */
@media (max-width: 992px) {
  .home-container .hero-section {
    flex-direction: column;
    text-align: center;
  }
  
  .home-container .hero-content {
    margin-bottom: 3rem;
  }
  
  .home-container .hero-buttons {
    justify-content: center;
  }
  
  .home-container .hero-title {
    font-size: 2.4rem;
  }
}

@media (max-width: 768px) {
  .home-container .nav-links {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: white;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    padding: 1rem;
    z-index: 1000;
  }

  .home-container .nav-links.hidden {
    display: none;
  }

  .home-container .mobile-menu-btn {
    display: block;
  }
  
  .home-container .hero-title {
    font-size: 2rem;
  }
  
  .home-container .section-title {
    font-size: 1.8rem;
  }
  
  .home-container .cta-title {
    font-size: 1.8rem;
  }
  
  .home-container .testimonials-section,
  .home-container .stats-section,
  .home-container .cta-section {
    margin: 1rem;
    border-radius: 16px;
  }
}

@media (max-width: 576px) {
  .home-container .header-content {
    padding: 0 1rem;
  }
  
  .home-container .logo-text {
    display: none;
  }
  
  .home-container .hero-section, .home-container .features-section, .home-container .testimonials-section, .home-container .stats-section, .home-container .cta-section {
    padding: 3rem 1rem;
  }
  
  .home-container .hero-title {
    font-size: 1.8rem;
  }
  
  .home-container .hero-description {
    font-size: 1rem;
  }
  
  .home-container .hero-buttons {
    flex-direction: column;
    gap: 1rem;
  }
  
  .home-container .try-now-btn, .home-container .learn-more-btn {
    width: 100%;
  }
  
  .home-container .footer-content {
    grid-template-columns: 1fr;
  }
  
  .home-container .testimonials-section,
  .home-container .stats-section,
  .home-container .cta-section {
    margin: 0.5rem;
    border-radius: 12px;
  }
}
</style> 