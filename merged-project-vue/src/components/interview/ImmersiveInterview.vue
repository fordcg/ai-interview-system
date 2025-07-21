<template>
  <div class="immersive-interview" :class="{ 'fullscreen-active': isFullscreen }">
    <!-- 全屏背景 -->
    <div class="immersive-background"></div>

    <!-- 主要内容区域 -->
    <div class="interview-content">
      <!-- 顶部问题显示区域 -->
      <div class="top-question-area" v-show="showUI">
        <div class="current-question" v-if="currentQuestion">
          <h3>{{ currentQuestion.text }}</h3>
        </div>
        <div class="ai-message" v-else-if="currentAIMessage">
          <h3>{{ currentAIMessage }}</h3>
        </div>
        <div class="ai-thinking" v-else-if="aiThinking">
          <span class="dot"></span>
          <span class="dot"></span>
          <span class="dot"></span>
        </div>
      </div>

      <!-- 主布局 -->
      <div class="main-interview-layout">
        <!-- 中央：音频可视化区域 -->
        <div class="visualization-area">
          <ParticleSystem
            :audio-stream="audioStream"
            :width="visualizerSize"
            :height="visualizerSize"
            :color-scheme="'white'"
            @audio-levels="handleAudioLevels"
            class="visualizer"
          />
        </div>


      </div>

      <!-- 右下角摄像头区域 -->
      <div class="bottom-right-camera">
        <!-- 表情分析结果显示在摄像头上方 -->
        <div class="emotion-text-bottom" v-if="cameraEnabled && showEmotionOverlay">
          {{ getEmotionText(currentEmotion) }}
        </div>

        <div class="camera-container-bottom">
          <video
            v-show="!imageCaptured && cameraEnabled"
            ref="userVideo"
            :width="180"
            :height="135"
            autoplay
            muted
            class="user-video-bottom"
          ></video>

          <!-- 摄像头未开启时的占位符 -->
          <div class="camera-placeholder-bottom" v-if="!cameraEnabled">
            <v-icon size="24" color="grey lighten-1">mdi-video-off</v-icon>
            <v-btn x-small color="primary" @click="startUserCamera" class="mt-1">开启</v-btn>
          </div>
        </div>
      </div>

      <!-- 用户回答显示区域 -->
      <div class="user-response-area" v-show="showUI && userResponse">
        <div class="user-response">
          <h4>您的回答</h4>
          <p>{{ userResponse }}</p>
        </div>
      </div>

      <!-- 底部控制栏 -->
      <div class="bottom-controls" v-show="showUI">
        <!-- 左侧区域 -->
        <div class="left-controls">
          <!-- 实时语音识别显示 -->
          <div v-if="isRecording && recognizedText" class="recognition-text">
            <p>{{ recognizedText }}</p>
          </div>
        </div>

        <!-- 中央区域 - 录音按钮 -->
        <div class="center-controls">
          <v-btn
            :color="isRecording ? 'error' : 'primary'"
            :loading="isProcessing"
            @click="toggleRecording"
            class="record-btn"
            fab
            large
          >
            <v-icon>{{ isRecording ? 'mdi-stop' : 'mdi-microphone' }}</v-icon>
          </v-btn>
        </div>

        <!-- 右侧区域 - 面试控制按钮 -->
        <div class="right-controls">
          <v-btn
            color="warning"
            outlined
            @click="endInterview"
            class="end-interview-btn"
          >
            <v-icon left>mdi-stop</v-icon>
            结束面试
          </v-btn>
        </div>
        
        <!-- 面试控制按钮暂时隐藏，保持居中布局 -->
        <div class="interview-controls" style="display: none;">
          <v-btn outlined @click="previousQuestion" :disabled="currentQuestionIndex === 0">
            <v-icon left>mdi-chevron-left</v-icon>
            上一题
          </v-btn>
          <v-btn outlined @click="nextQuestion" :disabled="currentQuestionIndex >= totalQuestions - 1">
            下一题
            <v-icon right>mdi-chevron-right</v-icon>
          </v-btn>
          <v-btn color="warning" outlined @click="endInterview">
            结束面试
          </v-btn>
        </div>
      </div>
    </div>
    
    <!-- 加载遮罩 -->
    <div class="loading-overlay" v-if="isLoading">
      <v-progress-circular indeterminate size="64" color="white"></v-progress-circular>
      <p class="loading-text">{{ loadingText }}</p>
    </div>
    
    <!-- 快捷键提示 -->
    <div class="shortcuts-help" v-show="showUI && showShortcuts">
      <div class="shortcuts-content">
        <h4>快捷键</h4>
        <div class="shortcut-list">
          <div class="shortcut-item">
            <kbd>ESC</kbd>
            <span>退出全屏</span>
          </div>
          <div class="shortcut-item">
            <kbd>空格</kbd>
            <span>开始/停止录音</span>
          </div>
          <div class="shortcut-item">
            <kbd>Ctrl + H</kbd>
            <span>显示/隐藏界面</span>
          </div>
          <div class="shortcut-item">
            <kbd>Ctrl + ←/→</kbd>
            <span>上一题/下一题</span>
          </div>
          <div class="shortcut-item">
            <kbd>Ctrl + 1/2/3</kbd>
            <span>切换可视化效果</span>
          </div>
        </div>
        <v-btn small text @click="showShortcuts = false" class="close-shortcuts">
          <v-icon small>mdi-close</v-icon>
        </v-btn>
      </div>
    </div>

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
import ParticleSystem from './audio-visualizers/ParticleSystem.vue'
import { analyzeFace } from '@/api/face_detection'

