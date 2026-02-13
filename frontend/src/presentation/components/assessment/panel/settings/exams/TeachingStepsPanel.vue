<!--
  TeachingStepsPanel - Teaching Steps Editor
  Sub-component of ContentTab
-->

<template>
  <div class="steps-panel">
    <div class="panel-header">
      <span class="panel-icon">🎯</span>
      <span class="panel-title">{{ $t('aiEditorContent.teachingSteps') }}</span>
      <button @click="$emit('add')" class="add-btn">+</button>
    </div>

    <!-- Steps List -->
    <div class="steps-list">
      <div v-if="steps.length === 0" class="steps-empty">
        <span class="empty-icon-small">📝</span>
        <p>{{ $t('aiEditorContent.noSteps') }}</p>
        <button @click="$emit('generate')" class="generate-link">
          ✨ {{ $t('aiEditorContent.generateWithAi') }}
        </button>
      </div>

      <div
        v-for="(step, index) in steps"
        :key="index"
        class="step-item"
      >
        <div class="step-number">{{ index + 1 }}</div>
        <div class="step-content">
          <input
            :value="step.title"
            @input="updateStep(index, 'title', ($event.target as HTMLInputElement).value)"
            type="text"
            class="step-title-input"
            :placeholder="$t('aiEditorContent.titlePlaceholder')"
          />
          <textarea
            :value="step.speech"
            @input="updateStep(index, 'speech', ($event.target as HTMLTextAreaElement).value)"
            class="step-speech-input"
            rows="2"
            :placeholder="$t('aiEditorContent.speechPlaceholder')"
          ></textarea>
        </div>
        <button @click="$emit('remove', index)" class="step-delete">🗑️</button>
      </div>
    </div>

    <!-- Generate Button -->
    <div class="steps-footer">
      <button @click="$emit('generate')" class="generate-steps-btn" :disabled="isGenerating">
        ✨ {{ $t('aiEditorContent.generateSteps') }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
interface TeachingStep {
  title: string
  speech: string
  animation: string
  duration: string
}

const props = defineProps<{
  steps: TeachingStep[]
  isGenerating: boolean
}>()

const emit = defineEmits<{
  (e: 'add'): void
  (e: 'remove', index: number): void
  (e: 'generate'): void
  (e: 'update', index: number, field: string, value: string): void
}>()

function updateStep(index: number, field: string, value: string) {
  emit('update', index, field, value)
}
</script>

<style scoped>
.steps-panel {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface-secondary);
}

.panel-icon { font-size: 1rem; }

.panel-title {
  flex: 1;
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.add-btn {
  padding: 0.25rem 0.5rem;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  cursor: pointer;
  line-height: 1;
}

.steps-list {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
}

.steps-empty {
  text-align: center;
  padding: 2rem 1rem;
  color: var(--color-text-secondary);
}

.empty-icon-small {
  font-size: 2rem;
  display: block;
  margin-bottom: 0.5rem;
}

.generate-link {
  background: none;
  border: none;
  color: var(--color-primary);
  font-size: 0.8125rem;
  cursor: pointer;
  margin-top: 0.5rem;
}

.generate-link:hover { text-decoration: underline; }

.step-item {
  display: flex;
  gap: 0.75rem;
  padding: 0.75rem;
  background: var(--color-surface-secondary);
  border-radius: 0.5rem;
  margin-bottom: 0.5rem;
}

.step-number {
  width: 1.75rem;
  height: 1.75rem;
  background: var(--color-primary);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 600;
  flex-shrink: 0;
}

.step-content {
  flex: 1;
  min-width: 0;
}

.step-title-input {
  width: 100%;
  background: transparent;
  border: none;
  color: var(--color-text-primary);
  font-size: 0.8125rem;
  font-weight: 500;
  margin-bottom: 0.375rem;
}

.step-title-input:focus { outline: none; }

.step-speech-input {
  width: 100%;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  padding: 0.5rem;
  color: var(--color-text-secondary);
  font-size: 0.75rem;
  resize: none;
}

.step-speech-input:focus {
  outline: none;
  border-color: var(--color-primary);
}

.step-delete {
  padding: 0.25rem;
  background: transparent;
  border: none;
  cursor: pointer;
  opacity: 0.5;
  transition: opacity 0.15s;
}

.step-delete:hover { opacity: 1; }

.steps-footer {
  padding: 0.75rem;
  border-top: 1px solid var(--color-border);
}

.generate-steps-btn {
  width: 100%;
  padding: 0.625rem;
  background: linear-gradient(135deg, #3b82f6, #06b6d4);
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.8125rem;
  font-weight: 500;
  cursor: pointer;
  transition: opacity 0.15s;
}

.generate-steps-btn:hover:not(:disabled) { opacity: 0.9; }
.generate-steps-btn:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
