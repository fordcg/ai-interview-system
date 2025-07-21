<template>
  <div class="min-h-screen w-full flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
    <div class="w-full max-w-4xl overflow-hidden rounded-2xl flex bg-white shadow-xl">
      <!-- 左侧 - 背景点阵 -->
      <div class="hidden md:block w-1/2 h-[600px] relative overflow-hidden border-r border-gray-100">
        <div class="absolute inset-0 bg-gradient-to-br from-blue-50 to-indigo-100">
          <div class="relative w-full h-full overflow-hidden">
            <canvas ref="mapCanvas" class="absolute inset-0 w-full h-full"></canvas>
          </div>
          
          <!-- Logo和文字覆盖 -->
          <div class="absolute inset-0 flex flex-col items-center justify-center p-8 z-10">
            <div class="mb-6">
              <div class="h-16 w-16 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-blue-200">
                <v-icon color="white" size="36">mdi-star-circle</v-icon>
              </div>
            </div>
            <h2 class="text-3xl font-bold mb-4 text-center text-blue-600">
              面试星途
            </h2>
            <p class="text-md text-center text-gray-700 max-w-xs font-medium">
              多模态智能面试模拟与评估系统
            </p>
          </div>
        </div>
      </div>
      
      <!-- 右侧 - 注册表单 -->
      <div class="w-full md:w-1/2 p-8 md:p-12 flex flex-col justify-center bg-white">
        <div>
          <h1 class="text-2xl md:text-3xl font-bold mb-2 text-gray-800">创建账号</h1>
          <p class="text-gray-500 mb-8">注册成为面试星途用户</p>
          
          <form class="space-y-6" @submit.prevent="handleRegister">
            <div>
              <label for="username" class="block text-sm font-medium text-gray-700 mb-1.5">
                账号 <span class="text-blue-500">*</span>
              </label>
              <v-text-field
                id="username"
                v-model="username"
                placeholder="请输入账号"
                outlined
                dense
                hide-details="auto"
                class="login-input bg-white border-gray-300 rounded-md text-input-lg"
                height="48"
                :rules="usernameRules"
              ></v-text-field>
            </div>
            
            <div>
              <label for="email" class="block text-sm font-medium text-gray-700 mb-1.5">
                邮箱 <span class="text-blue-500">*</span>
              </label>
              <v-text-field
                id="email"
                v-model="email"
                type="email"
                placeholder="请输入邮箱"
                outlined
                dense
                hide-details="auto"
                class="login-input bg-white border-gray-300 rounded-md text-input-lg"
                height="48"
                :rules="emailRules"
              ></v-text-field>
            </div>
            
            <div>
              <label for="password" class="block text-sm font-medium text-gray-700 mb-1.5">
                密码 <span class="text-blue-500">*</span>
              </label>
              <div class="relative">
                <v-text-field
                  id="password"
                  v-model="password"
                  :type="isPasswordVisible ? 'text' : 'password'"
                  placeholder="请输入密码"
                  outlined
                  dense
                  hide-details="auto"
                  class="login-input bg-white border-gray-300 rounded-md text-input-lg"
                  :append-icon="isPasswordVisible ? 'mdi-eye-off' : 'mdi-eye'"
                  @click:append="isPasswordVisible = !isPasswordVisible"
                  height="48"
                  :rules="passwordRules"
                ></v-text-field>
              </div>
            </div>
            
            <div>
              <label for="confirmPassword" class="block text-sm font-medium text-gray-700 mb-1.5">
                确认密码 <span class="text-blue-500">*</span>
              </label>
              <div class="relative">
                <v-text-field
                  id="confirmPassword"
                  v-model="confirmPassword"
                  :type="isConfirmPasswordVisible ? 'text' : 'password'"
                  placeholder="请再次输入密码"
                  outlined
                  dense
                  hide-details="auto"
                  class="login-input bg-white border-gray-300 rounded-md text-input-lg"
                  :append-icon="isConfirmPasswordVisible ? 'mdi-eye-off' : 'mdi-eye'"
                  @click:append="isConfirmPasswordVisible = !isConfirmPasswordVisible"
                  height="48"
                  :rules="confirmPasswordRules"
                ></v-text-field>
              </div>
            </div>
            
            <div>
              <v-checkbox
                v-model="agreeTerms"
                color="primary"
                hide-details
                class="mt-2"
              >
                <template v-slot:label>
                  <span class="text-sm text-gray-700">
                    我已阅读并同意 
                    <a href="#" class="text-blue-600 hover:text-blue-700">服务条款</a> 
                    和 
                    <a href="#" class="text-blue-600 hover:text-blue-700">隐私政策</a>
                  </span>
                </template>
              </v-checkbox>
            </div>
            
            <div class="pt-4">
              <v-btn
                block
                color="primary"
                height="50"
                class="bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-lg transition-all duration-300 shadow-hover text-base font-medium"
                elevation="2"
                type="submit"
                :loading="registerLoading"
                :disabled="!isFormValid || !agreeTerms"
              >
                <span class="flex items-center justify-center">
                  注册
                  <v-icon right class="ml-2">mdi-arrow-right</v-icon>
                </span>
              </v-btn>
            </div>
            
            <div class="text-center mt-6">
              <span class="text-gray-600 text-base">已有账号？</span>
              <router-link to="/login" class="text-blue-600 hover:text-blue-700 text-base transition-colors ml-1">
                立即登录
              </router-link>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { register } from '@/api/user'