export default {
  name: 'ImmersiveInterview',
  components: {
    ParticleSystem
  },
  props: {
    interviewQuestions: {
      type: Array,
      default: () => []
    },
    interviewTitle: {
      type: String,
      default: '模拟面试'
    },
    autoStart: {
      type: Boolean,
      default: true
    }
  },
  data() {
    return {
      // 全屏状态
      isFullscreen: false,
      showUI: true,
      showShortcuts: false,
      
      // 面试状态
      currentQuestionIndex: 0,
      totalQuestions: 0,
      isInterviewActive: false,
      
      // 音频相关
      audioStream: null,
      isRecording: false,
      isListening: false,
      isAISpeaking: false,
      isProcessing: false,
      userResponse: '',
      currentVolume: 0,
      audioLevels: {
        bass: 0,
        mid: 0,
        treble: 0
      },

      // 录音相关
      mediaRecorder: null,
      audioChunks: [],
      recordingStartTime: null,
      recordingDuration: 0,
      recordingTimer: null,

      // 语音识别
      speechRecognition: null,
      recognizedText: '',
      isRecognitionActive: false,
      
      // 可视化设置
      colorScheme: 'white',
      
      // 摄像头
      cameraEnabled: false,
      cameraStream: null,
      cameraWidth: 200,
      cameraHeight: 150,
      imageCaptured: false,

      // 表情识别相关
      currentEmotion: 'neutral',
      emotionConfidence: 0,
      showEmotionOverlay: true,
      emotionDetectionInterval: null,
      emotionDetectionActive: false,

      // AI面试官相关
      currentAIMessage: '',
      aiThinking: false,
      interviewPosition: '软件工程师',

      // SparkOS数字人交互
      sessionId: '',
      interviewStatus: 'idle', // idle, connecting, in_progress, ended
      isConnecting: false,
      messages: [],
      questionCount: 0,
      maxQuestions: 5,
      currentStage: 'introduction',
      duration: 0,
      durationTimer: null,
      responsePoller: null,

      // UI状态
      isLoading: false,
      loadingText: '正在初始化...',
      showError: false,
      errorMessage: '',
      
      // 问题数据
      questions: [
        { id: 1, text: '请简单介绍一下您自己。', type: 'open' },
        { id: 2, text: '您为什么想要这个职位？', type: 'open' },
        { id: 3, text: '您最大的优势是什么？', type: 'open' },
        { id: 4, text: '描述一个您克服困难的经历。', type: 'open' },
        { id: 5, text: '您对我们公司了解多少？', type: 'open' }
      ]
    }
  },
  computed: {
    currentQuestion() {
      return this.questions[this.currentQuestionIndex] || null
    },
    progressPercentage() {
      return this.totalQuestions > 0 ? (this.currentQuestionIndex / this.totalQuestions) * 100 : 0
    },

    visualizerSize() {
      return Math.min(window.innerWidth, window.innerHeight) * 0.4
    },
    cameraSize() {
      return {
        width: 200,
        height: 150
      }
    },
    aiStatusText() {
      if (this.isAISpeaking) return '正在提问...'
      if (this.isListening) return '正在聆听...'
      if (this.isProcessing) return '正在分析...'
      return '等待回答'
    }
  },
  watch: {
    isAISpeaking() {
      this.updateVisualizerState()
    },
    isRecording() {
      this.updateVisualizerState()
    },
    isListening() {
      this.updateVisualizerState()
    }
  },
  async mounted() {
    await this.initializeInterview()
  },
  beforeDestroy() {
    this.cleanup()
  },
  methods: {
    async initializeInterview() {
      try {
        this.isLoading = true
        this.loadingText = '正在进入沉浸模式...'

        // 尝试进入全屏（如果失败则继续）
        try {
          await this.enterFullscreen()
        } catch (fullscreenError) {
          console.warn('全屏模式失败，继续非全屏模式:', fullscreenError)
          this.isFullscreen = false
        }

        // 初始化问题
        this.initQuestions()

        // 请求音频权限
        this.loadingText = '正在获取音频权限...'
        await this.initAudio()

        // 请求摄像头权限（可选）
        if (this.autoStart) {
          this.loadingText = '正在获取摄像头权限...'
          await this.initCamera()
        }

        this.isLoading = false
        this.isInterviewActive = true

        // 初始化语音识别
        this.initSpeechRecognition()

        // 开始面试
        this.startInterview()

      } catch (error) {
        console.error('初始化失败:', error)
        this.showErrorMessage('初始化失败: ' + error.message)
        this.isLoading = false
      }
    },
    
    initQuestions() {
      if (this.interviewQuestions && this.interviewQuestions.length > 0) {
        this.questions = this.interviewQuestions
        // 如果传入了自定义问题，调整最大问题数量
        this.maxQuestions = Math.max(this.maxQuestions, this.interviewQuestions.length)
      }
      this.totalQuestions = this.questions.length
      console.log('初始化问题完成:', {
        questionsCount: this.questions.length,
        maxQuestions: this.maxQuestions,
        hasCustomQuestions: !!(this.interviewQuestions && this.interviewQuestions.length > 0)
      })
    },
    
    async enterFullscreen() {
      try {
        const element = this.$el
        if (element.requestFullscreen) {
          await element.requestFullscreen()
        } else if (element.webkitRequestFullscreen) {
          await element.webkitRequestFullscreen()
        } else if (element.msRequestFullscreen) {
          await element.msRequestFullscreen()
        }
        this.isFullscreen = true
        
        // 监听全屏状态变化
        document.addEventListener('fullscreenchange', this.handleFullscreenChange)
        document.addEventListener('webkitfullscreenchange', this.handleFullscreenChange)

        // 监听ESC键退出
        document.addEventListener('keydown', this.handleKeyDown)
        
      } catch (error) {
        console.error('进入全屏失败:', error)
        throw new Error('无法进入全屏模式')
      }
    },
    
    async initAudio() {
      try {
        this.audioStream = await navigator.mediaDevices.getUserMedia({
          audio: {
            echoCancellation: true,
            noiseSuppression: true,
            autoGainControl: true
          }
        })
      } catch (error) {
        console.error('音频初始化失败:', error)
        throw new Error('无法获取音频权限')
      }
    },
    
    async initCamera() {
      try {
        this.cameraStream = await navigator.mediaDevices.getUserMedia({
          video: {
            width: { ideal: this.cameraWidth },
            height: { ideal: this.cameraHeight }
          }
        })

        const video = this.$refs.userVideo
        if (video) {
          video.srcObject = this.cameraStream
          this.cameraEnabled = true

          // 开始表情检测
          this.startEmotionDetection()
        }
      } catch (error) {
        console.warn('摄像头初始化失败:', error)
        // 摄像头失败不阻止面试继续
      }
    },
    
    startInterview() {
      // 启动讯飞TTS数字人面试
      this.startXunfeiInterview()
    },
    
    async speakQuestion(questionText) {
      const text = questionText || (this.currentQuestion && this.currentQuestion.text)
      if (!text) return

      console.log('开始语音合成:', text)

      // 设置AI说话状态
      this.isAISpeaking = true

      try {
        // 调用后端讯飞TTS API
        const response = await this.$axios.post('/interview/local/test_tts', {
          text: text
        })

        if (response.data.success) {
          console.log('讯飞TTS合成成功')
          // 讯飞TTS在后端直接播放，前端显示说话状态
          this.simulateSpeaking(text)
        } else {
          console.warn('讯飞TTS API 调用失败，使用模拟模式')
          this.simulateSpeaking(text)
        }
      } catch (error) {
        console.error('讯飞TTS API 错误:', error)
        // 回退到模拟模式
        this.simulateSpeaking(text)
      }
    },

    playTTSAudio(audioUrl) {
      try {
        const audio = new Audio(audioUrl)
        audio.play().then(() => {
          console.log('TTS 音频播放开始')
        }).catch(error => {
          console.error('TTS 音频播放失败:', error)
          this.simulateSpeaking('音频播放失败')
        })

        audio.onended = () => {
          this.isAISpeaking = false
          this.isListening = true
          console.log('TTS 音频播放完成')
        }

        audio.onerror = () => {
          console.error('音频播放错误')
          this.simulateSpeaking('音频播放错误')
        }
      } catch (error) {
        console.error('创建音频对象失败:', error)
        this.simulateSpeaking('音频创建失败')
      }
    },

    simulateSpeaking(questionText) {
      // 模拟说话时长（根据文本长度）
      const speakingDuration = Math.max(2000, questionText.length * 100)

      setTimeout(() => {
        this.isAISpeaking = false
        this.isListening = true
        console.log('模拟语音播放完成')
      }, speakingDuration)
    },
    
    toggleRecording() {
      if (this.isRecording) {
        this.stopRecording()
      } else {
        this.startRecording()
      }
    },


    
    async startRecording() {
      try {
        if (!this.audioStream) {
          throw new Error('音频流未初始化')
        }

        this.isRecording = true
        this.isListening = true
        this.audioChunks = []
        this.recordingStartTime = Date.now()

        // 创建媒体录制器
        this.mediaRecorder = new MediaRecorder(this.audioStream, {
          mimeType: 'audio/webm;codecs=opus'
        })

        this.mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            this.audioChunks.push(event.data)
          }
        }

        this.mediaRecorder.onstop = () => {
          this.processRecording()
        }

        this.mediaRecorder.start(100) // 每100ms收集一次数据

        // 开始录音计时
        this.startRecordingTimer()

        // 启动语音识别
        this.startSpeechRecognition()

      } catch (error) {
        console.error('开始录音失败:', error)
        this.showErrorMessage('录音失败: ' + error.message)
        this.isRecording = false
        this.isListening = false
      }
    },

    stopRecording() {
      if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
        this.mediaRecorder.stop()
      }

      this.isRecording = false
      this.isListening = false
      this.stopRecordingTimer()
      this.stopSpeechRecognition()
    },

    processRecording() {
      this.isProcessing = true

      try {
        // 创建音频Blob
        const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' })

        // 创建音频URL用于播放
        const audioUrl = URL.createObjectURL(audioBlob)

        // 使用识别的文本作为回答
        // 验证语音内容：至少包含2个字符，避免误识别的单个字符或标点
        const speechText = this.recognizedText.trim()
        const hasValidSpeech = speechText.length >= 2 && !/^[。，！？\s]*$/.test(speechText)

        if (hasValidSpeech) {
          this.userResponse = speechText
        } else {
          this.userResponse = '未能识别到语音内容，请重新录音。'
        }

        // 添加用户回答到消息列表
        this.addUserMessage(this.userResponse)

        // 模拟处理延迟
        setTimeout(() => {
          this.isProcessing = false

          // 发出回答记录事件
          this.$emit('answer-recorded', {
            text: this.userResponse,
            audioBlob: audioBlob,
            audioUrl: audioUrl,
            duration: this.recordingDuration,
            hasValidSpeech: hasValidSpeech
          })

          // 处理回答并进入下一题
          if (this.interviewStatus === 'in_progress' && hasValidSpeech) {
            // 异步分析回答，不阻塞下一题
            this.analyzeAnswerWithDeepSeek(this.userResponse).catch(error => {
              console.error('DeepSeek分析失败，但不影响面试继续:', error)
            })

            // 检查是否是最后一题
            const totalQuestions = this.questions.length
            const maxQuestions = Math.min(this.maxQuestions, totalQuestions)

            if (this.questionCount >= maxQuestions) {
              // 最后一题，等待分析完成后结束面试
              setTimeout(() => {
                this.endXunfeiInterview()
              }, 3000)
            } else {
              // 不是最后一题，直接进入下一题
              setTimeout(() => {
                this.askNextQuestion()
              }, 2000)
            }
          } else if (!hasValidSpeech) {
            // 如果没有识别到语音，提示用户重新录音
            console.log('未识别到有效语音，请用户重新录音')
            this.showSpeechRetryHint()
          }
        }, 1000)

      } catch (error) {
        console.error('处理录音失败:', error)
        this.showErrorMessage('处理录音失败')
        this.isProcessing = false
      }
    },

    startRecordingTimer() {
      this.recordingDuration = 0
      this.recordingTimer = setInterval(() => {
        this.recordingDuration = Math.floor((Date.now() - this.recordingStartTime) / 1000)
      }, 1000)
    },

    stopRecordingTimer() {
      if (this.recordingTimer) {
        clearInterval(this.recordingTimer)
        this.recordingTimer = null
      }
    },

    initSpeechRecognition() {
      if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
        this.speechRecognition = new SpeechRecognition()

        this.speechRecognition.continuous = true
        this.speechRecognition.interimResults = true
        this.speechRecognition.lang = 'zh-CN'

        // 累积的最终文本
        let accumulatedFinalText = ''

        this.speechRecognition.onresult = (event) => {
          let finalTranscript = ''
          let interimTranscript = ''

          for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript
            if (event.results[i].isFinal) {
              finalTranscript += transcript
            } else {
              interimTranscript += transcript
            }
          }

          // 累积最终文本
          if (finalTranscript) {
            accumulatedFinalText += finalTranscript
          }

          // 显示累积的最终文本 + 当前临时文本
          this.recognizedText = accumulatedFinalText + interimTranscript
        }

        this.speechRecognition.onend = () => {
          console.log('语音识别结束，当前录音状态:', this.isRecording)
          // 如果用户仍在录音，自动重启语音识别
          if (this.isRecording && this.isRecognitionActive) {
            console.log('自动重启语音识别')
            setTimeout(() => {
              if (this.isRecording && this.speechRecognition) {
                try {
                  this.speechRecognition.start()
                } catch (error) {
                  console.error('重启语音识别失败:', error)
                }
              }
            }, 100)
          } else {
            this.isRecognitionActive = false
          }
        }

        this.speechRecognition.onerror = (event) => {
          console.error('语音识别错误:', event.error)
          // 如果是网络错误或其他可恢复错误，尝试重启
          if (event.error === 'network' || event.error === 'aborted') {
            if (this.isRecording) {
              setTimeout(() => {
                if (this.isRecording && this.speechRecognition) {
                  try {
                    this.speechRecognition.start()
                  } catch (error) {
                    console.error('错误后重启语音识别失败:', error)
                  }
                }
              }, 1000)
            }
          }
        }

        // 重置累积文本的方法
        this.resetAccumulatedText = () => {
          accumulatedFinalText = ''
          this.recognizedText = ''
        }
      }
    },

    startSpeechRecognition() {
      if (this.speechRecognition && !this.isRecognitionActive) {
        try {
          // 重置累积文本
          if (this.resetAccumulatedText) {
            this.resetAccumulatedText()
          }
          this.speechRecognition.start()
          this.isRecognitionActive = true
          console.log('语音识别已启动')
        } catch (error) {
          console.error('启动语音识别失败:', error)
        }
      }
    },

    stopSpeechRecognition() {
      if (this.speechRecognition && this.isRecognitionActive) {
        try {
          this.speechRecognition.stop()
          this.isRecognitionActive = false
        } catch (error) {
          console.error('停止语音识别失败:', error)
        }
      }
    },

    showSpeechRetryHint() {
      // 显示重新录音提示
      this.currentAIMessage = '未能识别到您的语音，请重新录音回答问题。'

      // 3秒后清除提示
      setTimeout(() => {
        this.currentAIMessage = ''
      }, 3000)
    },



    async analyzeAnswerWithDeepSeek(answer) {
      try {
        // 获取当前问题
        const currentQuestionText = this.getCurrentQuestionText()
        if (!currentQuestionText) {
          console.warn('无法获取当前问题，跳过 DeepSeek 分析')
          return
        }

        // 获取职位信息
        const jobPosition = this.getJobPosition()

        console.log('开始 DeepSeek 分析:', {
          question: currentQuestionText,
          answer: answer,
          jobPosition: jobPosition
        })

        // 调用 DeepSeek API 分析回答
        const response = await this.$axios.post('/deepseek/analyze/interview', {
          question: currentQuestionText,
          answer: answer,
          job_position: jobPosition
        })

        if (response.data && response.data.code === 0) {
          console.log('DeepSeek 分析成功:', response.data.data)

          // 保存分析结果到 localStorage
          this.saveAnalysisToLocalStorage(currentQuestionText, answer, response.data.data)
        } else {
          console.error('DeepSeek 分析失败:', response.data)
        }

      } catch (error) {
        console.error('DeepSeek 分析出错:', error)
        // 分析失败不影响面试继续进行
      }
    },

    getCurrentQuestionText() {
      // 获取当前问题文本
      if (this.questions && this.questions.length > 0) {
        const questionIndex = this.questionCount - 1
        if (questionIndex >= 0 && questionIndex < this.questions.length) {
          return this.questions[questionIndex].text
        }
      }
      return null
    },

    getJobPosition() {
      // 优先从 localStorage 中的 deepseekInterviewQuestions 获取职位信息
      try {
        const deepseekData = localStorage.getItem('deepseekInterviewQuestions')
        if (deepseekData) {
          const parsedData = JSON.parse(deepseekData)
          if (parsedData.job_position) {
            return parsedData.job_position
          }
          if (parsedData.target_position) {
            return parsedData.target_position
          }
        }
      } catch (error) {
        console.warn('获取 deepseekInterviewQuestions 职位信息失败:', error)
      }

      // 备选方案：从面试标题获取职位信息
      if (this.interviewTitle && this.interviewTitle.includes(' - ')) {
        return this.interviewTitle.split(' - ')[0]
      }

      return '通用职位'
    },

    saveAnalysisToLocalStorage(question, answer, analysis) {
      try {
        // 获取现有的分析结果
        const existingAnalyses = JSON.parse(localStorage.getItem('interviewAnalyses') || '[]')

        // 添加新的分析结果
        const newAnalysis = {
          question: question,
          answer: answer,
          analysis: analysis,
          timestamp: new Date().toISOString(),
          questionIndex: this.questionCount - 1,
          sessionId: this.sessionId
        }

        existingAnalyses.push(newAnalysis)

        // 保存到 localStorage
        localStorage.setItem('interviewAnalyses', JSON.stringify(existingAnalyses))

        console.log('分析结果已保存到 localStorage:', newAnalysis)

      } catch (error) {
        console.error('保存分析结果到 localStorage 失败:', error)
      }
    },
    
    nextQuestion() {
      if (this.currentQuestionIndex < this.totalQuestions - 1) {
        this.currentQuestionIndex++
        this.userResponse = ''
        this.speakQuestion()
      }
    },
    
    previousQuestion() {
      if (this.currentQuestionIndex > 0) {
        this.currentQuestionIndex--
        this.userResponse = ''
        this.speakQuestion()
      }
    },
    
    toggleCamera() {
      this.cameraEnabled = !this.cameraEnabled
      if (!this.cameraEnabled && this.cameraStream) {
        this.cameraStream.getTracks().forEach(track => track.stop())
        this.cameraStream = null
      } else if (this.cameraEnabled && !this.cameraStream) {
        this.initCamera()
      }
    },
    
    toggleUI() {
      this.showUI = !this.showUI
    },
    
    exitFullscreen() {
      if (document.exitFullscreen) {
        document.exitFullscreen()
      } else if (document.webkitExitFullscreen) {
        document.webkitExitFullscreen()
      } else if (document.msExitFullscreen) {
        document.msExitFullscreen()
      }
    },
    
    endInterview() {
      this.$emit('interview-ended', {
        questionsAnswered: this.currentQuestionIndex + 1,
        totalQuestions: this.totalQuestions
      })
      this.exitFullscreen()
    },
    
    handleFullscreenChange() {
      this.isFullscreen = !!(document.fullscreenElement || document.webkitFullscreenElement)
      if (!this.isFullscreen) {
        this.$emit('fullscreen-exited')
      }
    },

    handleKeyDown(event) {
      switch (event.key) {
        case 'Escape':
          // ESC键退出全屏或结束面试
          if (this.isFullscreen) {
            this.exitFullscreen()
          }
          break
        case ' ':
          // 空格键切换录音状态
          if (!this.isProcessing) {
            event.preventDefault()
            this.toggleRecording()
          }
          break
        case 'h':
        case 'H':
          // H键切换UI显示
          if (event.ctrlKey || event.metaKey) {
            event.preventDefault()
            this.toggleUI()
          }
          break
        case 'ArrowLeft':
          // 左箭头键上一题
          if (event.ctrlKey || event.metaKey) {
            event.preventDefault()
            this.previousQuestion()
          }
          break
        case 'ArrowRight':
          // 右箭头键下一题
          if (event.ctrlKey || event.metaKey) {
            event.preventDefault()
            this.nextQuestion()
          }
          break
        case '1':
        case '2':
        case '3':
          // 数字键切换可视化效果
          if (event.ctrlKey || event.metaKey) {
            event.preventDefault()
            const index = parseInt(event.key) - 1
            if (index >= 0 && index < this.visualizers.length) {
              this.currentVisualizerIndex = index
            }
          }
          break
      }
    },
    
    handleVolumeChange(volume) {
      this.currentVolume = volume
    },
    
    handleAudioLevels(levels) {
      this.audioLevels = levels
    },

    // 音频可视化优化方法
    updateVisualizerState() {
      // 保持白色粒子效果
      this.colorScheme = 'white'
    },



    showErrorMessage(message) {
      this.errorMessage = message
      this.showError = true
    },

    // 表情识别相关方法
    async startUserCamera() {
      try {
        this.cameraStream = await navigator.mediaDevices.getUserMedia({
          video: {
            width: { ideal: this.cameraWidth },
            height: { ideal: this.cameraHeight }
          }
        })

        const video = this.$refs.userVideo
        if (video) {
          video.srcObject = this.cameraStream
          this.cameraEnabled = true

          // 开始表情检测
          this.startEmotionDetection()
        }
      } catch (error) {
        console.error('摄像头启动失败:', error)
        this.showErrorMessage('无法启动摄像头: ' + error.message)
      }
    },

    startEmotionDetection() {
      if (this.emotionDetectionActive) return

      this.emotionDetectionActive = true
      this.emotionDetectionInterval = setInterval(() => {
        this.detectCurrentEmotion()
      }, 2000) // 每2秒检测一次表情
    },

    stopEmotionDetection() {
      if (this.emotionDetectionInterval) {
        clearInterval(this.emotionDetectionInterval)
        this.emotionDetectionInterval = null
        this.emotionDetectionActive = false
      }
    },

    detectCurrentEmotion() {
      if (!this.cameraEnabled || !this.$refs.userVideo) return

      // 创建一个临时canvas来捕获当前视频帧
      const video = this.$refs.userVideo
      const canvas = document.createElement('canvas')
      const context = canvas.getContext('2d')

      canvas.width = video.videoWidth
      canvas.height = video.videoHeight
      context.drawImage(video, 0, 0, canvas.width, canvas.height)

      const imageData = canvas.toDataURL('image/jpeg', 0.7)

      // 调用表情分析API
      this.analyzeCurrentEmotion(imageData)
    },

    async analyzeCurrentEmotion(imageData) {
      try {
        // 调用真实的表情分析API
        const response = await analyzeFace({
          image: imageData
        })

        if (response.success && response.data && response.data.expressions && response.data.expressions.length > 0) {
          // 获取第一个检测到的人脸的表情
          const faceExpression = response.data.expressions[0]
          // 获取英文表情标签
          const enEmotion = faceExpression.details.en_emotion

          console.log('检测到表情:', enEmotion, '置信度:', faceExpression.confidence)

          // 更新当前表情
          this.currentEmotion = enEmotion
          this.emotionConfidence = faceExpression.confidence

        } else if (response.success && response.data && response.data.face_count === 0) {
          console.log('未检测到人脸')
          this.currentEmotion = 'neutral'
          this.emotionConfidence = 0
        }
      } catch (error) {
        console.error('表情分析失败:', error)
        // 出错时默认为中性表情
        this.currentEmotion = 'neutral'
        this.emotionConfidence = 0
      }
    },

    getEmotionIcon(emotion) {
      const iconMap = {
        happiness: 'mdi-emoticon-happy',
        sadness: 'mdi-emoticon-sad',
        anger: 'mdi-emoticon-angry',
        surprise: 'mdi-emoticon-excited',
        neutral: 'mdi-emoticon-neutral',
        fear: 'mdi-emoticon-dead',
        disgust: 'mdi-emoticon-sick',
        // 保持向后兼容
        happy: 'mdi-emoticon-happy',
        sad: 'mdi-emoticon-sad',
        angry: 'mdi-emoticon-angry',
        surprised: 'mdi-emoticon-excited',
        focused: 'mdi-eye',
        confident: 'mdi-thumb-up'
      }
      return iconMap[emotion] || 'mdi-emoticon-neutral'
    },

    getEmotionText(emotion) {
      const textMap = {
        happiness: '开心',
        sadness: '难过',
        anger: '生气',
        surprise: '惊讶',
        neutral: '平静',
        fear: '恐惧',
        disgust: '厌恶',
        // 保持向后兼容
        happy: '开心',
        sad: '难过',
        angry: '生气',
        surprised: '惊讶',
        focused: '专注',
        confident: '自信'
      }
      return textMap[emotion] || '平静'
    },

    getUserStatusText() {
      if (this.isRecording) return '正在回答...'
      if (this.isListening) return '正在聆听...'
      if (this.currentEmotion !== 'neutral') {
        return `当前状态: ${this.getEmotionText(this.currentEmotion)}`
      }
      return '等待中...'
    },

    // 讯飞TTS面试交互相关方法
    async startXunfeiInterview() {
      try {
        this.isConnecting = true
        this.aiThinking = true
        this.currentAIMessage = '正在连接AI面试官...'

        // 创建讯飞TTS面试会话
        const response = await this.$axios.post('/interview/local/create_session', {
          mode_id: 'interview'
        })

        if (response.data.success) {
          this.sessionId = response.data.session_id
          this.interviewStatus = 'in_progress'
          this.aiThinking = false
          this.isConnecting = false

          // 开始计时
          this.startDurationTimer()

          // 合并欢迎语和第一个问题
          this.startWithWelcomeAndFirstQuestion()
        } else {
          throw new Error(response.data.message || '创建面试会话失败')
        }

      } catch (error) {
        console.error('启动讯飞TTS面试失败:', error)
        this.showErrorMessage('启动AI面试失败: ' + error.message)
        this.aiThinking = false

        // 如果讯飞TTS连接失败，回退到模拟模式
        console.log('回退到模拟模式')
        this.startFallbackMode()
      } finally {
        this.isConnecting = false
      }
    },

    startFallbackMode() {
      console.log('启动模拟模式')
      this.sessionId = 'session_' + Date.now()
      this.interviewStatus = 'in_progress'
      this.aiThinking = false

      // 开始计时
      this.startDurationTimer()

      // 使用合并的欢迎语和第一个问题（模拟模式）
      setTimeout(() => {
        this.startWithWelcomeAndFirstQuestion()
      }, 1000)
    },

    addAIMessage(message) {
      this.messages.push({
        type: 'interviewer',
        content: message,
        timestamp: Date.now()
      })

      this.currentAIMessage = message
      this.isAISpeaking = true

      // 模拟语音合成时间，根据消息长度计算
      const speakingDuration = Math.max(2000, message.length * 80) // 最少2秒

      setTimeout(() => {
        this.isAISpeaking = false
        this.currentAIMessage = '' // 清空消息显示
      }, speakingDuration)
    },

    addUserMessage(message) {
      this.messages.push({
        type: 'candidate',
        content: message,
        timestamp: Date.now()
      })
    },

    async startWithWelcomeAndFirstQuestion() {
      // 初始化问题索引
      this.questionCount = 1
      this.currentQuestionIndex = 0

      // 获取第一个问题
      let firstQuestion = '请简单介绍一下您自己。' // 默认问题
      if (this.questions && this.questions.length > 0) {
        const question = this.questions[0]
        if (question && question.text) {
          firstQuestion = question.text
        }
      }

      // 合并欢迎语和第一个问题
      const combinedMessage = `您好！欢迎参加面试。我是您的AI面试官小星，让我们开始吧！现在请回答第一个问题：${firstQuestion}`

      this.addAIMessage(combinedMessage)
      await this.speakQuestion(combinedMessage)
    },

    async askFirstQuestion() {
      // 问第一个问题，不需要调用后端API
      this.questionCount = 1
      this.currentQuestionIndex = 0

      // 显示AI思考状态
      this.aiThinking = true

      setTimeout(async () => {
        this.aiThinking = false

        // 调试信息
        console.log('askFirstQuestion - 当前问题数据:', {
          questionsLength: this.questions ? this.questions.length : 0,
          firstQuestion: this.questions && this.questions.length > 0 ? this.questions[0] : null,
          firstQuestionText: this.questions && this.questions.length > 0 ? this.questions[0].text : null,
          interviewQuestionsLength: this.interviewQuestions ? this.interviewQuestions.length : 0,
          allQuestions: this.questions
        })

        // 使用传入的问题数据或默认问题
        let question = '请简单介绍一下您自己。' // 默认问题

        if (this.questions && this.questions.length > 0) {
          const firstQuestion = this.questions[0]
          if (firstQuestion && firstQuestion.text) {
            question = firstQuestion.text
          }
        }

        console.log('askFirstQuestion - 将要播放的问题:', question)
        this.addAIMessage(question)

        // 使用讯飞TTS播放问题
        await this.speakQuestion(question)
      }, 1500)
    },

    async askNextQuestion() {
      // 检查是否还有问题（基于传入的问题数组）
      const totalQuestions = this.questions.length
      const maxQuestions = Math.min(this.maxQuestions, totalQuestions)

      if (this.questionCount >= maxQuestions) {
        this.endXunfeiInterview()
        return
      }

      try {
        // 调用后端API获取下一个问题
        const response = await this.$axios.post('/interview/local/user_response', {
          session_id: this.sessionId,
          response_text: '用户已回答'
        })

        if (response.data.success && response.data.has_next_question) {
          this.questionCount++
          this.currentQuestionIndex = this.questionCount - 1

          // 显示AI思考状态
          this.aiThinking = true

          setTimeout(async () => {
            this.aiThinking = false

            // 从传入的问题数组中获取问题文本
            let question = '请谈谈您的职业规划。' // 默认问题

            if (this.questions && this.questions.length > 0) {
              const questionIndex = this.questionCount - 1
              if (questionIndex < this.questions.length) {
                question = this.questions[questionIndex].text
              }
            }

            this.addAIMessage(question)

            // 使用讯飞TTS播放问题
            await this.speakQuestion(question)
          }, 1500)
        } else {
          // 没有更多问题，结束面试
          this.endXunfeiInterview()
        }
      } catch (error) {
        console.error('获取下一个问题失败:', error)
        this.endXunfeiInterview()
      }
    },

    async endXunfeiInterview() {
      this.interviewStatus = 'ended'
      this.stopDurationTimer()

      const endMessage = '感谢您参加本次面试！面试已结束，祝您好运！'
      this.addAIMessage(endMessage)

      // 使用讯飞TTS播放结束语
      await this.speakQuestion(endMessage)

      // 结束会话
      try {
        await this.$axios.post('/interview/local/end_session', {
          session_id: this.sessionId
        })
      } catch (error) {
        console.error('结束面试会话失败:', error)
      }

      setTimeout(() => {
        this.$emit('interview-ended', {
          sessionId: this.sessionId,
          questionsAnswered: this.questionCount,
          totalQuestions: this.maxQuestions,
          duration: this.duration,
          messages: this.messages
        })
      }, 3000)
    },

    startDurationTimer() {
      this.duration = 0
      this.durationTimer = setInterval(() => {
        this.duration++
      }, 1000)
    },

    stopDurationTimer() {
      if (this.durationTimer) {
        clearInterval(this.durationTimer)
        this.durationTimer = null
      }
    },

    cleanup() {
      // 停止录音
      if (this.isRecording) {
        this.stopRecording()
      }

      // 停止语音识别
      this.stopSpeechRecognition()

      // 停止计时器
      this.stopRecordingTimer()

      // 停止表情检测
      this.stopEmotionDetection()

      // 停止SparkOS相关定时器
      this.stopDurationTimer()

      // 清理音频资源
      if (this.audioStream) {
        this.audioStream.getTracks().forEach(track => track.stop())
      }
      if (this.cameraStream) {
        this.cameraStream.getTracks().forEach(track => track.stop())
      }

      // 清理媒体录制器
      if (this.mediaRecorder) {
        this.mediaRecorder = null
      }

      // 移除事件监听器
      document.removeEventListener('fullscreenchange', this.handleFullscreenChange)
      document.removeEventListener('webkitfullscreenchange', this.handleFullscreenChange)
      document.removeEventListener('keydown', this.handleKeyDown)
    }
  }
}
</script>

