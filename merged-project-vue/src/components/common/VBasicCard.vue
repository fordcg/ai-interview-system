<template>
  <v-card :color="color" :light="light" :dark="dark" :elevation="elevation" class="v-basic-card">
    <v-card-title
      v-if="showHeader"
      :class="[titleClass, 'px-4 py-3']"
    >
      {{ title }}
      <v-spacer></v-spacer>
      <slot name="toolbar-actions"></slot>
    </v-card-title>
    <v-divider v-if="showHeader && showDivider"></v-divider>
    <v-card-text :class="contentClass">
      <slot name="card-content"></slot>
    </v-card-text>
    <v-card-actions v-if="$slots['card-actions']">
      <slot name="card-actions"></slot>
    </v-card-actions>
  </v-card>
</template>

<script>
export default {
  name: 'VBasicCard',
  props: {
    showHeader: {
      type: Boolean,
      default: true,
    },
    showDivider: {
      type: Boolean,
      default: true,
    },
    toolbarHeight: {
      type: [Number, String],
      default: undefined,
    },
    title: {
      type: String,
      default: '',
    },
    color: {
      type: String,
      default: 'white',
    },
    headerColor: {
      type: String,
      default: 'transparent',
    },
    light: {
      type: Boolean,
      default: false,
    },
    dark: {
      type: Boolean,
      default: false,
    },
    headerDark: {
      type: Boolean,
      default: false,
    },
    elevation: {
      type: [Number, String],
      default: 2,
    },
    titleClass: {
      type: String,
      default: 'text-h6',
    },
    contentClass: {
      type: String,
      default: '',
    }
  },
};
</script>

<style scoped>
.v-basic-card {
  border-radius: 15px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.08) !important;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1) !important;
  position: relative;
}

.v-basic-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0));
  z-index: 0;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.v-basic-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.3) !important;
  background: rgba(255, 255, 255, 0.12) !important;
}

.v-basic-card:hover::before {
  opacity: 1;
}

.v-basic-card .v-card__title {
  padding: 16px 20px;
  font-size: 18px;
  font-weight: 500;
  background: linear-gradient(to right, var(--success), var(--primary));
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.v-basic-card .v-card__title::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 20px;
  width: 40px;
  height: 3px;
  background: linear-gradient(to right, var(--success), var(--primary));
  border-radius: 3px;
  transition: width 0.3s ease;
}

.v-basic-card:hover .v-card__title::after {
  width: 60px;
}

.v-basic-card .v-card__text {
  padding: 20px;
  position: relative;
  z-index: 1;
}

.v-basic-card .v-card__actions {
  padding: 12px 20px;
  position: relative;
  z-index: 1;
}
</style> 