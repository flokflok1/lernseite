<template>
  <div class="template-selector">
    <!-- Header -->
    <div class="mb-6">
      <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">
        {{ $t('panel.groups.templates.title') }}
      </h2>
      <p class="text-gray-600 dark:text-gray-400">
        {{ $t('panel.groups.templates.subtitle') }}
      </p>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
    </div>

    <!-- Templates Grid -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="template in templates"
        :key="template.template"
        class="template-card bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition-shadow cursor-pointer"
        @click="selectTemplate(template)"
      >
        <!-- Header with Color -->
        <div
          class="template-header p-6 text-white"
          :style="{ backgroundColor: template.default_color }"
        >
          <div class="text-5xl mb-3">{{ template.default_icon }}</div>
          <h3 class="text-xl font-bold mb-2">
            {{ $t(`panel.groups.templates.${template.template}`) }}
          </h3>
          <p class="text-sm opacity-90">
            {{ $t(`panel.groups.templates.${template.template}Desc`) }}
          </p>
        </div>

        <!-- Body -->
        <div class="p-6">
          <!-- Recommended Hierarchy -->
          <div class="flex items-center justify-between mb-4 text-sm">
            <span class="text-gray-500 dark:text-gray-400">
              {{ $t('panel.groups.hierarchyLevel') }}
            </span>
            <span class="font-semibold text-gray-900 dark:text-white">
              {{ template.recommended_hierarchy }}
            </span>
          </div>

          <!-- Default Features -->
          <div class="mb-4">
            <div class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {{ $t('panel.groups.features') }} ({{ template.default_features.length }})
            </div>
            <div class="flex flex-wrap gap-1">
              <span
                v-for="(feature, index) in template.default_features.slice(0, 5)"
                :key="feature"
                class="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded"
              >
                {{ feature }}
              </span>
              <span
                v-if="template.default_features.length > 5"
                class="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded"
              >
                +{{ template.default_features.length - 5 }}
              </span>
            </div>
          </div>

          <!-- Use Template Button -->
          <button
            class="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            {{ $t('panel.groups.templates.useTemplate') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Customization Modal -->
    <div
      v-if="selectedTemplate"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click.self="selectedTemplate = null"
    >
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <!-- Modal Header -->
        <div class="sticky top-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-6">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-4">
              <div class="text-4xl">{{ selectedTemplate.default_icon }}</div>
              <div>
                <h3 class="text-xl font-bold text-gray-900 dark:text-white">
                  {{ $t(`panel.groups.templates.${selectedTemplate.template}`) }}
                </h3>
                <p class="text-sm text-gray-500 dark:text-gray-400">
                  {{ $t('panel.groups.templates.customize') }}
                </p>
              </div>
            </div>
            <button
              @click="selectedTemplate = null"
              class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
            >
              ✕
            </button>
          </div>
        </div>

        <!-- Modal Body -->
        <form @submit.prevent="handleCreateFromTemplate" class="p-6 space-y-6">
          <!-- Role Name (Required) -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {{ $t('panel.groups.roleName') }} *
            </label>
            <input
              v-model="customization.role_name"
              type="text"
              required
              :placeholder="$t('panel.groups.form.roleNamePlaceholder')"
              pattern="^[a-z][a-z0-9_]*$"
              minlength="3"
              maxlength="50"
              class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            />
            <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
              {{ $t('panel.groups.form.roleNameHint') }}
            </p>
          </div>

          <!-- Display Name (Optional Override) -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {{ $t('panel.groups.displayName') }}
              <span class="text-gray-400">({{ $t('common.optional') }})</span>
            </label>
            <input
              v-model="customization.display_name"
              type="text"
              :placeholder="$t(`panel.groups.templates.${selectedTemplate.template}`)"
              class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            />
            <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
              {{ $t('common.leaveEmptyForDefault') }}
            </p>
          </div>

          <!-- Features Customization -->
          <div>
            <label class="flex items-center space-x-2 mb-2">
              <input
                v-model="customizeFeatures"
                type="checkbox"
                class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <span class="text-sm font-medium text-gray-700 dark:text-gray-300">
                {{ $t('panel.groups.templates.customize') }} {{ $t('panel.groups.features') }}
              </span>
            </label>

            <div
              v-if="customizeFeatures"
              class="mt-3 p-4 border border-gray-200 dark:border-gray-700 rounded-lg space-y-2 max-h-60 overflow-y-auto"
            >
              <label
                v-for="feature in availableFeatures"
                :key="feature.feature_id"
                class="flex items-center space-x-2 p-2 hover:bg-gray-50 dark:hover:bg-gray-700 rounded cursor-pointer"
              >
                <input
                  type="checkbox"
                  :value="feature.feature_id"
                  v-model="customization.customize_features"
                  class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <div class="flex-1">
                  <div class="text-sm font-medium text-gray-900 dark:text-white">
                    {{ feature.feature_name }}
                  </div>
                  <div class="text-xs text-gray-500 dark:text-gray-400">
                    {{ feature.feature_code }}
                  </div>
                </div>
              </label>
            </div>

            <p v-else class="mt-2 text-xs text-gray-500 dark:text-gray-400">
              {{ selectedTemplate.default_features.length }} {{ $t('panel.groups.features') }} {{ $t('common.default') }}
            </p>
          </div>

          <!-- Preview -->
          <div class="preview-card border-l-4 rounded-lg p-4 bg-gray-50 dark:bg-gray-700"
            :style="{ borderLeftColor: selectedTemplate.default_color }"
          >
            <div class="flex items-center space-x-3">
              <div class="text-3xl">{{ selectedTemplate.default_icon }}</div>
              <div>
                <div class="text-lg font-semibold text-gray-900 dark:text-white">
                  {{ customization.display_name || $t(`panel.groups.templates.${selectedTemplate.template}`) }}
                </div>
                <div class="text-sm text-gray-500 dark:text-gray-400">
                  {{ customization.role_name || $t('panel.groups.form.roleNamePlaceholder') }}
                </div>
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex justify-end gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
            <button
              type="button"
              @click="selectedTemplate = null"
              class="px-6 py-2 border border-gray-300 dark:border-gray-600 rounded-lg font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              {{ $t('common.cancel') }}
            </button>

            <button
              type="submit"
              :disabled="!customization.role_name || submitting"
              class="px-6 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {{ submitting ? $t('common.creating') : $t('panel.groups.templates.createFromTemplate') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { defineProps, defineEmits } from 'vue'
