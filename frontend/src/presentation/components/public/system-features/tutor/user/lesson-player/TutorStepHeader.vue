<!--
  TutorStepHeader - Header section with avatar, tutor info, and TTS controls
-->

<template>
  <div class="tutor-header">
    <div class="tutor-avatar">
      <span class="avatar-emoji">{{ $t('lesson.tutorPlayer.teacherIcon') }}</span>
    </div>
    <div class="tutor-info">
      <span class="tutor-name">{{ $t('lesson.tutorPlayer.tutorExplains', { lesson: lessonTitle }) }}</span>
      <span class="tutor-status" :class="{ speaking: isSpeaking }">
        {{ isSpeaking ? $t('lesson.tutorPlayer.speaking') : $t('lesson.tutorPlayer.ready') }}
      </span>
    </div>
    <div class="tutor-controls">
      <!-- Voice Select -->
      <select v-model="selectedVoiceLocal" class="tts-select voice-select" :title="$t('lesson.tutorPlayer.voice')">
        <option value="nova">{{ $t('lesson.tutorPlayer.voices.nova') }}</option>
        <option value="alloy">{{ $t('lesson.tutorPlayer.voices.alloy') }}</option>
        <option value="echo">{{ $t('lesson.tutorPlayer.voices.echo') }}</option>
        <option value="onyx">{{ $t('lesson.tutorPlayer.voices.onyx') }}</option>
        <option value="shimmer">{{ $t('lesson.tutorPlayer.voices.shimmer') }}</option>
      </select>
      <!-- Model Select -->
      <select v-model="selectedTTSModelLocal" class="tts-select model-select" :title="$t('lesson.tutorPlayer.ttsModel')">
        <option value="browser">{{ $t('lesson.tutorPlayer.browserFree') }}</option>
        <option value="tts-1">{{ $t('lesson.tutorPlayer.tts1Standard') }}</option>
        <option value="tts-1-hd">{{ $t('lesson.tutorPlayer.tts1HD') }}</option>
      </select>
      <button @click="$emit('toggle-tts')" class="tts-btn" :class="{ active: ttsEnabled }" :title="$t('lesson.tutorPlayer.speechOutput')">
        {{ ttsEnabled ? $t('lesson.tutorPlayer.audioOn') : $t('lesson.tutorPlayer.audioOff') }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * TutorStepHeader - Tutor avatar, status info, and TTS controls.
 */
import { ref, watch } from 'vue'

interface Props {
  lessonTitle: string
  isSpeaking: boolean
  ttsEnabled: boolean
  selectedVoice: string
  selectedTTSModel: string
}

const props = defineProps<Props>()

defineEmits<{
  'toggle-tts': []
}>()

const selectedVoiceLocal = ref(props.selectedVoice)
const selectedTTSModelLocal = ref(props.selectedTTSModel)

watch(() => props.selectedVoice, (newVal) => {
  selectedVoiceLocal.value = newVal
})

watch(() => props.selectedTTSModel, (newVal) => {
  selectedTTSModelLocal.value = newVal
})
</script>

<style scoped>
.tutor-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: var(--color-surface, #1e293b);
  border: 1px solid var(--color-border, #334155);
  border-radius: 0.75rem;
}

.tutor-avatar {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  color: white;
  flex-shrink: 0;
}

.tutor-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.tutor-name {
  font-weight: 600;
  color: var(--color-text-primary, #f1f5f9);
  font-size: 0.9375rem;
}

.tutor-status {
  font-size: 0.75rem;
  color: var(--color-text-tertiary, #64748b);
  margin-top: 0.25rem;
}

.tutor-status.speaking {
  color: #10b981;
}

.tutor-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.tts-select {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--color-border, #334155);
  border-radius: 0.5rem;
  background: var(--color-surface, #1e293b);
  color: var(--color-text-primary, #f1f5f9);
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
}

.tts-select:hover {
  border-color: var(--color-primary, #6366f1);
}

.tts-select:focus {
  outline: none;
  border-color: var(--color-primary, #6366f1);
}

.voice-select {
  min-width: 90px;
}

.model-select {
  min-width: 140px;
}

.tts-btn {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--color-border, #334155);
  border-radius: 0.5rem;
  background: transparent;
  font-size: 0.75rem;
  cursor: pointer;
  color: var(--color-text-secondary, #94a3b8);
  transition: all 0.2s;
}

.tts-btn:hover {
  border-color: var(--color-primary, #6366f1);
  color: var(--color-text-primary, #f1f5f9);
}

.tts-btn.active {
  background: rgba(16, 185, 129, 0.15);
  border-color: #10b981;
  color: #10b981;
}
</style>
