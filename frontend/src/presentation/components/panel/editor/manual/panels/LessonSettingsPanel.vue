/**
 * LessonSettingsPanel.vue
 *
 * Settings for the currently selected lesson.
 * Editable title, estimated reading time, position, internal notes.
 */

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useCourseEditorStore } from '@/application/stores/modules/content/courseEditor.store'

const { t } = useI18n()
const store = useCourseEditorStore()

const localTitle = ref('')
const localNotes = ref('')

const lesson = computed(() => store.currentLesson)

// Estimated reading time (words per minute)
const estimatedReadingTime = computed(() => {
  if (!lesson.value?.content) return 0
  const content = typeof lesson.value.content === 'string' ? lesson.value.content : ''
  const text = content.replace(/<[^>]*>/g, '')
  const words = text.split(/\s+/).filter(w => w.length > 0).length
  return Math.max(1, Math.ceil(words / 200))
})

// Sync local state with store
watch(lesson, (newLesson) => {
  if (newLesson) {
    localTitle.value = newLesson.title || ''
    localNotes.value = newLesson.notes || ''
  }
}, { immediate: true })

const updateTitle = async () => {
  if (!lesson.value || localTitle.value === lesson.value.title) return
  await store.updateLessonMeta(lesson.value.lesson_id, { title: localTitle.value })
}

const updateNotes = async () => {
  if (!lesson.value) return
  await store.updateLessonMeta(lesson.value.lesson_id, { notes: localNotes.value })
}
</script>

<template>
  <div class="lesson-settings-panel">
    <!-- No lesson selected -->
    <div v-if="!lesson" class="empty-state">
      <p>{{ $t('panel.manualEditor.content.noLessonSelected') }}</p>
    </div>

    <!-- Lesson settings -->
    <div v-else class="settings-form">
      <!-- Title -->
      <div class="form-group">
        <label class="form-label">{{ $t('panel.manualEditor.lessonSettings.lessonTitle') }}</label>
        <input
          v-model="localTitle"
          type="text"
          class="form-input"
          @blur="updateTitle"
          @keydown.enter="updateTitle"
        />
      </div>

      <!-- Reading time -->
      <div class="form-group">
        <label class="form-label">{{ $t('panel.manualEditor.lessonSettings.readingTime') }}</label>
        <div class="reading-time">
          <span class="time-value">{{ estimatedReadingTime }} {{ $t('panel.manualEditor.lessonSettings.minuteUnit') }}</span>
          <span class="time-hint">{{ $t('panel.manualEditor.lessonSettings.readingTimeAuto') }}</span>
        </div>
      </div>

      <!-- Order display -->
      <div class="form-group">
        <label class="form-label">{{ $t('panel.manualEditor.lessonSettings.position') }}</label>
        <div class="position-display">
          #{{ lesson.order_index ?? '-' }}
        </div>
      </div>

      <!-- Internal notes -->
      <div class="form-group">
        <label class="form-label">{{ $t('panel.manualEditor.lessonSettings.notes') }}</label>
        <textarea
          v-model="localNotes"
          class="form-textarea"
          rows="4"
          :placeholder="$t('panel.manualEditor.lessonSettings.notesHint')"
          @blur="updateNotes"
        ></textarea>
      </div>

    </div>
  </div>
</template>

<style scoped>
.lesson-settings-panel {
  height: 100%;
  overflow-y: auto;
  padding: 16px;
}

.empty-state {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-state p {
  color: var(--color-text-tertiary);
  font-size: 13px;
  margin: 0;
}

.settings-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.form-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.form-input {
  padding: 8px 10px;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.15s;
  background: var(--color-surface);
  color: var(--color-text-primary);
}

.form-input:focus {
  outline: none;
  border-color: var(--color-accent);
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--color-accent) 10%, transparent);
}

/* Reading time */
.reading-time {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.time-value {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.time-hint {
  font-size: 11px;
  color: var(--color-text-tertiary);
}

/* Position */
.position-display {
  font-size: 14px;
  color: var(--color-text-secondary);
  padding: 6px 0;
}

/* Notes */
.form-textarea {
  padding: 8px 10px;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  font-size: 13px;
  resize: vertical;
  font-family: inherit;
  min-height: 80px;
  transition: border-color 0.15s;
  background: var(--color-surface);
  color: var(--color-text-primary);
}

.form-textarea:focus {
  outline: none;
  border-color: var(--color-accent);
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--color-accent) 10%, transparent);
}
</style>
