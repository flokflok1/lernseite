<template>
  <div
    class="course-card bg-[var(--color-surface)] rounded-lg shadow-sm border border-[var(--color-border)] overflow-hidden cursor-pointer hover:shadow-md hover:border-primary-300 transition-all"
    @click="$emit('click')"
  >
    <!-- Thumbnail -->
    <div class="relative aspect-video bg-gradient-to-br from-primary-500 to-primary-700">
      <img
        v-if="course.thumbnail_url"
        :src="course.thumbnail_url"
        :alt="course.title"
        class="w-full h-full object-cover"
      />
      <div v-else class="w-full h-full flex items-center justify-center">
        <span class="text-white text-5xl">📚</span>
      </div>

      <!-- Level Badge -->
      <span
        class="absolute top-2 left-2 px-2 py-1 text-xs font-medium rounded-full bg-white/90 text-primary-700"
      >
        {{ levelLabel }}
      </span>

      <!-- Edit Button (for creators) -->
      <button
        v-if="showEdit"
        class="absolute top-2 right-2 p-2 rounded-full bg-white/90 hover:bg-white text-gray-700 hover:text-primary-600 transition-colors"
        @click.stop="$emit('edit')"
      >
        ✏️
      </button>
    </div>

    <!-- Content -->
    <div class="p-4">
      <h3 class="font-semibold text-[var(--color-text-primary)] mb-1 line-clamp-2">
        {{ course.title }}
      </h3>
      <p
        v-if="course.description"
        class="text-sm text-[var(--color-text-secondary)] mb-3 line-clamp-2"
      >
        {{ course.description }}
      </p>

      <!-- Meta Info -->
      <div class="flex items-center gap-3 text-xs text-[var(--color-text-tertiary)] mb-3">
        <span v-if="course.total_chapters" class="flex items-center gap-1">
          📖 {{ course.total_chapters }} Kapitel
        </span>
        <span v-if="course.total_lessons" class="flex items-center gap-1">
          📝 {{ course.total_lessons }} Lektionen
        </span>
        <span v-if="course.total_duration_minutes" class="flex items-center gap-1">
          ⏱️ {{ formatDuration(course.total_duration_minutes) }}
        </span>
      </div>

      <!-- Footer -->
      <div class="flex items-center justify-between pt-3 border-t border-[var(--color-border)]">
        <div class="flex items-center gap-2">
          <span v-if="course.creator_name" class="text-xs text-[var(--color-text-secondary)]">
            von {{ course.creator_name }}
          </span>
        </div>
        <div class="flex items-center gap-2">
          <span
            v-if="course.enrollment_count !== undefined"
            class="text-xs text-[var(--color-text-tertiary)]"
          >
            👥 {{ course.enrollment_count }}
          </span>
          <span
            v-if="course.average_rating"
            class="text-xs text-yellow-600 flex items-center gap-0.5"
          >
            ⭐ {{ course.average_rating.toFixed(1) }}
          </span>
        </div>
      </div>

      <!-- Price / Status -->
      <div class="mt-3 flex items-center justify-between">
        <span
          v-if="course.price === 0"
          class="px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-700"
        >
          Kostenlos
        </span>
        <span
          v-else-if="course.price"
          class="text-sm font-semibold text-[var(--color-text-primary)]"
        >
          {{ formatPrice(course.price) }}
        </span>

        <span
          v-if="!course.is_published"
          class="px-2 py-1 text-xs font-medium rounded-full bg-yellow-100 text-yellow-700"
        >
          Entwurf
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { CourseListItem } from '@/infrastructure/api/clients/content'

// ============================================================================
// Props & Emits
// ============================================================================

interface Props {
  course: CourseListItem
  showEdit?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showEdit: false
})

defineEmits<{
  click: []
  edit: []
}>()

// ============================================================================
// Computed
// ============================================================================

const levelLabel = computed(() => {
  const levelMap: Record<string, string> = {
    beginner: 'Anfänger',
    intermediate: 'Fortgeschritten',
    advanced: 'Experte',
    expert: 'Meister'
  }
  return levelMap[props.course.level] || props.course.level
})

// ============================================================================
// Methods
// ============================================================================

const formatDuration = (minutes: number): string => {
  if (minutes < 60) {
    return `${minutes} Min.`
  }
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`
}

const formatPrice = (price: number): string => {
  return new Intl.NumberFormat('de-DE', {
    style: 'currency',
    currency: 'EUR'
  }).format(price)
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