import type { RoleTemplate, SystemFeature, CreateFromTemplateRequest } from '@/application/services/api/admin'

defineProps<{
  templates: RoleTemplate[]
  availableFeatures: SystemFeature[]
  loading?: boolean
}>()

const emit = defineEmits<{
  (e: 'create', data: CreateFromTemplateRequest): void
}>()

// Local state
const selectedTemplate = ref<RoleTemplate | null>(null)
const customizeFeatures = ref(false)
const submitting = ref(false)
const customization = ref<CreateFromTemplateRequest>({
  template: 'parent',
  role_name: '',
  display_name: '',
  customize_features: []
})

function selectTemplate(template: RoleTemplate) {
  selectedTemplate.value = template
  customization.value = {
    template: template.template,
    role_name: '',
    display_name: '',
    customize_features: []
  }
  customizeFeatures.value = false
}

function handleCreateFromTemplate() {
  if (!customization.value.role_name || submitting.value) return

  submitting.value = true

  const data: CreateFromTemplateRequest = {
    template: customization.value.template,
    role_name: customization.value.role_name,
    display_name: customization.value.display_name || undefined,
    customize_features:
      customizeFeatures.value && customization.value.customize_features!.length > 0
        ? customization.value.customize_features
        : undefined
  }

  emit('create', data)

  setTimeout(() => {
    submitting.value = false
    selectedTemplate.value = null
  }, 100)
}
</script>

<style scoped>
.template-card {
  transition: all 0.3s ease;
}

.template-card:hover {
  transform: translateY(-4px);
}

.template-header {
  background: linear-gradient(135deg, var(--tw-gradient-from) 0%, var(--tw-gradient-to) 100%);
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.fixed {
  animation: fadeIn 0.2s ease;
}
</style>
