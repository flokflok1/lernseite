<script setup lang="ts">
/**
 * PlanTab — Plan Mode entry point with 4-phase wizard.
 *
 * Orchestrates the plan wizard lifecycle:
 * - No plan: shows course card (Phase 1 entry)
 * - Active plan: shows PlanPhaseWizard with phase navigation
 * - Plan history: recent plans for reloading
 */
import { onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { usePlanMode } from '../composables'
import { PlanPhaseWizard, PlanCourseCard } from '../panels'

interface Props {
  courseId: string
  hasFiles?: boolean
  fileIds?: string[]
}

const emit = defineEmits<{
  refreshStructure: []
}>()

const props = withDefaults(defineProps<Props>(), {
  hasFiles: false,
})
const { t } = useI18n()

const plan = usePlanMode()

onMounted(() => {
  if (props.courseId) {
    plan.loadPlanHistory(props.courseId)
  }
})

function handleGeneratePhase1(topic?: string, fileIds?: string[]) {
  plan.generatePhase1(props.courseId, topic, fileIds)
}

function handleDeletePlan(planId: string) {
  if (confirm(t('aiEditor.plan.confirmDelete'))) {
    plan.deletePlanFromHistory(planId)
  }
}

async function handleFinalizePlan() {
  await plan.finalizePlan()
  emit('refreshStructure')
}
</script>

<template>
  <div class="flex flex-col h-full gap-4">
    <!-- Plan History (when no active plan) -->
    <div v-if="!plan.hasPlan.value && plan.planHistory.value.length > 0" class="p-3 border-b border-gray-700">
      <label class="text-xs text-gray-500 mb-2 block">{{ t('aiEditor.plan.recentPlans') }}</label>
      <div class="space-y-1">
        <div
          v-for="p in plan.planHistory.value.slice(0, 5)"
          :key="p.plan_id"
          class="flex items-center gap-1"
        >
          <button
            class="flex-1 text-left px-3 py-2 rounded bg-gray-800/50 hover:bg-gray-800 text-sm text-gray-300 flex items-center justify-between"
            @click="plan.loadPlan(p.plan_id)"
          >
            <span>{{ p.scope }} · {{ p.phases.length }} {{ t('aiEditor.plan.phases') }}</span>
            <span class="text-xs text-gray-600">{{ p.status }}</span>
          </button>
          <button
            class="p-2 rounded hover:bg-red-900/40 text-gray-500 hover:text-red-400 transition-colors"
            :title="t('aiEditor.plan.delete')"
            @click.stop="handleDeletePlan(p.plan_id)"
          >
            <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M3 6h18M8 6V4a2 2 0 012-2h4a2 2 0 012 2v2m3 0v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6h14" />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Active Plan: Phase Wizard -->
    <PlanPhaseWizard
      v-if="plan.hasPlan.value"
      class="flex-1 min-h-0"
      :current-phase="plan.currentPhase.value"
      :plan="plan.currentPlan.value"
      :course-meta="plan.courseMeta.value"
      :chapters="plan.chapters.value"
      :chat-messages="plan.chatMessages.value"
      :is-creating="plan.isCreating.value"
      :is-executing="plan.isExecuting.value"
      :is-chatting="plan.isChatting.value"
      :has-files="hasFiles"
      :file-ids="fileIds"
      :is-draft="plan.isDraft.value"
      :is-approved="plan.isApproved.value"
      :total-steps="plan.totalSteps.value"
      :completed-steps="plan.completedSteps.value"
      @generate-phase1="handleGeneratePhase1"
      @confirm-phase="plan.confirmPhase"
      @go-back="plan.goBackToPhase"
      @send-chat="plan.sendPlanChatMessage"
      @execute="plan.execute"
      @discard="plan.clearPlan"
      @finalize-plan="handleFinalizePlan"
    />

    <!-- Empty State: Start New Plan -->
    <div v-if="!plan.hasPlan.value" class="flex-1">
      <PlanCourseCard
        :course-meta="null"
        :is-creating="plan.isCreating.value"
        :has-files="hasFiles"
        :file-ids="fileIds"
        @generate="handleGeneratePhase1"
      />
    </div>

    <!-- Error -->
    <div v-if="plan.error.value" class="px-2">
      <div class="p-3 bg-red-900/30 border border-red-800 rounded-lg text-xs text-red-300">
        {{ plan.error.value }}
      </div>
    </div>
  </div>
</template>
