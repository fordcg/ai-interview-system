<template>
  <v-app dark>
    <v-main class="main-background">
      <!-- 调试信息 -->
      <v-alert
        v-if="false"
        type="info"
        outlined
        class="debug-info ma-4"
      >
        <h3>调试信息</h3>
        <p>当前路由: {{ $route.path }}</p>
        <p>登录状态: {{ isLoggedIn ? '已登录' : '未登录' }}</p>
        <p>用户名: {{ username || '无' }}</p>
        <div class="mt-2">
          <v-btn small color="primary" class="mr-2" @click="goToDashboard">
            转到仪表盘
          </v-btn>
          <v-btn small color="success" class="mr-2" @click="setDummyToken">
            设置临时Token
          </v-btn>
          <v-btn small color="error" @click="clearToken">
            清除Token
          </v-btn>
        </div>
      </v-alert>
      
      <router-view />
    </v-main>
    
    <!-- 全局消息提示 -->
    <v-snackbar
      v-model="snackbarShow"
      :color="snackbarColor"
      :timeout="snackbarTimeout"
      :multi-line="snackbarMultiLine"
    >
      {{ snackbarContent }}
      
      <template v-slot:action="{ attrs }">
        <v-btn
          text
          v-bind="attrs"
          @click="hideSnackbar"
        >
          关闭
        </v-btn>
      </template>
    </v-snackbar>
    
    <!-- 全局加载指示器 -->
    <v-overlay :value="loading.show" :opacity="0.7" z-index="9999">
      <v-progress-circular
        indeterminate
        size="64"
        color="primary"
      ></v-progress-circular>
      <div class="mt-4 white--text">{{ loading.message }}</div>
    </v-overlay>
  </v-app>
</template>

<script>
import { mapState, mapGetters, mapActions } from 'vuex'

export default {
  name: 'App',
  created() {
    // 导入全局CSS
    require('./assets/css/main.css')
  },
  computed: {
    ...mapState({
      loading: state => state.loading || { show: false }
    }),
    ...mapGetters({
      snackbarShow: 'snackbar/show',
      snackbarContent: 'snackbar/content',
      snackbarColor: 'snackbar/color',
      snackbarTimeout: 'snackbar/timeout',
      snackbarMultiLine: 'snackbar/multiLine'
    }),
    isLoggedIn() {
      return !!localStorage.getItem('token')
    },
    username() {
      return localStorage.getItem('username')
    }
  },
  methods: {
    ...mapActions({
      hideSnackbar: 'snackbar/hideMessage'
    }),
    goToDashboard() {
      this.$router.push('/dashboard')
    },
    setDummyToken() {
      localStorage.setItem('token', 'dummy-token-for-debug')
      localStorage.setItem('username', 'debug-user')
      localStorage.setItem('userId', '1')
      this.$router.go(0) // 刷新页面
    },
    clearToken() {
      localStorage.removeItem('token')
      localStorage.removeItem('username')
      localStorage.removeItem('userId')
      this.$router.go(0) // 刷新页面
    }
  }
}
</script>

<style>
/* 全局样式 */
html, body {
  font-family: 'Noto Sans SC', 'Roboto', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  overflow-x: hidden;
}

.main-background {
  background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
  background-attachment: fixed;
  min-height: 100vh;
  padding: 0;
}

/* 自定义滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: rgba(241, 241, 241, 0.1);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: rgba(189, 189, 189, 0.5);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(158, 158, 158, 0.7);
}

/* 全局过渡效果 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter,
.fade-leave-to {
  opacity: 0;
}

.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s;
}

.slide-enter,
.slide-leave-to {
  transform: translateX(-20px);
  opacity: 0;
}

/* 常用辅助类 */
.cursor-pointer {
  cursor: pointer;
}

.text-truncate {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.flex-center {
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 渐变文字 */
.gradient-text {
  background: linear-gradient(to right, #4cc9f0, #4361ee);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  position: relative;
  display: inline-block;
}

/* 卡片样式覆盖 */
.v-card {
  background: #FFFFFF !important;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 15px;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  color: #333333;
}

.v-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1) !important;
  background: #FFFFFF !important;
}

/* 按钮样式覆盖 */
.v-btn.primary {
  background: linear-gradient(45deg, #4361ee, #4895ef) !important;
  box-shadow: 0 5px 15px rgba(67, 97, 238, 0.4);
  border-radius: 50px !important;
}

.v-btn.primary:hover {
  background: linear-gradient(45deg, #3f37c9, #4361ee) !important;
  box-shadow: 0 8px 20px rgba(67, 97, 238, 0.6);
  transform: translateY(-3px);
}

/* 容器样式 */
.container {
  max-width: 1400px;
  margin: 0 auto;
}

/* 列表样式覆盖 */
.v-list {
  border-radius: 8px;
}

/* 输入框样式覆盖 */
.v-text-field--outlined fieldset {
  border-color: rgba(255, 255, 255, 0.2) !important;
}

.v-text-field--outlined:hover fieldset {
  border-color: rgba(255, 255, 255, 0.3) !important;
}

.theme--dark.v-text-field--outlined:not(.v-input--is-focused):not(.v-input--has-state) > .v-input__control > .v-input__slot fieldset {
  border-color: rgba(255, 255, 255, 0.2) !important;
}

/* 表格样式覆盖 */
.v-data-table {
  background: rgba(255, 255, 255, 0.05) !important;
  border-radius: 15px;
  overflow: hidden;
}

.v-data-table th {
  background: rgba(0, 0, 0, 0.3) !important;
}

.v-data-table tr:hover {
  background: rgba(255, 255, 255, 0.1) !important;
}

/* 菜单样式覆盖 */
.v-menu__content {
  border-radius: 8px !important;
  overflow: hidden;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3) !important;
}
</style> 