<style scoped>
.immersive-interview {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: #000000;
  overflow: hidden;
  z-index: 9999;
  font-family: 'Roboto', sans-serif;
}

.immersive-interview.fullscreen-active {
  cursor: none;
}

.immersive-interview.fullscreen-active:hover {
  cursor: default;
}

/* 背景效果 */
.immersive-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: #000000;
  z-index: 1;
}

/* 主要内容区域 */
.interview-content {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  z-index: 2;
}

/* 顶部问题显示区域 */
.top-question-area {
  position: absolute;
  top: 40px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10;
  max-width: 80%;
  text-align: center;
}

.top-question-area .current-question h3 {
  color: white;
  font-size: 18px;
  font-weight: 500;
  margin: 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
  line-height: 1.4;
}

.top-question-area .ai-message h3 {
  color: white;
  font-size: 18px;
  font-weight: 500;
  margin: 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
  line-height: 1.4;
}

.top-question-area .ai-thinking {
  display: flex;
  gap: 8px;
  align-items: center;
  justify-content: center;
}

.top-question-area .ai-thinking .dot {
  width: 8px;
  height: 8px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 50%;
  animation: thinking-dots 1.5s ease-in-out infinite;
}

.top-question-area .ai-thinking .dot:nth-child(2) {
  animation-delay: 0.3s;
}

