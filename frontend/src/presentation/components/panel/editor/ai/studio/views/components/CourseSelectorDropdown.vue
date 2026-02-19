<!--
  CourseSelectorDropdown - Dropdown menu content for course selection
  Renders search, category filter, course list, and new course button.
-->

<template>
  <div class="dropdown-menu">
    <!-- Search Input -->
    <div class="search-section">
      <div class="search-input-wrapper">
        <svg class="search-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <input
          :value="searchQuery"
          @input="$emit('update:searchQuery', ($event.target as HTMLInputElement).value)"
          type="text"
          :placeholder="$t('panel.aiStudio.searchCourse')"
          class="search-input"
          @click.stop
        />
      </div>
    </div>

    <!-- Category Filter -->
    <div v-if="allCategories.length > 0" class="category-filter">
      <button
        @click.stop="$emit('toggle-category-popup')"
        class="category-toggle"
        :class="{ active: selectedCategoryFilter }"
      >
        <span class="category-label">
          <span>📁</span>
          <span>{{ categoryFilterLabel }}</span>
          <span class="category-count">({{ filteredCoursesCount }})</span>
        </span>
        <svg
          class="category-chevron"
          :class="{ open: categoryPopupOpen }"
          fill="none" stroke="currentColor" viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      <!-- Category List -->
      <div v-if="categoryPopupOpen" class="category-list">
        <button
          @click.stop="$emit('select-category', null)"
          class="category-item"
          :class="{ active: selectedCategoryFilter === null }"
        >
          <span>{{ $t('panel.aiStudio.allCategories') }}</span>
          <span>{{ totalCoursesCount }}</span>
        </button>

        <button
          v-for="cat in allCategories"
          :key="cat"
          @click.stop="$emit('select-category', cat)"
          class="category-item"
          :class="{ active: selectedCategoryFilter === cat }"
        >
          <span>{{ cat }}</span>
          <span>{{ categoryCounts[cat] || 0 }}</span>
        </button>

        <button
          @click.stop="$emit('select-category', '__uncategorized__')"
          class="category-item uncategorized"
          :class="{ active: selectedCategoryFilter === '__uncategorized__' }"
        >
          <span>{{ $t('panel.aiStudio.noCategory') }}</span>
          <span>{{ uncategorizedCount }}</span>
        </button>
      </div>
    </div>

    <!-- New Course Button -->
    <button
      @click="$emit('create')"
      class="new-course-btn"
    >
      <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
      </svg>
      {{ $t('panel.aiStudio.newCourse') }}
    </button>

    <!-- Recently Edited -->
    <div v-if="!searchQuery && recentCourses.length > 0" class="recent-section">
      <div class="section-header">
        {{ $t('panel.aiStudio.recentlyEdited') }}
      </div>
      <button
        v-for="course in recentCourses"
        :key="'recent-' + course.course_id"
        @click="$emit('select-course', course.course_id)"
        class="course-item"
        :class="{ active: selectedCourseId === course.course_id }"
      >
        <span class="course-icon">🕐</span>
        <span class="course-title">{{ course.title }}</span>
      </button>
    </div>

    <!-- Courses Header -->
    <div class="courses-header">
      <span>{{ searchQuery ? $t('panel.aiStudio.searchResults') : $t('panel.aiStudio.allCourses') }}</span>
      <span>{{ filteredCoursesCount }} / {{ totalCoursesCount }}</span>
    </div>

    <!-- Course List -->
    <div class="courses-list">
      <div v-if="coursesByCategory.sortedCategories.length === 0 && coursesByCategory.uncategorized.length === 0" class="empty-state">
        {{ searchQuery ? $t('panel.aiStudio.noCoursesFound') : $t('panel.aiStudio.noCoursesAvailable') }}
      </div>

      <!-- Categorized Courses -->
      <template v-for="categoryName in coursesByCategory.sortedCategories" :key="categoryName">
        <div class="category-header">
          <span>📁</span>
          <span>{{ categoryName }}</span>
          <span class="count">({{ coursesByCategory.groups[categoryName].length }})</span>
        </div>
        <button
          v-for="course in coursesByCategory.groups[categoryName]"
          :key="course.course_id"
          @click="$emit('select-course', course.course_id)"
          class="course-item"
          :class="{ active: selectedCourseId === course.course_id }"
        >
          <span class="course-icon">📚</span>
          <span class="course-title">{{ course.title }}</span>
          <svg v-if="selectedCourseId === course.course_id" class="check-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
        </button>
      </template>

      <!-- Uncategorized Courses -->
      <template v-if="coursesByCategory.uncategorized.length > 0">
        <div v-if="coursesByCategory.sortedCategories.length > 0" class="category-header uncategorized">
          <span>📦</span>
          <span>{{ $t('panel.aiStudio.noCategory') }}</span>
          <span class="count">({{ coursesByCategory.uncategorized.length }})</span>
        </div>
        <button
          v-for="course in coursesByCategory.uncategorized"
          :key="course.course_id"
          @click="$emit('select-course', course.course_id)"
          class="course-item"
          :class="{ active: selectedCourseId === course.course_id }"
        >
          <span class="course-icon">📚</span>
          <span class="course-title">{{ course.title }}</span>
          <svg v-if="selectedCourseId === course.course_id" class="check-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
        </button>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * CourseSelectorDropdown - Inner dropdown content for CourseSelector.
 * Receives all data as props, emits user actions to parent.
 */
