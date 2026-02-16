<!--
  WhiteboardTutorLesson - Professional Interactive Learning

  REDESIGNED: Clean, professional classroom style
  - Dark gradient background (no distracting elements)
  - 3D Avatar facing the viewer
  - Classic green chalkboard
  - Video-like experience
-->

<template>
  <div class="tutor-lesson">
    <!-- Video-Style Player Container -->
    <div class="video-container">
      <!-- Scene Background - Clean dark gradient -->
      <div class="scene-background"></div>

      <!-- Main Content Area -->
      <div class="content-area">
        <!-- 3D Character (Left Side) - Ready Player Me / Realistic Human -->
        <div class="character-container">
          <div class="character-wrapper">
            <RealisticTeacher3D
              ref="teacherRef"
              :is-speaking="timeline.isSpeaking.value"
              :point-at="isPointing ? { x: 0.5, y: 0.5 } : null"
              :animation="currentAnimation"
              :use-realistic-human="true"
              :width="380"
              :height="520"
            />
          </div>

          <!-- Character Name Badge -->
          <div class="character-badge">
            <div class="badge-icon">👨‍🏫</div>
            <span class="badge-name">{{ avatarName }}</span>
          </div>
        </div>

        <!-- Classic Green Chalkboard -->
        <div class="chalkboard-container">
          <!-- Wooden frame -->
          <div class="chalkboard-frame">
            <!-- Green board surface -->
            <div class="chalkboard-surface">
              <!-- Title in chalk style -->
              <h2 class="chalk-title">{{ currentTitle || $t('lesson.whiteboard.defaultTitle') }}</h2>
              <!-- Content area -->
              <InteractiveWhiteboard
                ref="whiteboardRef"
                :width="580"
                :height="340"
                :title="''"
                :show-controls="false"
                :background-color="'transparent'"
                :text-color="'#f5f5dc'"
                class="chalk-content"
              />
            </div>
            <!-- Chalk tray -->
            <div class="chalk-tray">
              <div class="chalk white"></div>
              <div class="chalk yellow"></div>
              <div class="chalk red"></div>
              <div class="eraser"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Speech Text (Video subtitle style) -->
      <div class="speech-overlay" v-if="currentSpeechText">
        <p class="speech-text">{{ currentSpeechText }}</p>
        <div v-if="timeline.isSpeaking.value" class="speaking-indicator">
          <span></span><span></span><span></span>
        </div>
      </div>

      <!-- Video Controls Bar -->
      <div class="video-controls">
        <div class="controls-left">
          <button @click="togglePlayPause" class="control-btn play-btn">
            <span v-if="timeline.isPaused.value">▶</span>
            <span v-else>⏸</span>
          </button>
          <button @click="onPrevious" class="control-btn" :disabled="!timeline.hasPrevious.value">
            ⏮
          </button>
          <button @click="onNext" class="control-btn" :disabled="!timeline.hasNext.value">
            ⏭
          </button>
        </div>

        <div class="controls-center">
          <!-- Progress Bar -->
          <div class="progress-bar">
            <div
              class="progress-fill"
              :style="{ width: `${((timeline.currentStepIndex.value + 1) / lessonContent.length) * 100}%` }"
            ></div>
          </div>
          <span class="progress-time">{{ timeline.currentStepIndex.value + 1 }} / {{ lessonContent.length }}</span>
        </div>

        <div class="controls-right">
          <button
            v-if="currentChallenge"
            @click="showCalculator = !showCalculator"
            class="control-btn calc-btn"
            :class="{ active: showCalculator }"
          >
            🧮
          </button>
          <button @click="handleExit" class="control-btn close-btn">✕</button>
        </div>
      </div>
    </div>

    <!-- Calculator Slide-In (Right Side) -->
    <Transition name="calc-slide">
      <div v-if="showCalculator && currentChallenge" class="calculator-panel">
        <div class="calc-header">
          <span>{{ $t('lesson.whiteboard.calculator') }}</span>
          <button @click="showCalculator = false" class="calc-close">×</button>
        </div>
        <OnScreenCalculator
          ref="calculatorRef"
          :challenge="currentChallenge"
          :show-history="false"
          @correct="onCalculatorCorrect"
          @wrong="onCalculatorWrong"
        />
      </div>
    </Transition>

    <!-- Celebration Overlay -->
    <Transition name="fade">
      <div v-if="showCelebration" class="celebration">
        <div class="celebration-content">
          <div class="confetti">🎉</div>
          <h2>{{ $t('lesson.whiteboard.celebration.title') }}</h2>
          <p>{{ $t('lesson.whiteboard.celebration.message') }}</p>
          <button @click="onComplete" class="btn-complete">{{ $t('common.continue') }}</button>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { InteractiveWhiteboard, OnScreenCalculator, RealisticTeacher3D } from '@/presentation/components/public/system-features/tutor/user'
