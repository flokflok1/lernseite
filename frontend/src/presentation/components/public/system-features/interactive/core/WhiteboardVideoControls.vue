<!--
  WhiteboardVideoControls - Video-style playback controls
  Extracted from WhiteboardTutorLesson for quality gate G01 compliance.
-->

<template>
  <div class="video-controls">
    <div class="controls-left">
      <button @click="$emit('toggle-play')" class="control-btn play-btn">
        <span v-if="isPaused">&#9654;</span>
        <span v-else>&#9208;</span>
      </button>
      <button @click="$emit('previous')" class="control-btn" :disabled="!hasPrevious">
        &#9198;
      </button>
      <button @click="$emit('next')" class="control-btn" :disabled="!hasNext">
        &#9197;
      </button>
    </div>

    <div class="controls-center">
      <div class="progress-bar">
        <div
          class="progress-fill"
          :style="{ width: `${progressPercent}%` }"
        ></div>
      </div>
      <span class="progress-time">{{ currentStep }} / {{ totalSteps }}</span>
    </div>

    <div class="controls-right">
      <button
        v-if="showCalculatorButton"
        @click="$emit('toggle-calculator')"
        class="control-btn calc-btn"
        :class="{ active: calculatorActive }"
      >
        &#129518;
      </button>
      <button @click="$emit('exit')" class="control-btn close-btn">&#10005;</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  isPaused: boolean
  hasPrevious: boolean
  hasNext: boolean
  currentStep: number
  totalSteps: number
  showCalculatorButton: boolean
  calculatorActive: boolean
}>()

defineEmits<{
  (e: 'toggle-play'): void
  (e: 'previous'): void
  (e: 'next'): void
  (e: 'toggle-calculator'): void
  (e: 'exit'): void
}>()

const progressPercent = computed((): number => {
  if (props.totalSteps === 0) return 0
  return (props.currentStep / props.totalSteps) * 100
})
</script>

<style scoped>
.video-controls {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  background: linear-gradient(0deg, rgba(0,0,0,0.8) 0%, rgba(0,0,0,0.4) 70%, transparent 100%);
  z-index: 20;
}

.controls-left,
.controls-right {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.controls-center {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0 1.5rem;
}

.control-btn {
  width: 36px;
  height: 36px;
  background: rgba(255, 255, 255, 0.15);
  border: none;
  border-radius: 50%;
  color: white;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.control-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.25);
  transform: scale(1.1);
}

.control-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.play-btn {
  width: 44px;
  height: 44px;
  background: white;
  color: #1e293b;
  font-size: 1.25rem;
}

.play-btn:hover {
  background: #f1f5f9;
}

.calc-btn.active {
  background: #f59e0b;
}

.close-btn:hover {
  background: rgba(239, 68, 68, 0.5);
}

.progress-bar {
  flex: 1;
  height: 4px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #60a5fa;
  border-radius: 2px;
  transition: width 0.3s ease;
}

.progress-time {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.8125rem;
  white-space: nowrap;
}
</style>
