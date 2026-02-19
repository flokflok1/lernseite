<!--
  TutorSpeechBubble - Speech bubble with audio controls for TutorAvatar

  Displays the tutor's text with optional audio progress bar and
  playback controls (play, pause, skip).
-->

<template>
  <Transition name="bubble-pop">
    <div v-if="visible && displayText" class="speech-bubble">
      <div class="bubble-content">
        <p class="bubble-text">{{ displayText }}</p>

        <div v-if="isSpeaking && audioDuration > 0" class="audio-progress">
          <div
            class="audio-progress-fill"
            :style="{ width: `${audioProgress}%` }"
          ></div>
        </div>
      </div>

      <div class="bubble-actions" v-if="showControls">
        <button
          v-if="isSpeaking"
          @click.stop="$emit('pause')"
          class="bubble-btn"
          title="Pause"
        >
          &#9208;&#65039;
        </button>
        <button
          v-else-if="audioReady && !isSpeaking"
          @click.stop="$emit('play')"
          class="bubble-btn"
          title="Abspielen"
        >
          &#9654;&#65039;
        </button>
        <button
          @click.stop="$emit('skip')"
          class="bubble-btn skip"
          title="Überspringen"
        >
          &#9197;&#65039;
        </button>
      </div>

      <div class="bubble-pointer"></div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
interface Props {
  visible: boolean
  displayText: string
  isSpeaking: boolean
  audioReady: boolean
  audioProgress: number
  audioDuration: number
  showControls: boolean
}

defineProps<Props>()

defineEmits<{
  (e: 'pause'): void
  (e: 'play'): void
  (e: 'skip'): void
}>()
</script>

<style scoped>
.speech-bubble {
  background: white;
  border-radius: 16px;
  padding: 1rem;
  max-width: var(--bubble-max-width, 320px);
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

.audio-progress {
  height: 3px;
  background: #e5e7eb;
  border-radius: 2px;
  margin-top: 0.75rem;
  overflow: hidden;
}

.audio-progress-fill {
  height: 100%;
  background: var(--primary-color, #6366f1);
  transition: width 0.1s linear;
}

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

.bubble-pointer {
  position: absolute;
  width: 12px;
  height: 12px;
  background: white;
  transform: rotate(45deg);
}

/* Pointer positions are inherited from parent position class */
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

/* Transition */
.bubble-pop-enter-active,
.bubble-pop-leave-active {
  transition: all 0.2s ease;
}

.bubble-pop-enter-from,
.bubble-pop-leave-to {
  opacity: 0;
  transform: scale(0.9);
}

/* Dark Mode */
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
</style>