import type { Course } from '../../composables/useAiStudioState'

interface Props {
  searchQuery: string
  selectedCourseId: string | null
  selectedCategoryFilter: string | null
  categoryPopupOpen: boolean
  categoryFilterLabel: string
  allCategories: string[]
  filteredCoursesCount: number
  totalCoursesCount: number
  uncategorizedCount: number
  categoryCounts: Record<string, number>
  recentCourses: Course[]
  coursesByCategory: {
    groups: Record<string, Course[]>
    uncategorized: Course[]
    sortedCategories: string[]
  }
}

defineProps<Props>()

defineEmits<{
  'update:searchQuery': [value: string]
  'toggle-category-popup': []
  'select-category': [category: string | null]
  'create': []
  'select-course': [courseId: string]
}>()
</script>

<style scoped>
.dropdown-menu {
  position: absolute;
  top: calc(100% + 0.25rem);
  right: 0;
  min-width: 320px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
  z-index: 50;
  overflow: hidden;
}

.search-section {
  padding: 0.5rem;
  border-bottom: 1px solid var(--color-border);
}

.search-input-wrapper {
  position: relative;
}

.search-icon {
  position: absolute;
  left: 0.625rem;
  top: 50%;
  transform: translateY(-50%);
  width: 1rem;
  height: 1rem;
  color: var(--color-text-tertiary);
}

.search-input {
  width: 100%;
  padding: 0.5rem 0.75rem 0.5rem 2rem;
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  font-size: 0.875rem;
  color: var(--color-text-primary);
}

.search-input:focus {
  outline: none;
  border-color: var(--color-primary);
}

.category-filter {
  border-bottom: 1px solid var(--color-border);
}

.category-toggle {
  width: 100%;
  padding: 0.5rem 0.75rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: none;
  border: none;
  font-size: 0.75rem;
  font-weight: 500;
  text-align: left;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: background 0.15s;
}

.category-toggle:hover {
  background: var(--color-surface-secondary);
}

.category-toggle.active {
  color: var(--color-primary);
  background: var(--color-primary-subtle);
}

.category-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.category-count {
  color: var(--color-text-tertiary);
}

.category-chevron {
  width: 1rem;
  height: 1rem;
  transition: transform 0.15s;
}

.category-chevron.open {
  transform: rotate(180deg);
}

.category-list {
  max-height: 150px;
  overflow-y: auto;
  background: var(--color-bg);
  border-top: 1px solid var(--color-border);
}

.category-item {
  width: 100%;
  padding: 0.375rem 1rem;
  display: flex;
  justify-content: space-between;
  background: none;
  border: none;
  font-size: 0.75rem;
  text-align: left;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: background 0.15s;
}

.category-item:hover {
  background: var(--color-surface-secondary);
}

.category-item.active {
  color: var(--color-primary);
  font-weight: 500;
}

.category-item.uncategorized {
  color: var(--color-text-tertiary);
}

.new-course-btn {
  width: 100%;
  padding: 0.625rem 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: linear-gradient(to right, rgba(139, 92, 246, 0.1), rgba(168, 85, 247, 0.1));
  border: none;
  border-bottom: 1px solid var(--color-border);
  font-size: 0.875rem;
  font-weight: 500;
  text-align: left;
  color: var(--color-primary);
  cursor: pointer;
  transition: background 0.15s;
}

.new-course-btn:hover {
  background: linear-gradient(to right, rgba(139, 92, 246, 0.2), rgba(168, 85, 247, 0.2));
}

.btn-icon {
  width: 1rem;
  height: 1rem;
}

.recent-section {
  border-bottom: 1px solid var(--color-border);
}

.section-header {
  padding: 0.25rem 0.75rem;
  font-size: 0.625rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-tertiary);
  background: var(--color-surface-secondary);
}

.courses-header {
  padding: 0.25rem 0.75rem;
  display: flex;
  justify-content: space-between;
  font-size: 0.625rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-tertiary);
  background: var(--color-surface-secondary);
}

.courses-list {
  max-height: 280px;
  overflow-y: auto;
}

.empty-state {
  padding: 1rem 0.75rem;
  text-align: center;
  font-size: 0.875rem;
  color: var(--color-text-tertiary);
}

.category-header {
  padding: 0.5rem 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-primary);
  background: rgba(139, 92, 246, 0.05);
  position: sticky;
  top: 0;
}

.category-header.uncategorized {
  color: var(--color-text-tertiary);
  background: var(--color-surface-secondary);
}

.category-header .count {
  font-size: 0.625rem;
  font-weight: normal;
  color: var(--color-text-tertiary);
}

.course-item {
  width: 100%;
  padding: 0.5rem 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: none;
  border: none;
  font-size: 0.875rem;
  text-align: left;
  color: var(--color-text-primary);
  cursor: pointer;
  transition: background 0.15s;
}

.course-item:hover {
  background: var(--color-surface-secondary);
}

.course-item.active {
  background: var(--color-primary-subtle);
  color: var(--color-primary);
}

.course-icon {
  width: 1.25rem;
  height: 1.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.25rem;
  background: var(--color-surface-secondary);
  font-size: 0.75rem;
}

.course-title {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.check-icon {
  width: 1rem;
  height: 1rem;
  color: var(--color-primary);
}
</style>
