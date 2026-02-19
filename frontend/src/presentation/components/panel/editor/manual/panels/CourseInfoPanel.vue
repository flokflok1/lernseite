/**
 * CourseInfoPanel.vue
 *
 * Course metadata form — title, description, category, difficulty,
 * language, duration, tags. Mode-aware fields for visibility/publish.
 * Replaces the shared CourseMetaForm reference.
 */

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useCourseEditorStore } from '@/application/stores/modules/content/courseEditor.store'
import type { EditorModeConfig } from '../types'

interface Props {
  modeConfig: EditorModeConfig
}

defineProps<Props>()

const { t } = useI18n()
const store = useCourseEditorStore()

const course = computed(() => store.currentCourse)

// Local form state (synced from store)
const title = ref('')
const description = ref('')
const level = ref<'beginner' | 'intermediate' | 'advanced'>('beginner')
const language = ref('de')
const estimatedDuration = ref(0)
const visibility = ref<'public' | 'private' | 'unlisted'>('private')
const tags = ref<string[]>([])
const newTag = ref('')

// Sync from store when course changes
watch(course, (c) => {
  if (c) {
    title.value = c.title || ''
    description.value = c.description || ''
    level.value = (c.level as 'beginner' | 'intermediate' | 'advanced') || 'beginner'
    language.value = c.language || 'de'
    estimatedDuration.value = c.estimated_duration || 0
    visibility.value = (c.visibility as 'public' | 'private' | 'unlisted') || 'private'
    tags.value = Array.isArray(c.tags) ? [...c.tags] : []
  }
}, { immediate: true })

const descriptionLength = computed(() => description.value.length)

const saveField = (field: string, value: unknown): void => {
  store.updateCourseMeta({ [field]: value })
}

const handleTitleBlur = (): void => {
  if (title.value.trim()) {
    saveField('title', title.value.trim())
  }
}

const handleDescriptionBlur = (): void => {
  saveField('description', description.value)
}

const handleLevelChange = (): void => {
  saveField('level', level.value)
}

const handleLanguageChange = (): void => {
  saveField('language', language.value)
}

const handleDurationBlur = (): void => {
  saveField('estimated_duration', estimatedDuration.value)
}

const handleVisibilityChange = (): void => {
  saveField('visibility', visibility.value)
}

const addTag = (): void => {
  const tag = newTag.value.trim()
  if (tag && !tags.value.includes(tag)) {
    tags.value.push(tag)
    saveField('tags', [...tags.value])
  }
  newTag.value = ''
}

const removeTag = (index: number): void => {
  tags.value.splice(index, 1)
  saveField('tags', [...tags.value])
}

const handleTagKeydown = (e: KeyboardEvent): void => {
  if (e.key === 'Enter') {
    e.preventDefault()
    addTag()
  }
}

const languages = [
  { code: 'de', label: 'Deutsch' },
  { code: 'en', label: 'English' },
  { code: 'pl', label: 'Polski' },
  { code: 'fr', label: 'Fran\u00e7ais' },
  { code: 'es', label: 'Espa\u00f1ol' },
  { code: 'tr', label: 'T\u00fcrk\u00e7e' },
]
</script>