import {
  useTeachingTimeline,
  type TeachingStep,
  type WhiteboardAction,
  type TeacherAnimation,
  type CalculatorChallenge
} from '@/application/composables/system/useTeachingTimeline'

const { t } = useI18n()

// Props & Emits
const props = defineProps<{
  lessonContent: TeachingStep[]
}>()

const emit = defineEmits<{
  (e: 'complete'): void
  (e: 'exit'): void
  (e: 'step-complete', stepIndex: number): void
}>()

// Refs
const whiteboardRef = ref<InstanceType<typeof InteractiveWhiteboard> | null>(null)
const calculatorRef = ref<InstanceType<typeof OnScreenCalculator> | null>(null)
const teacherRef = ref<InstanceType<typeof RealisticTeacher3D> | null>(null)

// Timeline
const timeline = useTeachingTimeline()

// State
const currentSpeechText = ref('')
const currentTitle = ref(t('lesson.whiteboard.defaultTitle'))
const currentChallenge = ref<CalculatorChallenge | null>(null)
const showCalculator = ref(false)
const showCelebration = ref(false)
const isPointing = ref(false)
const currentAnimation = ref<'idle' | 'talking' | 'pointing' | 'thinking' | 'celebrating'>('idle')

// ============================================================================
// 3D Avatar System - Image-based with pose switching
// ============================================================================
const avatarName = ref(t('lesson.whiteboard.teacherName'))

// ============================================================================
// Timeline Callbacks
// ============================================================================
async function onWhiteboardAction(action: WhiteboardAction): Promise<void> {
  if (whiteboardRef.value) {
    if (action.type === 'write' || action.type === 'highlight') {
      isPointing.value = true
    }
    await whiteboardRef.value.executeAction(action)
    setTimeout(() => {
      isPointing.value = false
    }, 500)
  }
}

function onAnimationChange(animation: TeacherAnimation) {
  if (animation.type === 'pointing') {
    isPointing.value = true
    currentAnimation.value = 'pointing'
  } else if (animation.type === 'talking') {
    isPointing.value = false
    currentAnimation.value = 'talking'
  } else if (animation.type === 'thinking') {
    isPointing.value = false
    currentAnimation.value = 'thinking'
  } else if (animation.type === 'celebrating') {
    isPointing.value = false
    currentAnimation.value = 'celebrating'
  } else {
    isPointing.value = false
    currentAnimation.value = 'idle'
  }
}

function onCalculatorChallenge(challenge: CalculatorChallenge) {
  currentChallenge.value = challenge
  showCalculator.value = true
}

function onStepComplete(step: TeachingStep, index: number) {
  emit('step-complete', index)
}

function onTimelineComplete() {
  showCelebration.value = true
}

function onSpeechStart() {
  if (timeline.currentStep.value) {
    currentSpeechText.value = timeline.currentStep.value.speech
  }
}

function onSpeechEnd() {
  // Keep text visible
}

// ============================================================================
// Calculator Handlers
// ============================================================================
function onCalculatorCorrect(result: number) {
  showCalculator.value = false
  currentChallenge.value = null
  timeline.submitCalculatorResult(result, true)
}

function onCalculatorWrong(_result: number) {
  // Keep calculator open for retry
}

// ============================================================================
// Control Handlers
// ============================================================================
function togglePlayPause() {
  if (timeline.isPaused.value) {
    timeline.resume()
  } else {
    timeline.pause()
  }
}

function onPrevious() {
  showCalculator.value = false
  currentChallenge.value = null
  timeline.previous()
}

function onNext() {
  if (timeline.isComplete.value) {
    showCelebration.value = true
  } else {
    showCalculator.value = false
    currentChallenge.value = null
    timeline.skipCurrentStep()
  }
}

function onComplete() {
  showCelebration.value = false
  emit('complete')
}

function handleExit() {
  timeline.stop()
  emit('exit')
}

