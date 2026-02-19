<script setup lang="ts">
/**
 * AnimatedTeacher - Professional 2D Animated Character
 *
 * High-quality illustrated character like Studyflix/Simpleclub
 * - Canvas-based rendering for smooth animations
 * - Professional business/teacher appearance
 * - Lip-sync animation
 * - Gesture animations (pointing, waving)
 * - Blinking and idle animations
 *
 * Uses composables: useTeacherAnimation, useTeacherDrawing
 */

import { ref, toRef, onMounted, onUnmounted } from 'vue'
import { useTeacherAnimation } from './composables/useTeacherAnimation'
import { useTeacherDrawing } from './composables/useTeacherDrawing'

const props = defineProps<{
  isSpeaking?: boolean
  isPointing?: boolean
  mood?: 'neutral' | 'happy' | 'thinking'
}>()

const canvas = ref<HTMLCanvasElement | null>(null)
let ctx: CanvasRenderingContext2D | null = null
let animationId: number | null = null

const {
  time,
  isBlinking,
  mouthOpenAmount,
  updateAnimations
} = useTeacherAnimation({
  isSpeaking: toRef(() => props.isSpeaking ?? false),
  isPointing: toRef(() => props.isPointing ?? false)
})

const { drawCharacter } = useTeacherDrawing()

function initCanvas(): void {
  if (!canvas.value) return

  ctx = canvas.value.getContext('2d')
  if (!ctx) return

  canvas.value.width = 500
  canvas.value.height = 550

  animate()
}

function animate(): void {
  if (!ctx || !canvas.value) return

  updateAnimations()

  ctx.clearRect(0, 0, canvas.value.width, canvas.value.height)

  drawCharacter({
    ctx,
    time: time.value,
    isPointing: props.isPointing ?? false,
    isBlinking: isBlinking.value,
    mouthOpenAmount: mouthOpenAmount.value
  })

  animationId = requestAnimationFrame(animate)
}

onMounted(() => {
  initCanvas()
})

onUnmounted(() => {
  if (animationId) {
    cancelAnimationFrame(animationId)
  }
})
</script>

<template>
  <div class="animated-teacher">
    <canvas ref="canvas" class="teacher-canvas"></canvas>
  </div>
</template>

<style scoped>
.animated-teacher {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.teacher-canvas {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}
</style>