.top-question-area .ai-thinking .dot:nth-child(3) {
  animation-delay: 0.6s;
}

/* 用户回答显示区域 */
.user-response-area {
  position: absolute;
  bottom: 140px;
  left: 32px;
  width: 400px;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(15px);
  border-radius: 16px;
  padding: 20px;
  color: white;
  z-index: 8;
}

.user-response h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.user-response p {
  margin: 0;
  line-height: 1.5;
}

/* 主布局 */
.main-interview-layout {
  display: flex;
  height: 100vh;
  align-items: center;
  justify-content: center;
  padding: 40px 40px 120px;
  gap: 40px;
}



/* 中央可视化区域 */
.visualization-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
}

.visualizer {
  filter: drop-shadow(0 0 20px rgba(255, 255, 255, 0.3));
}



/* 右下角摄像头区域 */
.bottom-right-camera {
  position: absolute;
  bottom: 120px;
  right: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  z-index: 15;
}

.camera-container-bottom {
  position: relative;
  width: 180px;
  height: 135px;
  border-radius: 12px;
  overflow: hidden;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(10px);
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.user-video-bottom {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 12px;
}

.camera-placeholder-bottom {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: rgba(255, 255, 255, 0.7);
  text-align: center;
}

.emotion-text-bottom {
  text-align: center;
  color: white;
  font-size: 12px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);
  margin-bottom: 8px;
  min-height: 16px;
}

