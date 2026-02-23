<script setup lang="ts">
/**
 * PlanModePanel — Plan visualization with steps, drag-reorder, file upload
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ContentPlan, PlanPhase, PlanStep } from '../types'

interface Props {
  plan: ContentPlan | null
  isCreating: boolean
  isExecuting: boolean
  isDraft: boolean
  isApproved: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  createPlan: [scope: string, scopeId?: string]
  createFromFile: [fileId: string]
  reorderStep: [phaseIndex: number, fromIndex: number, toIndex: number]
  removeStep: [phaseIndex: number, stepIndex: number]
  savePlan: []
  approve: []
  execute: []
}>()

const { t } = useI18n()

const statusColor = computed(() => {
  const map: Record<string, string> = {
    draft: 'text-yellow-400',
    approved: 'text-blue-400',
    executing: 'text-purple-400',
    completed: 'text-green-400',
    paused: 'text-orange-400',
  }
  return map[props.plan?.status || 'draft'] || 'text-gray-400'
})

const stepStatusIcon = (status: string) => {
  const map: Record<string, string> = {
    pending: '○',
    running: '◉',
    completed: '✓',
    failed: '✗',
    skipped: '—',
  }
  return map[status] || '○'
}

function moveStep(phaseIdx: number, stepIdx: number, direction: 'up' | 'down') {
  const newIdx = direction === 'up' ? stepIdx - 1 : stepIdx + 1
  emit('reorderStep', phaseIdx, stepIdx, newIdx)
}
</script>

<template>
  <div class="flex flex-col h-full">
    <!-- Empty State -->
    <div v-if="!plan" class="flex-1 flex flex-col items-center justify-center gap-6 p-8">
      <div class="text-center space-y-3">
        <div class="text-4xl">🗺️</div>
        <h3 class="text-lg font-semibold text-white">{{ t('aiEditor.plan.emptyTitle') }}</h3>
        <p class="text-sm text-gray-400 max-w-md">{{ t('aiEditor.plan.emptyDescription') }}</p>
      </div>
      <div class="flex gap-3">
        <button
          class="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-medium transition-colors"
          :disabled="isCreating"
          @click="emit('createPlan', 'course')"
        >
          <span v-if="isCreating" class="animate-pulse">{{ t('aiEditor.plan.creating') }}</span>
          <span v-else>{{ t('aiEditor.plan.createManual') }}</span>
        </button>
        <button
          class="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg text-sm font-medium transition-colors"
          :disabled="isCreating"
          @click="emit('createFromFile', '')"
        >
          {{ t('aiEditor.plan.uploadFile') }}
        </button>
      </div>
    </div>

    <!-- Plan View -->
    <div v-else class="flex-1 flex flex-col overflow-hidden">
      <!-- Header -->
      <div class="flex items-center justify-between p-4 border-b border-gray-700">
        <div class="flex items-center gap-3">
          <span :class="statusColor" class="font-medium text-sm uppercase">{{ plan.status }}</span>
          <span class="text-xs text-gray-500">
            ~{{ plan.estimated_total_tokens.toLocaleString() }} {{ t('aiEditor.plan.tokens') }}
          </span>
        </div>
        <div class="flex gap-2">
          <button
            v-if="isDraft"
            class="px-3 py-1.5 bg-gray-700 hover:bg-gray-600 text-white rounded text-xs"
            @click="emit('savePlan')"
          >
            {{ t('common.save') }}
          </button>
          <button
            v-if="isDraft"
            class="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded text-xs"
            @click="emit('approve')"
          >
            {{ t('aiEditor.plan.approve') }}
          </button>
          <button
            v-if="isApproved"
            class="px-3 py-1.5 bg-green-600 hover:bg-green-500 text-white rounded text-xs"
            :disabled="isExecuting"
            @click="emit('execute')"
          >
            <span v-if="isExecuting" class="animate-pulse">{{ t('aiEditor.plan.executing') }}</span>
            <span v-else>{{ t('aiEditor.plan.execute') }}</span>
          </button>
        </div>
      </div>

      <!-- Phases & Steps -->
      <div class="flex-1 overflow-y-auto p-4 space-y-4">
        <div v-for="(phase, phaseIdx) in plan.phases" :key="phase.phase_id" class="space-y-2">
          <h4 class="text-sm font-semibold text-gray-300 flex items-center gap-2">
            <span class="w-6 h-6 rounded-full bg-gray-700 flex items-center justify-center text-xs">
              {{ phaseIdx + 1 }}
            </span>
            {{ phase.title }}
          </h4>
          <div class="space-y-1 ml-8">
            <div
              v-for="(step, stepIdx) in phase.steps"
              :key="step.step_id"
              class="flex items-center gap-3 p-2 rounded bg-gray-800/50 hover:bg-gray-800 group"
            >
              <span class="text-xs w-4 text-center" :class="{
                'text-gray-500': step.status === 'pending',
                'text-blue-400 animate-pulse': step.status === 'running',
                'text-green-400': step.status === 'completed',
                'text-red-400': step.status === 'failed',
              }">
                {{ stepStatusIcon(step.status) }}
              </span>
              <div class="flex-1 min-w-0">
                <div class="text-sm text-white truncate">{{ step.skill_code }}</div>
                <div class="text-xs text-gray-500 truncate">{{ step.target_title }}</div>
              </div>
              <div v-if="isDraft" class="hidden group-hover:flex gap-1">
                <button
                  v-if="stepIdx > 0"
                  class="p-1 text-gray-500 hover:text-white"
                  @click="moveStep(phaseIdx, stepIdx, 'up')"
                >↑</button>
                <button
                  v-if="stepIdx < phase.steps.length - 1"
                  class="p-1 text-gray-500 hover:text-white"
                  @click="moveStep(phaseIdx, stepIdx, 'down')"
                >↓</button>
                <button
                  class="p-1 text-gray-500 hover:text-red-400"
                  @click="emit('removeStep', phaseIdx, stepIdx)"
                >✕</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
