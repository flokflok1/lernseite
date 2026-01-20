<template>
  <div class="permission-matrix">
    <!-- Header -->
    <div class="mb-6">
      <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">
        {{ mode === 'features' ? $t('admin.roles.features.title') : $t('admin.roles.permissions.title') }}
      </h2>
      <p class="text-gray-600 dark:text-gray-400">
        {{ mode === 'features' ? $t('admin.roles.features.subtitle') : $t('admin.roles.permissions.subtitle') }}
      </p>
      <div class="mt-2 text-sm text-gray-500 dark:text-gray-400">
        {{ $t('admin.roles.roleName') }}: <span class="font-semibold">{{ role.display_name }}</span>
      </div>
    </div>

    <!-- Mode Tabs -->
    <div class="tabs flex gap-2 mb-6">
      <button
        @click="mode = 'features'"
        :class="[
          'px-6 py-3 rounded-lg font-medium transition-colors',
          mode === 'features'
            ? 'bg-purple-600 text-white'
            : 'bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
        ]"
      >
        🎯 {{ $t('admin.roles.features.title') }}
        <span class="ml-2 px-2 py-1 rounded bg-white bg-opacity-20 text-xs">
          {{ selectedFeatures.length }}
        </span>
      </button>

      <button
        @click="mode = 'permissions'"
        :class="[
          'px-6 py-3 rounded-lg font-medium transition-colors',
          mode === 'permissions'
            ? 'bg-indigo-600 text-white'
            : 'bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
        ]"
      >
        🔐 {{ $t('admin.roles.permissions.title') }}
        <span class="ml-2 px-2 py-1 rounded bg-white bg-opacity-20 text-xs">
          {{ selectedPermissions.length }}
        </span>
      </button>
    </div>

    <!-- Replace Mode Toggle -->
    <div class="mode-toggle bg-white dark:bg-gray-800 rounded-lg shadow p-4 mb-6">
      <label class="flex items-center justify-between cursor-pointer">
        <div>
          <div class="font-medium text-gray-900 dark:text-white">
            {{ replaceMode ? $t('admin.roles.form.replaceMode') : $t('admin.roles.form.addMode') }}
          </div>
          <div class="text-sm text-gray-500 dark:text-gray-400">
            {{ replaceMode ? $t('admin.roles.form.replaceModeHint') : $t('admin.roles.form.addModeHint') }}
          </div>
        </div>
        <div class="relative">
          <input
            v-model="replaceMode"
            type="checkbox"
            class="sr-only peer"
          />
          <div class="w-11 h-6 bg-gray-200 peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
        </div>
      </label>
    </div>

    <!-- Features View -->
    <div v-if="mode === 'features'" class="features-matrix">
      <div
        v-for="(features, category) in groupedFeatures"
        :key="category"
        class="category-section bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-4"
      >
        <!-- Category Header -->
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
            {{ $t(`admin.roles.features.categories.${category}`) }}
          </h3>
          <div class="flex gap-2">
            <button
              @click="selectAllInCategory(category, true)"
              class="text-sm text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
            >
              {{ $t('admin.roles.features.selectAll') }}
            </button>
            <span class="text-gray-400">|</span>
            <button
              @click="selectAllInCategory(category, false)"
              class="text-sm text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300"
            >
              {{ $t('admin.roles.features.deselectAll') }}
            </button>
          </div>
        </div>

        <!-- Features Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          <label
            v-for="feature in features"
            :key="feature.feature_id"
            class="flex items-start space-x-3 p-3 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer transition-colors"
          >
            <input
              type="checkbox"
              :value="feature.feature_id"
              v-model="selectedFeatures"
              class="mt-1 w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <div class="flex-1 min-w-0">
              <div class="text-sm font-medium text-gray-900 dark:text-white truncate">
                {{ feature.feature_name }}
              </div>
              <div class="text-xs text-gray-500 dark:text-gray-400 truncate">
                {{ feature.feature_code }}
              </div>
            </div>
          </label>
        </div>
      </div>
    </div>

    <!-- Permissions View -->
    <div v-if="mode === 'permissions'" class="permissions-matrix">
      <div
        v-for="(permissions, category) in groupedPermissions"
        :key="category"
        class="category-section bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-4"
      >
        <!-- Category Header -->
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
            {{ category }}
          </h3>
          <div class="flex gap-2">
            <button
              @click="selectAllPermissionsInCategory(category, true)"
              class="text-sm text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
            >
              {{ $t('admin.roles.permissions.selectAll') }}
            </button>
            <span class="text-gray-400">|</span>
            <button
              @click="selectAllPermissionsInCategory(category, false)"
              class="text-sm text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300"
            >
              {{ $t('admin.roles.permissions.deselectAll') }}
            </button>
          </div>
        </div>

        <!-- Permissions Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <label
            v-for="permission in permissions"
            :key="permission.permission_id"
            class="flex items-start space-x-3 p-3 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer transition-colors"
          >
            <input
              type="checkbox"
              :value="permission.permission_id"
              v-model="selectedPermissions"
              class="mt-1 w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <div class="flex-1 min-w-0">
              <div class="text-sm font-medium text-gray-900 dark:text-white">
                {{ permission.display_name }}
              </div>
              <div class="text-xs text-gray-500 dark:text-gray-400">
                {{ permission.permission_key }}
              </div>
              <div v-if="permission.description" class="text-xs text-gray-400 dark:text-gray-500 mt-1">
                {{ permission.description }}
              </div>
            </div>
          </label>
        </div>
      </div>
    </div>

    <!-- Actions -->
    <div class="sticky bottom-0 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 p-6 -mx-6 -mb-6">
      <div class="flex justify-between items-center">
        <div class="text-sm text-gray-600 dark:text-gray-400">
          <span v-if="mode === 'features'">
            {{ selectedFeatures.length }} / {{ availableFeatures.length }} {{ $t('admin.roles.features') }}
          </span>
          <span v-else>
            {{ selectedPermissions.length }} / {{ availablePermissions.length }} {{ $t('admin.roles.permissions') }}
          </span>
        </div>

        <div class="flex gap-3">
          <button
            @click="$emit('cancel')"
            class="px-6 py-2 border border-gray-300 dark:border-gray-600 rounded-lg font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            {{ $t('common.cancel') }}
          </button>

          <button
            @click="handleSubmit"
            :disabled="submitting"
            class="px-6 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {{ submitting ? $t('common.saving') : (mode === 'features' ? $t('admin.roles.features.assign') : $t('admin.roles.permissions.assign')) }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { defineProps, defineEmits } from 'vue'
