<template>
  <div class="role-list">
    <!-- Stats Header -->
    <div class="stats-grid grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
      <div class="stat-card bg-white dark:bg-gray-800 rounded-lg shadow p-4">
        <div class="text-sm text-gray-500 dark:text-gray-400 mb-1">
          {{ $t('admin.roles.stats.totalRoles') }}
        </div>
        <div class="text-2xl font-bold text-gray-900 dark:text-white">
          {{ roles.length }}
        </div>
      </div>

      <div class="stat-card bg-white dark:bg-gray-800 rounded-lg shadow p-4">
        <div class="text-sm text-gray-500 dark:text-gray-400 mb-1">
          {{ $t('admin.roles.stats.systemRolesCount') }}
        </div>
        <div class="text-2xl font-bold text-blue-600 dark:text-blue-400">
          {{ systemRolesCount }}
        </div>
      </div>

      <div class="stat-card bg-white dark:bg-gray-800 rounded-lg shadow p-4">
        <div class="text-sm text-gray-500 dark:text-gray-400 mb-1">
          {{ $t('admin.roles.stats.customRolesCount') }}
        </div>
        <div class="text-2xl font-bold text-green-600 dark:text-green-400">
          {{ customRolesCount }}
        </div>
      </div>

      <div class="stat-card bg-white dark:bg-gray-800 rounded-lg shadow p-4">
        <div class="text-sm text-gray-500 dark:text-gray-400 mb-1">
          {{ $t('admin.roles.stats.totalUsers') }}
        </div>
        <div class="text-2xl font-bold text-purple-600 dark:text-purple-400">
          {{ totalUsers }}
        </div>
      </div>

      <div class="stat-card bg-white dark:bg-gray-800 rounded-lg shadow p-4">
        <div class="text-sm text-gray-500 dark:text-gray-400 mb-1">
          {{ $t('admin.roles.stats.avgFeatures') }}
        </div>
        <div class="text-2xl font-bold text-indigo-600 dark:text-indigo-400">
          {{ avgFeatures }}
        </div>
      </div>

      <div class="stat-card bg-white dark:bg-gray-800 rounded-lg shadow p-4">
        <div class="text-sm text-gray-500 dark:text-gray-400 mb-1">
          {{ $t('admin.roles.stats.avgPermissions') }}
        </div>
        <div class="text-2xl font-bold text-pink-600 dark:text-pink-400">
          {{ avgPermissions }}
        </div>
      </div>
    </div>

    <!-- Filters & Search -->
    <div class="filters bg-white dark:bg-gray-800 rounded-lg shadow p-4 mb-6">
      <div class="flex flex-col md:flex-row gap-4">
        <!-- Search -->
        <div class="flex-1">
          <input
            v-model="searchQuery"
            type="text"
            :placeholder="$t('admin.roles.searchPlaceholder')"
            class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
          />
        </div>

        <!-- Filter Buttons -->
        <div class="flex gap-2">
          <button
            @click="filter = 'all'"
            :class="[
              'px-4 py-2 rounded-lg font-medium transition-colors',
              filter === 'all'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
            ]"
          >
            {{ $t('admin.roles.allRoles') }}
          </button>

          <button
            @click="filter = 'custom'"
            :class="[
              'px-4 py-2 rounded-lg font-medium transition-colors',
              filter === 'custom'
                ? 'bg-green-600 text-white'
                : 'bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
            ]"
          >
            {{ $t('admin.roles.customRoles') }}
          </button>

          <button
            @click="filter = 'system'"
            :class="[
              'px-4 py-2 rounded-lg font-medium transition-colors',
              filter === 'system'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
            ]"
          >
            {{ $t('admin.roles.systemRoles') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
      <p class="mt-4 text-gray-600 dark:text-gray-400">
        {{ $t('admin.roles.loading') }}
      </p>
    </div>

    <!-- Empty State -->
    <div
      v-else-if="filteredRoles.length === 0"
      class="text-center py-12 bg-white dark:bg-gray-800 rounded-lg shadow"
    >
      <div class="text-6xl mb-4">🔍</div>
      <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">
        {{ $t('admin.roles.noRoles') }}
      </h3>
      <p class="text-gray-600 dark:text-gray-400">
        {{ filter === 'custom' ? $t('admin.roles.noCustomRoles') : $t('admin.roles.noRoles') }}
      </p>
    </div>

    <!-- Roles Grid -->
    <div
      v-else
      class="roles-grid grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
    >
      <RoleCard
        v-for="role in filteredRoles"
        :key="role.role_id"
        :role="role"
        @view-details="$emit('view-details', $event)"
        @edit="$emit('edit', $event)"
        @delete="$emit('delete', $event)"
        @assign-features="$emit('assign-features', $event)"
        @assign-permissions="$emit('assign-permissions', $event)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { defineProps, defineEmits } from 'vue'
import type { RoleWithStats } from '@/infrastructure/api/clients/admin'
import RoleCard from './RoleCard.vue'

const props = defineProps<{
  roles: RoleWithStats[]
  loading?: boolean
}>()

defineEmits<{
  (e: 'view-details', role: RoleWithStats): void
  (e: 'edit', role: RoleWithStats): void
  (e: 'delete', role: RoleWithStats): void
  (e: 'assign-features', role: RoleWithStats): void
  (e: 'assign-permissions', role: RoleWithStats): void
}>()

// Local state
const searchQuery = ref('')
const filter = ref<'all' | 'custom' | 'system'>('all')

// Computed
const filteredRoles = computed(() => {
  let filtered = props.roles

  // Apply search
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(
      (role) =>
        role.role_name.toLowerCase().includes(query) ||
        role.display_name.toLowerCase().includes(query) ||
        (role.description && role.description.toLowerCase().includes(query))
    )
  }

  // Apply filter
  if (filter.value === 'custom') {
    filtered = filtered.filter((role) => role.is_custom)
  } else if (filter.value === 'system') {
    filtered = filtered.filter((role) => role.is_system)
  }

  return filtered
})

const systemRolesCount = computed(() =>
  props.roles.filter((r) => r.is_system).length
)

const customRolesCount = computed(() =>
  props.roles.filter((r) => r.is_custom).length
)

const totalUsers = computed(() =>
  props.roles.reduce((sum, role) => sum + (role.user_count || 0), 0)
)

const avgFeatures = computed(() => {
  if (props.roles.length === 0) return 0
  const total = props.roles.reduce((sum, role) => sum + (role.feature_count || 0), 0)
  return Math.round(total / props.roles.length)
})

const avgPermissions = computed(() => {
  if (props.roles.length === 0) return 0
  const total = props.roles.reduce((sum, role) => sum + (role.permission_count || 0), 0)
  return Math.round(total / props.roles.length)
})
</script>

<style scoped>
.stat-card {
  transition: transform 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.roles-grid {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
