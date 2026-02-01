<template>
  <div class="course-details-sections">
    <!-- Course Description -->
    <div v-if="description" class="mb-4">
      <details class="details-card">
        <summary class="cursor-pointer font-semibold flex items-center gap-2">
          <svg viewBox="0 0 24 24" fill="currentColor" class="w-5 h-5">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/>
          </svg>
          {{ $t('courses.description') }}
        </summary>
        <p class="mt-4 opacity-70 whitespace-pre-line">
          {{ description }}
        </p>
      </details>
    </div>

    <!-- Learning Goals -->
    <div v-if="learningGoals && learningGoals.length > 0">
      <details class="details-card">
        <summary class="cursor-pointer font-semibold flex items-center gap-2">
          <svg viewBox="0 0 24 24" fill="currentColor" class="w-5 h-5">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
          </svg>
          {{ $t('courses.learning_goals') }}
        </summary>
        <ul class="mt-4 list-disc list-inside space-y-2 opacity-70">
          <li v-for="(goal, idx) in learningGoals" :key="idx">
            {{ goal }}
          </li>
        </ul>
      </details>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * CourseDetailsSections Component
 * ===============================
 * Course description and learning goals display
 */

interface Props {
  description?: string | null
  learningGoals?: string[] | null
}

defineProps<Props>()
</script>

<style scoped>
.details-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 1.25rem;
  transition: all 0.3s ease;
}

.details-card:hover {
  background: var(--color-surface-hover);
}

.details-card summary {
  color: var(--color-text-primary);
  list-style: none;
  transition: opacity 0.3s ease;
}

.details-card summary::-webkit-details-marker {
  display: none;
}

.details-card summary:hover {
  opacity: 0.8;
}

.details-card[open] summary {
  margin-bottom: 0.5rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--color-border);
}

.details-card p,
.details-card ul {
  color: var(--color-text-secondary);
}

.details-card ul li {
  padding-left: 0.5rem;
}
</style>
