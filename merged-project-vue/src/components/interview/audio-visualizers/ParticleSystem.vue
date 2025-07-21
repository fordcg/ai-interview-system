<template>
  <div class="particle-system-container">
    <canvas 
      ref="canvas"
      :width="canvasSize.width"
      :height="canvasSize.height"
      class="particle-canvas"
    ></canvas>
  </div>
</template>

<script>
export default {
  name: 'ParticleSystem',
  props: {
    audioStream: {
      type: MediaStream,
      default: null
    },
    width: {
      type: Number,
      default: 800
    },
    height: {
      type: Number,
      default: 600
    },
    particleCount: {
      type: Number,
      default: 800
    },
    colorScheme: {
      type: String,
      default: 'blue',
      validator: value => ['blue', 'purple', 'green', 'rainbow', 'white'].includes(value)
    }
  },
  data() {
    return {
      audioContext: null,
      analyser: null,
      dataArray: null,
      animationId: null,
      canvas: null,
      ctx: null,
      particles: [],
      currentVolume: 0,
      bassLevel: 0,
      midLevel: 0,
      trebleLevel: 0,
      isInitialized: false
    }
  },
  computed: {
    canvasSize() {
      return {
        width: this.width,
        height: this.height
      }
    },
    colorPalette() {
      const palettes = {
        blue: ['#1e3c72', '#2a5298', '#3498db', '#74b9ff', '#00cec9'],
        purple: ['#667eea', '#764ba2', '#a855f7', '#c084fc', '#e879f9'],
        green: ['#11998e', '#38ef7d', '#00b894', '#55efc4', '#26de81'],
        rainbow: ['#ff6b6b', '#feca57', '#48dbfb', '#ff9ff3', '#54a0ff'],
        white: ['#ffffff', '#f8f9fa', '#e9ecef', '#dee2e6', '#ced4da']
      }
      return palettes[this.colorScheme] || palettes.blue
    }
  },
  watch: {
    audioStream: {
      handler(newStream) {
        if (newStream) {
          this.initAudioAnalyzer()
        } else {
          this.stopAnalyzer()
        }
      },
      immediate: true
    }
  },
  mounted() {
    this.initCanvas()
    this.initParticles()
    this.startAnimation()
  },
  beforeDestroy() {
    this.stopAnalyzer()
  },
  methods: {
    initCanvas() {
      this.canvas = this.$refs.canvas
      if (!this.canvas) return
      
      this.ctx = this.canvas.getContext('2d')
      
      // 设置高DPI支持
      const dpr = window.devicePixelRatio || 1
      this.canvas.width = this.width * dpr
      this.canvas.height = this.height * dpr
      this.ctx.scale(dpr, dpr)
    },
    
    async initAudioAnalyzer() {
      if (!this.audioStream || this.isInitialized) return
      
      try {
        this.audioContext = new (window.AudioContext || window.webkitAudioContext)()
        const source = this.audioContext.createMediaStreamSource(this.audioStream)
        
        this.analyser = this.audioContext.createAnalyser()
        this.analyser.fftSize = 512
        this.analyser.smoothingTimeConstant = 0.7
        
        source.connect(this.analyser)
        
        const bufferLength = this.analyser.frequencyBinCount
        this.dataArray = new Uint8Array(bufferLength)
        
        this.isInitialized = true
        
      } catch (error) {
        console.error('音频分析器初始化失败:', error)
        this.$emit('error', error)
      }
    },
    
    initParticles() {
      this.particles = []
      for (let i = 0; i < this.particleCount; i++) {
        this.particles.push(this.createParticle(i))
      }
    },
    
    createParticle(index = 0) {
      const centerX = this.width / 2
      const centerY = this.height / 2

      // 均匀的角度分布
      const baseAngle = (index / this.particleCount) * Math.PI * 2
      const randomOffset = (Math.random() - 0.5) * 0.3
      const angle = baseAngle + randomOffset

      // 甜甜圈形状：缩小甜甜圈
      const innerRadius = 35
      const outerRadius = 55
      const ringWidth = outerRadius - innerRadius

      // 粒子在环形带内随机分布
      const radiusInRing = Math.random() * ringWidth + innerRadius

      // 散开时的距离减小到30px
      const maxSpreadDistance = radiusInRing + 30

      return {
        // 当前位置（在甜甜圈内）
        x: centerX + Math.cos(angle) * radiusInRing,
        y: centerY + Math.sin(angle) * radiusInRing,

        // 中心位置
        centerX: centerX,
        centerY: centerY,

        // 甜甜圈属性
        originalRadius: radiusInRing, // 原始半径位置
        innerRadius: innerRadius,
        outerRadius: outerRadius,

        // 散开时的目标位置（小幅度）
        maxSpreadDistance: maxSpreadDistance,

        // 移动速度
        vx: 0,
        vy: 0,

        // 外观属性
        size: 1.2, // 统一粒子大小为1.2px
        originalSize: 1.2,
        color: this.colorPalette[Math.floor(Math.random() * this.colorPalette.length)],
        alpha: 1.0, // 完全不透明
        originalAlpha: 1.0,

        // 动画属性
        angle: angle,
        frequency: Math.random() * 0.02 + 0.01,
        phase: Math.random() * Math.PI * 2,

        // 散开状态
        shouldSpread: false,
        spreadIndex: index // 用于决定散开顺序
      }
    },
    
    startAnimation() {
      const animate = () => {
        if (this.analyser && this.dataArray) {
          this.analyser.getByteFrequencyData(this.dataArray)
          this.updateAudioLevels()
        }
        
        this.updateParticles()
        this.drawParticles()
        this.animationId = requestAnimationFrame(animate)
      }
      
      animate()
    },
    
    updateAudioLevels() {
      if (!this.dataArray) return
      
      // 计算整体音量
      const volume = this.dataArray.reduce((sum, value) => sum + value, 0) / this.dataArray.length
      this.currentVolume = (volume / 255) * 100
      
      // 分频段分析
      const third = Math.floor(this.dataArray.length / 3)
      
      // 低频 (Bass)
      const bassData = this.dataArray.slice(0, third)
      this.bassLevel = bassData.reduce((sum, value) => sum + value, 0) / bassData.length / 255
      
      // 中频 (Mid)
      const midData = this.dataArray.slice(third, third * 2)
      this.midLevel = midData.reduce((sum, value) => sum + value, 0) / midData.length / 255
      
      // 高频 (Treble)
      const trebleData = this.dataArray.slice(third * 2)
      this.trebleLevel = trebleData.reduce((sum, value) => sum + value, 0) / trebleData.length / 255
      
      this.$emit('audio-levels', {
        volume: this.currentVolume,
        bass: this.bassLevel,
        mid: this.midLevel,
        treble: this.trebleLevel
      })
    },
    
    updateParticles() {
      // 根据音量决定散开的粒子数量
      const audioInfluence = this.currentVolume / 100

      this.particles.forEach((particle) => {
        // 定义外部区域：只有外部70%的环形区域的粒子可以散开
        const outerThreshold = particle.innerRadius + (particle.outerRadius - particle.innerRadius) * 0.3

        // 只有外部的粒子才能散开
        const isOuterParticle = particle.originalRadius > outerThreshold

        // 根据音量和位置决定是否散开 - 提高阈值避免微弱声音触发
        const spreadIntensity = Math.min(audioInfluence * 2, 1)
        particle.shouldSpread = isOuterParticle && audioInfluence > 0.15 && Math.random() < spreadIntensity

        let targetX, targetY

        if (particle.shouldSpread) {
          // 散开的粒子：向外散开，无震动
          const spreadDistance = particle.maxSpreadDistance

          targetX = particle.centerX + Math.cos(particle.angle) * spreadDistance
          targetY = particle.centerY + Math.sin(particle.angle) * spreadDistance
        } else {
          // 保持在甜甜圈内的粒子：静止不动，无旋转
          targetX = particle.centerX + Math.cos(particle.angle) * particle.originalRadius
          targetY = particle.centerY + Math.sin(particle.angle) * particle.originalRadius
        }

        // 平滑移动到目标位置 - 进一步减慢散开速度
        const moveSpeed = particle.shouldSpread ? 0.03 : 0.02

        particle.vx = (targetX - particle.x) * moveSpeed
        particle.vy = (targetY - particle.y) * moveSpeed

        particle.x += particle.vx
        particle.y += particle.vy

        // 保持统一大小和完全不透明
        particle.size = particle.originalSize // 统一大小2px
        particle.alpha = 1.0 // 完全不透明
      })
    },
    
    resetParticle(particle) {
      // 重新设置粒子在甜甜圈内的位置
      const angle = Math.random() * Math.PI * 2
      const ringWidth = particle.outerRadius - particle.innerRadius
      const radiusInRing = Math.random() * ringWidth + particle.innerRadius

      // 更新位置和属性
      particle.angle = angle
      particle.originalRadius = radiusInRing
      particle.maxSpreadDistance = radiusInRing + 30

      // 重置颜色
      particle.color = this.colorPalette[Math.floor(Math.random() * this.colorPalette.length)]
    },
    
    drawParticles() {
      if (!this.ctx) return
      
      // 清除画布
      this.ctx.clearRect(0, 0, this.width, this.height)

      // 绘制粒子
      this.particles.forEach(particle => {
        this.ctx.save()
        
        // 设置粒子样式
        this.ctx.globalAlpha = particle.alpha
        this.ctx.fillStyle = particle.color
        
        // 绘制粒子主体
        this.ctx.beginPath()
        this.ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2)
        this.ctx.fill()
        
        this.ctx.restore()
      })
    },
    

    
    stopAnalyzer() {
      if (this.animationId) {
        cancelAnimationFrame(this.animationId)
        this.animationId = null
      }
      
      if (this.audioContext && this.audioContext.state !== 'closed') {
        this.audioContext.close()
      }
      
      this.audioContext = null
      this.analyser = null
      this.dataArray = null
      this.isInitialized = false
    }
  }
}
</script>

<style scoped>
.particle-system-container {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.particle-canvas {
  display: block;
  width: 100%;
  height: 100%;
}
</style>
