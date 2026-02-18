<!--
  WhiteboardTutorLesson - Professional Interactive Learning

  REDESIGNED: Clean, professional classroom style
  - Dark gradient background (no distracting elements)
  - 3D Avatar facing the viewer
  - Classic green chalkboard
  - Video-like experience

  Sub-components:
  - WhiteboardChalkboard.vue - Classic green chalkboard with chalk tray
  - WhiteboardVideoControls.vue - Video-style playback controls
  - WhiteboardCelebration.vue - Lesson completion celebration overlay
-->

<template>
  <div class="tutor-lesson">
    <!-- Video-Style Player Container -->
    <div class="video-container">
      <!-- Scene Background - Clean dark gradient -->
      <div class="scene-background"></div>

      <!-- Main Content Area -->
      <div class="content-area">
        <!-- 3D Character (Left Side) -->
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
            <div class="badge-icon">&#128104;&#8205;&#127979;</div>
            <span class="badge-name">{{ avatarName }}</span>
          </div>
        </div>

        <!-- Classic Green Chalkboard -->
        <WhiteboardChalkboard
          ref="chalkboardRef"
          :title="currentTitle"
        />
      </div>

      <!-- Speech Text (Video subtitle style) -->
      <div class="speech-overlay" v-if="currentSpeechText">
        <p class="speech-text">{{ currentSpeechText }}</p>
        <div v-if="timeline.isSpeaking.value" class="speaking-indicator">
          <span></span><span></span><span></span>
        </div>
      </div>

      <!-- Video Controls Bar -->
      <WhiteboardVideoControls
        :is-paused="timeline.isPaused.value"
        :has-previous="timeline.hasPrevious.value"
        :has-next="timeline.hasNext.value"
        :current-step="timeline.currentStepIndex.value + 1"
        :total-steps="lessonContent.length"
        :show-calculator-button="!!currentChallenge"
        :calculator-active="showCalculator"
        @toggle-play="togglePlayPause"
        @previous="onPrevious"
        @next="onNext"
        @toggle-calculator="showCalculator = !showCalculator"
        @exit="handleExit"
      />
    </div>

    <!-- Calculator Slide-In (Right Side) -->
    <Transition name="calc-slide">
      <div v-if="showCalculator && currentChallenge" class="calculator-panel">
        <div class="calc-header">
          <span>{{ $t('lesson.whiteboard.calculator') }}</span>
          <button @click="showCalculator = false" class="calc-close">&times;</button>
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
    <WhiteboardCelebration
      :visible="showCelebration"
      @complete="onComplete"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { OnScreenCalculator, RealisticTeacher3D } from '@/presentation/components/public/system-features/tutor/user'
import {
  useTeachingTimeline,
  type TeachingStep,
  type WhiteboardAction,
  type TeacherAnimation,
  type CalculatorChallenge
} from '@/application/composables/system/useTeachingTimeline'
import WhiteboardChalkboard from './WhiteboardChalkboard.vue'
import WhiteboardVideoControls from './WhiteboardVideoControls.vue'
import WhiteboardCelebration from './WhiteboardCelebration.vue'

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
const chalkboardRef = ref<InstanceType<typeof WhiteboardChalkboard> | null>(null)
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
const avatarName = ref(t('lesson.whiteboard.teacherName'))

// Timeline Callbacks
async function onWhiteboardAction(action: WhiteboardAction): Promise<void> {
  if (chalkboardRef.value) {
    if (action.type === 'write' || action.type === 'highlight') {
      isPointing.value = true
    }
    await chalkboardRef.value.executeAction(action)
    setTimeout(() => {
      isPointing.value = false
    }, 500)
  }
}

function onAnimationChange(animation: TeacherAnimation): void {
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

function onCalculatorChallenge(challenge: CalculatorChallenge): void {
  currentChallenge.value = challenge
  showCalculator.value = true
}

function onStepComplete(_step: TeachingStep, index: number): void {
  emit('step-complete', index)
}

function onTimelineComplete(): void {
  showCelebration.value = true
}

function onSpeechStart(): void {
  if (timeline.currentStep.value) {
    currentSpeechText.value = timeline.currentStep.value.speech
  }
}

function onSpeechEnd(): void {
  // Keep text visible
}

// Calculator Handlers
function onCalculatorCorrect(result: number): void {
  showCalculator.value = false
  currentChallenge.value = null
  timeline.submitCalculatorResult(result, true)
}

function onCalculatorWrong(_result: number): void {
  // Keep calculator open for retry
}

// Control Handlers
function togglePlayPause(): void {
  if (timeline.isPaused.value) {
    timeline.resume()
  } else {
    timeline.pause()
  }
}

function onPrevious(): void {
  showCalculator.value = false
  currentChallenge.value = null
  timeline.previous()
}

function onNext(): void {
  if (timeline.isComplete.value) {
    showCelebration.value = true
  } else {
    showCalculator.value = false
    currentChallenge.value = null
    timeline.skipCurrentStep()
  }
}

function onComplete(): void {
  showCelebration.value = false
  emit('complete')
}

function handleExit(): void {
  timeline.stop()
  emit('exit')
}

// Lifecycle
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
/* Base - Video Container Style */
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

/* Scene Background - Professional Dark Style */
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

/* Content Area */
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

/* 3D Character */
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
  background: transparent;
  overflow: visible;
}

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

/* Speech Overlay */
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

/* Calculator Panel */
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

</style>
