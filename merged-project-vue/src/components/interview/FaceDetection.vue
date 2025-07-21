<template>
  <div class="ai-interview-container">
    <div class="interview-layout">
      <!-- 左侧：AI面试官区域 -->
      <div class="ai-interviewer-section">
        <div class="ai-avatar-container">
          <v-avatar size="120" class="ai-avatar">
            <v-img src="https://cdn.vuetifyjs.com/images/john.jpg" alt="AI面试官"></v-img>
          </v-avatar>
          <div class="ai-status" :class="{'ai-speaking': isSpeaking}"></div>
        </div>
        <div class="ai-name">AI面试官</div>
        <div class="ai-role">{{ interviewPosition || '职位面试' }}</div>
        
        <div class="ai-message-container">
          <div class="ai-message" v-if="currentMessage">
            <p>{{ currentMessage }}</p>
          </div>
          <div class="ai-thinking" v-if="aiThinking">
            <span class="dot"></span>
            <span class="dot"></span>
            <span class="dot"></span>
          </div>
        </div>
      </div>
      
      <!-- 右侧：用户摄像头和交互区域 -->
      <div class="user-section">
        <div class="camera-container">
          <video
            v-show="!imageCaptured && cameraActive"
            ref="video"
            :width="width"
            :height="height"
            autoplay
            muted
          ></video>
          <canvas
            ref="canvas"
            :width="width"
            :height="height"
            v-show="imageCaptured"
          ></canvas>
          <div class="camera-overlay" v-if="!cameraActive">
            <div class="camera-placeholder">
              <v-icon size="64" color="grey lighten-1">mdi-video-off</v-icon>
              <div class="mt-2">摄像头未开启</div>
              <v-btn color="primary" @click="startCamera" class="mt-4">开启摄像头</v-btn>
            </div>
          </div>
          
          <!-- 表情分析结果覆盖层 -->
          <div class="emotion-overlay" v-if="cameraActive && showEmotionOverlay">
            <div class="emotion-indicator" :class="currentEmotion">
              <v-icon>{{ getEmotionIcon(currentEmotion) }}</v-icon>
              <span>{{ getEmotionText(currentEmotion) }}</span>
              <span v-if="analysisResult && analysisResult.emotions && analysisResult.emotions.length > 0" class="emotion-confidence">
                {{ (analysisResult.emotions[0].confidence * 100).toFixed(0) }}%
              </span>
            </div>
          </div>
        </div>
        
        <!-- 面试进度 -->
        <div class="interview-progress-container">
          <div class="progress-header">
            <span>面试进度: {{ currentQuestionIndex + 1 }}/{{ totalQuestions }}</span>
            <span>剩余时间: {{ formatTime(remainingTime) }}</span>
          </div>
          <v-progress-linear
            :value="(currentQuestionIndex / totalQuestions) * 100"
            height="8"
            rounded
            color="primary"
          ></v-progress-linear>
        </div>
        
        <!-- 用户回答区域 -->
        <div class="user-answer-section">
          <div v-if="interviewState === 'answering'" class="answer-controls">
            <v-textarea
              v-if="inputMode === 'text'"
              v-model="userAnswer"
              outlined
              label="请输入您的回答"
              rows="3"
              auto-grow
              hide-details
            ></v-textarea>
            
            <div v-if="inputMode === 'voice'" class="voice-input-container">
              <div class="voice-status" :class="{'recording': isRecording}">
                <v-icon size="36" :color="isRecording ? 'red' : 'grey'">{{ isRecording ? 'mdi-microphone' : 'mdi-microphone-outline' }}</v-icon>
                <span>{{ isRecording ? '正在录音...' : '点击开始录音' }}</span>
              </div>
              <div v-if="recognizedText" class="recognized-text">
                "{{ recognizedText }}"
              </div>
            </div>
            
            <div class="answer-actions">
              <v-btn 
                v-if="inputMode === 'voice'"
                :color="isRecording ? 'error' : 'primary'"
                @click="toggleRecording"
              >
                {{ isRecording ? '停止录音' : '开始录音' }}
              </v-btn>
              
              <v-btn
                color="primary"
                :disabled="!canSubmitAnswer"
                @click="submitAnswer"
              >
                提交回答
              </v-btn>
              
              <v-btn-toggle v-model="inputMode" mandatory>
                <v-btn value="text" small>
                  <v-icon>mdi-keyboard</v-icon>
                </v-btn>
                <v-btn value="voice" small>
                  <v-icon>mdi-microphone</v-icon>
                </v-btn>
              </v-btn-toggle>
            </div>
          </div>
          
          <div v-else-if="interviewState === 'feedback'" class="feedback-container">
            <v-card outlined>
              <v-card-title>
                <v-icon left color="primary">mdi-comment-check</v-icon>
                AI评估反馈
              </v-card-title>
              <v-card-text>
                <p class="feedback-text">{{ currentFeedback.content }}</p>
                
                <div class="feedback-score">
                  <span>回答得分:</span>
                  <v-rating
                    :value="currentFeedback.score / 20"
                    color="amber"
                    background-color="grey lighten-1"
                    half-increments
                    readonly
                    dense
                  ></v-rating>
                  <span class="score-value">{{ currentFeedback.score }}/100</span>
                </div>
                
                <div class="feedback-tags">
                  <v-chip
                    v-for="(tag, i) in currentFeedback.tags"
                    :key="i"
                    small
                    class="mr-1 mb-1"
                  >
                    {{ tag }}
                  </v-chip>
                </div>
              </v-card-text>
              <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn
                  color="primary"
                  text
                  @click="nextQuestion"
                >
                  继续
                </v-btn>
              </v-card-actions>
            </v-card>
          </div>
          
          <div v-else-if="interviewState === 'completed'" class="completed-container">
            <v-alert type="success" prominent>
              <v-row align="center">
                <v-col class="grow">
                  面试已完成！感谢您的参与。
                </v-col>
                <v-col class="shrink">
                  <v-btn color="primary" @click="viewReport">
                    查看报告
                  </v-btn>
                </v-col>
              </v-row>
            </v-alert>
          </div>
          
          <div v-else class="waiting-container">
            <v-btn color="primary" @click="startInterview">
              开始面试
            </v-btn>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 表情分析结果 -->
    <div class="analysis-container" v-if="analysisResult && analysisResult.emotions">
      <h3>表情分析</h3>
      <div class="emotion-list">
        <div 
          v-for="(emotion, index) in analysisResult.emotions" 
          :key="index"
          class="emotion-item"
        >
          <p>人脸 #{{ emotion.face_id + 1 }}: {{ emotion.emotion }} (置信度: {{ emotion.confidence }})</p>
          <v-progress-linear 
            :value="emotion.confidence * 100" 
            height="5"
            :color="getEmotionColor(emotion.emotion)"
          ></v-progress-linear>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { detectFace, analyzeFace, getCurrentEmotion, getEmotionDistribution } from '@/api/face_detection'

