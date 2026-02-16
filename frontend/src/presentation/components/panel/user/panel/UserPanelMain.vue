<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import UserDashboard from './dashboard/UserDashboard.vue'
import UserCourses from './courses/UserCourses.vue'
import UserSettings from './settings/UserSettings.vue'
import { useUserPanel } from './composables'

const { t } = useI18n()

// Tabs
type TabType = 'dashboard' | 'courses' | 'settings'
const activeTab = ref<TabType>('dashboard')

const { userStats, isLoading, error } = useUserPanel()

const tabs = computed(() => [
  { id: 'dashboard', label: t('user.dashboard.title'), icon: 'grid' },
  { id: 'courses', label: t('user.courses.title'), icon: 'book' },
  { id: 'settings', label: t('user.settings.title'), icon: 'settings' }
])

const currentComponent = computed(() => {
  switch (activeTab.value) {
    case 'courses':
      return UserCourses
    case 'settings':
      return UserSettings
    default:
      return UserDashboard
  }
})
</script>

<template>
  <div class="user-panel">
    <!-- Header -->
    <div class="user-panel__header">
      <h1>{{ $t('user.panel.title') }}</h1>
      <p class="user-panel__subtitle">{{ $t('user.panel.subtitle') }}</p>
    </div>

    <!-- Error Alert -->
    <div v-if="error" class="alert alert--error">
      {{ error }}
    </div>

    <!-- Tab Navigation -->
    <div class="user-panel__tabs">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        :class="['tab', { 'tab--active': activeTab === tab.id }]"
        @click="activeTab = tab.id as TabType"
      >
        <span class="tab__icon" :data-icon="tab.icon"></span>
        {{ tab.label }}
      </button>
    </div>

    <!-- Content Area -->
    <div class="user-panel__content">
      <div v-if="isLoading" class="loading">
        {{ $t('common.loading') }}
      </div>

      <component
        v-else
        :is="currentComponent"
        :user-stats="userStats"
      />
    </div>
  </div>
</template>

<style scoped lang="scss">
.user-panel {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;

  &__header {
    margin-bottom: 2rem;

    h1 {
      font-size: 2rem;
      font-weight: 600;
      margin-bottom: 0.5rem;
      color: var(--color-text-primary);
    }
  }

  &__subtitle {
    color: var(--color-text-secondary);
    font-size: 0.95rem;
  }

  &__tabs {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 2rem;
    border-bottom: 1px solid var(--color-border);
    padding-bottom: 1rem;
  }

  &__content {
    animation: fadeIn 0.3s ease-in-out;
  }
}

.tab {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: none;
  border: none;
  color: var(--color-text-secondary);
  cursor: pointer;
  font-size: 0.95rem;
  font-weight: 500;
  transition: all 0.2s ease-in-out;
  position: relative;

  &:hover {
    color: var(--color-text-primary);
  }

  &--active {
    color: var(--color-primary);

    &::after {
      content: '';
      position: absolute;
      bottom: -1rem;
      left: 0;
      right: 0;
      height: 2px;
      background: var(--color-primary);
    }
  }

  &__icon {
    width: 1.2rem;
    height: 1.2rem;
  }
}

.alert {
  padding: 1rem;
  margin-bottom: 1.5rem;
  border-radius: 0.5rem;
  background: var(--color-error-light);
  color: var(--color-error-dark);
  border-left: 4px solid var(--color-error);

  &--error {
    background: var(--color-error-light);
    color: var(--color-error-dark);
    border-left-color: var(--color-error);
  }
}

.loading {
  text-align: center;
  padding: 2rem;
  color: var(--color-text-secondary);
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }

  to {
    opacity: 1;
  }
}
</style>
