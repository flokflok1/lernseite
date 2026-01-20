<template>
  <div
    class="enrolled-course-card bg-[var(--color-surface)] rounded-lg shadow-sm border border-[var(--color-border)] overflow-hidden cursor-pointer hover:shadow-md hover:border-primary-300 transition-all"
    @click="$emit('click')"
  >
    <!-- Thumbnail with Progress Overlay -->
    <div class="relative aspect-video bg-gradient-to-br from-primary-500 to-primary-700">
      <img
        v-if="enrollment.thumbnail_url"
        :src="enrollment.thumbnail_url"
        :alt="enrollment.title"
        class="w-full h-full object-cover"
      />
      <div v-else class="w-full h-full flex items-center justify-center">
        <span class="text-white text-5xl">📚</span>
      </div>

      <!-- Progress Overlay -->
      <div class="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent p-3">
        <div class="flex items-center justify-between text-white text-sm mb-1">
          <span>Fortschritt</span>
          <span class="font-semibold">{{ Math.round(enrollment.progress) }}%</span>
        </div>
        <div class="w-full bg-white/30 rounded-full h-2">
          <div
            class="bg-primary-400 h-2 rounded-full transition-all"
            :style="{ width: `${enrollment.progress}%` }"
          ></div>
        </div>
      </div>

      <!-- Completed Badge -->
      <div
        v-if="enrollment.is_completed"
        class="absolute top-2 right-2 px-2 py-1 text-xs font-medium rounded-full bg-green-500 text-white flex items-center gap-1"
      >
        ✅ Abgeschlossen
      </div>
    </div>

    <!-- Content -->
    <div class="p-4">
      <h3 class="font-semibold text-[var(--color-text-primary)] mb-1 line-clamp-2">
        {{ enrollment.title }}
      </h3>
      <p
        v-if="enrollment.description"
        class="text-sm text-[var(--color-text-secondary)] mb-3 line-clamp-2"
      >
        {{ enrollment.description }}
      </p>

      <!-- Stats -->
      <div class="flex items-center gap-3 text-xs text-[var(--color-text-tertiary)] mb-3">
        <span v-if="enrollment.lessons_completed !== undefined && enrollment.total_lessons" class="flex items-center gap-1">
          📝 {{ enrollment.lessons_completed }}/{{ enrollment.total_lessons }} Lektionen
        </span>
        <span v-if="enrollment.total_chapters" class="flex items-center gap-1">
          📖 {{ enrollment.total_chapters }} Kapitel
        </span>
      </div>

      <!-- Footer -->
      <div class="flex items-center justify-between pt-3 border-t border-[var(--color-border)]">
        <div class="text-xs text-[var(--color-text-secondary)]">
          <span v-if="enrollment.last_accessed_at">
            Zuletzt: {{ formatDate(enrollment.last_accessed_at) }}
          </span>
          <span v-else>
            Eingeschrieben: {{ formatDate(enrollment.enrolled_at) }}
          </span>
        </div>

        <!-- Continue Button -->
        <button
          class="px-3 py-1.5 text-xs font-medium rounded-lg transition-colors"
          :class="enrollment.is_completed
            ? 'bg-[var(--color-surface-secondary)] text-[var(--color-text-secondary)] hover:bg-[var(--color-border)]'
            : 'bg-primary-600 text-white hover:bg-primary-700'"
        >
          {{ enrollment.is_completed ? 'Wiederholen' : 'Fortsetzen' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { EnrolledCourse } from '@/infrastructure/api/courses.api'

// ============================================================================
// Props & Emits
// ============================================================================

interface Props {
  enrollment: EnrolledCourse
}

defineProps<Props>()

defineEmits<{
  click: []
}>()

// ============================================================================
// Methods
// ============================================================================

const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

  if (diffDays === 0) {
    return 'Heute'
  } else if (diffDays === 1) {
    return 'Gestern'
  } else if (diffDays < 7) {
    return `vor ${diffDays} Tagen`
  } else {
    return date.toLocaleDateString('de-DE', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    })
  }
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