export default {
  name: 'AIInterviewFace',
  props: {
    width: {
      type: Number,
      default: 640
    },
    height: {
      type: Number,
      default: 480
    },
    interviewPosition: {
      type: String,
      default: '软件工程师'
    },
    interviewDuration: {
      type: Number,
      default: 15 // 默认15分钟
    },
    interviewQuestions: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      // 摄像头相关
      stream: null,
      cameraActive: false,
      imageCaptured: false,
      imageData: null,
      drawMode: 'contours',
      detectionResult: null,
      analysisResult: null,
      loading: false,
      
      // 面试状态相关
      interviewState: 'waiting', // waiting, intro, answering, feedback, completed
      interviewStarted: false,
      currentQuestionIndex: 0,
      totalQuestions: 0,
      remainingTime: 0,
      timer: null,
      
      // AI面试官相关
      currentMessage: '',
      aiThinking: false,
      isSpeaking: false,
      
      // 语音识别相关
      isRecording: false,
      recognition: null,
      recognizedText: '',
      
      // 用户输入相关
      inputMode: 'text', // text 或 voice
      userAnswer: '',
      
      // 表情分析相关
      currentEmotion: 'neutral',
      showEmotionOverlay: true,
      emotionDetectionInterval: null,
      
      // 面试反馈相关
      currentFeedback: {
        content: '',
        score: 0,
        tags: []
      },
      
      // 面试问题
      questions: [
        {
          id: 1,
          text: '请简单介绍一下你自己和你的专业背景。',
          type: 'open'
        },
        {
          id: 2,
          text: '你为什么对我们公司的这个职位感兴趣？',
          type: 'open'
        },
        {
          id: 3,
          text: '请描述一个你在工作中遇到的挑战，以及你是如何解决的？',
          type: 'open'
        },
        {
          id: 4,
          text: '你认为你的优势是什么？有哪些方面需要提升？',
          type: 'open'
        },
        {
          id: 5,
          text: '你对未来的职业规划是什么？',
          type: 'open'
        }
      ]
    }
  },
  computed: {
    canSubmitAnswer() {
      if (this.inputMode === 'text') {
        return this.userAnswer.trim().length > 0
      } else {
        return this.recognizedText.trim().length > 0
      }
    },
    currentQuestion() {
      return this.questions[this.currentQuestionIndex] || null
    }
  },
  methods: {
    // 摄像头相关方法
    async startCamera() {
      console.log('AIInterviewFace: 开始启动摄像头...')
      
      // 检查浏览器是否支持getUserMedia
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        const errorMsg = '您的浏览器不支持访问摄像头，请使用最新版Chrome、Firefox或Edge浏览器'
        console.error(errorMsg)
        this.$emit('error', errorMsg)
        return
      }
      
      try {
        console.log('AIInterviewFace: 请求摄像头权限...')
        this.stream = await navigator.mediaDevices.getUserMedia({
          video: {
            width: { ideal: this.width },
            height: { ideal: this.height }
          }
        })
        
        console.log('AIInterviewFace: 摄像头权限已获取，设置视频源...')
        const video = this.$refs.video
        if (!video) {
          throw new Error('视频元素未找到')
        }
        
        video.srcObject = this.stream
        video.onloadedmetadata = () => {
          console.log('AIInterviewFace: 视频元数据已加载，开始播放...')
          video.play().catch(e => console.error('AIInterviewFace: 视频播放失败:', e))
        }
        
        this.cameraActive = true
        console.log('AIInterviewFace: 摄像头已成功激活')
        
        // 开始表情检测
        this.startEmotionDetection()
      } catch (error) {
        console.error('AIInterviewFace: 摄像头错误:', error)
        
        let errorMsg = '无法访问摄像头'
        if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
          errorMsg = '摄像头访问被拒绝，请在浏览器中授予摄像头权限'
        } else if (error.name === 'NotFoundError' || error.name === 'DevicesNotFoundError') {
          errorMsg = '未找到摄像头设备，请确认摄像头已连接'
        } else if (error.name === 'NotReadableError' || error.name === 'TrackStartError') {
          errorMsg = '摄像头可能被其他应用程序占用，请关闭其他使用摄像头的应用'
        } else if (error.name === 'OverconstrainedError') {
          errorMsg = '摄像头不满足指定的要求参数'
        } else if (error.name === 'TypeError') {
          errorMsg = '摄像头参数错误'
        }
        
        // 向父组件发送错误事件
        this.$emit('error', `${errorMsg}: ${error.message}`)
      }
    },
    
    stopCamera() {
      // 停止表情检测
      this.stopEmotionDetection()
      
      if (this.stream) {
        this.stream.getTracks().forEach(track => track.stop())
        this.stream = null
        this.cameraActive = false
      }
    },
    
    captureImage() {
      const video = this.$refs.video
      const canvas = this.$refs.canvas
      const context = canvas.getContext('2d')
      
      // 绘制视频帧到Canvas
      context.drawImage(video, 0, 0, this.width, this.height)
      
      // 获取图像数据
      this.imageData = canvas.toDataURL('image/jpeg')
      this.imageCaptured = true
      
      // 重置检测结果
      this.detectionResult = null
      this.analysisResult = null
    },
    
    resetCamera() {
      this.imageCaptured = false
      this.imageData = null
      this.detectionResult = null
      this.analysisResult = null
      
      // 如果摄像头已关闭，重新打开
      if (!this.cameraActive) {
        this.startCamera()
      }
    },
    
    async detectFace() {
      if (!this.imageData) {
        this.$message.warning('请先拍照')
        return
      }
      
      this.loading = true
      try {
        const response = await detectFace({
          image: this.imageData,
          draw_mode: this.drawMode
        })
        
        if (response.success) {
          this.detectionResult = response.data
          if (response.data.face_count === 0) {
            this.$message.info('未检测到人脸')
          }
        } else {
          this.$message.error(response.message || '人脸检测失败')
        }
      } catch (error) {
        console.error('人脸检测错误:', error)
        this.$message.error('人脸检测请求失败')
      } finally {
        this.loading = false
      }
    },
    
    async analyzeFace() {
      if (!this.imageData) {
        this.$message.warning('请先拍照')
        return
      }
      
      this.loading = true
      try {
        const response = await analyzeFace({
          image: this.imageData
        })
        
        if (response.success) {
          this.analysisResult = response.data
          if (response.data.face_count === 0) {
            this.$message.info('未检测到人脸，无法分析表情')
          }
        } else {
          this.$message.error(response.message || '表情分析失败')
        }
      } catch (error) {
        console.error('表情分析错误:', error)
        this.$message.error('表情分析请求失败')
      } finally {
        this.loading = false
      }
    },
    
    getEmotionColor(emotion) {
      const colors = {
        // EfficientFace使用的RAF-DB数据集标签
        'neutral': 'primary',
        'happiness': 'success',
        'sadness': 'blue-grey',
        'surprise': 'amber darken-2',
        'fear': 'purple',
        'disgust': 'brown',
        'anger': 'deep-orange',
        // 中文标签
        '微笑': 'success',
        '惊讶': 'amber darken-2',
        '闭眼': 'blue-grey',
        '中性': 'primary',
        '悲伤': 'blue-grey',
        '生气': 'deep-orange',
        '恐惧': 'purple',
        '厌恶': 'brown'
      }
      return colors[emotion] || 'primary'
    },
    
    getEmotionIcon(emotion) {
      const icons = {
        // EfficientFace使用的RAF-DB数据集标签
        'neutral': 'mdi-emoticon-neutral',
        'happiness': 'mdi-emoticon',
        'sadness': 'mdi-emoticon-sad',
        'surprise': 'mdi-emoticon-surprised',
        'fear': 'mdi-emoticon-frown',
        'disgust': 'mdi-emoticon-dead',
        'anger': 'mdi-emoticon-angry'
      }
      return icons[emotion] || 'mdi-emoticon-neutral'
    },
    
    getEmotionText(emotion) {
      const texts = {
        // EfficientFace使用的RAF-DB数据集标签
        'neutral': '中性',
        'happiness': '微笑',
        'sadness': '悲伤',
        'surprise': '惊讶',
        'fear': '恐惧',
        'disgust': '厌恶',
        'anger': '生气'
      }
      return texts[emotion] || '中性'
    },
    
    // 面试相关方法
    startInterview() {
      this.interviewState = 'intro'
      this.interviewStarted = true
      this.currentQuestionIndex = 0
      this.totalQuestions = this.questions.length
      this.remainingTime = this.interviewDuration * 60 // 转换为秒
      
      // 开始计时
      this.startTimer()
      
      // 如果摄像头未开启，自动开启
      if (!this.cameraActive) {
        this.startCamera()
      }
      
      // 显示AI介绍
      this.showAIMessage('你好！我是AI面试官。今天我将与你进行一次面试，请放松并准备好回答问题。', () => {
        this.askCurrentQuestion()
      })
    },
    
    askCurrentQuestion() {
      if (!this.currentQuestion) return
      
      this.interviewState = 'answering'
      this.userAnswer = ''
      this.recognizedText = ''
      
      // 显示当前问题
      this.showAIMessage(this.currentQuestion.text)
    },
    
    submitAnswer() {
      // 获取用户回答
      const answer = this.inputMode === 'text' ? this.userAnswer : this.recognizedText
      
      if (!answer.trim()) {
        this.$message.warning('请输入或录制您的回答')
        return
      }
      
      // 停止录音（如果正在录音）
      if (this.isRecording) {
        this.stopRecording()
      }
      
      // 显示AI思考中
      this.aiThinking = true
      
      // 向父组件发送答案
      this.$emit('answer-submitted', {
        questionId: this.currentQuestion ? this.currentQuestion.id : null,
        answer: answer,
        type: 'text'
      })
      
      // 模拟AI分析回答（实际项目中应该调用后端API）
      setTimeout(() => {
        this.aiThinking = false
        
        // 生成反馈
        this.generateFeedback(answer)
        
        // 切换到反馈状态
        this.interviewState = 'feedback'
      }, 2000)
    },
    
    generateFeedback(answer) {
      // 这里应该调用后端API进行分析，这里仅作模拟
      const feedbacks = [
        {
          content: "您的回答清晰明了，展示了良好的沟通能力。建议可以加入更多具体的例子来支持您的观点，这样会使回答更有说服力。",
          score: 85,
          tags: ["表达清晰", "逻辑性强", "缺少具体例子"]
        },
        {
          content: "您的回答展示了对问题的理解，但可以更加深入地分析问题背后的原理。建议在回答类似问题时，结合实际案例来支持您的观点。",
          score: 75,
          tags: ["理解力良好", "逻辑性待提高", "表达清晰"]
        },
        {
          content: "您的回答非常全面，涵盖了问题的多个方面，并且提供了具体的例子。建议可以更加简洁，突出最关键的信息。",
          score: 90,
          tags: ["内容全面", "有具体例子", "略显冗长"]
        }
      ]
      
      // 随机选择一个反馈
      this.currentFeedback = feedbacks[Math.floor(Math.random() * feedbacks.length)]
    },
    
    nextQuestion() {
      if (this.currentQuestionIndex < this.totalQuestions - 1) {
        // 进入下一题
        this.currentQuestionIndex++
        this.askCurrentQuestion()
      } else {
        // 面试结束
        this.completeInterview()
      }
    },
    
    completeInterview() {
      this.interviewState = 'completed'
      this.stopTimer()
      
      // 显示完成消息
      this.showAIMessage('面试已完成，感谢您的参与！您可以查看面试报告了解详细评估结果。')
      
      // 向父组件发送完成事件
      this.$emit('completed')
    },
    
    viewReport() {
      // 向父组件发送查看报告事件
      this.$emit('view-report')
    },
    
    // 计时器相关方法
    startTimer() {
      const startTime = Date.now()
      this.timer = setInterval(() => {
        const elapsedSeconds = Math.floor((Date.now() - startTime) / 1000)
        this.remainingTime = Math.max(0, this.interviewDuration * 60 - elapsedSeconds)
        
        // 时间用完，自动结束面试
        if (this.remainingTime <= 0) {
          this.completeInterview()
        }
      }, 1000)
    },
    
    stopTimer() {
      if (this.timer) {
        clearInterval(this.timer)
        this.timer = null
      }
    },
    
    formatTime(seconds) {
      const minutes = Math.floor(seconds / 60)
      const remainingSeconds = seconds % 60
      return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
    },
    
    // AI面试官相关方法
    showAIMessage(message, callback) {
      this.currentMessage = message
      this.isSpeaking = true
      
      // 模拟语音合成
      // 实际项目中应该使用Web Speech API或其他语音合成服务
      setTimeout(() => {
        this.isSpeaking = false
        
        if (callback) {
          setTimeout(callback, 500)
        }
      }, message.length * 50) // 根据消息长度模拟说话时间
    },
    
    // 语音识别相关方法
    initSpeechRecognition() {
      // 检查浏览器是否支持语音识别
      if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        this.$message.warning('您的浏览器不支持语音识别，请使用Chrome浏览器')
        return false
      }
      
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
      this.recognition = new SpeechRecognition()
      this.recognition.continuous = true
      this.recognition.interimResults = true
      this.recognition.lang = 'zh-CN'
      
      this.recognition.onresult = (event) => {
        let finalTranscript = ''
        let interimTranscript = ''
        
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) {
            finalTranscript += event.results[i][0].transcript
          } else {
            interimTranscript += event.results[i][0].transcript
          }
        }
        
        if (finalTranscript) {
          this.recognizedText += finalTranscript + ' '
        }
      }
      
      this.recognition.onerror = (event) => {
        console.error('语音识别错误:', event.error)
        this.isRecording = false
      }
      
      return true
    },
    
    toggleRecording() {
      if (this.isRecording) {
        this.stopRecording()
      } else {
        this.startRecording()
      }
    },
    
    startRecording() {
      if (!this.recognition && !this.initSpeechRecognition()) {
        return
      }
      
      try {
        this.recognition.start()
        this.isRecording = true
      } catch (error) {
        console.error('开始录音失败:', error)
        this.$message.error('开始录音失败')
      }
    },
    
    stopRecording() {
      if (this.recognition) {
        try {
          this.recognition.stop()
        } catch (error) {
          console.error('停止录音失败:', error)
        }
      }
      this.isRecording = false
    },
    
    // 表情检测相关方法
    startEmotionDetection() {
      // 每2秒检测一次表情，提高响应速度
      this.emotionDetectionInterval = setInterval(() => {
        this.detectCurrentEmotion()
      }, 2000)
      
      // 立即执行一次
      this.detectCurrentEmotion()
      
      console.log('表情检测已启动')
    },
    
    stopEmotionDetection() {
      if (this.emotionDetectionInterval) {
        clearInterval(this.emotionDetectionInterval)
        this.emotionDetectionInterval = null
      }
    },
    
    detectCurrentEmotion() {
      if (!this.cameraActive || !this.$refs.video) return
      
      // 创建一个临时canvas来捕获当前视频帧
      const video = this.$refs.video
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
        // 调用表情分析API
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
          
          // 更新分析结果
          this.analysisResult = {
            emotions: response.data.expressions.map(expr => ({
              face_id: expr.face_id,
              emotion: expr.expression,
              confidence: expr.confidence
            }))
          }
        } else if (response.success && response.data && response.data.face_count === 0) {
          console.log('未检测到人脸')
          this.currentEmotion = 'neutral'
        }
      } catch (error) {
        console.error('表情分析失败:', error)
        // 出错时默认为中性表情
        this.currentEmotion = 'neutral'
      }
    }
  },
  mounted() {
    // 检查浏览器是否支持语音识别
    this.initSpeechRecognition()
  },
  created() {
    // 如果传入了面试问题，则使用传入的问题
    if (this.interviewQuestions && this.interviewQuestions.length > 0) {
      // 将传入的问题格式化为组件内部使用的格式
      this.questions = this.interviewQuestions.map(q => {
        return {
          id: q.id || Math.random().toString(36).substr(2, 9),
          text: q.content || q.text || '未提供问题内容',
          type: q.type || 'open'
        };
      });
    }
    // 否则使用默认问题（已在data中定义）
    
    // 设置问题总数
    this.totalQuestions = this.questions.length;
  },
  beforeDestroy() {
    // 确保在组件销毁时关闭摄像头和停止计时器
    this.stopCamera()
    this.stopTimer()
    this.stopRecording()
  }
}
</script>

