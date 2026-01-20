<template>
  <form @submit.prevent="handleSubmit" class="role-form space-y-6">
    <!-- Basic Information -->
    <div class="section bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        {{ $t('admin.roles.form.basic') }}
      </h3>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Role Name -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            {{ $t('admin.roles.roleName') }} *
          </label>
          <input
            v-model="formData.role_name"
            type="text"
            required
            :disabled="isEditMode"
            :placeholder="$t('admin.roles.form.roleNamePlaceholder')"
            pattern="^[a-z][a-z0-9_]*$"
            minlength="3"
            maxlength="50"
            class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white disabled:opacity-50"
          />
          <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
            {{ $t('admin.roles.form.roleNameHint') }}
          </p>
        </div>

        <!-- Display Name -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            {{ $t('admin.roles.displayName') }} *
          </label>
          <input
            v-model="formData.display_name"
            type="text"
            required
            :placeholder="$t('admin.roles.form.displayNamePlaceholder')"
            minlength="3"
            maxlength="100"
            class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
          />
          <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
            {{ $t('admin.roles.form.displayNameHint') }}
          </p>
        </div>

        <!-- Hierarchy Level -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            {{ $t('admin.roles.form.hierarchyLevelLabel') }} *
          </label>
          <input
            v-model.number="formData.hierarchy_level"
            type="number"
            required
            min="1"
            max="8"
            class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
          />
          <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
            {{ $t('admin.roles.form.hierarchyLevelHint') }}
          </p>
        </div>

        <!-- Color -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            {{ $t('admin.roles.color') }}
          </label>
          <div class="flex gap-2">
            <input
              v-model="formData.color"
              type="color"
              class="h-10 w-20 rounded border border-gray-300 dark:border-gray-600"
            />
            <input
              v-model="formData.color"
              type="text"
              pattern="^#[0-9a-fA-F]{6}$"
              placeholder="#6b7280"
              class="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            />
          </div>
          <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
            {{ $t('admin.roles.form.colorHint') }}
          </p>
        </div>

        <!-- Icon -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            {{ $t('admin.roles.icon') }}
          </label>
          <input
            v-model="formData.icon"
            type="text"
            maxlength="10"
            :placeholder="$t('admin.roles.form.iconPlaceholder')"
            class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
          />
          <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
            {{ $t('admin.roles.form.iconHint') }}
          </p>
        </div>

        <!-- Description (Full Width) -->
        <div class="md:col-span-2">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            {{ $t('admin.roles.description') }}
          </label>
          <textarea
            v-model="formData.description"
            rows="3"
            maxlength="500"
            :placeholder="$t('admin.roles.form.descriptionPlaceholder')"
            class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white resize-none"
          ></textarea>
          <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
            {{ $t('admin.roles.form.descriptionHint') }}
          </p>
        </div>
      </div>
    </div>

    <!-- Features Selection -->
    <div
      v-if="!isEditMode"
      class="section bg-white dark:bg-gray-800 rounded-lg shadow p-6"
    >
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        {{ $t('admin.roles.form.selectFeatures') }}
      </h3>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
        {{ $t('admin.roles.form.featuresHint') }}
      </p>

      <div class="space-y-2 max-h-60 overflow-y-auto border border-gray-200 dark:border-gray-700 rounded p-4">
        <label
          v-for="feature in availableFeatures"
          :key="feature.feature_id"
          class="flex items-center space-x-3 p-2 hover:bg-gray-50 dark:hover:bg-gray-700 rounded cursor-pointer"
        >
          <input
            type="checkbox"
            :value="feature.feature_id"
            v-model="formData.feature_ids"
            class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
          />
          <div class="flex-1">
            <div class="text-sm font-medium text-gray-900 dark:text-white">
              {{ feature.feature_name }}
            </div>
            <div class="text-xs text-gray-500 dark:text-gray-400">
              {{ feature.feature_code }} ({{ feature.category }})
            </div>
          </div>
        </label>
      </div>

      <div class="mt-2 text-sm text-gray-600 dark:text-gray-400">
        {{ formData.feature_ids.length }} {{ $t('admin.roles.features') }}
        {{ $t('admin.roles.features.assigned') }}
      </div>
    </div>

    <!-- Permissions Selection -->
    <div
      v-if="!isEditMode"
      class="section bg-white dark:bg-gray-800 rounded-lg shadow p-6"
    >
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        {{ $t('admin.roles.form.selectPermissions') }}
      </h3>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
        {{ $t('admin.roles.form.permissionsHint') }}
      </p>

      <div class="space-y-2 max-h-60 overflow-y-auto border border-gray-200 dark:border-gray-700 rounded p-4">
        <label
          v-for="permission in availablePermissions"
          :key="permission.permission_id"
          class="flex items-center space-x-3 p-2 hover:bg-gray-50 dark:hover:bg-gray-700 rounded cursor-pointer"
        >
          <input
            type="checkbox"
            :value="permission.permission_id"
            v-model="formData.permission_ids"
            class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
          />
          <div class="flex-1">
            <div class="text-sm font-medium text-gray-900 dark:text-white">
              {{ permission.display_name }}
            </div>
            <div class="text-xs text-gray-500 dark:text-gray-400">
              {{ permission.permission_key }} ({{ permission.module }})
            </div>
          </div>
        </label>
      </div>

      <div class="mt-2 text-sm text-gray-600 dark:text-gray-400">
        {{ formData.permission_ids.length }} {{ $t('admin.roles.permissions') }}
        {{ $t('admin.roles.permissions.assigned') }}
      </div>
    </div>

    <!-- Preview Card -->
    <div class="section bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        {{ $t('common.preview') }}
      </h3>

      <div
        class="preview-card border-l-4 rounded-lg p-4 bg-gray-50 dark:bg-gray-700"
        :style="{ borderLeftColor: formData.color || '#6b7280' }"
      >
        <div class="flex items-center space-x-3">
          <div
            class="text-3xl w-12 h-12 flex items-center justify-center rounded-full"
            :style="{ backgroundColor: `${formData.color || '#6b7280'}20` }"
          >
            {{ formData.icon || '👤' }}
          </div>
          <div>
            <div class="text-lg font-semibold text-gray-900 dark:text-white">
              {{ formData.display_name || $t('admin.roles.form.displayNamePlaceholder') }}
            </div>
            <div class="text-sm text-gray-500 dark:text-gray-400">
              {{ formData.role_name || $t('admin.roles.form.roleNamePlaceholder') }}
            </div>
          </div>
        </div>
        <p v-if="formData.description" class="mt-3 text-sm text-gray-600 dark:text-gray-300">
          {{ formData.description }}
        </p>
      </div>
    </div>

    <!-- Actions -->
    <div class="flex justify-end gap-3">
      <button
        type="button"
        @click="$emit('cancel')"
        class="px-6 py-2 border border-gray-300 dark:border-gray-600 rounded-lg font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
      >
        {{ $t('admin.roles.form.cancel') }}
      </button>

      <button
        type="submit"
        :disabled="!isValid || submitting"
        class="px-6 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {{ submitting ? $t('common.saving') : (isEditMode ? $t('admin.roles.form.update') : $t('admin.roles.form.create')) }}
      </button>
    </div>
  </form>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { defineProps, defineEmits } from 'vue'
