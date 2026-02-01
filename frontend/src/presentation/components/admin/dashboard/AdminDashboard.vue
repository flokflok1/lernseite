<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const adminStats = computed(() => [
  {
    id: 'total-users',
    label: t('stats.totalUsers'),
    value: 1250,
    icon: 'users',
    color: 'primary'
  },
  {
    id: 'total-courses',
    label: t('stats.totalCourses'),
    value: 156,
    icon: 'book',
    color: 'secondary'
  },
  {
    id: 'pending-review',
    label: t('stats.pendingReview'),
    value: 12,
    icon: 'alert-circle',
    color: 'warning'
  },
  {
    id: 'system-health',
    label: t('stats.systemHealth'),
    value: '98%',
    icon: 'activity',
    color: 'success'
  }
])

const recentActivities = computed(() => [
  {
    id: 1,
    type: 'course_submission',
    message: t('activity.courseSubmitted', { course: 'Python Advanced' }),
    timestamp: '2024-01-26T10:30:00',
    icon: 'plus-circle'
  },
  {
    id: 2,
    type: 'user_registered',
    message: t('activity.userRegistered', { user: 'John Doe' }),
    timestamp: '2024-01-26T09:15:00',
    icon: 'user-plus'
  },
  {
    id: 3,
    type: 'course_published',
    message: t('activity.coursePublished', { course: 'Web Development 101' }),
    timestamp: '2024-01-26T08:45:00',
    icon: 'check-circle'
  },
  {
    id: 4,
    type: 'system_alert',
    message: t('activity.systemAlert', { issue: 'High memory usage' }),
    timestamp: '2024-01-25T16:20:00',
    icon: 'alert-triangle'
  }
])
</script>

