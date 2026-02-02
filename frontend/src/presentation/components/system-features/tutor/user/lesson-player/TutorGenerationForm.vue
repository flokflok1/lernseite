<template>
  <div class="generation-form">
    <div class="form-icon">{{ $t('lesson.tutorPlayer.teacherIcon') }}</div>
    <h3>{{ $t('lesson.tutorPlayer.createNewExplanation') }}</h3>
    <p>{{ $t('lesson.tutorPlayer.createDescription') }}</p>

    <!-- Generation Options -->
    <div class="generation-options">
      <!-- Style Select -->
      <div class="option-row">
        <label class="option-label">{{ $t('lesson.tutorPlayer.style') }}:</label>
        <select v-model="selectedStyleLocal" class="option-select">
          <option value="adhs">{{ $t('lesson.tutorPlayer.styles.adhs') }}</option>
          <option value="detailed">{{ $t('lesson.tutorPlayer.styles.detailed') }}</option>
          <option value="short">{{ $t('lesson.tutorPlayer.styles.short') }}</option>
          <option value="exam_focus">{{ $t('lesson.tutorPlayer.styles.examFocus') }}</option>
        </select>
      </div>

      <!-- Voice Select -->
      <div class="option-row">
        <label class="option-label">{{ $t('lesson.tutorPlayer.voice') }}:</label>
        <select v-model="selectedVoiceLocal" class="option-select">
          <option value="nova">{{ $t('lesson.tutorPlayer.voices.nova') }}</option>
          <option value="alloy">{{ $t('lesson.tutorPlayer.voices.alloy') }}</option>
          <option value="echo">{{ $t('lesson.tutorPlayer.voices.echo') }}</option>
          <option value="onyx">{{ $t('lesson.tutorPlayer.voices.onyx') }}</option>
          <option value="shimmer">{{ $t('lesson.tutorPlayer.voices.shimmer') }}</option>
        </select>
      </div>

      <!-- Generate with TTS Checkbox -->
      <div class="option-row">
        <label class="option-checkbox">
          <input type="checkbox" v-model="generateWithTTSLocal" />
          <span>{{ $t('lesson.tutorPlayer.generateWithAudio') }}</span>
        </label>
      </div>
    </div>

    <!-- Form Buttons -->
    <div class="form-buttons">
      <button @click="handleGenerate" class="generate-btn">
        {{ $t('lesson.tutorPlayer.generateWithAI') }}
      </button>
      <button v-if="hasExplanations" @click="$emit('cancel')" class="cancel-form-btn">
        {{ $t('common.cancel') }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * TutorGenerationForm Component
 * ==============================
 * Form for generating new explanations with AI (style, voice, TTS options)
 */
import { ref, watch } from 'vue'

interface Props {
  selectedStyle: string
  selectedVoice: string
  generateWithTTS: boolean
  hasExplanations: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'generate': [options: { style: string; voice: string; generateWithTTS: boolean }]
  'cancel': []
}>()

// Local state synced with props
const selectedStyleLocal = ref(props.selectedStyle)
const selectedVoiceLocal = ref(props.selectedVoice)
const generateWithTTSLocal = ref(props.generateWithTTS)

// Watch for external changes
watch(() => props.selectedStyle, (newVal) => {
  selectedStyleLocal.value = newVal
})

watch(() => props.selectedVoice, (newVal) => {
  selectedVoiceLocal.value = newVal
})

watch(() => props.generateWithTTS, (newVal) => {
  generateWithTTSLocal.value = newVal
})

// ============================================================================
// Methods
// ============================================================================

function handleGenerate() {
  emit('generate', {
    style: selectedStyleLocal.value,
    voice: selectedVoiceLocal.value,
    generateWithTTS: generateWithTTSLocal.value
  })
}
</script>

<style scoped>
/* Generation Form */
.generation-form {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  text-align: center;
  background: var(--color-surface, #1e293b);
  border: 2px dashed var(--color-border, #334155);
  border-radius: 1rem;
}

.form-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.generation-form h3 {
  color: var(--color-text-primary, #f1f5f9);
  margin: 0 0 0.5rem;
  font-size: 1.25rem;
}

.generation-form p {
  color: var(--color-text-secondary, #94a3b8);
  margin: 0 0 1.5rem;
  font-size: 0.9375rem;
}

/* Generation Options */
.generation-options {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: var(--color-surface-secondary, #0f172a);
  border-radius: 0.5rem;
  width: 100%;
  max-width: 400px;
}

.option-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.option-label {
  font-size: 0.875rem;
  color: var(--color-text-secondary, #94a3b8);
  min-width: 60px;
  text-align: left;
}

.option-select {
  flex: 1;
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--color-border, #334155);
  border-radius: 0.375rem;
  background: var(--color-surface, #1e293b);
  color: var(--color-text-primary, #f1f5f9);
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.option-select:hover {
  border-color: var(--color-primary, #6366f1);
}

.option-select:focus {
  outline: none;
  border-color: var(--color-primary, #6366f1);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.option-checkbox {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--color-text-secondary, #94a3b8);
  cursor: pointer;
}

.option-checkbox input[type="checkbox"] {
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.option-checkbox:hover {
  color: var(--color-text-primary, #f1f5f9);
}

/* Form Buttons */
.form-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.generate-btn {
  padding: 1rem 2rem;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  border: none;
  border-radius: 0.75rem;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s;
}

.generate-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.cancel-form-btn {
  padding: 1rem 2rem;
  background: transparent;
  border: 1px solid var(--color-border, #334155);
  border-radius: 0.75rem;
  color: var(--color-text-secondary, #94a3b8);
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s;
}

.cancel-form-btn:hover {
  border-color: var(--color-primary, #6366f1);
  color: var(--color-text-primary, #f1f5f9);
}
</style>