// ============================================================================
// Lifecycle
// ============================================================================
onMounted(async () => {
  await nextTick()
  await new Promise(resolve => setTimeout(resolve, 300))

  timeline.start(props.lessonContent, {
    onWhiteboardAction,
    onAnimationChange,
    onCalculatorChallenge,
    onStepComplete,
    onTimelineComplete,
    onSpeechStart,
    onSpeechEnd
  })
})

onUnmounted(() => {
  timeline.stop()
})

watch(() => timeline.currentStep.value, (step) => {
  if (step) {
    currentSpeechText.value = step.speech
  }
})
</script>

<style scoped>
/* ============================================================================
   BASE - Video Container Style
   ============================================================================ */
.tutor-lesson {
  display: flex;
  height: 100%;
  min-height: 650px;
  background: #0f172a;
  border-radius: 0.75rem;
  overflow: hidden;
  position: relative;
}

.video-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

/* ============================================================================
   SCENE BACKGROUND - Professional Dark Style
   ============================================================================ */
.scene-background {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg,
    #1a1a2e 0%,
    #16213e 50%,
    #0f0f23 100%
  );
  z-index: 0;
}

/* Subtle grid pattern for depth */
.scene-background::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px);
  background-size: 50px 50px;
  opacity: 0.5;
}

/* ============================================================================
   CONTENT AREA
   ============================================================================ */
.content-area {
  flex: 1;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  gap: 3rem;
  padding: 2rem 3rem 5rem;
  position: relative;
  z-index: 1;
}

/* ============================================================================
   3D CHARACTER (Three.js VRM)
   ============================================================================ */
.character-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex-shrink: 0;
  position: relative;
}

.character-wrapper {
  width: 380px;
  height: 520px;
  position: relative;
  /* No background, no border - avatar floats seamlessly */
  background: transparent;
  overflow: visible;
}

/* Character name badge */
.character-badge {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: rgba(255, 255, 255, 0.95);
  padding: 0.5rem 1.25rem;
  border-radius: 2rem;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
  margin-top: 0.5rem;
  position: relative;
  z-index: 5;
}

.badge-icon {
  font-size: 1.25rem;
}

.badge-name {
  color: #1e293b;
  font-weight: 600;
  font-size: 0.95rem;
}

/* ============================================================================
   CLASSIC GREEN CHALKBOARD
   ============================================================================ */
.chalkboard-container {
  flex: 1;
  max-width: 750px;
  min-width: 550px;
}

