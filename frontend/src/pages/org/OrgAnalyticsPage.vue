<template>
  <AdminLayout
    page-title="Analytics"
    page-subtitle="Fortschritt & Statistiken Ihrer Organisation"
    :is-org-admin="true"
  >
    <!-- Timeframe Filter -->
    <div class="mb-6 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <label class="text-sm font-medium text-gray-700">Zeitraum:</label>
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
        {{ analyticsLoading ? 'Laden...' : 'Aktualisieren' }}
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="initialLoading" class="bg-white rounded-lg shadow-sm p-16 text-center">
      <div class="flex justify-center mb-4">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
      <p class="text-gray-600">Analytics-Daten werden geladen...</p>
    </div>

    <!-- Error State -->
    <div
      v-else-if="analyticsError"
      class="bg-red-50 border border-red-200 rounded-lg p-6 mb-6"
    >
      <div class="flex items-center gap-3">
        <span class="text-2xl">⚠️</span>
        <div>
          <p class="font-medium text-red-800">Fehler beim Laden der Analytics-Daten</p>
          <p class="text-sm text-red-600 mt-1">{{ analyticsError }}</p>
        </div>
      </div>
    </div>

    <!-- Analytics Content -->
    <div v-else-if="hasData">
      <!-- KPI Cards Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <AnalyticsKpiCard
          label="Mitglieder Gesamt"
          :value="orgStats?.total_members || 0"
          format="number"
          icon="👥"
          :description="`${orgStats?.active_members_7_days || 0} aktiv (7d)`"
        />
        <AnalyticsKpiCard
          label="Aktive Mitglieder (30d)"
          :value="orgStats?.active_members_30_days || 0"
          format="number"
          icon="⚡"
          :trend="activeMemberTrend"
        />
        <AnalyticsKpiCard
          label="Zugewiesene Kurse"
          :value="orgStats?.total_assigned_courses || 0"
          format="number"
          icon="📚"
        />
        <AnalyticsKpiCard
          label="Durchschn. Abschlussrate"
          :value="Math.round(orgStats?.avg_completion_rate || 0)"
          format="percent"
          icon="✅"
          :trend="completionTrend"
        />
        <AnalyticsKpiCard
          label="Tokens verwendet (7d)"
          :value="orgStats?.token_used_7_days || 0"
          format="number"
          icon="🪙"
        />
        <AnalyticsKpiCard
          label="Tokens verwendet (30d)"
          :value="orgStats?.token_used_30_days || 0"
          format="number"
          icon="📊"
          :trend="tokenTrend"
        />
        <AnalyticsKpiCard
          label="Token Pool"
          :value="organisation?.token_pool || 0"
          format="number"
          icon="💰"
          :description="`${organisation?.token_available || 0} verfügbar`"
        />
        <AnalyticsKpiCard
          label="Token-Nutzung"
          :value="tokenUsagePercentage"
          format="percent"
          icon="📈"
          :trend="tokenUsagePercentage > 80 ? 'up' : 'neutral'"
        />
      </div>

      <!-- Time Series Charts -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <!-- Events Time Series -->
        <div class="bg-white rounded-lg shadow-sm p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Events pro Tag</h3>
          <LineChart
            v-if="eventsChartData.labels.length > 0"
            :labels="eventsChartData.labels"
            :datasets="eventsChartData.datasets"
            :height="300"
          />
          <p v-else class="text-center text-gray-500 py-8">Keine Daten verfügbar</p>
        </div>

        <!-- Active Members Time Series -->
        <div class="bg-white rounded-lg shadow-sm p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Aktive Mitglieder pro Tag</h3>
          <LineChart
            v-if="activeMembersChartData.labels.length > 0"
            :labels="activeMembersChartData.labels"
            :datasets="activeMembersChartData.datasets"
            :height="300"
          />
          <p v-else class="text-center text-gray-500 py-8">Keine Daten verfügbar</p>
        </div>
      </div>

      <!-- Top Lists -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Top Courses -->
        <div class="bg-white rounded-lg shadow-sm p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Top Kurse</h3>
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
                    {{ course.enrolled_count || 0 }} Teilnehmer ·
                    Ø {{ Math.round(course.avg_progress || 0) }}% Fortschritt
                  </p>
                </div>
              </div>
              <div class="text-right">
                <p
                  v-if="course.completion_rate !== undefined"
                  class="text-sm font-semibold text-blue-600"
                >
                  {{ Math.round(course.completion_rate) }}% Abschlussrate
                </p>
                <p v-if="course.events_count" class="text-xs text-gray-600">
                  {{ course.events_count }} Events
                </p>
              </div>
            </div>
          </div>
          <p v-else class="text-center text-gray-500 py-8">Keine Daten verfügbar</p>
        </div>

        <!-- Top Chapters -->
        <div class="bg-white rounded-lg shadow-sm p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Top Kapitel</h3>
          <div v-if="topChapters.length > 0" class="space-y-3">
            <div
              v-for="(chapter, index) in topChapters"
              :key="chapter.chapter_id"
              class="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <div class="flex items-center gap-3 flex-1">
                <span class="text-sm font-bold text-gray-500 w-6">{{ index + 1 }}</span>
                <div class="flex-1">
                  <p class="font-medium text-gray-900 text-sm">{{ chapter.chapter_title }}</p>
                  <p class="text-xs text-gray-600">{{ chapter.course_title }}</p>
                </div>
              </div>
              <div class="text-right">
                <p class="text-sm font-semibold text-green-600">
                  {{ chapter.completions || 0 }} Abschlüsse
                </p>
                <p v-if="chapter.avg_time_spent" class="text-xs text-gray-600">
                  Ø {{ Math.round(chapter.avg_time_spent) }} Min
                </p>
              </div>
            </div>
          </div>
          <p v-else class="text-center text-gray-500 py-8">Keine Daten verfügbar</p>
        </div>
      </div>

      <!-- Additional Stats from orgStats -->
      <div v-if="orgStats?.top_courses || orgStats?.top_users" class="mt-8">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- Top Users from orgStats -->
          <div v-if="orgStats?.top_users" class="bg-white rounded-lg shadow-sm p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Top Lernende</h3>
            <div class="space-y-3">
              <div
                v-for="(user, index) in orgStats.top_users"
                :key="user.user_id"
                class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
              >
                <div class="flex items-center gap-3 flex-1">
                  <span class="text-sm font-bold text-gray-500 w-6">{{ index + 1 }}</span>
                  <div class="flex-1">
                    <p class="font-medium text-gray-900 text-sm">{{ user.user_name }}</p>
                    <p class="text-xs text-gray-600">
                      {{ user.courses_completed || 0 }} Kurse abgeschlossen
                    </p>
                  </div>
                </div>
                <div class="text-right">
                  <p class="text-sm font-semibold text-purple-600">
                    {{ Math.round(user.total_progress || 0) }}% Fortschritt
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="bg-white rounded-lg shadow-sm p-16 text-center">
      <span class="text-6xl mb-4 block">📊</span>
      <p class="text-gray-600 mb-2">Keine Analytics-Daten verfügbar</p>
      <p class="text-sm text-gray-500">
        Bitte stellen Sie sicher, dass Ihre Organisation aktiv ist.
      </p>
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useOrgAdminStore } from '@/store/orgAdmin.store'
import AdminLayout from '@/layouts/AdminLayout.vue'
import AnalyticsKpiCard from '@/components/analytics/AnalyticsKpiCard.vue'
import LineChart from '@/components/analytics/LineChart.vue'

