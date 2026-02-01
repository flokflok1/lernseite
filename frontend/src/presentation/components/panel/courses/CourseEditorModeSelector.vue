<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/application/stores/modules/core'
import { useI18n } from 'vue-i18n'

const router = useRouter()
const authStore = useAuthStore()
const { t } = useI18n()

interface Props {
  open: boolean
  courseId?: string
}

const props = withDefaults(defineProps<Props>(), {
  open: true
})

const emit = defineEmits<{
  cancel: []
  select: [mode: 'manual' | 'ai']
}>()

// Permission checks
const isSystemAdmin = computed(() => authStore.isSystemAdmin)
const canAccessEditors = computed(() => isSystemAdmin.value)

// Button state
const buttons = computed(() => [
  {
    id: 'manual',
    label: t('panel.courseEditor.modes.manual'),
    description: t('panel.courseEditor.modes.manualDesc'),
    icon: '✏️',
    enabled: canAccessEditors.value
  },
  {
    id: 'ai',
    label: t('panel.courseEditor.modes.ai'),
    description: t('panel.courseEditor.modes.aiDesc'),
    icon: '🤖',
    enabled: canAccessEditors.value
  }
])

const handleSelectMode = (mode: 'manual' | 'ai') => {
  if (!canAccessEditors.value) {
    return
  }

  emit('select', mode)

  // Navigate to appropriate editor
  const coursePath = props.courseId ? `/${props.courseId}` : ''
  router.push(`/panel/kurs-editor/${mode}${coursePath}`)
}

const handleCancel = () => {
  emit('cancel')
  router.back()
}
</script>

<template>
  <div
    v-if="open"
    class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
    @click="handleCancel"
  >
    <!-- Modal Container -->
    <div
      class="bg-white rounded-lg shadow-xl p-8 max-w-md w-full mx-4"
      @click.stop
    >
      <!-- Header -->
      <div class="mb-6">
        <h2 class="text-2xl font-bold text-gray-900">
          {{ t('panel.courseEditor.selectMode') }}
        </h2>
        <p class="text-gray-600 text-sm mt-2">
          {{ t('panel.courseEditor.selectModeDesc') }}
        </p>
      </div>

      <!-- Permission Warning -->
      <div v-if="!canAccessEditors" class="bg-yellow-50 border border-yellow-200 rounded p-4 mb-6">
        <p class="text-yellow-800 text-sm">
          {{ t('panel.courseEditor.permissionDenied') }}
        </p>
      </div>

      <!-- Mode Buttons -->
      <div v-if="canAccessEditors" class="space-y-3 mb-6">
        <button
          v-for="button in buttons"
          :key="button.id"
          :disabled="!button.enabled"
          class="w-full p-4 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-all disabled:opacity-50 disabled:cursor-not-allowed text-left"
          @click="handleSelectMode(button.id as 'manual' | 'ai')"
        >
          <div class="flex items-start gap-3">
            <span class="text-2xl">{{ button.icon }}</span>
            <div class="flex-1">
              <h3 class="font-semibold text-gray-900">{{ button.label }}</h3>
              <p class="text-sm text-gray-600 mt-1">{{ button.description }}</p>
            </div>
          </div>
        </button>
      </div>

      <!-- No Permission State -->
      <div v-else class="mb-6">
        <p class="text-gray-700">
          {{ t('panel.courseEditor.contactAdmin') }}
        </p>
      </div>

      <!-- Cancel Button -->
      <div class="flex justify-end">
        <button
          class="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
          @click="handleCancel"
        >
          {{ t('common.cancel') }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Smooth transitions */
button:not(:disabled):hover {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1)
}

button:disabled {
  cursor: not-allowed
}
</style>
