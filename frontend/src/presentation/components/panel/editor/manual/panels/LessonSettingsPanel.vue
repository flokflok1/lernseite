/**
 * LessonSettingsPanel.vue
 *
 * Settings for the currently selected lesson.
 * Editable title, type selector, estimated reading time, internal notes.
 * Only visible in advanced/expert editor modes.
 */

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useCourseEditorStore } from '@/application/stores/modules/content/courseEditor.store'

const { t } = useI18n()
const store = useCourseEditorStore()

const localTitle = ref('')
const localNotes = ref('')
const localType = ref('text')

const lesson = computed(() => store.currentLesson)

const lessonTypes = computed(() => [
  { value: 'text', label: t('panel.manualEditor.lessonSettings.typeText'), icon: '📝' },
  { value: 'video', label: t('panel.manualEditor.lessonSettings.typeVideo'), icon: '🎬' },
  { value: 'quiz', label: t('panel.manualEditor.lessonSettings.typeQuiz'), icon: '❓' },
  { value: 'ai', label: t('panel.manualEditor.lessonSettings.typeAi'), icon: '🤖' },
])

// Estimated reading time (words per minute)
const estimatedReadingTime = computed(() => {
  if (!lesson.value?.content) return 0
  const content = typeof lesson.value.content === 'string' ? lesson.value.content : ''
  // Strip HTML tags for word count
  const text = content.replace(/<[^>]*>/g, '')
  const words = text.split(/\s+/).filter(w => w.length > 0).length
  // Average reading speed: 200 words/minute
  return Math.max(1, Math.ceil(words / 200))
})

// Sync local state with store
watch(lesson, (newLesson) => {
  if (newLesson) {
    localTitle.value = newLesson.title || ''
    localNotes.value = (newLesson as any).notes || ''
    localType.value = newLesson.lesson_type || 'text'
  }
}, { immediate: true })

const updateTitle = async () => {
  if (!lesson.value || localTitle.value === lesson.value.title) return
  await store.updateLessonMeta(lesson.value.lesson_id, { title: localTitle.value })
}

const updateType = async (newType: string) => {
  if (!lesson.value) return
  localType.value = newType
  await store.updateLessonMeta(lesson.value.lesson_id, { lesson_type: newType })
}

const updateNotes = async () => {
  if (!lesson.value) return
  await store.updateLessonMeta(lesson.value.lesson_id, { notes: localNotes.value } as any)
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

      <!-- Type selector -->
      <div class="form-group">
        <label class="form-label">{{ $t('panel.manualEditor.lessonSettings.lessonType') }}</label>
        <div class="type-selector">
          <button
            v-for="lt in lessonTypes"
            :key="lt.value"
            :class="['type-btn', { active: localType === lt.value }]"
            @click="updateType(lt.value)"
          >
            <span class="type-icon">{{ lt.icon }}</span>
            <span class="type-label">{{ lt.label }}</span>
          </button>
        </div>
      </div>

      <!-- Reading time -->
      <div class="form-group">
        <label class="form-label">{{ $t('panel.manualEditor.lessonSettings.readingTime') }}</label>
        <div class="reading-time">
          <span class="time-value">{{ estimatedReadingTime }} min</span>
          <span class="time-hint">{{ $t('panel.manualEditor.lessonSettings.readingTimeAuto') }}</span>
        </div>
      </div>

      <!-- Order display -->
      <div class="form-group">
        <label class="form-label">{{ $t('panel.manualEditor.lessonSettings.position') || 'Position' }}</label>
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
  color: #999;
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
  color: #555;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.form-input {
  padding: 8px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.15s;
}

.form-input:focus {
  outline: none;
  border-color: #2196f3;
  box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.1);
}

/* Type selector */
.type-selector {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px;
}

.type-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  transition: all 0.15s;
}

.type-btn:hover {
  background: #f5f5f5;
}

.type-btn.active {
  background: #e3f2fd;
  border-color: #2196f3;
  color: #1565c0;
}

.type-icon {
  font-size: 16px;
}

.type-label {
  font-size: 13px;
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
  color: #333;
}

.time-hint {
  font-size: 11px;
  color: #999;
}

/* Position */
.position-display {
  font-size: 14px;
  color: #666;
  padding: 6px 0;
}

/* Notes */
.form-textarea {
  padding: 8px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 13px;
  resize: vertical;
  font-family: inherit;
  min-height: 80px;
  transition: border-color 0.15s;
}

.form-textarea:focus {
  outline: none;
  border-color: #2196f3;
  box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.1);
}
</style>
