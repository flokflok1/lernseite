<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { Course } from '@/infrastructure/api/clients/learning'

const { t } = useI18n()

// Mock data
const mockCourses: Course[] = [
  {
    id: 'course-1',
    title: 'Python Advanced',
    description: 'Advanced Python programming',
    creator_id: 'user-123',
    source: 'community',
    status: 'approved',
    is_published: true,
    created_at: new Date('2024-01-20'),
    updated_at: new Date('2024-01-26')
  },
  {
    id: 'course-2',
    title: 'Web Dev Masterclass',
    description: 'Complete web development',
    creator_id: 'user-456',
    source: 'community',
    status: 'review_pending',
    is_published: false,
    created_at: new Date('2024-01-25'),
    updated_at: new Date('2024-01-26')
  },
  {
    id: 'course-3',
    title: 'Database Design',
    description: 'SQL and database design',
    creator_id: 'user-789',
    source: 'community',
    status: 'rejected',
    is_published: false,
    created_at: new Date('2024-01-18'),
    updated_at: new Date('2024-01-24')
  }
]

const courses = ref<Course[]>(mockCourses)
const filterStatus = ref<'all' | 'draft' | 'review' | 'approved' | 'rejected'>('all')
const searchQuery = ref('')
const sortBy = ref<'created' | 'updated' | 'title'>('updated')

const filteredCourses = computed(() => {
  let result = courses.value

  // Filter by status
  if (filterStatus.value !== 'all') {
    result = result.filter(course => {
      switch (filterStatus.value) {
        case 'draft':
          return !course.is_published
        case 'review':
          return course.status === 'review_pending'
        case 'approved':
          return course.status === 'approved' && course.is_published
        case 'rejected':
          return course.status === 'rejected'
        default:
          return true
      }
    })
  }

  // Search
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(
      course =>
        course.title.toLowerCase().includes(query) ||
        course.description.toLowerCase().includes(query)
    )
  }

  // Sort
  result.sort((a, b) => {
    switch (sortBy.value) {
      case 'title':
        return a.title.localeCompare(b.title)
      case 'created':
        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      case 'updated':
      default:
        return new Date(b.updated_at || 0).getTime() - new Date(a.updated_at || 0).getTime()
    }
  })

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
</script>

<template>
  <div class="admin-courses">
    <h2>{{ $t('panel.courses.allCourses') }}</h2>

    <!-- Filters -->
    <div class="filters">
      <div class="search-box">
        <input
          v-model="searchQuery"
          type="text"
          :placeholder="$t('common.search')"
          class="search-box__input"
        />
      </div>

      <div class="filter-group">
        <label>{{ $t('filter.status') }}:</label>
        <select v-model="filterStatus" class="select">
          <option value="all">{{ $t('filter.all') }}</option>
          <option value="draft">{{ $t('filter.drafts') }}</option>
          <option value="review">{{ $t('filter.reviewPending') }}</option>
          <option value="approved">{{ $t('filter.approved') }}</option>
          <option value="rejected">{{ $t('filter.rejected') }}</option>
        </select>
      </div>

      <div class="filter-group">
        <label>{{ $t('filter.sortBy') }}:</label>
        <select v-model="sortBy" class="select">
          <option value="updated">{{ $t('filter.lastUpdated') }}</option>
          <option value="created">{{ $t('filter.dateCreated') }}</option>
          <option value="title">{{ $t('filter.title') }}</option>
        </select>
      </div>
    </div>

    <!-- Courses Table -->
    <div class="table-container">
      <table v-if="filteredCourses.length > 0" class="courses-table">
        <thead>
          <tr>
            <th>{{ $t('table.title') }}</th>
            <th>{{ $t('table.creator') }}</th>
            <th>{{ $t('table.status') }}</th>
            <th>{{ $t('table.updated') }}</th>
            <th>{{ $t('table.actions') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="course in filteredCourses" :key="course.id">
            <td class="cell-title">
              <strong>{{ course.title }}</strong>
              <p class="description">{{ course.description }}</p>
            </td>
            <td>{{ course.creator_id }}</td>
            <td>
              <span :class="['badge', statusBadgeClass(course)]">
                {{ statusLabel(course) }}
              </span>
            </td>
            <td class="cell-date">
              {{ new Date(course.updated_at || course.created_at).toLocaleDateString() }}
            </td>
            <td class="cell-actions">
              <button class="btn btn--sm btn--secondary">{{ $t('common.edit') }}</button>
              <button class="btn btn--sm btn--outline">{{ $t('common.view') }}</button>
              <button class="btn btn--sm btn--danger">{{ $t('common.delete') }}</button>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-else class="empty-state">
        <p>{{ $t('common.noData') }}</p>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.admin-courses {
  h2 {
    font-size: 1.3rem;
    font-weight: 600;
    margin-bottom: 1.5rem;
    color: var(--color-text-primary);
  }
}

.filters {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  align-items: flex-end;
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

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;

  label {
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--color-text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .select {
    padding: 0.6rem 0.8rem;
    border: 1px solid var(--color-border);
    border-radius: 0.5rem;
    font-size: 0.9rem;
    background: var(--color-background-primary);
    color: var(--color-text-primary);
    cursor: pointer;

    &:focus {
      outline: none;
      border-color: var(--color-primary);
      box-shadow: 0 0 0 3px rgba(var(--color-primary-rgb), 0.1);
    }
  }
}

.table-container {
  overflow-x: auto;
}

.courses-table {
  width: 100%;
  border-collapse: collapse;
  background: var(--color-background-secondary);
  border-radius: 0.5rem;
  overflow: hidden;

  thead {
    background: var(--color-background-tertiary);
    border-bottom: 2px solid var(--color-border);

    th {
      padding: 1rem;
      text-align: left;
      font-weight: 600;
      color: var(--color-text-primary);
      font-size: 0.9rem;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }
  }

  tbody {
    tr {
      border-bottom: 1px solid var(--color-border);
      transition: all 0.2s ease-in-out;

      &:hover {
        background: var(--color-background-primary);
      }

      td {
        padding: 1rem;
        color: var(--color-text-primary);
      }
    }
  }
}

.cell-title {
  strong {
    display: block;
    margin-bottom: 0.25rem;
  }

  .description {
    margin: 0;
    font-size: 0.85rem;
    color: var(--color-text-secondary);
    line-height: 1.3;
  }
}

.cell-date {
  white-space: nowrap;
  font-size: 0.9rem;
  color: var(--color-text-secondary);
}

.cell-actions {
  display: flex;
  gap: 0.5rem;
  white-space: nowrap;
}

.badge {
  display: inline-block;
  padding: 0.35rem 0.75rem;
  border-radius: 0.25rem;
  font-size: 0.8rem;
  font-weight: 600;

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

.btn {
  padding: 0.5rem 0.8rem;
  border: none;
  border-radius: 0.4rem;
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease-in-out;

  &--sm {
    padding: 0.4rem 0.7rem;
    font-size: 0.75rem;
  }

  &--secondary {
    background: var(--color-secondary);
    color: white;

    &:hover {
      background: var(--color-secondary-hover);
    }
  }

  &--outline {
    background: transparent;
    border: 1px solid var(--color-border);
    color: var(--color-text-secondary);

    &:hover {
      background: var(--color-background-secondary);
    }
  }

  &--danger {
    background: var(--color-error);
    color: white;

    &:hover {
      background: var(--color-error-hover);
    }
  }
}

.empty-state {
  padding: 2rem;
  text-align: center;
  color: var(--color-text-secondary);
  background: var(--color-background-secondary);
  border-radius: 0.5rem;
}
</style>
