<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useUserStore } from '@/application/stores/modules/core/auth.store'

interface Props {
  userStats?: {
    totalCourses: number
    enrolledCourses: number
    completedCourses: number
    inProgressCourses: number
    averageProgress: number
    totalTokens: number
    tokenBalance: number
    lastLoginAt?: string
  }
}

defineProps<Props>()

const { t } = useI18n()
const userStore = useUserStore()

const currentUser = computed(() => userStore.currentUser)

const statCards = computed(() => [
  {
    id: 'enrolled',
    label: t('stats.enrolledCourses'),
    value: 12,
    icon: 'book-open',
    color: 'primary'
  },
  {
    id: 'in-progress',
    label: t('stats.inProgress'),
    value: 5,
    icon: 'trending-up',
    color: 'warning'
  },
  {
    id: 'completed',
    label: t('stats.completed'),
    value: 7,
    icon: 'check-circle',
    color: 'success'
  },
  {
    id: 'tokens',
    label: t('stats.tokenBalance'),
    value: '2,450',
    icon: 'zap',
    color: 'info'
  }
])

const quickActions = computed(() => [
  {
    id: 'new-course',
    label: t('actions.createCourse'),
    icon: 'plus',
    href: '/course-editor/new'
  },
  {
    id: 'browse-courses',
    label: t('actions.browseCourses'),
    icon: 'search',
    href: '/courses'
  },
  {
    id: 'buy-tokens',
    label: t('actions.buyTokens'),
    icon: 'shopping-cart',
    href: '/tokens/buy'
  }
])
</script>

<template>
  <div class="dashboard">
    <!-- Welcome Section -->
    <div class="welcome">
      <h2>{{ $t('dashboard.welcome', { name: currentUser?.name }) }}</h2>
      <p>{{ $t('dashboard.subtitle') }}</p>
    </div>

    <!-- Stats Grid -->
    <div class="stats-grid">
      <div
        v-for="stat in statCards"
        :key="stat.id"
        :class="['stat-card', `stat-card--${stat.color}`]"
      >
        <div class="stat-card__icon" :data-icon="stat.icon"></div>
        <div class="stat-card__content">
          <p class="stat-card__label">{{ stat.label }}</p>
          <p class="stat-card__value">{{ stat.value }}</p>
        </div>
      </div>
    </div>

    <!-- Progress Section -->
    <div class="progress-section">
      <h3>{{ $t('dashboard.currentProgress') }}</h3>
      <div class="course-progress">
        <div class="progress-item">
          <div class="progress-header">
            <span class="progress-title">Python Basics</span>
            <span class="progress-percent">65%</span>
          </div>
          <div class="progress-bar">
            <div class="progress-bar__fill" style="width: 65%"></div>
          </div>
        </div>

        <div class="progress-item">
          <div class="progress-header">
            <span class="progress-title">Web Development</span>
            <span class="progress-percent">40%</span>
          </div>
          <div class="progress-bar">
            <div class="progress-bar__fill" style="width: 40%"></div>
          </div>
        </div>

        <div class="progress-item">
          <div class="progress-header">
            <span class="progress-title">Database Design</span>
            <span class="progress-percent">85%</span>
          </div>
          <div class="progress-bar">
            <div class="progress-bar__fill" style="width: 85%"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="quick-actions">
      <h3>{{ $t('dashboard.quickActions') }}</h3>
      <div class="actions-grid">
        <a
          v-for="action in quickActions"
          :key="action.id"
          :href="action.href"
          :class="['action-btn', `action-btn--${action.id}`]"
        >
          <span class="action-btn__icon" :data-icon="action.icon"></span>
          {{ action.label }}
        </a>
      </div>
    </div>

    <!-- Recent Activity -->
    <div class="recent-activity">
      <h3>{{ $t('dashboard.recentActivity') }}</h3>
      <div class="activity-list">
        <div class="activity-item">
          <div class="activity-item__time">{{ $t('time.today') }}</div>
          <div class="activity-item__text">
            {{ $t('activity.completedLesson', { lesson: 'Database Fundamentals' }) }}
          </div>
        </div>

        <div class="activity-item">
          <div class="activity-item__time">{{ $t('time.yesterday') }}</div>
          <div class="activity-item__text">
            {{ $t('activity.earnedBadge', { badge: 'Expert Learner' }) }}
          </div>
        </div>

        <div class="activity-item">
          <div class="activity-item__time">3 {{ $t('time.daysAgo') }}</div>
          <div class="activity-item__text">
            {{ $t('activity.enrolledCourse', { course: 'Advanced Python' }) }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.dashboard {
  display: grid;
  gap: 2rem;
}

.welcome {
  h2 {
    font-size: 1.5rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
    color: var(--color-text-primary);
  }

  p {
    color: var(--color-text-secondary);
  }
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  background: var(--color-background-secondary);
  border-radius: 0.5rem;
  border-left: 4px solid var(--color-primary);
  transition: all 0.2s ease-in-out;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }

  &--success {
    border-left-color: var(--color-success);
  }

  &--warning {
    border-left-color: var(--color-warning);
  }

  &--info {
    border-left-color: var(--color-info);
  }

  &__icon {
    font-size: 2rem;
    opacity: 0.7;
  }

  &__content {
    flex: 1;
  }

  &__label {
    font-size: 0.875rem;
    color: var(--color-text-secondary);
    margin-bottom: 0.25rem;
  }

  &__value {
    font-size: 1.75rem;
    font-weight: 600;
    color: var(--color-text-primary);
  }
}

.progress-section {
  h3 {
    font-size: 1.1rem;
    font-weight: 600;
    margin-bottom: 1rem;
    color: var(--color-text-primary);
  }
}

.course-progress {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.progress-item {
  .progress-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 0.5rem;
    font-size: 0.9rem;
  }

  .progress-title {
    color: var(--color-text-primary);
    font-weight: 500;
  }

  .progress-percent {
    color: var(--color-text-secondary);
  }

  .progress-bar {
    height: 8px;
    background: var(--color-background-tertiary);
    border-radius: 4px;
    overflow: hidden;

    &__fill {
      height: 100%;
      background: linear-gradient(90deg, var(--color-primary), var(--color-secondary));
      border-radius: 4px;
      transition: width 0.3s ease-in-out;
    }
  }
}

.quick-actions {
  h3 {
    font-size: 1.1rem;
    font-weight: 600;
    margin-bottom: 1rem;
    color: var(--color-text-primary);
  }
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 1rem;
  background: var(--color-primary);
  color: white;
  border-radius: 0.5rem;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.2s ease-in-out;
  cursor: pointer;

  &:hover {
    background: var(--color-primary-hover);
    transform: translateY(-2px);
  }

  &__icon {
    font-size: 1.2rem;
  }
}

.recent-activity {
  h3 {
    font-size: 1.1rem;
    font-weight: 600;
    margin-bottom: 1rem;
    color: var(--color-text-primary);
  }
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.activity-item {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  background: var(--color-background-secondary);
  border-radius: 0.5rem;
  border-left: 3px solid var(--color-primary);

  &__time {
    min-width: 100px;
    font-size: 0.875rem;
    font-weight: 500;
    color: var(--color-text-secondary);
  }

  &__text {
    color: var(--color-text-primary);
  }
}
</style>
