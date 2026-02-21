/**
 * ActivityEditorContainerView.vue
 *
 * FloatingWindow content for editing a single LM activity.
 * Two tabs: Edit (form) and Preview (learner simulation).
 */
<script setup lang="ts">
import { ref, toRef } from 'vue'
import { useI18n } from 'vue-i18n'
import type { LessonActivity } from '../composables'
import { useActivityEditor } from '../composables'
import { useActivitySyncStore } from '@/application/stores/modules/content/activitySync.store'
import DifficultySelector from './primitives/DifficultySelector.vue'
import ActivityFormSwitch from './ActivityFormSwitch.vue'
import ActivityPreviewPanel from './ActivityPreviewPanel.vue'

const props = defineProps<{
  activity: LessonActivity
}>()

const emit = defineEmits<{
  'activity-saved': [updated: LessonActivity]
}>()

const { t } = useI18n()
const activitySyncStore = useActivitySyncStore()

const activeTab = ref<'edit' | 'preview'>('edit')
const activityRef = toRef(props, 'activity')

const onSaved = (updated: LessonActivity) => {
  activitySyncStore.notifySaved(updated)
  emit('activity-saved', updated)
}

const {
  localData,
  localTitle,
  localInstructions,
  localDifficulty,
  localDuration,
  saveStatus,
} = useActivityEditor(activityRef, onSaved)

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
  <div class="container-view">
    <!-- Tab bar -->
    <div class="tab-bar">
      <button
        class="tab-btn"
        :class="{ 'tab-btn--active': activeTab === 'edit' }"
        @click="activeTab = 'edit'"
      >
        {{ t('panel.manualEditor.activityEditor.tabs.edit') }}
      </button>
      <button
        class="tab-btn"
        :class="{ 'tab-btn--active': activeTab === 'preview' }"
        @click="activeTab = 'preview'"
      >
        {{ t('panel.manualEditor.activityEditor.tabs.preview') }}
      </button>
      <div class="tab-spacer" />
      <span v-if="saveStatus !== 'idle'" class="save-status" :class="`save-status--${saveStatus}`">
        {{ statusLabel(saveStatus) }}
      </span>
    </div>

    <!-- Edit tab -->
    <div v-show="activeTab === 'edit'" class="tab-content">
      <div class="editor-form">
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

        <div class="editor-divider" />

        <ActivityFormSwitch
          :method-type="activity.method_type"
          v-model="localData"
        />
      </div>
    </div>

    <!-- Preview tab -->
    <div v-show="activeTab === 'preview'" class="tab-content">
      <ActivityPreviewPanel
        :activity="activity"
        :data="localData"
      />
    </div>
  </div>
</template>

<style scoped>
.container-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.tab-bar {
  display: flex;
  align-items: center;
  gap: 0;
  border-bottom: 1px solid var(--color-border);
  padding: 0 12px;
  flex-shrink: 0;
}

.tab-btn {
  padding: 8px 16px;
  border: none;
  background: none;
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-secondary);
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: color 0.15s, border-color 0.15s;
}

.tab-btn:hover {
  color: var(--color-text-primary);
}

.tab-btn--active {
  color: var(--color-accent);
  border-bottom-color: var(--color-accent);
}

.tab-spacer {
  flex: 1;
}

.save-status {
  font-size: 11px;
  padding: 2px 8px;
}

.save-status--saving { color: var(--color-text-tertiary); }
.save-status--saved { color: var(--color-success); }
.save-status--error { color: var(--color-error); }

.tab-content {
  flex: 1;
  overflow-y: auto;
  min-height: 0;
}

.editor-form {
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 10px;
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
</style>
