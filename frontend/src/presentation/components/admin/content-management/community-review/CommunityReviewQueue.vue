<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { Course } from '@/infrastructure/api/clients/learning'

const { t } = useI18n()

interface CourseReview extends Course {
  submittedAt: Date
  creator: {
    name: string
    email: string
  }
}

const mockReviews: CourseReview[] = [
  {
    id: 'review-1',
    title: 'Web Development Masterclass',
    description: 'Complete guide to modern web development',
    creator_id: 'user-456',
    creator: { name: 'John Doe', email: 'john@example.com' },
    source: 'community',
    status: 'review_pending',
    is_published: false,
    created_at: new Date('2024-01-25'),
    updated_at: new Date('2024-01-26'),
    submittedAt: new Date('2024-01-25T14:30:00')
  },
  {
    id: 'review-2',
    title: 'Advanced React Patterns',
    description: 'Learn advanced React patterns and hooks',
    creator_id: 'user-567',
    creator: { name: 'Jane Smith', email: 'jane@example.com' },
    source: 'community',
    status: 'review_pending',
    is_published: false,
    created_at: new Date('2024-01-24'),
    updated_at: new Date('2024-01-24'),
    submittedAt: new Date('2024-01-24T10:15:00')
  },
  {
    id: 'review-3',
    title: 'Machine Learning Basics',
    description: 'Introduction to ML algorithms',
    creator_id: 'user-678',
    creator: { name: 'Bob Wilson', email: 'bob@example.com' },
    source: 'community',
    status: 'review_pending',
    is_published: false,
    created_at: new Date('2024-01-23'),
    updated_at: new Date('2024-01-23'),
    submittedAt: new Date('2024-01-23T09:45:00')
  }
]

const reviews = ref<CourseReview[]>(mockReviews)
const sortBy = ref<'submitted' | 'title'>('submitted')
const selectedReview = ref<CourseReview | null>(null)
const reviewNotes = ref('')

const sortedReviews = computed(() => {
  const sorted = [...reviews.value]
  sorted.sort((a, b) => {
    switch (sortBy.value) {
      case 'title':
        return a.title.localeCompare(b.title)
      case 'submitted':
      default:
        return new Date(b.submittedAt).getTime() - new Date(a.submittedAt).getTime()
    }
  })
  return sorted
})

const pendingCount = computed(() => reviews.value.length)

const handleApprove = (courseId: string) => {
  const course = reviews.value.find(r => r.id === courseId)
  if (course && confirm(`Approve "${course.title}"?`)) {
    reviews.value = reviews.value.filter(r => r.id !== courseId)
    selectedReview.value = null
    reviewNotes.value = ''
  }
}

const handleReject = (courseId: string) => {
  const course = reviews.value.find(r => r.id === courseId)
  if (course && reviewNotes.value.trim()) {
    reviews.value = reviews.value.filter(r => r.id !== courseId)
    selectedReview.value = null
    reviewNotes.value = ''
  }
}

const handleSelectReview = (review: CourseReview) => {
  selectedReview.value = review
  reviewNotes.value = ''
}
</script>