// ============================================================================
// Store & Route
// ============================================================================

const route = useRoute()
const orgAdminStore = useOrgAdminStore()

// ============================================================================
// State
// ============================================================================

const selectedTimeframe = ref<7 | 30 | 90>(7)
const initialLoading = ref(true)

const timeframeOptions = [
  { label: '7 Tage', value: 7 as const },
  { label: '30 Tage', value: 30 as const },
  { label: '90 Tage', value: 90 as const }
]

// ============================================================================
// Computed
// ============================================================================

const orgId = computed(() => {
  return Number(route.params.orgId) || orgAdminStore.organisation?.organisation_id || 0
})

const organisation = computed(() => orgAdminStore.organisation)
const orgStats = computed(() => orgAdminStore.orgStats)
const orgAnalytics = computed(() => orgAdminStore.orgAnalytics)
const analyticsLoading = computed(() => orgAdminStore.orgAnalyticsLoading)
const analyticsError = computed(() => orgAdminStore.orgAnalyticsError)

const hasData = computed(() => {
  return organisation.value !== null && orgAnalytics.value !== null
})

const topCourses = computed(() => orgAnalytics.value?.topCourses || [])
const topChapters = computed(() => orgAnalytics.value?.topChapters || [])

const tokenUsagePercentage = computed(() => {
  if (!organisation.value || organisation.value.token_pool === 0) return 0
  return Math.round((organisation.value.token_used / organisation.value.token_pool) * 100)
})

// Trends
const activeMemberTrend = computed(() => {
  if (!orgStats.value) return 'neutral'
  const active7 = orgStats.value.active_members_7_days || 0
  const active30 = orgStats.value.active_members_30_days || 0
  if (active7 > active30 / 4) return 'up'
  if (active7 < active30 / 4) return 'down'
  return 'neutral'
})

const completionTrend = computed(() => {
  const rate = orgStats.value?.avg_completion_rate || 0
  if (rate >= 70) return 'up'
  if (rate < 40) return 'down'
  return 'neutral'
})

const tokenTrend = computed(() => {
  if (!orgStats.value) return 'neutral'
  const used7 = orgStats.value.token_used_7_days || 0
  const used30 = orgStats.value.token_used_30_days || 0
  if (used7 > used30 / 4) return 'up'
  if (used7 < used30 / 4) return 'down'
  return 'neutral'
})

// Chart Data - Events Time Series
const eventsChartData = computed(() => {
  const timeSeries = orgAnalytics.value?.eventsTimeSeries || []
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

// Chart Data - Active Members Time Series
const activeMembersChartData = computed(() => {
  const timeSeries = orgAnalytics.value?.activeMembersTimeSeries || []
  return {
    labels: timeSeries.map((point) => formatDate(point.date)),
    datasets: [
      {
        label: 'Aktive Mitglieder',
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
  if (!orgId.value) {
    console.error('No organisation ID found')
    initialLoading.value = false
    return
  }

  try {
    await Promise.all([
      orgAdminStore.loadOrgDashboard(orgId.value),
      orgAdminStore.loadOrgAdvancedAnalytics(orgId.value, selectedTimeframe.value)
    ])
  } catch (error) {
    console.error('Failed to load analytics:', error)
  } finally {
    initialLoading.value = false
  }
}

const changeTimeframe = async (timeframe: 7 | 30 | 90) => {
  selectedTimeframe.value = timeframe
  if (orgId.value) {
    await orgAdminStore.changeOrgAnalyticsTimeframe(orgId.value, timeframe)
  }
}

const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('de-DE', {
    month: 'short',
    day: 'numeric'
  }).format(date)
}

// ============================================================================
// Lifecycle
// ============================================================================

onMounted(() => {
  loadAnalyticsData()
})
</script>