export default {
  name: 'Register',
  data() {
    return {
      username: '',
      email: '',
      password: '',
      confirmPassword: '',
      isPasswordVisible: false,
      isConfirmPasswordVisible: false,
      registerLoading: false,
      agreeTerms: false,
      
      // 表单验证规则
      usernameRules: [
        v => !!v || '账号不能为空',
        v => (v && v.length >= 3) || '账号至少需要3个字符'
      ],
      emailRules: [
        v => !!v || '邮箱不能为空',
        v => /.+@.+\..+/.test(v) || '请输入有效的邮箱地址'
      ],
      passwordRules: [
        v => !!v || '密码不能为空',
        v => (v && v.length >= 6) || '密码至少需要6个字符'
      ]
    }
  },
  computed: {
    confirmPasswordRules() {
      return [
        v => !!v || '确认密码不能为空',
        v => v === this.password || '两次输入的密码不一致'
      ]
    },
    isFormValid() {
      return this.username && 
             this.username.length >= 3 && 
             this.email && 
             /.+@.+\..+/.test(this.email) && 
             this.password && 
             this.password.length >= 6 && 
             this.confirmPassword && 
             this.confirmPassword === this.password;
    }
  },
  mounted() {
    this.$nextTick(() => {
      this.initDotMap();
    });
  },
  methods: {
    async handleRegister() {
      if (!this.isFormValid || !this.agreeTerms) {
        this.$store.dispatch('snackbar/showMessage', {
          content: '请完成所有必填项并同意服务条款',
          color: 'error'
        });
        return;
      }
      
      this.registerLoading = true;
      
      try {
        const response = await register({
          username: this.username,
          email: this.email,
          password: this.password
        });
        
        if (response.code !== 200) {
          throw new Error(response.message || '注册失败');
        }
        
        // 显示注册成功消息
        this.$store.dispatch('snackbar/showMessage', {
          content: '注册成功，请登录',
          color: 'success'
        });
        
        // 跳转到登录页面
        this.$router.push('/login');
      } catch (error) {
        console.error('注册失败:', error);
        this.$store.dispatch('snackbar/showMessage', {
          content: error.message || '注册失败，请稍后再试',
          color: 'error'
        });
      } finally {
        this.registerLoading = false;
      }
    },
    
    initDotMap() {
      const canvas = this.$refs.mapCanvas;
      if (!canvas) return;
      
      const ctx = canvas.getContext('2d');
      if (!ctx) return;
      
      // 确保canvas尺寸正确
      const updateCanvasSize = () => {
        const container = canvas.parentElement;
        if (!container) return;
        
        const { width, height } = container.getBoundingClientRect();
        canvas.width = width;
        canvas.height = height;
        
        // 重新生成点
        dots = generateDots(width, height);
      };
      
      // 监听尺寸变化
      const resizeObserver = new ResizeObserver(() => {
        updateCanvasSize();
      });
      
      resizeObserver.observe(canvas.parentElement);
      
      // 设置点
      const generateDots = (width, height) => {
        const dots = [];
        const gap = 12; // 设置间距为12px
        const dotRadius = 1; // 设置点大小为1px
        
        // 计算行列数
        const cols = Math.ceil(width / gap);
        const rows = Math.ceil(height / gap);
        
        // 设置边距，四周保持空白
        const margin = Math.min(width, height) * 0.15; // 边距为宽高中较小值的15%
        
        // 在中央区域均匀分布点
        for (let i = 0; i < cols; i++) {
          for (let j = 0; j < rows; j++) {
            const x = i * gap;
            const y = j * gap;
            
            // 检查是否在边距范围内（四周空白区域）
            if (x < margin || x > width - margin || y < margin || y > height - margin) {
              continue; // 跳过边缘区域
            }
            
            // 随机决定是否显示点，创建星空效果
            // 提高阈值到0.7，减少点的数量，增加空白感
            if (Math.random() > 0.7) {
              dots.push({
                x,
                y,
                radius: dotRadius,
                opacity: Math.random() * 0.5 + 0.2 // 最小不透明度为0.2
              });
            }
          }
        }
        console.log(`Generated ${dots.length} dots for canvas ${width}x${height} with margin ${margin}px and probability 30%`);
        return dots;
      };
      
      // 路线设置
      const routes = [
        {
          start: { x: 100, y: 150, delay: 0 },
          end: { x: 200, y: 80, delay: 2 },
          color: '#2563eb'
        },
        {
          start: { x: 200, y: 80, delay: 2 },
          end: { x: 260, y: 120, delay: 4 },
          color: '#2563eb'
        },
        {
          start: { x: 50, y: 50, delay: 1 },
          end: { x: 150, y: 180, delay: 3 },
          color: '#2563eb'
        },
        {
          start: { x: 280, y: 60, delay: 0.5 },
          end: { x: 180, y: 180, delay: 2.5 },
          color: '#2563eb'
        }
      ];
      
      let dots = [];
      let startTime = Date.now();
      let animationFrameId;
      
      // 初始化尺寸
      updateCanvasSize();
      
      function animate() {
        const width = canvas.width;
        const height = canvas.height;
        
        // 清除画布
        ctx.clearRect(0, 0, width, height);
        
        // 绘制点
        dots.forEach(dot => {
          ctx.beginPath();
          ctx.arc(dot.x, dot.y, dot.radius, 0, Math.PI * 2);
          ctx.fillStyle = `rgba(37, 99, 235, ${dot.opacity})`;
          ctx.fill();
        });
        
        // 绘制路线
        const currentTime = (Date.now() - startTime) / 1000;
        
        routes.forEach(route => {
          const elapsed = currentTime - route.start.delay;
          if (elapsed <= 0) return;
          
          const duration = 3;
          const progress = Math.min(elapsed / duration, 1);
          
          const x = route.start.x + (route.end.x - route.start.x) * progress;
          const y = route.start.y + (route.end.y - route.start.y) * progress;
          
          // 绘制路线
          ctx.beginPath();
          ctx.moveTo(route.start.x, route.start.y);
          ctx.lineTo(x, y);
          ctx.strokeStyle = route.color;
          ctx.lineWidth = 1.5;
          ctx.stroke();
          
          // 绘制起点
          ctx.beginPath();
          ctx.arc(route.start.x, route.start.y, 3, 0, Math.PI * 2);
          ctx.fillStyle = route.color;
          ctx.fill();
          
          // 绘制移动点
          ctx.beginPath();
          ctx.arc(x, y, 3, 0, Math.PI * 2);
          ctx.fillStyle = '#3b82f6';
          ctx.fill();
          
          // 添加移动点的发光效果
          ctx.beginPath();
          ctx.arc(x, y, 6, 0, Math.PI * 2);
          ctx.fillStyle = 'rgba(59, 130, 246, 0.4)';
          ctx.fill();
          
          // 如果路线完成，绘制终点
          if (progress === 1) {
            ctx.beginPath();
            ctx.arc(route.end.x, route.end.y, 3, 0, Math.PI * 2);
            ctx.fillStyle = route.color;
            ctx.fill();
          }
        });
        
        // 如果所有路线都完成，重置动画
        if (currentTime > 15) {
          startTime = Date.now();
        }
        
        animationFrameId = requestAnimationFrame(animate);
      }
      
      animate();
      
      return () => {
        cancelAnimationFrame(animationFrameId);
        resizeObserver.disconnect();
      };
    }
  }
}
</script>