<template>
  <div class="community-review">
    <h2>{{ $t('admin.community.reviewQueue') }}</h2>

    <!-- Review Queue Stats -->
    <div class="review-stats">
      <div class="stat-badge">
        <span class="stat-badge__label">{{ $t('admin.community.pending') }}</span>
        <span class="stat-badge__value">{{ pendingCount }}</span>
      </div>
    </div>

    <!-- Review List & Detail -->
    <div class="review-container">
      <!-- Queue List -->
      <div class="review-list">
        <div class="review-list__header">
          <h3>{{ $t('admin.community.submittedCourses') }}</h3>
          <div class="sort-control">
            <label>{{ $t('filter.sortBy') }}:</label>
            <select v-model="sortBy" class="select">
              <option value="submitted">{{ $t('filter.dateSubmitted') }}</option>
              <option value="title">{{ $t('filter.title') }}</option>
            </select>
          </div>
        </div>

        <div class="review-items">
          <div
            v-for="review in sortedReviews"
            :key="review.id"
            :class="['review-item', { 'review-item--active': selectedReview?.id === review.id }]"
            @click="handleSelectReview(review)"
          >
            <h4>{{ review.title }}</h4>
            <p class="creator">{{ review.creator.name }}</p>
            <p class="submitted-date">
              {{ new Date(review.submittedAt).toLocaleDateString() }}
            </p>
          </div>
        </div>
      </div>

      <!-- Review Detail -->
      <div class="review-detail">
        <div v-if="selectedReview" class="review-panel">
          <h3>{{ selectedReview.title }}</h3>

          <!-- Course Info -->
          <div class="course-info">
            <div class="info-group">
              <label>{{ $t('course.creator') }}:</label>
              <p>{{ selectedReview.creator.name }}</p>
              <p class="email">{{ selectedReview.creator.email }}</p>
            </div>

            <div class="info-group">
              <label>{{ $t('course.description') }}:</label>
              <p>{{ selectedReview.description }}</p>
            </div>

            <div class="info-group">
              <label>{{ $t('course.submitted') }}:</label>
              <p>{{ new Date(selectedReview.submittedAt).toLocaleString() }}</p>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="review-actions">
            <button
              class="btn btn--primary"
              @click="handleApprove(selectedReview.id)"
            >
              {{ $t('admin.community.approve') }}
            </button>

            <button
              :disabled="!reviewNotes.trim()"
              class="btn btn--danger"
              @click="handleReject(selectedReview.id)"
            >
              {{ $t('admin.community.reject') }}
            </button>
          </div>

          <!-- Review Notes -->
          <div class="review-notes">
            <label>{{ $t('admin.community.reviewNotes') }}:</label>
            <textarea
              v-model="reviewNotes"
              rows="6"
              :placeholder="$t('admin.community.notesPlaceholder')"
              class="textarea"
            ></textarea>
            <p class="notes-hint" v-if="!reviewNotes.trim()">
              {{ $t('admin.community.rejectRequiresNotes') }}
            </p>
          </div>
        </div>

        <div v-else class="empty-state">
          <p>{{ $t('admin.community.selectCourse') }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.community-review {
  h2 {
    font-size: 1.3rem;
    font-weight: 600;
    margin-bottom: 1.5rem;
    color: var(--color-text-primary);
  }
}

.review-stats {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-badge {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 1.5rem;
  background: var(--color-warning-light);
  border-radius: 0.5rem;
  border-left: 4px solid var(--color-warning);

  &__label {
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--color-warning-dark);
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  &__value {
    font-size: 2rem;
    font-weight: 700;
    color: var(--color-warning-dark);
  }
}

.review-container {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 1.5rem;

  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
  }
}

.review-list {
  background: var(--color-background-secondary);
  border-radius: 0.5rem;
  overflow: hidden;
  border: 1px solid var(--color-border);

  &__header {
    padding: 1rem;
    border-bottom: 1px solid var(--color-border);
    background: var(--color-background-tertiary);

    h3 {
      margin: 0 0 1rem 0;
      font-size: 0.95rem;
      font-weight: 600;
      color: var(--color-text-primary);
    }

    .sort-control {
      display: flex;
      align-items: center;
      gap: 0.5rem;

      label {
        font-size: 0.85rem;
        font-weight: 600;
        color: var(--color-text-secondary);
      }

      .select {
        padding: 0.4rem 0.6rem;
        border: 1px solid var(--color-border);
        border-radius: 0.4rem;
        font-size: 0.85rem;
        background: var(--color-background-primary);
        color: var(--color-text-primary);
        cursor: pointer;
      }
    }
  }
}

.review-items {
  max-height: 600px;
  overflow-y: auto;
}

.review-item {
  padding: 1rem;
  border-bottom: 1px solid var(--color-border);
  cursor: pointer;
  transition: all 0.2s ease-in-out;

  &:hover {
    background: var(--color-background-primary);
  }

  &--active {
    background: var(--color-primary-light);
    border-left: 3px solid var(--color-primary);
    padding-left: calc(1rem - 3px);
  }

  h4 {
    margin: 0 0 0.35rem 0;
    font-size: 0.95rem;
    font-weight: 600;
    color: var(--color-text-primary);
  }

  .creator {
    margin: 0 0 0.25rem 0;
    font-size: 0.85rem;
    color: var(--color-text-secondary);
  }

  .submitted-date {
    margin: 0;
    font-size: 0.8rem;
    color: var(--color-text-tertiary);
  }
}

.review-detail {
  background: var(--color-background-secondary);
  border-radius: 0.5rem;
  border: 1px solid var(--color-border);
  padding: 1.5rem;
}

.review-panel {
  h3 {
    margin: 0 0 1.5rem 0;
    font-size: 1.2rem;
    font-weight: 600;
    color: var(--color-text-primary);
  }
}

.course-info {
  margin-bottom: 2rem;
  padding: 1rem;
  background: var(--color-background-primary);
  border-radius: 0.5rem;
  border: 1px solid var(--color-border);
}

.info-group {
  margin-bottom: 1rem;

  &:last-child {
    margin-bottom: 0;
  }

  label {
    display: block;
    font-weight: 600;
    color: var(--color-text-secondary);
    margin-bottom: 0.35rem;
    font-size: 0.9rem;
  }

  p {
    margin: 0.25rem 0;
    color: var(--color-text-primary);
    line-height: 1.4;

    &.email {
      font-size: 0.9rem;
      color: var(--color-text-secondary);
    }
  }
}

.review-actions {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.btn {
  flex: 1;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease-in-out;

  &--primary {
    background: var(--color-success);
    color: white;

    &:hover {
      background: var(--color-success-hover);
    }
  }

  &--danger {
    background: var(--color-error);
    color: white;

    &:hover:not(:disabled) {
      background: var(--color-error-hover);
    }

    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
  }
}

.review-notes {
  label {
    display: block;
    font-weight: 600;
    color: var(--color-text-primary);
    margin-bottom: 0.5rem;
  }

  .textarea {
    width: 100%;
    padding: 1rem;
    border: 1px solid var(--color-border);
    border-radius: 0.5rem;
    font-family: inherit;
    font-size: 0.9rem;
    color: var(--color-text-primary);
    background: var(--color-background-primary);
    resize: vertical;

    &:focus {
      outline: none;
      border-color: var(--color-primary);
      box-shadow: 0 0 0 3px rgba(var(--color-primary-rgb), 0.1);
    }
  }

  .notes-hint {
    margin-top: 0.5rem;
    font-size: 0.85rem;
    color: var(--color-error);
    font-style: italic;
  }
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  color: var(--color-text-secondary);
  text-align: center;

  p {
    margin: 0;
  }
}
</style>