<style scoped>
.ai-interview-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.interview-layout {
  display: flex;
  width: 100%;
  gap: 20px;
  margin-bottom: 20px;
}

/* AI面试官部分 */
.ai-interviewer-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.ai-avatar-container {
  position: relative;
  margin-bottom: 10px;
}

.ai-avatar {
  border: 3px solid #1976d2;
}

.ai-status {
  position: absolute;
  bottom: 5px;
  right: 5px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background-color: #4caf50;
  border: 2px solid white;
}

.ai-status.ai-speaking {
  animation: pulse 1.5s infinite;
}

.ai-name {
  font-size: 1.5rem;
  font-weight: 500;
  margin-bottom: 5px;
}

.ai-role {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 20px;
}

.ai-message-container {
  width: 100%;
  min-height: 100px;
  background-color: white;
  border-radius: 8px;
  padding: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  margin-top: 8px;
}

.ai-message {
  font-size: 1rem;
  line-height: 1.4;
}

.ai-thinking {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 40px;
}

.ai-thinking .dot {
  width: 8px;
  height: 8px;
  background-color: #1976d2;
  border-radius: 50%;
  margin: 0 3px;
  animation: bounce 1.5s infinite ease-in-out;
}

.ai-thinking .dot:nth-child(2) {
  animation-delay: 0.2s;
}

