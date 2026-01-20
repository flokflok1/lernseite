<template>
  <div
    class="role-card bg-white dark:bg-gray-800 rounded-lg shadow-md hover:shadow-lg transition-shadow p-6 border-l-4"
    :style="{ borderLeftColor: role.color }"
  >
    <!-- Header -->
    <div class="flex items-start justify-between mb-4">
      <div class="flex items-center space-x-3">
        <div
          class="role-icon text-3xl w-12 h-12 flex items-center justify-center rounded-full"
          :style="{ backgroundColor: `${role.color}20` }"
        >
          {{ role.icon }}
        </div>
        <div>
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
            {{ role.display_name }}
          </h3>
          <p class="text-sm text-gray-500 dark:text-gray-400">
            {{ role.role_name }}
          </p>
        </div>
      </div>

      <!-- Badges -->
      <div class="flex flex-col items-end space-y-1">
        <span
          v-if="role.is_system"
          class="px-2 py-1 text-xs font-medium rounded bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200"
        >
          {{ $t('admin.roles.isSystem') }}
        </span>
        <span
          v-if="role.is_custom"
          class="px-2 py-1 text-xs font-medium rounded bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
        >
          {{ $t('admin.roles.isCustom') }}
        </span>
        <span
          class="px-2 py-1 text-xs font-medium rounded bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200"
        >
          {{ $t('admin.roles.hierarchyLevel') }}: {{ role.hierarchy_level }}
        </span>
      </div>
    </div>

    <!-- Description -->
    <p
      v-if="role.description"
      class="text-sm text-gray-600 dark:text-gray-300 mb-4 line-clamp-2"
    >
      {{ role.description }}
    </p>

    <!-- Stats -->
    <div class="grid grid-cols-3 gap-4 mb-4">
      <div class="text-center">
        <div class="text-2xl font-bold text-gray-900 dark:text-white">
          {{ role.feature_count || 0 }}
        </div>
        <div class="text-xs text-gray-500 dark:text-gray-400">
          {{ $t('admin.roles.features') }}
        </div>
      </div>
      <div class="text-center">
        <div class="text-2xl font-bold text-gray-900 dark:text-white">
          {{ role.permission_count || 0 }}
        </div>
        <div class="text-xs text-gray-500 dark:text-gray-400">
          {{ $t('admin.roles.permissions') }}
        </div>
      </div>
      <div class="text-center">
        <div class="text-2xl font-bold text-gray-900 dark:text-white">
          {{ role.user_count || 0 }}
        </div>
        <div class="text-xs text-gray-500 dark:text-gray-400">
          {{ $t('admin.roles.userCount') }}
        </div>
      </div>
    </div>

    <!-- Actions -->
    <div class="flex flex-wrap gap-2">
      <button
        @click="$emit('view-details', role)"
        class="flex-1 px-3 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600 transition-colors"
      >
        {{ $t('admin.roles.details') }}
      </button>

      <button
        v-if="!role.is_system"
        @click="$emit('edit', role)"
        class="px-3 py-2 text-sm font-medium text-blue-700 bg-blue-100 rounded hover:bg-blue-200 dark:bg-blue-900 dark:text-blue-200 dark:hover:bg-blue-800 transition-colors"
      >
        {{ $t('admin.roles.edit') }}
      </button>

      <button
        @click="$emit('assign-features', role)"
        class="px-3 py-2 text-sm font-medium text-purple-700 bg-purple-100 rounded hover:bg-purple-200 dark:bg-purple-900 dark:text-purple-200 dark:hover:bg-purple-800 transition-colors"
        :title="$t('admin.roles.assignFeatures')"
      >
        🎯
      </button>

      <button
        @click="$emit('assign-permissions', role)"
        class="px-3 py-2 text-sm font-medium text-indigo-700 bg-indigo-100 rounded hover:bg-indigo-200 dark:bg-indigo-900 dark:text-indigo-200 dark:hover:bg-indigo-800 transition-colors"
        :title="$t('admin.roles.assignPermissions')"
      >
        🔐
      </button>

      <button
        v-if="!role.is_system"
        @click="$emit('delete', role)"
        class="px-3 py-2 text-sm font-medium text-red-700 bg-red-100 rounded hover:bg-red-200 dark:bg-red-900 dark:text-red-200 dark:hover:bg-red-800 transition-colors"
      >
        {{ $t('admin.roles.delete') }}
      </button>
    </div>

    <!-- Created Info -->
    <div
      v-if="role.created_by || role.created_at"
      class="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700 text-xs text-gray-500 dark:text-gray-400"
    >
      <span v-if="role.created_at">
        {{ $t('admin.roles.createdAt') }}:
        {{ formatDate(role.created_at) }}
      </span>
      <span v-if="role.created_by" class="ml-2">
        | {{ $t('admin.roles.createdBy') }}: {{ role.created_by }}
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps, defineEmits } from 'vue'
import type { RoleWithStats } from '@/infrastructure/api/clients/admin'

defineProps<{
  role: RoleWithStats
}>()

defineEmits<{
  (e: 'view-details', role: RoleWithStats): void
  (e: 'edit', role: RoleWithStats): void
  (e: 'delete', role: RoleWithStats): void
  (e: 'assign-features', role: RoleWithStats): void
  (e: 'assign-permissions', role: RoleWithStats): void
}>()

function formatDate(date: string): string {
  return new Date(date).toLocaleDateString('de-DE', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}
</script>

<style scoped>
.role-card {
  transition: all 0.2s ease;
}

.role-card:hover {
  transform: translateY(-2px);
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
