<!--
  CourseDetailsForm - Form fields for course title, description, category, etc.
-->

<template>
  <div class="details-section" :class="{ faded: isFaded }">
    <div class="section-header">
      <span>{{ $t('panel.aiStudio.step2CourseDetails') }}</span>
      <span v-if="aiAnalyzed" class="ai-badge">{{ $t('panel.aiStudio.aiSuggestion') }}</span>
    </div>

    <!-- Title -->
    <div class="form-field">
      <label class="field-label">{{ $t('panel.aiStudio.courseTitle') }} *</label>
      <input
        :value="modelValue.title"
        @input="emitUpdate('title', ($event.target as HTMLInputElement).value)"
        type="text"
        :placeholder="$t('panel.aiStudio.courseTitlePlaceholder')"
        class="field-input"
      />
    </div>

    <!-- Description -->
    <div class="form-field">
      <label class="field-label">{{ $t('panel.aiStudio.courseDescription') }}</label>
      <textarea
        :value="modelValue.description"
        @input="emitUpdate('description', ($event.target as HTMLTextAreaElement).value)"
        rows="3"
        :placeholder="$t('panel.aiStudio.courseDescriptionPlaceholder')"
        class="field-textarea"
      ></textarea>
    </div>

    <!-- Category & Profile -->
    <div class="form-row">
      <div class="form-field">
        <label class="field-label">{{ $t('panel.aiStudio.category') }}</label>
        <select
          :value="modelValue.categoryId"
          @change="emitUpdate('categoryId', parseSelectValue(($event.target as HTMLSelectElement).value))"
          class="field-select"
        >
          <option :value="null">{{ $t('panel.aiStudio.noCategory') }}</option>
          <option v-for="cat in availableCategories" :key="cat.category_id" :value="cat.category_id">
            {{ cat.name }}
          </option>
        </select>
      </div>
      <div class="form-field">
        <label class="field-label">{{ $t('panel.aiStudio.aiProfile') }}</label>
        <select
          :value="modelValue.profileKey"
          @change="emitUpdate('profileKey', ($event.target as HTMLSelectElement).value)"
          class="field-select"
        >
          <option v-for="profile in availableProfiles" :key="profile.key" :value="profile.key">
            {{ profile.name }}{{ profile.is_default ? ` (${$t('panel.aiStudio.default')})` : '' }}
          </option>
        </select>
      </div>
    </div>

    <!-- Language & Level -->
    <div class="form-row">
      <div class="form-field">
        <label class="field-label">{{ $t('panel.aiStudio.language') }}</label>
        <select
          :value="modelValue.language"
          @change="emitUpdate('language', ($event.target as HTMLSelectElement).value)"
          class="field-select"
        >
          <option value="de">{{ $t('panel.aiStudio.languageDe') }}</option>
          <option value="en">{{ $t('panel.aiStudio.languageEn') }}</option>
          <option value="es">{{ $t('panel.aiStudio.languageEs') }}</option>
          <option value="fr">{{ $t('panel.aiStudio.languageFr') }}</option>
        </select>
      </div>
      <div class="form-field">
        <label class="field-label">{{ $t('panel.aiStudio.level') }}</label>
        <select
          :value="modelValue.level"
          @change="emitUpdate('level', ($event.target as HTMLSelectElement).value)"
          class="field-select"
        >
          <option value="beginner">{{ $t('panel.aiStudio.levelBeginner') }}</option>
          <option value="intermediate">{{ $t('panel.aiStudio.levelIntermediate') }}</option>
          <option value="advanced">{{ $t('panel.aiStudio.levelAdvanced') }}</option>
        </select>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * CourseDetailsForm - Manages course metadata fields with v-model support.
 */
import type { Category, Profile } from '../composables/useCourseManagement'

// =============================================================================
// Types
// =============================================================================

export interface CourseFormData {
  title: string
  description: string
  language: string
  level: string
  categoryId: number | null
  profileKey: string
}

// =============================================================================
// Props
// =============================================================================

interface Props {
  modelValue: CourseFormData
  availableCategories: Category[]
  availableProfiles: Profile[]
  aiAnalyzed: boolean
  isFaded: boolean
}

const props = defineProps<Props>()

// =============================================================================
// Emits
// =============================================================================

const emit = defineEmits<{
  (e: 'update:modelValue', data: CourseFormData): void
}>()

// =============================================================================
// Methods
// =============================================================================

function emitUpdate(field: keyof CourseFormData, value: string | number | null): void {
  emit('update:modelValue', {
    ...props.modelValue,
    [field]: value
  })
}

function parseSelectValue(value: string): number | null {
  if (!value || value === 'null') return null
  return Number(value)
}
</script>

<style scoped>
.details-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  transition: opacity 0.15s;
}

.details-section.faded {
  opacity: 0.5;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text-primary);
}

.ai-badge {
  padding: 0.125rem 0.5rem;
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;
  border-radius: 0.25rem;
  font-size: 0.75rem;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.field-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text-secondary);
}

.field-input,
.field-textarea,
.field-select {
  padding: 0.5rem 0.75rem;
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  font-size: 0.875rem;
  color: var(--color-text-primary);
}

.field-input:focus,
.field-textarea:focus,
.field-select:focus {
  outline: none;
  border-color: var(--color-primary);
}

.field-textarea {
  resize: none;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}
</style>
