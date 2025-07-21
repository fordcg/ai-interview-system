<template>
  <div class="interview-question">
    <v-card class="mb-4" elevation="2">
      <v-card-title class="primary--text">
        <v-icon left color="primary">mdi-help-circle</v-icon>
        问题 {{ questionNumber }}/{{ totalQuestions }}
      </v-card-title>
      
      <v-card-text class="question-content">
        <!-- AI提问区域 -->
        <div class="ai-question-container mb-4">
          <v-avatar color="primary" size="36" class="mr-3">
            <v-icon dark>mdi-robot</v-icon>
          </v-avatar>
          <div class="ai-question-bubble">
            <h2 class="text-h5 mb-2">{{ question.content }}</h2>
            
            <div v-if="question.description" class="question-description">
              {{ question.description }}
            </div>
            
            <div v-if="aiThinking" class="ai-thinking mt-2">
              <v-progress-linear indeterminate color="primary" height="3"></v-progress-linear>
              <span class="caption">AI正在思考后续问题...</span>
            </div>
          </div>
        </div>
        
        <div v-if="question.type === 'choice'" class="mt-4">
          <v-radio-group v-model="answer" :disabled="answered">
            <v-radio
              v-for="(option, index) in question.options"
              :key="index"
              :label="option.text"
              :value="option.value"
            ></v-radio>
          </v-radio-group>
        </div>
        
        <div v-else-if="question.type === 'multiple_choice'" class="mt-4">
          <v-checkbox
            v-for="(option, index) in question.options"
            :key="index"
            v-model="multipleAnswer"
            :label="option.text"
            :value="option.value"
            :disabled="answered"
            hide-details
            class="mb-2"
          ></v-checkbox>
        </div>
        
        <div v-else class="mt-4">
          <v-textarea
            v-model="textAnswer"
            outlined
            :disabled="answered"
            :rows="5"
            placeholder="请输入您的回答..."
            hide-details
            auto-grow
          ></v-textarea>
          
          <!-- 音频录制区域 -->
          <div v-if="isRecording || audioUrl" class="audio-container mt-4">
            <div class="audio-visualizer-container" v-if="isRecording">
              <div 
                v-for="(bar, index) in audioVisualizerBars" 
                :key="index"
                class="audio-visualizer-bar"
                :style="{ height: bar + '%' }"
              ></div>
            </div>
            
            <audio v-if="audioUrl" :src="audioUrl" controls class="audio-player"></audio>
            
            <div class="audio-info">
              <div v-if="isRecording" class="recording-indicator">
                <v-progress-circular
                  indeterminate
                  color="red"
                  size="20"
                  width="2"
                  class="mr-2"
                ></v-progress-circular>
                正在录音... {{ recordingTime }}秒
              </div>
              
              <div v-else-if="audioUrl" class="audio-status">
                <v-icon color="success" small class="mr-2">mdi-check-circle</v-icon>
                录音已保存
              </div>
            </div>
          </div>
        </div>
      </v-card-text>
      
      <v-card-actions>
        <v-btn
          v-if="!answered && question.type === 'text'"
          color="error"
          outlined
          @click="toggleRecording"
          class="mr-2"
          :disabled="processingAudio"
        >
          <v-icon left>{{ isRecording ? 'mdi-stop' : 'mdi-microphone' }}</v-icon>
          {{ isRecording ? '停止录音' : '语音回答' }}
        </v-btn>
        
        <v-btn
          v-if="audioUrl && !answered"
          text
          color="primary"
          @click="clearAudio"
          class="mr-2"
        >
          <v-icon left>mdi-delete</v-icon>
          清除录音
        </v-btn>
        
        <v-spacer></v-spacer>
        
        <v-btn
          v-if="!answered"
          color="primary"
          :disabled="!isAnswerValid || processingAudio"
          @click="submitAnswer"
        >
          提交回答
        </v-btn>
        
        <v-btn
          v-else
          color="success"
          @click="nextQuestion"
        >
          下一题
        </v-btn>
      </v-card-actions>
    </v-card>
    
    <v-expand-transition>
      <v-card v-if="answered && analysis" elevation="2">
        <v-card-title class="success--text">
          <v-icon left color="success">mdi-check-circle</v-icon>
          回答分析
        </v-card-title>
        
        <v-card-text>
          <div v-if="question.type !== 'text'" class="mb-4">
            <div class="font-weight-bold">正确答案:</div>
            <div v-if="question.type === 'choice'">
              {{ getCorrectAnswerText() }}
            </div>
            <div v-else-if="question.type === 'multiple_choice'">
              <div v-for="(option, index) in question.options" :key="index">
                <v-icon v-if="isCorrectOption(option.value)" color="success" small>mdi-check</v-icon>
                {{ option.text }}
              </div>
            </div>
          </div>
          
          <div class="font-weight-bold mb-2">分析:</div>
          <div v-html="analysis.content"></div>
          
          <!-- 评分维度 -->
          <div class="score-dimensions mt-4">
            <div class="font-weight-bold mb-2">评分维度:</div>
            <v-row>
              <v-col cols="12" sm="6" v-for="(dimension, index) in analysis.dimensions" :key="index">
                <div class="d-flex align-center mb-2">
                  <div class="mr-3 grey--text text--darken-1">{{ dimension.name }}</div>
                  <v-progress-linear
                    :value="dimension.score"
                    height="8"
                    rounded
                    :color="getScoreColor(dimension.score)"
                    class="flex-grow-1"
                  ></v-progress-linear>
                  <div class="ml-3 font-weight-medium">{{ dimension.score }}</div>
                </div>
              </v-col>
            </v-row>
          </div>
          
          <v-chip-group class="mt-4">
            <v-chip
              v-for="(tag, index) in analysis.tags"
              :key="index"
              color="primary"
              text-color="white"
              small
            >
              {{ tag }}
            </v-chip>
          </v-chip-group>
          
          <v-progress-linear
            v-if="analysis.score !== undefined"
            :value="analysis.score"
            color="success"
            height="20"
            class="mt-4"
          >
            <template v-slot:default>
              得分: {{ analysis.score }}/100
            </template>
          </v-progress-linear>
        </v-card-text>
      </v-card>
    </v-expand-transition>
  </div>
