<template>
  <div class="immersive-interview-page">
    <!-- 准备阶段 -->
    <div v-if="!interviewStarted" class="preparation-screen">
      <div class="preparation-content">
        <div class="preparation-header">
          <h1 class="preparation-title">沉浸式模拟面试</h1>
          <p class="preparation-subtitle">专业的语音面试练习平台，提升您的面试技能</p>
        </div>
        
        <div class="preparation-info">
          <div class="info-card">
            <v-icon size="48" color="primary" class="mb-4">mdi-microphone</v-icon>
            <h3>语音面试</h3>
            <p>通过语音回答问题，模拟真实面试场景，提升您的面试表现</p>
          </div>

          <div class="info-card">
            <v-icon size="48" color="primary" class="mb-4">mdi-video</v-icon>
            <h3>视频录制</h3>
            <p>可选择开启摄像头录制面试过程，便于后续回顾和改进</p>
          </div>
        </div>
        
        <div class="preparation-settings">
          <v-card class="settings-card">
            <v-card-title>面试设置</v-card-title>
            <v-card-text>
              <v-row>
                <v-col cols="12">
                  <v-text-field
                    v-model="interviewTitle"
                    label="面试标题"
                    outlined
                    dense
                  ></v-text-field>
                </v-col>
              </v-row>

              <v-row>
                <v-col cols="12">
                  <v-switch
                    v-model="enableCamera"
                    label="启用摄像头"
                    color="primary"
                  ></v-switch>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </div>
        
        <div class="preparation-questions" v-if="questions.length > 0">
          <v-card class="questions-card">
            <v-card-title>面试问题预览 ({{ questions.length }} 题)</v-card-title>
            <v-card-text>
              <v-list dense>
                <v-list-item v-for="(question, index) in questions.slice(0, 3)" :key="question.id">
                  <v-list-item-content>
                    <v-list-item-title>{{ index + 1 }}. {{ question.text }}</v-list-item-title>
                  </v-list-item-content>
                </v-list-item>
                <v-list-item v-if="questions.length > 3">
                  <v-list-item-content>
                    <v-list-item-title class="text--secondary">
                      ... 还有 {{ questions.length - 3 }} 个问题
                    </v-list-item-title>
                  </v-list-item-content>
                </v-list-item>
              </v-list>
            </v-card-text>
          </v-card>
        </div>
        
        <div class="preparation-actions">
          <v-btn
            color="primary"
            large
            :loading="isStarting"
            @click="startImmersiveInterview"
            class="start-btn"
          >
            <v-icon left>mdi-play</v-icon>
            开始沉浸式面试
          </v-btn>
          
          <v-btn
            outlined
            large
            @click="goBack"
            class="back-btn"
          >
            <v-icon left>mdi-arrow-left</v-icon>
            返回
          </v-btn>
        </div>
        
        <div class="preparation-tips">
          <v-alert
            type="info"
            outlined
            class="tips-alert"
          >
            <div class="tips-content">
              <h4>使用提示</h4>
              <ul>
                <li>确保您的麦克风权限已开启</li>
                <li>如需录制视频，请开启摄像头权限</li>
                <li>建议在安静的环境中进行面试</li>
                <li>您可以随时暂停或结束面试</li>
              </ul>
            </div>
          </v-alert>
        </div>
      </div>
    </div>
    
    <!-- 沉浸式面试组件 -->
    <ImmersiveInterview
      v-if="interviewStarted"
      :interview-questions="questions"
      :interview-title="interviewTitle"
      :auto-start="true"
      @interview-ended="handleInterviewEnded"
      @fullscreen-exited="handleFullscreenExited"
    />
    
    <!-- 面试结束对话框 -->
    <v-dialog v-model="showEndDialog" max-width="600" persistent>
      <v-card>
        <v-card-title class="text-h5">
          <v-icon color="success" class="mr-2">mdi-check-circle</v-icon>
          面试已结束
        </v-card-title>
        <v-card-text>
          <div class="interview-summary">
            <div class="summary-item">
              <strong>完成问题：</strong>{{ interviewResult.questionsAnswered }} / {{ interviewResult.totalQuestions }} 个
            </div>
            <div class="summary-item" v-if="interviewResult.duration">
              <strong>面试时长：</strong>{{ formatDuration(interviewResult.duration) }}
            </div>
            <div class="summary-item" v-if="interviewResult.sessionId">
              <strong>会话ID：</strong>{{ interviewResult.sessionId }}
            </div>
          </div>
          <v-divider class="my-3"></v-divider>
          <p class="text-center">感谢您参与本次AI模拟面试！</p>
          <p class="text-center text-caption">您的表现已被记录，可以查看详细报告了解面试情况。</p>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" @click="viewReport">查看报告</v-btn>
          <v-btn text @click="returnToHome">返回首页</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    
    <!-- 错误提示 -->
    <v-snackbar v-model="showError" color="error" top>
      {{ errorMessage }}
      <template v-slot:action="{ attrs }">
        <v-btn text v-bind="attrs" @click="showError = false">关闭</v-btn>
      </template>
    </v-snackbar>
  </div>
