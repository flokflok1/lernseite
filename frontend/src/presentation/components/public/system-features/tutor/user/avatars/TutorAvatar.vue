<!--
  TutorAvatar - Universeller KI-Tutor mit Sprachausgabe

  Features:
  - Animierter Avatar der "spricht"
  - Edge TTS (kostenlos, Premium-Qualitaet) mit Caching
  - Fallback zu OpenAI TTS und Browser TTS
  - Verschiedene Stimmungen/Emotionen
  - Positionierbar (floating, inline, corner)
  - Guided Mode Support
  - Click-to-skip Audio

  Usage:
  <TutorAvatar
    :visible="true"
    :text="'Hallo! Ich erklaere dir jetzt...'"
    :auto-play="true"
    position="floating"
    mood="friendly"
    voice="thorsten"
    @speech-end="onSpeechEnd"
    @click="onAvatarClick"
  />

  Available Piper TTS Voice (kostenlos, offline, hochwertig):
  - thorsten: Natuerliche deutsche maennliche Stimme (Standard)

  OpenAI Voices (kostenpflichtig, Fallback):
  - nova, alloy, echo, fable, onyx, shimmer
-->

<template>
  <Transition name="avatar-fade">
    <div
      v-if="visible"
      class="tutor-avatar"
      :class="[
        `position-${position}`,
        `mood-${currentMood}`,
        { 'is-speaking': audio.isSpeaking.value, 'is-thinking': audio.isThinking.value }
      ]"
      @click="handleClick"
    >
      <!-- Avatar Container -->
      <div class="avatar-container">
        <div class="avatar-visual">
          <div class="avatar-glow" :class="{ active: audio.isSpeaking.value }"></div>

          <div class="avatar-image-wrapper" :class="{ speaking: audio.isSpeaking.value }">
            <img
              :src="tutorAvatarSvg"
              alt="Tutor Lumi"
              class="avatar-image"
            />
            <div v-if="audio.isSpeaking.value" class="speaking-indicator">
              <span class="sound-wave"></span>
              <span class="sound-wave"></span>
              <span class="sound-wave"></span>
            </div>
          </div>
        </div>

        <div class="avatar-status" v-if="showStatus">
          <span v-if="audio.isThinking.value" class="status-dot thinking"></span>
          <span v-else-if="audio.isSpeaking.value" class="status-dot speaking"></span>
          <span v-else class="status-dot idle"></span>
        </div>
      </div>

      <!-- Speech Bubble -->
      <TutorSpeechBubble
        :visible="showBubble"
        :display-text="audio.displayText.value"
        :is-speaking="audio.isSpeaking.value"
        :audio-ready="audio.audioReady.value"
        :audio-progress="audio.audioProgress.value"
        :audio-duration="audio.audioDuration.value"
        :show-controls="showControls"
        @pause="audio.pauseAudio"
        @play="audio.playAudio"
        @skip="audio.skipToEnd"
      />

      <!-- Name tag -->
      <div v-if="showName" class="avatar-name">
        {{ tutorName }}
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, computed, watch, toRef } from 'vue'
import tutorAvatarSvg from '@/shared/assets/tutor-avatar.svg'
import { useTutorAudio, DEFAULT_TUTOR_VOICE } from './composables/useTutorAudio'
import TutorSpeechBubble from './TutorSpeechBubble.vue'

// ============================================================================
// Props
// ============================================================================
interface Props {
  visible?: boolean
  text?: string
  autoPlay?: boolean
  position?: 'floating' | 'inline' | 'corner-br' | 'corner-bl' | 'corner-tr' | 'corner-tl'
  mood?: 'friendly' | 'excited' | 'thinking' | 'encouraging' | 'neutral'
  voice?: string
  speed?: number
  showBubble?: boolean
  showControls?: boolean
  showStatus?: boolean
  showName?: boolean
  tutorName?: string
  typewriter?: boolean
  typewriterSpeed?: number
}

const props = withDefaults(defineProps<Props>(), {
  visible: true,
  text: '',
  autoPlay: true,
  position: 'floating',
  mood: 'friendly',
  voice: DEFAULT_TUTOR_VOICE,
  speed: 1.0,
  showBubble: true,
  showControls: true,
  showStatus: true,
  showName: false,
  tutorName: 'Lumi',
  typewriter: true,
  typewriterSpeed: 30
})

// ============================================================================
// Emits
// ============================================================================
const emit = defineEmits<{
  (e: 'speech-start'): void
  (e: 'speech-end'): void
  (e: 'speech-error', error: Error): void
  (e: 'click'): void
  (e: 'skip'): void
}>()

// ============================================================================
// State
// ============================================================================
const currentMood = ref(props.mood)

// ============================================================================
// Composable
// ============================================================================
const audio = useTutorAudio(
  {
    text: toRef(props, 'text'),
    autoPlay: toRef(props, 'autoPlay'),
    voice: toRef(props, 'voice'),
    speed: toRef(props, 'speed'),
    typewriter: toRef(props, 'typewriter'),
    typewriterSpeed: toRef(props, 'typewriterSpeed')
  },
  {
    onSpeechStart: () => emit('speech-start'),
    onSpeechEnd: () => emit('speech-end'),
    onSpeechError: (error: Error) => emit('speech-error', error),
    onSkip: () => emit('skip')
  }
)

// ============================================================================
// Methods
// ============================================================================
function handleClick(): void {
  emit('click')
}