</template>

<script>
export default {
  name: "InterviewQuestion",
  props: {
    question: {
      type: Object,
      required: true
    },
    questionNumber: {
      type: Number,
      default: 1
    },
    totalQuestions: {
      type: Number,
      default: 10
    }
  },
  data() {
    return {
      answer: null,
      multipleAnswer: [],
      textAnswer: "",
      answered: false,
      analysis: null,
      isRecording: false,
      recordingTime: 0,
      recordingTimer: null,
      audioRecorder: null,
      audioChunks: [],
      audioUrl: null,
      processingAudio: false,
      audioVisualizerBars: Array(50).fill(0),
      audioAnalyser: null,
      audioDataArray: null,
      visualizerInterval: null,
      aiThinking: false
    };
  },
  computed: {
    isAnswerValid() {
      if (this.question.type === 'choice') {
        return this.answer !== null;
      } else if (this.question.type === 'multiple_choice') {
        return this.multipleAnswer.length > 0;
      } else {
        return this.textAnswer.trim().length > 0 || this.audioUrl !== null;
      }
    }
  },
  methods: {
    submitAnswer() {
      let answerData = null;
      
      if (this.question.type === 'choice') {
        answerData = this.answer;
      } else if (this.question.type === 'multiple_choice') {
        answerData = this.multipleAnswer;
      } else {
        answerData = this.textAnswer;
      }
      
      // 停止录音（如果正在录音）
      if (this.isRecording) {
        this.stopRecording();
      }
      
      this.$emit('submit', {
        questionId: this.question.id,
        answer: answerData,
        type: this.question.type
      });
      
      // 模拟AI思考
      this.aiThinking = true;
      
      // 模拟获取分析结果
      setTimeout(() => {
        this.aiThinking = false;
        
        this.analysis = {
          content: "您的回答展示了对问题的理解，但可以更加深入地分析问题背后的原理。建议在回答类似问题时，结合实际案例来支持您的观点，这样会使回答更加有说服力。",
          tags: ["理解力良好", "逻辑性待提高", "表达清晰"],
          score: Math.floor(Math.random() * 30) + 70, // 70-100之间的随机分数
          dimensions: [
            { name: "专业知识", score: Math.floor(Math.random() * 30) + 70 },
            { name: "表达能力", score: Math.floor(Math.random() * 30) + 70 },
            { name: "逻辑思维", score: Math.floor(Math.random() * 30) + 70 },
            { name: "应变能力", score: Math.floor(Math.random() * 30) + 70 }
          ]
        };
        this.answered = true;
      }, 1500);
    },
    
    nextQuestion() {
      this.$emit('next');
      this.resetQuestion();
    },
    
    resetQuestion() {
      this.answer = null;
      this.multipleAnswer = [];
      this.textAnswer = "";
      this.answered = false;
      this.analysis = null;
      this.isRecording = false;
      this.recordingTime = 0;
      this.audioUrl = null;
      this.aiThinking = false;
      
      // 清除可能存在的音频URL
      if (this.audioUrl) {
        URL.revokeObjectURL(this.audioUrl);
        this.audioUrl = null;
      }
    },
    
    getCorrectAnswerText() {
      if (!this.question.options) return '';
      
      const correctOption = this.question.options.find(option => option.correct);
      return correctOption ? correctOption.text : '';
    },
    
    isCorrectOption(value) {
      if (!this.question.options) return false;
      
      const option = this.question.options.find(opt => opt.value === value);
      return option && option.correct;
    },
    
    getScoreColor(score) {
      if (score >= 90) return 'success';
      if (score >= 75) return 'primary';
      if (score >= 60) return 'warning';
      return 'error';
    },
    
    toggleRecording() {
      if (this.isRecording) {
        this.stopRecording();
      } else {
        this.startRecording();
      }
    },
    
    startRecording() {
      if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ audio: true })
          .then(stream => {
            this.audioRecorder = new MediaRecorder(stream);
            this.audioChunks = [];
            
            this.audioRecorder.addEventListener('dataavailable', event => {
              this.audioChunks.push(event.data);
            });
            
            this.audioRecorder.addEventListener('stop', () => {
              const audioBlob = new Blob(this.audioChunks);
              this.processAudioBlob(audioBlob);
            });
            
            this.audioRecorder.start();
            this.isRecording = true;
            
            // 设置音频可视化
            this.setupAudioVisualizer(stream);
            
            this.recordingTimer = setInterval(() => {
              this.recordingTime++;
              
              // 自动停止录音（最多60秒）
              if (this.recordingTime >= 60) {
                this.stopRecording();
              }
            }, 1000);
          })
          .catch(error => {
            console.error('获取麦克风权限失败:', error);
            this.$emit('error', '无法访问麦克风，请检查权限设置');
          });
      } else {
        this.$emit('error', '您的浏览器不支持录音功能');
      }
    },
    
    stopRecording() {
      if (this.audioRecorder && this.isRecording) {
        this.audioRecorder.stop();
        clearInterval(this.recordingTimer);
        this.isRecording = false;
        
        // 停止音频可视化
        this.stopAudioVisualizer();
        
        // 停止所有音轨
        this.audioRecorder.stream.getTracks().forEach(track => track.stop());
      }
    },
    
    processAudioBlob(audioBlob) {
      // 创建音频URL
      if (this.audioUrl) {
        URL.revokeObjectURL(this.audioUrl);
      }
      this.audioUrl = URL.createObjectURL(audioBlob);
      
      // 通知父组件正在处理音频
      this.$emit('processing-audio');
      
      // 模拟语音识别过程
      setTimeout(() => {
        // 模拟识别结果
        const recognizedText = "这是一个模拟的语音识别结果，实际应用中需要接入语音识别API。根据您的语音内容，我们分析您对问题有一定的理解，但可以提供更多细节和例子来支持您的观点。";
        this.textAnswer = recognizedText;
        this.$emit('audio-processed', recognizedText);
      }, 1500);
    },
    
    clearAudio() {
      if (this.audioUrl) {
        URL.revokeObjectURL(this.audioUrl);
        this.audioUrl = null;
      }
      this.textAnswer = "";
    },
    
    // 音频可视化相关方法
    setupAudioVisualizer(stream) {
      try {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const source = audioContext.createMediaStreamSource(stream);
        this.audioAnalyser = audioContext.createAnalyser();
        this.audioAnalyser.fftSize = 256;
        
        source.connect(this.audioAnalyser);
        
        const bufferLength = this.audioAnalyser.frequencyBinCount;
        this.audioDataArray = new Uint8Array(bufferLength);
        
        this.visualizerInterval = setInterval(() => {
          this.updateAudioVisualizer();
        }, 50);
      } catch (error) {
        console.error('设置音频可视化失败:', error);
      }
    },
    
    updateAudioVisualizer() {
      if (!this.audioAnalyser || !this.audioDataArray) return;
      
      this.audioAnalyser.getByteFrequencyData(this.audioDataArray);
      
      // 更新可视化条
      for (let i = 0; i < this.audioVisualizerBars.length; i++) {
        const index = Math.floor(i * this.audioDataArray.length / this.audioVisualizerBars.length);
        const value = this.audioDataArray[index];
        this.audioVisualizerBars.splice(i, 1, value / 2); // 0-128 范围转换为 0-64
      }
    },
    
    stopAudioVisualizer() {
      if (this.visualizerInterval) {
        clearInterval(this.visualizerInterval);
        this.visualizerInterval = null;
      }
      
      // 重置可视化条
      this.audioVisualizerBars = Array(50).fill(0);
    }
  },
  beforeDestroy() {
    if (this.recordingTimer) {
      clearInterval(this.recordingTimer);
    }
    
    if (this.visualizerInterval) {
      clearInterval(this.visualizerInterval);
    }
    
    if (this.isRecording && this.audioRecorder) {
      this.stopRecording();
    }
    
    if (this.audioUrl) {
      URL.revokeObjectURL(this.audioUrl);
    }
  }
};
</script>