.chalkboard-frame {
  background: linear-gradient(180deg, #8B4513 0%, #654321 50%, #4a3520 100%);
  padding: 20px;
  border-radius: 8px;
  box-shadow:
    0 8px 32px rgba(0, 0, 0, 0.4),
    inset 0 2px 4px rgba(255, 255, 255, 0.1),
    inset 0 -2px 4px rgba(0, 0, 0, 0.2);
  position: relative;
}

/* Wood grain texture */
.chalkboard-frame::before {
  content: '';
  position: absolute;
  inset: 0;
  background: repeating-linear-gradient(
    90deg,
    transparent,
    transparent 2px,
    rgba(0, 0, 0, 0.05) 2px,
    rgba(0, 0, 0, 0.05) 4px
  );
  border-radius: 8px;
  pointer-events: none;
}

.chalkboard-surface {
  background: linear-gradient(170deg, #2d5a3d 0%, #1e4a2e 50%, #1a3d26 100%);
  border-radius: 4px;
  padding: 1.5rem;
  min-height: 380px;
  position: relative;
  box-shadow:
    inset 0 2px 8px rgba(0, 0, 0, 0.3),
    inset 0 0 20px rgba(0, 0, 0, 0.1);
}

/* Chalk dust texture */
.chalkboard-surface::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image:
    radial-gradient(circle at 20% 30%, rgba(255,255,255,0.03) 1px, transparent 1px),
    radial-gradient(circle at 60% 70%, rgba(255,255,255,0.02) 1px, transparent 1px),
    radial-gradient(circle at 80% 20%, rgba(255,255,255,0.03) 1px, transparent 1px);
  background-size: 50px 50px;
  pointer-events: none;
}

.chalk-title {
  font-family: 'Segoe UI', sans-serif;
  font-size: 1.75rem;
  font-weight: 600;
  color: #f5f5dc;
  text-shadow:
    1px 1px 2px rgba(0, 0, 0, 0.3),
    0 0 10px rgba(245, 245, 220, 0.1);
  margin: 0 0 1rem 0;
  text-align: center;
  letter-spacing: 1px;
}

.chalk-content {
  background: transparent !important;
  color: #f5f5dc !important;
}

/* Make InteractiveWhiteboard use chalk colors */
.chalk-content :deep(canvas) {
  background: transparent !important;
}

.chalk-content :deep(.whiteboard-text) {
  color: #f5f5dc !important;
  text-shadow: 1px 1px 1px rgba(0, 0, 0, 0.3);
}

/* Chalk tray at bottom */
.chalk-tray {
  background: linear-gradient(180deg, #654321 0%, #4a3520 100%);
  height: 25px;
  margin-top: 8px;
  border-radius: 0 0 4px 4px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  gap: 12px;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.2);
}

.chalk {
  width: 40px;
  height: 10px;
  border-radius: 2px;
  box-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
}

.chalk.white {
  background: linear-gradient(180deg, #f5f5f5 0%, #e0e0e0 100%);
}

.chalk.yellow {
  background: linear-gradient(180deg, #ffd54f 0%, #ffca28 100%);
}

.chalk.red {
  background: linear-gradient(180deg, #ef5350 0%, #e53935 100%);
}

.eraser {
  width: 50px;
  height: 16px;
  background: linear-gradient(180deg, #8d6e63 0%, #6d4c41 100%);
  border-radius: 2px;
  margin-left: auto;
  box-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
}

/* ============================================================================
   SPEECH OVERLAY
   ============================================================================ */
.speech-overlay {
  position: absolute;
  bottom: 70px;
  left: 50%;
  transform: translateX(-50%);
  max-width: 80%;
  background: rgba(0, 0, 0, 0.8);
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  z-index: 10;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.speech-text {
  color: white;
  font-size: 1rem;
  line-height: 1.5;
  margin: 0;
  text-align: center;
}

.speaking-indicator {
  display: flex;
  gap: 3px;
}

.speaking-indicator span {
  width: 6px;
  height: 6px;
  background: #60a5fa;
  border-radius: 50%;
  animation: pulse-dot 0.6s ease-in-out infinite;
}

.speaking-indicator span:nth-child(2) { animation-delay: 0.1s; }
.speaking-indicator span:nth-child(3) { animation-delay: 0.2s; }

@keyframes pulse-dot {
  0%, 100% { transform: scale(1); opacity: 0.5; }
  50% { transform: scale(1.3); opacity: 1; }
}

/* ============================================================================
   VIDEO CONTROLS
   ============================================================================ */
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

/* ============================================================================
   CALCULATOR PANEL
   ============================================================================ */
.calculator-panel {
  position: absolute;
  right: 0;
  top: 0;
  bottom: 0;
  width: 290px;
  background: rgba(15, 23, 42, 0.98);
  border-left: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  flex-direction: column;
  z-index: 100;
}

.calc-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  background: rgba(0, 0, 0, 0.3);
  color: #e2e8f0;
  font-size: 0.875rem;
  font-weight: 500;
}

.calc-close {
  width: 24px;
  height: 24px;
  background: transparent;
  border: none;
  color: #64748b;
  font-size: 1.25rem;
  cursor: pointer;
  border-radius: 50%;
  transition: all 0.2s;
}

.calc-close:hover {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.calculator-panel :deep(.calc-wrapper) {
  margin: 0.5rem;
}

.calc-slide-enter-active,
.calc-slide-leave-active {
  transition: transform 0.25s ease;
}

.calc-slide-enter-from,
.calc-slide-leave-to {
  transform: translateX(100%);
}

/* ============================================================================
   CELEBRATION
   ============================================================================ */
.celebration {
  position: absolute;
  inset: 0;
  background: rgba(15, 23, 42, 0.95);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
}

.celebration-content {
  text-align: center;
  padding: 2rem;
}

.confetti {
  font-size: 4rem;
  animation: pop 0.5s ease-out;
}

@keyframes pop {
  0% { transform: scale(0); }
  50% { transform: scale(1.2); }
  100% { transform: scale(1); }
}

.celebration h2 {
  color: #f1f5f9;
  font-size: 1.75rem;
  margin: 1rem 0 0.5rem;
}

.celebration p {
  color: #94a3b8;
  margin-bottom: 1.5rem;
}

.btn-complete {
  padding: 0.875rem 2.5rem;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s;
}

.btn-complete:hover {
  transform: translateY(-2px);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
