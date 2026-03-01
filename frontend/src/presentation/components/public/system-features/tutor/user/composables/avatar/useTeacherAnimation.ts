/**
 * useTeacherAnimation - Animation state management for 2D teacher
 *
 * Manages blink timing, mouth lip-sync interpolation, and arm
 * position interpolation for the canvas-based animated teacher.
 */

import { ref, type Ref } from 'vue'

interface TeacherAnimationProps {
  isSpeaking: Ref<boolean>
  isPointing: Ref<boolean>
}

interface UseTeacherAnimationReturn {
  time: Ref<number>
  isBlinking: Ref<boolean>
  mouthOpenAmount: Ref<number>
  armAngle: Ref<number>
  updateAnimations: () => void
}

export function useTeacherAnimation(props: TeacherAnimationProps): UseTeacherAnimationReturn {
  const time = ref(0)
  const isBlinking = ref(false)
  const mouthOpenAmount = ref(0)
  const armAngle = ref(0)

  let blinkTimer = 0
  let nextBlinkTime = 3
  let targetMouthOpen = 0
  let targetArmAngle = 0

  function updateBlink(): void {
    blinkTimer += 0.016

    if (!isBlinking.value && blinkTimer > nextBlinkTime) {
      isBlinking.value = true
      setTimeout(() => {
        isBlinking.value = false
        blinkTimer = 0
        nextBlinkTime = 2 + Math.random() * 3
      }, 150)
    }
  }

  function updateMouth(): void {
    if (props.isSpeaking.value) {
      const t = time.value
      const speechWave = Math.sin(t * 12) * 0.3 +
                         Math.sin(t * 7.3) * 0.2 +
                         Math.sin(t * 18.7) * 0.15
      targetMouthOpen = 0.3 + Math.max(0, speechWave) * 0.5
    } else {
      targetMouthOpen = 0
    }

    mouthOpenAmount.value += (targetMouthOpen - mouthOpenAmount.value) * 0.3
  }

  function updateArm(): void {
    if (props.isPointing.value) {
      targetArmAngle = -0.8
    } else {
      targetArmAngle = 0.3
    }

    armAngle.value += (targetArmAngle - armAngle.value) * 0.1
  }

  function updateAnimations(): void {
    time.value += 0.016

    updateBlink()
    updateMouth()
    updateArm()
  }

  return {
    time,
    isBlinking,
    mouthOpenAmount,
    armAngle,
    updateAnimations
  }
}
