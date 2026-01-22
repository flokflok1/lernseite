<!--
  TutorAvatar - Universeller KI-Tutor mit Sprachausgabe

  Features:
  - Animierter Avatar der "spricht"
  - Edge TTS (kostenlos, Premium-Qualität) mit Caching
  - Fallback zu OpenAI TTS und Browser TTS
  - Verschiedene Stimmungen/Emotionen
  - Positionierbar (floating, inline, corner)
  - Guided Mode Support
  - Click-to-skip Audio

  Usage:
  <TutorAvatar
    :visible="true"
    :text="'Hallo! Ich erkläre dir jetzt...'"
    :auto-play="true"
    position="floating"
    mood="friendly"
    voice="thorsten"
    @speech-end="onSpeechEnd"
    @click="onAvatarClick"
  />

  Available Piper TTS Voice (kostenlos, offline, hochwertig):
  - thorsten: Natürliche deutsche männliche Stimme (Standard)

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
        { 'is-speaking': isSpeaking, 'is-thinking': isThinking }
      ]"
      @click="handleClick"
    >
      <!-- Avatar Container -->
      <div class="avatar-container">
        <!-- Avatar Image/Animation -->
        <div class="avatar-visual">
          <!-- Animated glow ring behind avatar when speaking -->
          <div class="avatar-glow" :class="{ active: isSpeaking }"></div>

          <!-- Main Avatar - Realistic SVG -->
          <div class="avatar-image-wrapper" :class="{ speaking: isSpeaking }">
            <img
              :src="tutorAvatarSvg"
              alt="Tutor Lumi"
              class="avatar-image"
            />
            <!-- Speaking indicator overlay -->
            <div v-if="isSpeaking" class="speaking-indicator">
              <span class="sound-wave"></span>
              <span class="sound-wave"></span>
              <span class="sound-wave"></span>
            </div>
          </div>
        </div>

        <!-- Status indicator -->
        <div class="avatar-status" v-if="showStatus">
          <span v-if="isThinking" class="status-dot thinking"></span>
          <span v-else-if="isSpeaking" class="status-dot speaking"></span>
          <span v-else class="status-dot idle"></span>
        </div>
      </div>

      <!-- Speech Bubble -->
      <Transition name="bubble-pop">
        <div v-if="showBubble && displayText" class="speech-bubble">
          <div class="bubble-content">
            <p class="bubble-text">{{ displayText }}</p>

            <!-- Progress bar for audio -->
            <div v-if="isSpeaking && audioDuration > 0" class="audio-progress">
              <div
                class="audio-progress-fill"
                :style="{ width: `${audioProgress}%` }"
              ></div>
            </div>
          </div>

          <!-- Bubble actions -->
          <div class="bubble-actions" v-if="showControls">
            <button
              v-if="isSpeaking"
              @click.stop="pauseAudio"
              class="bubble-btn"
              title="Pause"
            >
              ⏸️
            </button>
            <button
              v-else-if="audioReady && !isSpeaking"
              @click.stop="playAudio"
              class="bubble-btn"
              title="Abspielen"
            >
              ▶️
            </button>
            <button
              @click.stop="skipToEnd"
              class="bubble-btn skip"
              title="Überspringen"
            >
              ⏭️
            </button>
          </div>

          <!-- Bubble pointer -->
          <div class="bubble-pointer"></div>
        </div>
      </Transition>

      <!-- Name tag -->
      <div v-if="showName" class="avatar-name">
        {{ tutorName }}
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, computed, watch, onUnmounted } from 'vue'
import { ttsApi, DEFAULT_TUTOR_VOICE } from '@/infrastructure/api/tts.api'
import tutorAvatarSvg from '@/shared/assets/tutor-avatar.svg'

