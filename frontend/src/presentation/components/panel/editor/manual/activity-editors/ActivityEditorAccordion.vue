/**
 * ActivityEditorAccordion.vue
 *
 * Expanded editor for a single activity. Shows common fields
 * (title, difficulty, duration, instructions) + LM-specific form below.
 */
<script setup lang="ts">
import { toRef } from 'vue'
import { useI18n } from 'vue-i18n'
import type { LessonActivity } from '../composables'
import { useActivityEditor } from '../composables'
import DifficultySelector from './primitives/DifficultySelector.vue'
import ActivityFormSwitch from './ActivityFormSwitch.vue'

const props = defineProps<{
  activity: LessonActivity
}>()

const emit = defineEmits<{
  saved: [updated: LessonActivity]
}>()

const { t } = useI18n()
const activityRef = toRef(props, 'activity')

const {
  localData,
  localTitle,
  localInstructions,
  localDifficulty,
  localDuration,
  saveStatus,
} = useActivityEditor(activityRef, (updated) => emit('saved', updated))

const statusLabel = (s: string) => {
  const map: Record<string, string> = {
    idle: '',
    saving: t('panel.manualEditor.activityEditor.saving'),
    saved: t('panel.manualEditor.activityEditor.saved'),
    error: t('panel.manualEditor.activityEditor.error'),
  }
  return map[s] ?? ''
}
</script>

<template>
  <div class="activity-editor">
    <!-- Common fields -->
    <div class="editor-field">
      <label>{{ t('panel.manualEditor.activityEditor.commonFields.title') }}</label>
      <input v-model="localTitle" type="text" class="editor-input" />
    </div>

    <div class="editor-row">
      <div class="editor-field">
        <label>{{ t('panel.manualEditor.activityEditor.commonFields.difficulty') }}</label>
        <DifficultySelector v-model="localDifficulty" />
      </div>
      <div class="editor-field">
        <label>{{ t('panel.manualEditor.activityEditor.commonFields.duration') }}</label>
        <input v-model.number="localDuration" type="number" min="0" class="editor-input editor-input--short" />
      </div>
    </div>

    <div class="editor-field">
      <label>{{ t('panel.manualEditor.activityEditor.commonFields.instructions') }}</label>
      <textarea v-model="localInstructions" class="editor-textarea" rows="2" />
    </div>

    <!-- LM-specific form -->
    <div class="editor-divider" />
    <ActivityFormSwitch
      :method-type="activity.method_type"
      v-model="localData"
    />

    <!-- Save status -->
    <div v-if="saveStatus !== 'idle'" class="editor-status" :class="`editor-status--${saveStatus}`">
      {{ statusLabel(saveStatus) }}
    </div>
  </div>
</template>

<style scoped>
.activity-editor {
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  background: var(--color-surface-alt, var(--color-surface));
  border: 1px solid var(--color-border);
  border-top: none;
  border-radius: 0 0 4px 4px;
}

.editor-field {
  display: flex;
  flex-direction: column;
  gap: 3px;
  flex: 1;
}

.editor-field label {
  font-size: 11px;
  font-weight: 600;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.editor-row {
  display: flex;
  gap: 12px;
}

.editor-input,
.editor-textarea {
  padding: 6px 8px;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  font-size: 13px;
  background: var(--color-surface);
  color: var(--color-text-primary);
  transition: border-color 0.15s;
}

.editor-input:focus,
.editor-textarea:focus {
  outline: none;
  border-color: var(--color-accent);
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--color-accent) 10%, transparent);
}

.editor-input--short {
  max-width: 100px;
}

.editor-textarea {
  resize: vertical;
  min-height: 40px;
}

.editor-divider {
  border-top: 1px solid var(--color-border);
  margin: 4px 0;
}

.editor-status {
  font-size: 11px;
  text-align: right;
  padding: 2px 0;
}

.editor-status--saving { color: var(--color-text-tertiary); }
.editor-status--saved { color: var(--color-success); }
.editor-status--error { color: var(--color-error); }
</style>
