<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import AdminCourses from './courses/AdminCourses.vue'
import CommunityReviewQueue from './community-review/CommunityReviewQueue.vue'
import AcademyCourses from './academy/AcademyCourses.vue'
import LMConfiguration from './learning-methods-management/LMConfiguration.vue'
import { useAccessControl } from '@/application/composables/useAccessControl'

const { t } = useI18n()
const { isAdmin, isOwner } = useAccessControl()

// Tabs - only content management tabs (not dashboard)
type ContentManagementTabType = 'courses' | 'community' | 'academy' | 'lm'
const activeTab = ref<ContentManagementTabType>('courses')

const tabs = computed(() => {
  const allTabs = [
    { id: 'courses', label: t('panel.courses.title'), icon: 'book' },
    { id: 'community', label: t('panel.community.title'), icon: 'users', badge: 3 },
    { id: 'academy', label: t('panel.academy.title'), icon: 'star' },
    { id: 'lm', label: t('panel.learningMethods.title'), icon: 'settings' }
  ]

  // Filter tabs based on user role
  return allTabs.filter(tab => {
    // Community review only for admin/owner
    if (tab.id === 'community') return isAdmin.value || isOwner.value
    // Academy only for owner
    if (tab.id === 'academy') return isOwner.value
    return true
  })
})

const currentComponent = computed(() => {
  switch (activeTab.value) {
    case 'community':
      return CommunityReviewQueue
    case 'academy':
      return AcademyCourses
    case 'lm':
      return LMConfiguration
    default:
      return AdminCourses
  }
})
</script>

<template>
  <div class="content-management">
    <!-- Header -->
    <div class="content-header">
      <h1>{{ $t('panel.contentManagement.title') }}</h1>
      <p class="content-header__subtitle">{{ $t('panel.contentManagement.subtitle') }}</p>
    </div>

    <!-- Tab Navigation -->
    <div class="content-tabs">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        :class="['tab', { 'tab--active': activeTab === tab.id }]"
        @click="activeTab = tab.id as ContentManagementTabType"
      >
        <span class="tab__icon" :data-icon="tab.icon"></span>
        {{ tab.label }}
        <span v-if="tab.badge" class="tab__badge">{{ tab.badge }}</span>
      </button>
    </div>

    <!-- Content Area -->
    <div class="content-area">
      <component :is="currentComponent" />
    </div>
  </div>
</template>

<style scoped lang="scss">
.content-management {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
}

.content-header {
  margin-bottom: 2rem;

  h1 {
    font-size: 2rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
    color: var(--color-text-primary);
  }

  &__subtitle {
    color: var(--color-text-secondary);
    font-size: 0.95rem;
  }
}

.content-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 2rem;
  border-bottom: 1px solid var(--color-border);
  padding-bottom: 1rem;
  overflow-x: auto;
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
  white-space: nowrap;

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

  &__badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 1.5rem;
    height: 1.5rem;
    padding: 0 0.35rem;
    background: var(--color-warning);
    color: white;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-left: 0.5rem;
  }
}

.content-area {
  animation: fadeIn 0.3s ease-in-out;
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
