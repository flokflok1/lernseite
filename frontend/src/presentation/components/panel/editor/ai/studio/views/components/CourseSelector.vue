<!--
  CourseSelector - Course dropdown with search, filter, and categories
-->

<template>
  <div class="course-selector" ref="selectorRef">
    <!-- Dropdown Button -->
    <button
      @click="dropdownOpen = !dropdownOpen"
      class="selector-button"
    >
      <span class="selector-text">
        {{ selectedCourseTitle || $t('panel.aiStudio.selectCourse') }}
      </span>
      <svg
        class="selector-chevron"
        :class="{ open: dropdownOpen }"
        fill="none" stroke="currentColor" viewBox="0 0 24 24"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </button>

    <!-- Dropdown Menu -->
    <CourseSelectorDropdown
      v-if="dropdownOpen"
      :search-query="searchQuery"
      :selected-course-id="selectedCourseId"
      :selected-category-filter="selectedCategoryFilter"
      :category-popup-open="categoryPopupOpen"
      :category-filter-label="categoryFilterLabel"
      :all-categories="allCategories"
      :filtered-courses-count="filteredCourses.length"
      :total-courses-count="courses.length"
      :uncategorized-count="getUncategorizedCount()"
      :category-counts="categoryCounts"
      :recent-courses="recentCourses"
      :courses-by-category="coursesByCategory"
      @update:search-query="searchQuery = $event"
      @toggle-category-popup="categoryPopupOpen = !categoryPopupOpen"
      @select-category="selectedCategoryFilter = $event"
      @create="$emit('create'); dropdownOpen = false"
      @select-course="handleSelectCourse"
    />
  </div>
</template>

<script setup lang="ts">
/**
 * CourseSelector - Complex dropdown for course selection.
 * Delegates dropdown content to CourseSelectorDropdown sub-component
 * and filtering/categorization logic to useCourseSelector composable.
 */
import { computed } from 'vue'
import type { Course } from '../composables/useAiStudioState'
import { useCourseSelector } from './composables/useCourseSelector'
import CourseSelectorDropdown from './CourseSelectorDropdown.vue'

interface Props {
  courses: Course[]
  selectedCourseId: string | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'select', courseId: string): void
  (e: 'create'): void
}>()

const {
  selectorRef,
  dropdownOpen,
  categoryPopupOpen,
  searchQuery,
  selectedCategoryFilter,
  selectedCourseTitle,
  filteredCourses,
  coursesByCategory,
  allCategories,
  recentCourses,
  categoryFilterLabel,
  handleSelectCourse: composableSelectCourse,
  getCategoryCount,
  getUncategorizedCount
} = useCourseSelector(
  () => props.courses,
  () => props.selectedCourseId
)

const categoryCounts = computed((): Record<string, number> => {
  const counts: Record<string, number> = {}
  for (const cat of allCategories.value) {
    counts[cat] = getCategoryCount(cat)
  }
  return counts
})

function handleSelectCourse(courseId: string): void {
  composableSelectCourse(courseId, emit)
}
</script>

<style scoped>
.course-selector {
  position: relative;
}

.selector-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  min-width: 280px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 0.5rem;
  color: white;
  font-size: 0.875rem;
  cursor: pointer;
  transition: background 0.15s;
}

.selector-button:hover {
  background: rgba(255, 255, 255, 0.2);
}

.selector-text {
  flex: 1;
  text-align: left;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.selector-chevron {
  width: 1rem;
  height: 1rem;
  transition: transform 0.15s;
}

.selector-chevron.open {
  transform: rotate(180deg);
}
</style>