import type { RoleWithStats, SystemFeature } from '@/infrastructure/api/clients/admin'
import type { Permission } from '@/infrastructure/api/clients/admin'

const props = defineProps<{
  role: RoleWithStats
  availableFeatures: SystemFeature[]
  availablePermissions: Permission[]
  initialFeatures?: number[]
  initialPermissions?: number[]
}>()

const emit = defineEmits<{
  (e: 'submit', data: { type: 'features' | 'permissions'; ids: number[]; replace: boolean }): void
  (e: 'cancel'): void
}>()

// Local state
const mode = ref<'features' | 'permissions'>('features')
const selectedFeatures = ref<number[]>(props.initialFeatures || [])
const selectedPermissions = ref<number[]>(props.initialPermissions || [])
const replaceMode = ref(false)
const submitting = ref(false)

// Group features by category
const groupedFeatures = computed(() => {
  const groups: Record<string, SystemFeature[]> = {}
  props.availableFeatures.forEach((feature) => {
    if (!groups[feature.category]) {
      groups[feature.category] = []
    }
    groups[feature.category].push(feature)
  })
  return groups
})

// Group permissions by category
const groupedPermissions = computed(() => {
  const groups: Record<string, Permission[]> = {}
  props.availablePermissions.forEach((permission) => {
    const category = permission.category || permission.module || 'Other'
    if (!groups[category]) {
      groups[category] = []
    }
    groups[category].push(permission)
  })
  return groups
})

function selectAllInCategory(category: string, select: boolean) {
  const features = groupedFeatures.value[category]
  if (!features) return

  features.forEach((feature) => {
    const index = selectedFeatures.value.indexOf(feature.feature_id)
    if (select && index === -1) {
      selectedFeatures.value.push(feature.feature_id)
    } else if (!select && index !== -1) {
      selectedFeatures.value.splice(index, 1)
    }
  })
}

function selectAllPermissionsInCategory(category: string, select: boolean) {
  const permissions = groupedPermissions.value[category]
  if (!permissions) return

  permissions.forEach((permission) => {
    const index = selectedPermissions.value.indexOf(permission.permission_id)
    if (select && index === -1) {
      selectedPermissions.value.push(permission.permission_id)
    } else if (!select && index !== -1) {
      selectedPermissions.value.splice(index, 1)
    }
  })
}

function handleSubmit() {
  submitting.value = true

  const data = {
    type: mode.value,
    ids: mode.value === 'features' ? selectedFeatures.value : selectedPermissions.value,
    replace: replaceMode.value
  }

  emit('submit', data)

  setTimeout(() => {
    submitting.value = false
  }, 100)
}
</script>

<style scoped>
.permission-matrix {
  max-height: calc(100vh - 200px);
  overflow-y: auto;
}

.category-section {
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
