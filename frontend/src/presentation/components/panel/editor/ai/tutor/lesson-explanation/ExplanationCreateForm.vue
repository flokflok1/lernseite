<!--
  ExplanationCreateForm - Form for creating a new lesson explanation
-->

<template>
  <div class="create-form">
    <div class="panel-header">
      <span class="panel-icon">&#x2728;</span>
      <span class="panel-title">{{ $t('lessonExplanationView.newExplanation') }}</span>
    </div>

    <div class="form-content">
      <div class="form-section">
        <label>{{ $t('lessonExplanationView.styleLabel') }}</label>
        <select v-model="localStyle" class="form-select">
          <option value="adhs">{{ $t('lessonExplanationView.styles.adhs') }}</option>
          <option value="detailed">{{ $t('lessonExplanationView.styles.detailed') }}</option>
          <option value="short">{{ $t('lessonExplanationView.styles.short') }}</option>
          <option value="exam_focus">{{ $t('lessonExplanationView.styles.examFocus') }}</option>
        </select>
      </div>

      <div class="form-section">
        <label>{{ $t('lessonExplanationView.voiceLabel') }}</label>
        <select v-model="localVoice" class="form-select">
          <option v-for="voice in voices" :key="voice.id" :value="voice.id">
            {{ voice.name }}
          </option>
        </select>
      </div>

      <div class="form-section">
        <label class="checkbox-label">
          <input type="checkbox" v-model="localGenerateWithAudio" />
          {{ $t('lessonExplanationView.generateWithAudio') }}
        </label>
      </div>

      <button
        @click="handleGenerate"
        class="generate-btn"
        :disabled="isGenerating"
      >
        <span v-if="isGenerating">{{ $t('lessonExplanationView.generating') }}</span>
        <span v-else>{{ $t('lessonExplanationView.generate') }}</span>
      </button>

      <button @click="$emit('cancel-create')" class="cancel-btn">
        {{ $t('lessonExplanationView.cancel') }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * ExplanationCreateForm - Form to configure and trigger explanation generation.
 */
import { ref, watch } from 'vue'

interface Voice {
  id: string
  name: string
}

interface Props {
  isGenerating: boolean
  voices: Voice[]
  selectedVoice: string
  style: string
  generateWithAudio: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isGenerating: false,
  voices: () => [],
  selectedVoice: '',
  style: 'adhs',
  generateWithAudio: false
})

const emit = defineEmits<{
  (e: 'generate', options: { style: string; voice: string; generateWithAudio: boolean }): void
  (e: 'cancel-create'): void
}>()

const localStyle = ref(props.style)
const localVoice = ref(props.selectedVoice)
const localGenerateWithAudio = ref(props.generateWithAudio)

watch(() => props.selectedVoice, (val) => {
  localVoice.value = val
})

function handleGenerate(): void {
  emit('generate', {
    style: localStyle.value,
    voice: localVoice.value,
    generateWithAudio: localGenerateWithAudio.value
  })
}
</script>

<style scoped>
.create-form {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface-secondary);
}

.panel-icon {
  font-size: 1rem;
}

.panel-title {
  font-weight: 600;
  font-size: 0.875rem;
  flex: 1;
}

.form-content {
  flex: 1;
  padding: 1.5rem;
  overflow-y: auto;
}

.form-section {
  margin-bottom: 1.25rem;
}

.form-section label {
  display: block;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
}

.form-select {
  width: 100%;
  padding: 0.625rem;
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  font-size: 0.875rem;
  background: var(--color-surface);
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.checkbox-label input {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.generate-btn {
  width: 100%;
  padding: 0.75rem;
  margin-bottom: 0.75rem;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}

.generate-btn:hover:not(:disabled) {
  background: var(--color-primary-dark);
}

.generate-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.cancel-btn {
  width: 100%;
  padding: 0.75rem;
  background: var(--color-surface-secondary);
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  font-size: 0.875rem;
  cursor: pointer;
}
</style>