.emotion-indicator.happy {
  color: #f39c12;
}

.emotion-indicator.confident {
  color: #27ae60;
}

.emotion-indicator.focused {
  color: #3498db;
}

.emotion-indicator.surprised {
  color: #e74c3c;
}

.emotion-indicator.neutral {
  color: rgba(255, 255, 255, 0.8);
}

.emotion-confidence {
  margin-left: auto;
  font-size: 10px;
  opacity: 0.8;
}



/* 用户摄像头样式已移至 .user-camera-section */

/* 底部控制栏 */
.bottom-controls {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 100px;
  background: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  z-index: 10;
}

/* 左侧控制区域 */
.left-controls {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: flex-start;
}

/* 中央控制区域 - 录音按钮 */
.center-controls {
  flex: 0 0 auto;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 右侧控制区域 */
.right-controls {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 16px;
}

.end-interview-btn {
  min-width: 120px;
  height: 40px;
  font-weight: 500;
  text-transform: none;
  border-radius: 20px;
}

.recognition-text {
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(10px);
  border-radius: 8px;
  padding: 12px 16px;
  max-width: 300px;
  color: white;
  font-size: 14px;
  text-align: left;
}

.recognition-text p {
  margin: 0;
  line-height: 1.4;
}

.record-btn {
  width: 64px !important;
  height: 64px !important;
}

.interview-controls {
  display: flex;
  gap: 12px;
}

/* 快捷键提示 */
.shortcuts-help {
  position: absolute;
  top: 100px;
  right: 32px;
  z-index: 15;
}

.shortcuts-content {
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(15px);
  border-radius: 12px;
  padding: 20px;
  color: white;
  min-width: 250px;
  position: relative;
}

.shortcuts-content h4 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 500;
  text-align: center;
}