.ai-thinking .dot:nth-child(3) {
  animation-delay: 0.4s;
}

/* 用户部分 */
.user-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* 视频和画布样式 */
video, canvas {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 6px;
}

.camera-container {
  position: relative;
  width: 280px;
  height: 280px;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  overflow: hidden;
  margin: 0 auto 15px;
  background-color: #000;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.camera-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: rgba(0, 0, 0, 0.7);
}

.camera-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: white;
}

.emotion-overlay {
  position: absolute;
  top: 10px;
  right: 10px;
  background-color: rgba(0, 0, 0, 0.5);
  border-radius: 20px;
  padding: 5px 12px;
  display: flex;
  align-items: center;
  color: white;
}

.emotion-indicator {
  display: flex;
  align-items: center;
  gap: 5px;
}

.emotion-confidence {
  margin-left: 5px;
  font-size: 0.8em;
  opacity: 0.8;
}

/* EfficientFace表情类名 */
.emotion-indicator.happiness {
  color: #4caf50;
}

.emotion-indicator.sadness {
  color: #78909c;
}

.emotion-indicator.anger {
  color: #ff5722;
}

.emotion-indicator.surprise {
  color: #ffc107;
}

.emotion-indicator.fear {
  color: #9c27b0;
}

.emotion-indicator.disgust {
  color: #795548;
}

