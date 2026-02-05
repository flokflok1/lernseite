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
 */

import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps<{
  isSpeaking?: boolean
  isPointing?: boolean
  mood?: 'neutral' | 'happy' | 'thinking'
}>()

const canvas = ref<HTMLCanvasElement | null>(null)
let ctx: CanvasRenderingContext2D | null = null
let animationId: number | null = null

// Animation state
let time = 0
let blinkTimer = 0
let nextBlinkTime = 3
let isBlinking = false
let mouthOpenAmount = 0
let targetMouthOpen = 0
let armAngle = 0
let targetArmAngle = 0

// Character colors (Professional teacher look)
const colors = {
  skin: '#F5D0C5',
  skinShadow: '#E8B5A4',
  hair: '#4A3728',
  hairHighlight: '#5D4A3A',
  shirt: '#5B8DBE',
  shirtShadow: '#4A7AAD',
  vest: '#8B5A3C',
  vestShadow: '#7A4A2C',
  tie: '#C44536',
  glasses: '#2D3748',
  eyeWhite: '#FFFFFF',
  iris: '#5D4E37',
  pupil: '#1A1A1A',
  mouth: '#A04030',
  teeth: '#FFFFFF',
  beard: '#3D2E22'
}

const initCanvas = () => {
  if (!canvas.value) return

  ctx = canvas.value.getContext('2d')
  if (!ctx) return

  // Set canvas size - wider to accommodate pointing arm
  canvas.value.width = 500
  canvas.value.height = 550

  // Start animation loop
  animate()
}

const animate = () => {
  if (!ctx || !canvas.value) return

  time += 0.016 // ~60fps

  // Update animations
  updateBlink()
  updateMouth()
  updateArm()

  // Clear and draw
  ctx.clearRect(0, 0, canvas.value.width, canvas.value.height)
  drawCharacter()

  animationId = requestAnimationFrame(animate)
}

const updateBlink = () => {
  blinkTimer += 0.016

  if (!isBlinking && blinkTimer > nextBlinkTime) {
    isBlinking = true
    setTimeout(() => {
      isBlinking = false
      blinkTimer = 0
      nextBlinkTime = 2 + Math.random() * 3
    }, 150)
  }
}

const updateMouth = () => {
  if (props.isSpeaking) {
    // Natural speech pattern
    const speechWave = Math.sin(time * 12) * 0.3 +
                       Math.sin(time * 7.3) * 0.2 +
                       Math.sin(time * 18.7) * 0.15
    targetMouthOpen = 0.3 + Math.max(0, speechWave) * 0.5
  } else {
    targetMouthOpen = 0
  }

  // Smooth interpolation
  mouthOpenAmount += (targetMouthOpen - mouthOpenAmount) * 0.3
}

const updateArm = () => {
  if (props.isPointing) {
    targetArmAngle = -0.8 // Raised position
  } else {
    targetArmAngle = 0.3 // Relaxed position
  }

  armAngle += (targetArmAngle - armAngle) * 0.1
}

const drawCharacter = () => {
  if (!ctx) return

  // Center X - shifted left a bit to make room for pointing arm
  const cx = props.isPointing ? 180 : 220
  const cy = 300 // Center Y (upper body focus)

  ctx.save()

  // Subtle idle animation
  const idleBob = Math.sin(time * 2) * 2
  ctx.translate(0, idleBob)

  // Draw in order (back to front)
  drawBody(cx, cy)
  drawLeftArm(cx, cy)
  drawRightArm(cx, cy)
  drawHead(cx, cy - 120)

  ctx.restore()
}

