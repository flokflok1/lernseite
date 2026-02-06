<template>
  <div
    class="group-card bg-white dark:bg-gray-800 rounded-lg shadow-md hover:shadow-lg transition-shadow p-6 border-l-4"
    :class="groupColorClass"
  >
    <!-- Header (GBA) -->
    <div class="flex items-start justify-between mb-4">
      <div class="flex items-center space-x-3">
        <div
          class="group-icon text-3xl w-12 h-12 flex items-center justify-center rounded-full text-white"
          :class="groupBgClass"
        >
          {{ group.name.charAt(0).toUpperCase() }}
        </div>
        <div>
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
            {{ group.name }}
          </h3>
          <p class="text-sm text-gray-500 dark:text-gray-400">
            {{ group.slug }}
          </p>
        </div>
      </div>

      <!-- Type Badge (GBA) -->
      <div class="flex flex-col items-end space-y-1">
        <span :class="typeBadgeClass">
          {{ groupTypeLabel }}
        </span>
      </div>
    </div>

    <!-- Description (GBA) -->
    <p
      v-if="group.description"
      class="text-sm text-gray-600 dark:text-gray-300 mb-4 line-clamp-2"
    >
      {{ group.description }}
    </p>

    <!-- Actions (GBA) -->
    <div class="flex flex-wrap gap-2">
      <button
        @click="$emit('view-details', group)"
        class="flex-1 px-3 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600 transition-colors"
      >
        {{ $t('panel.groups.details') }}
      </button>

      <button
        v-if="group.type !== 'system_admin'"
        @click="$emit('edit', group)"
        class="px-3 py-2 text-sm font-medium text-blue-700 bg-blue-100 rounded hover:bg-blue-200 dark:bg-blue-900 dark:text-blue-200 dark:hover:bg-blue-800 transition-colors"
      >
        {{ $t('panel.groups.edit') }}
      </button>

      <button
        @click="$emit('assign-permissions', group)"
        class="px-3 py-2 text-sm font-medium text-indigo-700 bg-indigo-100 rounded hover:bg-indigo-200 dark:bg-indigo-900 dark:text-indigo-200 dark:hover:bg-indigo-800 transition-colors"
        :title="$t('panel.groups.assignPermissions')"
      >
        🔐
      </button>

      <button
        v-if="group.type === 'custom'"
        @click="$emit('delete', group)"
        class="px-3 py-2 text-sm font-medium text-red-700 bg-red-100 rounded hover:bg-red-200 dark:bg-red-900 dark:text-red-200 dark:hover:bg-red-800 transition-colors"
      >
        {{ $t('panel.groups.delete') }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * Group Card (GBA)
 * Displays a group card with actions.
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { Group } from '@/presentation/components/panel/groups/types/group.types'

const { t } = useI18n()

const props = defineProps<{
  group: Group
}>()

defineEmits<{
  (e: 'view-details', group: Group): void
  (e: 'edit', group: Group): void
  (e: 'delete', group: Group): void
  (e: 'assign-permissions', group: Group): void
}>()

// GBA computed styles
const groupColorClass = computed(() => {
  switch (props.group.type) {
    case 'system_admin': return 'border-l-red-600'
    case 'org_admin': return 'border-l-blue-600'
    default: return 'border-l-green-600'
  }
})

const groupBgClass = computed(() => {
  switch (props.group.type) {
    case 'system_admin': return 'bg-red-600'
    case 'org_admin': return 'bg-blue-600'
    default: return 'bg-green-600'
  }
})

const typeBadgeClass = computed(() => {
  const base = 'px-2 py-1 text-xs font-medium rounded'
  switch (props.group.type) {
    case 'system_admin': return `${base} bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200`
    case 'org_admin': return `${base} bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200`
    default: return `${base} bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200`
  }
})

const groupTypeLabel = computed(() => {
  switch (props.group.type) {
    case 'system_admin': return t('panel.groups.typeSystem')
    case 'org_admin': return t('panel.groups.typeOrg')
    default: return t('panel.groups.typeCustom')
  }
})
</script>

<style scoped>
.group-card {
  transition: all 0.2s ease;
}

.group-card:hover {
  transform: translateY(-2px);
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
