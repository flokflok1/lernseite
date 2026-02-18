<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAccessControl } from '@/application/composables/auth/useAccessControl'
import type { Course } from '@/infrastructure/api/clients/learning'

const { t } = useI18n()
const { canCreateCourse, canEditCourse, canDeleteCourse } = useAccessControl()

// Mock course data for demonstration
const mockCourses: Course[] = [
  {
    id: 'course-1',
    title: 'Python Basics',
    description: 'Learn Python fundamentals',
    creator_id: 'user-123',
    source: 'private',
    status: 'draft',
    is_published: false,
    created_at: new Date('2024-01-15'),
    updated_at: new Date('2024-01-20')
  },
  {
    id: 'course-2',
    title: 'Web Development',
    description: 'HTML, CSS, JavaScript',
    creator_id: 'user-123',
    source: 'community',
    status: 'approved',
    is_published: true,
    created_at: new Date('2024-01-10'),
    updated_at: new Date('2024-01-18')
  }
]

const courses = ref<Course[]>(mockCourses)
const filter = ref<'all' | 'draft' | 'published'>('all')
const searchQuery = ref('')

const filteredCourses = computed(() => {
  let result = courses.value

  if (filter.value !== 'all') {
    result = result.filter(course => {
      if (filter.value === 'draft') return !course.is_published
      if (filter.value === 'published') return course.is_published
      return true
    })
  }

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(
      course =>
        course.title.toLowerCase().includes(query) ||
        course.description.toLowerCase().includes(query)
    )
  }

  return result
})

const statusBadgeClass = (course: Course) => {
  if (!course.is_published) return 'badge--draft'
  if (course.status === 'approved') return 'badge--approved'
  if (course.status === 'review_pending') return 'badge--pending'
  if (course.status === 'rejected') return 'badge--rejected'
  return 'badge--published'
}

const statusLabel = (course: Course) => {
  if (!course.is_published) return t('course.status.draft')
  if (course.status === 'review_pending') return t('course.status.reviewPending')
  if (course.status === 'approved') return t('course.status.approved')
  if (course.status === 'rejected') return t('course.status.rejected')
  return t('course.status.published')
}

const handleCreateCourse = () => {
  // Navigate to course editor
  window.location.href = '/course-editor/new'
}

const handleEditCourse = (courseId: string) => {
  window.location.href = `/course-editor/${courseId}`
}

const handleDeleteCourse = (courseId: string) => {
  if (confirm(t('course.confirmDelete'))) {
    courses.value = courses.value.filter(c => c.id !== courseId)
  }
}
</script>

<template>
  <div class="user-courses">
    <!-- Header -->
    <div class="courses-header">
      <div class="courses-header__title">
        <h2>{{ $t('user.courses.myContent') }}</h2>
        <p>{{ $t('user.courses.subtitle') }}</p>
      </div>

      <button
        v-if="canCreateCourse('private')"
        class="btn btn--primary"
        @click="handleCreateCourse"
      >
        + {{ $t('course.createNew') }}
      </button>
    </div>

    <!-- Filters & Search -->
    <div class="filters">
      <div class="search-box">
        <input
          v-model="searchQuery"
          type="text"
          :placeholder="$t('common.search')"
          class="search-box__input"
        />
      </div>

      <div class="filter-buttons">
        <button
          :class="['filter-btn', { 'filter-btn--active': filter === 'all' }]"
          @click="filter = 'all'"
        >
          {{ $t('filter.all') }}
        </button>
        <button
          :class="['filter-btn', { 'filter-btn--active': filter === 'draft' }]"
          @click="filter = 'draft'"
        >
          {{ $t('filter.drafts') }}
        </button>
        <button
          :class="['filter-btn', { 'filter-btn--active': filter === 'published' }]"
          @click="filter = 'published'"
        >
          {{ $t('filter.published') }}
        </button>
      </div>
    </div>

    <!-- Courses List -->
    <div v-if="filteredCourses.length > 0" class="courses-list">
      <div v-for="course in filteredCourses" :key="course.id" class="course-card">
        <div class="course-card__header">
          <h3>{{ course.title }}</h3>
          <span :class="['badge', statusBadgeClass(course)]">
            {{ statusLabel(course) }}
          </span>
        </div>

        <p class="course-card__description">{{ course.description }}</p>

        <div class="course-card__meta">
          <span class="meta-item">
            <span class="meta-label">{{ $t('course.type') }}:</span>
            <span class="meta-value">{{ course.source }}</span>
          </span>
          <span class="meta-item">
            <span class="meta-label">{{ $t('course.updated') }}:</span>
            <span class="meta-value">{{
              course.updated_at ? new Date(course.updated_at).toLocaleDateString() : '-'
            }}</span>
          </span>
        </div>

        <div class="course-card__actions">
          <button
            v-if="canEditCourse(course)"
            class="btn btn--secondary"
            @click="handleEditCourse(course.id)"
          >
            {{ $t('common.edit') }}
          </button>

          <button
            v-if="canDeleteCourse(course)"
            class="btn btn--danger"
            @click="handleDeleteCourse(course.id)"
          >
            {{ $t('common.delete') }}
          </button>

          <a
            v-if="course.is_published"
            :href="`/courses/${course.id}`"
            class="btn btn--outline"
          >
            {{ $t('course.view') }}
          </a>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="empty-state">
      <div class="empty-state__icon">📚</div>
      <h3>{{ $t('course.noContent') }}</h3>
      <p>{{ $t('course.startByCreating') }}</p>
      <button
        v-if="canCreateCourse('private')"
        class="btn btn--primary"
        @click="handleCreateCourse"
      >
        {{ $t('course.createFirst') }}
      </button>
    </div>
  </div>