// ============================================================================
// Watchers
// ============================================================================
watch(() => props.mood, (newMood) => {
  currentMood.value = newMood
})

// ============================================================================
// Expose for parent components
// ============================================================================
defineExpose({
  speak: audio.generateAndPlayAudio,
  pause: audio.pauseAudio,
  skip: audio.skipToEnd,
  isSpeaking: audio.isSpeaking,
  isThinking: audio.isThinking
})
</script>

<style scoped>
/* ============================================================================
   Base Container
   ============================================================================ */
.tutor-avatar {
  --avatar-size: 80px;
  --bubble-max-width: 320px;
  --primary-color: #6366f1;
  --glow-color: rgba(99, 102, 241, 0.4);

  display: flex;
  align-items: flex-start;
  gap: 1rem;
  z-index: 1000;
}

/* Position variants */
.position-floating {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  flex-direction: row-reverse;
}

.position-inline {
  position: relative;
  flex-direction: row;
}

.position-corner-br {
  position: fixed;
  bottom: 1rem;
  right: 1rem;
  flex-direction: column;
  align-items: flex-end;
}

.position-corner-bl {
  position: fixed;
  bottom: 1rem;
  left: 1rem;
  flex-direction: column;
  align-items: flex-start;
}

.position-corner-tr {
  position: fixed;
  top: 1rem;
  right: 1rem;
  flex-direction: column;
  align-items: flex-end;
}

.position-corner-tl {
  position: fixed;
  top: 1rem;
  left: 1rem;
  flex-direction: column;
  align-items: flex-start;
}

/* ============================================================================
   Avatar Container
   ============================================================================ */
.avatar-container {
  position: relative;
  width: var(--avatar-size);
  height: var(--avatar-size);
  flex-shrink: 0;
}

.avatar-visual {
  width: 100%;
  height: 100%;
  position: relative;
}

.avatar-glow {
  position: absolute;
  inset: -8px;
  background: radial-gradient(circle, var(--glow-color) 0%, transparent 70%);
  border-radius: 50%;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.avatar-glow.active {
  opacity: 1;
  animation: pulse-glow 1.5s ease-in-out infinite;
}

@keyframes pulse-glow {
  0%, 100% { transform: scale(1); opacity: 0.6; }
  50% { transform: scale(1.1); opacity: 1; }
}

.avatar-image-wrapper {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  overflow: hidden;
  position: relative;
  box-shadow: 0 4px 20px rgba(30, 41, 59, 0.4);
  transition: transform 0.2s ease;
}

.avatar-image-wrapper:hover {
  transform: scale(1.02);
}

.avatar-image-wrapper.speaking {
  animation: subtle-bounce 0.6s ease-in-out infinite;
}

@keyframes subtle-bounce {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.02); }
}

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* Speaking Indicator */
.speaking-indicator {
  position: absolute;
  bottom: 8px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 3px;
  align-items: flex-end;
  padding: 4px 8px;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 12px;
}

.sound-wave {
  width: 3px;
  height: 8px;
  background: #10b981;
  border-radius: 2px;
  animation: sound-wave 0.4s ease-in-out infinite;
}

.sound-wave:nth-child(1) { animation-delay: 0s; }
.sound-wave:nth-child(2) { animation-delay: 0.1s; height: 12px; }
.sound-wave:nth-child(3) { animation-delay: 0.2s; }

@keyframes sound-wave {
  0%, 100% { transform: scaleY(0.5); }
  50% { transform: scaleY(1); }
}

/* Status indicator */
.avatar-status {
  position: absolute;
  bottom: 0;
  right: 0;
}

.status-dot {
  display: block;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid white;
}

.status-dot.idle { background: #9ca3af; }
.status-dot.speaking {
  background: #10b981;
  animation: pulse-status 1s ease-in-out infinite;
}
.status-dot.thinking {
  background: #f59e0b;
  animation: pulse-status 0.5s ease-in-out infinite;
}

@keyframes pulse-status {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.2); }
}

/* ============================================================================
   Avatar Name
   ============================================================================ */
.avatar-name {
  position: absolute;
  bottom: -1.5rem;
  left: 50%;
  transform: translateX(-50%);
  font-size: 0.75rem;
  font-weight: 600;
  color: #6b7280;
  white-space: nowrap;
}

/* ============================================================================
   Mood Variants
   ============================================================================ */
.mood-friendly .avatar-glow { --glow-color: rgba(99, 102, 241, 0.4); }
.mood-excited .avatar-glow { --glow-color: rgba(245, 87, 108, 0.4); }
.mood-thinking .avatar-glow { --glow-color: rgba(79, 172, 254, 0.4); }
.mood-encouraging .avatar-glow { --glow-color: rgba(67, 233, 123, 0.4); }
.mood-neutral .avatar-glow { --glow-color: rgba(156, 163, 175, 0.4); }

/* ============================================================================
   Transitions
   ============================================================================ */
.avatar-fade-enter-active,
.avatar-fade-leave-active {
  transition: all 0.3s ease;
}

.avatar-fade-enter-from,
.avatar-fade-leave-to {
  opacity: 0;
  transform: scale(0.8) translateY(20px);
}

/* ============================================================================
   Responsive
   ============================================================================ */
@media (max-width: 640px) {
  .tutor-avatar {
    --avatar-size: 60px;
    --bubble-max-width: 250px;
  }

  .position-floating {
    bottom: 1rem;
    right: 1rem;
  }
}
</style>