<template>
  <div class="course-info-panel">
    <h3 class="panel-title">{{ $t('panel.manualEditor.courseInfo.title') }}</h3>

    <div v-if="!course" class="empty-state">
      <p>{{ $t('panel.manualEditor.content.noLessonSelected') }}</p>
    </div>

    <div v-else class="form-fields">
      <!-- Title -->
      <div class="field">
        <label>{{ $t('panel.manualEditor.courseInfo.courseName') }} *</label>
        <input
          v-model="title"
          type="text"
          @blur="handleTitleBlur"
        />
      </div>

      <!-- Description -->
      <div class="field">
        <label>{{ $t('panel.manualEditor.courseInfo.description') }}</label>
        <textarea
          v-model="description"
          rows="4"
          maxlength="500"
          @blur="handleDescriptionBlur"
        />
        <span class="char-count" :class="{ warn: descriptionLength > 450 }">
          {{ descriptionLength }}/500
        </span>
      </div>

      <!-- Difficulty -->
      <div class="field">
        <label>{{ $t('panel.manualEditor.courseInfo.difficulty') }}</label>
        <div class="radio-group">
          <label class="radio-label">
            <input type="radio" v-model="level" value="beginner" @change="handleLevelChange" />
            {{ $t('panel.manualEditor.levels.beginner') }}
          </label>
          <label class="radio-label">
            <input type="radio" v-model="level" value="intermediate" @change="handleLevelChange" />
            {{ $t('panel.manualEditor.levels.intermediate') }}
          </label>
          <label class="radio-label">
            <input type="radio" v-model="level" value="advanced" @change="handleLevelChange" />
            {{ $t('panel.manualEditor.levels.advanced') }}
          </label>
        </div>
      </div>

      <!-- Language -->
      <div class="field">
        <label>{{ $t('panel.manualEditor.courseInfo.language') }}</label>
        <select v-model="language" @change="handleLanguageChange">
          <option v-for="lang in languages" :key="lang.code" :value="lang.code">
            {{ lang.label }}
          </option>
        </select>
      </div>

      <!-- Duration -->
      <div class="field">
        <label>{{ $t('panel.manualEditor.courseInfo.duration') }}</label>
        <input
          v-model.number="estimatedDuration"
          type="number"
          min="0"
          @blur="handleDurationBlur"
        />
      </div>

      <!-- Tags -->
      <div class="field">
        <label>{{ $t('panel.manualEditor.courseInfo.tags') }}</label>
        <div class="tags-container">
          <span v-for="(tag, i) in tags" :key="i" class="tag">
            {{ tag }}
            <button class="tag-remove" @click="removeTag(i)">&times;</button>
          </span>
          <input
            v-model="newTag"
            type="text"
            class="tag-input"
            :placeholder="$t('panel.manualEditor.courseInfo.tagsHint')"
            @keydown="handleTagKeydown"
          />
        </div>
      </div>

      <!-- Visibility (expert mode only) -->
      <div v-if="modeConfig.showCourseVisibility" class="field">
        <label>{{ $t('panel.manualEditor.courseInfo.visibility') }}</label>
        <select v-model="visibility" @change="handleVisibilityChange">
          <option value="public">{{ $t('panel.manualEditor.courseInfo.visibilityPublic') }}</option>
          <option value="private">{{ $t('panel.manualEditor.courseInfo.visibilityPrivate') }}</option>
          <option value="unlisted">{{ $t('panel.manualEditor.courseInfo.visibilityUnlisted') }}</option>
        </select>
      </div>
    </div>
  </div>
</template>

<style scoped>
.course-info-panel {
  padding: 16px;
  overflow-y: auto;
  height: 100%;
}

.panel-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 16px;
}

.empty-state {
  color: #999;
  text-align: center;
  padding: 24px;
}

.form-fields {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.field > label {
  font-size: 12px;
  font-weight: 600;
  color: #555;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.field input[type="text"],
.field input[type="number"],
.field input[type="url"],
.field textarea,
.field select {
  padding: 8px 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 13px;
  transition: border-color 0.2s;
}

.field input:focus,
.field textarea:focus,
.field select:focus {
  border-color: #2196f3;
  outline: none;
}

.field textarea {
  resize: vertical;
  min-height: 80px;
}

.char-count {
  font-size: 11px;
  color: #999;
  text-align: right;
}

.char-count.warn {
  color: #ff9800;
}

.radio-group {
  display: flex;
  gap: 16px;
}

.radio-label {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  cursor: pointer;
}

/* Tags */
.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  padding: 6px;
  border: 1px solid #ddd;
  border-radius: 6px;
  min-height: 36px;
  align-items: center;
}

.tag {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  background: #e3f2fd;
  color: #1565c0;
  border-radius: 12px;
  font-size: 12px;
}

.tag-remove {
  border: none;
  background: none;
  cursor: pointer;
  color: #1565c0;
  font-size: 14px;
  padding: 0;
  line-height: 1;
}

.tag-input {
  border: none !important;
  outline: none;
  flex: 1;
  min-width: 100px;
  font-size: 13px;
  padding: 2px 4px !important;
}
</style>