.emotion-indicator.neutral {
  color: #2196f3;
}

/* 面试进度 */
.interview-progress-container {
  margin-bottom: 15px;
  width: 100%;
  max-width: 500px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
  font-size: 0.9rem;
  color: #666;
}

/* 用户回答区域 */
.user-answer-section {
  flex: 1;
  min-height: 120px;
  width: 100%;
  max-width: 500px;
}

.answer-controls {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.answer-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
}

.voice-input-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  border: 1px dashed #dcdfe6;
  border-radius: 4px;
  background-color: #f9f9f9;
}

.voice-status {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.voice-status.recording {
  color: #f44336;
}

.voice-status.recording i {
  animation: pulse 1.5s infinite;
}

.recognized-text {
  margin-top: 15px;
  font-style: italic;
  color: #666;
  text-align: center;
}

.feedback-container {
  margin-top: 10px;
}

.feedback-text {
  margin-bottom: 15px;
  line-height: 1.6;
}

.feedback-score {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
  gap: 10px;
}

.score-value {
  font-weight: 500;
  color: #ff9800;
}

.feedback-tags {
  margin-top: 10px;
}

.waiting-container, .completed-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 150px;
}

/* 表情分析结果 */
.analysis-container {
  width: 100%;
  max-width: 1200px;
  margin-top: 20px;
  padding: 15px;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  background-color: #fff;
}

.emotion-list {
  margin-top: 10px;
}

.emotion-item {
  margin-bottom: 15px;
}

/* 动画 */
@keyframes pulse {
  0% {
    opacity: 0.6;
    transform: scale(1);
  }
  50% {
    opacity: 1;
    transform: scale(1.2);
  }
  100% {
    opacity: 0.6;
    transform: scale(1);
  }
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-5px);
  }
}

/* 响应式布局 */
@media (max-width: 768px) {
  .interview-layout {
    flex-direction: column;
  }
  
  .ai-interviewer-section {
    margin-bottom: 20px;
  }
  
  .camera-container {
    width: 240px;
    height: 240px;
  }
}

@media (min-width: 1200px) {
  .camera-container {
    width: 320px;
    height: 320px;
  }
}
</style> 