import type { RoleWithStats, SystemFeature } from '@/infrastructure/api/clients/admin'
import type { Permission } from '@/infrastructure/api/clients/admin'

const props = defineProps<{
  role?: RoleWithStats
  availableFeatures: SystemFeature[]
  availablePermissions: Permission[]
}>()

const emit = defineEmits<{
  (e: 'submit', data: any): void
  (e: 'cancel'): void
}>()

// Local state
const submitting = ref(false)
const formData = ref({
  role_name: '',
  display_name: '',
  description: '',
  hierarchy_level: 1,
  color: '#6b7280',
  icon: '👤',
  feature_ids: [] as number[],
  permission_ids: [] as number[]
})

const isEditMode = computed(() => !!props.role)

const isValid = computed(() => {
  return (
    formData.value.role_name.length >= 3 &&
    formData.value.display_name.length >= 3 &&
    formData.value.hierarchy_level >= 1 &&
    formData.value.hierarchy_level <= 8 &&
    /^[a-z][a-z0-9_]*$/.test(formData.value.role_name) &&
    /^#[0-9a-fA-F]{6}$/.test(formData.value.color)
  )
})

// Initialize form with role data if editing
watch(
  () => props.role,
  (role) => {
    if (role) {
      formData.value = {
        role_name: role.role_name,
        display_name: role.display_name,
        description: role.description || '',
        hierarchy_level: role.hierarchy_level,
        color: role.color,
        icon: role.icon,
        feature_ids: [],
        permission_ids: []
      }
    }
  },
  { immediate: true }
)

function handleSubmit() {
  if (!isValid.value || submitting.value) return

  submitting.value = true
  emit('submit', {
    ...formData.value,
    ...(isEditMode.value ? { role_name: undefined } : {}) // Don't send role_name in edit mode
  })

  // Reset submitting after emit (parent handles success/error)
  setTimeout(() => {
    submitting.value = false
  }, 100)
}
</script>

<style scoped>
.section {
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

input:invalid {
  border-color: #ef4444;
}

input:valid {
  border-color: #10b981;
}
</style>
