<template>
  <div class="admin-analytics-page">
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-[var(--color-text-primary)]">{{ $t('admin.analyticsPage.title') }}</h1>
      <p class="text-[var(--color-text-secondary)] mt-1">{{ $t('admin.analyticsPage.subtitle') }}</p>
    </div>
    <!-- Timeframe Filter -->
    <div class="mb-6 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <label class="text-sm font-medium text-gray-700">{{ $t('admin.analyticsPage.timeframe') }}</label>
        <div class="flex gap-2">
          <button
            v-for="tf in timeframeOptions"
            :key="tf.value"
            @click="changeTimeframe(tf.value)"
            :class="[
              'px-4 py-2 text-sm font-medium rounded-md transition-colors',
              selectedTimeframe === tf.value
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
            ]"
          >
            {{ tf.label }}
          </button>
        </div>
      </div>

      <button
        @click="loadAnalyticsData"
        :disabled="analyticsLoading"
        class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50"
      >
        {{ analyticsLoading ? $t('admin.analyticsPage.loading') : $t('admin.analyticsPage.refresh') }}
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="initialLoading" class="bg-white rounded-lg shadow-sm p-16 text-center">
      <div class="flex justify-center mb-4">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
      <p class="text-gray-600">{{ $t('admin.analyticsPage.loadingData') }}</p>
    </div>

    <!-- Error State -->
    <div
      v-else-if="analyticsError"
      class="bg-red-50 border border-red-200 rounded-lg p-6 mb-6"
    >
      <div class="flex items-center gap-3">
        <span class="text-2xl">⚠️</span>
        <div>
          <p class="font-medium text-red-800">{{ $t('admin.analyticsPage.loadError') }}</p>
          <p class="text-sm text-red-600 mt-1">{{ analyticsError }}</p>
        </div>
      </div>
    </div>

    <!-- Analytics Content -->
    <div v-else-if="hasData">
      <!-- KPI Cards Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 mb-8">
        <AnalyticsKpiCard
          :label="$t('admin.analyticsPage.totalUsers')"
          :value="systemStats?.total_users || 0"
          format="number"
          icon="👥"
          :trend="userTrend"
          :description="$t('admin.analyticsPage.newIn7Days', { count: systemStats?.new_users_7_days || 0 })"
        />
        <AnalyticsKpiCard
          :label="$t('admin.analyticsPage.activeUsers7d')"
          :value="systemStats?.active_users_7_days || 0"
          format="number"
          icon="⚡"
          :trend="activeUserTrend"
        />
        <AnalyticsKpiCard
          :label="$t('admin.analyticsPage.organisations')"
          :value="systemStats?.total_organisations || 0"
          format="number"
          icon="🏢"
        />
        <AnalyticsKpiCard
          :label="$t('admin.analyticsPage.coursesPublished')"
          :value="systemStats?.published_courses || 0"
          format="number"
          icon="📚"
          :description="`${systemStats?.total_courses || 0} ${$t('admin.analyticsPage.total')}`"
        />
        <AnalyticsKpiCard
          :label="$t('admin.analyticsPage.totalEnrollments')"
          :value="systemStats?.total_enrollments || 0"
          format="number"
          icon="✍️"
        />
        <AnalyticsKpiCard
          :label="$t('admin.analyticsPage.premiumSubscriptions')"
          :value="systemStats?.premium_subscriptions || 0"
          format="number"
          icon="💎"
        />
        <AnalyticsKpiCard
          :label="$t('admin.analyticsPage.tokensAvailable')"
          :value="systemStats?.token_stats?.total_tokens_available || 0"
          format="number"
          icon="🪙"
          :description="`${systemStats?.token_stats?.total_tokens_used || 0} ${$t('admin.analyticsPage.tokensUsed')}`"
        />
        <AnalyticsKpiCard
          :label="$t('admin.analyticsPage.tokens30d')"
          :value="systemStats?.token_stats?.tokens_used_30_days || 0"
          format="number"
          icon="📊"
          :trend="tokenTrend"
        />
      </div>

      <!-- Time Series Charts -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <!-- Events Time Series -->
        <div class="bg-white rounded-lg shadow-sm p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">{{ $t('admin.analyticsPage.eventsPerDay') }}</h3>
          <LineChart
            v-if="eventsChartData.labels.length > 0"
            :labels="eventsChartData.labels"
            :datasets="eventsChartData.datasets"
            :height="300"
          />
          <p v-else class="text-center text-gray-500 py-8">{{ $t('admin.analyticsPage.noDataAvailable') }}</p>
        </div>

        <!-- Active Users Time Series -->
        <div class="bg-white rounded-lg shadow-sm p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">{{ $t('admin.analyticsPage.activeUsersPerDay') }}</h3>
          <LineChart
            v-if="activeUsersChartData.labels.length > 0"
            :labels="activeUsersChartData.labels"
            :datasets="activeUsersChartData.datasets"
            :height="300"
          />
          <p v-else class="text-center text-gray-500 py-8">{{ $t('admin.analyticsPage.noDataAvailable') }}</p>
        </div>
      </div>

      <!-- Top Lists -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Top Courses -->
        <div class="bg-white rounded-lg shadow-sm p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">{{ $t('admin.analyticsPage.topCourses') }}</h3>
          <div v-if="topCourses.length > 0" class="space-y-3">
            <div
              v-for="(course, index) in topCourses"
              :key="course.course_id"
              class="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <div class="flex items-center gap-3 flex-1">
                <span class="text-sm font-bold text-gray-500 w-6">{{ index + 1 }}</span>
                <div class="flex-1">
                  <p class="font-medium text-gray-900 text-sm">{{ course.title }}</p>
                  <p class="text-xs text-gray-600">
                    {{ course.enrollments || 0 }} {{ $t('admin.analyticsPage.enrollments') }} ·
                    {{ course.completions || 0 }} {{ $t('admin.analyticsPage.completions') }}
                  </p>
                </div>
              </div>
              <div class="text-right">
                <p class="text-sm font-semibold text-blue-600">
                  {{ course.events_count || 0 }} {{ $t('admin.analyticsPage.events') }}
                </p>
                <p
                  v-if="course.avg_completion_rate !== undefined"
                  class="text-xs text-gray-600"
                >
                  {{ Math.round(course.avg_completion_rate) }}% {{ $t('admin.analyticsPage.completionRate') }}
                </p>
              </div>
            </div>
          </div>
          <p v-else class="text-center text-gray-500 py-8">{{ $t('admin.analyticsPage.noDataAvailable') }}</p>
        </div>

        <!-- Top Learning Methods -->
        <div class="bg-white rounded-lg shadow-sm p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">{{ $t('admin.analyticsPage.topLearningMethods') }}</h3>
          <div v-if="topMethods.length > 0" class="space-y-3">
            <div
              v-for="(method, index) in topMethods"
              :key="method.method_id"
              class="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <div class="flex items-center gap-3 flex-1">
                <span class="text-sm font-bold text-gray-500 w-6">{{ index + 1 }}</span>
                <div class="flex-1">
                  <p class="font-medium text-gray-900 text-sm">{{ method.name }}</p>
                  <p class="text-xs text-gray-600">{{ method.calls || 0 }} {{ $t('admin.analyticsPage.calls') }}</p>
                </div>
              </div>
              <div class="text-right">
                <p class="text-sm font-semibold text-green-600">
                  {{ formatNumber(method.tokens_used || 0) }} {{ $t('admin.analyticsPage.tokens') }}
                </p>
                <p v-if="method.avg_tokens" class="text-xs text-gray-600">
                  {{ $t('admin.analyticsPage.avgPerCall', { count: formatNumber(method.avg_tokens) }) }}
                </p>
              </div>
            </div>
          </div>
          <p v-else class="text-center text-gray-500 py-8">{{ $t('admin.analyticsPage.noDataAvailable') }}</p>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div
      v-else
      class="bg-white rounded-lg shadow-sm p-16 text-center"
    >
      <span class="text-6xl mb-4 block">📊</span>
      <p class="text-gray-600 mb-2">{{ $t('admin.analyticsPage.noData') }}</p>
      <p class="text-sm text-gray-500">
        {{ $t('admin.analyticsPage.noDataHint') }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAdminStore } from '@/store/modules/admin'