const drawBody = (cx: number, cy: number) => {
  if (!ctx) return

  // Torso / Shirt
  ctx.fillStyle = colors.shirt
  ctx.beginPath()
  ctx.moveTo(cx - 70, cy - 60)
  ctx.quadraticCurveTo(cx - 80, cy + 80, cx - 60, cy + 120)
  ctx.lineTo(cx + 60, cy + 120)
  ctx.quadraticCurveTo(cx + 80, cy + 80, cx + 70, cy - 60)
  ctx.quadraticCurveTo(cx, cy - 80, cx - 70, cy - 60)
  ctx.fill()

  // Shirt shadow
  ctx.fillStyle = colors.shirtShadow
  ctx.beginPath()
  ctx.moveTo(cx - 30, cy - 40)
  ctx.quadraticCurveTo(cx - 40, cy + 40, cx - 35, cy + 120)
  ctx.lineTo(cx - 60, cy + 120)
  ctx.quadraticCurveTo(cx - 80, cy + 80, cx - 70, cy - 60)
  ctx.quadraticCurveTo(cx - 50, cy - 70, cx - 30, cy - 40)
  ctx.fill()

  // Vest
  ctx.fillStyle = colors.vest
  ctx.beginPath()
  ctx.moveTo(cx - 55, cy - 50)
  ctx.lineTo(cx - 45, cy + 100)
  ctx.lineTo(cx - 15, cy + 100)
  ctx.lineTo(cx - 5, cy - 30)
  ctx.quadraticCurveTo(cx - 30, cy - 40, cx - 55, cy - 50)
  ctx.fill()

  ctx.beginPath()
  ctx.moveTo(cx + 55, cy - 50)
  ctx.lineTo(cx + 45, cy + 100)
  ctx.lineTo(cx + 15, cy + 100)
  ctx.lineTo(cx + 5, cy - 30)
  ctx.quadraticCurveTo(cx + 30, cy - 40, cx + 55, cy - 50)
  ctx.fill()

  // Vest buttons
  ctx.fillStyle = colors.vestShadow
  for (let i = 0; i < 3; i++) {
    ctx.beginPath()
    ctx.arc(cx - 10, cy + 10 + i * 30, 5, 0, Math.PI * 2)
    ctx.fill()
  }

  // Collar
  ctx.fillStyle = colors.shirt
  ctx.beginPath()
  ctx.moveTo(cx - 30, cy - 60)
  ctx.lineTo(cx, cy - 30)
  ctx.lineTo(cx + 30, cy - 60)
  ctx.lineTo(cx + 20, cy - 70)
  ctx.lineTo(cx, cy - 50)
  ctx.lineTo(cx - 20, cy - 70)
  ctx.closePath()
  ctx.fill()

  // Tie
  ctx.fillStyle = colors.tie
  ctx.beginPath()
  ctx.moveTo(cx - 8, cy - 55)
  ctx.lineTo(cx + 8, cy - 55)
  ctx.lineTo(cx + 12, cy + 50)
  ctx.lineTo(cx, cy + 70)
  ctx.lineTo(cx - 12, cy + 50)
  ctx.closePath()
  ctx.fill()

  // Tie knot
  ctx.beginPath()
  ctx.moveTo(cx - 12, cy - 55)
  ctx.lineTo(cx + 12, cy - 55)
  ctx.lineTo(cx + 8, cy - 40)
  ctx.lineTo(cx - 8, cy - 40)
  ctx.closePath()
  ctx.fill()
}

const drawLeftArm = (cx: number, cy: number) => {
  if (!ctx) return

  // Left arm - relaxed at side
  ctx.save()

  // Upper arm
  ctx.fillStyle = colors.shirt
  ctx.beginPath()
  ctx.moveTo(cx - 65, cy - 40)
  ctx.quadraticCurveTo(cx - 90, cy, cx - 85, cy + 50)
  ctx.quadraticCurveTo(cx - 80, cy + 60, cx - 70, cy + 55)
  ctx.quadraticCurveTo(cx - 55, cy + 10, cx - 50, cy - 35)
  ctx.closePath()
  ctx.fill()

  // Forearm
  ctx.fillStyle = colors.shirt
  ctx.beginPath()
  ctx.moveTo(cx - 85, cy + 45)
  ctx.quadraticCurveTo(cx - 95, cy + 80, cx - 90, cy + 110)
  ctx.quadraticCurveTo(cx - 85, cy + 120, cx - 75, cy + 115)
  ctx.quadraticCurveTo(cx - 65, cy + 85, cx - 70, cy + 50)
  ctx.closePath()
  ctx.fill()

  // Hand
  ctx.fillStyle = colors.skin
  ctx.beginPath()
  ctx.ellipse(cx - 82, cy + 125, 16, 20, 0.1, 0, Math.PI * 2)
  ctx.fill()

  // Fingers
  ctx.beginPath()
  ctx.ellipse(cx - 90, cy + 140, 5, 10, 0.2, 0, Math.PI * 2)
  ctx.fill()
  ctx.beginPath()
  ctx.ellipse(cx - 82, cy + 145, 5, 12, 0, 0, Math.PI * 2)
  ctx.fill()
  ctx.beginPath()
  ctx.ellipse(cx - 74, cy + 143, 5, 11, -0.1, 0, Math.PI * 2)
  ctx.fill()

  ctx.restore()
}