.shortcut-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.shortcut-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.shortcut-item kbd {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 4px;
  padding: 4px 8px;
  font-size: 12px;
  font-family: monospace;
  min-width: 60px;
  text-align: center;
}

.shortcut-item span {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
}

.close-shortcuts {
  position: absolute;
  top: 8px;
  right: 8px;
  min-width: auto !important;
  width: 24px !important;
  height: 24px !important;
  color: rgba(255, 255, 255, 0.7) !important;
}

/* 加载遮罩 */
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 20;
}

.loading-text {
  color: white;
  font-size: 18px;
  margin-top: 24px;
  text-align: center;
}



/* 关键帧动画 */
@keyframes thinking-dots {
  0%, 100% {
    opacity: 0.3;
    transform: scale(1);
  }
  50% {
    opacity: 1;
    transform: scale(1.2);
  }
}

@keyframes pulse-ring {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  100% {
    transform: scale(1.2);
    opacity: 0;
  }
}



/* 响应式设计 */
@media (max-width: 1200px) {
  .main-interview-layout {
    padding: 80px 20px 120px;
    gap: 20px;
  }

  .ai-interviewer-section {
    max-width: 280px;
  }

  .user-camera-section {
    max-width: 180px;
  }

  .camera-container {
    width: 160px;
    height: 120px;
  }

  .status-bar {
    padding: 0 24px;
  }

  .bottom-controls {
    padding: 0 24px;
  }
}

@media (max-width: 768px) {
  .main-interview-layout {
    flex-direction: column;
    padding: 60px 16px 140px;
    gap: 20px;
    justify-content: flex-start;
    overflow-y: auto;
  }

  .ai-interviewer-section,
  .user-camera-section,
  .visualization-area {
    max-width: 100%;
    width: 100%;
  }

  .camera-container {
    width: 100%;
    max-width: 320px;
    height: 240px;
    margin: 0 auto 20px;
  }

  .ai-avatar {
    width: 80px;
    height: 80px;
  }

  .ai-message-container {
    min-height: 80px;
    padding: 16px;
  }

  .status-bar {
    padding: 0 16px;
  }

  .bottom-controls {
    padding: 0 16px;
    height: 120px;
    flex-direction: column;
    gap: 12px;
  }

  .left-controls,
  .center-controls,
  .right-controls {
    flex: none;
    width: 100%;
    justify-content: center;
  }

  .left-controls {
    order: 1;
  }

  .center-controls {
    order: 2;
  }

  .right-controls {
    order: 3;
  }

  .interview-controls {
    flex-wrap: wrap;
    justify-content: center;
  }
}
</style>