import { AnalyticsKpiCard, LineChart } from '@/components/analytics/charts'

const { t } = useI18n()

// ============================================================================
// Store
// ============================================================================

const adminStore = useAdminStore()

// ============================================================================
// State
// ============================================================================

const selectedTimeframe = ref<7 | 30 | 90>(7)
const initialLoading = ref(true)

const timeframeOptions = computed(() => [
  { label: t('admin.analyticsPage.days7'), value: 7 as const },
  { label: t('admin.analyticsPage.days30'), value: 30 as const },
  { label: t('admin.analyticsPage.days90'), value: 90 as const }
])

// ============================================================================
// Computed
// ============================================================================

const systemStats = computed(() => adminStore.systemStats)
const systemAnalytics = computed(() => adminStore.systemAnalytics)
const analyticsLoading = computed(() => adminStore.systemAnalyticsLoading)
const analyticsError = computed(() => adminStore.systemAnalyticsError)

const hasData = computed(() => {
  return systemStats.value !== null && systemAnalytics.value !== null
})

const topCourses = computed(() => systemAnalytics.value?.topCourses || [])
const topMethods = computed(() => systemAnalytics.value?.topMethods || [])

// Trends (simple up/down based on comparison - in real app would need historical data)
const userTrend = computed(() => {
  if (!systemStats.value) return 'neutral'
  const newUsers = systemStats.value.new_users_7_days || 0
  return newUsers > 0 ? 'up' : 'neutral'
})

