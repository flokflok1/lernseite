<template>
  <AdminLayout page-title="Organisation Dashboard" page-subtitle="Überblick über Ihre Organisation" :is-org-admin="true">
    <div v-if="orgAdminStore.loading" class="flex justify-center items-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
    </div>

    <div v-else-if="!authStore.currentOrganisationId" class="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
      <p class="text-yellow-800">Sie sind keiner Organisation zugeordnet.</p>
    </div>

    <div v-else>
      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div class="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <div class="flex items-center justify-between mb-2">
            <span class="text-3xl">👥</span>
          </div>
          <p class="text-3xl font-bold text-gray-900">{{ orgAdminStore.memberCount }}</p>
          <p class="text-sm text-gray-600 mt-1">Mitglieder</p>
          <p class="text-xs text-gray-500 mt-2">{{ orgAdminStore.activeMembersCount }} aktiv</p>
        </div>

        <div class="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <div class="flex items-center justify-between mb-2">
            <span class="text-3xl">📚</span>
          </div>
          <p class="text-3xl font-bold text-gray-900">{{ orgAdminStore.orgCourseCount }}</p>
          <p class="text-sm text-gray-600 mt-1">Kurse</p>
        </div>

        <div class="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <div class="flex items-center justify-between mb-2">
            <span class="text-3xl">🪙</span>
          </div>
          <p class="text-3xl font-bold text-gray-900">{{ formatNumber(orgAdminStore.tokenAvailable) }}</p>
          <p class="text-sm text-gray-600 mt-1">Token verfügbar</p>
          <p class="text-xs text-gray-500 mt-2">{{ Math.round(orgAdminStore.tokenUsagePercentage) }}% verbraucht</p>
        </div>

        <div class="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <div class="flex items-center justify-between mb-2">
            <span class="text-3xl">📈</span>
          </div>
          <p class="text-3xl font-bold text-gray-900">{{ Math.round(orgAdminStore.orgCompletionRate) }}%</p>
          <p class="text-sm text-gray-600 mt-1">Abschlussrate</p>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <router-link to="/org/users" class="block bg-white rounded-lg shadow-sm p-6 border border-gray-200 hover:border-primary-300 transition-colors">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center text-2xl">👥</div>
            <div>
              <p class="font-semibold text-gray-900">Mitglieder verwalten</p>
              <p class="text-sm text-gray-600">Einladen & zuweisen</p>
            </div>
          </div>
        </router-link>

        <router-link to="/org/courses" class="block bg-white rounded-lg shadow-sm p-6 border border-gray-200 hover:border-primary-300 transition-colors">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center text-2xl">📚</div>
            <div>
              <p class="font-semibold text-gray-900">Kurse zuweisen</p>
              <p class="text-sm text-gray-600">Lernpfade verwalten</p>
            </div>
          </div>
        </router-link>

        <router-link to="/org/analytics" class="block bg-white rounded-lg shadow-sm p-6 border border-gray-200 hover:border-primary-300 transition-colors">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center text-2xl">📈</div>
            <div>
              <p class="font-semibold text-gray-900">Fortschritt ansehen</p>
              <p class="text-sm text-gray-600">Analytics & Reports</p>
            </div>
          </div>
        </router-link>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useOrgAdminStore } from '@/store/orgAdmin.store'
import { useAuthStore } from '@/store/auth.store'
import AdminLayout from '@/layouts/AdminLayout.vue'

const orgAdminStore = useOrgAdminStore()
const authStore = useAuthStore()

const formatNumber = (num: number): string => {
  return new Intl.NumberFormat('de-DE').format(num)
}

onMounted(async () => {
  const orgId = authStore.currentOrganisationId
  if (orgId) {
    try {
      await orgAdminStore.loadOrgDashboard(orgId)
    } catch (err) {
      console.error('Failed to load org dashboard:', err)
    }
  }
})
</script>