const drawRightArm = (cx: number, cy: number) => {
  if (!ctx) return

  ctx.save()

  if (props.isPointing) {
    // Pointing pose - arm raised toward right

    // Upper arm
    ctx.fillStyle = colors.shirt
    ctx.beginPath()
    ctx.moveTo(cx + 65, cy - 40)
    ctx.quadraticCurveTo(cx + 100, cy - 50, cx + 130, cy - 40)
    ctx.quadraticCurveTo(cx + 140, cy - 35, cx + 135, cy - 25)
    ctx.quadraticCurveTo(cx + 100, cy - 30, cx + 55, cy - 25)
    ctx.closePath()
    ctx.fill()

    // Forearm extending right
    ctx.fillStyle = colors.shirt
    ctx.beginPath()
    ctx.moveTo(cx + 130, cy - 40)
    ctx.quadraticCurveTo(cx + 170, cy - 50, cx + 200, cy - 45)
    ctx.quadraticCurveTo(cx + 210, cy - 40, cx + 205, cy - 30)
    ctx.quadraticCurveTo(cx + 170, cy - 35, cx + 135, cy - 25)
    ctx.closePath()
    ctx.fill()

    // Hand pointing
    ctx.fillStyle = colors.skin
    ctx.beginPath()
    ctx.ellipse(cx + 215, cy - 38, 18, 15, 0.2, 0, Math.PI * 2)
    ctx.fill()

    // Pointing finger
    ctx.fillStyle = colors.skin
    ctx.beginPath()
    ctx.moveTo(cx + 228, cy - 42)
    ctx.lineTo(cx + 260, cy - 50)
    ctx.quadraticCurveTo(cx + 265, cy - 48, cx + 263, cy - 43)
    ctx.lineTo(cx + 232, cy - 35)
    ctx.closePath()
    ctx.fill()

    // Other fingers curled
    ctx.beginPath()
    ctx.ellipse(cx + 222, cy - 28, 8, 6, 0.3, 0, Math.PI * 2)
    ctx.fill()

  } else {
    // Relaxed pose - arm at side (mirrored from left)

    // Upper arm
    ctx.fillStyle = colors.shirt
    ctx.beginPath()
    ctx.moveTo(cx + 65, cy - 40)
    ctx.quadraticCurveTo(cx + 90, cy, cx + 85, cy + 50)
    ctx.quadraticCurveTo(cx + 80, cy + 60, cx + 70, cy + 55)
    ctx.quadraticCurveTo(cx + 55, cy + 10, cx + 50, cy - 35)
    ctx.closePath()
    ctx.fill()

    // Forearm
    ctx.fillStyle = colors.shirt
    ctx.beginPath()
    ctx.moveTo(cx + 85, cy + 45)
    ctx.quadraticCurveTo(cx + 95, cy + 80, cx + 90, cy + 110)
    ctx.quadraticCurveTo(cx + 85, cy + 120, cx + 75, cy + 115)
    ctx.quadraticCurveTo(cx + 65, cy + 85, cx + 70, cy + 50)
    ctx.closePath()
    ctx.fill()

    // Hand
    ctx.fillStyle = colors.skin
    ctx.beginPath()
    ctx.ellipse(cx + 82, cy + 125, 16, 20, -0.1, 0, Math.PI * 2)
    ctx.fill()

    // Fingers
    ctx.beginPath()
    ctx.ellipse(cx + 90, cy + 140, 5, 10, -0.2, 0, Math.PI * 2)
    ctx.fill()
    ctx.beginPath()
    ctx.ellipse(cx + 82, cy + 145, 5, 12, 0, 0, Math.PI * 2)
    ctx.fill()
    ctx.beginPath()
    ctx.ellipse(cx + 74, cy + 143, 5, 11, 0.1, 0, Math.PI * 2)
    ctx.fill()
  }

  ctx.restore()
}