// ============================================================================
// Props
// ============================================================================
interface Props {
  visible?: boolean
  text?: string
  autoPlay?: boolean
  position?: 'floating' | 'inline' | 'corner-br' | 'corner-bl' | 'corner-tr' | 'corner-tl'
  mood?: 'friendly' | 'excited' | 'thinking' | 'encouraging' | 'neutral'
  voice?: string  // Piper TTS (thorsten) or OpenAI fallback (nova, alloy, etc.)
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
  voice: DEFAULT_TUTOR_VOICE,  // thorsten (Piper TTS - kostenlos, offline, hochwertig!)
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
const isSpeaking = ref(false)
const isThinking = ref(false)
const audioReady = ref(false)
const audioProgress = ref(0)
const audioDuration = ref(0)
const currentMood = ref(props.mood)

// Typewriter effect
const displayText = ref('')
const typewriterIndex = ref(0)

// Audio
let audioElement: HTMLAudioElement | null = null
let audioProgressInterval: number | null = null

// ============================================================================
// Computed
// ============================================================================
const shouldSpeak = computed(() => props.text && props.text.length > 0)

// ============================================================================
// Methods
// ============================================================================
async function generateAndPlayAudio() {
  if (!props.text || props.text.length === 0) return

  isThinking.value = true

  try {
    // Generate TTS
    const response = await ttsApi.speak({
      text: props.text,
      voice: props.voice,
      speed: props.speed
    })

    if (response.success && response.data) {
      // Create audio element - use the API URL, not local path
      // Extract base URL from VITE_API_BASE_URL (remove /api/v1 suffix)
      const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api/v1'
      const baseUrl = apiBaseUrl.replace(/\/api\/v1$/, '')
      const audioUrl = `${baseUrl}${response.data.audio_url}`

      if (audioElement) {
        audioElement.pause()
        audioElement = null
      }

      audioElement = new Audio(audioUrl)
      audioDuration.value = response.data.duration_ms || 0
      audioReady.value = true

      // Audio events
      audioElement.onplay = () => {
        isSpeaking.value = true
        isThinking.value = false
        emit('speech-start')
        startProgressTracking()
      }

      audioElement.onended = () => {
        isSpeaking.value = false
        audioProgress.value = 100
        stopProgressTracking()
        emit('speech-end')
      }

      audioElement.onerror = (e) => {
        isSpeaking.value = false
        isThinking.value = false
        stopProgressTracking()
        // Fallback to browser TTS on audio error
        console.warn('Audio playback failed, using browser TTS fallback')
        fallbackBrowserTTS()
      }

      // Auto-play if enabled
      if (props.autoPlay) {
        await audioElement.play()
      }
    } else {
      // API returned error, use browser TTS fallback
      console.warn('TTS API failed, using browser TTS fallback:', response.error)
      isThinking.value = false
      fallbackBrowserTTS()
    }
  } catch (error) {
    console.warn('TTS generation error, using browser TTS fallback:', error)
    isThinking.value = false

    // Fallback: Use browser TTS
    fallbackBrowserTTS()
  }
}

function fallbackBrowserTTS() {
  if (!props.text || !('speechSynthesis' in window)) return

  const utterance = new SpeechSynthesisUtterance(props.text)
  utterance.lang = 'de-DE'
  utterance.rate = props.speed

  utterance.onstart = () => {
    isSpeaking.value = true
    emit('speech-start')
  }

  utterance.onend = () => {
    isSpeaking.value = false
    emit('speech-end')
  }

  window.speechSynthesis.speak(utterance)
}

function playAudio() {
  if (audioElement && audioReady.value) {
    audioElement.play()
  }
}

function pauseAudio() {
  if (audioElement) {
    audioElement.pause()
    isSpeaking.value = false
    stopProgressTracking()
  }

  // Also stop browser TTS
  if ('speechSynthesis' in window) {
    window.speechSynthesis.pause()
  }
}

function skipToEnd() {
  pauseAudio()

  if (audioElement) {
    audioElement.currentTime = audioElement.duration
  }

  // Show full text immediately
  displayText.value = props.text
  isSpeaking.value = false
  audioProgress.value = 100

  emit('skip')
  emit('speech-end')
}

function startProgressTracking() {
  stopProgressTracking()

  audioProgressInterval = window.setInterval(() => {
    if (audioElement && audioDuration.value > 0) {
      audioProgress.value = (audioElement.currentTime / audioElement.duration) * 100
    }
  }, 100)
}

function stopProgressTracking() {
  if (audioProgressInterval) {
    clearInterval(audioProgressInterval)
    audioProgressInterval = null
  }
}

// Typewriter effect
function startTypewriter() {
  if (!props.typewriter) {
    displayText.value = props.text
    return
  }

  displayText.value = ''
  typewriterIndex.value = 0

  const typeNext = () => {
    if (typewriterIndex.value < props.text.length) {
      displayText.value += props.text[typewriterIndex.value]
      typewriterIndex.value++
      setTimeout(typeNext, props.typewriterSpeed)
    }
  }

  typeNext()
}

function handleClick() {
  emit('click')
}

// ============================================================================
// Watchers
// ============================================================================
watch(() => props.text, (newText) => {
  if (newText) {
    audioProgress.value = 0
    audioReady.value = false
    startTypewriter()

    if (props.autoPlay) {
      generateAndPlayAudio()
    }
  }
}, { immediate: true })

watch(() => props.mood, (newMood) => {
  currentMood.value = newMood
})

// ============================================================================
// Lifecycle
// ============================================================================
onUnmounted(() => {
  stopProgressTracking()

  if (audioElement) {
    audioElement.pause()
    audioElement = null
  }

  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel()
  }
})