</template>

<script>
import ImmersiveInterview from '@/components/interview/ImmersiveInterview.vue'
import { getInterviewDataByPosition, filterQuestionsByDifficulty } from '@/data/testInterviewData'

export default {
  name: 'ImmersiveInterviewPage',
  components: {
    ImmersiveInterview
  },
  data() {
    return {
      // 面试状态
      interviewStarted: false,
      isStarting: false,
      
      // 面试设置
      interviewTitle: '模拟面试',
      enableCamera: true,
      
      // 问题数据
      questions: [],
      
      // 面试结果
      showEndDialog: false,
      interviewResult: {
        questionsAnswered: 0,
        totalQuestions: 0
      },
      
      // 错误处理
      showError: false,
      errorMessage: ''
    }
  },
  created() {
    this.loadInterviewData()
  },
  methods: {
    loadInterviewData() {
      // 从路由参数或API加载面试数据
      const { interviewId } = this.$route.params
      const { jobName, mode, difficulty, testMode, title } = this.$route.query

      // 检查是否为测试模式
      if (testMode === 'true' || interviewId === 'quick-test') {
        this.loadTestData()
        return
      }

      // 优先检查 localStorage 中的 deepseekInterviewQuestions
      if (this.loadDeepSeekQuestions()) {
        console.log('已从 localStorage 加载 DeepSeek 面试问题')
        return
      }

      if (jobName) {
        this.interviewTitle = `${jobName} - 模拟面试`
      }

      if (title) {
        this.interviewTitle = decodeURIComponent(title)
      }

      // 加载问题数据
      this.loadQuestions(interviewId, { mode, difficulty })
    },

    loadTestData() {
      // 测试模式：从路由参数加载配置
      const { jobName, difficulty, title, enableCamera } = this.$route.query

      // 设置面试标题
      if (title) {
        this.interviewTitle = decodeURIComponent(title)
      } else if (jobName) {
        this.interviewTitle = `${jobName} - 模拟面试`
      }

      // 应用测试配置
      if (enableCamera !== undefined) {
        this.enableCamera = enableCamera === 'true'
      }

      // 加载测试问题数据
      try {
        const positionKey = this.getPositionKey(jobName)
        const interviewData = getInterviewDataByPosition(positionKey)
        const filteredQuestions = filterQuestionsByDifficulty(interviewData.questions, difficulty || 'medium')

        this.questions = filteredQuestions
        console.log('测试模式：已加载', this.questions.length, '个问题')

      } catch (error) {
        console.error('加载测试数据失败:', error)
        this.showErrorMessage('加载测试数据失败')
      }
    },

    loadDeepSeekQuestions() {
      try {
        // 从 localStorage 获取 deepseekInterviewQuestions
        const deepseekData = localStorage.getItem('deepseekInterviewQuestions')
        if (!deepseekData) {
          console.log('localStorage 中未找到 deepseekInterviewQuestions')
          return false
        }

        const parsedData = JSON.parse(deepseekData)
        console.log('从 localStorage 获取到的 DeepSeek 数据:', parsedData)

        // 验证数据结构 - 处理嵌套的 questions 结构
        let questionsArray = null

        if (parsedData.questions && Array.isArray(parsedData.questions)) {
          // 直接的 questions 数组
          questionsArray = parsedData.questions
        } else if (parsedData.questions && parsedData.questions.questions && Array.isArray(parsedData.questions.questions)) {
          // 嵌套的 questions.questions 数组
          questionsArray = parsedData.questions.questions
        }

        if (!questionsArray || questionsArray.length === 0) {
          console.error('DeepSeek 数据格式无效：未找到有效的 questions 数组')
          return false
        }

        // 设置面试标题
        if (parsedData.job_position || parsedData.target_position) {
          const position = parsedData.job_position || parsedData.target_position
          this.interviewTitle = `${position} - 深度面试`
        }

        // 转换问题格式
        this.questions = questionsArray.map((question, index) => ({
          id: index + 1,
          text: question.text,
          type: question.type || 'open',
          focus: question.focus,
          metadata: {
            originalType: question.type,
            focus: question.focus
          }
        }))

        console.log('已转换 DeepSeek 问题:', this.questions.length, '个问题')
        console.log('第一个问题:', this.questions[0])
        console.log('所有问题:', this.questions.map(q => q.text))
        return true

      } catch (error) {
        console.error('加载 DeepSeek 面试问题失败:', error)
        return false
      }
    },

    getPositionKey(jobName) {
      // 将职位名称映射到数据键
      const positionMap = {
        '前端工程师': 'frontend',
        '后端工程师': 'backend',
        '产品经理': 'product',
        '数据分析师': 'dataAnalyst'
      }
      return positionMap[jobName] || 'general'
    },

    async loadQuestions(interviewId, options = {}) {
      try {
        // 这里应该调用API获取问题
        // const response = await getInterviewQuestions(interviewId, options)
        // this.questions = response.data.questions
        
        // 临时使用模拟数据
        this.questions = [
          { id: 1, text: '请简单介绍一下您自己。', type: 'open' },
          { id: 2, text: '您为什么想要这个职位？', type: 'open' },
          { id: 3, text: '您最大的优势是什么？', type: 'open' },
          { id: 4, text: '描述一个您克服困难的经历。', type: 'open' },
          { id: 5, text: '您对我们公司了解多少？', type: 'open' },
          { id: 6, text: '您的职业规划是什么？', type: 'open' },
          { id: 7, text: '您如何处理工作压力？', type: 'open' },
          { id: 8, text: '您有什么问题要问我们吗？', type: 'open' }
        ]
        
      } catch (error) {
        console.error('加载问题失败:', error)
        this.showErrorMessage('加载面试问题失败')
      }
    },
    
    async startImmersiveInterview() {
      try {
        this.isStarting = true

        // 检查是否为测试模式
        const { testMode, skipPermissionCheck } = this.$route.query
        const isTestMode = testMode === 'true' || skipPermissionCheck === 'true'

        if (!isTestMode) {
          // 检查浏览器支持
          if (!this.checkBrowserSupport()) {
            this.showErrorMessage('您的浏览器不支持全屏模式或音频API')
            return
          }

          // 预检查权限
          await this.checkPermissions()
        } else {
          console.log('测试模式：跳过权限检查')
        }

        // 开始面试
        this.interviewStarted = true

      } catch (error) {
        console.error('启动面试失败:', error)
        this.showErrorMessage('启动面试失败: ' + error.message)
      } finally {
        this.isStarting = false
      }
    },
    
    checkBrowserSupport() {
      // 检查全屏API支持
      const fullscreenSupported = !!(
        document.fullscreenEnabled ||
        document.webkitFullscreenEnabled ||
        document.msFullscreenEnabled
      )
      
      // 检查音频API支持
      const audioSupported = !!(
        window.AudioContext ||
        window.webkitAudioContext
      )
      
      // 检查媒体设备API支持
      const mediaSupported = !!(
        navigator.mediaDevices &&
        navigator.mediaDevices.getUserMedia
      )
      
      return fullscreenSupported && audioSupported && mediaSupported
    },
    
    async checkPermissions() {
      try {
        // 检查麦克风权限
        const audioStream = await navigator.mediaDevices.getUserMedia({ audio: true })
        audioStream.getTracks().forEach(track => track.stop())
        
        // 如果启用摄像头，检查摄像头权限
        if (this.enableCamera) {
          const videoStream = await navigator.mediaDevices.getUserMedia({ video: true })
          videoStream.getTracks().forEach(track => track.stop())
        }
        
      } catch (error) {
        throw new Error('无法获取音频或视频权限，请检查浏览器设置')
      }
    },

    formatDuration(seconds) {
      const mins = Math.floor(seconds / 60)
      const secs = seconds % 60
      return `${mins}分${secs}秒`
    },

    handleInterviewEnded(result) {
      this.interviewResult = result
      this.showEndDialog = true
      this.interviewStarted = false
    },
    
    handleFullscreenExited() {
      // 用户主动退出全屏
      this.interviewStarted = false
    },
    
    viewReport() {
      this.showEndDialog = false
      // 跳转到报告页面，使用一个固定的ID（因为我们主要依赖localStorage数据）
      this.$router.push('/interview/report/analysis')
    },
    
    returnToHome() {
      this.showEndDialog = false
      this.$router.push('/interview')
    },
    
    goBack() {
      this.$router.go(-1)
    },
    
    showErrorMessage(message) {
      this.errorMessage = message
      this.showError = true
    }
  }
}
</script>

