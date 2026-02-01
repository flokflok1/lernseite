<template>
  <div :class="loaderClasses">
    <div v-if="type === 'spinner'" class="spinner" :style="spinnerStyle">
      <svg class="animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
    </div>
    <div v-else-if="type === 'dots'" class="dots">
      <div class="dot"></div>
      <div class="dot"></div>
      <div class="dot"></div>
    </div>
    <div v-else-if="type === 'pulse'" class="pulse" :style="pulseStyle"></div>
    <p v-if="text" class="loader-text">{{ text }}</p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  type?: 'spinner' | 'dots' | 'pulse'
  size?: 'sm' | 'md' | 'lg' | 'xl'
  color?: 'primary' | 'white' | 'gray'
  text?: string
  fullscreen?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  type: 'spinner',
  size: 'md',
  color: 'primary',
  fullscreen: false,
})

const sizeMap = {
  sm: '1rem',
  md: '2rem',
  lg: '3rem',
  xl: '4rem',
}

const colorMap = {
  primary: 'var(--color-primary)',
  white: '#ffffff',
  gray: '#6b7280',
}

const loaderClasses = computed(() => {
  return [
    'loader',
    {
      'loader-fullscreen': props.fullscreen,
    },
  ]
})

const spinnerStyle = computed(() => {
  return {
    width: sizeMap[props.size],
    height: sizeMap[props.size],
    color: colorMap[props.color],
  }
})

const pulseStyle = computed(() => {
  return {
    width: sizeMap[props.size],
    height: sizeMap[props.size],
    backgroundColor: colorMap[props.color],
  }
})
</script>

<style scoped>
.loader {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
}

.loader-fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.9);
  z-index: 9998;
}

.spinner {
  display: inline-block;
}

.dots {
  display: flex;
  gap: 0.5rem;
}

.dot {
  width: 0.75rem;
  height: 0.75rem;
  background-color: var(--color-primary);
  border-radius: 50%;
  animation: dot-bounce 1.4s infinite ease-in-out both;
}

.dot:nth-child(1) { animation-delay: -0.32s; }
.dot:nth-child(2) { animation-delay: -0.16s; }

@keyframes dot-bounce {
  0%, 80%, 100% {
    transform: scale(0);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

.pulse {
  border-radius: 50%;
  animation: pulse-animation 1.5s ease-in-out infinite;
}

@keyframes pulse-animation {
  0%, 100% {
    opacity: 1;
    transform: scale(0.8);
  }
  50% {
    opacity: 0.5;
    transform: scale(1.2);
  }
}

.loader-text {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  margin-top: 0.5rem;
}
</style>
