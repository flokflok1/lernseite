<script setup lang="ts">
/**
 * BatchProgressPanel — Multi-skill batch execution progress
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { BatchProgress } from '../../types'

interface Props {
  progress: BatchProgress
}

const props = defineProps<Props>()
const emit = defineEmits<{ pause: []; resume: []; cancel: [] }>()
const { t } = useI18n()

const progressPercent = computed(() =>
  props.progress.total_steps > 0
    ? Math.round((props.progress.completed_steps / props.progress.total_steps) * 100)
    : 0,
)

const statusLabel = computed(() => {
  if (props.progress.is_paused) return t('aiEditor.batch.paused')
  if (props.progress.is_running) return t('aiEditor.batch.running')
  if (props.progress.completed_steps === props.progress.total_steps) return t('aiEditor.batch.completed')
  return t('aiEditor.batch.idle')
})
</script>

<template>
  <div class="p-4 space-y-3">
    <!-- Progress Bar -->
    <div>
      <div class="flex items-center justify-between mb-1">
        <span class="text-xs text-gray-400">{{ statusLabel }}</span>
        <span class="text-xs text-gray-500">
          {{ progress.completed_steps }}/{{ progress.total_steps }}
        </span>
      </div>
      <div class="h-2 bg-gray-800 rounded-full overflow-hidden">
        <div
          class="h-full rounded-full transition-all duration-500"
          :class="progress.failed_steps > 0 ? 'bg-orange-500' : 'bg-indigo-500'"
          :style="{ width: `${progressPercent}%` }"
        />
      </div>
    </div>

    <!-- Current Step -->
    <div v-if="progress.is_running && progress.current_skill_code" class="text-xs text-gray-400">
      {{ t('aiEditor.batch.currentStep') }}: <span class="text-white">{{ progress.current_skill_code }}</span>
    </div>

    <!-- Failed count -->
    <div v-if="progress.failed_steps > 0" class="text-xs text-red-400">
      {{ progress.failed_steps }} {{ t('aiEditor.batch.failed') }}
    </div>

    <!-- Controls -->
    <div v-if="progress.is_running || progress.is_paused" class="flex gap-2">
      <button
        v-if="progress.is_running"
        class="px-3 py-1.5 bg-yellow-600 hover:bg-yellow-500 text-white rounded text-xs"
        @click="emit('pause')"
      >
        {{ t('aiEditor.batch.pause') }}
      </button>
      <button
        v-if="progress.is_paused"
        class="px-3 py-1.5 bg-green-600 hover:bg-green-500 text-white rounded text-xs"
        @click="emit('resume')"
      >
        {{ t('aiEditor.batch.resume') }}
      </button>
      <button
        class="px-3 py-1.5 bg-gray-700 hover:bg-gray-600 text-red-400 rounded text-xs"
        @click="emit('cancel')"
      >
        {{ t('aiEditor.batch.cancel') }}
      </button>
    </div>
  </div>
</template>