<style scoped>
.immersive-interview-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.preparation-screen {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px;
}

.preparation-content {
  max-width: 1200px;
  width: 100%;
}

.preparation-header {
  text-align: center;
  margin-bottom: 48px;
}

.preparation-title {
  font-size: 48px;
  font-weight: 300;
  color: #2c3e50;
  margin-bottom: 16px;
}

.preparation-subtitle {
  font-size: 20px;
  color: #7f8c8d;
  margin: 0;
}

.preparation-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 32px;
  margin-bottom: 48px;
}

.info-card {
  text-align: center;
  padding: 32px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.info-card h3 {
  font-size: 24px;
  font-weight: 500;
  color: #2c3e50;
  margin-bottom: 16px;
}

.info-card p {
  color: #7f8c8d;
  line-height: 1.6;
  margin: 0;
}

.preparation-settings {
  margin-bottom: 32px;
}

.settings-card {
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.preparation-questions {
  margin-bottom: 32px;
}

.questions-card {
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.preparation-actions {
  display: flex;
  justify-content: center;
  gap: 24px;
  margin-bottom: 32px;
}

.start-btn {
  min-width: 200px;
  height: 56px;
  border-radius: 28px;
  font-size: 16px;
  font-weight: 500;
  text-transform: none;
}

.back-btn {
  min-width: 120px;
  height: 56px;
  border-radius: 28px;
  font-size: 16px;
  font-weight: 500;
  text-transform: none;
}

/* 面试摘要样式 */
.interview-summary {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
  margin: 16px 0;
}

.summary-item {
  margin-bottom: 8px;
  font-size: 14px;
}

.summary-item:last-child {
  margin-bottom: 0;
}

.preparation-tips {
  max-width: 600px;
  margin: 0 auto;
}

.tips-alert {
  border-radius: 12px;
}

.tips-content h4 {
  margin-bottom: 12px;
  color: #2c3e50;
}

.tips-content ul {
  margin: 0;
  padding-left: 20px;
}

.tips-content li {
  margin-bottom: 8px;
  color: #7f8c8d;
  line-height: 1.5;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .preparation-title {
    font-size: 36px;
  }
  
  .preparation-subtitle {
    font-size: 18px;
  }
  
  .preparation-info {
    grid-template-columns: 1fr;
    gap: 24px;
  }
  
  .preparation-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .start-btn,
  .back-btn {
    width: 100%;
    max-width: 300px;
  }
}
</style>
