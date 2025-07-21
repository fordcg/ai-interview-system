<template>
  <transition name="popup-animation">
    <div 
      v-if="visible" 
      class="animated-popup"
      :class="[`popup-${position}`, contentClass]"
      :style="{ zIndex: zIndex }"
    >
      <div class="popup-inner" :class="innerClass">
        <div class="popup-header" v-if="title">
          <h3 class="popup-title">{{ title }}</h3>
          <v-btn 
            v-if="closable" 
            icon 
            small 
            @click="$emit('close')"
            class="popup-close"
          >
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </div>
        <div class="popup-content">
          <slot></slot>
        </div>
      </div>
    </div>
  </transition>
</template>

<script>
export default {
  name: 'AnimatedPopup',
  props: {
    visible: {
      type: Boolean,
      required: true,
      default: false
    },
    title: {
      type: String,
      default: ''
    },
    position: {
      type: String,
      default: 'center',
      validator: value => ['center', 'left', 'right', 'top', 'bottom'].includes(value)
    },
    closable: {
      type: Boolean,
      default: true
    },
    zIndex: {
      type: [Number, String],
      default: 10
    },
    contentClass: {
      type: String,
      default: ''
    },
    innerClass: {
      type: String,
      default: ''
    }
  },
  mounted() {
    if (this.visible) {
      this.onOpen();
    }
  },
  methods: {
    onOpen() {
      // 可以在此添加弹出时的额外逻辑，比如触发动画或发出事件
      this.$emit('opened');
    }
  },
  watch: {
    visible(newVal) {
      if (newVal) {
        this.onOpen();
      } else {
        this.$emit('closed');
      }
    }
  }
}
</script>

<style scoped>
.animated-popup {
  position: absolute;
  overflow: hidden;
}

.popup-inner {
  background-color: #ffffff;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  max-height: 100%;
  width: 100%;
}

.popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.popup-title {
  margin: 0;
  font-size: 18px;
  font-weight: 500;
}

.popup-content {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
}

.no-padding .popup-content {
  padding: 0;
}

/* 位置变体 */
.popup-center {
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  max-width: 90%;
  width: auto;
}

.popup-left {
  top: 0;
  left: 0;
  height: 100%;
  max-width: 90%;
}

.popup-right {
  top: 0;
  right: 0;
  height: 100%;
  max-width: 90%;
}

.popup-top {
  top: 0;
  left: 0;
  width: 100%;
  max-height: 90%;
}

.popup-bottom {
  bottom: 0;
  left: 0;
  width: 100%;
  max-height: 90%;
}

/* 动画效果 */
.popup-animation-enter-active,
.popup-animation-leave-active {
  transition: all 0.4s cubic-bezier(0.5, 0, 0.15, 1.35);
}

/* 中央弹出 */
.popup-center.popup-animation-enter,
.popup-center.popup-animation-leave-to {
  opacity: 0;
  transform: translate(-50%, -50%) scale(0.7);
}

/* 左侧弹出 */
.popup-left.popup-animation-enter,
.popup-left.popup-animation-leave-to {
  opacity: 0;
  transform: translateX(-100%);
}

/* 右侧弹出 */
.popup-right.popup-animation-enter,
.popup-right.popup-animation-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

/* 顶部弹出 */
.popup-top.popup-animation-enter,
.popup-top.popup-animation-leave-to {
  opacity: 0;
  transform: translateY(-100%);
}

/* 底部弹出 */
.popup-bottom.popup-animation-enter,
.popup-bottom.popup-animation-leave-to {
  opacity: 0;
  transform: translateY(100%);
}

/* 深色模式 */
.popup-dark .popup-inner {
  background-color: #212121;
  color: white;
  border: none;
  box-shadow: none;
  border-radius: 0;
}

.popup-dark .popup-header {
  border-color: rgba(255, 255, 255, 0.1);
}

/* 完全黑色模式 */
.full-black {
  background-color: #212121 !important;
}

.full-black.popup-inner {
  background-color: #212121 !important;
  color: white;
  border: none !important;
  box-shadow: none !important;
  border-radius: 0 !important;
  margin: 0 !important;
  padding: 0 !important;
  overflow: hidden !important;
}

.full-black .popup-content {
  background-color: #212121 !important;
  padding: 0 !important;
  margin: 0 !important;
}

/* 响应式调整 */
@media (max-width: 600px) {
  .popup-left, .popup-right {
    width: 100%;
    max-width: 100%;
  }
  
  .popup-content {
    padding: 16px;
  }
}
</style> 