<style scoped>
/* 基本样式 */
.bg-gradient-to-br {
  background: linear-gradient(to bottom right, var(--from-color), var(--to-color));
}

.from-blue-50 {
  --from-color: #eff6ff;
}

.to-indigo-100 {
  --to-color: #e0e7ff;
}

.text-gray-800 {
  color: #1f2937;
}

.text-gray-500 {
  color: #6b7280;
}

.text-gray-600 {
  color: #4b5563;
}

.text-gray-700 {
  color: #374151;
}

.text-blue-600 {
  color: #2563eb;
}

.text-blue-500 {
  color: #3b82f6;
}

.bg-gradient-to-r {
  background: linear-gradient(to right, var(--from-color), var(--to-color));
}

.from-blue-500 {
  --from-color: #3b82f6;
}

.to-indigo-600 {
  --to-color: #4f46e5;
}

.bg-white {
  background-color: white;
}

.bg-gray-50 {
  background-color: #f9fafb;
}

.border-gray-100 {
  border-color: #f3f4f6;
}

.border-gray-200 {
  border-color: #e5e7eb;
}

.border-gray-300 {
  border-color: #d1d5db;
}

/* 布局和尺寸 */
.min-h-screen {
  min-height: 100vh;
}

.w-full {
  width: 100%;
}

