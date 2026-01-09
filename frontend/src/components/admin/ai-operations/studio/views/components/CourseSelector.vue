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
        {{ selectedCourseTitle || $t('admin.aiStudio.selectCourse') }}
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
    <div v-if="dropdownOpen" class="dropdown-menu">
      <!-- Search Input -->
      <div class="search-section">
        <div class="search-input-wrapper">
          <svg class="search-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            v-model="searchQuery"
            type="text"
            :placeholder="$t('admin.aiStudio.searchCourse')"
            class="search-input"
            @click.stop
          />
        </div>
      </div>

      <!-- Category Filter -->
      <div v-if="allCategories.length > 0" class="category-filter">
        <button
          @click.stop="categoryPopupOpen = !categoryPopupOpen"
          class="category-toggle"
          :class="{ active: selectedCategoryFilter }"
        >
          <span class="category-label">
            <span>📁</span>
            <span>{{ categoryFilterLabel }}</span>
            <span class="category-count">({{ filteredCourses.length }})</span>
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
          <!-- All Categories -->
          <button
            @click.stop="selectedCategoryFilter = null"
            class="category-item"
            :class="{ active: selectedCategoryFilter === null }"
          >
            <span>{{ $t('admin.aiStudio.allCategories') }}</span>
            <span>{{ courses.length }}</span>
          </button>

          <!-- Individual Categories -->
          <button
            v-for="cat in allCategories"
            :key="cat"
            @click.stop="selectedCategoryFilter = cat"
            class="category-item"
            :class="{ active: selectedCategoryFilter === cat }"
          >
            <span>{{ cat }}</span>
            <span>{{ getCategoryCount(cat) }}</span>
          </button>

          <!-- Uncategorized -->
          <button
            @click.stop="selectedCategoryFilter = '__uncategorized__'"
            class="category-item uncategorized"
            :class="{ active: selectedCategoryFilter === '__uncategorized__' }"
          >
            <span>{{ $t('admin.aiStudio.noCategory') }}</span>
            <span>{{ getUncategorizedCount() }}</span>
          </button>
        </div>
      </div>

      <!-- New Course Button -->
      <button
        @click="$emit('create'); dropdownOpen = false"
        class="new-course-btn"
      >
        <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        {{ $t('admin.aiStudio.newCourse') }}
      </button>

      <!-- Recently Edited -->
      <div v-if="!searchQuery && recentCourses.length > 0" class="recent-section">
        <div class="section-header">
          {{ $t('admin.aiStudio.recentlyEdited') }}
        </div>
        <button
          v-for="course in recentCourses"
          :key="'recent-' + course.course_id"
          @click="handleSelectCourse(course.course_id)"
          class="course-item"
          :class="{ active: selectedCourseId === course.course_id }"
        >
          <span class="course-icon">🕐</span>
          <span class="course-title">{{ course.title }}</span>
        </button>
      </div>

      <!-- Courses Header -->
      <div class="courses-header">
        <span>{{ searchQuery ? $t('admin.aiStudio.searchResults') : $t('admin.aiStudio.allCourses') }}</span>
        <span>{{ filteredCourses.length }} / {{ courses.length }}</span>
      </div>

      <!-- Course List -->
      <div class="courses-list">
        <div v-if="filteredCourses.length === 0" class="empty-state">
          {{ searchQuery ? $t('admin.aiStudio.noCoursesFound') : $t('admin.aiStudio.noCoursesAvailable') }}
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
            @click="handleSelectCourse(course.course_id)"
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
            <span>{{ $t('admin.aiStudio.noCategory') }}</span>
            <span class="count">({{ coursesByCategory.uncategorized.length }})</span>
          </div>
          <button
            v-for="course in coursesByCategory.uncategorized"
            :key="course.course_id"
            @click="handleSelectCourse(course.course_id)"
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
  </div>
</template>

<script setup lang="ts">
/**
 * CourseSelector - Complex dropdown for course selection
 */
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import type { Course } from '../composables/useAiStudioState'

const { t } = useI18n()

// =============================================================================
// Props
// =============================================================================

interface Props {
  courses: Course[]
  selectedCourseId: string | null
}

const props = defineProps<Props>()

// =============================================================================
// Emits
// =============================================================================

const emit = defineEmits<{
  (e: 'select', courseId: string): void
  (e: 'create'): void
}>()

// =============================================================================
// State
// =============================================================================

const selectorRef = ref<HTMLElement | null>(null)
const dropdownOpen = ref(false)
const categoryPopupOpen = ref(false)
const searchQuery = ref('')
const selectedCategoryFilter = ref<string | null>(null)

// =============================================================================
// Computed
// =============================================================================

const selectedCourseTitle = computed(() => {
  if (!props.selectedCourseId) return ''
  const course = props.courses.find(c => c.course_id === props.selectedCourseId)
  return course?.title || ''
})

const filteredCourses = computed(() => {
  let filtered = props.courses

  // Apply search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(course =>
      course.title.toLowerCase().includes(query) ||
      course.description?.toLowerCase().includes(query)
    )
  }

  // Apply category filter
  if (selectedCategoryFilter.value) {
    if (selectedCategoryFilter.value === '__uncategorized__') {
      filtered = filtered.filter(course => !course.category_name)
    } else {
      filtered = filtered.filter(course =>
        course.category_name === selectedCategoryFilter.value
      )
    }
  }

  return filtered
})

const coursesByCategory = computed(() => {
  const groups: Record<string, Course[]> = {}
  const uncategorized: Course[] = []

  filteredCourses.value.forEach(course => {
    if (!course.category_name) {
      uncategorized.push(course)
    } else {
      if (!groups[course.category_name]) {
        groups[course.category_name] = []
      }
      groups[course.category_name].push(course)
    }
  })

  const sortedCategories = Object.keys(groups).sort()

  return { groups, uncategorized, sortedCategories }
})

const allCategories = computed(() => {
  const categories = new Set<string>()
  props.courses.forEach(course => {
    if (course.category_name) {
      categories.add(course.category_name)
    }
  })
  return Array.from(categories).sort()
})

const recentCourses = computed(() => {
  // TODO: Implement recent courses logic (last 5 edited)
  return []
})

const categoryFilterLabel = computed(() => {
  if (!selectedCategoryFilter.value) {
    return t('admin.aiStudio.allCategories')
  }
  if (selectedCategoryFilter.value === '__uncategorized__') {
    return t('admin.aiStudio.noCategory')
  }
  return selectedCategoryFilter.value
})

// =============================================================================
// Methods
// =============================================================================

function handleSelectCourse(courseId: string): void {
  emit('select', courseId)
  dropdownOpen.value = false
  categoryPopupOpen.value = false
  searchQuery.value = ''
}

function getCategoryCount(categoryName: string): number {
  return props.courses.filter(c => c.category_name === categoryName).length
}

function getUncategorizedCount(): number {
  return props.courses.filter(c => !c.category_name).length
}

function handleClickOutside(event: MouseEvent): void {
  if (selectorRef.value && !selectorRef.value.contains(event.target as Node)) {
    dropdownOpen.value = false
    categoryPopupOpen.value = false
  }
}

// =============================================================================
// Lifecycle
// =============================================================================

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.course-selector {
  position: relative;
}

/* Dropdown Button */
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

/* Dropdown Menu */
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

/* Search Section */
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

/* Category Filter */
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

/* New Course Button */
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

/* Recent Section */
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

/* Courses Header */
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

/* Courses List */
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