const activeUserTrend = computed(() => {
  if (!systemStats.value) return 'neutral'
  const active7 = systemStats.value.active_users_7_days || 0
  const active30 = systemStats.value.active_users_30_days || 0
  if (active7 > active30 / 4) return 'up'
  if (active7 < active30 / 4) return 'down'
  return 'neutral'
})

const tokenTrend = computed(() => {
  if (!systemStats.value?.token_stats) return 'neutral'
  const used7 = systemStats.value.token_stats.tokens_used_7_days || 0
  const used30 = systemStats.value.token_stats.tokens_used_30_days || 0
  if (used7 > used30 / 4) return 'up'
  if (used7 < used30 / 4) return 'down'
  return 'neutral'
})

// Chart Data - Events Time Series
const eventsChartData = computed(() => {
  const timeSeries = systemAnalytics.value?.eventsTimeSeries || []
  return {
    labels: timeSeries.map((point) => formatDate(point.date)),
    datasets: [
      {
        label: 'Events',
        data: timeSeries.map((point) => point.value),
        color: '#3B82F6',
        fill: true
      }
    ]
  }
})

// Chart Data - Active Users Time Series
const activeUsersChartData = computed(() => {
  const timeSeries = systemAnalytics.value?.activeUsersTimeSeries || []
  return {
    labels: timeSeries.map((point) => formatDate(point.date)),
    datasets: [
      {
        label: 'Aktive Nutzer',
        data: timeSeries.map((point) => point.value),
        color: '#10B981',
        fill: true
      }
    ]
  }
})

// ============================================================================
// Methods
// ============================================================================

const loadAnalyticsData = async () => {
  try {
    await Promise.all([
      adminStore.loadAdminDashboard(),
      adminStore.loadAdminAnalytics(selectedTimeframe.value)
    ])
  } catch (error) {
    console.error('Failed to load analytics:', error)
  } finally {
    initialLoading.value = false
  }
}

const changeTimeframe = async (timeframe: 7 | 30 | 90) => {
  selectedTimeframe.value = timeframe
  await adminStore.changeAnalyticsTimeframe(timeframe)
}

const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('de-DE', {
    month: 'short',
    day: 'numeric'
  }).format(date)
}

const formatNumber = (num: number): string => {
  return new Intl.NumberFormat('de-DE').format(num)
}

// ============================================================================
// Lifecycle
// ============================================================================

onMounted(() => {
  loadAnalyticsData()
})
</script>
