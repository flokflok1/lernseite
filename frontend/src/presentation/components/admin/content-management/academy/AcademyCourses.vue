<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { Course } from '@/infrastructure/api/clients/learning'

const { t } = useI18n()

interface AcademyCourse extends Course {
  teamMember: string
  createdBy: string
}

const mockCourses: AcademyCourse[] = [
  {
    id: 'academy-1',
    title: 'Enterprise Python Development',
    description: 'Advanced Python for enterprise applications',
    creator_id: 'admin-1',
    source: 'academy',
    status: 'approved',
    is_published: true,
    teamMember: 'John Smith',
    createdBy: 'System Owner',
    created_at: new Date('2024-01-10'),
    updated_at: new Date('2024-01-26')
  },
  {
    id: 'academy-2',
    title: 'Cloud Architecture Masterclass',
    description: 'AWS and cloud design patterns',
    creator_id: 'admin-2',
    source: 'academy',
    status: 'approved',
    is_published: true,
    teamMember: 'Jane Doe',
    createdBy: 'System Owner',
    created_at: new Date('2024-01-05'),
    updated_at: new Date('2024-01-20')
  }
]

const courses = ref<AcademyCourse[]>(mockCourses)
const searchQuery = ref('')
const sortBy = ref<'updated' | 'title' | 'created'>('updated')

const filteredCourses = computed(() => {
  let result = courses.value

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(
      course =>
        course.title.toLowerCase().includes(query) ||
        course.description.toLowerCase().includes(query)
    )
  }

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
</script>

<template>
  <div class="academy-courses">
    <h2>{{ $t('admin.academy.courses') }}</h2>

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
        <label>{{ $t('filter.sortBy') }}:</label>
        <select v-model="sortBy" class="select">
          <option value="updated">{{ $t('filter.lastUpdated') }}</option>
          <option value="created">{{ $t('filter.dateCreated') }}</option>
          <option value="title">{{ $t('filter.title') }}</option>
        </select>
      </div>

      <button class="btn btn--primary">+ {{ $t('admin.academy.createCourse') }}</button>
    </div>

    <!-- Academy Courses List -->
    <div class="courses-grid">
      <div
        v-for="course in filteredCourses"
        :key="course.id"
        class="course-card"
      >
        <div class="course-card__header">
          <h3>{{ course.title }}</h3>
          <span class="badge badge--academy">{{ $t('course.type.academy') }}</span>
        </div>

        <p class="course-card__description">{{ course.description }}</p>

        <div class="course-card__meta">
          <div class="meta-item">
            <span class="meta-label">{{ $t('course.teamMember') }}:</span>
            <span class="meta-value">{{ course.teamMember }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">{{ $t('course.createdBy') }}:</span>
            <span class="meta-value">{{ course.createdBy }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">{{ $t('course.updated') }}:</span>
            <span class="meta-value">{{
              new Date(course.updated_at || course.created_at).toLocaleDateString()
            }}</span>
          </div>
        </div>

        <div class="course-card__actions">
          <button class="btn btn--secondary">{{ $t('common.edit') }}</button>
          <button class="btn btn--outline">{{ $t('common.view') }}</button>
          <button class="btn btn--danger">{{ $t('common.delete') }}</button>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="filteredCourses.length === 0" class="empty-state">
      <p>{{ $t('admin.academy.noCourses') }}</p>
    </div>
  </div>
</template>

<style scoped lang="scss">
.academy-courses {
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
  margin-bottom: 2rem;
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
  }

  .select {
    padding: 0.6rem 0.8rem;
    border: 1px solid var(--color-border);
    border-radius: 0.5rem;
    font-size: 0.9rem;
    background: var(--color-background-primary);
    color: var(--color-text-primary);
    cursor: pointer;
  }
}

.btn {
  padding: 0.6rem 1.2rem;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease-in-out;

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

.courses-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
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
    display: grid;
    gap: 0.75rem;
    margin-bottom: 1rem;
    font-size: 0.85rem;
    padding: 1rem 0;
    border-top: 1px solid var(--color-border);
    border-bottom: 1px solid var(--color-border);
  }

  &__actions {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
  }
}

.meta-item {
  display: flex;
  gap: 0.5rem;
}

.meta-label {
  color: var(--color-text-tertiary);
  font-weight: 600;
}

.meta-value {
  color: var(--color-text-secondary);
}

.badge {
  display: inline-block;
  padding: 0.35rem 0.75rem;
  border-radius: 0.25rem;
  font-size: 0.8rem;
  font-weight: 600;

  &--academy {
    background: var(--color-primary-light);
    color: var(--color-primary);
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