.h-full {
  height: 100%;
}

.max-w-4xl {
  max-width: 56rem;
}

.h-\[600px\] {
  height: 600px;
}

.w-1\/2 {
  width: 50%;
}

.p-4 {
  padding: 1rem;
}

.p-8 {
  padding: 2rem;
}

.p-10 {
  padding: 2.5rem;
}

.px-2 {
  padding-left: 0.5rem;
  padding-right: 0.5rem;
}

.py-2 {
  padding-top: 0.5rem;
  padding-bottom: 0.5rem;
}

.pt-2 {
  padding-top: 0.5rem;
}

.p-3 {
  padding: 0.75rem;
}

.mb-1 {
  margin-bottom: 0.25rem;
}

.mb-2 {
  margin-bottom: 0.5rem;
}

.mb-6 {
  margin-bottom: 1.5rem;
}

.mb-8 {
  margin-bottom: 2rem;
}

.mt-6 {
  margin-top: 1.5rem;
}

.my-6 {
  margin-top: 1.5rem;
  margin-bottom: 1.5rem;
}

.ml-2 {
  margin-left: 0.5rem;
}

.space-y-5 {
  & > * + * {
    margin-top: 1.25rem;
  }
}

/* Flexbox和Grid */
.flex {
  display: flex;
}

.hidden {
  display: none;
}

.items-center {
  align-items: center;
}

.justify-center {
  justify-content: center;
}

.flex-col {
  flex-direction: column;
}

.gap-2 {
  gap: 0.5rem;
}

/* 定位 */
.relative {
  position: relative;
}

.absolute {
  position: absolute;
}

.inset-0 {
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
}

.z-10 {
  z-index: 10;
}

/* 文字样式 */
.text-2xl {
  font-size: 1.5rem;
}

.text-3xl {
  font-size: 1.875rem;
}

.text-sm {
  font-size: 0.875rem;
}

.font-bold {
  font-weight: 700;
}

.font-medium {
  font-weight: 500;
}

.text-center {
  text-align: center;
}

.text-transparent {
  color: transparent;
}

.bg-clip-text {
  background-clip: text;
  -webkit-background-clip: text;
}

.block {
  display: block;
}

/* 边框和阴影 */
.border {
  border-width: 1px;
  border-style: solid;
}

.border-r {
  border-right-width: 1px;
  border-right-style: solid;
}

.border-t {
  border-top-width: 1px;
  border-top-style: solid;
}

.rounded-2xl {
  border-radius: 1rem;
}

.rounded-full {
  border-radius: 9999px;
}

.rounded-lg {
  border-radius: 0.5rem;
}

.rounded-md {
  border-radius: 0.375rem;
}

.shadow-xl {
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.shadow-lg {
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

.shadow-sm {
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
}

.shadow-blue-200 {
  box-shadow: 0 0 15px rgba(59, 130, 246, 0.3);
}

.shadow-hover:hover {
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
  transform: translateY(-1px);
}

/* 动画和过渡 */
.transition-all {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 150ms;
}

.duration-300 {
  transition-duration: 300ms;
}

.transition-colors {
  transition-property: color, background-color, border-color, text-decoration-color, fill, stroke;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 150ms;
}

/* 状态 */
.hover\:bg-gray-100:hover {
  background-color: #f3f4f6;
}

.hover\:text-blue-700:hover {
  color: #1d4ed8;
}

.overflow-hidden {
  overflow: hidden;
}

/* 自定义输入框样式 */
.login-input :deep(.v-input__slot) {
  background-color: white !important;
  border: 1px solid #d1d5db !important;
}

.login-input :deep(.v-text-field__slot input) {
  color: #1f2937 !important;
  font-weight: 500 !important;
}

.login-input :deep(.v-text-field__slot input::placeholder) {
  color: #9ca3af !important;
  opacity: 1 !important;
}

/* 媒体查询 */
@media (min-width: 768px) {
  .md\:block {
    display: block;
  }
  
  .md\:w-1\/2 {
    width: 50%;
  }
  
  .md\:text-3xl {
    font-size: 1.875rem;
  }
  
  .md\:p-10 {
    padding: 2.5rem;
  }
}
</style> 