<template>
  <div class="admin-dashboard-page">
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-[var(--color-text-primary)]">System Dashboard</h1>
      <p class="text-[var(--color-text-secondary)] mt-1">Überblick über das gesamte System - Phase 2.1</p>
    </div>
    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4">
      <p class="text-red-700">{{ error }}</p>
    </div>

    <!-- Dashboard Content - Phase 2.1 -->
    <div v-else class="space-y-6">
      <!-- User Stats Row -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          title="Total Users"
          :value="userStats.total_users"
          icon="👥"
          icon-color="primary"
          subtitle="Alle registrierten Benutzer"
          :loading="loading"
        />

        <StatsCard
          title="Active Users"
          :value="userStats.active_users"
          icon="✅"
          icon-color="success"
          subtitle="Aktiv in den letzten 7 Tagen"
          :loading="loading"
        />

        <StatsCard
          title="Banned Users"
          :value="userStats.banned_users"
          icon="🚫"
          icon-color="danger"
          subtitle="Gesperrte Konten"
          :loading="loading"
        />

        <StatsCard
          title="New Users (30d)"
          :value="userStats.new_users_30d"
          icon="🆕"
          icon-color="info"
          subtitle="Neue Registrierungen"
          :loading="loading"
        />
      </div>

      <!-- Course Stats Row -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          title="Total Courses"
          :value="courseStats.total_courses"
          icon="📚"
          icon-color="primary"
          subtitle="Alle Kurse im System"
          :loading="loading"
        />

        <StatsCard
          title="Published"
          :value="courseStats.published"
          icon="✅"
          icon-color="success"
          subtitle="Veröffentlichte Kurse"
          :loading="loading"
        />

        <StatsCard
          title="Pending Review"
          :value="courseStats.pending_review"
          icon="⏳"
          icon-color="warning"
          subtitle="Warten auf Freigabe"
          :loading="loading"
        />

        <StatsCard
          title="Rejected"
          :value="courseStats.rejected"
          icon="❌"
          icon-color="danger"
          subtitle="Abgelehnte Kurse"
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
            title="Uptime"
            :value="systemStats.uptime"
            icon="⏱️"
            icon-color="success"
            format="duration"
            subtitle="System läuft seit"
            :loading="loading"
          />

          <StatsCard
            title="DB Latency"
            :value="systemStats.db_latency + ' ms'"
            icon="💾"
            :icon-color="dbLatencyColor"
            subtitle="Datenbankgeschwindigkeit"
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
              <p class="font-semibold text-[var(--color-text-primary)]">Benutzer verwalten</p>
              <p class="text-sm text-[var(--color-text-secondary)]">Rollen, Status & mehr</p>
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
              <p class="font-semibold text-[var(--color-text-primary)]">Organisationen</p>
              <p class="text-sm text-[var(--color-text-secondary)]">Schulen & Unternehmen</p>
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
              <p class="font-semibold text-[var(--color-text-primary)]">Kurse verwalten</p>
              <p class="text-sm text-[var(--color-text-secondary)]">Freigabe & Archivierung</p>
            </div>
          </div>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { adminGetUserStats, adminGetCourseStats, adminGetSystemStatsData } from '@/api/admin.api'
import type { UserStatsData, CourseStatsData, SystemStatsData } from '@/api/admin.api'
import StatsCard from '@/components/admin/StatsCard.vue'
import SystemStatus from '@/components/admin/SystemStatus.vue'

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
