<template>
  <div class="search-box-container">
    <div class="search-input-wrapper">
      <v-text-field
        outlined
        dense
        clearable
        color="white"
        v-model="searchTerm"
        placeholder="输入职位关键词"
        hide-details
        class="search-input no-hover dark-search-input"
        @keyup.enter="search"
        dark
        background-color="rgba(255,255,255,0.1)"
      >
        <template #prepend-inner>
          <v-icon size="18" color="white" class="search-icon">mdi-magnify</v-icon>
        </template>
        <template #append>
          <v-icon @click="voiceSearch" size="21" color="white">mdi-microphone</v-icon>
        </template>
      </v-text-field>

      <v-btn 
        color="white" 
        class="search-btn no-hover"
        height="40" 
        @click="search"
        :disabled="!searchTerm"
        dark
      >
        搜索
      </v-btn>
    </div>

    <v-dialog v-model="voiceDialog" max-width="400">
      <v-card>
        <v-card-title class="headline">语音搜索</v-card-title>
        <v-card-text>
          <div class="text-center">
            <v-icon size="80" :color="isListening ? 'red' : 'grey'">mdi-microphone</v-icon>
            <p class="mt-3">{{ voicePrompt }}</p>
          </div>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" text @click="toggleVoiceRecognition">
            {{ isListening ? '停止' : '开始' }}
          </v-btn>
          <v-btn color="grey" text @click="voiceDialog = false">
            取消
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
export default {
  name: "SearchBox",
  data: () => ({
    searchTerm: "",
    loading: false,
    voiceDialog: false,
    isListening: false,
    voicePrompt: "点击开始按钮开始语音搜索",
    recognition: null
  }),
  methods: {
    search() {
      if (!this.searchTerm) return
      
      const keyword = this.searchTerm.trim()
      
      this.$emit('search', {
        keyword: keyword
      })
      
      this.$router.push({
        path: '/job/list',
        query: { keyword: keyword }
      })
      
      // 搜索后清空输入框
      this.searchTerm = ""
    },
    
    voiceSearch() {
      // 检查浏览器是否支持语音识别
      if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        this.voiceDialog = true
        this.initSpeechRecognition()
      } else {
        this.$emit('error', '您的浏览器不支持语音识别功能')
      }
    },
    
    initSpeechRecognition() {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
      
      if (!this.recognition) {
        this.recognition = new SpeechRecognition()
        this.recognition.lang = 'zh-CN'
        this.recognition.continuous = false
        this.recognition.interimResults = false
        
        this.recognition.onresult = (event) => {
          const transcript = event.results[0][0].transcript
          this.searchTerm = transcript
          this.voicePrompt = `识别结果: "${transcript}"`
          setTimeout(() => {
            this.voiceDialog = false
            this.search()
          }, 1000)
        }
        
        this.recognition.onerror = (event) => {
          this.isListening = false
          this.voicePrompt = `识别错误: ${event.error}`
        }
        
        this.recognition.onend = () => {
          this.isListening = false
        }
      }
    },
    
    toggleVoiceRecognition() {
      if (this.isListening) {
        this.recognition.stop()
        this.isListening = false
        this.voicePrompt = "点击开始按钮开始语音搜索"
      } else {
        this.recognition.start()
        this.isListening = true
        this.voicePrompt = "正在聆听..."
      }
    }
  }
};
</script>

<style>
.search-box-container {
  display: flex;
  flex-direction: column;
  width: 100%;
}

.search-input-wrapper {
  display: flex;
  align-items: center;
}

.search-input {
  margin-bottom: 0 !important;
}

.dark-search-input :deep(.v-input__slot) {
  border-color: rgba(255, 255, 255, 0.3) !important;
}

.dark-search-input :deep(.v-label) {
  color: rgba(255, 255, 255, 0.7) !important;
}

.dark-search-input :deep(input) {
  color: white !important;
}

.dark-search-input :deep(.v-input__append-inner .v-icon),
.dark-search-input :deep(.v-input__prepend-inner .v-icon) {
  color: white !important;
}

.search-btn {
  margin-left: 12px;
}

.search-icon {
  margin-top: 2px !important;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  top: 1px;
}

.v-text-field.v-text-field--enclosed .v-text-field__prepend-inner {
  margin-top: 8px !important;
}

.transparent-scroll {
  scrollbar-width: thin;
  scrollbar-color: transparent;
}

.transparent-scroll::-webkit-scrollbar {
  width: 6px;
  background-color: transparent;
}

.transparent-scroll::-webkit-scrollbar-thumb {
  background: #d8dcde;
  border-radius: 4.5px;
}

.transparent-scroll::-webkit-scrollbar-track {
  background-color: transparent;
}

.no-hover {
  transition: none !important;
  transform: none !important;
}

.no-hover:hover {
  transform: none !important;
  box-shadow: none !important;
}
</style> 