</template>

<style scoped lang="scss">
.user-courses {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.courses-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;

  &__title {
    h2 {
      font-size: 1.5rem;
      font-weight: 600;
      margin-bottom: 0.5rem;
      color: var(--color-text-primary);
    }

    p {
      color: var(--color-text-secondary);
      font-size: 0.95rem;
    }
  }

  @media (max-width: 768px) {
    flex-direction: column;
    align-items: stretch;
  }
}

.filters {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  align-items: center;
}

.search-box {
  flex: 1;
  min-width: 250px;

  &__input {
    width: 100%;
    padding: 0.75rem 1rem;
    border: 1px solid var(--color-border);
    border-radius: 0.5rem;
    font-size: 0.95rem;
    background: var(--color-background-primary);
    color: var(--color-text-primary);

    &:focus {
      outline: none;
      border-color: var(--color-primary);
      box-shadow: 0 0 0 3px rgba(var(--color-primary-rgb), 0.1);
    }

    &::placeholder {
      color: var(--color-text-tertiary);
    }
  }
}

.filter-buttons {
  display: flex;
  gap: 0.5rem;
}

.filter-btn {
  padding: 0.6rem 1.2rem;
  background: var(--color-background-secondary);
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  color: var(--color-text-secondary);
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease-in-out;

  &:hover {
    border-color: var(--color-primary);
    color: var(--color-primary);
  }

  &--active {
    background: var(--color-primary);
    border-color: var(--color-primary);
    color: white;
  }
}

.courses-list {
  display: grid;
  gap: 1.5rem;
}

.course-card {
  padding: 1.5rem;
  background: var(--color-background-secondary);
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  transition: all 0.2s ease-in-out;

  &:hover {
    border-color: var(--color-primary);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  }

  &__header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 1rem;
    margin-bottom: 0.75rem;

    h3 {
      font-size: 1.1rem;
      font-weight: 600;
      color: var(--color-text-primary);
      margin: 0;
    }
  }

  &__description {
    color: var(--color-text-secondary);
    font-size: 0.9rem;
    margin-bottom: 1rem;
    line-height: 1.5;
  }

  &__meta {
    display: flex;
    gap: 2rem;
    margin-bottom: 1rem;
    font-size: 0.85rem;
  }

  &__actions {
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
  }
}

.badge {
  display: inline-block;
  padding: 0.35rem 0.75rem;
  border-radius: 0.25rem;
  font-size: 0.8rem;
  font-weight: 600;
  white-space: nowrap;

  &--draft {
    background: var(--color-warning-light);
    color: var(--color-warning-dark);
  }

  &--pending {
    background: var(--color-info-light);
    color: var(--color-info-dark);
  }

  &--approved,
  &--published {
    background: var(--color-success-light);
    color: var(--color-success-dark);
  }

  &--rejected {
    background: var(--color-error-light);
    color: var(--color-error-dark);
  }
}

.meta-item {
  display: inline-flex;
  gap: 0.5rem;
}

.meta-label {
  color: var(--color-text-tertiary);
  font-weight: 500;
}

.meta-value {
  color: var(--color-text-secondary);
}

.btn {
  padding: 0.6rem 1.2rem;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;

  &--primary {
    background: var(--color-primary);
    color: white;

    &:hover {
      background: var(--color-primary-hover);
    }
  }

  &--secondary {
    background: var(--color-secondary);
    color: white;

    &:hover {
      background: var(--color-secondary-hover);
    }
  }

  &--danger {
    background: var(--color-error);
    color: white;

    &:hover {
      background: var(--color-error-hover);
    }
  }

  &--outline {
    background: transparent;
    border: 1px solid var(--color-primary);
    color: var(--color-primary);

    &:hover {
      background: var(--color-primary-light);
    }
  }
}

.empty-state {
  text-align: center;
  padding: 3rem 2rem;
  background: var(--color-background-secondary);
  border-radius: 0.5rem;
  border: 1px dashed var(--color-border);

  &__icon {
    font-size: 3rem;
    margin-bottom: 1rem;
  }

  h3 {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--color-text-primary);
    margin-bottom: 0.5rem;
  }

  p {
    color: var(--color-text-secondary);
    margin-bottom: 1.5rem;
  }
}
</style>
