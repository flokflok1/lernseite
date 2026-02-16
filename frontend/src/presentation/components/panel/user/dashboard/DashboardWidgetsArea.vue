<template>
  <div class="dashboard-widgets-area">
    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">
      {{ error }}
    </div>

    <!-- Widgets Grid -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
      <component
        v-for="widgetInstance in dashboardStore.visibleWidgets"
        :key="widgetInstance.instanceId"
        :is="getWidgetComponent(widgetInstance.widgetId)"
        :instance="widgetInstance"
        :definition="getDefinition(widgetInstance.widgetId)"
        :data-context="dataContext"
      />
    </div>

    <!-- Empty State -->
    <div
      v-if="!loading && !error && dashboardStore.visibleWidgets.length === 0"
      class="text-center py-12 text-[var(--color-text-secondary)]"
    >
      <p class="text-lg">{{ $t('widgets.noWidgets') }}</p>
      <p class="text-sm mt-2">
        <span v-if="dashboardStore.canCustomizeWidgets">
          {{ $t('widgets.enableWidgets') }}
        </span>
        <span v-else>
          {{ $t('widgets.contactSupport') }}
        </span>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineAsyncComponent } from 'vue'
import { useDashboardStore } from '@/application/stores/modules/learning/dashboard.store'
import { getWidgetDefinition } from '@/infrastructure/config/widgetRegistry'
import type { WidgetDataContext, WidgetDefinition } from '@/types/widgets'

// ============================================================================
// Props
// ============================================================================

interface Props {
  dataContext: WidgetDataContext
  loading?: boolean
  error?: string | null
}

withDefaults(defineProps<Props>(), {
  loading: false,
  error: null
})

// ============================================================================
// Store
// ============================================================================

const dashboardStore = useDashboardStore()

// ============================================================================
// Widget Component Mapping
// ============================================================================

const widgetComponents: Record<string, ReturnType<typeof defineAsyncComponent>> = {
  'welcome': defineAsyncComponent(() => import('./widgets/WelcomeWidget.vue')),
  'profile-summary': defineAsyncComponent(() => import('./widgets/ProfileSummaryWidget.vue')),
  'plan-tokens': defineAsyncComponent(() => import('./widgets/PlanTokensWidget.vue')),
  'enrolled-courses': defineAsyncComponent(() => import('./widgets/EnrolledCoursesWidget.vue')),
  'courses-progress': defineAsyncComponent(() => import('./widgets/CoursesProgressWidget.vue')),
  'org-overview': defineAsyncComponent(() => import('./widgets/OrgOverviewWidget.vue'))
}

// ============================================================================
// Methods
// ============================================================================

const getWidgetComponent = (widgetId: string) => {
  return widgetComponents[widgetId] || null
}

const getDefinition = (widgetId: string): WidgetDefinition | undefined => {
  return getWidgetDefinition(widgetId)
}
</script>

<style scoped>
.dashboard-widgets-area {
  width: 100%;
}
</style>
