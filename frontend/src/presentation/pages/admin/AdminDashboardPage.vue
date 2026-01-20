<template>
  <div class="admin-dashboard-page">
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-[var(--color-text-primary)]">{{ $t('admin.dashboard.title') }}</h1>
      <p class="text-[var(--color-text-secondary)] mt-1">{{ $t('admin.dashboard.subtitle') }}</p>
    </div>
    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4">
      <p class="text-red-700">{{ error }}</p>
    </div>

    <!-- Dashboard Content -->
    <div v-else class="space-y-6">
      <!-- User Stats Row -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          :title="$t('admin.dashboard.totalUsers')"
          :value="userStats.total_users"
          icon="👥"
          icon-color="primary"
          :subtitle="$t('admin.dashboard.totalUsersDesc')"
          :loading="loading"
        />

        <StatsCard
          :title="$t('admin.dashboard.activeUsers')"
          :value="userStats.active_users"
          icon="✅"
          icon-color="success"
          :subtitle="$t('admin.dashboard.activeUsersDesc')"
          :loading="loading"
        />

        <StatsCard
          :title="$t('admin.dashboard.bannedUsers')"
          :value="userStats.banned_users"
          icon="🚫"
          icon-color="danger"
          :subtitle="$t('admin.dashboard.bannedUsersDesc')"
          :loading="loading"
        />

        <StatsCard
          :title="$t('admin.dashboard.newUsers30d')"
          :value="userStats.new_users_30d"
          icon="🆕"
          icon-color="info"
          :subtitle="$t('admin.dashboard.newUsersDesc')"
          :loading="loading"
        />
      </div>

      <!-- Course Stats Row -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          :title="$t('admin.dashboard.totalCourses')"
          :value="courseStats.total_courses"
          icon="📚"
          icon-color="primary"
          :subtitle="$t('admin.dashboard.totalCoursesDesc')"
          :loading="loading"
        />

        <StatsCard
          :title="$t('admin.dashboard.published')"
          :value="courseStats.published"
          icon="✅"
          icon-color="success"
          :subtitle="$t('admin.dashboard.publishedDesc')"
          :loading="loading"
        />

        <StatsCard
          :title="$t('admin.dashboard.pendingReview')"
          :value="courseStats.pending_review"
          icon="⏳"
          icon-color="warning"
          :subtitle="$t('admin.dashboard.pendingReviewDesc')"
          :loading="loading"
        />

        <StatsCard
          :title="$t('admin.dashboard.rejected')"
          :value="courseStats.rejected"
          icon="❌"
          icon-color="danger"
          :subtitle="$t('admin.dashboard.rejectedDesc')"
          :loading="loading"
        />
      </div>

      <!-- System Stats Row - System Status + API Metrics -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- System Status Component -->
        <div class="lg:col-span-2">
          <SystemStatus :stats="systemStats" :loading="loading" />
        </div>

        <!-- Request Volume Card -->
        <div class="space-y-6">
          <StatsCard
            :title="$t('admin.dashboard.uptime')"
            :value="systemStats.uptime"
            icon="⏱️"
            icon-color="success"
            format="duration"
            :subtitle="$t('admin.dashboard.uptimeDesc')"
            :loading="loading"
          />

          <StatsCard
            :title="$t('admin.dashboard.dbLatency')"
            :value="systemStats.db_latency + ' ms'"
            icon="💾"
            :icon-color="dbLatencyColor"
            :subtitle="$t('admin.dashboard.dbLatencyDesc')"
            :loading="loading"
          />
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <router-link
          to="/admin/users"
          class="block bg-[var(--color-surface)] rounded-lg shadow-sm p-6 border border-[var(--color-border)] hover:border-primary-300 transition-colors"
        >
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center text-2xl">
              👥
            </div>
            <div>
              <p class="font-semibold text-[var(--color-text-primary)]">{{ $t('admin.dashboard.manageUsers') }}</p>
              <p class="text-sm text-[var(--color-text-secondary)]">{{ $t('admin.dashboard.manageUsersDesc') }}</p>
            </div>
          </div>
        </router-link>

        <router-link
          to="/admin/organisations"
          class="block bg-[var(--color-surface)] rounded-lg shadow-sm p-6 border border-[var(--color-border)] hover:border-primary-300 transition-colors"
        >
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center text-2xl">
              🏢
            </div>
            <div>
              <p class="font-semibold text-[var(--color-text-primary)]">{{ $t('admin.dashboard.organisations') }}</p>
              <p class="text-sm text-[var(--color-text-secondary)]">{{ $t('admin.dashboard.organisationsDesc') }}</p>
            </div>
          </div>
        </router-link>

        <router-link
          to="/admin/courses"
          class="block bg-[var(--color-surface)] rounded-lg shadow-sm p-6 border border-[var(--color-border)] hover:border-primary-300 transition-colors"
        >
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center text-2xl">
              📚
            </div>
            <div>
              <p class="font-semibold text-[var(--color-text-primary)]">{{ $t('admin.dashboard.manageCourses') }}</p>
              <p class="text-sm text-[var(--color-text-secondary)]">{{ $t('admin.dashboard.manageCoursesDesc') }}</p>
            </div>
          </div>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
import { adminGetUserStats, adminGetCourseStats, adminGetSystemStatsData } from '@/infrastructure/api/admin.api'
import type { UserStatsData, CourseStatsData, SystemStatsData } from '@/infrastructure/api/admin.api'
import StatsCard from '@/presentation/components/system/shared/StatsCard.vue'
import SystemStatus from '@/presentation/components/system/admin/SystemStatus.vue'

// ============================================================================
// State
// ============================================================================

const loading = ref(true)
const error = ref<string | null>(null)

const userStats = ref<UserStatsData>({
  total_users: 0,
  active_users: 0,
  banned_users: 0,
  new_users_30d: 0
})

const courseStats = ref<CourseStatsData>({
  total_courses: 0,
  published: 0,
  pending_review: 0,
  rejected: 0
})

const systemStats = ref<SystemStatsData>({
  uptime: 0,
  db_latency: 0,
  request_count_24h: 0,
  error_rate: 0
})

// ============================================================================
// Computed
// ============================================================================

const dbLatencyColor = computed(() => {
  const latency = systemStats.value.db_latency
  if (latency < 50) return 'success'
  if (latency < 100) return 'warning'
  return 'danger'
})

// ============================================================================
// Methods
// ============================================================================

const loadDashboardData = async () => {
  loading.value = true
  error.value = null

  try {
    // Load all stats in parallel for better performance
    const [usersData, coursesData, systemData] = await Promise.all([
      adminGetUserStats(),
      adminGetCourseStats(),
      adminGetSystemStatsData()
    ])

    userStats.value = usersData
    courseStats.value = coursesData
    systemStats.value = systemData
  } catch (err: any) {
    console.error('Failed to load dashboard data:', err)
    error.value = err.response?.data?.message || err.message || 'Failed to load dashboard data'
  } finally {
    loading.value = false
  }
}

// ============================================================================
// Lifecycle
// ============================================================================

onMounted(async () => {
  await loadDashboardData()

  // Auto-refresh every 30 seconds
  setInterval(() => {
    loadDashboardData()
  }, 30000)
})
</script>
