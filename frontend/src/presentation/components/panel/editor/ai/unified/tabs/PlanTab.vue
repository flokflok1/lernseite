<script setup lang="ts">
/**
 * PlanTab — Plan Mode entry point: create, edit, approve, execute plans
 */
import { onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { usePlanMode } from '../composables'
import { PlanModePanel, BatchProgressPanel } from '../panels'

interface Props {
  courseId: string
}

const props = defineProps<Props>()
const { t } = useI18n()

const plan = usePlanMode()

onMounted(() => {
  if (props.courseId) {
    plan.loadPlanHistory(props.courseId)
  }
})

function handleCreatePlan(scope: string, scopeId?: string) {
  plan.createNewPlan(props.courseId, scope, scopeId)
}

function handleCreateFromFile(fileId: string) {
  // TODO: Open file picker dialog, then call plan.createFromFile(courseId, fileId)
  plan.createFromFile(props.courseId, fileId)
}
</script>

<template>
  <div class="flex flex-col h-full">
    <!-- Plan History (when no active plan) -->
    <div v-if="!plan.hasPlan.value && plan.planHistory.value.length > 0" class="p-4 border-b border-gray-700">
      <label class="text-xs text-gray-500 mb-2 block">{{ t('aiEditor.plan.recentPlans') }}</label>
      <div class="space-y-1">
        <button
          v-for="p in plan.planHistory.value.slice(0, 5)"
          :key="p.plan_id"
          class="w-full text-left px-3 py-2 rounded bg-gray-800/50 hover:bg-gray-800 text-sm text-gray-300 flex items-center justify-between"
          @click="plan.loadPlan(p.plan_id)"
        >
          <span>{{ p.scope }} · {{ p.phases.length }} {{ t('aiEditor.plan.phases') }}</span>
          <span class="text-xs text-gray-600">{{ p.status }}</span>
        </button>
      </div>
    </div>

    <!-- Active Plan -->
    <PlanModePanel
      :plan="plan.currentPlan.value"
      :is-creating="plan.isCreating.value"
      :is-executing="plan.isExecuting.value"
      :is-draft="plan.isDraft.value"
      :is-approved="plan.isApproved.value"
      @create-plan="handleCreatePlan"
      @create-from-file="handleCreateFromFile"
      @reorder-step="plan.reorderStep"
      @remove-step="plan.removeStep"
      @save-plan="plan.savePlan"
      @approve="plan.approve"
      @execute="plan.execute"
    />

    <!-- Error -->
    <div v-if="plan.error.value" class="p-4">
      <div class="p-3 bg-red-900/30 border border-red-800 rounded-lg text-xs text-red-300">
        {{ plan.error.value }}
      </div>
    </div>
  </div>
</template>