<template>
  <div class="admin-dashboard">
    <h1>{{ $t('admin.dashboard.title') }}</h1>
    <p class="subtitle">{{ $t('admin.dashboard.subtitle') }}</p>

    <!-- Key Metrics -->
    <div class="metrics-grid">
      <div
        v-for="stat in adminStats"
        :key="stat.id"
        :class="['metric-card', `metric-card--${stat.color}`]"
      >
        <div class="metric-card__icon" :data-icon="stat.icon"></div>
        <div class="metric-card__content">
          <p class="metric-card__label">{{ stat.label }}</p>
          <p class="metric-card__value">{{ stat.value }}</p>
        </div>
      </div>
    </div>

    <!-- System Overview -->
    <div class="system-overview">
      <h2>{{ $t('admin.dashboard.systemOverview') }}</h2>
      <div class="overview-grid">
        <div class="overview-item">
          <h4>{{ $t('admin.dashboard.apiHealth') }}</h4>
          <div class="health-indicator health-indicator--healthy"></div>
          <p>All systems operational</p>
        </div>

        <div class="overview-item">
          <h4>{{ $t('admin.dashboard.databaseStatus') }}</h4>
          <div class="health-indicator health-indicator--healthy"></div>
          <p>Connected (156 tables)</p>
        </div>

        <div class="overview-item">
          <h4>{{ $t('admin.dashboard.cacheStatus') }}</h4>
          <div class="health-indicator health-indicator--healthy"></div>
          <p>Redis connected</p>
        </div>

        <div class="overview-item">
          <h4>{{ $t('admin.dashboard.storageUsage') }}</h4>
          <div class="progress-bar">
            <div class="progress-bar__fill" style="width: 68%"></div>
          </div>
          <p>68% of capacity used</p>
        </div>
      </div>
    </div>

    <!-- Recent Activities -->
    <div class="recent-activities">
      <h2>{{ $t('admin.dashboard.recentActivities') }}</h2>
      <div class="activity-timeline">
        <div
          v-for="activity in recentActivities"
          :key="activity.id"
          class="timeline-item"
        >
          <div class="timeline-item__icon" :data-icon="activity.icon"></div>
          <div class="timeline-item__content">
            <p class="message">{{ activity.message }}</p>
            <span class="timestamp">{{
              new Date(activity.timestamp).toLocaleString()
            }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Links -->
    <div class="quick-links">
      <h2>{{ $t('admin.dashboard.quickLinks') }}</h2>
      <div class="links-grid">
        <a href="/admin/users" class="link-card">
          <span class="link-card__icon" data-icon="users"></span>
          <span class="link-card__label">{{ $t('admin.manageUsers') }}</span>
        </a>

        <a href="/admin/content-management" class="link-card">
          <span class="link-card__icon" data-icon="book"></span>
          <span class="link-card__label">{{ $t('admin.contentManagement.title') }}</span>
        </a>

        <a href="/admin/reports" class="link-card">
          <span class="link-card__icon" data-icon="bar-chart"></span>
          <span class="link-card__label">{{ $t('admin.viewReports') }}</span>
        </a>

        <a href="/admin/settings" class="link-card">
          <span class="link-card__icon" data-icon="settings"></span>
          <span class="link-card__label">{{ $t('admin.systemSettings') }}</span>
        </a>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.admin-dashboard {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;

  h1 {
    font-size: 2rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
    color: var(--color-text-primary);
  }

  .subtitle {
    color: var(--color-text-secondary);
    font-size: 0.95rem;
    margin-bottom: 2rem;
  }

  h2 {
    font-size: 1.2rem;
    font-weight: 600;
    margin-bottom: 1.5rem;
    color: var(--color-text-primary);
  }
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.metric-card {
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

  &--secondary {
    border-left-color: var(--color-secondary);
  }

  &--warning {
    border-left-color: var(--color-warning);
  }

  &--success {
    border-left-color: var(--color-success);
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

.system-overview {
  margin-bottom: 2rem;

  .overview-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
  }
}

.overview-item {
  padding: 1.5rem;
  background: var(--color-background-secondary);
  border-radius: 0.5rem;
  border: 1px solid var(--color-border);

  h4 {
    font-size: 0.9rem;
    color: var(--color-text-secondary);
    margin: 0 0 0.75rem 0;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  p {
    margin: 0;
    font-size: 0.9rem;
    color: var(--color-text-primary);
  }
}

.health-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin: 0.5rem 0;

  &--healthy {
    background: var(--color-success);
  }

  &--warning {
    background: var(--color-warning);
  }

  &--error {
    background: var(--color-error);
  }
}

.progress-bar {
  height: 8px;
  background: var(--color-background-tertiary);
  border-radius: 4px;
  overflow: hidden;
  margin: 0.75rem 0;

  &__fill {
    height: 100%;
    background: var(--color-primary);
    border-radius: 4px;
  }
}

.recent-activities {
  margin-bottom: 2rem;
}

.activity-timeline {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.timeline-item {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  background: var(--color-background-secondary);
  border-radius: 0.5rem;
  border-left: 3px solid var(--color-primary);

  &__icon {
    font-size: 1.5rem;
    flex-shrink: 0;
  }

  &__content {
    flex: 1;
  }

  .message {
    color: var(--color-text-primary);
    margin: 0 0 0.25rem 0;
    font-weight: 500;
  }

  .timestamp {
    font-size: 0.85rem;
    color: var(--color-text-tertiary);
  }
}

.quick-links {
  .links-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 1.5rem;
  }
}

.link-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  padding: 1.5rem;
  background: var(--color-background-secondary);
  border-radius: 0.5rem;
  border: 1px solid var(--color-border);
  text-decoration: none;
  color: inherit;
  transition: all 0.2s ease-in-out;

  &:hover {
    border-color: var(--color-primary);
    box-shadow: 0 4px 12px rgba(var(--color-primary-rgb), 0.2);
    transform: translateY(-2px);
  }

  &__icon {
    font-size: 2rem;
  }

  &__label {
    font-size: 0.9rem;
    font-weight: 500;
    color: var(--color-text-primary);
    text-align: center;
  }
}
</style>