<style scoped>
.interview-question {
  max-width: 800px;
  margin: 0 auto;
}

.question-content {
  padding: 20px;
}

.question-description {
  color: #666;
  font-style: italic;
}

/* AI问题区域 */
.ai-question-container {
  display: flex;
  align-items: flex-start;
}

.ai-question-bubble {
  background-color: rgba(25, 118, 210, 0.1);
  border-radius: 12px;
  padding: 16px;
  flex: 1;
  position: relative;
}

.ai-question-bubble:before {
  content: '';
  position: absolute;
  left: -8px;
  top: 16px;
  width: 0;
  height: 0;
  border-top: 8px solid transparent;
  border-bottom: 8px solid transparent;
  border-right: 8px solid rgba(25, 118, 210, 0.1);
}

.ai-thinking {
  margin-top: 8px;
}

/* 音频录制区域 */
.audio-container {
  background-color: rgba(0, 0, 0, 0.05);
  border-radius: 8px;
  padding: 16px;
  margin-top: 16px;
}

.audio-visualizer-container {
  display: flex;
  align-items: flex-end;
  height: 64px;
  background-color: rgba(0, 0, 0, 0.2);
  border-radius: 4px;
  padding: 0 8px;
  margin-bottom: 16px;
}

.audio-visualizer-bar {
  flex: 1;
  background-color: #f44336;
  margin: 0 1px;
  min-height: 2px;
  transition: height 0.1s ease;
}

.audio-player {
  width: 100%;
  margin-bottom: 8px;
}

.audio-info {
  display: flex;
  align-items: center;
  margin-top: 8px;
}

.recording-indicator {
  display: flex;
  align-items: center;
  color: #f44336;
  font-size: 14px;
}

.audio-status {
  display: flex;
  align-items: center;
  color: #4caf50;
  font-size: 14px;
}

/* 评分维度 */
.score-dimensions {
  background-color: rgba(0, 0, 0, 0.05);
  border-radius: 8px;
  padding: 16px;
}
</style> 