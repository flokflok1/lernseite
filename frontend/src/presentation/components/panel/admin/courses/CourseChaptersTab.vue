<!--
  CourseChaptersTab - Chapter management tab for course editor

  Displays chapter list with edit/delete actions and add new chapter button.
-->

<template>
  <div class="p-6">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-semibold text-[var(--color-text-primary)]">
        {{ $t('courseEditor.chapters.title', { count: chapters.length }) }}
      </h3>
      <button
        @click="$emit('add-chapter')"
        class="px-3 py-1.5 bg-[var(--color-primary)] text-white text-sm rounded-lg hover:bg-[var(--color-primary-hover)]"
      >
        {{ $t('courseEditor.chapters.addNew') }}
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loadingChapters" class="text-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-[var(--color-primary)] mx-auto"></div>
    </div>

    <!-- Empty State -->
    <div v-else-if="chapters.length === 0" class="text-center py-8">
      <p class="text-[var(--color-text-secondary)]">{{ $t('courseEditor.chapters.noChapters') }}</p>
    </div>

    <!-- Chapter List -->
    <div v-else class="space-y-3">
      <div
        v-for="chapter in chapters"
        :key="chapter.chapter_id"
        class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-4 hover:border-[var(--color-primary)] transition-colors"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <h4 class="font-semibold text-[var(--color-text-primary)] mb-1">
              {{ chapter.order_index }}. {{ chapter.title }}
            </h4>
            <p v-if="chapter.description" class="text-sm text-[var(--color-text-secondary)] mb-2">
              {{ chapter.description }}
            </p>
            <div class="flex gap-4 text-xs text-[var(--color-text-secondary)]">
              <span>{{ $t('courseEditor.chapters.lessons', { count: chapter.lesson_count || 0 }) }}</span>
              <span>{{ $t('courseEditor.chapters.duration', { minutes: chapter.duration_minutes }) }}</span>
            </div>
          </div>
          <div class="flex gap-2">
            <button
              @click="$emit('edit-chapter', chapter)"
              class="px-2 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              {{ $t('courseEditor.chapters.edit') }}
            </button>
            <button
              @click="$emit('delete-chapter', chapter.chapter_id)"
              class="px-2 py-1 text-xs bg-red-600 text-white rounded hover:bg-red-700"
            >
              {{ $t('courseEditor.chapters.delete') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { AdminChapter } from './composables/useCourseEditor'

interface Props {
  chapters: AdminChapter[]
  loadingChapters: boolean
}

defineProps<Props>()

defineEmits<{
  (e: 'add-chapter'): void
  (e: 'edit-chapter', chapter: AdminChapter): void
  (e: 'delete-chapter', chapterId: string): void
}>()
</script>
