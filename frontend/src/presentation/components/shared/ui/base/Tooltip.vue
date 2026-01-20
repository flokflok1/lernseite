<template>
  <div class="tooltip-wrapper" @mouseenter="show = true" @mouseleave="show = false">
    <slot></slot>
    <div v-if="show" :class="['tooltip', `tooltip-${position}`]">
      {{ text }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

defineProps<{
  text: string
  position?: 'top' | 'bottom' | 'left' | 'right'
}>()

const show = ref(false)
</script>

<style scoped>
.tooltip-wrapper {
  position: relative;
  display: inline-block;
}

.tooltip {
  position: absolute;
  background-color: #1f2937;
  color: white;
  padding: 0.5rem 0.75rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  white-space: nowrap;
  z-index: 1000;
  pointer-events: none;
}

.tooltip-top {
  bottom: calc(100% + 0.5rem);
  left: 50%;
  transform: translateX(-50%);
}

.tooltip-bottom {
  top: calc(100% + 0.5rem);
  left: 50%;
  transform: translateX(-50%);
}

.tooltip-left {
  right: calc(100% + 0.5rem);
  top: 50%;
  transform: translateY(-50%);
}

.tooltip-right {
  left: calc(100% + 0.5rem);
  top: 50%;
  transform: translateY(-50%);
}
</style>
