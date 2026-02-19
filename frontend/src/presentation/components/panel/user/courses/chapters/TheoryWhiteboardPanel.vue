<!--
  TheoryWhiteboardPanel - Whiteboard + TTS controls for chapter theory

  Displays the interactive whiteboard canvas and playback controls
  for starting/stopping the animated explanation with voice.
-->

<template>
  <div class="whiteboard-section">
    <div class="whiteboard-header">
      <span class="whiteboard-icon">&#128203;</span>
      <span>{{ $t('chapterTheory.whiteboard.title') }}</span>
    </div>

    <div class="whiteboard-container" :class="{ animating: isAnimating }">
      <InteractiveWhiteboard
        ref="whiteboardRef"
        :width="480"
        :height="320"
        :show-controls="false"
        background-color="#1e293b"
        text-color="#f1f5f9"
        @action-complete="$emit('action-complete', $event)"
      />
    </div>

    <!-- TTS Controls -->
    <div class="tts-controls">
      <button
        v-if="!isPlaying"
        class="play-btn"
        :disabled="isAnimating"
        @click="$emit('start')"
      >
        <span class="btn-icon">&#9654;</span>
        {{ $t('chapterTheory.controls.startExplanation') }}
      </button>
      <button
        v-else
        class="stop-btn"
        @click="$emit('stop')"
      >
        <span class="btn-icon">&#9632;</span>
        {{ $t('chapterTheory.controls.stop') }}
      </button>

      <div class="voice-select">
        <label>{{ $t('chapterTheory.controls.voice') }}</label>
        <select :value="selectedVoice" @input="$emit('update:selectedVoice', ($event.target as HTMLSelectElement).value)">
          <option value="nova">{{ $t('chapterTheory.voices.nova') }}</option>
          <option value="alloy">{{ $t('chapterTheory.voices.alloy') }}</option>
          <option value="echo">{{ $t('chapterTheory.voices.echo') }}</option>
          <option value="onyx">{{ $t('chapterTheory.voices.onyx') }}</option>
          <option value="fable">{{ $t('chapterTheory.voices.fable') }}</option>
          <option value="shimmer">{{ $t('chapterTheory.voices.shimmer') }}</option>
        </select>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { InteractiveWhiteboard } from '@/presentation/components/public/system-features/tutor/user'

interface Props {
  isAnimating: boolean
  isPlaying: boolean
  selectedVoice: string
}

defineProps<Props>()

defineEmits<{
  (e: 'start'): void
  (e: 'stop'): void
  (e: 'action-complete', action: unknown): void
  (e: 'update:selectedVoice', voice: string): void
}>()

const whiteboardRef = ref<InstanceType<typeof InteractiveWhiteboard> | null>(null)

defineExpose({
  whiteboardRef
})
</script>

<style scoped>
.whiteboard-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.whiteboard-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--color-text-secondary, #94a3b8);
  padding-bottom: 0.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.whiteboard-icon {
  font-size: 1rem;
}

.whiteboard-container {
  background: #0f172a;
  border-radius: 0.75rem;
  padding: 0.5rem;
  border: 1px solid rgba(99, 102, 241, 0.2);
  transition: border-color 0.3s, box-shadow 0.3s;
}

.whiteboard-container.animating {
  border-color: rgba(139, 92, 246, 0.5);
  box-shadow: 0 0 20px rgba(139, 92, 246, 0.2);
}

/* TTS Controls */
.tts-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.play-btn, .stop-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.play-btn {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
}

.play-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.play-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.stop-btn {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: white;
}

.stop-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}

.btn-icon {
  font-size: 1.2rem;
}

.voice-select {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--color-text-secondary, #94a3b8);
}

.voice-select select {
  padding: 0.5rem 0.75rem;
  background: rgba(15, 23, 42, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.375rem;
  color: var(--color-text-primary, #f1f5f9);
  font-size: 0.875rem;
}
</style>
