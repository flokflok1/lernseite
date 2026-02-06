<template>
  <div class="group-list">
    <!-- Stats Header (GBA) -->
    <div class="stats-grid grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
      <div class="stat-card bg-white dark:bg-gray-800 rounded-lg shadow p-4">
        <div class="text-sm text-gray-500 dark:text-gray-400 mb-1">
          {{ $t('panel.groups.stats.totalGroups') }}
        </div>
        <div class="text-2xl font-bold text-gray-900 dark:text-white">
          {{ groups.length }}
        </div>
      </div>

      <div class="stat-card bg-white dark:bg-gray-800 rounded-lg shadow p-4">
        <div class="text-sm text-gray-500 dark:text-gray-400 mb-1">
          {{ $t('panel.groups.systemGroups') }}
        </div>
        <div class="text-2xl font-bold text-blue-600 dark:text-blue-400">
          {{ systemGroupsCount }}
        </div>
      </div>

      <div class="stat-card bg-white dark:bg-gray-800 rounded-lg shadow p-4">
        <div class="text-sm text-gray-500 dark:text-gray-400 mb-1">
          {{ $t('panel.groups.customGroups') }}
        </div>
        <div class="text-2xl font-bold text-green-600 dark:text-green-400">
          {{ customGroupsCount }}
        </div>
      </div>
    </div>

    <!-- Filters & Search (GBA) -->
    <div class="filters bg-white dark:bg-gray-800 rounded-lg shadow p-4 mb-6">
      <div class="flex flex-col md:flex-row gap-4">
        <!-- Search -->
        <div class="flex-1">
          <input
            v-model="searchQuery"
            type="text"
            :placeholder="$t('panel.groups.searchPlaceholder')"
            class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
          />
        </div>

        <!-- Filter Buttons (GBA) -->
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
            {{ $t('panel.groups.allGroups') }}
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
            {{ $t('panel.groups.customGroups') }}
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
            {{ $t('panel.groups.systemGroups') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
      <p class="mt-4 text-gray-600 dark:text-gray-400">
        {{ $t('panel.groups.loading') }}
      </p>
    </div>

    <!-- Empty State (GBA) -->
    <div
      v-else-if="filteredGroups.length === 0"
      class="text-center py-12 bg-white dark:bg-gray-800 rounded-lg shadow"
    >
      <div class="text-6xl mb-4">🔍</div>
      <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">
        {{ $t('panel.groups.noGroups') }}
      </h3>
      <p class="text-gray-600 dark:text-gray-400">
        {{ filter === 'custom' ? $t('panel.groups.noCustomGroups') : $t('panel.groups.noGroups') }}
      </p>
    </div>

    <!-- Groups Grid (GBA) -->
    <div
      v-else
      class="groups-grid grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
    >
      <GroupCard
        v-for="group in filteredGroups"
        :key="group.id"
        :group="group"
        @view-details="$emit('view-details', $event)"
        @edit="$emit('edit', $event)"
        @delete="$emit('delete', $event)"
        @assign-permissions="$emit('assign-permissions', $event)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * Group List (GBA)
 * Displays groups with filtering and search.
 */
import { ref, computed } from 'vue'
import type { Group } from '@/presentation/components/panel/groups/types/group.types'
import GroupCard from './GroupCard.vue'

const props = defineProps<{
  groups: Group[]
  loading?: boolean
}>()

defineEmits<{
  (e: 'view-details', group: Group): void
  (e: 'edit', group: Group): void
  (e: 'delete', group: Group): void
  (e: 'assign-permissions', group: Group): void
}>()

// Local state
const searchQuery = ref('')
const filter = ref<'all' | 'custom' | 'system'>('all')

// Computed (GBA)
const filteredGroups = computed(() => {
  let filtered = props.groups

  // Apply search
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(
      (group) =>
        group.name.toLowerCase().includes(query) ||
        group.slug.toLowerCase().includes(query) ||
        (group.description && group.description.toLowerCase().includes(query))
    )
  }

  // Apply filter (GBA - by type)
  if (filter.value === 'custom') {
    filtered = filtered.filter((group) => group.type === 'custom')
  } else if (filter.value === 'system') {
    filtered = filtered.filter((group) => group.type === 'system_admin' || group.type === 'org_admin')
  }

  return filtered
})

const systemGroupsCount = computed(() =>
  props.groups.filter((g) => g.type === 'system_admin' || g.type === 'org_admin').length
)

const customGroupsCount = computed(() =>
  props.groups.filter((g) => g.type === 'custom').length
)
</script>

<style scoped>
.stat-card {
  transition: transform 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.groups-grid {
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