// ============================================================================
// Expose for parent components
// ============================================================================
defineExpose({
  speak: generateAndPlayAudio,
  pause: pauseAudio,
  skip: skipToEnd,
  isSpeaking,
  isThinking
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

/* Glow effect */
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

/* Avatar Image Wrapper */
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

/* Avatar Image */
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

.sound-wave:nth-child(1) {
  animation-delay: 0s;
}

.sound-wave:nth-child(2) {
  animation-delay: 0.1s;
  height: 12px;
}

.sound-wave:nth-child(3) {
  animation-delay: 0.2s;
}

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

.status-dot.idle {
  background: #9ca3af;
}

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
   Speech Bubble
   ============================================================================ */
.speech-bubble {
  background: white;
  border-radius: 16px;
  padding: 1rem;
  max-width: var(--bubble-max-width);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  position: relative;
}

.bubble-content {
  margin-bottom: 0.5rem;
}

.bubble-text {
  margin: 0;
  font-size: 0.9375rem;
  line-height: 1.5;
  color: #1f2937;
}

/* Audio progress */
.audio-progress {
  height: 3px;
  background: #e5e7eb;
  border-radius: 2px;
  margin-top: 0.75rem;
  overflow: hidden;
}

.audio-progress-fill {
  height: 100%;
  background: var(--primary-color);
  transition: width 0.1s linear;
}

/* Bubble actions */
.bubble-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}

.bubble-btn {
  background: none;
  border: none;
  padding: 0.25rem;
  cursor: pointer;
  font-size: 1rem;
  opacity: 0.6;
  transition: opacity 0.2s ease;
}

.bubble-btn:hover {
  opacity: 1;
}

/* Bubble pointer */
.bubble-pointer {
  position: absolute;
  width: 12px;
  height: 12px;
  background: white;
  transform: rotate(45deg);
}

.position-floating .bubble-pointer {
  right: -6px;
  top: 20px;
}

.position-inline .bubble-pointer {
  left: -6px;
  top: 20px;
}

.position-corner-br .bubble-pointer,
.position-corner-tr .bubble-pointer {
  right: 20px;
  bottom: -6px;
}

.position-corner-bl .bubble-pointer,
.position-corner-tl .bubble-pointer {
  left: 20px;
  bottom: -6px;
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
   Mood Variants - Glow colors for different moods
   ============================================================================ */
.mood-friendly .avatar-glow {
  --glow-color: rgba(99, 102, 241, 0.4);
}

.mood-excited .avatar-glow {
  --glow-color: rgba(245, 87, 108, 0.4);
}

.mood-thinking .avatar-glow {
  --glow-color: rgba(79, 172, 254, 0.4);
}

.mood-encouraging .avatar-glow {
  --glow-color: rgba(67, 233, 123, 0.4);
}

.mood-neutral .avatar-glow {
  --glow-color: rgba(156, 163, 175, 0.4);
}

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

.bubble-pop-enter-active,
.bubble-pop-leave-active {
  transition: all 0.2s ease;
}

.bubble-pop-enter-from,
.bubble-pop-leave-to {
  opacity: 0;
  transform: scale(0.9);
}

/* ============================================================================
   Dark Mode
   ============================================================================ */
:root.dark .speech-bubble,
.dark .speech-bubble {
  background: #1f2937;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

:root.dark .bubble-text,
.dark .bubble-text {
  color: #f3f4f6;
}

:root.dark .bubble-pointer,
.dark .bubble-pointer {
  background: #1f2937;
}

:root.dark .audio-progress,
.dark .audio-progress {
  background: #374151;
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

  .bubble-text {
    font-size: 0.875rem;
  }
}
</style>