const drawHead = (cx: number, cy: number) => {
  if (!ctx) return

  // Neck
  ctx.fillStyle = colors.skin
  ctx.beginPath()
  ctx.ellipse(cx, cy + 70, 25, 30, 0, 0, Math.PI * 2)
  ctx.fill()

  // Head shape
  ctx.fillStyle = colors.skin
  ctx.beginPath()
  ctx.ellipse(cx, cy, 65, 80, 0, 0, Math.PI * 2)
  ctx.fill()

  // Head shadow (left side)
  ctx.fillStyle = colors.skinShadow
  ctx.beginPath()
  ctx.ellipse(cx - 30, cy + 10, 30, 60, 0.2, Math.PI * 0.5, Math.PI * 1.5)
  ctx.fill()

  // Ears
  ctx.fillStyle = colors.skin
  ctx.beginPath()
  ctx.ellipse(cx - 62, cy, 12, 20, 0, 0, Math.PI * 2)
  ctx.fill()
  ctx.beginPath()
  ctx.ellipse(cx + 62, cy, 12, 20, 0, 0, Math.PI * 2)
  ctx.fill()

  // Ear inner
  ctx.fillStyle = colors.skinShadow
  ctx.beginPath()
  ctx.ellipse(cx - 60, cy, 6, 12, 0, 0, Math.PI * 2)
  ctx.fill()
  ctx.beginPath()
  ctx.ellipse(cx + 60, cy, 6, 12, 0, 0, Math.PI * 2)
  ctx.fill()

  // Hair
  ctx.fillStyle = colors.hair
  ctx.beginPath()
  ctx.moveTo(cx - 60, cy - 20)
  ctx.quadraticCurveTo(cx - 65, cy - 70, cx, cy - 85)
  ctx.quadraticCurveTo(cx + 65, cy - 70, cx + 60, cy - 20)
  ctx.quadraticCurveTo(cx + 50, cy - 50, cx, cy - 55)
  ctx.quadraticCurveTo(cx - 50, cy - 50, cx - 60, cy - 20)
  ctx.fill()

  // Hair highlight
  ctx.fillStyle = colors.hairHighlight
  ctx.beginPath()
  ctx.ellipse(cx + 15, cy - 65, 20, 12, -0.3, 0, Math.PI * 2)
  ctx.fill()

  // Sideburns / hair sides
  ctx.fillStyle = colors.hair
  ctx.beginPath()
  ctx.moveTo(cx - 55, cy - 30)
  ctx.quadraticCurveTo(cx - 65, cy - 10, cx - 58, cy + 10)
  ctx.lineTo(cx - 50, cy + 5)
  ctx.quadraticCurveTo(cx - 55, cy - 15, cx - 50, cy - 30)
  ctx.fill()

  ctx.beginPath()
  ctx.moveTo(cx + 55, cy - 30)
  ctx.quadraticCurveTo(cx + 65, cy - 10, cx + 58, cy + 10)
  ctx.lineTo(cx + 50, cy + 5)
  ctx.quadraticCurveTo(cx + 55, cy - 15, cx + 50, cy - 30)
  ctx.fill()

  // Eyebrows
  ctx.fillStyle = colors.hair
  ctx.lineWidth = 4
  ctx.lineCap = 'round'

  // Left eyebrow
  ctx.beginPath()
  ctx.moveTo(cx - 40, cy - 25)
  ctx.quadraticCurveTo(cx - 25, cy - 32, cx - 12, cy - 27)
  ctx.stroke()

  // Right eyebrow
  ctx.beginPath()
  ctx.moveTo(cx + 12, cy - 27)
  ctx.quadraticCurveTo(cx + 25, cy - 32, cx + 40, cy - 25)
  ctx.stroke()

  // Eyes
  const eyeY = cy - 10
  const eyeSpacing = 28

  // Eye whites
  ctx.fillStyle = colors.eyeWhite
  ctx.beginPath()
  ctx.ellipse(cx - eyeSpacing, eyeY, 18, isBlinking ? 2 : 14, 0, 0, Math.PI * 2)
  ctx.fill()
  ctx.beginPath()
  ctx.ellipse(cx + eyeSpacing, eyeY, 18, isBlinking ? 2 : 14, 0, 0, Math.PI * 2)
  ctx.fill()

  if (!isBlinking) {
    // Iris
    ctx.fillStyle = colors.iris
    ctx.beginPath()
    ctx.ellipse(cx - eyeSpacing + 2, eyeY + 2, 10, 11, 0, 0, Math.PI * 2)
    ctx.fill()
    ctx.beginPath()
    ctx.ellipse(cx + eyeSpacing + 2, eyeY + 2, 10, 11, 0, 0, Math.PI * 2)
    ctx.fill()

    // Pupils
    ctx.fillStyle = colors.pupil
    ctx.beginPath()
    ctx.arc(cx - eyeSpacing + 3, eyeY + 2, 5, 0, Math.PI * 2)
    ctx.fill()
    ctx.beginPath()
    ctx.arc(cx + eyeSpacing + 3, eyeY + 2, 5, 0, Math.PI * 2)
    ctx.fill()

    // Eye shine
    ctx.fillStyle = '#FFFFFF'
    ctx.beginPath()
    ctx.arc(cx - eyeSpacing - 1, eyeY - 2, 4, 0, Math.PI * 2)
    ctx.fill()
    ctx.beginPath()
    ctx.arc(cx + eyeSpacing - 1, eyeY - 2, 4, 0, Math.PI * 2)
    ctx.fill()
  }

  // Glasses
  ctx.strokeStyle = colors.glasses
  ctx.lineWidth = 3
  ctx.fillStyle = 'rgba(200, 220, 255, 0.1)'

  // Left lens
  ctx.beginPath()
  ctx.roundRect(cx - 50, eyeY - 18, 42, 35, 5)
  ctx.fill()
  ctx.stroke()

  // Right lens
  ctx.beginPath()
  ctx.roundRect(cx + 8, eyeY - 18, 42, 35, 5)
  ctx.fill()
  ctx.stroke()

  // Bridge
  ctx.beginPath()
  ctx.moveTo(cx - 8, eyeY)
  ctx.lineTo(cx + 8, eyeY)
  ctx.stroke()

  // Temple arms
  ctx.beginPath()
  ctx.moveTo(cx - 50, eyeY - 5)
  ctx.lineTo(cx - 65, eyeY - 8)
  ctx.stroke()
  ctx.beginPath()
  ctx.moveTo(cx + 50, eyeY - 5)
  ctx.lineTo(cx + 65, eyeY - 8)
  ctx.stroke()

  // Nose
  ctx.strokeStyle = colors.skinShadow
  ctx.lineWidth = 3
  ctx.beginPath()
  ctx.moveTo(cx, cy + 5)
  ctx.quadraticCurveTo(cx - 5, cy + 25, cx + 5, cy + 30)
  ctx.stroke()

  // Beard/stubble area
  ctx.fillStyle = colors.beard
  ctx.globalAlpha = 0.3
  ctx.beginPath()
  ctx.moveTo(cx - 45, cy + 20)
  ctx.quadraticCurveTo(cx - 55, cy + 50, cx, cy + 75)
  ctx.quadraticCurveTo(cx + 55, cy + 50, cx + 45, cy + 20)
  ctx.quadraticCurveTo(cx + 30, cy + 35, cx, cy + 40)
  ctx.quadraticCurveTo(cx - 30, cy + 35, cx - 45, cy + 20)
  ctx.fill()
  ctx.globalAlpha = 1

  // Mustache
  ctx.fillStyle = colors.beard
  ctx.beginPath()
  ctx.moveTo(cx - 25, cy + 38)
  ctx.quadraticCurveTo(cx - 15, cy + 32, cx, cy + 35)
  ctx.quadraticCurveTo(cx + 15, cy + 32, cx + 25, cy + 38)
  ctx.quadraticCurveTo(cx + 15, cy + 45, cx, cy + 42)
  ctx.quadraticCurveTo(cx - 15, cy + 45, cx - 25, cy + 38)
  ctx.fill()

  // Mouth
  const mouthY = cy + 50
  const mouthWidth = 25
  const mouthHeight = 8 + mouthOpenAmount * 20

  ctx.fillStyle = colors.mouth
  ctx.beginPath()
  if (mouthOpenAmount > 0.1) {
    // Open mouth
    ctx.ellipse(cx, mouthY + mouthHeight/2, mouthWidth, mouthHeight, 0, 0, Math.PI * 2)
    ctx.fill()

    // Teeth
    ctx.fillStyle = colors.teeth
    ctx.beginPath()
    ctx.rect(cx - 18, mouthY - 2, 36, 8)
    ctx.fill()

    // Tongue hint
    ctx.fillStyle = '#C44536'
    ctx.beginPath()
    ctx.ellipse(cx, mouthY + mouthHeight - 5, 12, 8, 0, 0, Math.PI)
    ctx.fill()
  } else {
    // Closed mouth - friendly smile
    ctx.strokeStyle = colors.mouth
    ctx.lineWidth = 4
    ctx.lineCap = 'round'
    ctx.beginPath()
    ctx.moveTo(cx - 20, mouthY)
    ctx.quadraticCurveTo(cx, mouthY + 12, cx + 20, mouthY)
    ctx.stroke()
  }
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
