<!--
  Course Chapters Tab

  Displays a list of chapters for a course with options to
  create, edit, and delete chapters.
-->

<template>
  <div class="p-6">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-semibold text-[var(--color-text-primary)]">
        Kapitel ({{ chapters.length }})
      </h3>
      <button
        @click="$emit('create-chapter')"
        class="px-3 py-1.5 bg-[var(--color-primary)] text-white text-sm rounded-lg hover:bg-[var(--color-primary-hover)]"
      >
        + Neues Kapitel
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-[var(--color-primary)] mx-auto"></div>
    </div>

    <!-- Empty State -->
    <div v-else-if="chapters.length === 0" class="text-center py-8">
      <p class="text-[var(--color-text-secondary)]">Noch keine Kapitel vorhanden</p>
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
              <span>{{ chapter.lesson_count || 0 }} Lektionen</span>
              <span>{{ chapter.duration_minutes }} Min.</span>
            </div>
          </div>
          <div class="flex gap-2">
            <button
              @click="$emit('edit-chapter', chapter)"
              class="px-2 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Bearbeiten
            </button>
            <button
              @click="$emit('delete-chapter', chapter.chapter_id)"
              class="px-2 py-1 text-xs bg-red-600 text-white rounded hover:bg-red-700"
            >
              Loeschen
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Chapter {
  chapter_id: string
  title: string
  description?: string
  order_index: number
  lesson_count?: number
  duration_minutes?: number
}

interface Props {
  chapters: Chapter[]
  loading: boolean
}

defineProps<Props>()

defineEmits<{
  (e: 'create-chapter'): void
  (e: 'edit-chapter', chapter: Chapter): void
  (e: 'delete-chapter', chapterId: string): void
}>()
</script>
