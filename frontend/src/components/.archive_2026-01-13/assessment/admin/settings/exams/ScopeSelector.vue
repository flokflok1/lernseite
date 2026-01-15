<!--
  ScopeSelector - Scope Level Selection
  Sub-component of SystemFeaturesTab
-->

<template>
  <div class="scope-selector">
    <button
      @click="$emit('update:modelValue', 'course')"
      class="scope-btn"
      :class="{ active: modelValue === 'course' }"
    >
      {{ $t('windows.aiEditorFeatures.scopeCourse') }}
    </button>
    <button
      v-if="chapter"
      @click="$emit('update:modelValue', 'chapter')"
      class="scope-btn"
      :class="{ active: modelValue === 'chapter' }"
    >
      {{ $t('windows.aiEditorFeatures.scopeChapter') }}: {{ chapter.title }}
    </button>
    <button
      v-if="lesson"
      @click="$emit('update:modelValue', 'lesson')"
      class="scope-btn"
      :class="{ active: modelValue === 'lesson' }"
    >
      {{ $t('windows.aiEditorFeatures.scopeLesson') }}: {{ lesson.title }}
    </button>
  </div>
</template>

<script setup lang="ts">
interface Chapter {
  chapter_id: string
  title: string
}

interface Lesson {
  lesson_id: string
  title: string
}

defineProps<{
  modelValue: 'course' | 'chapter' | 'lesson'
  chapter?: Chapter | null
  lesson?: Lesson | null
}>()

defineEmits<{
  (e: 'update:modelValue', value: 'course' | 'chapter' | 'lesson'): void
}>()
</script>

<style scoped>
.scope-selector {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  padding: 0.5rem;
  background: var(--color-surface);
  border-radius: 0.75rem;
  border: 1px solid var(--color-border);
}

.scope-btn {
  flex: 1;
  padding: 0.75rem 1rem;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.scope-btn:hover {
  background: var(--color-surface-secondary);
}

.scope-btn.active {
  background: var(--color-primary-subtle);
  border-color: var(--color-primary);
  color: var(--color-primary);
  font-weight: 600;
}
</style>
